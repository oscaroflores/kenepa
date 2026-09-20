from __future__ import annotations

from datetime import date
from typing import Any


POINT_CONCEPTS = {
    "cash_and_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    ],
}

DURATION_CONCEPTS = {
    "gaap_net_income": ["NetIncomeLoss", "ProfitLoss"],
    "stock_based_compensation": ["ShareBasedCompensation"],
    "diluted_share_count": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
}

REVENUE_CONCEPTS = ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"]
RPO_CONCEPTS = ["RevenueRemainingPerformanceObligation"]
OPERATING_INCOME_CONCEPTS = ["OperatingIncomeLoss"]
OPERATING_CASH_FLOW_CONCEPTS = ["NetCashProvidedByUsedInOperatingActivities"]
CAPEX_CONCEPTS = ["PaymentsToAcquirePropertyPlantAndEquipment"]

UNIT_HINTS = {
    "cash_and_equivalents": ["USD"],
    "gaap_net_income": ["USD"],
    "stock_based_compensation": ["USD"],
    "diluted_share_count": ["shares"],
}


def _concept_items(companyfacts: dict[str, Any], concepts: list[str], units: list[str]) -> list[dict[str, Any]]:
    facts = companyfacts.get("facts", {}).get("us-gaap", {})
    items: list[dict[str, Any]] = []
    for concept in concepts:
        unit_values = facts.get(concept, {}).get("units", {})
        for unit in units:
            for item in unit_values.get(unit, []):
                if item.get("form") in {"10-Q", "10-K"} and item.get("val") is not None:
                    items.append({**item, "concept": concept, "unit": unit})
    return items


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _is_quarter_duration(item: dict[str, Any]) -> bool:
    start = _parse_date(item.get("start"))
    end = _parse_date(item.get("end"))
    if not start or not end:
        return False
    return 75 <= (end - start).days <= 100


def _period_key(item: dict[str, Any]) -> tuple[str, str]:
    return str(item.get("fy") or ""), str(item.get("fp") or "")


def _detail(item: dict[str, Any], *, note: str | None = None) -> dict[str, Any]:
    detail = {
        "concept": item.get("concept"),
        "unit": item.get("unit"),
        "form": item.get("form"),
        "filed": item.get("filed"),
        "start": item.get("start"),
        "end": item.get("end"),
        "accession_number": item.get("accn"),
    }
    if note:
        detail["note"] = note
    return detail


def _latest_quarterly_item(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [item for item in items if _is_quarter_duration(item)]
    if not candidates:
        candidates = [item for item in items if item.get("end")]
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item.get("end") or "", item.get("filed") or ""))


def _duration_for_period(items: list[dict[str, Any]], fy: str, fp: str) -> dict[str, Any] | None:
    exact = [item for item in items if _period_key(item) == (fy, fp) and _is_quarter_duration(item)]
    if exact:
        return max(exact, key=lambda item: (item.get("filed") or "", item.get("frame") or ""))

    if fp == "Q1":
        ytd = [item for item in items if _period_key(item) == (fy, fp) and item.get("start") and item.get("end")]
        return max(ytd, key=lambda item: (item.get("end") or "", item.get("filed") or "")) if ytd else None

    return None


def _ytd_for_period(items: list[dict[str, Any]], fy: str, fp: str) -> dict[str, Any] | None:
    ytd = [item for item in items if _period_key(item) == (fy, fp) and item.get("start") and item.get("end")]
    if not ytd:
        return None
    return max(ytd, key=lambda item: (_parse_date(item.get("end")) or date.min, _parse_date(item.get("start")) or date.max, item.get("filed") or ""))


def _previous_fp(fp: str) -> str | None:
    return {"Q2": "Q1", "Q3": "Q2", "FY": "Q3"}.get(fp)


def _duration_value(items: list[dict[str, Any]], fy: str, fp: str) -> tuple[float, dict[str, Any]] | None:
    quarter = _duration_for_period(items, fy, fp)
    if quarter:
        return float(quarter["val"]), _detail(quarter)

    current_ytd = _ytd_for_period(items, fy, fp)
    previous_fp = _previous_fp(fp)
    previous_ytd = _ytd_for_period(items, fy, previous_fp) if previous_fp else None
    if current_ytd and previous_ytd:
        value = float(current_ytd["val"]) - float(previous_ytd["val"])
        detail = _detail(current_ytd, note=f"Derived as {fp} YTD less {previous_fp} YTD.")
        detail["previous_ytd_accession_number"] = previous_ytd.get("accn")
        return value, detail
    return None


def _instant_for_period(items: list[dict[str, Any]], fy: str, fp: str) -> dict[str, Any] | None:
    exact = [item for item in items if _period_key(item) == (fy, fp) and item.get("start") is None]
    if exact:
        return max(exact, key=lambda item: (item.get("end") or "", item.get("filed") or ""))
    all_instants = [item for item in items if item.get("start") is None and item.get("end")]
    return max(all_instants, key=lambda item: (item.get("end") or "", item.get("filed") or "")) if all_instants else None


