from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.security import OAuth2PasswordBearer

from . import db as dbmod
from .auth import create_access_token, decode_token, hash_password, verify_password
from .binance_public import BinancePublicClient
from .config import settings
from .models import (
    PortfolioResponse,
    SignalResponse,
    TokenResponse,
    TradeRequest,
    TradeResponse,
    UserCreate,
    UserLogin,
)
from .notifier import Notifier
from .scheduler import SchedulerHandle, start_scheduler
from .signal_engine import score_signal


app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
binance = BinancePublicClient()
notifier = Notifier()
_scheduler: Optional[SchedulerHandle] = None


def _mode() -> str:
    return "LIVE" if settings.LIVE_TRADING else "PAPER"


def _require_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        data = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        return int(data.sub)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")


@app.on_event("startup")
def _startup() -> None:
    global _scheduler
    dbmod.init_db()
    _scheduler = start_scheduler(_background_scan_new_coins)


@app.on_event("shutdown")
def _shutdown() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown()
        _scheduler = None


@app.get("/")
def root() -> dict:
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "mode": _mode(),
        "firebase": notifier.status(),
    }


@app.post("/auth/register", response_model=TokenResponse)
def register(payload: UserCreate) -> TokenResponse:
    if dbmod.get_user_by_email(payload.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    user_id = dbmod.create_user(payload.email, payload.username, hash_password(payload.password))
    return TokenResponse(access_token=create_access_token(str(user_id)))


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: UserLogin) -> TokenResponse:
    row = dbmod.get_user_by_email(payload.email)
    if not row or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(str(row["id"])))


