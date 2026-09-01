"""
Traceviz backend.

Phase 1 (this file): lessons, curated problems, sandboxed test running,
progressive hints, solution reveal, attempt logging, revision scheduling,
progress dashboard. Phase 2's trace endpoint lives in execution/tracer.py
and is wired in below. AST hints / complexity / stress testing (Phase 4)
are in logic/analysis.py.
"""
import json

from flask import Flask, jsonify, request
from flask_cors import CORS

from db.init_db import get_connection, ensure_db
from execution.sandbox import run_code
from execution.test_runner import run_against_tests, _extract_function_name
from execution.tracer import trace_code
from logic.revision import compute_next_schedule
from logic.analysis import estimate_complexity, generate_hint_from_code
from logic.curriculum_graph import all_prerequisite_blocks

_LESSON_STATUSES = {"not_started", "in_progress", "completed", "skipped", "known"}
_DONE_STATUSES = {"completed", "skipped", "known"}  # "no longer pending" for resume/recommended-next purposes

app = Flask(__name__)
CORS(app)


def row_to_dict(row):
    return dict(row) if row else None


# ---------------------------------------------------------------- health --

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# -------------------------------------------------------------- lessons --

@app.route("/api/lessons", methods=["GET"])
def list_lessons():
    conn = get_connection()
    rows = conn.execute(
        """SELECT l.day, l.title, l.block, l.estimated_minutes,
                  COALESCE(lp.status, 'not_started') AS status
           FROM lessons l LEFT JOIN lesson_progress lp ON lp.day = l.day
           ORDER BY l.day"""
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/lessons/<int:day>", methods=["GET"])
def get_lesson(day):
    conn = get_connection()
    lesson = conn.execute(
        """SELECT l.*, COALESCE(lp.status, 'not_started') AS status,
                  lp.started_at, lp.completed_at
           FROM lessons l LEFT JOIN lesson_progress lp ON lp.day = l.day
           WHERE l.day = ?""", (day,)
    ).fetchone()
    if lesson is None:
        conn.close()
        return jsonify({"error": f"No lesson found for day {day}"}), 404
    problems = conn.execute(
        "SELECT slug, title, difficulty, topic FROM problems WHERE day = ?", (day,)
    ).fetchall()
    result = dict(lesson)
    result["problems"] = [dict(p) for p in problems]

    # Recommended prerequisites -- informational only, never blocking (see
    # logic/curriculum_graph.py). Each entry reports how much of that
    # prerequisite block is already done, so the UI can show e.g.
    # "Arrays, Strings, Hashing: 7/9 done" without gating access.
    prereq_blocks = all_prerequisite_blocks(lesson["block"])
    prerequisites = []
    for block in prereq_blocks:
        block_days = conn.execute(
            """SELECT COUNT(*) total,
                      SUM(CASE WHEN lp.status IN ('completed','skipped','known') THEN 1 ELSE 0 END) done
               FROM lessons l LEFT JOIN lesson_progress lp ON lp.day = l.day
               WHERE l.block = ?""", (block,)
        ).fetchone()
        prerequisites.append({
            "block": block,
            "days_done": block_days["done"] or 0,
            "days_total": block_days["total"],
            "satisfied": (block_days["done"] or 0) == block_days["total"],
        })
    result["recommended_prerequisites"] = prerequisites
    conn.close()
    return jsonify(result)


@app.route("/api/lessons/<int:day>/progress", methods=["PUT"])
def set_lesson_progress(day):
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    if status not in _LESSON_STATUSES:
        return jsonify({"error": f"status must be one of {sorted(_LESSON_STATUSES)}"}), 400

    conn = get_connection()
    lesson = conn.execute("SELECT day FROM lessons WHERE day = ?", (day,)).fetchone()
    if lesson is None:
        conn.close()
        return jsonify({"error": f"No lesson found for day {day}"}), 404

    existing = conn.execute("SELECT * FROM lesson_progress WHERE day = ?", (day,)).fetchone()
    now = __import__("datetime").datetime.utcnow().isoformat()
    started_at = existing["started_at"] if existing else None
    completed_at = existing["completed_at"] if existing else None
    if status in ("in_progress",) and not started_at:
        started_at = now
    if status in _DONE_STATUSES:
        completed_at = now
    if status == "not_started":
        started_at, completed_at = None, None

    if existing:
        conn.execute(
            "UPDATE lesson_progress SET status=?, started_at=?, completed_at=?, updated_at=? WHERE day=?",
            (status, started_at, completed_at, now, day),
        )
    else:
        conn.execute(
            "INSERT INTO lesson_progress (day, status, started_at, completed_at, updated_at) VALUES (?,?,?,?,?)",
            (day, status, started_at, completed_at, now),
        )
    conn.commit()
    conn.close()
    return jsonify({"day": day, "status": status, "started_at": started_at, "completed_at": completed_at})


# ------------------------------------------------------------- problems --

_PROBLEM_LIST_FIELDS = (
    "id, slug, title, day, topic, pattern, difficulty, "
    "interview_priority, estimated_solve_minutes, progression_stage, path_tier"
)
_PROBLEM_DETAIL_FIELDS = (
    "id, slug, title, day, topic, pattern, difficulty, description_markdown, "
    "constraints_markdown, function_signature, starter_code, "
    "expected_time_complexity, expected_space_complexity, edge_cases, comparison_mode, "
    "interview_priority, estimated_solve_minutes, progression_stage, canonical_reference, path_tier"
)


@app.route("/api/problems", methods=["GET"])
def list_problems():
    day = request.args.get("day")
    topic = request.args.get("topic")
    path_tier = request.args.get("path_tier")  # 'core' | 'extended' | 'advanced'
    conn = get_connection()
    query = f"SELECT {_PROBLEM_LIST_FIELDS} FROM problems WHERE 1=1"
    params = []
    if day:
        query += " AND day = ?"
        params.append(day)
    if topic:
        query += " AND topic = ?"
        params.append(topic)
    if path_tier:
        query += " AND path_tier = ?"
        params.append(path_tier)
    query += " ORDER BY CASE path_tier WHEN 'core' THEN 0 WHEN 'extended' THEN 1 ELSE 2 END, day, id"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


def _get_problem_or_404(conn, slug, fields):
    row = conn.execute(f"SELECT {fields} FROM problems WHERE slug = ?", (slug,)).fetchone()
    return row


@app.route("/api/problems/<slug>", methods=["GET"])
def get_problem(slug):
    conn = get_connection()
    problem = _get_problem_or_404(conn, slug, _PROBLEM_DETAIL_FIELDS)
    if problem is None:
        conn.close()
        return jsonify({"error": f"No problem '{slug}'"}), 404
    result = dict(problem)
    # visible test cases only (none are marked hidden in the seed set, but
    # the mechanism exists for future expansion per problem-roadmap.md)
    visible = conn.execute(
        "SELECT input_args_json, expected_output_json, label FROM test_cases "
        "WHERE problem_id = ? AND is_hidden = 0 ORDER BY id", (problem["id"],)
    ).fetchall()
    conn.close()
    result["visible_test_cases"] = [
        {"args": json.loads(t["input_args_json"]), "expected": json.loads(t["expected_output_json"])}
        for t in visible
    ]
    return jsonify(result)


@app.route("/api/problems/<slug>/hints/<int:rung>", methods=["GET"])
def get_hint(slug, rung):
    if rung not in (1, 2, 3):
        return jsonify({"error": "rung must be 1, 2, or 3"}), 400
    conn = get_connection()
    problem = conn.execute("SELECT id FROM problems WHERE slug = ?", (slug,)).fetchone()
    if problem is None:
        conn.close()
        return jsonify({"error": f"No problem '{slug}'"}), 404
    hint = conn.execute(
        "SELECT content_markdown FROM hints WHERE problem_id = ? AND rung = ?",
        (problem["id"], rung),
    ).fetchone()
    conn.close()
    if hint is None:
        return jsonify({"error": f"No rung {rung} hint for '{slug}'"}), 404
    return jsonify({"rung": rung, "content": hint["content_markdown"]})


@app.route("/api/problems/<slug>/hint-from-code", methods=["POST"])
def hint_from_code(slug):
    """Phase 4: an AST-derived hint 2 tailored to the learner's own
    submitted attempt, layered on top of the static rung-2 hint."""
    payload = request.get_json(silent=True) or {}
    code = payload.get("code", "")
    conn = get_connection()
    problem = conn.execute("SELECT * FROM problems WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    if problem is None:
        return jsonify({"error": f"No problem '{slug}'"}), 404
    hint = generate_hint_from_code(code, dict(problem))
    return jsonify({"hint": hint})


@app.route("/api/problems/<slug>/solution", methods=["GET"])
def get_solution(slug):
    conn = get_connection()
    problem = conn.execute(
        "SELECT brute_force_reference, optimal_approach, brute_force_approach FROM problems WHERE slug = ?",
        (slug,),
    ).fetchone()
    conn.close()
    if problem is None:
        return jsonify({"error": f"No problem '{slug}'"}), 404
    return jsonify({
        "solution_code": problem["brute_force_reference"],
        "optimal_approach": problem["optimal_approach"],
        "brute_force_approach": problem["brute_force_approach"],
    })


@app.route("/api/problems/<slug>/run", methods=["POST"])
def run_problem(slug):
    payload = request.get_json(silent=True) or {}
    code = payload.get("code", "")
    if not code.strip():
        return jsonify({"error": "code is required"}), 400

    conn = get_connection()
    problem = conn.execute("SELECT * FROM problems WHERE slug = ?", (slug,)).fetchone()
    if problem is None:
        conn.close()
        return jsonify({"error": f"No problem '{slug}'"}), 404
    # ORDER BY id matters here beyond simple determinism: the failure-
    # analysis UI (ProblemWorkspace's "inspect in trace" jump) relies on a
    # failing result's index lining up with the SAME position in
    # visible_test_cases (get_problem, same ORDER BY) so it can open the
    # Trace tab against the exact case that failed. Since no test case in
    # the current bank is marked hidden (see get_problem's comment), this
    # index is presently 1:1 with the visible list; is_hidden is not
    # filtered here because ungraded submissions must still be checked
    # against every test case, visible or not.
    test_case_rows = conn.execute(
        "SELECT input_args_json, expected_output_json FROM test_cases WHERE problem_id = ? ORDER BY id",
        (problem["id"],),
    ).fetchall()
    conn.close()

    test_cases = [
        {"args": json.loads(t["input_args_json"]), "expected": json.loads(t["expected_output_json"])}
        for t in test_case_rows
    ]
    outcome = run_against_tests(code, problem["function_signature"], test_cases, problem["comparison_mode"])
    all_passed = (not outcome["crashed"]) and all(r["passed"] for r in outcome["results"]) and len(outcome["results"]) > 0
    outcome["all_passed"] = all_passed
    return jsonify(outcome)


@app.route("/api/problems/<slug>/run-custom", methods=["POST"])
def run_custom(slug):
    """Custom test-case playground: run the learner's code against ONE
    input THEY provide, rather than the problem's seeded test cases. This
    is deliberately ungraded (there's no "expected" to compare against --
    the learner is exploring, not being scored) so it reuses the exact
    same sandboxed grading harness as /run with expected=None; the caller
    ignores the resulting "passed" field and just shows the actual output
    or error. Kept as a thin variant of run_problem rather than new
    sandbox code, so it inherits the same timeout/crash handling for free.
    """
    payload = request.get_json(silent=True) or {}
    code = payload.get("code", "")
    args = payload.get("args")
    if not code.strip():
        return jsonify({"error": "code is required"}), 400
    if not isinstance(args, list):
        return jsonify({"error": "args must be a JSON array matching the function's parameters"}), 400

    conn = get_connection()
    problem = conn.execute("SELECT * FROM problems WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    if problem is None:
        return jsonify({"error": f"No problem '{slug}'"}), 404

    outcome = run_against_tests(code, problem["function_signature"], [{"args": args, "expected": None}], "exact")
    if outcome["crashed"] or not outcome["results"]:
        return jsonify({"crashed": True, "error": None, "actual": None,
                         "stdout": outcome["stdout"], "stderr": outcome["stderr"]})
    r = outcome["results"][0]
    return jsonify({"crashed": False, "actual": r["actual"], "error": r["error"],
                     "stdout": outcome["stdout"], "stderr": outcome["stderr"]})


# --------------------------------------------------------------- attempts --

@app.route("/api/problems/<slug>/attempts", methods=["GET"])
def get_attempts(slug):
    """Attempt history / solution journey for one problem: every logged
    submission in order, so the learner can revisit how they actually got
    from first try to Accepted (or see they're stuck repeating the same
    mistake). Reuses the attempts table that log_attempt already writes to
    -- no new tracking, just a read view of data collected all along."""
    conn = get_connection()
    problem = conn.execute("SELECT id FROM problems WHERE slug = ?", (slug,)).fetchone()
    if problem is None:
        conn.close()
        return jsonify({"error": f"No problem '{slug}'"}), 404
    rows = conn.execute(
        """SELECT id, submitted_code, passed, hints_used, max_hint_rung_seen,
                  solution_revealed, is_independent, time_taken_seconds, created_at
           FROM attempts WHERE problem_id = ? ORDER BY id""",
        (problem["id"],),
    ).fetchall()
    conn.close()
    return jsonify({"attempts": [dict(r) for r in rows]})

@app.route("/api/attempts", methods=["POST"])
def log_attempt():
    payload = request.get_json(silent=True) or {}
    slug = payload.get("slug")
    submitted_code = payload.get("submitted_code", "")
    passed = bool(payload.get("passed", False))
    hints_used = int(payload.get("hints_used", 0))
    max_hint_rung_seen = int(payload.get("max_hint_rung_seen", 0))
    solution_revealed = bool(payload.get("solution_revealed", False))
    time_taken_seconds = payload.get("time_taken_seconds")

    is_independent = passed and hints_used == 0 and not solution_revealed

    conn = get_connection()
    problem = conn.execute("SELECT id, topic FROM problems WHERE slug = ?", (slug,)).fetchone()
    if problem is None:
        conn.close()
        return jsonify({"error": f"No problem '{slug}'"}), 404

    cur = conn.execute(
        """INSERT INTO attempts
           (problem_id, submitted_code, passed, hints_used, max_hint_rung_seen,
            solution_revealed, is_independent, time_taken_seconds)
           VALUES (?,?,?,?,?,?,?,?)""",
        (problem["id"], submitted_code, int(passed), hints_used, max_hint_rung_seen,
         int(solution_revealed), int(is_independent), time_taken_seconds),
    )
    attempt_id = cur.lastrowid

    # Revision scheduling
    existing = conn.execute(
        "SELECT interval_index FROM revision_schedule WHERE problem_id = ?", (problem["id"],)
    ).fetchone()
    current_index = existing["interval_index"] if existing else -1  # -1 so first pass -> index 0
    new_index, next_due, result_label = compute_next_schedule(passed, is_independent, max(current_index, 0))
    if existing:
        conn.execute(
            "UPDATE revision_schedule SET last_attempt_id=?, next_due_date=?, interval_index=?, last_result=? WHERE problem_id=?",
            (attempt_id, next_due, new_index, result_label, problem["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO revision_schedule (problem_id, last_attempt_id, next_due_date, interval_index, last_result) VALUES (?,?,?,?,?)",
            (problem["id"], attempt_id, next_due, new_index, result_label),
        )

    conn.commit()
    conn.close()
    return jsonify({"attempt_id": attempt_id, "is_independent": is_independent,
                     "next_due_date": next_due, "result": result_label})


# --------------------------------------------------------------- progress --

@app.route("/api/progress", methods=["GET"])
def progress():
    conn = get_connection()

    total_attempted = conn.execute(
        "SELECT COUNT(DISTINCT problem_id) c FROM attempts"
    ).fetchone()["c"]
    total_solved = conn.execute(
        "SELECT COUNT(DISTINCT problem_id) c FROM attempts WHERE passed = 1"
    ).fetchone()["c"]
    independent_solves = conn.execute(
        "SELECT COUNT(*) c FROM attempts WHERE is_independent = 1"
    ).fetchone()["c"]
    total_passed_attempts = conn.execute(
        "SELECT COUNT(*) c FROM attempts WHERE passed = 1"
    ).fetchone()["c"]
    independent_rate = (independent_solves / total_passed_attempts) if total_passed_attempts else None

    avg_time = conn.execute(
        "SELECT AVG(time_taken_seconds) a FROM attempts WHERE passed = 1 AND time_taken_seconds IS NOT NULL"
    ).fetchone()["a"]
    total_hints = conn.execute("SELECT SUM(hints_used) s FROM attempts").fetchone()["s"] or 0
    total_attempts_count = conn.execute("SELECT COUNT(*) c FROM attempts").fetchone()["c"]
    hint_usage_rate = (total_hints / total_attempts_count) if total_attempts_count else None

    weak_topics = conn.execute(
        """SELECT p.topic, COUNT(*) mistake_count
           FROM attempts a JOIN problems p ON a.problem_id = p.id
           WHERE a.passed = 0 OR a.hints_used > 0
           GROUP BY p.topic ORDER BY mistake_count DESC LIMIT 5"""
    ).fetchall()
    strong_topics = conn.execute(
        """SELECT p.topic, COUNT(*) independent_count
           FROM attempts a JOIN problems p ON a.problem_id = p.id
           WHERE a.is_independent = 1
           GROUP BY p.topic ORDER BY independent_count DESC LIMIT 5"""
    ).fetchall()
    mastered_topics = conn.execute(
        """SELECT p.topic, COUNT(*) c
           FROM attempts a JOIN problems p ON a.problem_id = p.id
           WHERE a.is_independent = 1
           GROUP BY p.topic HAVING COUNT(*) >= 2"""
    ).fetchall()

    today = __import__("datetime").date.today().isoformat()
    revision_due = conn.execute(
        """SELECT p.slug, p.title, p.topic, rs.next_due_date, rs.last_result
           FROM revision_schedule rs JOIN problems p ON rs.problem_id = p.id
           WHERE rs.next_due_date <= ? ORDER BY rs.next_due_date""",
        (today,),
    ).fetchall()

    # simple daily streak: count consecutive days (from today backward)
    # with at least one attempt logged
    streak_rows = conn.execute(
        "SELECT DISTINCT date(created_at) d FROM attempts ORDER BY d DESC"
    ).fetchall()
    streak = 0
    if streak_rows:
        import datetime as _dt
        expected = _dt.date.today()
        dates = {_dt.date.fromisoformat(r["d"]) for r in streak_rows}
        while expected in dates:
            streak += 1
            expected -= _dt.timedelta(days=1)

    # ---- Core 45-Day Path completion, separate from extended/advanced ----
    # Surfaced so the dashboard/UI can clearly communicate that finishing
    # the Core Path (Easy/Medium, required) is "job-ready", while Extended
    # and Advanced (Hard) problems are optional add-ons that never gate
    # that message -- see docs/problem-roadmap.md.
    tier_counts = conn.execute(
        """SELECT p.path_tier, COUNT(*) total,
                  SUM(CASE WHEN EXISTS (
                      SELECT 1 FROM attempts a WHERE a.problem_id = p.id AND a.passed = 1
                  ) THEN 1 ELSE 0 END) solved
           FROM problems p GROUP BY p.path_tier"""
    ).fetchall()
    path_tier_progress = {
        row["path_tier"]: {"total": row["total"], "solved": row["solved"] or 0}
        for row in tier_counts
    }
    for tier in ("core", "extended", "advanced"):
        path_tier_progress.setdefault(tier, {"total": 0, "solved": 0})

    # ---- lesson navigation: recommended next / resume / status counts ----
    lesson_rows = conn.execute(
        """SELECT l.day, l.title, l.block, COALESCE(lp.status, 'not_started') AS status, lp.updated_at
           FROM lessons l LEFT JOIN lesson_progress lp ON lp.day = l.day
           ORDER BY l.day"""
    ).fetchall()

    status_counts = {"not_started": 0, "in_progress": 0, "completed": 0, "skipped": 0, "known": 0}
    for r in lesson_rows:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1

    recommended_next = next((dict(r) for r in lesson_rows if r["status"] == "not_started"), None)
    in_progress_rows = [r for r in lesson_rows if r["status"] == "in_progress"]
    resume = None
    if in_progress_rows:
        resume = dict(max(in_progress_rows, key=lambda r: r["updated_at"] or ""))

    conn.close()
    return jsonify({
        "total_problems_attempted": total_attempted,
        "total_problems_solved": total_solved,
        "independent_solves": independent_solves,
        "independent_solve_rate": independent_rate,
        "current_streak_days": streak,
        "top_weaknesses": [dict(r) for r in weak_topics],
        "top_strengths": [dict(r) for r in strong_topics],
        "topics_mastered": [r["topic"] for r in mastered_topics],
        "problems_due_for_revision": [dict(r) for r in revision_due],
        "average_solve_time_seconds": avg_time,
        "hint_usage_rate": hint_usage_rate,
        "path_tier_progress": path_tier_progress,
        "lesson_status_counts": status_counts,
        "recommended_next_lesson": recommended_next,
        "resume_lesson": resume,
        "lessons_overview": [
            {"day": r["day"], "title": r["title"], "block": r["block"], "status": r["status"]}
            for r in lesson_rows
        ],
    })


# ----------------------------------------------------------- complexity --

@app.route("/api/problems/<slug>/complexity-estimate", methods=["POST"])
def complexity_estimate(slug):
    payload = request.get_json(silent=True) or {}
    code = payload.get("code", "")
    conn = get_connection()
    problem = conn.execute("SELECT id, function_signature FROM problems WHERE slug = ?", (slug,)).fetchone()
    if problem is None:
        conn.close()
        return jsonify({"error": f"No problem '{slug}'"}), 404
    test_case_rows = conn.execute(
        "SELECT input_args_json, expected_output_json FROM test_cases WHERE problem_id = ?",
        (problem["id"],),
    ).fetchall()
    conn.close()
    test_cases = [
        {"args": json.loads(t["input_args_json"]), "expected": json.loads(t["expected_output_json"])}
        for t in test_case_rows
    ]
    result = estimate_complexity(code, problem["function_signature"], test_cases)
    return jsonify(result)


# --------------------------------------------------------- plain run/trace --

@app.route("/api/run", methods=["POST"])
def run():
    payload = request.get_json(silent=True) or {}
    code = payload.get("code", "")
    if not isinstance(code, str) or not code.strip():
        return jsonify({"error": "Request body must include non-empty 'code'"}), 400
    result = run_code(code)
    return jsonify(result)


@app.route("/api/trace", methods=["POST"])
def trace():
    payload = request.get_json(silent=True) or {}
    code = payload.get("code", "")
    if not isinstance(code, str) or not code.strip():
        return jsonify({"error": "Request body must include non-empty 'code'"}), 400
    result = trace_code(code)
    return jsonify(result)


@app.route("/api/problems/<slug>/trace", methods=["POST"])
def trace_problem(slug):
    """Like /api/trace, but for a problem-workspace submission specifically:
    the learner's code is normally JUST a function definition (that's what
    starter_code gives them), so tracing it raw would only ever show the
    `def` statement itself -- the function body never runs because nothing
    calls it. This appends an actual call to the learner's function using
    one of the problem's own visible test cases (selectable by index), so
    "Trace my code" is useful out of the box without the learner having to
    hand-write their own driver/print statement first."""
    payload = request.get_json(silent=True) or {}
    code = payload.get("code", "")
    test_case_index = payload.get("test_case_index", 0)
    # Custom test-case playground: lets the trace be driven by args the
    # learner typed themselves instead of one of the problem's seeded
    # cases -- "Enter test input -> Run -> Trace -> Inspect" needs this to
    # reach the Trace step for input that was never one of the stored
    # examples. When present, this takes priority over test_case_index.
    custom_args = payload.get("custom_args")
    if not isinstance(code, str) or not code.strip():
        return jsonify({"error": "Request body must include non-empty 'code'"}), 400

    conn = get_connection()
    problem = conn.execute(
        "SELECT id, function_signature FROM problems WHERE slug = ?", (slug,)
    ).fetchone()
    if problem is None:
        conn.close()
        return jsonify({"error": f"No problem '{slug}'"}), 404
    try:
        fn_name = _extract_function_name(problem["function_signature"])
    except ValueError as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

    if isinstance(custom_args, list):
        conn.close()
        args = custom_args
        idx = None
        test_case_count = None
    else:
        test_case_rows = conn.execute(
            "SELECT input_args_json FROM test_cases WHERE problem_id = ? AND is_hidden = 0 ORDER BY id",
            (problem["id"],),
        ).fetchall()
        conn.close()
        if not test_case_rows:
            return jsonify({"error": "This problem has no visible test cases to trace against"}), 400
        idx = test_case_index if isinstance(test_case_index, int) and 0 <= test_case_index < len(test_case_rows) else 0
        args = json.loads(test_case_rows[idx]["input_args_json"])
        test_case_count = len(test_case_rows)

    # repr(), not json.dumps(): JSON's true/false/null aren't valid Python
    # syntax -- the exact same class of bug the grading harness already
    # hit once and fixed the same way (see test_runner.py).
    augmented_code = code.rstrip() + f"\n\n{fn_name}(*{args!r})\n"

    result = trace_code(augmented_code)
    result["traced_test_case_index"] = idx
    result["traced_test_case_args"] = args
    result["traced_test_case_count"] = test_case_count
    result["traced_custom"] = isinstance(custom_args, list)
    return jsonify(result)


if __name__ == "__main__":
    ensure_db()  # only creates+seeds if traceviz.db doesn't exist yet -- never wipes progress on restart
    app.run(debug=True, port=5001)
