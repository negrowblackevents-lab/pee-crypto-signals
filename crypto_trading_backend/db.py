from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional


DB_PATH = Path(__file__).resolve().parent / "app.sqlite3"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL,
                mode TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS devices (
                token TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS signal_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                signal TEXT NOT NULL,
                score REAL NOT NULL,
                price REAL NOT NULL,
                indicators_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    finally:
        conn.close()


def create_user(email: str, username: str, password_hash: str) -> int:
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO users(email, username, password_hash, created_at) VALUES(?,?,?,?)",
            (email.lower().strip(), username.strip(), password_hash, _utc_now_iso()),
        )
        return int(cur.lastrowid)


def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    with db() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),)).fetchone()


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    with db() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def list_user_trades(user_id: int, limit: int = 100) -> list[sqlite3.Row]:
    with db() as conn:
        return conn.execute(
            "SELECT * FROM trades WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()


def insert_trade(
    trade_id: str,
    user_id: int,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    status: str,
    mode: str,
) -> None:
    with db() as conn:
        conn.execute(
            """
            INSERT INTO trades(id, user_id, symbol, side, quantity, price, status, mode, created_at)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (trade_id, user_id, symbol, side, quantity, price, status, mode, _utc_now_iso()),
        )


def upsert_device(token: str, user_id: Optional[int]) -> None:
    with db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO devices(token, user_id, created_at) VALUES(?,?,?)",
            (token, user_id, _utc_now_iso()),
        )


def delete_device(token: str) -> None:
    with db() as conn:
        conn.execute("DELETE FROM devices WHERE token = ?", (token,))


def list_devices(user_id: Optional[int] = None) -> list[sqlite3.Row]:
    with db() as conn:
        if user_id is None:
            return conn.execute("SELECT * FROM devices ORDER BY created_at DESC").fetchall()
        return conn.execute(
            "SELECT * FROM devices WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()


def insert_alert(symbol: str, alert_type: str, message: str, severity: str) -> None:
    with db() as conn:
        conn.execute(
            "INSERT INTO alerts(symbol, alert_type, message, severity, created_at) VALUES(?,?,?,?,?)",
            (symbol, alert_type, message, severity, _utc_now_iso()),
        )


def list_alerts(limit: int = 100) -> list[sqlite3.Row]:
    with db() as conn:
        return conn.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()


def insert_signal_history(
    symbol: str, timeframe: str, signal: str, score: float, price: float, indicators_json: str
) -> None:
    with db() as conn:
        conn.execute(
            """
            INSERT INTO signal_history(symbol, timeframe, signal, score, price, indicators_json, created_at)
            VALUES(?,?,?,?,?,?,?)
            """,
            (symbol, timeframe, signal, score, price, indicators_json, _utc_now_iso()),
        )


def list_signal_history(limit: int = 200) -> list[sqlite3.Row]:
    with db() as conn:
        return conn.execute("SELECT * FROM signal_history ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()

