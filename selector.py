import json
from typing import List, Dict, Any
from openai import OpenAI
from prompts import TOP_NEWS_SELECTOR_PROMPT

client = OpenAI()

TOP_NEWS_MAX = 2

MAX_PER_CATEGORY = {
    "수요관리": 5,
    "전기차": 5,
    "에너지저장장치": 5,
    "재생에너지": 5,
    "전력시스템": 5,
    "기타": 5,
}

CATEGORY_ORDER = ["수요관리", "전기차", "에너지저장장치", "재생에너지", "전력시스템", "기타"]
KOREAN_SOURCES = [
    "연합뉴스", "뉴스1", "전기신문", "전자신문",
    "한국경제", "매일경제", "서울경제", "머니투데이",
    "이투뉴스", "에너지경제신문", "투데이에너지",
    "에너지신문", "에너지데일리", "에너지프로슈머",
    "임팩트온", "뉴시스", "KBS", "MBC", "SBS",
    "한겨레", "경향신문", "조선일보", "중앙일보", "동아일보",
    "네이트", "네이버", "다음"
]

OPINION_PREFIXES = ["기자의눈", "브리핑ON", "칼럼", "오피니언", "[기자", "(기자"]

def is_opinion_article(title: str) -> bool:
    return any(prefix in title for prefix in OPINION_PREFIXES)

def is_korean_news(article: Dict[str, Any]) -> bool:
    source = article.get("source", "")
    return any(keyword in source for keyword in KOREAN_SOURCES)

def adjust_category(article: Dict[str, Any], category: str) -> str:
    if category in ("전력시스템", "수요관리"):
        if not is_korean_news(article):
            return "기타"
    return category

def select_top_news_by_llm(candidates: list) -> list:
    if not candidates:
        return []

    numbered = "\n".join(
        [f"[{i}] {a['title']} - {a['source']}" for i, a in enumerate(candidates)]
    )

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": TOP_NEWS_SELECTOR_PROMPT},
            {"role": "user", "content": numbered},
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    indices = result.get("top_indices", [])
    valid = [i for i in indices if 0 <= i < len(candidates)]
    return [candidates[i] for i in valid[:TOP_NEWS_MAX]]

def score_cluster(cluster: Dict[str, Any]) -> int:
    rep = cluster.get("representative", {})
    title = rep.get("title", "")
    source = rep.get("source", "")
    cluster_label = cluster.get("cluster_label", "MARKET_SNAPSHOT")
    category = cluster.get("category", "기타")

    score = 0

    if cluster_label == "TOP":
        score += 50
    else:
        score += 20

    if category in ("전력시스템", "수요관리", "재생에너지", "에너지저장장치", "전기차"):
        score += 10

    major_keywords = [
        "정부", "기후부", "전력시장", "전기요금", "요금제", "계통",
        "수급", "재생에너지", "석탄", "vpp", "ess", "데이터센터", "ai"
    ]
    if any(keyword.lower() in title.lower() for keyword in major_keywords):
        score += 20

    trusted_like = ["연합뉴스", "뉴스1", "전기신문", "전자신문", "한국경제", "매일경제", "서울경제"]
    if any(t in source for t in trusted_like):
        score += 5

    return score

def build_market_snapshot_buckets() -> Dict[str, List[Dict[str, Any]]]:
    return {category: [] for category in CATEGORY_ORDER}

def cluster_to_item(cluster: Dict[str, Any]) -> Dict[str, Any]:
    rep = cluster.get("representative", {})
    category = adjust_category(rep, cluster.get("category", "기타"))

    return {
        "cluster_id": cluster.get("cluster_id"),
        "cluster_topic": cluster.get("cluster_topic"),
        "article_count": cluster.get("article_count", 1),
        "title": rep.get("title", ""),
        "source": rep.get("source", ""),
        "published_at_kst": rep.get("published_at_kst", ""),
        "category": category,
        "cluster_label": cluster.get("cluster_label", "MARKET_SNAPSHOT"),
        "cluster_reason": cluster.get("cluster_reason", ""),
        "link": rep.get("link", ""),
        "score": score_cluster(cluster),
    }

def select_top_news(clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Step 1: TOP 라벨 우선, 없으면 전체 클러스터에서 선택
    all_top = [cluster_to_item(c) for c in clusters if c.get("cluster_label") == "TOP"]

    if not all_top:  # ← 이 부분 추가
        all_top = [cluster_to_item(c) for c in clusters]

    # Step 2: 칼럼/기자의눈 제외
    non_opinion = [item for item in all_top if not is_opinion_article(item["title"])]
    candidates = non_opinion if non_opinion else all_top

    # Step 3: 점수 정렬 후 상위 10개 LLM 전달
    candidates.sort(key=lambda x: x["score"], reverse=True)

    # Step 4: LLM 최종 선정
    selected = select_top_news_by_llm(candidates[:10])
    if selected:
        return selected

    # Fallback
    return candidates[:TOP_NEWS_MAX]

def select_market_snapshot(
    clusters: List[Dict[str, Any]],
    top_news: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    top_links = {item["link"] for item in top_news}
    buckets = build_market_snapshot_buckets()
    remaining = []

    for cluster in clusters:
        item = cluster_to_item(cluster)
        if item["link"] in top_links:
            continue
        if item["cluster_label"] not in ("TOP", "MARKET_SNAPSHOT"):
            continue
        remaining.append(item)

    remaining.sort(key=lambda x: x["score"], reverse=True)

    for article in remaining:
        category = article.get("category", "기타")
        if category not in buckets:
            category = "기타"
        buckets[category].append(article)

    for category, items in buckets.items():
        max_count = MAX_PER_CATEGORY.get(category)
        if max_count:
            buckets[category] = items[:max_count]

    return buckets

def build_newsletter_result(categorized_clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
    top_news = select_top_news(categorized_clusters)
    market_snapshot = select_market_snapshot(categorized_clusters, top_news)

    return {
        "top_news": top_news,
        "market_snapshot": market_snapshot,
    }