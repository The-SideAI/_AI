from typing import List


def aggregate_signals(rule_signals: List[str]) -> List[str]:
    """규칙 기반 신호를 정규화하여 정렬된 리스트로 반환."""
    return sorted(set(rule_signals))
