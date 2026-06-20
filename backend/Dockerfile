# DIALECTA backend — production image
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better layer caching
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install -e .

# Copy source
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts
COPY tests ./tests

# Non-root user
RUN useradd --create-home --shell /bin/bash dialecta \
    && chown -R dialecta:dialecta /app
USER dialecta

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=4s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Run migrations then start uvicorn
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]
