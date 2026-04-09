#classifier.py
from config import OUTPUT_DIR
 #"filtered_news.json" → f"{OUTPUT_DIR}/filtered_news.json"
# "classified_news.json" → f"{OUTPUT_DIR}/classified_news.json"
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, build_user_prompt

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 병렬 작업 수
MAX_WORKERS = 5


def classify_article(title: str, summary: str):
    user_prompt = build_user_prompt(title, summary)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except Exception:
        return {
            "label": "IRRELEVANT",
            "reason": content
        }


def process_article(idx: int, article: dict) -> tuple[int, dict]:
    title = article.get("title", "")
    summary = article.get("summary", "")

    try:
        result = classify_article(title, summary)
        article["label"] = result.get("label", "IRRELEVANT")
        article["reason"] = result.get("reason", "분류 실패")
    except Exception as e:
        article["label"] = "IRRELEVANT"
        article["reason"] = f"API 호출 실패: {str(e)}"

    return idx, article


def main():
    input_file = f"{OUTPUT_DIR}/filtered_news.json"
    output_file = f"{OUTPUT_DIR}/classified_news.json"

    if not os.path.exists(input_file):
        print(f"{input_file} 파일이 없습니다.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        articles = json.load(f)

    results = [None] * len(articles)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_article, idx, article): idx
            for idx, article in enumerate(articles)
        }

        for count, future in enumerate(as_completed(futures), start=1):
            idx = futures[future]

            try:
                result_idx, processed_article = future.result()
                results[result_idx] = processed_article
                print(f"[{count}/{len(articles)}] {processed_article['label']} - {processed_article['title']}")
            except Exception as e:
                print(f"[ERROR] {idx + 1}번째 기사 처리 실패: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n완료: {output_file} 생성됨")


if __name__ == "__main__":
    main()