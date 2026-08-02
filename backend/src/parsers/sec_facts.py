from __future__ import annotations

from typing import Any


CONCEPTS = {
    "cash_and_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    ],
    "gaap_net_income": ["NetIncomeLoss", "ProfitLoss"],
    "stock_based_compensation": ["ShareBasedCompensation"],
    "diluted_share_count": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
}

UNIT_HINTS = {
    "cash_and_equivalents": ["USD"],
    "gaap_net_income": ["USD"],
    "stock_based_compensation": ["USD"],
    "diluted_share_count": ["shares"],
}


def _latest_fact(companyfacts: dict[str, Any], concepts: list[str], units: list[str]) -> dict[str, Any] | None:
    facts = companyfacts.get("facts", {}).get("us-gaap", {})
    candidates: list[dict[str, Any]] = []
    for concept in concepts:
        concept_data = facts.get(concept, {})
        unit_values = concept_data.get("units", {})
        for unit in units:
            for item in unit_values.get(unit, []):
                if item.get("form") in {"10-Q", "10-K"} and item.get("val") is not None:
                    candidates.append({**item, "concept": concept, "unit": unit})
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item.get("end") or "", item.get("filed") or ""))


def parse_companyfacts_to_metrics(companyfacts: dict[str, Any]) -> dict[str, Any] | None:
    values: dict[str, float] = {}
    fact_details: dict[str, dict[str, Any]] = {}
    fiscal_year: int | None = None
    fiscal_period: str | None = None

    for field, concepts in CONCEPTS.items():
        fact = _latest_fact(companyfacts, concepts, UNIT_HINTS[field])
        if not fact:
            continue
        values[field] = float(fact["val"])
        fact_details[field] = {
            "concept": fact.get("concept"),
            "unit": fact.get("unit"),
            "form": fact.get("form"),
            "filed": fact.get("filed"),
            "end": fact.get("end"),
            "accession_number": fact.get("accn"),
        }
        fiscal_year = fiscal_year or fact.get("fy")
        fiscal_period = fiscal_period or fact.get("fp")

    if not values:
        return None

    fp = str(fiscal_period or "latest").replace("Q", "Q")
    quarter = f"FY{fiscal_year}-{fp}" if fiscal_year else "latest"
    return {
        "quarter": quarter,
        "fiscal_year": int(fiscal_year) if fiscal_year else None,
        "values": values,
        "fact_details": fact_details,
    }
