import json
import time
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import quote

from config import KST, GOOGLE_NEWS_RSS_SEARCH_URL
from models import NewsItem


def get_news_window(now: datetime) -> tuple[datetime, datetime]:
    now = now.astimezone(KST)

    if now.weekday() == 0:  # Monday
        friday = now - timedelta(days=3)
        start = friday.replace(hour=15, minute=0, second=0, microsecond=0)
    else:
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=9, minute=0, second=0, microsecond=0)

    end = now
    return start, end


def build_google_news_rss_url(keyword: str) -> str:
    encoded_query = quote(keyword)
    return GOOGLE_NEWS_RSS_SEARCH_URL.format(query=encoded_query)


def parse_entry_datetime(entry) -> Optional[datetime]:
    time_struct = None

    if hasattr(entry, "published_parsed") and entry.published_parsed:
        time_struct = entry.published_parsed
    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
        time_struct = entry.updated_parsed

    if not time_struct:
        return None

    return datetime.fromtimestamp(time.mktime(time_struct), tz=timezone.utc)


def save_news_to_json(filename: str, items: list[NewsItem]) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump([asdict(item) for item in items], f, ensure_ascii=False, indent=2)