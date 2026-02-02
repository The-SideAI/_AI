from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class CorpusEntry:
    source: str
    note: str
    path: str
    tags: List[str] = field(default_factory=list)


AVAILABLE_CORPORA: List[CorpusEntry] = [
    CorpusEntry(
        source="정책브리핑",
        note="중고거래 피해 예방 안내",
        path="정책브리핑_뉴스기사1.md",
        tags=["중고거래", "3자사기", "안전결제", "택배거래", "계좌조회"]
    ),
    CorpusEntry(
        source="정책브리핑",
        note="보이스피싱 유의사항",
        path="정책브리핑_뉴스기사2.md",
        tags=["중고거래", "사이버사기", "택배거래", "3자사기", "안전결제", "직거래"]
    ),
    CorpusEntry(
        source="정책브리핑",
        note="보이스피싱 유의사항",
        path="정책브리핑_뉴스기사3.md",
        tags=["중고거래", "피해대처", "분쟁조정", "계좌조회", "사이버범죄"]
    ),
    CorpusEntry(
        source="정책브리핑",
        note="보이스피싱 유의사항",
        path="정책브리핑_뉴스기사4.md",
        tags=["중고거래", "티켓거래", "입금요구", "계좌조회", "사이버범죄"]
    ),
    CorpusEntry(
        source="고용노동부",
        note="취업사기사례",
        path="고용노동부_취업사기사례.md",
        tags=["취업사기", "개인정보", "공인인증서", "통장비밀번호", "대출", "구인광고"]
    ),
]
