def valuation_bands(forward_free_cash_flow: float | None) -> dict[str, dict[str, float | None]]:
    if forward_free_cash_flow is None:
        return {
            "bear": {"multiple": 14, "enterprise_value": None},
            "base": {"multiple": 20, "enterprise_value": None},
            "bull": {"multiple": 35, "enterprise_value": None},
        }
    return {
        "bear": {"multiple": 14, "enterprise_value": forward_free_cash_flow * 14},
        "base": {"multiple": 20, "enterprise_value": forward_free_cash_flow * 20},
        "bull": {"multiple": 35, "enterprise_value": forward_free_cash_flow * 35},
    }
