# representative.py
from typing import Dict, Any, List
from config import TRUSTED_SOURCES

# GridWiz 핵심 주제 키워드
CORE_KEYWORDS = [
    "수요관리", "수요반응", "VPP", "플러스DR", "마이너스DR",
    "수요자원", "그리드위즈", "Gridwiz", "DR사업", "가상발전소"
]

def source_priority(source: str) -> int:
    for idx, trusted in enumerate(TRUSTED_SOURCES):
        if trusted in source:
            return idx
    return 9999

def is_trusted_source(source: str) -> bool:
    return any(trusted in source for trusted in TRUSTED_SOURCES)

def has_core_keyword(article: Dict[str, Any]) -> bool:
    title = article.get("title", "")
    return any(kw in title for kw in CORE_KEYWORDS)

def choose_representative_article(cluster: Dict[str, Any]) -> Dict[str, Any]:
    articles: List[Dict[str, Any]] = cluster["articles"]

    trusted_articles = [
        article for article in articles
        if is_trusted_source(article.get("source", ""))
    ]
    candidates = trusted_articles if trusted_articles else articles

    # 1순위: 핵심 키워드(수요관리/VPP/DR) 포함 기사
    priority = [a for a in candidates if has_core_keyword(a)]
    if priority:
        priority.sort(key=lambda x: (
            source_priority(x.get("source", "")),
            x.get("published_at_kst", "")
        ))
        chosen = priority[0]
    else:
        # 2순위: 기존 로직 (신뢰 출처 + 발행일)
        candidates.sort(key=lambda x: (
            source_priority(x.get("source", "")),
            x.get("published_at_kst", "")
        ))
        chosen = candidates[0]

    return {
        "cluster_id": cluster["cluster_id"],
        "cluster_topic": cluster["cluster_topic"],
        "article_count": len(articles),
        "representative": chosen,
        "articles": articles,
    }

def choose_representatives(clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [choose_representative_article(cluster) for cluster in clusters]