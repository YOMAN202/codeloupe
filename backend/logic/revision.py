"""
Adaptive spaced-revision scheduling, per docs/problem-roadmap.md: base
ladder of 1/3/7/14 days, compressed when an attempt needed hints/failed,
advanced at the normal pace (or slightly slower) when solved
independently. Deliberately simple -- see docs/decisions.md on why a
full SM-2-style algorithm is out of scope.
"""
import datetime

BASE_INTERVALS_DAYS = [1, 3, 7, 14]


def compute_next_schedule(passed: bool, is_independent: bool, current_interval_index: int):
    """Returns (new_interval_index, next_due_date_iso, result_label)."""
    today = datetime.date.today()

    if not passed:
        return 0, (today + datetime.timedelta(days=1)).isoformat(), "failed"

    if is_independent:
        new_index = min(current_interval_index + 1, len(BASE_INTERVALS_DAYS) - 1)
        days = BASE_INTERVALS_DAYS[new_index]
        return new_index, (today + datetime.timedelta(days=days)).isoformat(), "independent"

    # Passed, but with hints or a revealed solution: compress the ladder --
    # don't advance, and use half the current interval (min 1 day).
    days = max(1, BASE_INTERVALS_DAYS[current_interval_index] // 2)
    return current_interval_index, (today + datetime.timedelta(days=days)).isoformat(), "assisted"
