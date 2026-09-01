"""
Codeloupe backend.

All API routes live in this one file: lessons (day-based curriculum),
concept lessons (the teaching system, see db/schema.sql's concept_lessons
comment), curated problems, sandboxed test running, progressive hints,
solution reveal, attempt logging, revision scheduling, the mistake
journal, pattern-level revision, adaptive practice sessions, approach
comparison, and the trace endpoint. Supporting logic is split out by
concern: execution/ (sandbox, test runner, tracer), logic/ (mistakes,
pattern families, curriculum graph, revision scheduling, practice
sessions, approach comparison, AST/complexity analysis). See
docs/architecture.md for the full picture.
"""
import json
import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from db.init_db import get_connection, ensure_db
from execution.sandbox import run_code
from execution.test_runner import run_against_tests, _extract_function_name
from execution.tracer import trace_code
from logic.revision import compute_next_schedule
from logic.analysis import estimate_complexity, generate_hint_from_code
from logic.curriculum_graph import all_prerequisite_blocks
from logic.mistakes import classify_mistake, MISTAKE_CATEGORIES, CONFIDENCE_LEVELS
from logic.pattern_families import pattern_family_for, concept_lesson_for_family
from logic.practice_session import build_practice_session
from logic.approach_comparison import compare_candidate

_LESSON_STATUSES = {"not_started", "in_progress", "completed", "skipped", "known"}
_DONE_STATUSES = {"completed", "skipped", "known"}  # "no longer pending" for resume/recommended-next purposes

app = Flask(__name__)
CORS(app)


def row_to_dict(row):
    return dict(row) if row else None


# ---------------------------------------------------------- concept links --
# Shared by the lessons/problems endpoints below (to surface "concepts you
# should know" inline) and by the /api/concepts endpoints further down.
# See db/schema.sql's concept_lessons comment: the link is a computed
# topic-string match, not a join table, so it never goes stale as new
# problems/days/concept lessons are added.

def _related_concept_lessons(conn, topics):
    topics = [t for t in dict.fromkeys(topics) if t]  # dedupe, preserve order, drop falsy
    if not topics:
        return []
    placeholders = ",".join("?" * len(topics))
    rows = conn.execute(
        f"""SELECT cl.slug, cl.kind, cl.title, cl.summary,
                   COALESCE(clp.status, 'not_started') AS status
            FROM concept_lessons cl LEFT JOIN concept_lesson_progress clp ON clp.concept_lesson_id = cl.id
            WHERE cl.topic IN ({placeholders})
            ORDER BY cl.topic, CASE cl.kind WHEN 'topic' THEN 0 ELSE 1 END, cl.display_order""",
        topics,
    ).fetchall()
    return [dict(r) for r in rows]


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
    # "concepts you should know" for this day, derived from its problems'
    # topics -- empty for most days until the teaching system's content
    # expands past the arrays/two-pointers pilot (see db/seed_concepts.py).
    result["concept_lessons"] = _related_concept_lessons(conn, [p["topic"] for p in problems])
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
    "interview_priority, estimated_solve_minutes, progression_stage, canonical_reference, path_tier, "
    "(brute_force_reference IS NOT NULL) AS has_approach_baseline"
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
    result["concept_lessons"] = _related_concept_lessons(conn, [problem["topic"]])
    conn.close()
    result["visible_test_cases"] = [
        {"args": json.loads(t["input_args_json"]), "expected": json.loads(t["expected_output_json"])}
        for t in visible
    ]
    return jsonify(result)


# ------------------------------------------------------------- concepts --
# Teaching-system concept lessons: topic overviews ('arrays') and pattern
# deep-dives ('two-pointers') that teach the "what/why/when should I use
# this" a curated problem never had room for. See db/schema.sql's
# concept_lessons comment and db/seed_concepts.py's module docstring for
# the content-architecture reasoning; this is a pilot covering the
# curriculum's own first topic + pattern (days 8/13/14), not the full
# curriculum yet.

