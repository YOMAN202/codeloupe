"""
Initialize (or re-initialize) the SQLite database: schema + full lesson
and problem seed data. Run directly: `python3 db/init_db.py` from
backend/, or it's called automatically on `python3 app.py` startup.

This drops and recreates all tables every run. That's intentional for
now (see docs/decisions.md): there's no real migration system, and the
project is young enough that "reseed from source" is simpler and safer
than hand-writing ALTER TABLE migrations for a single-user tool. If you
have real attempt history you care about, back up traceviz.db before
re-running this after a schema change.
"""
import copy
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(__file__))
from seed_lessons import LESSONS
from seed_problems import PROBLEMS

DB_PATH = os.path.join(os.path.dirname(__file__), "traceviz.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

_TABLES = ["mistakes", "revision_schedule", "attempts", "hints",
           "test_cases", "problems", "lessons"]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _seed_lessons(conn):
    for l in LESSONS:
        conn.execute(
            """INSERT INTO lessons
               (day, title, concept_markdown, block, python_concepts, dsa_concepts,
                why_it_matters, visual_concept, example_code, prediction_question,
                prediction_answer, exercises_markdown, must_explain, common_mistakes,
                estimated_minutes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (l["day"], l["title"], l.get("concept_markdown", l["why"]), l["block"],
             l["python_concepts"], l["dsa_concepts"], l["why"], l["visual"],
             l.get("example_code", ""), l.get("prediction_question", ""),
             l.get("prediction_answer", ""), l["exercises"], l["must_explain"],
             l["common_mistakes"], l["minutes"]),
        )


def _compute_expected_outputs(reference_source, test_inputs):
    """Run the reference solution against each test input to get verified
    expected outputs, rather than trusting hand-typed values.

    Calls fn() on a DEEP COPY of each args tuple, never the original. Some
    reference solutions mutate their input in place (e.g. "remove
    duplicates in place" -- that's the whole point of the exercise). If we
    called fn(*args) directly, that mutation would corrupt the very
    `test_inputs` objects _seed_problems() later serializes as the stored
    input_args_json -- silently shipping a test case whose stored input no
    longer matches the input the expected output was actually computed
    from. Caught by test_endpoints.py running every reference solution
    through the live API: remove-duplicates-sorted's own reference
    solution failed its own seeded test case because of exactly this."""
    namespace = {}
    exec(reference_source, namespace)
    # The function under test is whichever top-level def matches the
    # problem's public name -- reference sources define exactly one
    # public-facing function (helpers are fine, e.g. Node/build_list).
    fn_name = None
    for line in reference_source.splitlines():
        if line.startswith("def ") and not line.startswith("def build_") and not line.startswith("def to_"):
            candidate = line[4:].split("(")[0]
            fn_name = candidate  # keep the LAST top-level def -- the public one
    fn = namespace[fn_name]
    outputs = []
    for args in test_inputs:
        outputs.append(fn(*copy.deepcopy(args)))
    return outputs


def _seed_problems(conn):
    for p in PROBLEMS:
        expected_outputs = _compute_expected_outputs(p["reference_solution"], p["test_inputs"])

        cur = conn.execute(
            """INSERT INTO problems
               (slug, title, day, topic, pattern, difficulty, description_markdown,
                constraints_markdown, function_signature, starter_code,
                expected_time_complexity, expected_space_complexity,
                brute_force_approach, optimal_approach, common_mistakes, edge_cases,
                related_problem_slugs, prerequisite_topics, has_stress_test,
                stress_test_generator, brute_force_reference, comparison_mode,
                interview_priority, estimated_solve_minutes, progression_stage,
                canonical_reference, path_tier)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (p["slug"], p["title"], p.get("day"), p["topic"], p["pattern"], p["difficulty"],
             p["description"], p.get("constraints", ""), p["function_signature"],
             p["starter_code"], p["expected_time_complexity"], p["expected_space_complexity"],
             p["brute_force_approach"], p["optimal_approach"], p["common_mistakes"],
             p["edge_cases"], "", "", 0, None, p["reference_solution"],
             p.get("comparison_mode", "exact"), p.get("interview_priority"),
             p.get("estimated_solve_minutes"), p.get("progression_stage"),
             p.get("canonical_reference"), p.get("path_tier", "core")),
        )
        problem_id = cur.lastrowid

        for args, expected in zip(p["test_inputs"], expected_outputs):
            conn.execute(
                """INSERT INTO test_cases (problem_id, input_args_json, expected_output_json, is_hidden, label)
                   VALUES (?,?,?,?,?)""",
                (problem_id, json.dumps(list(args)), json.dumps(expected), 0, None),
            )

        for rung, content in enumerate(p["hints"], start=1):
            conn.execute(
                "INSERT INTO hints (problem_id, rung, content_markdown) VALUES (?,?,?)",
                (problem_id, rung, content),
            )


def init_db():
    """Full (re)initialization: drops and recreates every table, including
    attempts/revision_schedule/mistakes, then reseeds lessons and
    problems from source. Destroys any recorded progress -- this is the
    explicit "reset everything" action, meant to be run deliberately via
    `python3 db/init_db.py`, never silently on every app.py startup (see
    ensure_db below, which is what app.py actually calls)."""
    conn = get_connection()
    for t in _TABLES:
        conn.execute(f"DROP TABLE IF EXISTS {t}")
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    _seed_lessons(conn)
    _seed_problems(conn)
    conn.commit()
    lesson_count = conn.execute("SELECT COUNT(*) c FROM lessons").fetchone()["c"]
    problem_count = conn.execute("SELECT COUNT(*) c FROM problems").fetchone()["c"]
    test_case_count = conn.execute("SELECT COUNT(*) c FROM test_cases").fetchone()["c"]
    conn.close()
    print(f"Initialized {DB_PATH}: {lesson_count} lessons, {problem_count} problems, "
          f"{test_case_count} test cases (auto-verified against reference solutions).")


def ensure_db():
    """Safe to call on every app startup: initializes the database ONLY if
    it doesn't exist yet. Never wipes an existing database, so a learner's
    attempts/revision_schedule/streak history survives closing and
    reopening the app. Use `python3 db/init_db.py` directly (init_db())
    when you deliberately want a full reset (e.g. after editing the
    curriculum/problem seed data)."""
    if not os.path.exists(DB_PATH):
        init_db()


if __name__ == "__main__":
    init_db()
