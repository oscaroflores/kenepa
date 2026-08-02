from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SignalResult:
    signal_key: str
    signal_name: str
    status: str
    summary: str
    triggered: bool = False
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Diagnosis:
    overall_signal: str
    conclusion: str
    missing_metrics: list[str]
    signals: list[SignalResult]
    exit_signals: list[str]
    scale_in_signals: list[str]


def _value(metrics: dict[str, Any], field: str) -> Any:
    value = metrics.get(field)
    return None if value == "" else value


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "si", "sí"}
    return bool(value)


def _ai_target_billions(value: float | None) -> float | None:
    if value is None:
        return None
    return value if value < 100 else value / 1_000_000_000


def _two_quarters_above(field: str, threshold: float, metrics: dict[str, Any], previous: dict[str, Any] | None) -> bool:
    return previous is not None and _value(metrics, field) is not None and _value(previous, field) is not None and _value(metrics, field) > threshold and _value(previous, field) > threshold


def _two_quarters_below(field: str, threshold: float, metrics: dict[str, Any], previous: dict[str, Any] | None) -> bool:
    return previous is not None and _value(metrics, field) is not None and _value(previous, field) is not None and _value(metrics, field) < threshold and _value(previous, field) < threshold


def evaluate_metrics(metrics: dict[str, Any], history: list[dict[str, Any]] | None = None) -> Diagnosis:
    history = history or []
    previous = history[0] if history else None
    signals: list[SignalResult] = []
    missing: list[str] = []
    exit_signals: list[str] = []
    scale_in_signals: list[str] = []

    crpo = _value(metrics, "current_rpo_growth_constant_currency")
    if crpo is None:
        missing.append("current_rpo_growth_constant_currency")
        signals.append(SignalResult("demand", "Demand / cRPO constant currency", "missing", "cRPO constant-currency growth is missing."))
    elif crpo < 19:
        signals.append(SignalResult("demand", "Demand / cRPO constant currency", "bear", f"cRPO constant-currency growth is {crpo:.1f}%, below the 19% bear threshold.", True, {"value": crpo}))
    elif crpo <= 21:
        signals.append(SignalResult("demand", "Demand / cRPO constant currency", "base", f"cRPO constant-currency growth is {crpo:.1f}%, inside the 19%-21% base range.", False, {"value": crpo}))
    elif _two_quarters_above("current_rpo_growth_constant_currency", 21.5, metrics, previous):
        signals.append(SignalResult("demand", "Demand / cRPO constant currency", "strong_bull", "cRPO constant-currency growth is above 21.5% for two quarters.", True, {"value": crpo}))
        scale_in_signals.append("cRPO > 21.5% for two quarters")
    else:
        signals.append(SignalResult("demand", "Demand / cRPO constant currency", "bull", f"cRPO constant-currency growth is {crpo:.1f}%, above the 21% bull threshold.", True, {"value": crpo}))

    if _two_quarters_below("current_rpo_growth_constant_currency", 19, metrics, previous):
        exit_signals.append("cRPO < 19% for two quarters")

    renewal = _value(metrics, "renewal_rate")
    wins = _as_bool(_value(metrics, "named_competitive_wins"))
    if renewal is None:
        missing.append("renewal_rate")
        signals.append(SignalResult("moat", "Moat / renewal", "missing", "Renewal rate is missing."))
    elif renewal < 96:
        signals.append(SignalResult("moat", "Moat / renewal", "bear", f"Renewal rate is {renewal:.1f}%, below the 96% exit threshold.", True, {"value": renewal}))
        exit_signals.append("Renewal rate < 96%")
    elif renewal >= 97 and wins:
        signals.append(SignalResult("moat", "Moat / renewal", "bull", "Renewal is healthy and named competitive wins were reported.", True, {"value": renewal}))
        scale_in_signals.append("Named enterprise wins against competitors")
    else:
        signals.append(SignalResult("moat", "Moat / renewal", "base", f"Renewal rate is {renewal:.1f}%, consistent with the base case.", False, {"value": renewal}))

    creator_share = _value(metrics, "creator_other_share")
    previous_creator_share = _value(previous, "creator_other_share") if previous else None
    if creator_share is None:
        missing.append("creator_other_share")
        signals.append(SignalResult("ai_monetization", "AI monetization / Creator share", "missing", "Creator/other share is missing."))
    elif creator_share > 25:
        signals.append(SignalResult("ai_monetization", "AI monetization / Creator share", "bull", f"Creator/other share is {creator_share:.1f}%, above the 25% bull threshold.", True, {"value": creator_share}))
        scale_in_signals.append("Creator/other share > 25%")
    elif previous_creator_share is not None and creator_share <= previous_creator_share:
        signals.append(SignalResult("ai_monetization", "AI monetization / Creator share", "bear", "Creator/other share is flat or falling versus the prior quarter.", True, {"value": creator_share, "previous": previous_creator_share}))
    elif previous_creator_share is not None and creator_share > previous_creator_share:
        signals.append(SignalResult("ai_monetization", "AI monetization / Creator share", "base", "Creator/other share is growing, supporting the base case.", False, {"value": creator_share, "previous": previous_creator_share}))
    else:
        signals.append(SignalResult("ai_monetization", "AI monetization / Creator share", "base", "Creator/other share is present but needs a prior quarter for trend classification.", False, {"value": creator_share}))

    ai_target = _ai_target_billions(_value(metrics, "ai_acv_target"))
    if ai_target is not None and ai_target > 2:
        scale_in_signals.append("AI ACV target > $2B")

    op_margin = _value(metrics, "non_gaap_operating_margin")
    if op_margin is None:
        missing.append("non_gaap_operating_margin")
        signals.append(SignalResult("profitability", "Profitability / operating margin", "missing", "Non-GAAP operating margin is missing."))
    elif op_margin > 33:
        signals.append(SignalResult("profitability", "Profitability / operating margin", "bull", f"Non-GAAP operating margin is {op_margin:.1f}%, above the post-Armis 33% bull threshold.", True, {"value": op_margin}))
        scale_in_signals.append("Operating margin > 33% post-Armis")
    elif op_margin >= 30:
        signals.append(SignalResult("profitability", "Profitability / operating margin", "base", f"Non-GAAP operating margin is {op_margin:.1f}%, near the expected normalization range.", False, {"value": op_margin}))
    else:
        signals.append(SignalResult("profitability", "Profitability / operating margin", "bear", f"Non-GAAP operating margin is {op_margin:.1f}%, below the expected normalization range.", True, {"value": op_margin}))

    if _as_bool(_value(metrics, "named_displacements")):
        exit_signals.append("Named Fortune 500 displacement")
    if _as_bool(_value(metrics, "discretionary_insider_selling_depressed")):
        exit_signals.append("Discretionary insider selling at depressed prices")
    fy27_growth = _value(metrics, "fy27_growth_guidance")
    if fy27_growth is not None and fy27_growth < 16:
        exit_signals.append("FY27 guide < 16%")

    triggered_bears = sum(1 for signal in signals if signal.status == "bear")
    triggered_bulls = sum(1 for signal in signals if signal.status in {"bull", "strong_bull"})

    if len(exit_signals) >= 2:
        overall = "bear"
        conclusion = "Two or more exit signals are active. Review sale or reduction before adding exposure."
    elif triggered_bears >= 2:
        overall = "bear"
        conclusion = "Multiple core signals are bearish. The model says the thesis needs re-validation."
    elif len(scale_in_signals) >= 2 or triggered_bulls >= 3:
        overall = "bull"
        conclusion = "Several scale-in or bull signals are active. The model supports constructive review."
    elif len(missing) >= 3:
        overall = "missing"
        conclusion = "Important KPIs are missing. Enter manual values with sources before relying on the diagnosis."
    else:
        overall = "base"
        conclusion = "No decisive exit cluster is active. The base case remains the working diagnosis."

    return Diagnosis(overall, conclusion, missing, signals, exit_signals, scale_in_signals)
