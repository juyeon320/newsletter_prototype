from flask import Flask, render_template, jsonify, request
import json
import os
import subprocess
import sys
import threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from summary_generator import generate_summary

app = Flask(__name__)

RESULT_PATH = "output/newsletter_result.json"

# 중복 실행 방지
pipeline_lock = threading.Lock()
is_running = False


def get_last_run_time():
    if os.path.exists(RESULT_PATH):
        return datetime.fromtimestamp(
            os.path.getmtime(RESULT_PATH)
        ).strftime("%Y-%m-%d %H:%M:%S")
    return "없음"

def get_collection_time_range():
    kst = ZoneInfo("Asia/Seoul")
    now = datetime.now(kst)

    today_1300 = now.replace(hour=13, minute=0, second=0, microsecond=0)

    if now >= today_1300:
        end_time = today_1300
    else:
        end_time = today_1300 - timedelta(days=1)

    # 월요일이면 금요일 13시 ~ 월요일 13시
    if end_time.weekday() == 0:
        start_time = end_time - timedelta(days=3)
    else:
        start_time = end_time - timedelta(days=1)

    return f"{start_time.strftime('%Y.%m.%d %H:%M:%S')} ~ {end_time.strftime('%Y.%m.%d %H:%M:%S')}"

# 시작 페이지
@app.route("/")
def start():
    last_run_time = get_last_run_time()
    return render_template("start.html", last_run_time=last_run_time)


# 프리로더 페이지
@app.route("/run-page")
def run_page():
    last_run_time = get_last_run_time()
    return render_template("run.html", last_run_time=last_run_time)


# 뉴스레터 결과 페이지
@app.route("/newsletter")
def newsletter():
    data = {}
    last_run_time = "없음"

    if os.path.exists(RESULT_PATH):
        last_run_time = datetime.fromtimestamp(
            os.path.getmtime(RESULT_PATH)
        ).strftime("%Y-%m-%d %H:%M:%S")

        with open(RESULT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

    return render_template("index.html", data=data, last_run_time=last_run_time)

@app.route("/api/all-news")
def all_news():
    path = "output/classified_news.json"

    if not os.path.exists(path):
        return jsonify({
            "success": False,
            "items": [],
            "time_range": get_collection_time_range()
        })

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = []

    for idx, article in enumerate(data):
        published_at = (
            article.get("published_at")
            or article.get("published_at_kst")  # 👈 이거 추가
            or article.get("published")
            or article.get("pub_date")
            or article.get("published_date")
            or article.get("date")
            or ""
        )

        items.append({
            "id": article.get("id") or f"news-{idx}",
            "title": article.get("title", ""),
            "link": article.get("link", ""),
            "source": article.get("source", ""),
            "category": article.get("label") or article.get("category") or "",
            "summary": article.get("summary", ""),
            "published_at": published_at
        })

    return jsonify({
        "success": True,
        "items": items,
        "time_range": get_collection_time_range()
    })


@app.route("/api/summary", methods=["POST"])
def summarize_news():
    try:
        data = request.get_json()
        title = (data.get("title") or "").strip()

        if not title:
            return jsonify({
                "success": False,
                "message": "제목이 없습니다."
            }), 400

        result = generate_summary({
            "title": title
        })

        return jsonify({
            "success": True,
            "summary_line1": result.get("summary_line1", ""),
            "summary_line2": result.get("summary_line2", ""),
            "summary_points": result.get("summary_points", [])
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"요약 생성 중 오류가 발생했습니다: {str(e)}"
        }), 500

# 파이프라인 실행 API
@app.route("/api/run", methods=["POST"])
def run_pipeline():
    global is_running

    with pipeline_lock:
        if is_running:
            return jsonify({
                "success": False,
                "message": "이미 생성 작업이 진행 중입니다."
            }), 409
        is_running = True

    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logs = []

        scripts = [
            "news_collector.py",
            "classifier.py",
            "newsletter_pipeline.py"
        ]

        for script in scripts:
            logs.append(f"\n===== {script} 실행 시작 =====\n")

            result = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
                check=True,
                cwd=base_dir
            )

            if result.stdout:
                logs.append(result.stdout)
            if result.stderr:
                logs.append(result.stderr)

            logs.append(f"\n===== {script} 실행 완료 =====\n")

        return jsonify({
            "success": True,
            "message": "뉴스 수집부터 뉴스레터 생성까지 완료되었습니다.",
            "stdout": "\n".join(logs)
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            "success": False,
            "message": f"{os.path.basename(e.cmd[1])} 실행 중 오류가 발생했습니다.",
            "stdout": e.stdout,
            "stderr": e.stderr
        }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"서버 오류: {str(e)}"
        }), 500

    finally:
        with pipeline_lock:
            is_running = False


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)

#if __name__ == "__main__":
#   app.run(debug=True)
    