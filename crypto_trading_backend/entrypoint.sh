#!/bin/sh
set -e

SECRETS_PATH="/run/secrets/firebase-service-account.json"
TARGET_PATH="/app/crypto_trading_backend/firebase-service-account.json"

if [ -n "${FIREBASE_SERVICE_ACCOUNT_JSON:-}" ] && [ ! -f "$TARGET_PATH" ]; then
  echo "$FIREBASE_SERVICE_ACCOUNT_JSON" > "$TARGET_PATH"
  chmod 600 "$TARGET_PATH"
  echo "Wrote Firebase service account JSON from env var."
fi

if [ -n "${FIREBASE_SERVICE_ACCOUNT_PATH:-}" ] && [ -f "$FIREBASE_SERVICE_ACCOUNT_PATH" ] && [ ! -f "$TARGET_PATH" ]; then
  cp "$FIREBASE_SERVICE_ACCOUNT_PATH" "$TARGET_PATH"
  chmod 600 "$TARGET_PATH"
  echo "Copied Firebase service account JSON from FIREBASE_SERVICE_ACCOUNT_PATH."
fi

if [ -f "$SECRETS_PATH" ] && [ ! -f "$TARGET_PATH" ]; then
  cp "$SECRETS_PATH" "$TARGET_PATH"
  chmod 600 "$TARGET_PATH"
  echo "Copied Firebase service account JSON from Docker secrets path."
fi

exec "$@"
