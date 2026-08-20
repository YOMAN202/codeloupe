"""
Traceviz backend -- Milestone 1.

Scope: serve lesson content from SQLite, and run submitted code through the
sandbox. Deliberately does NOT include: trace recording, AST-based hints,
stress testing, complexity estimation, or progress tracking -- those are
Milestone 2+ (see docs/development-roadmap.md). Keeping this file small on
purpose so Milestone 1's "stop and test" checkpoint is easy to verify.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS

from db.init_db import get_connection, init_db
from execution.sandbox import run_code

app = Flask(__name__)
CORS(app)  # local dev only: frontend (Vite) and backend run on different ports


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/lessons/<int:day>", methods=["GET"])
def get_lesson(day):
    conn = get_connection()
    row = conn.execute(
        "SELECT day, title, concept_markdown FROM lessons WHERE day = ?", (day,)
    ).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": f"No lesson found for day {day}"}), 404
    return jsonify(dict(row))


@app.route("/api/run", methods=["POST"])
def run():
    payload = request.get_json(silent=True) or {}
    code = payload.get("code", "")
    if not isinstance(code, str) or not code.strip():
        return jsonify({"error": "Request body must include non-empty 'code'"}), 400
    result = run_code(code)
    return jsonify(result)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)
