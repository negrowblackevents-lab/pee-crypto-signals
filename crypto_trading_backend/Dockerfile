FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Install system deps (if needed)
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY crypto_trading_backend/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy app as a package so relative imports keep working.
COPY crypto_trading_backend /app/crypto_trading_backend
COPY crypto_trading_backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Do NOT bake secrets into the image. Provide service account via bind mount, Docker secret, or env var.
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "crypto_trading_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
