import math
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.agents.explanation.rag.corpus_registry import AVAILABLE_CORPORA, CorpusEntry
from app.agents.explanation.rag.retrieval_contract import Reference, RetrievalRequest

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
MAX_REFERENCES = 3


def _resolve_path(entry: CorpusEntry) -> Path:
    path = Path(entry.path)
    if path.is_absolute():
        return path
    candidate = CORPUS_DIR / path
    if candidate.exists():
        return candidate

    target = unicodedata.normalize("NFC", candidate.name)
    for file_path in CORPUS_DIR.iterdir():
        if not file_path.is_file():
            continue
        if unicodedata.normalize("NFC", file_path.name) == target:
            return file_path
        if unicodedata.normalize("NFD", file_path.name) == unicodedata.normalize(
            "NFD", target
        ):
            return file_path
    return candidate


def _load_text(entry: CorpusEntry) -> str:
    path = _resolve_path(entry)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[가-힣A-Za-z0-9]+", text.lower())


def _split_sentences(text: str) -> List[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    joined = " ".join(lines)
    parts = re.split(r"(?<=[.!?])\s+|\n+", joined)
    return [part.strip() for part in parts if part.strip()]


def _tfidf_vectors(texts: List[str]) -> List[Dict[str, float]]:
    tokenized = [_tokenize(text) for text in texts]
    doc_counts = [Counter(tokens) for tokens in tokenized]
    df = Counter()
    for tokens in tokenized:
        for term in set(tokens):
            df[term] += 1

    total_docs = len(texts)
    idf = {
        term: math.log((1 + total_docs) / (1 + freq)) + 1.0 for term, freq in df.items()
    }

    vectors: List[Dict[str, float]] = []
    for counts in doc_counts:
        total = sum(counts.values())
        if total == 0:
            vectors.append({})
            continue
        vec = {term: (count / total) * idf.get(term, 0.0) for term, count in counts.items()}
        vectors.append(vec)
    return vectors


def _cosine_similarity(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(value * b.get(term, 0.0) for term, value in a.items())
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _tag_overlap(query_tokens: List[str], tags: List[str]) -> int:
    if not query_tokens or not tags:
        return 0
    normalized_tags = [tag.lower() for tag in tags]
    count = 0
    for token in query_tokens:
        token_lower = token.lower()
        for tag in normalized_tags:
            if token_lower in tag or tag in token_lower:
                count += 1
                break
    return count


def _best_sentence(
    query_text: str, sentences: List[str], tags: List[str]
) -> Tuple[Optional[str], float]:
    if not sentences:
        return None, 0.0
    vectors = _tfidf_vectors([query_text] + sentences)
    query_vector = vectors[0]
    best_sentence = None
    best_score = 0.0
    query_tokens = _tokenize(query_text)
    tag_overlap = _tag_overlap(query_tokens, tags)
    tag_boost = 0.05 * float(tag_overlap)
    for sentence, vector in zip(sentences, vectors[1:]):
        score = _cosine_similarity(query_vector, vector) + tag_boost
        if score > best_score:
            best_score = score
            best_sentence = sentence
    return best_sentence, best_score


def _source_title(entry: CorpusEntry) -> str:
    path = _resolve_path(entry)
    if path.suffix:
        return path.stem
    return path.name if path.name else entry.path


def retrieve_evidence(request: RetrievalRequest) -> List[Reference]:
    """선택적 검색 계층. 참고 자료를 반환."""
    if not AVAILABLE_CORPORA:
        return []

    query_text = " ".join(
        [
            request.risk_stage,
            request.conversation_type,
            *request.signals,
            *request.query_terms,
            *request.matched_phrases,
        ]
    ).strip()
    query_tokens = _tokenize(query_text)
    if not query_tokens:
        return []

    scored: List[Tuple[float, CorpusEntry, str]] = []
    for entry in AVAILABLE_CORPORA:
        text = _load_text(entry)
        if not text:
            continue
        sentences = _split_sentences(text)
        best_sentence, score = _best_sentence(query_text, sentences, entry.tags)
        if best_sentence and score > 0.0:
            scored.append((score, entry, best_sentence))

    if not scored:
        fallback: List[Tuple[int, CorpusEntry, str]] = []
        query_tokens = _tokenize(query_text)
        for entry in AVAILABLE_CORPORA:
            text = _load_text(entry)
            if not text:
                continue
            sentences = _split_sentences(text)
            if not sentences:
                continue
            overlap = _tag_overlap(query_tokens, entry.tags)
            if overlap > 0:
                fallback.append((overlap, entry, sentences[0]))
        if not fallback:
            return []
        fallback.sort(key=lambda item: item[0], reverse=True)
        selected = fallback[:MAX_REFERENCES]
        return [
            Reference(source=_source_title(entry), note=sentence)
            for _, entry, sentence in selected
        ]

    scored.sort(key=lambda item: item[0], reverse=True)
    selected = scored[:MAX_REFERENCES]
    return [
        Reference(source=_source_title(entry), note=sentence)
        for _, entry, sentence in selected
    ]
