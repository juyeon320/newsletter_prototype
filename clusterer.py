
#clusterer.py

# clusterer.py
import re
from difflib import SequenceMatcher
from typing import List, Dict, Any

from config import CLUSTER_SIMILARITY_THRESHOLD


STOPWORDS = {
    "정부", "기후부", "추진", "도입", "조기", "달성", "중심", "기반",
    "관련", "가속화", "개편", "추진…", "추진...", "보급",
    "한다", "한다.", "추진한다", "통해", "위해", "대한", "및", "에서", "으로",
    "까지", "전면", "조기달성", "추진\"", "추진”"
}


def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"\[[^\]]+\]", " ", title)   # [속보] 제거
    title = re.sub(r"\([^)]+\)", " ", title)    # (종합) 제거
    title = re.sub(r"[\"'“”‘’]", " ", title)
    title = re.sub(r"[^0-9a-zA-Z가-힣\s]", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def title_tokens(title: str) -> set[str]:
    normalized = normalize_title(title)
    tokens = set(normalized.split())
    return {t for t in tokens if len(t) >= 2 and t not in STOPWORDS}


def jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def sequence_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def combined_similarity(title1: str, title2: str) -> float:
    token_score = jaccard_similarity(title_tokens(title1), title_tokens(title2))
    seq_score = sequence_similarity(title1, title2)
    return max(token_score, seq_score)


def is_similar_article(article1: Dict[str, Any], article2: Dict[str, Any]) -> bool:
    score = combined_similarity(article1["title"], article2["title"])
    return score >= CLUSTER_SIMILARITY_THRESHOLD


def filter_relevant_articles(articles):
    return [a for a in articles if a.get("label") in ("TOP", "MARKET_SNAPSHOT")]

def cluster_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    relevant_articles = filter_relevant_articles(articles)
    clusters: List[Dict[str, Any]] = []

    MAX_CLUSTER_SIZE = 5  # 클러스터 최대 크기 제한

    for article in relevant_articles:
        placed = False

        for cluster in clusters:
            # 최대 크기 초과 클러스터 건너뜀
            if len(cluster["articles"]) >= MAX_CLUSTER_SIZE:
                continue

            # 아무 기사가 아닌 대표 기사(첫 기사)와만 비교 → 체인 방지
            representative = cluster["articles"][0]
            if is_similar_article(article, representative):
                cluster["articles"].append(article)
                placed = True
                break

        if not placed:
            clusters.append({
                "cluster_id": len(clusters) + 1,
                "articles": [article],
                "cluster_topic": article["title"],
            })

    return clusters