# Crypto Signal Engine (Backend)

FastAPI backend scaffold for signal analysis, paper trading, new coin scanning, and optional Firebase push notifications.

## Quick start (Windows / PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r crypto_trading_backend/requirements.txt
Copy-Item crypto_trading_backend/.env.example crypto_trading_backend/.env
uvicorn crypto_trading_backend.main:app --reload
```

Open `http://127.0.0.1:8000/` and the docs at `http://127.0.0.1:8000/docs`.

## Configure FCM (Push Notifications)

This backend can send push notifications via Firebase Cloud Messaging (FCM) using the Firebase Admin SDK.

1) Create a Firebase project
1. Firebase Console -> **Add project**
2. Pick a project name (optionally enable Analytics) and finish creation

2) Enable/confirm Cloud Messaging for the project
1. Firebase Console -> your project
2. Gear icon -> **Project settings**
3. **Cloud Messaging** tab
4. If you see a prompt to enable messaging/APIs, follow it (it may open Google Cloud Console to enable the **Firebase Cloud Messaging API**)

3) Create a service account key for the server (Admin SDK)
1. Firebase Console -> **Project settings** -> **Service accounts**
2. Under **Firebase Admin SDK**, click **Generate new private key**
3. Save the JSON file as `crypto_trading_backend/firebase-service-account.json` (do not commit it; it is already ignored by `crypto_trading_backend/.gitignore`)

4) Install the optional dependency:

```powershell
.\.venv\Scripts\python -m pip install -r crypto_trading_backend/requirements-fcm.txt
```[]()

5) Restart the server and verify `GET /` shows `firebase: "Firebase initialized"`.
6) Register a device token (from your Flutter app) and test:

```powershell
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/devices/register?token=YOUR_FCM_TOKEN"
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/notify/test?symbol=BTCUSDT&score=85"
```

## Notes

- Paper trading is the only enabled trading mode in this template.
- To enable push notifications, place `firebase-service-account.json` in `crypto_trading_backend/`.
