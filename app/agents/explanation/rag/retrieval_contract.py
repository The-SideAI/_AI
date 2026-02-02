from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class RetrievalRequest:
    risk_stage: str
    conversation_type: str
    signals: List[str]
    query_terms: List[str] = field(default_factory=list)
    matched_phrases: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class Reference:
    source: str
    note: str
