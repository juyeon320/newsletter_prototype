from flask import Flask, render_template, jsonify, request
import json
import os
import subprocess
import sys
import threading

from datetime import datetime
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
    path = "output/representative_news.json"

    if not os.path.exists(path):
        return jsonify({"success": False, "items": []})

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = []

    for cluster in data:
        rep = cluster.get("representative", {})

        items.append({
            "id": f"cluster-{cluster.get('cluster_id')}",
            "title": rep.get("title"),
            "link": rep.get("link"),
            "source": rep.get("source"),
            "category": rep.get("label"),
            "topic": cluster.get("cluster_topic")
        })

    return jsonify({
        "success": True,
        "items": items
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
        result = subprocess.run(
            [sys.executable, "newsletter_pipeline.py"],
            capture_output=True,
            text=True,
            check=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        return jsonify({
            "success": True,
            "message": "생성 완료",
            "stdout": result.stdout
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            "success": False,
            "message": "파이프라인 실행 중 오류가 발생했습니다.",
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
    app.run(debug=True)