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
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": f"제목: {title}"},
            ],
        )

        content = response.choices[0].message.content.strip()

        summary_line1 = ""
        summary_line2 = ""

        try:
            result = json.loads(content)
            summary_line1 = result.get("summary_line1", "").strip()
            summary_line2 = result.get("summary_line2", "").strip()
        except Exception:
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            summary_line1 = lines[0] if len(lines) > 0 else ""
            summary_line2 = lines[1] if len(lines) > 1 else ""

        summary_points = []
        if summary_line1:
            summary_points.append(summary_line1)
        if summary_line2:
            summary_points.append(summary_line2)

        item["summary_line1"] = summary_line1
        item["summary_line2"] = summary_line2
        item["summary_points"] = summary_points
        item["summary"] = " ".join(summary_points)

    except Exception as e:
        item["summary_line1"] = ""
        item["summary_line2"] = ""
        item["summary_points"] = []
        item["summary"] = ""
        item["summary_error"] = str(e)

    return item


def add_summaries(items: list) -> list:
    if not items:
        return items

    results = [None] * len(items)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(generate_summary, item): idx
            for idx, item in enumerate(items)
        }

        for future in as_completed(futures):
            idx = futures[future]
            results[idx] = future.result()

    return results