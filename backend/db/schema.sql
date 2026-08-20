-- Milestone 1 schema: just enough to back the basic lesson view.
-- Problem/hint/progress-tracking tables are Milestone 3 (see
-- docs/development-roadmap.md) and are deliberately not created yet.

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY,
    day INTEGER NOT NULL UNIQUE,
    title TEXT NOT NULL,
    concept_markdown TEXT NOT NULL
);
