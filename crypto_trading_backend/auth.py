from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from pydantic import BaseModel
from passlib.hash import pbkdf2_sha256


SECRET_KEY = "change-me-in-production-use-256-bit-random-string"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


class TokenData(BaseModel):
    sub: str


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pbkdf2_sha256.verify(password, password_hash)


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + pad).encode("ascii"))


def _sign(message: bytes) -> str:
    sig = hmac.new(SECRET_KEY.encode("utf-8"), message, hashlib.sha256).digest()
    return _b64url_encode(sig)


def _encode_jwt(payload: dict[str, Any]) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True, default=str).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    return f"{header_b64}.{payload_b64}.{_sign(signing_input)}"


def _decode_jwt(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token format")
    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected = _sign(signing_input)
    if not hmac.compare_digest(expected, sig_b64):
        raise ValueError("Bad signature")
    payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    exp = payload.get("exp")
    if not exp:
        raise ValueError("Missing exp")
    exp_dt = datetime.fromisoformat(exp) if isinstance(exp, str) else datetime.fromtimestamp(float(exp), tz=timezone.utc)
    if exp_dt.tzinfo is None:
        exp_dt = exp_dt.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) >= exp_dt:
        raise ValueError("Token expired")
    return payload


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire.isoformat()}
    return _encode_jwt(to_encode)


def decode_token(token: str) -> TokenData:
    try:
        payload = _decode_jwt(token)
        sub = payload.get("sub")
        if not sub:
            raise ValueError("Missing sub")
        return TokenData(sub=sub)
    except ValueError as e:
        raise ValueError("Invalid token") from e
