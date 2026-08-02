from src.model.rules import Diagnosis


def diagnosis_score(diagnosis: Diagnosis) -> int:
    weights = {"bear": -2, "missing": 0, "base": 1, "bull": 2, "strong_bull": 3}
    return sum(weights.get(signal.status, 0) for signal in diagnosis.signals)