_CONCEPT_LIST_FIELDS = "cl.slug, cl.kind, cl.topic, cl.pattern_family, cl.title, cl.display_order, cl.estimated_minutes, cl.summary"


def _resolve_concept_prereqs(conn, prerequisite_slugs):
    slugs = [s.strip() for s in (prerequisite_slugs or "").split(",") if s.strip()]
    if not slugs:
        return []
    placeholders = ",".join("?" * len(slugs))
    rows = conn.execute(
        f"""SELECT cl.slug, cl.title, COALESCE(clp.status, 'not_started') AS status
            FROM concept_lessons cl LEFT JOIN concept_lesson_progress clp ON clp.concept_lesson_id = cl.id
            WHERE cl.slug IN ({placeholders})""",
        slugs,
    ).fetchall()
    order = {s: i for i, s in enumerate(slugs)}
    return sorted([dict(r) for r in rows], key=lambda r: order.get(r["slug"], len(slugs)))


def _related_problems_for_concept(conn, concept):
    """Problems this concept lesson applies to -- topic match, narrowed to
    a specific pattern family when the lesson targets one (most
    'pattern'-kind lessons will; both pilot lessons happen to leave
    pattern_family NULL and cover a whole topic instead, per
    seed_concepts.py). Core-tier problems sort first so a learner coming
    from a lesson sees the curriculum's own curated entry point before
    the extended/advanced pool."""
    rows = conn.execute(
        """SELECT slug, title, difficulty, pattern, path_tier, day FROM problems
           WHERE topic = ?
           ORDER BY CASE path_tier WHEN 'core' THEN 0 WHEN 'extended' THEN 1 ELSE 2 END, day, id""",
        (concept["topic"],),
    ).fetchall()
    result = [dict(r) for r in rows]
    if concept["pattern_family"]:
        result = [r for r in result if pattern_family_for(concept["topic"], r["pattern"]) == concept["pattern_family"]]
    return result[:12]


