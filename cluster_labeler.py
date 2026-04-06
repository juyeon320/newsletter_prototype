import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI
from dotenv import load_dotenv
from prompts import CLUSTER_LABEL_SYSTEM_PROMPT, build_cluster_label_user_prompt

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_WORKERS = 10


def classify_cluster_label(cluster_topic, representative_title, article_titles):
    user_prompt = build_cluster_label_user_prompt(
        cluster_topic,
        representative_title,
        article_titles,
    )

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": CLUSTER_LABEL_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except Exception:
        return {
            "cluster_label": "MARKET",
            "reason": content,
        }


def process_cluster(idx, cluster):
    representative = cluster.get("representative", {})
    representative_title = representative.get("title", "")

    cluster_topic = cluster.get("cluster_topic", representative_title)

    article_titles = [
        article.get("title", "")
        for article in cluster.get("articles", [])
    ]

    try:
        result = classify_cluster_label(
            cluster_topic,
            representative_title,
            article_titles,
        )

        cluster["cluster_label"] = result.get("cluster_label", "MARKET")
        cluster["cluster_reason"] = result.get("reason", "분류 실패")

    except Exception as e:
        cluster["cluster_label"] = "MARKET"
        cluster["cluster_reason"] = f"API 실패: {str(e)}"

    return idx, cluster


def main():
    input_file = "representative_news.json"
    output_file = "labeled_clusters.json"

    if not os.path.exists(input_file):
        print(f"{input_file} 파일이 없습니다.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        clusters = json.load(f)

    results = [None] * len(clusters)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_cluster, idx, cluster): idx
            for idx, cluster in enumerate(clusters)
        }

        for count, future in enumerate(as_completed(futures), start=1):
            idx = futures[future]

            try:
                result_idx, processed_cluster = future.result()
                results[result_idx] = processed_cluster

                rep = processed_cluster.get("representative", {})
                print(f"[{count}/{len(clusters)}] {processed_cluster['cluster_label']} - {rep.get('title', '')}")

            except Exception as e:
                print(f"[ERROR] {idx + 1}번째 실패: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n완료: {output_file} 생성됨")


if __name__ == "__main__":
    main()