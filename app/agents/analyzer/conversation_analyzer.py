from typing import Dict, List

from app.utils.text_patterns import RISK_SIGNAL_RULES, SIGNAL_QUERY_TERMS
from app.utils.text_utils import normalize_text


def analyze_conversation(conversation: List[str]) -> List[str]:
    """규칙 기반 신호 추출. 순수 함수이며 결정론적으로 동작."""
    signals = set()
    for message in conversation:
        normalized = normalize_text(message)
        for signal, patterns in RISK_SIGNAL_RULES.items():
            if any(pattern.search(normalized) for pattern in patterns):
                signals.add(signal)
    return sorted(signals)


def extract_signal_phrases(conversation: List[str]) -> List[str]:
    """RAG 쿼리 개선을 위해 신호에 매칭된 구절을 추출."""
    phrases = set()
    for message in conversation:
        normalized = normalize_text(message)
        for patterns in RISK_SIGNAL_RULES.values():
            for pattern in patterns:
                for match in pattern.finditer(normalized):
                    phrase = match.group(0).strip()
                    if phrase:
                        phrases.add(phrase)
    return sorted(phrases)


def extract_signal_phrases_by_signal(conversation: List[str]) -> Dict[str, List[str]]:
    """신호별로 매칭된 구절 목록을 반환."""
    matches: Dict[str, set] = {}
    for message in conversation:
        normalized = normalize_text(message)
        for signal, patterns in RISK_SIGNAL_RULES.items():
            for pattern in patterns:
                for match in pattern.finditer(normalized):
                    phrase = match.group(0).strip()
                    if not phrase:
                        continue
                    matches.setdefault(signal, set()).add(phrase)
    return {signal: sorted(list(phrases)) for signal, phrases in matches.items()}


def signal_query_terms(signals: List[str]) -> List[str]:
    terms: List[str] = []
    for signal in signals:
        terms.extend(SIGNAL_QUERY_TERMS.get(signal, []))
    return sorted(set(terms))
