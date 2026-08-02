FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend:/app

COPY backend /app/backend
COPY companies /app/companies

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e /app/backend

RUN mkdir -p /app/data/raw/sec /app/data/raw/ir /app/data/processed /app/reports

EXPOSE 8000

CMD ["sh", "-c", "alembic -c backend/alembic.ini upgrade head && uvicorn src.api:app --host 0.0.0.0 --port 8000 --app-dir backend"]
