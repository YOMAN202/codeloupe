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
    day INTEGER,                   -- curriculum day this belongs to; NULL for
                                    -- extended-practice problems not tied to a
                                    -- specific required day (see path_tier)
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
    stress_test_generator TEXT,    -- reserved for future randomized differential correctness
                                    -- testing (generate(n) -> args tuple, compared against
                                    -- optimal_reference). Not used by approach comparison below --
                                    -- see growth_curve_generator/growth_curve_sizes for that.
    optimal_reference TEXT,        -- python source for the canonical correct solution -- the SAME
                                    -- code already used to compute this problem's expected test
                                    -- outputs at seed time (see init_db.py's _compute_expected_outputs).
                                    -- Populated for every problem. Powers "reveal solution" and the
                                    -- optimal side of approach comparison. (Was named
                                    -- brute_force_reference before the approach-comparison feature --
                                    -- renamed because it was never actually a brute-force solution.)
    brute_force_reference TEXT,    -- python source for a genuinely distinct, correct BASELINE
                                    -- approach with meaningfully worse complexity than
                                    -- optimal_reference. Deliberately NULL for most problems --
                                    -- only populated where a real, useful naive alternative exists
                                    -- (see docs/decisions.md). Approach comparison degrades
                                    -- gracefully to "your code vs the optimal reference" when NULL.
    growth_curve_generator TEXT,   -- python source defining generate(n) -> args tuple, sized ~n.
                                    -- Only set alongside brute_force_reference -- used for the
                                    -- empirical runtime/memory growth-curve in approach comparison.
    growth_curve_sizes TEXT,       -- JSON array of input sizes to benchmark at, hand-picked per
                                    -- problem's complexity class. Only set alongside
                                    -- growth_curve_generator.
    comparison_mode TEXT NOT NULL DEFAULT 'exact',  -- 'exact' | 'float_close' | 'unordered_list' | 'unordered_list_of_lists' | 'unordered_list_of_sorted_lists'
    interview_priority TEXT,       -- 'Core' | 'Important' | 'Optional' -- interview-frequency curation, see problem-roadmap.md
    estimated_solve_minutes INTEGER,
    progression_stage TEXT,        -- 'core' | 'variation' -- whether this is a topic's primary problem or a follow-up building the same pattern
    canonical_reference TEXT,      -- e.g. "LeetCode 1: Two Sum" -- citation only, never copied problem text
    path_tier TEXT NOT NULL DEFAULT 'core'  -- 'core' (required 45-day path, tied to a day) | 'extended' (optional Easy/Medium reinforcement, day is NULL) | 'advanced' (optional curated Hard problems, day is NULL, never required for Core Path completion)
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

-- Mistake journal: one row per FAILED attempt (never for a pass), created
-- automatically at log-attempt time by the heuristic classifier in
-- logic/mistakes.py, then optionally revised by the learner themselves.
-- category is NULL for "unclassified" -- a legitimate, expected outcome,
-- not an error state. See logic/mistakes.py's module docstring for the
-- full confidence-level design (why the automated classifier never
-- assigns anything above "likely_issue").
CREATE TABLE IF NOT EXISTS mistakes (
    id INTEGER PRIMARY KEY,
    attempt_id INTEGER NOT NULL UNIQUE REFERENCES attempts(id),
    problem_id INTEGER NOT NULL REFERENCES problems(id),
    category TEXT,                      -- one of logic/mistakes.py's MISTAKE_CATEGORIES, or NULL
    confidence TEXT NOT NULL,           -- 'unclassified' (category IS NULL) | 'observed_confirmed' |
                                         -- 'likely_issue' | 'user_confirmed' | 'manually_selected'
    evidence TEXT,                      -- short factual note the classifier (or the learner) attached
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------
-- Teaching system: structured concept lessons (topic overviews and
-- pattern deep-dives), separate from the day-based `lessons` table above.
-- `lessons` stays what it always was -- a concise per-day mix of Python
-- fundamentals and a pointer at the DSA vocabulary for that day.
-- `concept_lessons` is the deeper "what is this, why does it work, when
-- do I reach for it" teaching content the day lessons never had room for.
--
-- Deliberately hangs off the SAME vocabulary the problem bank already
-- uses -- problems.topic (15 existing values: 'arrays', 'two-pointer',
-- etc.) and logic/pattern_families.py's normalized family names -- rather
-- than inventing a new taxonomy. That is what makes this scale to the
-- rest of the curriculum later without a redesign: a new concept lesson
-- is just a new row whose `topic` matches an existing problems.topic
-- value, and every problem/day/lesson tagged with that topic picks it up
-- automatically (see the dynamic linking notes below) -- no new join
-- table to keep in sync, no per-problem/per-day authoring required.
--
-- Linking to problems and day-lessons is intentionally NOT a foreign key
-- or join table: it's computed at request time in app.py by matching
-- problems.topic (and logic.pattern_families.pattern_family_for) against
-- concept_lessons.topic/pattern_family. A hardcoded link table would go
-- stale the moment a new problem or day lesson is added; deriving it from
-- the vocabulary both already share never can.
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS concept_lessons (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,             -- e.g. 'arrays', 'two-pointers'
    kind TEXT NOT NULL CHECK (kind IN ('topic', 'pattern')),
                                            -- 'topic'   = broad foundational lesson for a problems.topic
                                            --             value (what arrays are, indexing, traversal...)
                                            -- 'pattern' = a recognizable technique within/across topics
                                            --             (two pointers, sliding window...), taught with
                                            --             explicit "when should I use this?" signals
    topic TEXT NOT NULL,                   -- matches an existing problems.topic value
    pattern_family TEXT,                   -- optional: matches a logic/pattern_families.py family name,
                                            -- for a 'pattern' lesson that maps onto one specific family
    title TEXT NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,
    estimated_minutes INTEGER,
    summary TEXT NOT NULL,                 -- 1 sentence, shown on Learn hub cards and problem-page callouts
    prerequisite_slugs TEXT,               -- comma-separated concept_lessons.slug values (recommended, not gated)
    what_markdown TEXT NOT NULL,           -- what the concept/pattern is
    why_markdown TEXT NOT NULL,            -- why it's useful / what problem it solves
    recognize_markdown TEXT,               -- "when should I use this?" -- concrete recognition signals
                                            -- (NULL for most 'topic' lessons, required in spirit for 'pattern' ones)
    intuition_markdown TEXT NOT NULL,      -- the core idea in plain language, before any code
    walkthrough_intro_markdown TEXT,       -- short lead-in to the worked example below
    walkthrough_code TEXT,                 -- the annotated worked-example code shown alongside the walkthrough
    walkthrough_frames_json TEXT,          -- JSON array of {caption, locals} teaching-visualization frames --
                                            -- controlled/authored example state, NOT a trace of the user's own
                                            -- code. Rendered by ConceptWalkthrough.jsx, which reuses the same
                                            -- ArrayPointerView/etc. components the real tracer uses, but is a
                                            -- fully separate component from TraceViewer.jsx: this data never
                                            -- touches the sys.settrace pipeline. See docs/decisions.md.
    common_mistakes_markdown TEXT,
    complexity_markdown TEXT               -- time/space complexity discussion for this concept/pattern
);

CREATE TABLE IF NOT EXISTS concept_checkpoints (
    id INTEGER PRIMARY KEY,
    concept_lesson_id INTEGER NOT NULL REFERENCES concept_lessons(id),
    display_order INTEGER NOT NULL DEFAULT 0,
    kind TEXT NOT NULL CHECK (kind IN
        ('predict_output', 'choose_pattern', 'spot_bug', 'complexity', 'order_steps')),
    prompt_markdown TEXT NOT NULL,
    code TEXT,                              -- optional code snippet the prompt refers to
    choices_json TEXT,                      -- JSON array of choice strings (multiple-choice-style checkpoints);
                                             -- NULL for free-response ones (predict_output, complexity)
    correct_answer TEXT NOT NULL,           -- matches a choices_json entry, or free text otherwise
    explanation_markdown TEXT NOT NULL      -- shown after answering, right or wrong -- reinforces either way
);

-- Small guided drills done in the scratchpad BEFORE a full curated
-- problem -- deliberately lighter-weight than the problem bank (no test
-- harness, no hints ladder, no attempt/mistake tracking). Just a prompt,
-- a nudge, and a reference solution to compare against.
CREATE TABLE IF NOT EXISTS concept_practice_exercises (
    id INTEGER PRIMARY KEY,
    concept_lesson_id INTEGER NOT NULL REFERENCES concept_lessons(id),
    display_order INTEGER NOT NULL DEFAULT 0,
    prompt_markdown TEXT NOT NULL,
    starter_code TEXT,
    solution_code TEXT NOT NULL,
    hint_markdown TEXT
);

-- Per-concept-lesson learning status, independent of day lesson_progress
-- above (a learner can know the "two pointers" pattern lesson without
-- that being tied to any single curriculum day).
CREATE TABLE IF NOT EXISTS concept_lesson_progress (
    concept_lesson_id INTEGER PRIMARY KEY REFERENCES concept_lessons(id),
    status TEXT NOT NULL DEFAULT 'not_started'
        CHECK (status IN ('not_started', 'in_progress', 'completed', 'known')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
