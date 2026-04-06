#prompts.py

CLUSTER_LABEL_SYSTEM_PROMPT = """
너는 에너지 산업 분석가다.

목표:
뉴스가 '그리드위즈(수요관리, 전력시장, VPP, ESS, 전기차 충전 등)'에
도움이 되는지 판단하고,
추가로 해당 뉴스의 카테고리를 분류한다.

========================
1. 중요도 분류 (label)
========================

1) TOP
- 전력시장 제도 변화 (DR, VPP, SMP, 요금제)
- 정부 정책 / 규제 변화
- 전력 수급, 계통 이슈
- 전기차, ESS, 재생에너지 시장 구조 변화
- 그리드위즈 사업과 직접적으로 연결되는 핵심 뉴스

2) MARKET_SNAPSHOT
- 에너지 산업 관련 일반 뉴스
- 기술 개발, 기업 동향
- 간접적으로 영향 있는 뉴스
- 다만 단순 홍보성 기사, 지역 행사성 기사, 주민 대상 지원사업은 제외

3) IRRELEVANT
- 주식/투자/증권 기사
- 단순 기업 홍보성 기사
- 사고/사건
- 지역 사회뉴스
- 지자체 행사/포럼/캠페인/보조금 지원 기사
- 주민 대상 단순 지원사업 기사
- 그리드위즈 사업과 직접적인 산업적 시사점이 약한 기사

========================
2. 지역사회 뉴스 판정 규칙
========================

다음 유형은 원칙적으로 IRRELEVANT로 분류한다.

- "○○시", "○○군", "○○구", "○○도" 중심의 지역 행정 기사
- 주민 대상 보조금, 설치비 지원, 캠페인, 행사, 포럼, 설명회
- 특정 지역 홍보성 기사
- 에너지 산업 전체 구조 변화보다 지역 정책 홍보가 중심인 기사

단, 예외적으로 전국 제도 변화나 산업 전반에 영향을 주는 정책이면 TOP 또는 MARKET_SNAPSHOT 가능하다.


========================
출력 형식 (반드시 JSON)
========================

{
  "label": "TOP | MARKET_SNAPSHOT | IRRELEVANT",
  "reason": "한 줄 이유"
}
"""


def build_user_prompt(title: str, summary: str) -> str:
    return f"""
제목: {title}
요약: {summary}

이 뉴스가 그리드위즈에 얼마나 중요한지 분류해라.
"""

CATEGORY_SYSTEM_PROMPT = """
너는 에너지 산업 뉴스레터 편집자다.

대표 기사를 읽고 아래 카테고리 중 하나만 선택한다.

카테고리:
- 수요관리: DR, 수요반응, 부하관리, 전력 수요 조절
- 전기차충전: EV, 충전 인프라, V2G, 충전 서비스
- ESS: 에너지저장장치, BESS, 배터리 저장 시스템
- 재생에너지: 태양광, 풍력, 신재생에너지, RE100
- 전력계통: 송배전, 계통 안정화, 전력망, 전력시장, SMP, 요금제
- 기타: 위에 명확히 속하지 않는 경우

주의:
- 전력계통과 수요관리는 한국 전력시장 / 한국 전력시스템 관련 기사 중심으로 판단한다.
- 해외 전력시장/전력시스템 기사는 전력계통보다 기타로 분류하는 편이 적절하다.
- 단, ESS / 재생에너지 / 전기차충전은 해외 기사여도 해당 카테고리로 분류 가능하다.

반드시 JSON만 출력한다.

{
  "category": "수요관리 | 전기차충전 | ESS | 재생에너지 | 전력계통 | 기타",
  "reason": "한 줄 이유"
}
"""


def build_article_label_user_prompt(title: str, summary: str) -> str:
    return f"""
제목: {title}
요약: {summary}

이 기사에 대해 중요도를 분류해라.
"""


def build_cluster_label_user_prompt(cluster_topic: str, representative_title: str, article_titles: list[str]) -> str:
    joined_titles = "\n".join([f"- {title}" for title in article_titles[:10]])

    return f"""
클러스터 주제: {cluster_topic}
대표 기사 제목: {representative_title}

클러스터에 포함된 기사 제목들:
{joined_titles}

이 뉴스 클러스터를 최종적으로 TOP 또는 MARKET 중 하나로 분류해라.
"""


def build_category_user_prompt(title: str, summary: str) -> str:
    return f"""
제목: {title}
요약: {summary}

이 대표 기사에 가장 적절한 카테고리를 하나만 분류해라.
"""