from typing import Dict

from app.agents.actions.safe_action_generator import generate_safe_actions
from app.agents.aggregator.risk_signal_aggregator import aggregate_signals
from app.agents.analyzer.conversation_analyzer import (
    analyze_conversation,
    extract_signal_phrases,
    extract_signal_phrases_by_signal,
    signal_query_terms,
)
from app.agents.context.conversation_type_classifier import classify_conversation_type
from app.agents.decision.decision_orchestrator import decide_risk_stage
from app.agents.explanation.rag.rag_provider import retrieve_evidence
from app.agents.explanation.rag.retrieval_contract import RetrievalRequest
from app.core.logging import get_logger
from app.schemas.request import AnalyzeRequest

logger = get_logger(__name__)


def run_analysis_pipeline(payload: AnalyzeRequest) -> Dict[str, object]:
    conversation = payload.conversation
    messages = [turn.text for turn in conversation]
    other_messages = [turn.text for turn in conversation if turn.speaker == "other"]
    logger.info("Pipeline start: %d turns (other=%d)", len(conversation), len(other_messages))

    # 1. 규칙 기반 신호 추출
    rule_signals = analyze_conversation(other_messages)
    signal_phrase_map = extract_signal_phrases_by_signal(other_messages)
    step1_signal_map = {signal: signal_phrase_map.get(signal, []) for signal in rule_signals}
    logger.info("Step 1 signals: %s", step1_signal_map)

    # 2. 위험 신호 집계
    aggregated_signals = aggregate_signals(rule_signals)
    step2_signal_map = {
        signal: signal_phrase_map.get(signal, []) for signal in aggregated_signals
    }
    logger.info("Step 2 aggregated_signals: %s", step2_signal_map)

    # 2.1 RAG 쿼리 보강
    signal_terms = signal_query_terms(aggregated_signals)
    matched_phrases = extract_signal_phrases(other_messages)
    logger.info("Step 2.1 query_terms=%s matched_phrases=%s", signal_terms, matched_phrases)

    # 3. 결정 오케스트레이터
    risk_stage = decide_risk_stage(aggregated_signals)
    logger.info("Step 3 risk_stage: %s", risk_stage)

    # 4. 대화 유형 분류
    conversation_type = classify_conversation_type(messages)
    logger.info("Step 4 conversation_type: %s", conversation_type)

    # 5. RAG 검색
    retrieval_request = RetrievalRequest(
        risk_stage=risk_stage,
        conversation_type=conversation_type,
        signals=aggregated_signals,
        query_terms=signal_terms,
        matched_phrases=matched_phrases,
    )
    references = retrieve_evidence(retrieval_request)
    logger.info("Step 5 references: %d", len(references))

    # 6. 안전 행동 생성 (LLM: references + 대화 발췌 사용)
    conversation_lines = [f"{turn.speaker}: {turn.text}" for turn in conversation]
    safe_actions = generate_safe_actions(
        risk_stage, conversation_type, references, conversation_lines
    )
    logger.info("Step 6 safe_actions generated")

    return {
        "risk_stage": risk_stage,
        "type": conversation_type,
        "reason": [reference.__dict__ for reference in references],
        "summary": safe_actions["summary"],
        "recommended_questions": safe_actions["recommended_questions"],
    }
