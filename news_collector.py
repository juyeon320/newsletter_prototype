from datetime import datetime
from typing import List

import feedparser

from config import (
    KST,
    STOCK_EXCLUDE_KEYWORDS,
    LOCAL_EXCLUDE_KEYWORDS,
    KEYWORDS,
)
from filters import (
    deduplicate_news,
    filter_foreign_news,
    filter_stock_news,
    filter_local_news,
)
from models import NewsItem
from utils import (
    get_news_window,
    build_google_news_rss_url,
    parse_entry_datetime,
    save_news_to_json,
)


def collect_news_by_keyword(
    keyword: str,
    start: datetime,
    end: datetime,
    max_items: int = 50,
) -> List[NewsItem]:
    url = build_google_news_rss_url(keyword)
    feed = feedparser.parse(url)

    items: List[NewsItem] = []

    for entry in feed.entries:
        published_dt_utc = parse_entry_datetime(entry)
        if published_dt_utc is None:
            continue

        published_dt_kst = published_dt_utc.astimezone(KST)

        if not (start <= published_dt_kst <= end):
            continue

        source = ""
        if hasattr(entry, "source") and entry.source:
            source = entry.source.get("title", "")
        elif hasattr(entry, "author"):
            source = entry.author

        item = NewsItem(
            keyword=keyword,
            title=getattr(entry, "title", "").strip(),
            link=getattr(entry, "link", "").strip(),
            published_at_kst=published_dt_kst.isoformat(),
            source=source.strip(),
        )
        items.append(item)

        if len(items) >= max_items:
            break

    return items


def collect_news_for_keywords(
    keywords: List[str],
    start: datetime,
    end: datetime,
    max_items_per_keyword: int = 50,
) -> List[NewsItem]:
    all_items: List[NewsItem] = []

    for keyword in keywords:
        try:
            news = collect_news_by_keyword(
                keyword=keyword,
                start=start,
                end=end,
                max_items=max_items_per_keyword,
            )
            all_items.extend(news)
        except Exception as e:
            print(f"[ERROR] keyword='{keyword}' 수집 실패: {e}")

    deduped = deduplicate_news(all_items)
    deduped.sort(key=lambda x: x.published_at_kst, reverse=True)
    return deduped


if __name__ == "__main__":
    now_kst = datetime.now(KST)
    start, end = get_news_window(now_kst)

    print("수집 시작:", start)
    print("수집 종료:", end)

    all_results = collect_news_for_keywords(
        keywords=KEYWORDS,
        start=start,
        end=end,
        max_items_per_keyword=50,
    )
    print(f"[1차 수집] 총 {len(all_results)}건")

    filtered_no_foreign = filter_foreign_news(all_results)
    print(f"[해외 뉴스 필터 후] 총 {len(filtered_no_foreign)}건")

    filtered_no_stock = filter_stock_news(
        filtered_no_foreign,
        STOCK_EXCLUDE_KEYWORDS,
    )
    print(f"[주가 뉴스 필터 후] 총 {len(filtered_no_stock)}건")

    filtered_no_local = filter_local_news(
        filtered_no_stock,
        LOCAL_EXCLUDE_KEYWORDS,
    )
    print(f"[지역사회 뉴스 필터 후] 총 {len(filtered_no_local)}건")

    final_results = filtered_no_local

    save_news_to_json("filtered_news.json", final_results)
    print("filtered_news.json 저장 완료\n")

    for item in final_results:
        print("=" * 80)
        print(f"[키워드] {item.keyword}")
        print(f"[제목] {item.title}")
        print(f"[언론사] {item.source}")
        print(f"[발행시각 KST] {item.published_at_kst}")
        print(f"[링크] {item.link}")