from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from .config import settings

SignalLabel = Literal["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]


@dataclass(frozen=True)
class SignalResult:
    symbol: str
    timeframe: str
    signal: SignalLabel
    score: float
    price: float
    indicators: dict
    timestamp: datetime
    risk_note: str

    def indicators_json(self) -> str:
        return json.dumps(self.indicators, separators=(",", ":"), sort_keys=True)


def _rsi(closes: list[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return float("nan")
    gains: list[float] = []
    losses: list[float] = []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(delta if delta > 0 else 0.0)
        losses.append(-delta if delta < 0 else 0.0)
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def _ema(values: list[float], period: int) -> float:
    if not values:
        return float("nan")
    alpha = 2 / (period + 1)
    ema = float(values[0])
    for v in values[1:]:
        ema = alpha * v + (1 - alpha) * ema
    return float(ema)


def score_signal(symbol: str, timeframe: str, closes: list[float], last_price: float) -> SignalResult:
    rsi = _rsi(closes)
    ema_fast = _ema(closes[-50:], 12) if len(closes) >= 12 else float("nan")
    ema_slow = _ema(closes[-50:], 26) if len(closes) >= 26 else float("nan")
    macd = ema_fast - ema_slow if (ema_fast == ema_fast and ema_slow == ema_slow) else float("nan")
    trend = 0.0
    if len(closes) >= 50 and closes[-50] != 0:
        trend = float((closes[-1] - closes[-50]) / closes[-50] * 100.0)

    score = 50.0
    if rsi == rsi:
        if rsi < 30:
            score += 20
        elif rsi > 70:
            score -= 20
        else:
            score += (50 - abs(rsi - 50)) / 50 * 5
    if macd == macd:
        score += max(min(macd * 10, 10), -10)
    score += max(min(trend, 10), -10)

    score = float(max(min(score, 100.0), 0.0))
    if score >= 85:
        label: SignalLabel = "STRONG_BUY"
    elif score >= 70:
        label = "BUY"
    elif score <= 15:
        label = "STRONG_SELL"
    elif score <= 30:
        label = "SELL"
    else:
        label = "HOLD"

    risk_note = (
        f"PAPER mode: {settings.PAPER_TRADING}. Live mode: {settings.LIVE_TRADING}. "
        "Signals are probabilistic; use stops and position sizing."
    )
    indicators = {
        "rsi14": None if rsi != rsi else round(float(rsi), 2),
        "macd": None if macd != macd else round(float(macd), 6),
        "trend_50": round(float(trend), 3),
    }
    return SignalResult(
        symbol=symbol.upper(),
        timeframe=timeframe,
        signal=label,
        score=round(score, 2),
        price=float(last_price),
        indicators=indicators,
        timestamp=datetime.now(timezone.utc),
        risk_note=risk_note,
    )
