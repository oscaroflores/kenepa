# Plan Tecnico: Aplicacion Local para Diagnosticar ServiceNow (NOW)

## Decision Recomendada

Construir una aplicacion local full-stack con:

- **Frontend:** Vue 3 + Vite + TypeScript.
- **Componentes UI:** shadcn-vue.
- **Styling:** Tailwind CSS donde haga falta.
- **Backend:** FastAPI.
- **Runtime backend:** Docker container.
- **Database:** Postgres.
- **Runtime database:** Docker container via Docker Compose.
- **ORM/Migrations:** SQLAlchemy + Alembic como fuente canonica del schema.
- **Data pipeline:** Python modular dentro del backend.
- **Parsing:** requests, pandas, BeautifulSoup, pdfplumber, sec-edgar-downloader o cliente propio liviano para SEC.
- **Reportes:** Markdown/HTML exportable por corrida.
- **Fuentes oficiales:** SEC EDGAR + ServiceNow Investor Relations fallback.
- **Arquitectura:** core reusable para cualquier compania + adapters especificos por compania.

Esta combinacion prioriza bajo costo, auditabilidad, una UI local mas pulida que Streamlit y una base extensible para multiples companias.

## Drivers

1. **Costo recurrente bajo:** evitar APIs que cobren por consulta.
2. **Datos oficiales primero:** SEC e Investor Relations antes que agregadores financieros.
3. **Reproducibilidad:** cada corrida debe guardar los inputs usados.
4. **Diagnostico simple:** el modelo debe clasificar bear/base/bull con reglas visibles.
5. **Escalabilidad moderada:** empezar con NOW, pero dejar la estructura lista para otros tickers.
6. **Separacion de responsabilidades:** FastAPI ejecuta el modelo y la ingesta; Vue muestra y edita; Postgres persiste; DBeaver puede inspeccionar la base via puerto local.

## Fuentes de Datos

Principio:

- SEC EDGAR debe ser la fuente primaria por defecto.
- Investor Relations no debe ser una dependencia obligatoria para datos que ya esten disponibles en SEC.
- El adapter de Investor Relations se usa solo para gaps: documentos no adjuntos a SEC, paginas de quarterly results, presentaciones, prepared remarks, webcast links o KPIs operativos que no esten estructurados en XBRL.

### 1. SEC EDGAR API

Uso:

- 10-K y 10-Q oficiales.
- Company Facts XBRL.
- Submissions API para detectar filings nuevos.
- Form 4 para insider transactions.
- 8-K cuando ServiceNow adjunte earnings releases, presentaciones o reconciliaciones non-GAAP.

Ventajas:

- Oficial.
- Gratis.
- Sin API key.
- JSON disponible para companyfacts/submissions.
- Actualizacion casi en tiempo real para filings.

Limitaciones:

- Requiere User-Agent identificable.
- Hay que respetar rate limits.
- No todo KPI operativo aparece como XBRL facil de mapear.
- cRPO constant currency, AI ACV y commentary pueden requerir parsing de press releases.
- Algunos materiales pueden ser "furnished" en 8-K y no aparecer como fact estructurado en Company Facts; aun asi el documento puede estar en EDGAR como exhibit.

### 2. ServiceNow Investor Relations

Uso:

- Earnings releases.
- Quarterly results.
- Investor presentations.
- Prepared remarks o earnings webcast links cuando esten disponibles.
- Non-GAAP reconciliations.
- cRPO, RPO, ACV, customer counts, margin guidance y comentarios de AI.

Ventajas:

- Fuente primaria de la compania.
- Gratis.
- Mejor para KPIs operativos especificos del modelo.
- Sirve como fallback o fuente complementaria cuando SEC no trae el material en formato facil de localizar.

Limitaciones:

- Puede requerir scraping de HTML o PDF.
- Formato puede cambiar entre trimestres.
- Algunos datos estaran en texto no estructurado.
- Debe vivir como adapter especifico de ServiceNow, no como core reusable.

Decision inicial:

- No construir scraping agresivo de Investor Relations en el MVP.
- Primero intentar resolver el trimestre con SEC: submissions, 10-Q/10-K, 8-K exhibits, Form 4 y Company Facts.
- Usar Investor Relations solo como fallback controlado para localizar el earnings release o materiales suplementarios si no estan disponibles de forma conveniente en SEC.

### 3. Precio de Accion

Recomendacion inicial:

- Permitir entrada manual de precio.
- Agregar proveedor opcional gratuito para conveniencia, no como fuente canonica.

Opciones:

- Stooq CSV para precio diario.
- yfinance como conveniencia no oficial.
- Nasdaq/NYSE pages solo como fallback manual.

Razon:

El diagnostico principal depende mas de earnings, cRPO, renewal, AI ACV y guidance que de precio intradia. Para evitar fragilidad y terminos inciertos, el MVP puede aceptar precio manual y calcular rangos con ese input.

## Arquitectura Propuesta