@app.route("/api/concepts", methods=["GET"])
def list_concepts():
    conn = get_connection()
    rows = conn.execute(
        f"""SELECT {_CONCEPT_LIST_FIELDS}, COALESCE(clp.status, 'not_started') AS status
            FROM concept_lessons cl LEFT JOIN concept_lesson_progress clp ON clp.concept_lesson_id = cl.id
            ORDER BY cl.topic, CASE cl.kind WHEN 'topic' THEN 0 ELSE 1 END, cl.display_order"""
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/concepts/<slug>", methods=["GET"])
def get_concept(slug):
    conn = get_connection()
    concept = conn.execute(
        """SELECT cl.*, COALESCE(clp.status, 'not_started') AS status
           FROM concept_lessons cl LEFT JOIN concept_lesson_progress clp ON clp.concept_lesson_id = cl.id
           WHERE cl.slug = ?""", (slug,)
    ).fetchone()
    if concept is None:
        conn.close()
        return jsonify({"error": f"No concept lesson '{slug}'"}), 404

    result = dict(concept)
    result["walkthrough_frames"] = (
        json.loads(concept["walkthrough_frames_json"]) if concept["walkthrough_frames_json"] else []
    )
    del result["walkthrough_frames_json"]

    checkpoint_rows = conn.execute(
        """SELECT id, kind, prompt_markdown, code, choices_json, correct_answer, explanation_markdown
           FROM concept_checkpoints WHERE concept_lesson_id = ? ORDER BY display_order""",
        (concept["id"],),
    ).fetchall()
    checkpoints = []
    for chk in checkpoint_rows:
        d = dict(chk)
        d["choices"] = json.loads(d["choices_json"]) if d["choices_json"] else None
        del d["choices_json"]
        checkpoints.append(d)
    result["checkpoints"] = checkpoints

    exercise_rows = conn.execute(
        """SELECT id, prompt_markdown, starter_code, solution_code, hint_markdown
           FROM concept_practice_exercises WHERE concept_lesson_id = ? ORDER BY display_order""",
        (concept["id"],),
    ).fetchall()
    result["practice_exercises"] = [dict(e) for e in exercise_rows]

    result["prerequisites"] = _resolve_concept_prereqs(conn, concept["prerequisite_slugs"])
    result["related_problems"] = _related_problems_for_concept(conn, concept)
    conn.close()
    return jsonify(result)


@app.route("/api/concepts/<slug>/progress", methods=["PUT"])
def set_concept_progress(slug):
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    valid_statuses = {"not_started", "in_progress", "completed", "known"}
    if status not in valid_statuses:
        return jsonify({"error": f"status must be one of {sorted(valid_statuses)}"}), 400

    conn = get_connection()
    concept = conn.execute("SELECT id FROM concept_lessons WHERE slug = ?", (slug,)).fetchone()
    if concept is None:
        conn.close()
        return jsonify({"error": f"No concept lesson '{slug}'"}), 404

    now = __import__("datetime").datetime.utcnow().isoformat()
    existing = conn.execute(
        "SELECT concept_lesson_id FROM concept_lesson_progress WHERE concept_lesson_id = ?", (concept["id"],)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE concept_lesson_progress SET status=?, updated_at=? WHERE concept_lesson_id=?",
            (status, now, concept["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO concept_lesson_progress (concept_lesson_id, status, updated_at) VALUES (?,?,?)",
            (concept["id"], status, now),
        )
    conn.commit()
    conn.close()
    return jsonify({"slug": slug, "status": status})


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
        "SELECT optimal_reference, optimal_approach, brute_force_approach FROM problems WHERE slug = ?",
        (slug,),
    ).fetchone()
    conn.close()
    if problem is None:
        return jsonify({"error": f"No problem '{slug}'"}), 404
    return jsonify({
        "solution_code": problem["optimal_reference"],
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
        """SELECT a.id, a.submitted_code, a.passed, a.hints_used, a.max_hint_rung_seen,
                  a.solution_revealed, a.is_independent, a.time_taken_seconds, a.created_at,
                  m.id AS mistake_id, m.category AS mistake_category, m.confidence AS mistake_confidence,
                  m.evidence AS mistake_evidence
           FROM attempts a LEFT JOIN mistakes m ON m.attempt_id = a.id
           WHERE a.problem_id = ? ORDER BY a.id""",
        (problem["id"],),
    ).fetchall()
    conn.close()

    attempts = []
    for r in rows:
        d = dict(r)
        mistake = None
        if d["mistake_id"] is not None:
            mistake = {"id": d["mistake_id"], "category": d["mistake_category"],
                       "confidence": d["mistake_confidence"], "evidence": d["mistake_evidence"]}
        for k in ("mistake_id", "mistake_category", "mistake_confidence", "mistake_evidence"):
            del d[k]
        d["mistake"] = mistake
        attempts.append(d)
    return jsonify({"attempts": attempts})

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
    # Optional: {"crashed": bool, "first_failure": {...}|None, "num_failed": int,
    # "num_total": int} built by the frontend from the /run response it
    # already has in hand -- see logic/mistakes.py's classify_mistake.
    failure_context = payload.get("failure_context")

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

    # Mistake journal: only for FAILED attempts (a pass isn't a "mistake"
    # in the sense of the fixed category list, even an assisted one --
    # hints_used/solution_revealed already track "needed help" separately
    # on the attempt itself). Always writes a row when there's a failure,
    # even when unclassified, so the journal can honestly show "N failures,
    # M classified, K not yet classified" instead of silently dropping the
    # unclear ones.
    mistake_out = None
    if not passed:
        category, evidence = classify_mistake(failure_context, problem["topic"])
        confidence = "likely_issue" if category else "unclassified"
        mcur = conn.execute(
            "INSERT INTO mistakes (attempt_id, problem_id, category, confidence, evidence) VALUES (?,?,?,?,?)",
            (attempt_id, problem["id"], category, confidence, evidence),
        )
        mistake_out = {"id": mcur.lastrowid, "category": category, "confidence": confidence, "evidence": evidence}

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
                     "next_due_date": next_due, "result": result_label, "mistake": mistake_out})


# ---------------------------------------------------------- mistake journal --

@app.route("/api/mistakes/<int:mistake_id>", methods=["PUT"])
def update_mistake(mistake_id):
    """Lets the learner review a classifier suggestion: confirm it as-is
    (user_confirmed), replace it with their own pick (manually_selected --
    also how an unclassified mistake gets a category at all), or leave it
    alone. Never re-runs the heuristic classifier -- once a human has
    looked at it, the human's answer wins."""
    payload = request.get_json(silent=True) or {}
    category = payload.get("category")
    confirm = bool(payload.get("confirm", False))

    if category is not None and category not in MISTAKE_CATEGORIES:
        return jsonify({"error": f"category must be one of {MISTAKE_CATEGORIES}"}), 400

    conn = get_connection()
    existing = conn.execute("SELECT * FROM mistakes WHERE id = ?", (mistake_id,)).fetchone()
    if existing is None:
        conn.close()
        return jsonify({"error": f"No mistake {mistake_id}"}), 404

    if confirm:
        new_category = existing["category"]
        new_confidence = "user_confirmed"
    elif category is not None:
        new_category = category
        new_confidence = "manually_selected"
    else:
        conn.close()
        return jsonify({"error": "Provide 'confirm': true or a 'category' to set."}), 400

    conn.execute("UPDATE mistakes SET category = ?, confidence = ? WHERE id = ?",
                 (new_category, new_confidence, mistake_id))
    conn.commit()
    conn.close()
    return jsonify({"id": mistake_id, "category": new_category, "confidence": new_confidence})


@app.route("/api/mistakes/journal", methods=["GET"])
def mistake_journal():
    """The mistake journal, across every problem: answers 'what kinds of
    mistakes do I repeatedly make?' with real counts by category and
    confidence, plus the individual entries (each linking back to its
    problem and attempt) so the learner can revisit exactly what happened."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT m.id, m.category, m.confidence, m.evidence, m.created_at,
                  p.slug, p.title, p.topic, p.pattern, a.id AS attempt_id
           FROM mistakes m
           JOIN problems p ON m.problem_id = p.id
           JOIN attempts a ON m.attempt_id = a.id
           ORDER BY m.created_at DESC"""
    ).fetchall()

    entries = []
    category_counts = {}
    unclassified_count = 0
    for r in rows:
        d = dict(r)
        d["pattern_family"] = pattern_family_for(r["topic"], r["pattern"])
        # Recurring-mistake -> lesson: an honest, explainable link back
        # into the teaching system (never a guess -- see
        # concept_lesson_for_family's own docstring), so the journal's
        # "revise" step has somewhere concrete to go instead of leaving
        # the learner to self-navigate the Learn hub.
        d["related_lesson"] = concept_lesson_for_family(conn, r["topic"], d["pattern_family"])
        entries.append(d)
        if r["category"]:
            category_counts[r["category"]] = category_counts.get(r["category"], 0) + 1
        else:
            unclassified_count += 1
    conn.close()

    recurring = sorted(
        ({"category": c, "count": n} for c, n in category_counts.items()),
        key=lambda x: -x["count"],
    )
    return jsonify({
        "entries": entries,
        "total_mistakes": len(entries),
        "unclassified_count": unclassified_count,
        "recurring_categories": recurring,
    })


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

    # ---- pattern-level weakness (enhances, never replaces, the topic-level
    # weak_topics above -- see logic/pattern_families.py) and a recurring-
    # mistakes summary from the mistake journal.
    mistake_join_rows = conn.execute(
        """SELECT p.topic, p.pattern, m.category
           FROM mistakes m JOIN problems p ON m.problem_id = p.id"""
    ).fetchall()
    family_counts, family_categories, category_counts, family_topics = {}, {}, {}, {}
    for r in mistake_join_rows:
        family = pattern_family_for(r["topic"], r["pattern"])
        family_counts[family] = family_counts.get(family, 0) + 1
        family_topics.setdefault(family, r["topic"])
        if r["category"]:
            family_categories.setdefault(family, {})
            family_categories[family][r["category"]] = family_categories[family].get(r["category"], 0) + 1
            category_counts[r["category"]] = category_counts.get(r["category"], 0) + 1
    pattern_weaknesses = [
        {
            "pattern_family": family,
            "mistake_count": count,
            "top_category": max(family_categories[family], key=family_categories[family].get) if family_categories.get(family) else None,
            # Same honest, explainable link as the mistake journal's
            # entries -- omitted (None) rather than guessed when no
            # lesson covers this family yet.
            "related_lesson": concept_lesson_for_family(conn, family_topics.get(family), family),
        }
        for family, count in sorted(family_counts.items(), key=lambda kv: -kv[1])[:5]
    ]
    recurring_mistakes = [
        {"category": cat, "count": n}
        for cat, n in sorted(category_counts.items(), key=lambda kv: -kv[1])[:5]
    ]

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

    # ---- Learn-hub concept lesson status, alongside (never merged into)
    # the 45-day curriculum counts above. These are two genuinely
    # separate tracks -- 45 day-by-day lessons vs. 28 concept lessons
    # covering the same material from a different angle -- so folding one
    # count into the other would misrepresent both. Surfaced as its own
    # field so the dashboard's "lesson progress" isn't blind to Learn-hub
    # activity, without pretending the two are one number.
    concept_lesson_rows = conn.execute(
        """SELECT COALESCE(clp.status, 'not_started') AS status
           FROM concept_lessons cl
           LEFT JOIN concept_lesson_progress clp ON clp.concept_lesson_id = cl.id"""
    ).fetchall()
    concept_status_counts = {"not_started": 0, "in_progress": 0, "completed": 0, "skipped": 0, "known": 0}
    for r in concept_lesson_rows:
        concept_status_counts[r["status"]] = concept_status_counts.get(r["status"], 0) + 1

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
        "pattern_weaknesses": pattern_weaknesses,
        "recurring_mistakes": recurring_mistakes,
        "problems_due_for_revision": [dict(r) for r in revision_due],
        "average_solve_time_seconds": avg_time,
        "hint_usage_rate": hint_usage_rate,
        "path_tier_progress": path_tier_progress,
        "lesson_status_counts": status_counts,
        "concept_lesson_status_counts": concept_status_counts,
        "recommended_next_lesson": recommended_next,
        "resume_lesson": resume,
        "lessons_overview": [
            {"day": r["day"], "title": r["title"], "block": r["block"], "status": r["status"]}
            for r in lesson_rows
        ],
    })


