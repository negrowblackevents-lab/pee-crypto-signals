from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class SignalRequest(BaseModel):
    symbol: str = Field(..., examples=["BTCUSDT"])
    timeframe: str = Field(default="4h", examples=["4h"])


class TradeRequest(BaseModel):
    symbol: str = Field(..., examples=["BTCUSDT"])
    side: Literal["BUY", "SELL"] = Field(..., examples=["BUY"])
    quantity: float = Field(..., gt=0, examples=[0.01])
    price: Optional[float] = Field(None, examples=[65000.0])
    order_type: Literal["MARKET", "LIMIT"] = Field(default="MARKET")


class SignalResponse(BaseModel):
    symbol: str
    timeframe: str
    signal: Literal["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]
    score: float
    price: float
    indicators: dict
    timestamp: datetime
    risk_note: str


class TradeResponse(BaseModel):
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    status: str
    mode: Literal["PAPER", "LIVE"]
    timestamp: datetime
    warning: Optional[str] = None


class PortfolioResponse(BaseModel):
    balance_usdt: float
    positions: list[dict]
    mode: Literal["PAPER", "LIVE"]
    daily_trades_count: int
    pnl_24h: float


class Alert(BaseModel):
    symbol: str
    alert_type: Literal["SIGNAL", "PRICE", "STOP_LOSS", "TAKE_PROFIT"]
    message: str
    severity: Literal["INFO", "WARNING", "CRITICAL"]
    timestamp: datetime


class UserCreate(BaseModel):
    email: str
    username: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

