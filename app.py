import os
from uuid import uuid4

from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==== 配置头像上传 ====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "avatars")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ==== 饽饽山成员数据（你可以以后改名字） ====
members = [
    {"id": 1, "name": "饽饽山 1号", "avatar": None},
    {"id": 2, "name": "饽饽山 2号", "avatar": None},
    {"id": 3, "name": "饽饽山 3号", "avatar": None},
    {"id": 4, "name": "饽饽山 4号", "avatar": None},
    {"id": 5, "name": "饽饽山 5号", "avatar": None},
    {"id": 6, "name": "饽饽山 6号", "avatar": None},
    {"id": 7, "name": "饽饽山 7号", "avatar": None},
    {"id": 8, "name": "饽饽山 8号", "avatar": None},
    {"id": 9, "name": "饽饽山 9号", "avatar": None},
    {"id": 10, "name": "饽饽山 10号", "avatar": None},
]

# 评分统计：每个成员的总分和评分次数
member_stats = {
    m["id"]: {"total_score": 0, "rating_count": 0}
    for m in members
}

# 保存所有评价记录（目前只是内存，不写数据库）
ratings = []  # 每条: {rater_id, target_id, score, comment}


def get_member(member_id: int):
    for m in members:
        if m["id"] == member_id:
            return m
    return None


def build_board_data():
    """把成员 + 统计数据合并，方便模板使用"""
    board = []
    for m in members:
        stats = member_stats[m["id"]]
        count = stats["rating_count"]
        avg = stats["total_score"] / count if count > 0 else 0
        board.append(
            {
                "id": m["id"],
                "name": m["name"],
                "avatar": m["avatar"],
                "avg_score": round(avg, 2),
                "rating_count": count,
            }
        )
    # 按平均分从高到低排序
    board.sort(key=lambda x: x["avg_score"], reverse=True)
    return board


@app.route("/")
def index():
    board = build_board_data()
    return render_template("index.html", members=members, board=board)


@app.route("/rate", methods=["POST"])
def rate():
    data = request.get_json() or {}
    try:
        rater_id = int(data.get("rater_id", 0))
        target_id = int(data.get("target_id", 0))
        score = int(data.get("score", 0))
    except ValueError:
        return jsonify({"error": "参数格式错误"}), 400

    comment = (data.get("comment") or "").strip()

    if rater_id not in [m["id"] for m in members]:
        return jsonify({"error": "请选择你是谁"}), 400
    if target_id not in [m["id"] for m in members]:
        return jsonify({"error": "请选择要评价的人"}), 400
    if rater_id == target_id:
        return jsonify({"error": "不能给自己打分噢"}), 400
    if score < 1 or score > 5:
        return jsonify({"error": "评分必须在 1 到 5 之间"}), 400

    ratings.append(
        {
            "rater_id": rater_id,
            "target_id": target_id,
            "score": score,
            "comment": comment,
        }
    )

    member_stats[target_id]["total_score"] += score
    member_stats[target_id]["rating_count"] += 1

    return jsonify({"ok": True})


@app.route("/upload-avatar", methods=["POST"])
def upload_avatar():
    member_id = request.form.get("member_id")
    file = request.files.get("avatar")

    # 简单校验
    try:
        member_id = int(member_id)
    except (TypeError, ValueError):
        return redirect(url_for("index"))

    member = get_member(member_id)
    if not member:
        return redirect(url_for("index"))

    if not file or file.filename == "":
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    new_name = f"{uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, new_name)
    file.save(save_path)

    # 设置该成员的头像 URL
    member["avatar"] = f"/static/avatars/{new_name}"

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