@app.route("/api/practice-session", methods=["GET"])
def practice_session():
    """Adaptive 'Today's Session': see logic/practice_session.py. Purely a
    suggestion list built from data the rest of the app already computes
    (revision_schedule, the mistake journal, topic weakness, plain
    progress) -- never a required path, the learner can ignore it and
    open any problem directly."""
    conn = get_connection()
    items = build_practice_session(conn)
    conn.close()
    return jsonify({"items": items})


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


# ---------------------------------------------------- approach comparison --

@app.route("/api/problems/<slug>/approach-comparison", methods=["POST"])
def approach_comparison(slug):
    """Optional, explicitly-triggered comparison between the learner's own
    code and this problem's reference approach(es). Never run
    automatically -- the frontend only calls this from a deliberate
    "Compare my approach" click, gated (client-side) behind having run at
    least once first, mirroring the honor-system gate already used for
    hint/solution reveal.

    Two-stage reveal, same idea as the Hints tab's solution reveal:
    reveal_code=False (the default) returns every number -- structural
    estimate, empirical timing/memory, growth curve, operation count --
    for every candidate, but never the reference CODE itself. Those
    numbers alone explain *why* one approach is better without handing
    over the algorithm. reveal_code=True additionally returns the actual
    source, which the frontend treats exactly like the existing solution
    reveal (marks the attempt assisted, not independent).

    See logic/approach_comparison.py for what each number actually
    measures and why brute_force_baseline is null for most problems."""
    payload = request.get_json(silent=True) or {}
    code = payload.get("code", "")
    reveal_code = bool(payload.get("reveal_code", False))
    if not code.strip():
        return jsonify({"error": "code is required"}), 400

    conn = get_connection()
    problem = conn.execute(
        "SELECT id, function_signature, optimal_reference, brute_force_reference, "
        "growth_curve_generator, growth_curve_sizes, brute_force_approach, optimal_approach, "
        "expected_time_complexity, expected_space_complexity FROM problems WHERE slug = ?",
        (slug,),
    ).fetchone()
    if problem is None:
        conn.close()
        return jsonify({"error": f"No problem '{slug}'"}), 404
    test_case_rows = conn.execute(
        "SELECT input_args_json, expected_output_json FROM test_cases WHERE problem_id = ? ORDER BY id",
        (problem["id"],),
    ).fetchall()
    conn.close()

    test_cases = [
        {"args": json.loads(t["input_args_json"]), "expected": json.loads(t["expected_output_json"])}
        for t in test_case_rows
    ]
    if not test_cases:
        return jsonify({"error": "This problem has no test cases to benchmark against"}), 400
    sample_args = test_cases[0]["args"]

    has_baseline = problem["brute_force_reference"] is not None
    growth_generator = problem["growth_curve_generator"] if has_baseline else None
    growth_sizes = json.loads(problem["growth_curve_sizes"]) if (has_baseline and problem["growth_curve_sizes"]) else None

    mine = compare_candidate(code, problem["function_signature"], test_cases, sample_args,
                              growth_generator, growth_sizes)

    optimal = compare_candidate(problem["optimal_reference"], problem["function_signature"], test_cases,
                                 sample_args, growth_generator, growth_sizes)
    optimal["narrative"] = problem["optimal_approach"]
    if reveal_code:
        optimal["code"] = problem["optimal_reference"]

    baseline = None
    if has_baseline:
        baseline = compare_candidate(problem["brute_force_reference"], problem["function_signature"], test_cases,
                                      sample_args, growth_generator, growth_sizes)
        baseline["narrative"] = problem["brute_force_approach"]
        if reveal_code:
            baseline["code"] = problem["brute_force_reference"]

    return jsonify({
        "has_baseline": has_baseline,
        "expected_time_complexity": problem["expected_time_complexity"],
        "expected_space_complexity": problem["expected_space_complexity"],
        "my_approach": mine,
        "optimal_reference": optimal,
        "brute_force_baseline": baseline,
    })


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
    # Debug mode (the interactive Werkzeug debugger + auto-reload) is the
    # right default for local development -- exactly what this app is built
    # for -- but its debugger is an unauthenticated remote-code-execution
    # console if this process is ever reachable from outside localhost. Set
    # FLASK_DEBUG=0 before running for anything other than "on my own
    # machine, for myself" (see docs/architecture.md's "Running beyond
    # local dev" section). PORT is likewise overridable for anyone who
    # already has something on 5001.
    debug = os.environ.get("FLASK_DEBUG", "1") not in ("0", "false", "False")
    port = int(os.environ.get("PORT", "5001"))
    app.run(debug=debug, port=port)
