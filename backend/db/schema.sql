-- Traceviz schema (post-Milestone-1). Covers Phase 1 (lessons, problems,
-- hints, testing, progress, revision) per docs/development-roadmap.md and
-- docs/problem-roadmap.md. Superset of the Milestone 1 schema -- `lessons`
-- gains columns via migration-safe ALTERs in init_db.py rather than being
-- redefined here, so existing local databases upgrade cleanly.

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY,
    day INTEGER NOT NULL UNIQUE,
    title TEXT NOT NULL,
    concept_markdown TEXT NOT NULL,
    block TEXT,                    -- e.g. "Python Fundamentals", "Arrays/Strings/Hashing"
    python_concepts TEXT,          -- short text
    dsa_concepts TEXT,
    why_it_matters TEXT,
    visual_concept TEXT,
    example_code TEXT,
    prediction_question TEXT,
    prediction_answer TEXT,
    exercises_markdown TEXT,       -- Day 1-7 style plain drills (no problem row needed)
    must_explain TEXT,
    common_mistakes TEXT,
    estimated_minutes INTEGER
);

CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    day INTEGER NOT NULL,          -- curriculum day this belongs to
    topic TEXT NOT NULL,           -- e.g. "arrays", "hashing"
    pattern TEXT,                  -- e.g. "two-pointer", "sliding-window"
    difficulty TEXT NOT NULL,      -- Easy / Medium / Hard
    description_markdown TEXT NOT NULL,
    constraints_markdown TEXT,
    function_signature TEXT NOT NULL,   -- e.g. "def two_sum(nums, target):"
    starter_code TEXT NOT NULL,
    expected_time_complexity TEXT,
    expected_space_complexity TEXT,
    brute_force_approach TEXT,
    optimal_approach TEXT,
    common_mistakes TEXT,
    edge_cases TEXT,               -- human-readable notes on edge cases to consider
    related_problem_slugs TEXT,    -- comma-separated slugs
    prerequisite_topics TEXT,
    has_stress_test INTEGER NOT NULL DEFAULT 0,
    stress_test_generator TEXT,    -- python source for generate(n) -> args tuple, or NULL
    brute_force_reference TEXT,    -- python source for a reference solution used in stress testing, or NULL
    comparison_mode TEXT NOT NULL DEFAULT 'exact',  -- 'exact' | 'unordered_list' | 'unordered_list_of_lists'
    interview_priority TEXT,       -- 'Core' | 'Important' | 'Optional' -- interview-frequency curation, see problem-roadmap.md
    estimated_solve_minutes INTEGER,
    progression_stage TEXT,        -- 'core' | 'variation' -- whether this is a topic's primary problem or a follow-up building the same pattern
    canonical_reference TEXT       -- e.g. "LeetCode 1: Two Sum" -- citation only, never copied problem text
);

-- Per-lesson learning status, independent of the recommended day order.
-- Lets the curriculum be a *recommended path*, not a locked sequence: any
-- day can be jumped to, marked complete/known/skipped, and resumed from.
-- See docs/decisions.md "Non-linear curriculum navigation".
CREATE TABLE IF NOT EXISTS lesson_progress (
    day INTEGER PRIMARY KEY REFERENCES lessons(day),
    status TEXT NOT NULL DEFAULT 'not_started'
        CHECK (status IN ('not_started', 'in_progress', 'completed', 'skipped', 'known')),
    started_at TEXT,
    completed_at TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER NOT NULL REFERENCES problems(id),
    input_args_json TEXT NOT NULL,   -- JSON array of positional args
    expected_output_json TEXT NOT NULL,
    is_hidden INTEGER NOT NULL DEFAULT 0,  -- shown vs held-out edge case
    label TEXT                        -- e.g. "empty array", "single element"
);

CREATE TABLE IF NOT EXISTS hints (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER NOT NULL REFERENCES problems(id),
    rung INTEGER NOT NULL,     -- 1=conceptual, 2=directional, 3=pseudocode
    content_markdown TEXT NOT NULL,
    UNIQUE(problem_id, rung)
);

CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER NOT NULL REFERENCES problems(id),
    submitted_code TEXT NOT NULL,
    passed INTEGER NOT NULL,           -- 1 if all visible+hidden tests passed
    hints_used INTEGER NOT NULL DEFAULT 0,
    max_hint_rung_seen INTEGER NOT NULL DEFAULT 0,
    solution_revealed INTEGER NOT NULL DEFAULT 0,
    is_independent INTEGER NOT NULL,   -- passed AND hints_used=0 AND solution_revealed=0
    time_taken_seconds INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS revision_schedule (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER NOT NULL UNIQUE REFERENCES problems(id),
    last_attempt_id INTEGER REFERENCES attempts(id),
    next_due_date TEXT NOT NULL,       -- ISO date
    interval_index INTEGER NOT NULL DEFAULT 0,  -- position in the ladder: 0,1,2,3,4
    last_result TEXT                    -- 'independent' | 'assisted' | 'failed'
);

CREATE TABLE IF NOT EXISTS mistake_patterns (
    id INTEGER PRIMARY KEY,
    topic TEXT NOT NULL,
    pattern_key TEXT NOT NULL,   -- e.g. "off_by_one", "missing_visited_set"
    occurrence_count INTEGER NOT NULL DEFAULT 0,
    last_seen_at TEXT,
    UNIQUE(topic, pattern_key)
);
