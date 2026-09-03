"""
Pattern families: a normalization layer over problems.pattern.

problems.pattern is deliberately specific per-problem ("Floyd's slow/fast
pointer", "fast/slow + reversal", "fast/slow pointer" are three DIFFERENT
strings for what's really the same underlying technique family). Grouping
directly on the raw column would make pattern-level revision tracking
nearly useless -- 107 distinct pattern strings across 109 problems, almost
all singletons. What the user actually wants ("needs more practice with
fast/slow pointers") requires bucketing related patterns together first.

This is a small ordered rule table (topic + keyword-in-pattern -> family
name), not a hardcoded per-problem lookup, specifically so it keeps
working correctly as new problems are added later without needing a new
entry for every single one. Rules are checked in order; first match wins.
Falls back to a topic-level family name ("General <topic>") rather than
guessing at a family that doesn't apply -- this NEVER replaces
topic-level tracking (see docs/decisions.md), it sits alongside it.
"""

# Each rule: (predicate(topic, pattern_lower) -> bool, family name)
_RULES = [
    (lambda t, p: "fast/slow" in p or "slow/fast" in p, "Fast/slow pointers"),
    (lambda t, p: t == "linked-lists" and ("reversal" in p or "rewiring" in p), "Pointer rewiring"),
    (lambda t, p: t == "linked-lists" and ("merge" in p or "dummy-head" in p), "Linked-list merging"),
    (lambda t, p: t == "linked-lists" and "gap" in p, "Pointer rewiring"),
    (lambda t, p: t == "sliding-window" and "variable" in p, "Sliding-window boundaries"),
    (lambda t, p: t == "sliding-window" and "fixed" in p, "Sliding-window fixed-size"),
    (lambda t, p: t == "hashing" and "frequency" in p, "Hash-map frequency counting"),
    (lambda t, p: t == "hashing" and ("lookup" in p or "membership" in p), "Hash-map lookup"),
    (lambda t, p: t == "hashing" and "prefix sum" in p, "Prefix sum + hashing"),
    (lambda t, p: t == "arrays" and "prefix" in p, "Prefix sums"),
    (lambda t, p: t == "arrays" and "two-pointer" in p, "Two-pointer (array)"),
    (lambda t, p: t == "arrays" and "cyclic sort" in p, "Cyclic sort / in-place index mapping"),
    (lambda t, p: t == "arrays" and "rotation" in p, "In-place array rotation"),
    (lambda t, p: t == "two-pointer" and "opposite-direction" in p, "Two-pointer (opposite-direction)"),
    (lambda t, p: t == "two-pointer" and ("same-direction" in p or "read/write" in p or "greedy" in p), "Two-pointer (same-direction)"),
    (lambda t, p: t == "two-pointer" and ("dutch" in p or "3-way" in p or "partition" in p), "Two-pointer (partitioning)"),
    (lambda t, p: t == "binary-search" and "answer space" in p, "Binary search on answer space"),
    (lambda t, p: t == "binary-search", "Binary-search boundaries"),
    (lambda t, p: t == "recursion" and "backtracking" in p, "Backtracking"),
    (lambda t, p: t == "recursion", "Recursion base cases"),
    (lambda t, p: t == "trees" and ("dfs" in p or "traversal" in p or "recursion" in p), "Tree DFS recursion"),
    (lambda t, p: t == "trees" and "bfs" in p, "Tree BFS / level order"),
    (lambda t, p: t == "graphs" and "grid" in p and "bfs" in p, "Grid BFS"),
    (lambda t, p: t == "graphs" and "grid" in p and "dfs" in p, "Grid DFS / flood fill"),
    (lambda t, p: t == "graphs" and ("bfs" in p or "shortest path" in p or "dijkstra" in p), "Graph shortest paths"),
    (lambda t, p: t == "graphs" and ("dfs" in p or "cycle" in p or "topological" in p), "Graph DFS / cycle detection"),
    (lambda t, p: t == "heaps", "Heap / top-K selection"),
    (lambda t, p: t == "stacks" and "monotonic" in p, "Monotonic stack"),
    (lambda t, p: t == "stacks", "Stack-based simulation"),
    (lambda t, p: t == "queues" and "monotonic" in p, "Monotonic queue/deque"),
    (lambda t, p: t == "queues", "Queue simulation"),
    (lambda t, p: t == "sorting" and "divide" in p, "Divide and conquer sorting"),
    (lambda t, p: t == "sorting", "Sorting fundamentals"),
    (lambda t, p: t == "dynamic-programming" and "knapsack" in p, "Knapsack DP"),
    (lambda t, p: t == "dynamic-programming" and "1d" in p, "1D dynamic programming"),
    (lambda t, p: t == "dynamic-programming" and "2d" in p, "2D dynamic programming"),
    (lambda t, p: t == "dynamic-programming", "Dynamic programming"),
    # New 16th topic (see docs/50-day-curriculum.md's Greedy addition).
    # Every problem seeded with topic="greedy" lands in one family
    # regardless of its specific pattern text -- there's no sub-family
    # split the way two-pointer/DP get, since the curriculum only needs
    # one Greedy concept lesson to cover Easy through Complex.
    (lambda t, p: t == "greedy", "Greedy"),
]


def pattern_family_for(topic: str, pattern: str) -> str:
    t = (topic or "").strip().lower()
    p = (pattern or "").strip().lower()
    for predicate, family in _RULES:
        if predicate(t, p):
            return family
    readable_topic = t.replace("-", " ") or "general"
    return f"General {readable_topic}"


# The one DB-touching function in an otherwise pure module -- kept here
# rather than duplicated in app.py and logic/practice_session.py (both
# need it, and practice_session.py can't import from app.py without a
# cycle) because it's really the same normalization job as
# pattern_family_for: turning a (topic, pattern) signal into one settled
# name, just resolved one step further into an actual concept_lessons row.
#
# This is the EXACT reverse of app.py's _related_problems_for_concept, so
# it reuses that function's own matching rule rather than inventing a
# second one: a lesson "covers" a (topic, pattern_family) pair when
# lesson.topic matches AND (lesson.pattern_family IS NULL, meaning the
# lesson covers the whole topic -- kind is 'topic' vs 'pattern' as
# content categorization, it is NOT part of this match -- OR
# lesson.pattern_family equals the family exactly, never fuzzily). When
# more than one lesson covers a topic, the one with a matching specific
# pattern_family wins over a whole-topic one, same preference order
# _related_problems_for_concept's narrowing implies. Returns None --
# never a guess -- when nothing covers it, so every caller can simply
# omit the suggestion rather than link somewhere that doesn't fit.
def concept_lesson_for_family(conn, topic, pattern_family):
    if not topic:
        return None
    row = conn.execute(
        """SELECT slug, title FROM concept_lessons
           WHERE topic = ? AND (pattern_family IS NULL OR pattern_family = ?)
           ORDER BY CASE WHEN pattern_family = ? THEN 0 ELSE 1 END
           LIMIT 1""",
        (topic, pattern_family, pattern_family),
    ).fetchone()
    return dict(row) if row else None