def _same_period_prior_year(items: list[dict[str, Any]], item: dict[str, Any]) -> dict[str, Any] | None:
    end = _parse_date(item.get("end"))
    if not end:
        return None
    prior_end = end.replace(year=end.year - 1).isoformat()
    same_period = [candidate for candidate in items if candidate.get("end") == prior_end]
    if _is_quarter_duration(item):
        same_period = [candidate for candidate in same_period if _is_quarter_duration(candidate)]
    elif item.get("start") is None:
        same_period = [candidate for candidate in same_period if candidate.get("start") is None]
    if not same_period:
        return None
    return max(same_period, key=lambda candidate: (candidate.get("filed") or "", candidate.get("frame") or ""))


def _growth_percent(current: float, prior: float) -> float | None:
    if prior == 0:
        return None
    return (current / prior - 1) * 100


def parse_companyfacts_to_metrics(companyfacts: dict[str, Any]) -> dict[str, Any] | None:
    values: dict[str, float] = {}
    fact_details: dict[str, dict[str, Any]] = {}

    revenue_items = _concept_items(companyfacts, REVENUE_CONCEPTS, ["USD"])
    latest_revenue = _latest_quarterly_item(revenue_items)
    if not latest_revenue:
        return None

    fiscal_year = str(latest_revenue.get("fy") or "")
    fiscal_period = str(latest_revenue.get("fp") or "")
    if not fiscal_year or not fiscal_period:
        return None

    revenue_value = float(latest_revenue["val"])
    fact_details["revenue"] = _detail(latest_revenue)
    prior_revenue = _same_period_prior_year(revenue_items, latest_revenue)
    if prior_revenue:
        growth = _growth_percent(revenue_value, float(prior_revenue["val"]))
        if growth is not None:
            values["subscription_revenue_growth"] = growth
            fact_details["subscription_revenue_growth"] = _detail(latest_revenue, note="SEC total revenue YoY growth used when subscription revenue is not separately tagged.")

    for field, concepts in DURATION_CONCEPTS.items():
        result = _duration_value(_concept_items(companyfacts, concepts, UNIT_HINTS[field]), fiscal_year, fiscal_period)
        if result:
            values[field], fact_details[field] = result

    for field, concepts in POINT_CONCEPTS.items():
        fact = _instant_for_period(_concept_items(companyfacts, concepts, UNIT_HINTS[field]), fiscal_year, fiscal_period)
        if fact:
            values[field] = float(fact["val"])
            fact_details[field] = _detail(fact)

    rpo_items = _concept_items(companyfacts, RPO_CONCEPTS, ["USD"])
    rpo = _instant_for_period(rpo_items, fiscal_year, fiscal_period)
    prior_rpo = _same_period_prior_year(rpo_items, rpo) if rpo else None
    if rpo and prior_rpo:
        growth = _growth_percent(float(rpo["val"]), float(prior_rpo["val"]))
        if growth is not None:
            values["current_rpo_growth"] = growth
            values["current_rpo_growth_constant_currency"] = growth
            detail = _detail(rpo, note="SEC total RPO YoY growth used as cRPO constant-currency proxy when exact cRPO CC is not tagged.")
            fact_details["current_rpo_growth"] = detail
            fact_details["current_rpo_growth_constant_currency"] = detail

    operating_income = _duration_value(_concept_items(companyfacts, OPERATING_INCOME_CONCEPTS, ["USD"]), fiscal_year, fiscal_period)
    if operating_income and revenue_value:
        values["non_gaap_operating_margin"] = operating_income[0] / revenue_value * 100
        fact_details["non_gaap_operating_margin"] = {**operating_income[1], "note": "GAAP operating margin proxy used when non-GAAP operating margin is not SEC-tagged."}

    operating_cash_flow = _duration_value(_concept_items(companyfacts, OPERATING_CASH_FLOW_CONCEPTS, ["USD"]), fiscal_year, fiscal_period)
    capex = _duration_value(_concept_items(companyfacts, CAPEX_CONCEPTS, ["USD"]), fiscal_year, fiscal_period)
    if operating_cash_flow and capex:
        free_cash_flow = operating_cash_flow[0] - capex[0]
        values["free_cash_flow"] = free_cash_flow
        values["free_cash_flow_margin"] = free_cash_flow / revenue_value * 100 if revenue_value else 0
        fact_details["free_cash_flow"] = {**operating_cash_flow[1], "capex_detail": capex[1], "note": "Derived as operating cash flow less capital expenditures."}
        fact_details["free_cash_flow_margin"] = {**fact_details["free_cash_flow"], "revenue_detail": _detail(latest_revenue)}

    if not values:
        return None

    quarter = f"FY{fiscal_year}-{fiscal_period}"
    return {
        "quarter": quarter,
        "fiscal_year": int(fiscal_year),
        "values": values,
        "fact_details": fact_details,
    }
