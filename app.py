from flask import Flask, render_template
import json
import os
import subprocess

app = Flask(__name__)


@app.route("/")
def index():
    data = {}

    if os.path.exists("newsletter_result.json"):
        with open("newsletter_result.json", "r", encoding="utf-8") as f:
            data = json.load(f)

    return render_template("index.html", data=data)


@app.route("/run")
def run_pipeline():
    subprocess.run(["python", "newsletter_pipeline.py"])
    return "뉴스 생성 완료! 다시 / 로 가서 확인"


if __name__ == "__main__":
    app.run(debug=True)