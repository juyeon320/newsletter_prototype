#models.py
from dataclasses import dataclass

@dataclass
class NewsItem:
    keyword: str
    title: str
    link: str
    published_at_kst: str
    source: str
    summary: str = ""  # ← 추가