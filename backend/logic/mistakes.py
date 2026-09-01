"""
Mistake journal classification.

Deliberately conservative: the automated classifier NEVER claims the
top-tier "observed/confirmed" confidence for a mistake CATEGORY. Mapping
a raw execution fact (an exception type, which test case failed, a
truncated trace) onto one of the named DSA mistake categories below is
always an inference, even when it's a strong one -- so every automatic
classification is tagged "likely_issue" at most, or left unclassified
entirely when no rule confidently applies. "Unclassified is better than
an inaccurate classification" (the user's own words) is the guiding
constraint here, not a throwaway line.

The four confidence levels, and who assigns them:
  - observed_confirmed: reserved for facts that are directly read off
    execution/test results with no interpretation at all (used for the
    supporting `evidence` string, and available for a future rule that's
    ever this certain about a category -- none of the current rules are).
  - likely_issue: the classifier's best guess at a category, always
    paired with the fact(s) that produced it.
  - user_confirmed: the learner reviewed a likely_issue suggestion and
    confirmed it's correct (PUT /api/mistakes/<id> with the same category).
  - manually_selected: the learner picked a category themselves, either
    overriding a suggestion or classifying something the system left
    unclassified.

This module only classifies WHAT KIND of mistake it might be, from
evidence the frontend already has in hand at attempt-log time (the /run
result) -- it never re-executes code or calls out to the tracer, keeping
classification a cheap, synchronous part of logging an attempt.
"""

# Fixed category list. A category outside this list is never stored --
# better to leave a mistake unclassified than invent a new label on the fly.
MISTAKE_CATEGORIES = [
    "Off-by-one errors",
    "Missed edge cases",
    "Incorrect pointer movement",
    "Incorrect base case",
    "Incorrect data-structure usage",
    "Pattern recognition difficulty",
    "Logic errors",
    "Complexity misunderstanding",
    "Recursion issues",
    "Boundary-condition mistakes",
]

CONFIDENCE_LEVELS = ["observed_confirmed", "likely_issue", "user_confirmed", "manually_selected"]

_POINTER_TOPICS = {"linked-lists", "trees", "graphs"}


def _is_edge_shaped(value):
    """A single arg value that looks like a deliberately extreme/edge input."""
    if value is None:
        return True
    if isinstance(value, (list, str, dict, tuple)) and len(value) == 0:
        return True
    if isinstance(value, (list, tuple)) and len(value) == 1:
        return True
    if isinstance(value, (int, float)) and not isinstance(value, bool) and value in (0, -1):
        return True
    return False


def classify_mistake(failure_context: dict, topic: str):
    """failure_context (built by the frontend from a /run response):
        {
          "crashed": bool,
          "first_failure": {"args": [...], "expected": ..., "actual": ..., "error": str|None} | None,
          "num_failed": int, "num_total": int,
        }
    topic: the problem's topic column (e.g. "linked-lists"), used only to
    disambiguate a couple of otherwise-ambiguous exception types.

    Returns (category: str|None, evidence: str|None). category is None
    ("unclassified") whenever no rule confidently applies -- this is a
    normal, expected, and honest outcome, not a fallback to avoid.
    """
    if not failure_context:
        return None, None

    if failure_context.get("crashed"):
        # A SyntaxError or an unhandled crash before the grading harness
        # could even run any case -- not really a DSA mistake category,
        # just "the code doesn't run yet."
        return None, "Submission didn't run (syntax error or crash before any test case executed)."

    first = failure_context.get("first_failure")
    if not first:
        return None, None

    error = (first.get("error") or "").strip()
    args = first.get("args") or []
    num_failed = failure_context.get("num_failed")
    num_total = failure_context.get("num_total")

    if error:
        exc_type = error.split(":", 1)[0].strip()
        if exc_type == "RecursionError":
            return "Recursion issues", f"Your code raised {error} -- recursion never reached its base case."
        if exc_type == "IndexError":
            return "Off-by-one errors", f"Your code raised {error} while running on input {args!r}."
        if exc_type == "KeyError":
            return "Incorrect data-structure usage", f"Your code raised {error} -- a lookup key wasn't where the code expected."
        if exc_type == "AttributeError" and topic in _POINTER_TOPICS:
            return "Incorrect pointer movement", f"Your code raised {error} -- likely followed a pointer/reference that was None."
        if exc_type == "TypeError":
            return "Logic errors", f"Your code raised {error} -- likely comparing or combining incompatible values."
        # Some other exception type we don't have a confident mapping for.
        return None, f"Your code raised {error}, but this doesn't map clearly onto one mistake category."

    # No exception -- a plain wrong answer. Look at the shape of the input
    # that failed.
    if any(_is_edge_shaped(a) for a in args):
        return "Missed edge cases", f"Failed specifically on an edge-shaped input ({args!r}) while other input sizes/shapes passed."

    if num_failed is not None and num_total and num_failed == num_total:
        return "Logic errors", "Every test case failed -- likely a problem with the overall approach rather than one edge case."

    # Fails some cases but not all, with no obviously edge-shaped input:
    # genuinely ambiguous. Guessing here (e.g. "off-by-one") without real
    # signal is exactly the overclaiming the user asked to avoid.
    return None, f"Failed on input {args!r} (and {num_failed or '?'} of {num_total or '?'} cases total) -- no confident pattern detected."
