# Prompt para OpenCode: Build del Proyecto ServiceNow Health

Quiero que construyas una aplicacion local full-stack para diagnosticar la salud de la accion de ServiceNow (NOW) usando el modelo documentado en `servicenow-stock-health-model.md` y el plan tecnico en `.omx/plans/servicenow-local-model-plan.md`.

## Objetivo

Crear una app local que pueda correr cuando quiera revisar el estatus de NOW. La app debe descargar/cachear documentos fuente, guardar metricas por trimestre, permitir completar manualmente KPIs que no se puedan parsear en v1, ejecutar reglas bear/base/bull y mostrar un dashboard claro.

No es asesoramiento financiero. La app debe mostrar fuentes y marcar datos faltantes en vez de inventar valores.

## Stack Obligatorio

- Frontend: Vue 3 + Vite + TypeScript.
- UI components: shadcn-vue.
- Styling: Tailwind CSS donde haga falta.
- Backend: FastAPI.
- Backend runtime: Docker container.
- Database: Postgres corriendo en Docker container.
- ORM: SQLAlchemy.
- Migrations: Alembic.
- DB inspection: external DBeaver connection to local Postgres port.
- Data sources: SEC EDGAR primero; ServiceNow Investor Relations solo como fallback controlado.

## Arquitectura Esperada

```text
servicenow-health/
  docker-compose.yml
  .env.example
  frontend/
    package.json
    vite.config.ts
    tailwind.config.ts
    components.json
    src/
      main.ts
      App.vue
      api/
        client.ts
      views/
        DashboardView.vue
        MetricsView.vue
        SourcesView.vue
        ReportsView.vue
      components/
        SignalCard.vue
        MetricTable.vue
        ValuationBandChart.vue
        SourceBadge.vue
        QuarterSelector.vue
        RunRefreshButton.vue
        ManualMetricDialog.vue
  backend/
    Dockerfile
    pyproject.toml
    alembic.ini
    alembic/
    src/
      api.py
      config.py
      db.py
      models.py
      schemas.py
      providers/
        sec_client.py
        price_client.py
      parsers/
        sec_facts.py
        earnings_release.py
        insider_forms.py
      model/
        rules.py
        valuation.py
        scoring.py
      storage.py
      report.py
  companies/
    servicenow/
      profile.yaml
      ir_adapter.py
      metrics_map.yaml
  data/
    raw/
      sec/
      ir/
    processed/
  reports/
  tests/
```

## Arquitectura Core vs Company-Specific

- `backend/src/` debe contener codigo reusable para cualquier compania: SEC client, storage, reglas, valuacion, reportes, parsers comunes.
- `companies/servicenow/` debe contener lo especifico de ServiceNow: CIK, ticker, fiscal calendar, URLs IR, aliases de metricas, selectors o regex especificos.
- No pongas un `ServiceNowInvestorRelationsClient` dentro del core reusable.
- Puedes definir una interfaz/protocolo generico para adapters de Investor Relations, pero la implementacion concreta de ServiceNow debe vivir en `companies/servicenow/`.

## Data Sources

Implementa SEC-first:

- Usar SEC submissions API para identificar filings de NOW.
- Usar SEC companyfacts API para facts XBRL disponibles.
- Descargar/cachear 10-Q, 10-K, 8-K exhibits y Form 4 cuando aplique.
- Usar un `User-Agent` configurable desde `.env`.
- Respetar rate limits y cache local.

Investor Relations:

- No hagas scraping agresivo en MVP.
- Usalo solo como fallback controlado para localizar earnings releases/materiales suplementarios si SEC no los trae convenientemente.
- Si un KPI no se puede extraer de forma confiable, marcalo como missing y permite entrada manual con fuente asociada.

## Docker Compose

Debe incluir al menos:

- `db`: Postgres container, volumen persistente, healthcheck.
- `backend`: FastAPI container, depende de `db` healthy.
- `frontend`: Vue dev server o build servido en container.
Backend debe conectarse a Postgres usando hostname interno `db`.
DBeaver debe poder conectarse desde el host a `localhost:5440` usando las credenciales del `.env`.

Incluye `.env.example` con:

```env
POSTGRES_USER=now_user
POSTGRES_PASSWORD=now_password
POSTGRES_DB=now_health
DATABASE_URL=postgresql+psycopg://now_user:now_password@db:5432/now_health
SEC_USER_AGENT=your-name your-email@example.com
```

## Database

Usa SQLAlchemy models + Alembic migrations como fuente canonica del schema.

Tablas minimas:

- `companies`
- `filings`
- `earnings_reports`
- `quarterly_metrics`
- `insider_transactions`
- `model_runs`
- `model_signal_results`
- `source_documents`

Campos importantes de `quarterly_metrics`:

