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
from seed_concepts import CONCEPT_LESSONS, CONCEPT_CHECKPOINTS, CONCEPT_PRACTICE_EXERCISES

DB_PATH = os.path.join(os.path.dirname(__file__), "traceviz.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

_TABLES = ["mistakes", "revision_schedule", "attempts", "hints",
           "test_cases", "problems", "lesson_progress", "lessons",
           "concept_lesson_progress", "concept_practice_exercises",
           "concept_checkpoints", "concept_lessons"]
# lesson_progress was missing from this list before per-visitor isolation
# (see docs on visitor_id below) -- harmless as long as lesson_progress was
# always empty when init_db() ran (true for every prior reseed, since
# run_all_tests.sh's reseed() and every doc'd workflow delete traceviz.db
# outright rather than calling init_db() against an existing one), but a
# real FOREIGN KEY constraint failure waiting to happen the first time
# init_db() runs against a database that actually has lesson_progress rows
# -- dropping `lessons` while `lesson_progress` still references it (FK
# enforcement is on, see get_connection()) fails unless lesson_progress is
# dropped first. Fixed here since testing this change's migration surfaced
# it directly.


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
                stress_test_generator, optimal_reference, brute_force_reference,
                growth_curve_generator, growth_curve_sizes, comparison_mode,
                interview_priority, estimated_solve_minutes, progression_stage,
                canonical_reference, path_tier, secondary_concept_slugs)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (p["slug"], p["title"], p.get("day"), p["topic"], p["pattern"], p["difficulty"],
             p["description"], p.get("constraints", ""), p["function_signature"],
             p["starter_code"], p["expected_time_complexity"], p["expected_space_complexity"],
             p["brute_force_approach"], p["optimal_approach"], p["common_mistakes"],
             p["edge_cases"], "", "", 0, None, p["reference_solution"],
             p.get("brute_force_code"), p.get("growth_curve_generator"),
             json.dumps(p["growth_curve_sizes"]) if p.get("growth_curve_sizes") else None,
             p.get("comparison_mode", "exact"), p.get("interview_priority"),
             p.get("estimated_solve_minutes"), p.get("progression_stage"),
             p.get("canonical_reference"), p.get("path_tier", "core"),
             p.get("secondary_concept_slugs")),
        )
        problem_id = cur.lastrowid

        # test_labels is optional and, when present, must be the same length
        # as test_inputs (entries may be None for a case that doesn't need
        # one) -- it's a short human-readable tag like "single element" or
        # "duplicates with negative numbers", surfaced by get_problem() as
        # part of each visible test case so the frontend's "Trace against"
        # picker can show something more scannable than raw JSON args once
        # a problem has more than a couple of cases.
        labels = p.get("test_labels") or [None] * len(p["test_inputs"])
        for args, expected, label in zip(p["test_inputs"], expected_outputs, labels):
            conn.execute(
                """INSERT INTO test_cases (problem_id, input_args_json, expected_output_json, is_hidden, label)
                   VALUES (?,?,?,?,?)""",
                (problem_id, json.dumps(list(args)), json.dumps(expected), 0, label),
            )

        for rung, content in enumerate(p["hints"], start=1):
            conn.execute(
                "INSERT INTO hints (problem_id, rung, content_markdown) VALUES (?,?,?)",
                (problem_id, rung, content),
            )