@app.get("/auth/me")
def me(user_id: int = Depends(_require_user_id)) -> dict:
    row = dbmod.get_user_by_id(user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": row["id"], "email": row["email"], "username": row["username"], "created_at": row["created_at"]}


@app.get("/signal/{symbol}", response_model=SignalResponse)
async def signal(symbol: str, timeframe: str = Query(default="4h")) -> SignalResponse:
    interval = timeframe
    try:
        klines = await binance.get_klines(symbol, interval=interval, limit=120)
        closes = [k.close for k in klines]
        last_price = closes[-1] if closes else await binance.get_price(symbol)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Market data error: {e}")

    res = score_signal(symbol=symbol, timeframe=timeframe, closes=closes, last_price=last_price)
    dbmod.insert_signal_history(
        symbol=res.symbol,
        timeframe=res.timeframe,
        signal=res.signal,
        score=res.score,
        price=res.price,
        indicators_json=res.indicators_json(),
    )
    return SignalResponse(**res.__dict__)


@app.get("/scan")
async def scan(user_id: int = Depends(_require_user_id)) -> dict:
    results = []
    for symbol in settings.TOP_COINS:
        results.append((await signal(symbol=symbol, timeframe="4h")).model_dump())
    return {"user_id": user_id, "results": results, "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/history")
def history(user_id: int = Depends(_require_user_id), limit: int = 200) -> dict:
    _ = user_id
    rows = dbmod.list_signal_history(limit=limit)
    out = []
    for r in rows:
        out.append(
            {
                "symbol": r["symbol"],
                "timeframe": r["timeframe"],
                "signal": r["signal"],
                "score": r["score"],
                "price": r["price"],
                "indicators": json.loads(r["indicators_json"]),
                "timestamp": r["created_at"],
            }
        )
    return {"items": out}


@app.post("/user/trade", response_model=TradeResponse)
async def user_trade(payload: TradeRequest, user_id: int = Depends(_require_user_id)) -> TradeResponse:
    if settings.LIVE_TRADING:
        raise HTTPException(status_code=403, detail="Live trading disabled in this template")

    try:
        price = payload.price or await binance.get_price(payload.symbol)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Pricing error: {e}")

    trade_id = str(uuid.uuid4())
    dbmod.insert_trade(
        trade_id=trade_id,
        user_id=user_id,
        symbol=payload.symbol.upper(),
        side=payload.side,
        quantity=float(payload.quantity),
        price=float(price),
        status="FILLED",
        mode=_mode(),
    )
    warning = "Paper trade only. Validate strategy before risking capital."
    return TradeResponse(
        order_id=trade_id,
        symbol=payload.symbol.upper(),
        side=payload.side,
        quantity=float(payload.quantity),
        price=float(price),
        status="FILLED",
        mode=_mode(),
        timestamp=datetime.now(timezone.utc),
        warning=warning,
    )


@app.get("/user/history")
def user_history(user_id: int = Depends(_require_user_id), limit: int = 100) -> dict:
    rows = dbmod.list_user_trades(user_id=user_id, limit=limit)
    return {"items": [dict(r) for r in rows]}


@app.get("/user/portfolio", response_model=PortfolioResponse)
def user_portfolio(user_id: int = Depends(_require_user_id)) -> PortfolioResponse:
    rows = dbmod.list_user_trades(user_id=user_id, limit=1000)
    balance = 10_000.0
    positions: dict[str, float] = {}
    for r in rows[::-1]:
        qty = float(r["quantity"])
        sym = r["symbol"]
        if r["side"] == "BUY":
            positions[sym] = positions.get(sym, 0.0) + qty
            balance -= qty * float(r["price"])
        else:
            positions[sym] = positions.get(sym, 0.0) - qty
            balance += qty * float(r["price"])
    positions_list = [{"symbol": k, "qty": round(v, 8)} for k, v in positions.items() if abs(v) > 1e-12]
    return PortfolioResponse(
        balance_usdt=round(balance, 2),
        positions=positions_list,
        mode=_mode(),
        daily_trades_count=min(len(rows), settings.MAX_DAILY_TRADES),
        pnl_24h=0.0,
    )


@app.get("/alerts")
def alerts(user_id: int = Depends(_require_user_id), limit: int = 100) -> dict:
    _ = user_id
    rows = dbmod.list_alerts(limit=limit)
    return {"items": [dict(r) for r in rows]}


@app.post("/devices/register")
def register_device(token: str = Query(..., min_length=10)) -> dict:
    dbmod.upsert_device(token=token, user_id=None)
    return {"ok": True}


@app.post("/devices/unregister")
def unregister_device(token: str = Query(..., min_length=10)) -> dict:
    dbmod.delete_device(token=token)
    return {"ok": True}


@app.get("/devices")
def devices() -> dict:
    return {"items": [dict(r) for r in dbmod.list_devices()]}


@app.post("/user/devices/register")
def user_register_device(token: str = Query(..., min_length=10), user_id: int = Depends(_require_user_id)) -> dict:
    dbmod.upsert_device(token=token, user_id=user_id)
    return {"ok": True}


@app.get("/user/devices")
def user_devices(user_id: int = Depends(_require_user_id)) -> dict:
    return {"items": [dict(r) for r in dbmod.list_devices(user_id=user_id)]}


@app.get("/stablecoins")
async def stablecoins(user_id: int = Depends(_require_user_id)) -> dict:
    _ = user_id
    results = []
    for symbol in settings.STABLECOIN_PAIRS:
        try:
            tick = await binance.get_24h_ticker(symbol)
            results.append(
                {
                    "symbol": symbol,
                    "price": float(tick["lastPrice"]),
                    "change_pct": float(tick["priceChangePercent"]),
                    "volume_quote": float(tick.get("quoteVolume", 0.0)),
                }
            )
        except Exception:
            continue
    return {"items": results}


@app.get("/new-coins")
async def new_coins(user_id: int = Depends(_require_user_id)) -> dict:
    _ = user_id
    return await _scan_new_coins()


@app.get("/new-coins/{symbol}")
async def new_coin_detail(symbol: str, user_id: int = Depends(_require_user_id)) -> dict:
    _ = user_id
    tick = await binance.get_24h_ticker(symbol)
    return {"symbol": symbol.upper(), "ticker": tick, "risk_warning": settings.NEW_COIN_RISK_WARNING}


@app.post("/notify/test")
def notify_test(symbol: str = Query(default="BTCUSDT"), score: float = Query(default=85.0)) -> dict:
    title = f"{symbol.upper()} Alert - Score {score:.0f}"
    body = "Test notification from backend"
    res = notifier.send_to_tokens(title=title, body=body, data={"symbol": symbol.upper(), "score": score})
    return {"ok": res.ok, "detail": res.detail}


@app.post("/notify/trigger-scan")
async def notify_trigger_scan(request: Request) -> dict:
    _ = request
    out = await _scan_new_coins(send_notifications=True)
    return {"ok": True, "scan": out}


async def _scan_new_coins(send_notifications: bool = False) -> dict:
    tickers = await binance.all_24h_tickers()
    candidates = []
    for t in tickers:
        sym = t.get("symbol", "")
        if not sym.endswith("USDT"):
            continue
        try:
            change_pct = float(t.get("priceChangePercent", 0.0))
            quote_volume = float(t.get("quoteVolume", 0.0))
            last_price = float(t.get("lastPrice", 0.0))
        except Exception:
            continue
        if quote_volume < settings.NEW_COIN_MIN_VOLUME_USD:
            continue
        if change_pct < settings.NEW_COIN_MIN_CHANGE_PCT:
            continue
        candidates.append((sym, change_pct, quote_volume, last_price))

    candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
    candidates = candidates[: settings.NEW_COIN_MAX_RESULTS]

    items = []
    for sym, change_pct, quote_volume, last_price in candidates:
        score = min(100.0, 60.0 + (change_pct / 2))
        items.append(
            {
                "symbol": sym,
                "price": last_price,
                "price_change_pct": round(change_pct, 2),
                "volume_quote": round(quote_volume, 2),
                "score": round(score, 2),
                "risk_warning": settings.NEW_COIN_RISK_WARNING,
            }
        )
        if send_notifications and score >= 80:
            title = f"{sym} Alert - Score {score:.0f}"
            body = f"NEW COIN MOVE: +{change_pct:.1f}% in 24h. Tap to view details."
            res = notifier.send_to_tokens(
                title=title,
                body=body,
                data={"symbol": sym, "score": score, "price_change": change_pct, "category": "NEW_COIN"},
            )
            dbmod.insert_alert(symbol=sym, alert_type="SIGNAL", message=body, severity="INFO" if res.ok else "WARNING")
    return {"items": items, "timestamp": datetime.now(timezone.utc).isoformat()}


async def _background_scan_new_coins() -> None:
    try:
        await _scan_new_coins(send_notifications=True)
    except Exception:
        return