```text
servicenow-health/
  docker-compose.yml
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
  backend/
    Dockerfile
    pyproject.toml
    src/
      api.py
      config.py
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

Regla de arquitectura:

- `backend/src/` contiene codigo generico reusable: SEC, storage, reglas del modelo, valuacion, reportes, parsing comun.
- `companies/<company>/` contiene conocimiento especifico de una compania: URLs de investor relations, selectors, regex, aliases de metricas, CIK, ticker, fiscal calendar y cualquier excepcion.
- Un `InvestorRelationsAdapter` puede existir como interfaz generica, pero cada implementacion concreta vive fuera del core reusable.
- Para ServiceNow, el adapter especifico seria `companies/servicenow/ir_adapter.py`.
- SQLAlchemy + Alembic son la fuente canonica del schema y de las migraciones.
- DBeaver se usa fuera del repo para inspeccionar Postgres usando el puerto local expuesto por Docker Compose.

## Flujo de la Aplicacion

1. Usuario corre `docker compose up`.
2. Postgres levanta como container con volumen persistente.
3. Backend FastAPI levanta en container.
4. Frontend Vue levanta localmente o en container segun el modo de desarrollo.
5. Usuario abre el dashboard Vue.
6. App muestra ultimo trimestre disponible y estado de cache.
7. Usuario elige:
   - refrescar datos desde fuentes oficiales;
   - usar cache local;
   - ingresar datos manuales faltantes.
8. Backend descarga filings y earnings releases nuevos.
9. Parsers extraen KPIs.
10. Reglas clasifican cada senal como bear/base/bull.
11. Dashboard muestra:
   - resumen de estado;
   - tabla de KPIs;
   - senales rotas;
   - triggers de salida;
   - triggers de scale-in;
   - valuacion por escenarios;
   - fuentes usadas.
12. App guarda un reporte Markdown/HTML por corrida.

## API FastAPI Inicial

Endpoints propuestos:

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

## Docker Compose

Servicios minimos:

- `db`: Postgres container.
- `backend`: FastAPI container, depende de `db`.
- `frontend`: Vue dev server o build servido localmente/containerizado.

Requisitos:

- `db` usa volumen persistente, por ejemplo `postgres_data`.
- `db` expone puerto local solo para desarrollo, por ejemplo `5440:5432`.
- DBeaver puede conectarse a `localhost:5440` usando las credenciales de `.env`.
- `backend` se conecta usando hostname interno `db`.
- `backend` espera healthcheck de Postgres antes de iniciar tareas de ingesta.
- `.env` define `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL` y SEC `USER_AGENT`.

Ejemplo conceptual:

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: now_user
      POSTGRES_PASSWORD: now_password
      POSTGRES_DB: now_health
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5440:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U now_user -d now_health"]
      interval: 5s
      timeout: 5s
      retries: 10

  backend:
    build: ./backend
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+psycopg://now_user:now_password@db:5432/now_health

volumes:
  postgres_data:
```

## Frontend Vue Inicial

Vistas:

- Dashboard: diagnostico actual, senales y conclusion.
- Metrics: tabla editable de KPIs por trimestre.
- Sources: documentos SEC/IR usados y estado de parsing.
- Reports: reportes generados por corrida.

Componentes:

- `SignalCard`
- `MetricTable`
- `ValuationBandChart`
- `SourceBadge`
- `QuarterSelector`
- `RunRefreshButton`
- `ManualMetricDialog`

shadcn-vue debe usarse para primitives de UI: Button, Card, Table, Dialog, Tabs, Badge, Alert, Select, Input, Skeleton y Tooltip.
Tailwind se usa para layout, spacing y refinamientos visuales.

## Modelo de Datos Inicial

Tablas:

- `companies`
- `filings`
- `earnings_reports`
- `quarterly_metrics`
- `insider_transactions`
- `model_runs`
- `model_signal_results`
- `source_documents`

Campos criticos en `quarterly_metrics`:

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

## Reglas del Diagnostico

Las reglas deben vivir en codigo y tambien mostrarse en UI.

Ejemplo:

- cRPO constant currency < 19% => bear.
- cRPO 19% a 21% => base.
- cRPO > 21% => bull.
- cRPO > 21.5% por dos trimestres => bull fuerte.
- Renewal < 96% => bear.
- Renewal 97% a 98% => base.
- Creator/other share > 25% => bull.
- Dos o mas exit signals en un trimestre => revisar venta/reduccion.

## MVP

El MVP debe hacer solo esto:

1. Descargar filings SEC para NOW.
2. Descargar o registrar link de ultimo earnings release, priorizando SEC cuando el release este adjunto como 8-K exhibit.
3. Parsear datos GAAP desde SEC Company Facts.
4. Permitir entrada manual de KPIs dificiles de parsear en v1.
5. Guardar cada dato con fuente y fecha.
6. Ejecutar reglas bear/base/bull.
7. Exponer resultados via FastAPI.
8. Mostrar dashboard local en Vue.
9. Permitir inspeccion de Postgres desde DBeaver via `localhost:5440`.
10. Exportar reporte Markdown.

## Fase 2

- Parser mas robusto para PDFs de earnings releases.
- Deteccion automatica de cRPO, RPO, non-GAAP margin y guidance.
- Form 4 insider transaction parser.
- Alertas locales cuando aparezca un filing nuevo.
- Comparacion historica trimestre contra trimestre.
- Soporte para otros tickers.

## Riesgos

- Los press releases pueden cambiar de formato.
- Algunos KPIs del video no son financieros estandarizados.
- Fuentes gratuitas de precio pueden ser menos confiables.
- El parsing automatizado de texto financiero necesita validacion manual.
- SEC no soporta CORS; la app debe llamar SEC desde backend Python, no desde browser.

## Verificacion

Para considerar el MVP completo:

- Una corrida nueva descarga o reutiliza documentos fuente.
- Cada KPI muestra su fuente.
- El modelo produce una clasificacion por senal.
- El reporte generado puede revisarse sin correr la app.
- Si falta un dato, la app lo marca como missing y no inventa valores.
- Las reglas coinciden con `servicenow-stock-health-model.md`.
