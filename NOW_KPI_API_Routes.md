# ServiceNow (NOW) — KPI API Routes

**CIK:** `0001373715` · **Ticker:** NOW
**SEC User-Agent header (requerido):** `oscaromarflores@gmail.com`

> SEC EDGAR bloquea requests sin `User-Agent`. Manda siempre:
> `User-Agent: oscaromarflores@gmail.com`

---

## 1. SEC EDGAR XBRL — route por concepto (gratis, sin key)

Base:
```
https://data.sec.gov/api/xbrl/companyconcept/CIK0001373715/us-gaap/{TAG}.json
```

| KPI | Tag / Route completo |
|---|---|
| `cash_and_equivalents` | `https://data.sec.gov/api/xbrl/companyconcept/CIK0001373715/us-gaap/CashAndCashEquivalentsAtCarryingValue.json` |
| `gaap_net_income` | `https://data.sec.gov/api/xbrl/companyconcept/CIK0001373715/us-gaap/NetIncomeLoss.json` |
| `stock_based_compensation` | `https://data.sec.gov/api/xbrl/companyconcept/CIK0001373715/us-gaap/ShareBasedCompensation.json` |
| `diluted_share_count` | `https://data.sec.gov/api/xbrl/companyconcept/CIK0001373715/us-gaap/WeightedAverageNumberOfDilutedSharesOutstanding.json` |
| `free_cash_flow` (componente 1) | `https://data.sec.gov/api/xbrl/companyconcept/CIK0001373715/us-gaap/NetCashProvidedByUsedInOperatingActivities.json` |
| `free_cash_flow` (componente 2) | `https://data.sec.gov/api/xbrl/companyconcept/CIK0001373715/us-gaap/PaymentsToAcquirePropertyPlantAndEquipment.json` |
| `current_rpo_growth` (parcial)* | `https://data.sec.gov/api/xbrl/companyconcept/CIK0001373715/us-gaap/RevenueRemainingPerformanceObligation.json` |

\* El RPO **total** sale aquí; el **current** RPO viene con dimensión `TimeAxis` que `companyconcept` no separa limpio. Más fiable del press release (sección 4).

**Todos los facts de la empresa en un solo JSON:**
```
https://data.sec.gov/api/xbrl/companyfacts/CIK0001373715.json
```

**Index de todos los filings (para localizar 8-K / 10-Q):**
```
https://data.sec.gov/submissions/CIK0001373715.json
```

---

## 2. Yahoo Finance — datos de mercado (gratis, sin key)

| KPI | Route |
|---|---|
| `share_price_used` | `https://query1.finance.yahoo.com/v8/finance/chart/NOW` |
| `market_cap` / `enterprise_value` / shares / cash | `https://query1.finance.yahoo.com/v10/finance/quoteSummary/NOW?modules=defaultKeyStatistics,financialData,summaryDetail` |

> `quoteSummary` ahora requiere **crumb + cookie**. Flujo:
> 1. `GET https://fc.yahoo.com` (recoge cookie)
> 2. `GET https://query1.finance.yahoo.com/v1/test/getcrumb` (con la cookie)
> 3. Añade `&crumb={CRUMB}` al route de `quoteSummary`.
> El endpoint `v8/finance/chart` NO requiere crumb.

---

## 3. SEC Form 4 — insider transactions (gratis, sin key)

| KPI | Route |
|---|---|
| `insider_buys` | `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=1373715&type=4&output=atom` |

Full-text search de filings (alternativa):
```
https://efts.sec.gov/LATEST/search-index?q=&forms=4&ciks=0001373715
```

---

## 4. Press release / prepared remarks — **NO hay API (scraping)**

Localización: `https://data.sec.gov/submissions/CIK0001373715.json` → filtrar `form = "8-K"` → bajar el adjunto `EX-99.1` (press release) y, cuando aplique, los prepared remarks del investor deck en `investors.servicenow.com`.

Estos KPIs **solo existen como texto/tabla** en esos documentos:

`subscription_revenue_growth`, `organic_constant_currency_revenue_growth`, `current_rpo_growth_constant_currency`, `non_gaap_operating_margin`, `free_cash_flow_margin`, `forward_free_cash_flow_estimate`, `buyback_authorization_remaining`, `ai_acv_run_rate`, `ai_acv_target`, `creator_other_share`, `renewal_rate`, `customers_over_5m_acv`, `average_acv_large_customers`, `named_competitive_wins`, `named_displacements`, `fy_growth_guidance`, `fy_operating_margin_guidance`, `fy27_growth_guidance`

---

## 5. Derivados (CALC) — no tienen route propio

| KPI | Cálculo |
|---|---|
| `free_cash_flow` | `NetCashProvidedByUsedInOperatingActivities` − `PaymentsToAcquirePropertyPlantAndEquipment` |
| `free_cash_flow_multiple` | `enterprise_value` / `free_cash_flow` |
| `share_count_growth` | serie de `WeightedAverageNumberOfDilutedSharesOutstanding` |
| `discretionary_insider_selling_depressed` | Form 4 (§3) + precio Yahoo (§2) |

---

### Resumen de cobertura

- **API real:** ~11 KPIs (EDGAR XBRL §1 + Yahoo §2 + Form 4 §3)
- **Derivados:** 4 KPIs (§5)
- **Solo scraping:** ~18 KPIs (§4) — incluye 6 de los 9 core del rule engine