def _seed_concepts(conn):
    for c in CONCEPT_LESSONS:
        cur = conn.execute(
            """INSERT INTO concept_lessons
               (slug, kind, topic, pattern_family, title, display_order, estimated_minutes,
                summary, prerequisite_slugs, what_markdown, why_markdown, recognize_markdown,
                intuition_markdown, walkthrough_intro_markdown, walkthrough_code,
                walkthrough_frames_json, common_mistakes_markdown, complexity_markdown)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (c["slug"], c["kind"], c["topic"], c.get("pattern_family"), c["title"],
             c.get("display_order", 0), c.get("estimated_minutes"), c["summary"],
             c.get("prerequisite_slugs", ""), c["what_markdown"], c["why_markdown"],
             c.get("recognize_markdown"), c["intuition_markdown"],
             c.get("walkthrough_intro_markdown"), c.get("walkthrough_code"),
             json.dumps(c["walkthrough_frames"]) if c.get("walkthrough_frames") else None,
             c.get("common_mistakes_markdown"), c.get("complexity_markdown")),
        )
        concept_id = cur.lastrowid

        for order, chk in enumerate(CONCEPT_CHECKPOINTS.get(c["slug"], [])):
            conn.execute(
                """INSERT INTO concept_checkpoints
                   (concept_lesson_id, display_order, kind, prompt_markdown, code,
                    choices_json, correct_answer, explanation_markdown)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (concept_id, order, chk["kind"], chk["prompt_markdown"], chk.get("code"),
                 json.dumps(chk["choices_json"]) if chk.get("choices_json") else None,
                 chk["correct_answer"], chk["explanation_markdown"]),
            )

        for order, ex in enumerate(CONCEPT_PRACTICE_EXERCISES.get(c["slug"], [])):
            conn.execute(
                """INSERT INTO concept_practice_exercises
                   (concept_lesson_id, display_order, prompt_markdown, starter_code,
                    solution_code, hint_markdown)
                   VALUES (?,?,?,?,?,?)""",
                (concept_id, order, ex["prompt_markdown"], ex.get("starter_code"),
                 ex["solution_code"], ex.get("hint_markdown")),
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
    _seed_concepts(conn)
    conn.commit()
    lesson_count = conn.execute("SELECT COUNT(*) c FROM lessons").fetchone()["c"]
    problem_count = conn.execute("SELECT COUNT(*) c FROM problems").fetchone()["c"]
    test_case_count = conn.execute("SELECT COUNT(*) c FROM test_cases").fetchone()["c"]
    concept_count = conn.execute("SELECT COUNT(*) c FROM concept_lessons").fetchone()["c"]
    conn.close()
    print(f"Initialized {DB_PATH}: {lesson_count} lessons, {problem_count} problems, "
          f"{test_case_count} test cases (auto-verified against reference solutions), "
          f"{concept_count} concept lessons.")


# Sentinel visitor_id existing rows are backfilled to when a pre-visitor-
# isolation database is migrated (see _migrate_add_visitor_id below). Must
# match schema.sql's DEFAULT 'legacy-local-user' on every per-visitor
# table, and app.py's DEFAULT_VISITOR_ID fallback for callers that don't
# send an X-Visitor-Id header -- all three need to agree for a migrated
# install's pre-existing progress to stay reachable at all (see that
# function's docstring for how to actually reach it from a browser).
LEGACY_VISITOR_ID = "legacy-local-user"


def _table_columns(conn, table):
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def _rebuild_table_with_visitor_pk(conn, table, create_sql, copy_columns):
    """Shared implementation for the three tables whose PRIMARY KEY/UNIQUE
    constraint has to change to include visitor_id -- SQLite can't ALTER an
    existing key constraint in place, so this does the standard SQLite
    "rebuild" migration: rename the old table aside, create the new one
    from `create_sql` (which must match schema.sql's CREATE TABLE for
    `table` exactly), copy every existing row across with visitor_id set to
    LEGACY_VISITOR_ID, then drop the old table. Runs inside one transaction
    with foreign_keys off for the swap, so a failure partway through never
    leaves the database in a half-migrated state."""
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        conn.execute(f"ALTER TABLE {table} RENAME TO {table}_pre_visitor")
        conn.execute(create_sql)
        cols = ", ".join(copy_columns)
        conn.execute(
            f"INSERT INTO {table} ({cols}, visitor_id) "
            f"SELECT {cols}, ? FROM {table}_pre_visitor",
            (LEGACY_VISITOR_ID,),
        )
        conn.execute(f"DROP TABLE {table}_pre_visitor")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")


def _migrate_add_visitor_id(conn):
    """Anonymous per-visitor data isolation, added after Codeloupe had
    already been running as a single global-progress install for a while
    (see docs/decisions.md). Brings an existing traceviz.db up to the same
    visitor_id-scoped shape schema.sql now defines for a fresh install,
    WITHOUT deleting any recorded progress:

    - attempts/mistakes just gain a plain visitor_id column (ALTER TABLE
      ADD COLUMN works fine for a new nullable-by-default column).
    - lesson_progress/revision_schedule/concept_lesson_progress each had a
      PRIMARY KEY or UNIQUE constraint that has to actually change shape
      (day -> (day, visitor_id), etc.), which SQLite cannot do with ALTER
      TABLE -- those three go through the rebuild helper above instead.

    Every existing row, in every case, is backfilled to LEGACY_VISITOR_ID
    rather than dropped -- so upgrading never loses history. That id isn't
    automatically "your" browser's new visitor id, though: the frontend
    always generates a fresh random id for a browser profile that doesn't
    have one yet (see frontend/src/api/visitorId.js), on purpose -- two
    genuinely separate first-time visitors (e.g. two incognito windows on a
    machine with no existing database) must never be handed the same id.
    That means a solo user upgrading an existing local install won't
    automatically see their pre-upgrade history under their new id. Their
    data is NOT lost -- it's sitting in the database under
    'legacy-local-user' -- and reclaiming it is one manual step: open the
    browser console on http://127.0.0.1:5173 and run
        localStorage.setItem('codeloupe_visitor_id', 'legacy-local-user')
    then reload. ensure_db() prints this same note at startup whenever it
    detects legacy rows, so it isn't buried in a comment nobody reads."""
    if "visitor_id" not in _table_columns(conn, "attempts"):
        conn.execute(f"ALTER TABLE attempts ADD COLUMN visitor_id TEXT NOT NULL DEFAULT '{LEGACY_VISITOR_ID}'")
        conn.commit()
    if "visitor_id" not in _table_columns(conn, "mistakes"):
        conn.execute(f"ALTER TABLE mistakes ADD COLUMN visitor_id TEXT NOT NULL DEFAULT '{LEGACY_VISITOR_ID}'")
        conn.commit()

    if "visitor_id" not in _table_columns(conn, "lesson_progress"):
        _rebuild_table_with_visitor_pk(
            conn, "lesson_progress",
            """CREATE TABLE lesson_progress (
                   day INTEGER NOT NULL REFERENCES lessons(day),
                   visitor_id TEXT NOT NULL DEFAULT 'legacy-local-user',
                   status TEXT NOT NULL DEFAULT 'not_started'
                       CHECK (status IN ('not_started', 'in_progress', 'completed', 'skipped', 'known')),
                   started_at TEXT,
                   completed_at TEXT,
                   updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                   PRIMARY KEY (day, visitor_id)
               )""",
            ["day", "status", "started_at", "completed_at", "updated_at"],
        )

    if "visitor_id" not in _table_columns(conn, "revision_schedule"):
        _rebuild_table_with_visitor_pk(
            conn, "revision_schedule",
            """CREATE TABLE revision_schedule (
                   id INTEGER PRIMARY KEY,
                   problem_id INTEGER NOT NULL REFERENCES problems(id),
                   visitor_id TEXT NOT NULL DEFAULT 'legacy-local-user',
                   last_attempt_id INTEGER REFERENCES attempts(id),
                   next_due_date TEXT NOT NULL,
                   interval_index INTEGER NOT NULL DEFAULT 0,
                   last_result TEXT,
                   source TEXT NOT NULL DEFAULT 'auto',
                   UNIQUE(problem_id, visitor_id)
               )""",
            ["id", "problem_id", "last_attempt_id", "next_due_date", "interval_index", "last_result", "source"],
        )

    if "visitor_id" not in _table_columns(conn, "concept_lesson_progress"):
        _rebuild_table_with_visitor_pk(
            conn, "concept_lesson_progress",
            """CREATE TABLE concept_lesson_progress (
                   concept_lesson_id INTEGER NOT NULL REFERENCES concept_lessons(id),
                   visitor_id TEXT NOT NULL DEFAULT 'legacy-local-user',
                   status TEXT NOT NULL DEFAULT 'not_started'
                       CHECK (status IN ('not_started', 'in_progress', 'completed', 'known')),
                   updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                   PRIMARY KEY (concept_lesson_id, visitor_id)
               )""",
            ["concept_lesson_id", "status", "updated_at"],
        )


def _migrate_schema(conn):
    """Additive, idempotent migrations for databases created before a given
    column existed -- run on EVERY startup (not just fresh installs) so an
    existing learner's traceviz.db picks up new columns without ever being
    dropped/recreated. Deliberately tiny and column-by-column rather than a
    real migration framework (see the module docstring on why that's out of
    scope for a single-user tool) -- extend this, never init_db()'s
    DROP/CREATE path, when a new column needs to reach existing installs."""
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(revision_schedule)").fetchall()}
    if "source" not in cols:
        conn.execute("ALTER TABLE revision_schedule ADD COLUMN source TEXT NOT NULL DEFAULT 'auto'")
        conn.commit()

    _migrate_add_visitor_id(conn)


def _legacy_visitor_notice(conn):
    """Printed at startup whenever a migrated database still has rows under
    the legacy sentinel from _migrate_add_visitor_id -- see that function's
    docstring for the one-line browser-console snippet this is pointing
    at. Silent (no query at all) once every legacy row has been reclaimed
    or has aged out, so this doesn't nag forever on a long-lived install."""
    try:
        n = conn.execute(
            "SELECT COUNT(*) c FROM attempts WHERE visitor_id = ?", (LEGACY_VISITOR_ID,)
        ).fetchone()["c"]
    except sqlite3.OperationalError:
        return  # pre-migration db mid-startup race; harmless, next check will see it
    if n:
        print(
            f"[codeloupe] {n} attempt(s) from before per-visitor isolation are stored under a "
            f"legacy id. To see them again in your browser, open its console and run:\n"
            f"    localStorage.setItem('codeloupe_visitor_id', '{LEGACY_VISITOR_ID}')\n"
            f"then reload the page."
        )


def ensure_db():
    """Safe to call on every app startup: initializes the database ONLY if
    it doesn't exist yet. Never wipes an existing database, so a learner's
    attempts/revision_schedule/streak history survives closing and
    reopening the app. Use `python3 db/init_db.py` directly (init_db())
    when you deliberately want a full reset (e.g. after editing the
    curriculum/problem seed data). Runs _migrate_schema either way, since
    a brand-new db and an existing one both need to end up with the same
    columns -- schema.sql covers the former, the migration covers the
    latter."""
    if not os.path.exists(DB_PATH):
        init_db()
    else:
        conn = get_connection()
        _migrate_schema(conn)
        _legacy_visitor_notice(conn)
        conn.close()


if __name__ == "__main__":
    init_db()
