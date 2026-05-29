from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import db as dbmod


@dataclass
class NotificationResult:
    ok: bool
    detail: str


class Notifier:
    def __init__(self) -> None:
        self._firebase_ready = False
        self._init_detail = "FCM not configured"
        self._try_init_firebase()

    def _try_init_firebase(self) -> None:
        path = Path(__file__).resolve().parent / "firebase-service-account.json"
        if not path.exists():
            return
        try:
            import firebase_admin
            from firebase_admin import credentials

            if not firebase_admin._apps:
                cred = credentials.Certificate(str(path))
                firebase_admin.initialize_app(cred)
            self._firebase_ready = True
            self._init_detail = "Firebase initialized"
        except Exception as e:  # noqa: BLE001
            self._firebase_ready = False
            self._init_detail = f"Firebase init failed: {e}"

    def status(self) -> str:
        return self._init_detail

    def send_to_tokens(self, title: str, body: str, data: Optional[dict] = None) -> NotificationResult:
        tokens = [r["token"] for r in dbmod.list_devices()]
        if not tokens:
            return NotificationResult(ok=True, detail="No devices registered")
        if not self._firebase_ready:
            return NotificationResult(ok=False, detail=self._init_detail)
        try:
            from firebase_admin import messaging

            message = messaging.MulticastMessage(
                tokens=tokens,
                notification=messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in (data or {}).items()},
            )
            resp = messaging.send_multicast(message)
            return NotificationResult(ok=True, detail=f"sent={resp.success_count} failed={resp.failure_count}")
        except Exception as e:  # noqa: BLE001
            return NotificationResult(ok=False, detail=str(e))

