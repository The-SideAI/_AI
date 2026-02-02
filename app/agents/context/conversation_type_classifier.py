from typing import Dict, List

from app.utils.text_patterns import CONVERSATION_TYPE_RULES
from app.utils.text_utils import normalize_text


ALLOWED_CONTEXT_TYPES = ["중고거래", "투자", "대출", "취업", "알 수 없음"]


def classify_conversation_type(conversation: List[str]) -> str:
    """대화 유형 분류. risk_stage에는 영향을 주지 않음."""
    scores: Dict[str, int] = {key: 0 for key in CONVERSATION_TYPE_RULES.keys()}
    for message in conversation:
        normalized = normalize_text(message)
        for conversation_type, patterns in CONVERSATION_TYPE_RULES.items():
            if any(pattern.search(normalized) for pattern in patterns):
                scores[conversation_type] += 1

    if not scores:
        return "알 수 없음"

    best_type = max(scores, key=scores.get)
    if scores[best_type] <= 0:
        return "알 수 없음"

    if best_type not in ALLOWED_CONTEXT_TYPES:
        return "알 수 없음"
    return best_type
