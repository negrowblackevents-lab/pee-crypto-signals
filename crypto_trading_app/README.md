# Crypto Signal Engine (Flutter)

Placeholder folder for the Flutter client described in `COMPLETE_PROJECT.md`.

Recommended next step:

```bash
flutter create crypto_trading_app
```

Then implement:
- JWT auth + storage
- Signal list/detail screens (use `/scan`, `/signal/{symbol}`)
- Paper trading UI (use `/user/trade`, `/user/portfolio`, `/user/history`)
- FCM device token registration (use `/devices/register` or `/user/devices/register`)

## Frontend API base URL

Create a local `.env` from `.env.example` and configure the backend endpoint:

```bash
cp crypto_trading_app/.env.example crypto_trading_app/.env
```

If you run the backend locally, use:

```bash
BACKEND_API_BASE_URL=http://127.0.0.1:8000
```

Then reference `BACKEND_API_BASE_URL` in your Flutter HTTP client or environment config.

