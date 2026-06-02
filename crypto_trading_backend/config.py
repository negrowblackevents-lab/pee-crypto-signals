"""
Configuration - PAPER TRADING IS DEFAULT.
Set LIVE_TRADING=false always until you fully backtest and accept risks.
"""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    PAPER_TRADING: bool = os.getenv("PAPER_TRADING", "true").lower() == "true"
    LIVE_TRADING: bool = os.getenv("LIVE_TRADING", "false").lower() == "true"

    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET_KEY: str = os.getenv("BINANCE_SECRET_KEY", "")

    MAX_POSITION_PCT: float = float(os.getenv("MAX_POSITION_PCT", "0.05"))
    STOP_LOSS_PCT: float = float(os.getenv("STOP_LOSS_PCT", "0.03"))
    TAKE_PROFIT_PCT: float = float(os.getenv("TAKE_PROFIT_PCT", "0.06"))
    MAX_DAILY_TRADES: int = int(os.getenv("MAX_DAILY_TRADES", "5"))
    MIN_SIGNAL_SCORE: float = float(os.getenv("MIN_SIGNAL_SCORE", "75.0"))

    TIMEFRAMES: list[str] = ["1h", "4h", "1d"]
    TOP_COINS: list[str] = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"]
    STABLECOIN_PAIRS: list[str] = ["USDCUSDT", "FDUSDUSDT", "TUSDUSDT", "DAIUSDT"]

    APP_NAME: str = "CryptoSignal Engine"
    VERSION: str = "1.0.0"
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    UPDATE_INTERVAL_SECONDS: int = int(os.getenv("UPDATE_INTERVAL_SECONDS", "300"))

    NEW_COIN_MIN_VOLUME_USD: float = float(os.getenv("NEW_COIN_MIN_VOLUME_USD", "5000000"))
    NEW_COIN_MIN_CHANGE_PCT: float = float(os.getenv("NEW_COIN_MIN_CHANGE_PCT", "15.0"))
    NEW_COIN_MAX_RESULTS: int = int(os.getenv("NEW_COIN_MAX_RESULTS", "10"))
    NEW_COIN_RISK_WARNING: str = (
        "New coins can lose 90%+ value in hours. Never invest more than you can afford to lose completely."
    )


settings = Settings()

