from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# 简单内存数据库（真正上线可以换成数据库）
messages = []  # 每条是 dict: {"name": ..., "text": ..., "time": ...}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/messages", methods=["GET"])
def get_messages():
    # 返回所有留言
    return jsonify(messages)

@app.route("/api/messages", methods=["POST"])
def add_message():
    data = request.get_json()
    name = data.get("name", "匿名同学")
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "留言内容不能为空"}), 400

    msg = {
        "name": name or "匿名同学",
        "text": text,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    messages.insert(0, msg)  # 最新在最前面
    return jsonify({"ok": True, "message": msg}), 201

if __name__ == "__main__":
    # 本地调试用，Render 上会自己用 gunicorn 之类来跑
    app.run(host="0.0.0.0", port=5000, debug=True)
