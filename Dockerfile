FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UNISHORT_DATABASE_URL=sqlite:////data/unishort.db \
    UNISHORT_BASE_URL=http://localhost:8000

WORKDIR /app

RUN useradd --create-home --uid 10001 unishort \
    && mkdir -p /data \
    && chown -R unishort:unishort /app /data

COPY backend/requirements.txt ./backend/requirements.txt
COPY requirements.lock ./requirements.lock
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.lock

COPY backend ./backend
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

USER unishort

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else 1)"]

CMD ["sh", "-c", "python -m alembic upgrade head && exec python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --no-access-log"]
