# AGENTS.md

- This repo is Docker-first. `docker compose up --build` starts Postgres, runs Alembic, serves FastAPI on `http://localhost:8090`, and serves the Vue app on `http://localhost:5180`.
- There is no root JS task runner. Frontend commands run in `frontend/`; backend commands run from the repo root.

## Verify

- Frontend: `cd frontend && npm run build`
- Backend install for local work: `.venv/bin/pip install -e backend`
- Backend tests: `DATA_DIR=data REPORTS_DIR=reports COMPANIES_DIR=companies .venv/bin/python -m pytest`
- There is no repo lint, formatter, or frontend test config checked in. Do not invent `lint`, `format`, or `test` commands for the frontend.

## Env Gotchas

- Root `.env` is container-oriented: it points `DATA_DIR` and `REPORTS_DIR` at `/app/...`. Plain local `pytest` or local `uvicorn` will fail unless you override those paths to repo-local directories.
- `frontend/src/api/client.ts` defaults `VITE_API_BASE_URL` to `http://localhost:8000`, but Docker exposes the backend on host port `8090`. If you run Vite outside Docker against the Docker backend, set `VITE_API_BASE_URL=http://localhost:8090`.

## Architecture

- `backend/src/` is the reusable app core. Keep ServiceNow-specific logic under `companies/servicenow/`, not in the shared backend modules.
- The app is still effectively single-company. The backend seeds its default company from `companies/servicenow/profile.yaml`, and the frontend hardcodes ticker `NOW` in `DashboardView`, `MetricsView`, and `SourcesView`.
- SEC is the primary source. `POST /api/companies/NOW/refresh` caches SEC data under `data/raw/sec`.
- IR scraping is intentionally not automated in the MVP. `companies/servicenow/ir_adapter.py` returns `manual_required`; missing KPIs are expected to stay missing until manual entry.
- Reports are generated as Markdown files under `reports/`.

## Backend Runtime

- The container startup command is `alembic -c backend/alembic.ini upgrade head && uvicorn src.api:app --host 0.0.0.0 --port 8000 --app-dir backend`.
- If you change schema or models, keep Alembic migrations in sync; container startup applies migrations automatically.
