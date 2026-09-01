"""
Block-level curriculum structure: the recommended sequential order plus a
coarse prerequisite graph, used so navigation can be non-linear (jump to
any day, mark it known/skipped) while still SHOWING a learner what's
recommended background for an advanced topic, per the "recommended path,
not a locked sequence" requirement (see docs/decisions.md).

Deliberately block-level, not lesson-level: a precise per-lesson
dependency graph (45 nodes, hand-authored edges) would take real effort
to get right and mostly wouldn't change what's shown to the learner
(you'd still be pointed at "the earlier stuff"). Block-level prerequisites
capture the real pedagogical structure -- e.g. trees/graphs need
recursion, DP needs recursion -- without that cost. This is a
recommendation surfaced in the UI, never an access gate.
"""

# Order matches the curriculum's block sequence (see db/seed_lessons.py).
BLOCK_ORDER = [
    "Python Fundamentals",
    "Arrays, Strings, Hashing",
    "Sorting, Binary Search, Recursion",
    "Linked Lists, Stacks, Queues, Trees",
    "Heaps, Graphs",
    "Dynamic Programming",
    "Revision & Mock Interviews",
]

# block -> list of blocks it recommends as background. Not transitive
# closure by design (each entry lists DIRECT prerequisites only); the API
# layer walks this to build the full recommended set for display.
BLOCK_PREREQUISITES = {
    "Python Fundamentals": [],
    "Arrays, Strings, Hashing": ["Python Fundamentals"],
    "Sorting, Binary Search, Recursion": ["Arrays, Strings, Hashing"],
    "Linked Lists, Stacks, Queues, Trees": ["Sorting, Binary Search, Recursion"],
    "Heaps, Graphs": ["Linked Lists, Stacks, Queues, Trees"],
    "Dynamic Programming": ["Sorting, Binary Search, Recursion"],
    "Revision & Mock Interviews": [
        "Arrays, Strings, Hashing", "Sorting, Binary Search, Recursion",
        "Linked Lists, Stacks, Queues, Trees", "Heaps, Graphs", "Dynamic Programming",
    ],
}


def all_prerequisite_blocks(block: str) -> list:
    """Direct prerequisites only (not transitive) -- e.g. Heaps/Graphs lists
    Linked-Lists-block, not also Sorting/Recursion beneath it. A learner
    who already knows the immediate prerequisite doesn't need every
    ancestor spelled out."""
    return list(BLOCK_PREREQUISITES.get(block, []))
