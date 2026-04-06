# newsletter_pipeline.py
import json
import os

from clusterer import cluster_articles
from representative import choose_representatives
from cluster_labeler import process_cluster as process_cluster_label
from category_classifier import process_cluster as process_cluster_category
from selector import build_newsletter_result


def main():
    input_file = "classified_news.json"
    clusters_file = "clustered_news.json"
    representatives_file = "representative_news.json"
    cluster_labeled_file = "labeled_clusters.json"
    categorized_file = "categorized_clusters.json"
    output_file = "newsletter_result.json"

    if not os.path.exists(input_file):
        print(f"{input_file} 파일이 없습니다.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        articles = json.load(f)

    # 1. TOP / MARKET 기사만 클러스터링
    clusters = cluster_articles(articles)
    with open(clusters_file, "w", encoding="utf-8") as f:
        json.dump(clusters, f, ensure_ascii=False, indent=2)
    print(f"클러스터링 완료: {clusters_file}")

    # 2. 각 클러스터 대표 기사 선정
    representatives = choose_representatives(clusters)
    with open(representatives_file, "w", encoding="utf-8") as f:
        json.dump(representatives, f, ensure_ascii=False, indent=2)
    print(f"대표 기사 선정 완료: {representatives_file}")

    # 3. 클러스터 단위 TOP/MARKET 재판단
    labeled_clusters = []
    for idx, cluster in enumerate(representatives):
        _, processed = process_cluster_label(idx, cluster)
        labeled_clusters.append(processed)

    with open(cluster_labeled_file, "w", encoding="utf-8") as f:
        json.dump(labeled_clusters, f, ensure_ascii=False, indent=2)
    print(f"클러스터 라벨링 완료: {cluster_labeled_file}")

    # 4. 대표 기사에 카테고리 부여
    categorized_clusters = []
    for idx, cluster in enumerate(labeled_clusters):
        _, processed = process_cluster_category(idx, cluster)
        categorized_clusters.append(processed)

    with open(categorized_file, "w", encoding="utf-8") as f:
        json.dump(categorized_clusters, f, ensure_ascii=False, indent=2)
    print(f"카테고리 분류 완료: {categorized_file}")

    # 5. 최종 결과 생성
    newsletter_result = build_newsletter_result(categorized_clusters)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(newsletter_result, f, ensure_ascii=False, indent=2)
    print(f"최종 결과 생성 완료: {output_file}")

    print("\n=== Top News ===")
    for idx, item in enumerate(newsletter_result["top_news"], start=1):
        print(f"[{idx}] {item['title']} ({item['source']})")

    print("\n=== Market Snapshot ===")
    for category, items in newsletter_result["market_snapshot"].items():
        print(f"\n[{category}] {len(items)}건")
        for item in items:
            print(f"- {item['title']} ({item['source']})")


if __name__ == "__main__":
    main()