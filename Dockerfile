ARG VARIANT=3.12.8-slim-bookworm

# Base stage
FROM python:${VARIANT} AS base
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1
COPY gunicorn.conf.py pyproject.toml ./

## Dev with mounted volumes and dev deps
FROM base AS dev
COPY requirements-dev.lock  ./
RUN pip install -r requirements-dev.lock
VOLUME ["/app/src", "/app/tests"]
CMD ["gunicorn", "trace_deidentifier.api.main:app"]

# Standalone dev with code included
FROM dev AS dev-standalone
COPY src ./src
COPY tests ./tests

## Prod with copied code and minimal deps
FROM base AS prod
COPY requirements.lock ./
RUN pip install --no-deps --no-compile -r requirements.lock
COPY src ./src
CMD ["gunicorn", "trace_deidentifier.api.main:app"]
