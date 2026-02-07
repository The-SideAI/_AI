from dataclasses import dataclass
from typing import Dict, List


SUPPORTED_PLATFORMS = ("INSTAGRAM", "TELEGRAM")


@dataclass(frozen=True)
class PlatformGuidance:
    platform: str
    llm_instructions: str
    mandatory_recommendation: str
    recommendation_keywords: List[str]
    fallback_recommendations: List[str]


_GENERIC_GUIDANCE = PlatformGuidance(
    platform="GENERIC",
    llm_instructions=(
        "플랫폼 내 차단/신고 기능을 우선 사용하고, 외부 링크나 결제 유도는 피하도록 안내해라."
    ),
    mandatory_recommendation=(
        "대화 중인 플랫폼에서 상대 계정을 차단하고 사기/스팸 사유로 신고하세요."
    ),
    recommendation_keywords=["차단", "신고", "플랫폼"],
    fallback_recommendations=[
        "외부 링크나 결제 요청은 즉시 중단하고 사실 여부를 재확인하세요.",
        "플랫폼 보안 설정에서 2단계 인증과 로그인 이력 점검을 진행하세요.",
    ],
)


_PLATFORM_GUIDANCE: Dict[str, PlatformGuidance] = {
    "INSTAGRAM": PlatformGuidance(
        platform="INSTAGRAM",
        llm_instructions=(
            "인스타그램 DM/프로필 링크 기반 사기 가능성을 고려해 "
            "차단/신고, 링크 검증, 계정 보안 점검 조치를 포함해라."
        ),
        mandatory_recommendation=(
            "인스타그램에서 해당 계정을 차단하고 사기/스팸 사유로 신고하세요."
        ),
        recommendation_keywords=["인스타그램", "dm", "프로필", "차단", "신고"],
        fallback_recommendations=[
            "인스타그램 DM으로 받은 외부 결제 링크나 프로필 링크 접속은 피하세요.",
            "인스타그램 보안 설정에서 2단계 인증을 활성화하고 로그인 활동을 점검하세요.",
        ],
    ),
    "TELEGRAM": PlatformGuidance(
        platform="TELEGRAM",
        llm_instructions=(
            "텔레그램 초대 링크/비공개 대화 기반 사기 가능성을 고려해 "
            "차단/신고, 링크 검증, 계정 보안 점검 조치를 포함해라."
        ),
        mandatory_recommendation=(
            "텔레그램에서 해당 계정을 차단하고 스팸/사기 사유로 신고하세요."
        ),
        recommendation_keywords=["텔레그램", "telegram", "차단", "신고", "초대 링크"],
        fallback_recommendations=[
            "텔레그램에서 받은 초대 링크나 외부 결제 링크는 검증 전까지 열지 마세요.",
            "텔레그램 개인정보·보안 설정에서 2단계 인증과 활성 세션을 점검하세요.",
        ],
    ),
}


def get_platform_guidance(platform: str) -> PlatformGuidance:
    key = str(platform or "").strip().upper()
    return _PLATFORM_GUIDANCE.get(key, _GENERIC_GUIDANCE)


def supported_platforms_text() -> str:
    return ", ".join(SUPPORTED_PLATFORMS)
