#filters.py
from typing import List

from config import (
    ALLOWED_FOREIGN_KEYWORDS,
    FOREIGN_KEYWORDS,
)
from models import NewsItem

import re

def filter_non_korean_titles(items: List[NewsItem]) -> List[NewsItem]:
    return [item for item in items if re.search(r'[가-힣]', item.title)]

def deduplicate_news(items: List[NewsItem]) -> List[NewsItem]:
    seen = set()
    unique_items = []

    for item in items:
        if item.link in seen:
            continue
        seen.add(item.link)
        unique_items.append(item)

    return unique_items


def filter_by_allowed_sources(items: List[NewsItem], allowed_sources: List[str]) -> List[NewsItem]:
    filtered = []

    for item in items:
        if any(allowed_source in item.source for allowed_source in allowed_sources):
            filtered.append(item)

    return filtered


def is_foreign_news(title: str) -> bool:
    return any(keyword in title for keyword in FOREIGN_KEYWORDS)


def is_allowed_foreign_news(title: str) -> bool:
    return any(keyword in title for keyword in ALLOWED_FOREIGN_KEYWORDS)


def filter_foreign_news(items: List[NewsItem]) -> List[NewsItem]:
    filtered = []

    for item in items:
        title = item.title.strip()

        if not is_foreign_news(title):
            filtered.append(item)
            continue

        if is_allowed_foreign_news(title):
            filtered.append(item)
            continue

    return filtered


def filter_stock_news(items: List[NewsItem], exclude_keywords: List[str]) -> List[NewsItem]:
    filtered = []

    for item in items:
        title = item.title.strip()
        if any(keyword in title for keyword in exclude_keywords):
            continue
        filtered.append(item)

    return filtered


def filter_local_news(items: List[NewsItem], exclude_keywords: List[str]) -> List[NewsItem]:
    filtered = []

    for item in items:
        title = item.title.strip()
        if any(keyword in title for keyword in exclude_keywords):
            continue
        filtered.append(item)

    return filtered

def deduplicate_by_title(items: List[NewsItem]) -> List[NewsItem]:
    seen_titles = set()
    unique_items = []

    for item in items:
        title = item.title.strip().lower()

        if title in seen_titles:
            continue

        seen_titles.add(title)
        unique_items.append(item)

    return unique_items