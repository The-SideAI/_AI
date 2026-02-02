from typing import List, Literal


RiskStage = Literal["normal", "suspicious", "critical"]


def decide_risk_stage(signals: List[str]) -> RiskStage:
    """결정론적 판단 로직. LLM 사용 없음."""
    signal_set = set(signals)
    if "money_request" in signal_set and "urgency" in signal_set:
        return "critical"
    if signal_set:
        return "suspicious"
    return "normal"
