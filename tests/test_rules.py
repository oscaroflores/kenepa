from src.model.rules import evaluate_metrics


def test_exit_cluster_when_two_exit_signals_present() -> None:
    current = {
        "current_rpo_growth_constant_currency": 18.5,
        "renewal_rate": 95.5,
        "creator_other_share": 22,
        "non_gaap_operating_margin": 31,
    }
    previous = {"current_rpo_growth_constant_currency": 18.7, "creator_other_share": 21}

    diagnosis = evaluate_metrics(current, [previous])

    assert diagnosis.overall_signal == "bear"
    assert "cRPO < 19% for two quarters" in diagnosis.exit_signals
    assert "Renewal rate < 96%" in diagnosis.exit_signals


def test_scale_in_cluster_when_multiple_bull_signals_present() -> None:
    current = {
        "current_rpo_growth_constant_currency": 22.0,
        "renewal_rate": 98.0,
        "creator_other_share": 26.0,
        "non_gaap_operating_margin": 34.0,
        "ai_acv_target": 2.2,
    }
    previous = {"current_rpo_growth_constant_currency": 21.8, "creator_other_share": 24.0}

    diagnosis = evaluate_metrics(current, [previous])

    assert diagnosis.overall_signal == "bull"
    assert "cRPO > 21.5% for two quarters" in diagnosis.scale_in_signals
    assert "Creator/other share > 25%" in diagnosis.scale_in_signals
    assert "Operating margin > 33% post-Armis" in diagnosis.scale_in_signals


def test_missing_metrics_are_not_invented() -> None:
    diagnosis = evaluate_metrics({}, [])

    assert diagnosis.overall_signal == "missing"
    assert "current_rpo_growth_constant_currency" in diagnosis.missing_metrics
    assert "renewal_rate" in diagnosis.missing_metrics
