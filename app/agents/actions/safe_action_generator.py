import json
import os
from typing import Dict, List, Optional

from openai import OpenAI
from dotenv import load_dotenv

from app.core.logging import get_logger
from app.agents.explanation.rag.retrieval_contract import Reference


load_dotenv()

OPENAI_MODEL_ENV = "OPENAI_MODEL_ENV"
DEFAULT_OPENAI_MODEL = "gpt-5-mini"

logger = get_logger(__name__)


def _fallback_safe_actions(
    risk_stage: str, references: List[Reference]
) -> Dict[str, List[str] | str]:
    if references:
        note = references[0].note.strip()
        summary = f"참고 자료에 따르면 {note}"
    elif risk_stage == "critical":
        summary = "진행 전 확인이 필요하다는 신호가 관찰되었습니다."
    elif risk_stage == "suspicious":
        summary = "추가 확인이 필요해 보이는 상황입니다."
    else:
        summary = "현재로서는 명확한 위험 징후가 보이지 않습니다."

    if risk_stage == "critical":
        recommended_questions = [
            "공식 확인 자료나 계약서를 보여주실 수 있나요?",
            "거래 전에 신원 확인 가능한 방법이 있나요?",
        ]
    elif risk_stage == "suspicious":
        recommended_questions = [
            "요청하신 절차를 조금 더 자세히 설명해 주실 수 있나요?",
            "확인 가능한 공식 안내나 정책이 있나요?",
        ]
    else:
        recommended_questions = [
            "거래 조건을 다시 한번 확인해 주실 수 있나요?",
            "진행 전에 확인해야 할 사항이 있나요?",
        ]

    return {
        "summary": summary,
        "recommended_questions": recommended_questions,
    }


def _call_openai_safe_actions(
    risk_stage: str,
    conversation_type: str,
    references: List[Reference],
    conversation_lines: List[str],
) -> Optional[Dict[str, List[str] | str]]:
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set; using fallback safe actions.")
        return None

    model = os.getenv(OPENAI_MODEL_ENV, DEFAULT_OPENAI_MODEL)

    reference_text = (
        "; ".join(f"{ref.source}: {ref.note}" for ref in references)
        if references
        else "없음"
    )

    def _conversation_excerpt(lines: List[str], max_lines: int = 12) -> str:
        if len(lines) <= max_lines:
            return "\n".join(lines)
        head = lines[: max_lines // 2]
        tail = lines[-(max_lines - len(head)) :]
        return "\n".join(head + ["..."] + tail)

    conversation_excerpt = _conversation_excerpt(conversation_lines)

    instructions = (
        "너는 위험 단계에 맞는 안전 행동 요약과 질문 예시를 만드는 어시스턴트다. "
        "반드시 JSON으로만 출력해라. "
        "summary는 1문장 요약이며, 반드시 참고 자료를 근거로 작성한다. "
        "recommended_questions는 2개의 짧은 질문이며, 사용자가 상대방(의심되는 대상)에게 던질 확인 질문이어야 한다. "
        "대화 발췌 내용을 참고해 질문을 구체화해라. "
        "참고 자료에 없는 사실은 만들지 마라. "
        "중립적이고 설명적인 톤을 유지하고, 판단을 확정하지 마라."
    )
    prompt = (
        f"위험 단계: {risk_stage}\n"
        f"대화 유형: {conversation_type}\n"
        f"참고 자료: {reference_text}\n"
        f"대화 발췌:\n{conversation_excerpt}\n"
        "출력은 JSON 형식이어야 한다."
    )

    try:
        client = OpenAI()
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=prompt,
            max_output_tokens=200,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "safe_actions",
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "summary": {"type": "string"},
                            "recommended_questions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                        },
                        "required": ["summary", "recommended_questions"],
                    },
                    "strict": True,
                }
            },
        )
        text = response.output_text.strip()
        if not text:
            logger.warning("OpenAI safe actions returned empty output; using fallback.")
            return None
        payload = json.loads(text)
        summary = str(payload.get("summary", "")).strip()
        questions = payload.get("recommended_questions", [])
        if not summary or not isinstance(questions, list):
            logger.warning("OpenAI safe actions missing fields; using fallback.")
            return None
        cleaned_questions = [str(item).strip() for item in questions if str(item).strip()]
        if len(cleaned_questions) != 2:
            logger.warning("OpenAI safe actions questions invalid; using fallback.")
            return None
        return {
            "summary": summary,
            "recommended_questions": cleaned_questions,
        }
    except Exception as exc:
        logger.exception("OpenAI safe actions failed: %s", exc)
        return None


def generate_safe_actions(
    risk_stage: str,
    conversation_type: str,
    references: List[Reference],
    conversation_lines: List[str],
) -> Dict[str, List[str] | str]:
    """요약과 추천 질문을 생성."""
    llm_result = _call_openai_safe_actions(
        risk_stage, conversation_type, references, conversation_lines
    )
    if llm_result:
        return llm_result

    return _fallback_safe_actions(risk_stage, references)
