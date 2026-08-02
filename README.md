# Kenepa

Kenepa is a local full-stack diagnostics app for ServiceNow (`NOW`). It pulls SEC data, preserves source traceability, keeps missing KPIs explicit, accepts manual metric entry for non-parsed fields, and evaluates the stock-health rules documented in `docs/servicenow-stock-health-model.md`.

## What it does

- Seeds a default company profile for ServiceNow from `companies/servicenow/profile.yaml`
- Fetches and caches SEC submissions and companyfacts data under `data/raw/sec`
- Stores quarterly metrics, source documents, filings, and model runs in Postgres
- Lets you add manual KPIs with a required source label and optional URL/notes
- Generates a diagnosis with bear/base/bull signals plus exit and scale-in checklists
- Writes Markdown reports to `reports/`

## Current scope

The current app is built around a single company: ServiceNow (`NOW`).

- Backend data seeding comes from `companies/servicenow/`
- The frontend views currently target `NOW`
- The model logic is based on the ServiceNow thesis in `docs/servicenow-stock-health-model.md`

## Stack

- Backend: FastAPI, SQLAlchemy, Alembic
- Frontend: Vue 3, Vite, TypeScript, Tailwind CSS
- Database: Postgres 16
- Runtime: Docker Compose for the default local workflow

## Quick start

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Set a valid SEC user agent in `.env`.

The SEC expects a real contact string, for example:

```env
SEC_USER_AGENT=Your Name your-email@example.com
```

3. Start the stack:

```bash
docker compose up --build
```

4. Open the app:

- Frontend: `http://localhost:5180`
- Backend health check: `http://localhost:8090/health`
- Backend OpenAPI docs: `http://localhost:8090/docs`

The backend container runs Alembic migrations automatically on startup.

## Default local configuration

If you use `.env.example` as-is, the default connection values are:

- Postgres host: `localhost`
- Postgres port: `5440`
- Database: `kenepa`
- User: `user`
- Password: `password`

The main environment variables are:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_PORT`
- `DATABASE_URL`
- `SEC_USER_AGENT`
- `DATA_DIR`
- `REPORTS_DIR`

## DBeaver

Connect with the values from your `.env` file.

With the defaults from `.env.example`:

- Host: `localhost`
- Port: `5440`
- Database: `kenepa`
- User: `user`
- Password: `password`

## Repo layout

```text
backend/                 FastAPI app, models, storage, parsers, Alembic
frontend/                Vue app and UI
companies/servicenow/    Seed company profile and metric mapping
data/                    Local cached inputs and processed data
reports/                 Generated Markdown reports
docs/                    Model notes and supporting documents
tests/                   Backend tests
```

## Key backend endpoints

- `GET /health`
- `GET /api/companies`
- `GET /api/companies/{ticker}/quarters`
- `GET /api/companies/{ticker}/latest-diagnosis`
- `POST /api/companies/{ticker}/refresh`
- `GET /api/companies/{ticker}/metrics/{quarter}`
- `POST /api/companies/{ticker}/manual-metrics`
- `GET /api/companies/{ticker}/sources`
- `GET /api/reports`
- `GET /api/reports/{run_id}`

Useful example:

```bash
curl -X POST "http://localhost:8090/api/companies/NOW/refresh?limit=20"
```

## Local development without Docker

### Backend

```bash
pip install -e backend
alembic -c backend/alembic.ini upgrade head
uvicorn src.api:app --host 0.0.0.0 --port 8090 --app-dir backend
```

Set `DATABASE_URL` and the other environment variables before starting the API.

### Frontend

```bash
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:8090 npm run dev -- --host 0.0.0.0
```

If you do not set `VITE_API_BASE_URL`, the frontend client falls back to `http://localhost:8000`.

## Testing

Run the backend test suite from the repo root:

```bash
pytest
```

## Data and outputs

- SEC API caches are written under `data/raw/sec`
- Generated reports are written under `reports/`
- Manual metric entries keep source metadata so missing or hand-entered values remain auditable

## Known limitations

- The app currently focuses on one company, `NOW`
- Some operating KPIs are not reliably parsed from SEC data and must be entered manually
- Investor relations and earnings-release parsing is still best-effort compared with the SEC-first path

## Related files

- `docs/servicenow-stock-health-model.md`: thesis and rule definitions
- `companies/servicenow/metrics_map.yaml`: metric-to-source mapping
- `backend/src/api.py`: API surface
