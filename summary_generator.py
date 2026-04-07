import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from prompts import SUMMARY_SYSTEM_PROMPT

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_summary(item: dict) -> dict:
    title = item.get("title", "")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": f"제목: {title}"},
            ],
        )
        content = response.choices[0].message.content.strip()
        try:
            result = json.loads(content)
            item["summary_line1"] = result.get("summary_line1", "")
            item["summary_line2"] = result.get("summary_line2", "")
        except Exception:
            item["summary_line1"] = content
            item["summary_line2"] = ""
    except Exception as e:
        item["summary_line1"] = ""
        item["summary_line2"] = f"요약 실패: {e}"
    return item


def add_summaries(items: list) -> list:
    if not items:
        return items
    results = [None] * len(items)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(generate_summary, item): idx
                   for idx, item in enumerate(items)}
        for future in as_completed(futures):
            idx = futures[future]
            results[idx] = future.result()
    return results