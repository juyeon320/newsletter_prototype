# representative.py
from typing import Dict, Any, List

from config import TRUSTED_SOURCES


def source_priority(source: str) -> int:
    for idx, trusted in enumerate(TRUSTED_SOURCES):
        if trusted in source:
            return idx
    return 9999


def is_trusted_source(source: str) -> bool:
    return any(trusted in source for trusted in TRUSTED_SOURCES)


def choose_representative_article(cluster: Dict[str, Any]) -> Dict[str, Any]:
    articles: List[Dict[str, Any]] = cluster["articles"]

    trusted_articles = [
        article for article in articles
        if is_trusted_source(article.get("source", ""))
    ]

    if trusted_articles:
        trusted_articles.sort(
            key=lambda x: (
                source_priority(x.get("source", "")),
                x.get("published_at_kst", "")
            )
        )
        chosen = trusted_articles[0]
    else:
        chosen = articles[0]

    return {
        "cluster_id": cluster["cluster_id"],
        "cluster_topic": cluster["cluster_topic"],
        "article_count": len(articles),
        "representative": chosen,
        "articles": articles,
    }


def choose_representatives(clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [choose_representative_article(cluster) for cluster in clusters]