- quarter
- fiscal_year
- share_price_used
- market_cap
- enterprise_value
- cash_and_equivalents
- subscription_revenue_growth
- current_rpo_growth
- current_rpo_growth_constant_currency
- renewal_rate
- gaap_net_income
- non_gaap_operating_margin
- free_cash_flow
- free_cash_flow_margin
- stock_based_compensation
- diluted_share_count
- buyback_authorization_remaining
- ai_acv_run_rate
- ai_acv_target
- creator_other_share
- customers_over_5m_acv
- named_competitive_wins
- named_displacements
- fy_growth_guidance
- fy_operating_margin_guidance
- fy27_growth_guidance

Cada metrica debe poder apuntar a una fuente/documento o quedar marcada como manual.

## API FastAPI

Implementa endpoints:

- `GET /health`
- `GET /api/companies`
- `GET /api/companies/{ticker}/quarters`
- `GET /api/companies/{ticker}/latest-diagnosis`
- `POST /api/companies/{ticker}/refresh`
- `GET /api/companies/{ticker}/metrics/{quarter}`
- `POST /api/companies/{ticker}/manual-metrics`
- `GET /api/reports`
- `GET /api/reports/{run_id}`
- `GET /api/sources/{source_id}`

## Modelo de Diagnostico

Implementa las reglas desde `servicenow-stock-health-model.md`.

Reglas principales:

- cRPO constant currency < 19% => bear.
- cRPO 19% a 21% => base.
- cRPO > 21% => bull.
- cRPO > 21.5% por dos trimestres => bull fuerte.
- Renewal < 96% => bear.
- Renewal 97% a 98% => base.
- Creator/other share flat o cayendo => bear.
- Creator/other share creciendo => base.
- Creator/other share > 25% => bull.
- Operating margin > 33% post-Armis => bull.
- Dos o mas exit signals en el mismo trimestre => recomendar revisar venta/reduccion.

Exit signals:

- cRPO < 19% por dos trimestres.
- Renewal rate < 96%.
- Named Fortune 500 displacement.
- Discretionary insider selling at depressed prices.
- FY27 guide < 16%.

Scale-in signals:

- cRPO > 21.5% por dos trimestres.
- Operating margin > 33% post-Armis.
- Creator/other share > 25%.
- Named enterprise wins against competitors.
- AI ACV target > $2B.

## Frontend

Usa Vue + shadcn-vue + Tailwind.

Vistas:

- Dashboard: diagnostico actual, estado bear/base/bull, senales, conclusion, ultimo refresh.
- Metrics: tabla editable de KPIs por trimestre, con missing/manual/source badges.
- Sources: documentos SEC/IR cacheados y estado de parsing.
- Reports: reportes generados.

Componentes:

- `SignalCard`
- `MetricTable`
- `ValuationBandChart`
- `SourceBadge`
- `QuarterSelector`
- `RunRefreshButton`
- `ManualMetricDialog`

Usa componentes shadcn-vue para Button, Card, Table, Dialog, Tabs, Badge, Alert, Select, Input, Skeleton y Tooltip.

La UI debe ser sobria, densa y orientada a decision. No crear landing page.

## MVP Acceptance Criteria

- `docker compose up` levanta Postgres, backend y frontend.
- Alembic puede crear las tablas en Postgres.
- FastAPI responde `GET /health`.
- La app registra ServiceNow/NOW con CIK y metadata base.
- `POST /api/companies/NOW/refresh` intenta traer/cachear filings SEC.
- Los documentos descargados quedan registrados en `source_documents` o `filings`.
- Los KPIs que no se pueden parsear quedan como missing, no inventados.
- El usuario puede ingresar metricas manuales por trimestre desde el frontend.
- El backend ejecuta el diagnostico bear/base/bull.
- Dashboard muestra resultado por senal y resumen final.
- Se puede generar un reporte Markdown en `reports/`.
- DBeaver puede conectarse a Postgres via `localhost:5440`.
- Tests cubren al menos reglas del modelo y storage basico.

## Constraints

- No uses APIs pagadas.
- No agregues dependencias innecesarias.
- Mantener diffs pequenos y codigo modular.
- No hardcodear secretos.
- No mezclar conocimiento especifico de ServiceNow dentro del core reusable.
- Si falta un dato, mostrarlo explicitamente como missing.
- Cada dato parseado/manual debe tener trazabilidad de fuente.

## Suggested Implementation Order

1. Scaffold Docker Compose, backend, frontend, database tooling.
2. Implement SQLAlchemy models + Alembic migration inicial.
3. Implement FastAPI health + companies endpoints.
4. Implement SEC client con cache local y User-Agent configurable.
5. Implement storage de source documents/filings.
6. Implement reglas del modelo con tests.
7. Implement manual metrics API.
8. Build Vue dashboard y metrics table.
9. Add report export.
10. Run end-to-end verification with `docker compose up`.
