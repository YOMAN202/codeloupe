"""
Adaptive "Today's Session" recommender.

Deliberately NOT a new subsystem: every signal here is read from data that
already exists elsewhere (revision_schedule, the mistakes table, the same
topic-weakness query /api/progress already runs, plain problem/attempt
counts) -- this module just combines them into one small, explained list.
Every item carries a plain-language `reason` so a recommendation is never
a black box, and this is purely additive: nothing here locks the learner
into a path or hides any other problem/lesson from normal navigation.
"""
import datetime

from .pattern_families import pattern_family_for

MAX_ITEMS = 4


def _first_unsolved_in_family(conn, family):
    rows = conn.execute(
        """SELECT p.slug, p.title, p.topic, p.pattern FROM problems p
           WHERE NOT EXISTS (SELECT 1 FROM attempts a WHERE a.problem_id = p.id AND a.passed = 1)"""
    ).fetchall()
    for r in rows:
        if pattern_family_for(r["topic"], r["pattern"]) == family:
            return r
    return None


def build_practice_session(conn):
    today = datetime.date.today().isoformat()
    items = []
    seen = set()

    def add(slug, title, kind, reason):
        if slug in seen:
            return
        seen.add(slug)
        items.append({"slug": slug, "title": title, "kind": kind, "reason": reason})

    # 1. Revision: earliest problem due today or overdue -- reuses the same
    # revision_schedule data /api/progress's "problems_due_for_revision" does.
    due = conn.execute(
        """SELECT p.slug, p.title, rs.next_due_date, rs.last_result
           FROM revision_schedule rs JOIN problems p ON rs.problem_id = p.id
           WHERE rs.next_due_date <= ? ORDER BY rs.next_due_date LIMIT 1""",
        (today,),
    ).fetchone()
    if due:
        when = "today" if due["next_due_date"] == today else f"since {due['next_due_date']}"
        add(due["slug"], due["title"], "revision",
            f"Revision recommended -- due {when} (last result: {due['last_result']}).")

    # Shared groundwork for slots 2 and 3: classified mistakes bucketed by
    # pattern family (see logic/pattern_families.py).
    mistake_rows = conn.execute(
        """SELECT p.topic, p.pattern, m.category
           FROM mistakes m JOIN problems p ON m.problem_id = p.id
           WHERE m.category IS NOT NULL"""
    ).fetchall()
    pair_counts, family_counts = {}, {}
    for r in mistake_rows:
        family = pattern_family_for(r["topic"], r["pattern"])
        family_counts[family] = family_counts.get(family, 0) + 1
        key = (family, r["category"])
        pair_counts[key] = pair_counts.get(key, 0) + 1

    # 2. A problem tied to a RECURRING mistake -- the same (pattern family,
    # category) pair showing up 2+ times, not a one-off.
    recurring = [(k, c) for k, c in pair_counts.items() if c >= 2]
    if recurring:
        (family, category), count = max(recurring, key=lambda kv: kv[1])
        candidate = _first_unsolved_in_family(conn, family)
        if candidate:
            add(candidate["slug"], candidate["title"], "recurring_mistake",
                f"Recommended because '{category}' has come up {count} times in {family}.")

    # 3. A problem targeting a weak topic or pattern. Pattern-level (more
    # specific) is preferred when there's mistake-journal data to support
    # it; falls back to the existing topic-level weakness signal otherwise
    # -- this NEVER replaces topic-level tracking, it's a second lens on
    # the same underlying attempts.
    if family_counts:
        weak_family = max(family_counts, key=family_counts.get)
        candidate = _first_unsolved_in_family(conn, weak_family)
        if candidate:
            add(candidate["slug"], candidate["title"], "weak_pattern",
                f"Recommended because you've had {family_counts[weak_family]} mistake(s) classified under {weak_family}.")
    if len(items) < 3:
        weak_topic_row = conn.execute(
            """SELECT p.topic, COUNT(*) c FROM attempts a JOIN problems p ON a.problem_id = p.id
               WHERE a.passed = 0 OR a.hints_used > 0 GROUP BY p.topic ORDER BY c DESC LIMIT 1"""
        ).fetchone()
        if weak_topic_row:
            candidate = conn.execute(
                """SELECT slug, title FROM problems p WHERE topic = ?
                   AND NOT EXISTS (SELECT 1 FROM attempts a WHERE a.problem_id = p.id AND a.passed = 1)
                   ORDER BY day, id LIMIT 1""",
                (weak_topic_row["topic"],),
            ).fetchone()
            if candidate:
                add(candidate["slug"], candidate["title"], "weak_topic",
                    f"Recommended because {weak_topic_row['topic']} has been your most-struggled-with topic recently.")

    # 4. A new problem appropriate to current progress: first untouched
    # Core-tier problem, in curriculum day order.
    new_candidate = conn.execute(
        """SELECT slug, title, day FROM problems p WHERE path_tier = 'core'
           AND NOT EXISTS (SELECT 1 FROM attempts a WHERE a.problem_id = p.id)
           ORDER BY day, id LIMIT 1"""
    ).fetchone()
    if new_candidate:
        add(new_candidate["slug"], new_candidate["title"], "new",
            f"A new Core Path problem matching where you are (day {new_candidate['day']}).")

    return items[:MAX_ITEMS]
