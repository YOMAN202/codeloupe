"""
Regression test for ensure_db()'s additive migration path (see
db/init_db.py's _migrate_schema / _migrate_seed_new_content).

run_all_tests.sh's reseed() helper (rm -f traceviz.db && python3
db/init_db.py) always starts from an empty file, so it only ever exercises
the fresh-install codepath -- never ensure_db()'s "existing database, run
migrations only" branch (see ensure_db's own docstring: it runs init_db()
ONLY when DB_PATH doesn't exist at all). That gap is exactly what let the
150-problem/50-day curriculum refinement ship a new problems.
secondary_concept_slugs column and new lesson/problem/concept rows that an
already-deployed traceviz.db would never receive: every /api/lessons/<day>
request for a day the old DB didn't have 404'd, and every /api/concepts/
<slug> request 500'd (SELECT ... secondary_concept_slugs FROM problems
against a table that didn't have the column yet).

This script simulates that scenario directly: build a full, freshly seeded
database with the CURRENT code, age it back down to a pre-refinement shape
(drop the newest lesson days/problems/concept lesson, rebuild `problems`
without secondary_concept_slugs), record some fake user progress against
it, then run the real ensure_db() and assert it heals the schema/content
gap completely while leaving every pre-existing row -- and the fake
progress recorded against it -- untouched. Also asserts a second ensure_db()
call is a true no-op (no duplicate rows), since it runs on every app.py
startup, not just once.

Not a pytest suite -- same throwaway PASS/FAIL style as test_endpoints.py.
Run standalone: `python3 test_migration.py` from backend/. Does not talk to
a running server -- this is a database-layer test, exercising the exact
functions app.py's WSGI-time `ensure_db()` call runs (see app.py's own
comment on why that call happens at import time, not just under
`if __name__ == "__main__":`).
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "db"))

import db.init_db as init_db_mod
from db.seed_lessons import LESSONS
from db.seed_problems import PROBLEMS

failures = []


def check(label, cond, extra=None):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {label}" + (f" -- {extra}" if extra and not cond else ""))
    if not cond:
        failures.append(label)


TEST_DB = os.path.join(os.path.dirname(__file__), "db", "test_migration.db")
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
init_db_mod.DB_PATH = TEST_DB

FULL_LESSON_COUNT = len(LESSONS)
FULL_PROBLEM_COUNT = len(PROBLEMS)

# 1. Build a full, freshly seeded database with the CURRENT code -- "what a
#    real install looks like after every seed has landed".
init_db_mod.init_db()

# 2. Age it down into a pre-refinement shape: drop the newest 5 lesson
#    days, drop everything past the historical 109-problem count, drop the
#    greedy concept lesson, and rebuild `problems` WITHOUT
#    secondary_concept_slugs -- i.e. undo exactly what the 150-problem/
#    50-day refinement added, so this test keeps testing "migrating an
#    install that predates the newest expansion" even as future expansions
#    grow LESSONS/PROBLEMS/CONCEPT_LESSONS further.
OLD_LESSON_COUNT = FULL_LESSON_COUNT - 5
OLD_PROBLEM_COUNT = 109  # the pre-expansion problem count (see docs/EXPANSION_PLAN.md)

conn = sqlite3.connect(TEST_DB)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = OFF")

old_days = [r["day"] for r in conn.execute("SELECT day FROM lessons ORDER BY day").fetchall()][:OLD_LESSON_COUNT]
conn.execute(f"DELETE FROM lesson_progress WHERE day NOT IN ({','.join('?' * len(old_days))})", old_days)
conn.execute(f"DELETE FROM lessons WHERE day NOT IN ({','.join('?' * len(old_days))})", old_days)

old_problem_ids = [r["id"] for r in conn.execute("SELECT id FROM problems ORDER BY id").fetchall()][:OLD_PROBLEM_COUNT]
placeholders = ",".join("?" * len(old_problem_ids))
conn.execute(f"DELETE FROM test_cases WHERE problem_id NOT IN ({placeholders})", old_problem_ids)
conn.execute(f"DELETE FROM hints WHERE problem_id NOT IN ({placeholders})", old_problem_ids)
conn.execute(f"DELETE FROM attempts WHERE problem_id NOT IN ({placeholders})", old_problem_ids)
conn.execute(f"DELETE FROM revision_schedule WHERE problem_id NOT IN ({placeholders})", old_problem_ids)
conn.execute(f"DELETE FROM problems WHERE id NOT IN ({placeholders})", old_problem_ids)

conn.execute("DELETE FROM concept_practice_exercises WHERE concept_lesson_id IN "
             "(SELECT id FROM concept_lessons WHERE slug = 'greedy')")
conn.execute("DELETE FROM concept_checkpoints WHERE concept_lesson_id IN "
             "(SELECT id FROM concept_lessons WHERE slug = 'greedy')")
conn.execute("DELETE FROM concept_lesson_progress WHERE concept_lesson_id IN "
             "(SELECT id FROM concept_lessons WHERE slug = 'greedy')")
conn.execute("DELETE FROM concept_lessons WHERE slug = 'greedy'")

# Rebuild `problems` without secondary_concept_slugs, simulating a database
# from before that column existed (SQLite can't DROP COLUMN pre-3.35, and
# this keeps the test honest about the actual pre-migration shape rather
# than just leaving the column present-but-empty). Starts from SQLite's own
# stored CREATE TABLE text (sqlite_master.sql, produced by schema.sql's
# executescript when this DB was first created above) rather than
# re-parsing schema.sql's raw source, so this can't be thrown off by
# comment text/commas in that file's column comments.
cols = [r["name"] for r in conn.execute("PRAGMA table_info(problems)").fetchall()
        if r["name"] != "secondary_concept_slugs"]
col_list = ", ".join(cols)
original_create_sql = conn.execute(
    "SELECT sql FROM sqlite_master WHERE type='table' AND name='problems'"
).fetchone()["sql"]
old_shape_lines = [
    line for line in original_create_sql.splitlines()
    if "secondary_concept_slugs" not in line
]
old_shape_sql = "\n".join(old_shape_lines)
# The removed column's line carried the trailing comma for its row; strip
# a lone comma that now immediately precedes the closing paren/comment so
# the statement stays valid (path_tier's own line, the new last column,
# already has no trailing comma of its own -- see schema.sql).
import re as _re
old_shape_sql = _re.sub(r",(\s*(--[^\n]*\n)?\s*\))", r"\1", old_shape_sql, count=1)

# legacy_alter_table stops SQLite's default "smart" RENAME from also
# rewriting the REFERENCES clauses that test_cases/hints/attempts/
# revision_schedule hold on `problems` (which would otherwise leave them
# pointing at a `problems_old_shape` table that's about to be dropped) --
# with it on, ALTER TABLE RENAME touches only the `problems` table's own
# name, exactly what's needed since a table named `problems` exists again
# by the time this connection's foreign-key-checked INSERTs run.
conn.execute("PRAGMA legacy_alter_table = ON")
conn.execute("ALTER TABLE problems RENAME TO problems_old_shape")
conn.execute(old_shape_sql)
conn.execute(f"INSERT INTO problems ({col_list}) SELECT {col_list} FROM problems_old_shape")
conn.execute("DROP TABLE problems_old_shape")
conn.execute("PRAGMA legacy_alter_table = OFF")
conn.execute("PRAGMA foreign_keys = ON")
conn.commit()

# 3. Record some fake pre-existing user progress against this "old" DB,
#    the way a real learner's browser would have by the time an expansion
#    ships -- this is what must survive the migration untouched.
VISITOR = "migration-test-visitor"
conn.execute(
    "INSERT INTO lesson_progress (day, visitor_id, status, started_at, completed_at, updated_at) "
    "VALUES (?, ?, 'completed', '2026-01-01T00:00:00', '2026-01-02T00:00:00', '2026-01-02T00:00:00')",
    (old_days[4], VISITOR),
)
conn.execute(
    "INSERT INTO lesson_progress (day, visitor_id, status, started_at, completed_at, updated_at) "
    "VALUES (?, ?, 'known', '2026-01-03T00:00:00', '2026-01-03T00:00:00', '2026-01-03T00:00:00')",
    (old_days[10], VISITOR),
)
first_old_problem_id = old_problem_ids[0]
conn.execute(
    "INSERT INTO attempts (problem_id, visitor_id, submitted_code, passed, is_independent, created_at) "
    "VALUES (?, ?, 'print(1)', 1, 1, '2026-01-01T00:00:00')",
    (first_old_problem_id, VISITOR),
)
conn.commit()

check("pre-migration fixture has the old (pre-expansion) lesson count",
      conn.execute("SELECT COUNT(*) c FROM lessons").fetchone()["c"] == OLD_LESSON_COUNT)
check("pre-migration fixture has the old (pre-expansion) problem count",
      conn.execute("SELECT COUNT(*) c FROM problems").fetchone()["c"] == OLD_PROBLEM_COUNT)
check("pre-migration fixture has no greedy concept lesson",
      conn.execute("SELECT COUNT(*) c FROM concept_lessons WHERE slug='greedy'").fetchone()["c"] == 0)
check("pre-migration fixture has no secondary_concept_slugs column",
      "secondary_concept_slugs" not in [r["name"] for r in conn.execute("PRAGMA table_info(problems)").fetchall()])
conn.close()

# 4. Run the REAL migration entry point -- exactly what app.py runs at
#    import time on every deploy/restart.
init_db_mod.ensure_db()

conn = sqlite3.connect(TEST_DB)
conn.row_factory = sqlite3.Row

check(f"ensure_db() backfills all {FULL_LESSON_COUNT} lesson days",
      conn.execute("SELECT COUNT(*) c FROM lessons").fetchone()["c"] == FULL_LESSON_COUNT,
      conn.execute("SELECT COUNT(*) c FROM lessons").fetchone()["c"])
check(f"ensure_db() backfills all {FULL_PROBLEM_COUNT} problems",
      conn.execute("SELECT COUNT(*) c FROM problems").fetchone()["c"] == FULL_PROBLEM_COUNT,
      conn.execute("SELECT COUNT(*) c FROM problems").fetchone()["c"])
check("ensure_db() backfills the greedy concept lesson",
      conn.execute("SELECT COUNT(*) c FROM concept_lessons WHERE slug='greedy'").fetchone()["c"] == 1)
check("ensure_db() adds the secondary_concept_slugs column",
      "secondary_concept_slugs" in [r["name"] for r in conn.execute("PRAGMA table_info(problems)").fetchall()])

# A query shaped exactly like app.py's _related_problems_for_concept --
# this is the query that would raise sqlite3.OperationalError against an
# unmigrated database and 500 every /api/concepts/<slug> request.
try:
    conn.execute("SELECT id, slug, title, difficulty, pattern, path_tier, day, topic, "
                 "secondary_concept_slugs FROM problems").fetchall()
    concept_query_ok = True
except sqlite3.OperationalError:
    concept_query_ok = False
check("app.py's concept-detail query (reads secondary_concept_slugs) succeeds post-migration", concept_query_ok)

lp = {r["day"]: r["status"] for r in
      conn.execute("SELECT day, status FROM lesson_progress WHERE visitor_id=?", (VISITOR,)).fetchall()}
check("pre-existing lesson_progress ('completed') survives the migration untouched",
      lp.get(old_days[4]) == "completed", lp)
check("pre-existing lesson_progress ('known') survives the migration untouched",
      lp.get(old_days[10]) == "known", lp)
attempts = conn.execute("SELECT problem_id, submitted_code, passed FROM attempts WHERE visitor_id=?",
                         (VISITOR,)).fetchall()
check("pre-existing attempt survives the migration untouched",
      len(attempts) == 1 and attempts[0]["problem_id"] == first_old_problem_id and attempts[0]["passed"] == 1,
      [dict(a) for a in attempts])

# 5. ensure_db() runs on every app startup, not just once -- a second call
#    must be a true no-op (no duplicate rows, nothing re-inserted).
conn.close()
init_db_mod.ensure_db()
conn = sqlite3.connect(TEST_DB)
conn.row_factory = sqlite3.Row
check("a second ensure_db() call does not duplicate lessons",
      conn.execute("SELECT COUNT(*) c FROM lessons").fetchone()["c"] == FULL_LESSON_COUNT)
check("a second ensure_db() call does not duplicate problems",
      conn.execute("SELECT COUNT(*) c FROM problems").fetchone()["c"] == FULL_PROBLEM_COUNT)
check("a second ensure_db() call does not duplicate the fake attempt",
      conn.execute("SELECT COUNT(*) c FROM attempts WHERE visitor_id=?", (VISITOR,)).fetchone()["c"] == 1)
conn.close()

os.remove(TEST_DB)

print(f"\n{len(failures)} failure(s)." if failures else "\nAll migration checks passed.")
sys.exit(1 if failures else 0)
