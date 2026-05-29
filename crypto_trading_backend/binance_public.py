from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

_BASE_URL = "https://api.binance.com"


@dataclass(frozen=True)
class Kline:
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: int


class BinancePublicClient:
    def __init__(self, timeout_seconds: float = 10.0):
        self._timeout = timeout_seconds

    async def get_price(self, symbol: str) -> float:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.get(f"{_BASE_URL}/api/v3/ticker/price", params={"symbol": symbol.upper()})
            r.raise_for_status()
            return float(r.json()["price"])

    async def get_24h_ticker(self, symbol: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.get(f"{_BASE_URL}/api/v3/ticker/24hr", params={"symbol": symbol.upper()})
            r.raise_for_status()
            return dict(r.json())

    async def get_klines(self, symbol: str, interval: str, limit: int = 200) -> list[Kline]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.get(
                f"{_BASE_URL}/api/v3/klines",
                params={"symbol": symbol.upper(), "interval": interval, "limit": limit},
            )
            r.raise_for_status()
            data = r.json()
        klines: list[Kline] = []
        for row in data:
            klines.append(
                Kline(
                    open_time=int(row[0]),
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=float(row[5]),
                    close_time=int(row[6]),
                )
            )
        return klines

    async def exchange_info(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.get(f"{_BASE_URL}/api/v3/exchangeInfo")
            r.raise_for_status()
            return dict(r.json())

    async def all_24h_tickers(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.get(f"{_BASE_URL}/api/v3/ticker/24hr")
            r.raise_for_status()
            data = r.json()
            if not isinstance(data, list):
                raise ValueError("Unexpected response")
            return [dict(x) for x in data]

