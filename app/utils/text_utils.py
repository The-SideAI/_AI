from typing import Iterable, List


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def join_conversation(conversation: Iterable[str]) -> str:
    return "\n".join(conversation)


def tokenize(text: str) -> List[str]:
    return [token for token in text.split() if token]
