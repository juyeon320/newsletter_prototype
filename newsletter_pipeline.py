import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import OUTPUT_DIR
from clusterer import cluster_articles
from representative import choose_representatives
from cluster_labeler import process_cluster as process_cluster_label
from category_classifier import process_cluster as process_cluster_category
from selector import build_newsletter_result
from summary_generator import add_summaries

GRIDWIZ_KEYWORDS = ["그리드위즈", "Gridwiz", "GridWiz"]

def is_gridwiz_article(article: dict) -> bool:
    title = article.get("title", "")
    summary = article.get("summary", "")
    return any(kw in title or kw in summary for kw in GRIDWIZ_KEYWORDS)


def main():
    input_file = f"{OUTPUT_DIR}/classified_news.json"
    clusters_file = f"{OUTPUT_DIR}/clustered_news.json"
    representatives_file = f"{OUTPUT_DIR}/representative_news.json"
    output_file = f"{OUTPUT_DIR}/newsletter_result.json"

    if not os.path.exists(input_file):
        print(f"{input_file} 파일이 없습니다.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        articles = json.load(f)

    # 1. 클러스터링
    clusters = cluster_articles(articles)
    with open(clusters_file, "w", encoding="utf-8") as f:
        json.dump(clusters, f, ensure_ascii=False, indent=2)
    print(f"클러스터링 완료: {clusters_file}")

    # 2. 대표 기사 선정
    representatives = choose_representatives(clusters)
    with open(representatives_file, "w", encoding="utf-8") as f:
        json.dump(representatives, f, ensure_ascii=False, indent=2)
    print(f"대표 기사 선정 완료: {representatives_file}")

    # 3. TOP/MARKET_SNAPSHOT 재판단
    labeled_results = [None] * len(representatives)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_cluster_label, idx, cluster): idx
                   for idx, cluster in enumerate(representatives)}
        for future in as_completed(futures):
            try:
                idx, processed = future.result()
                labeled_results[idx] = processed
            except Exception as e:
                print(f"[ERROR] cluster_label 실패: {e}")
    labeled_clusters = labeled_results

    # 4. 카테고리 부여
    categorized_results = [None] * len(labeled_clusters)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_cluster_category, idx, cluster): idx
                   for idx, cluster in enumerate(labeled_clusters)
                   if cluster is not None}
        for future in as_completed(futures):
            try:
                idx, processed = future.result()
                categorized_results[idx] = processed
            except Exception as e:
                print(f"[ERROR] category 실패: {e}")
    categorized_clusters = categorized_results

    # 5. 최종 결과 생성
    newsletter_result = build_newsletter_result(categorized_clusters)

    # 그리드위즈 기사 분리
    gridwiz_news = []
    filtered_top = []

    for item in newsletter_result["top_news"]:
        if is_gridwiz_article(item):
            gridwiz_news.append(item)
        else:
            filtered_top.append(item)

    for cat, items in newsletter_result["market_snapshot"].items():
        remaining = []
        for item in items:
            if is_gridwiz_article(item):
                gridwiz_news.append(item)
            else:
                remaining.append(item)
        newsletter_result["market_snapshot"][cat] = remaining

    newsletter_result["top_news"] = filtered_top
    newsletter_result["gridwiz_news"] = gridwiz_news
    newsletter_result["market_snapshot"].pop("기타", None)

    # 요약 생성
    print("요약 생성 중...")
    newsletter_result["gridwiz_news"] = add_summaries(gridwiz_news)
    newsletter_result["top_news"] = add_summaries(filtered_top)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(newsletter_result, f, ensure_ascii=False, indent=2)
    print(f"완료: {output_file}")

    # 출력
    print("\n=== 그리드위즈 뉴스 ===")
    for item in newsletter_result["gridwiz_news"]:
        print(f"- {item['title']}")

    print("\n=== Top News ===")
    for idx, item in enumerate(newsletter_result["top_news"], start=1):
        print(f"[{idx}] {item['title']} ({item['source']})")

    print("\n=== Market Snapshot ===")
    for category, items in newsletter_result["market_snapshot"].items():
        print(f"\n[{category}] {len(items)}건")
        for item in items:
            print(f"- {item['title']} ({item['source']})")

import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

import json
json_str = json.dumps(newsletter_result, ensure_ascii=False)
html = re.sub(r'const DATA = \{.*?\};', f'const DATA = {json_str};', html, flags=re.DOTALL)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
    
if __name__ == "__main__":
    main()