# Deployment Guide

This repo contains a FastAPI backend in `crypto_trading_backend/`. Below are quick deployment options.

## Local (Docker Compose)

Build and run locally with Docker Compose:

```bash
docker compose up --build -d
```

- The backend will be reachable at `http://localhost:8001`.
- The compose file mounts `firebase-service-account.json` and `app.sqlite3` from the repo root. Do NOT commit secrets to git.
- The Dockerfile also supports runtime secret injection for Firebase credentials via:
  - `FIREBASE_SERVICE_ACCOUNT_PATH=/run/secrets/firebase-service-account.json`, or
  - `FIREBASE_SERVICE_ACCOUNT_JSON` containing the JSON payload.

## Container registry (GitHub Container Registry)

1. Push to `main` branch. The GitHub Action `.github/workflows/docker-image.yml` builds and pushes the image to `ghcr.io/<owner>/<repo>:latest` if `GITHUB_TOKEN` is available.
2. Add `CR_PAT` or `GITHUB_TOKEN` as repository secrets to allow pushing to GHCR for non-owner accounts.

## Render / Heroku / Cloud Run (example)

### Render

1. Create a new Web Service.
2. Connect your GitHub repository.
3. For the Docker build, point to `crypto_trading_backend/Dockerfile`.
4. Set the start command to:
   - `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Add a secret or file for `firebase-service-account.json` in Render and mount it at `/app/firebase-service-account.json`.

### Heroku

Heroku can deploy the Docker image from this repo using the Container Registry:

```bash
heroku container:login
docker build -t registry.heroku.com/<app-name>/web -f crypto_trading_backend/Dockerfile .
docker push registry.heroku.com/<app-name>/web
heroku container:release web --app <app-name>
```

Then add any required config vars from `.env` in the Heroku dashboard.

### GCP Cloud Run

1. Build and push the image to Artifact Registry or Google Container Registry.
2. Deploy to Cloud Run with port `8000`.
3. Configure secrets so `firebase-service-account.json` is available at `/app/firebase-service-account.json` or update the app to load credentials from environment variables.

## Secrets and service account

- Provide `firebase-service-account.json` via your host mount, cloud secret manager, or platform secret. Do NOT include it in the repository.

## TLS / Domain

- For production, put the container behind a reverse proxy or managed platform (Render, Cloud Run, Azure) to obtain TLS automatically.

## Next steps I can take for you

- Build the Docker image locally and run it (I can run `docker` commands if you want).
- Create a GitHub repo and push the workflow (requires your confirmation).
- Add Helm chart or Kubernetes manifest for cluster deploys.

