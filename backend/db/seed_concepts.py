"""
Concept-lesson content for the teaching system (see schema.sql's
concept_lessons/concept_checkpoints/concept_practice_exercises tables).

This is a PILOT: two lessons -- 'arrays' (topic) and 'two-pointers'
(pattern) -- chosen because they're the curriculum's own first topic and
first pattern (days 8, 13, 14; see docs/45-day-curriculum.md), so the
teaching system plugs directly into an existing, already-taught sequence
rather than sitting off to the side. Once reviewed, the same shape
(CONCEPT_LESSONS / CONCEPT_CHECKPOINTS / CONCEPT_PRACTICE_EXERCISES, one
dict per lesson keyed by slug) extends to the rest of the curriculum's
topics without any schema or code change -- see docs/decisions.md
"Teaching system content architecture".

walkthrough_frames is a hand-authored, verified-by-hand trace of the
walkthrough_code's REAL behavior on the given input (not invented output)
-- each frame is a {caption, locals} pair rendered by
ConceptWalkthrough.jsx, which reuses ArrayPointerView the same way the
real per-user-code tracer does, but from this static authored list, never
from sys.settrace. That is the whole point: a controlled example for
teaching, kept structurally separate from the trace-your-own-code system.
"""

CONCEPT_LESSONS = [
    dict(
        slug="arrays",
        kind="topic",
        topic="arrays",
        pattern_family=None,
        title="Arrays: the foundation",
        display_order=1,
        estimated_minutes=15,
        summary="What a Python list actually is, how indexing and traversal work, and the in-place-modification "
                "habit almost every array problem builds on.",
        prerequisite_slugs="",
        what_markdown=(
            "An array (Python's `list`) is a sequence of values you reach by position -- `arr[0]` is the first "
            "element, `arr[len(arr) - 1]` is the last. Under the hood a Python list is a resizable array of "
            "references: indexing and appending are fast (`O(1)`), but inserting or deleting in the middle means "
            "shifting every element after it (`O(n)`)."
        ),
        why_markdown=(
            "Arrays are the single most common structure in interview problems -- directly, or as the backbone of "
            "strings, hash maps, stacks, and sliding windows. Nearly everything else in this curriculum assumes "
            "you're fluent with indexing and traversal first."
        ),
        recognize_markdown=(
            "You're already reaching for array thinking whenever a problem gives you an ordered sequence and asks "
            "you to look at, compare, or rearrange its elements by position -- \"find the largest\", \"reverse "
            "this\", \"remove every occurrence of X\". The recurring question worth asking is: do I need a new "
            "list, or can I get away with rewriting this one in place?"
        ),
        intuition_markdown=(
            "Two ideas cover most of what you need before the harder patterns (two pointers, sliding window, "
            "prefix sums) make sense. First: traversal is just visiting `arr[0]` through `arr[len(arr)-1]` in "
            "order -- `for x in arr` when you don't need the index, `for i, x in enumerate(arr)` when you do. "
            "Second: in-place modification means writing new values back into the same list instead of building a "
            "second one, which is what \"O(1) extra space\" means in an interview -- you're allowed the array "
            "you were given, not a copy of it."
        ),
        walkthrough_intro_markdown=(
            "Here's in-place modification in action: removing consecutive duplicates from a sorted array without "
            "allocating a new one. Two index variables do the work -- `read` scans forward looking at every "
            "element, `write` marks where the next value we're keeping should go. `write` never gets ahead of "
            "`read`, so it's always safe to write into a slot `read` has already passed."
        ),
        walkthrough_code=(
            "def remove_duplicates(arr):\n"
            "    write = 1\n"
            "    for read in range(1, len(arr)):\n"
            "        if arr[read] != arr[write - 1]:\n"
            "            arr[write] = arr[read]\n"
            "            write += 1\n"
            "    return write  # arr[:write] is the deduped result"
        ),
        walkthrough_frames=[
            dict(caption="write=1, read=1. arr[read]=1 equals arr[write-1]=arr[0]=1 -- a duplicate. Skip it; write doesn't move.",
                 locals={"arr": [1, 1, 2, 2, 3, 3, 3, 4], "write": 1, "read": 1}),
            dict(caption="read=2. arr[read]=2 differs from arr[write-1]=arr[0]=1 -- a new value. Copy it to arr[write], then advance write.",
                 locals={"arr": [1, 1, 2, 2, 3, 3, 3, 4], "write": 1, "read": 2}),
            dict(caption="arr[1] is now 2. read=3: arr[read]=2 equals arr[write-1]=arr[1]=2 -- duplicate, skip.",
                 locals={"arr": [1, 2, 2, 2, 3, 3, 3, 4], "write": 2, "read": 3}),
            dict(caption="read=4. arr[read]=3 differs from arr[write-1]=arr[1]=2 -- new value. Copy to arr[write], advance write.",
                 locals={"arr": [1, 2, 2, 2, 3, 3, 3, 4], "write": 2, "read": 4}),
            dict(caption="arr[2] is now 3. read=5 and read=6 are also 3 -- both skipped as duplicates of arr[write-1]=arr[2]=3.",
                 locals={"arr": [1, 2, 3, 2, 3, 3, 3, 4], "write": 3, "read": 5}),
            dict(caption="read=7. arr[read]=4 differs from arr[write-1]=arr[2]=3 -- new value. Copy to arr[write], advance write.",
                 locals={"arr": [1, 2, 3, 2, 3, 3, 3, 4], "write": 3, "read": 7}),
            dict(caption="write is now 4 and the loop ends. arr[:4] = [1, 2, 3, 4] is the deduped result -- everything from index 4 on is leftover, no longer meaningful.",
                 locals={"arr": [1, 2, 3, 4, 3, 3, 3, 4], "write": 4, "read": 7}),
        ],
        common_mistakes_markdown=(
            "Mutating a list while iterating over it directly (`for x in arr: arr.remove(x)`) -- the iterator "
            "gets confused about positions as the list shrinks underneath it; iterate by index instead when the "
            "list itself is changing. Confusing reassignment with in-place mutation -- `arr = arr + [x]` builds a "
            "brand-new list, `arr.append(x)` mutates the existing one; if a caller is holding the old reference, "
            "only the second one is visible to them. And aliasing: `b = a` does not copy the list -- `b` and `a` "
            "point at the same one, so writes through either name affect both."
        ),
        complexity_markdown=(
            "Indexing (`arr[i]`) and appending are `O(1)`. Inserting or deleting at an arbitrary index is `O(n)` "
            "because everything after it has to shift. A full traversal is always `O(n)`. Keep this in your head "
            "when a brute-force idea involves repeated inserts/deletes in the middle of a list inside a loop -- "
            "that's a hidden `O(n^2)`."
        ),
    ),
    dict(
        slug="two-pointers",
        kind="pattern",
        topic="two-pointer",
        pattern_family=None,
        title="Two pointers",
        display_order=1,
        estimated_minutes=20,
        summary="Replace a nested loop with two indices moving through the array once -- the highest-leverage "
                "pattern for turning an O(n^2) brute force into O(n).",
        prerequisite_slugs="arrays",
        what_markdown=(
            "Two pointers means tracking two index variables into the same sequence instead of one, and moving "
            "them according to a rule instead of trying every pair. The two variables can start at opposite ends "
            "and move toward each other (**opposite-direction**), or both start near the beginning and move "
            "forward at different times (**same-direction**) -- same core idea, different shape of problem."
        ),
        why_markdown=(
            "The brute-force instinct for \"find a pair/segment that satisfies some condition\" is a nested loop: "
            "try every `(i, j)` pair, `O(n^2)`. Two pointers gets the same answer in one pass, `O(n)`, by "
            "exploiting structure in the data (usually sortedness) so that moving a pointer can only make the "
            "answer better in one direction -- you never need to backtrack and re-check a pair you've already "
            "ruled out."
        ),
        recognize_markdown=(
            "Reach for two pointers when several of these line up: the input is sorted, or can cheaply be made "
            "sorted, or has a monotonic property. You're comparing elements from two different positions in the "
            "same sequence, not looking things up by value (that's more often a hash-map job). You're looking for "
            "a pair, triplet, or contiguous span that meets some condition. And your first instinct was a nested "
            "loop, but you notice that moving one side always moves the answer in a predictable direction -- that "
            "predictability is what lets you drop a whole dimension of brute force."
        ),
        intuition_markdown=(
            "**Opposite-direction** (sorted array, looking for a pair): start `left` at 0 and `right` at the end. "
            "If the pair's current value is too big, the only way to shrink it is to move `right` inward "
            "(dropping the largest element under consideration); if it's too small, move `left` inward. Because "
            "the array is sorted, this is safe -- you're never skipping over a valid pair that involves the "
            "elements you're leaving behind. **Same-direction** (e.g. containers, read/write compaction): both "
            "pointers start near the beginning, but one (often called `left` or `write`) marks \"the last position "
            "known to be good\" while the other (`right` or `read`) scans ahead looking for the next thing worth "
            "keeping or comparing -- the first pointer only moves when the scanning one finds something that "
            "matters."
        ),
        walkthrough_intro_markdown=(
            "Trace `two_sum_sorted([1, 2, 4, 7, 11, 15], 15)` -- opposite-direction two pointers on a sorted "
            "array, looking for a pair that sums to the target. Watch which pointer moves at each step, and why."
        ),
        walkthrough_code=(
            "def two_sum_sorted(nums, target):\n"
            "    left, right = 0, len(nums) - 1\n"
            "    while left < right:\n"
            "        total = nums[left] + nums[right]\n"
            "        if total == target:\n"
            "            return [left, right]\n"
            "        elif total < target:\n"
            "            left += 1\n"
            "        else:\n"
            "            right -= 1\n"
            "    return []"
        ),
        walkthrough_frames=[
            dict(caption="left=0, right=5. sum = nums[0] + nums[5] = 1 + 15 = 16 -- too big (target 15). The only way to shrink the sum is to drop the larger endpoint, so move right inward.",
                 locals={"nums": [1, 2, 4, 7, 11, 15], "target": 15, "left": 0, "right": 5}),
            dict(caption="left=0, right=4. sum = 1 + 11 = 12 -- too small now. Move left forward to consider a bigger value on that side.",
                 locals={"nums": [1, 2, 4, 7, 11, 15], "target": 15, "left": 0, "right": 4}),
            dict(caption="left=1, right=4. sum = 2 + 11 = 13 -- still too small. Move left forward again.",
                 locals={"nums": [1, 2, 4, 7, 11, 15], "target": 15, "left": 1, "right": 4}),
            dict(caption="left=2, right=4. sum = 4 + 11 = 15 -- match. Return [2, 4]. Notice left only ever moved right and right only ever moved left -- each pointer crosses the array at most once, which is where the O(n) comes from.",
                 locals={"nums": [1, 2, 4, 7, 11, 15], "target": 15, "left": 2, "right": 4}),
        ],
        common_mistakes_markdown=(
            "Running opposite-direction two pointers on unsorted data -- the \"moving a pointer only helps in one "
            "direction\" guarantee depends on sortedness; without it the technique is just wrong, not slower. "
            "Moving the wrong pointer -- e.g. in the classic \"container with most water\" problem, moving the "
            "**taller** wall's pointer can only ever shrink the area (width drops, height is capped by the shorter "
            "wall either way), so only the shorter wall's pointer is worth moving. Off-by-one on the loop "
            "condition (`while left < right` vs `<=`) -- with `<=` a single element can pair with itself. And "
            "forgetting the loop can end without finding anything -- always decide what to return in that case."
        ),
        complexity_markdown=(
            "`O(n)` time: `left` only ever increases and `right` only ever decreases, and the loop stops the "
            "moment they meet, so between them they take at most `n` steps total -- not `n` steps **each** nested "
            "inside another `n`. `O(1)` extra space: no new data structure, just two integers. Compare that to "
            "the nested-loop brute force's `O(n^2)` time for the same answer."
        ),
    ),
]

CONCEPT_CHECKPOINTS = {
    "arrays": [
        dict(kind="predict_output",
             prompt_markdown="What does this print?",
             code="arr = [10, 20, 30]\nfor x in arr:\n    x = x * 2\nprint(arr)",
             choices_json=None,
             correct_answer="[10, 20, 30]",
             explanation_markdown="`x` is a fresh local variable bound to each value in turn -- reassigning `x` "
                                   "never writes back into `arr`. To actually change the list you need to write "
                                   "through an index: `for i in range(len(arr)): arr[i] *= 2`."),
        dict(kind="spot_bug",
             prompt_markdown="This is meant to remove every 3 from the list. What's wrong with it?",
             code="arr = [1, 3, 3, 2, 3, 4]\nfor x in arr:\n    if x == 3:\n        arr.remove(x)\nprint(arr)",
             choices_json=None,
             correct_answer="Mutating the list (arr.remove) while iterating over it directly skips elements, "
                             "because the iterator's position and the list's indices shift out of sync as items "
                             "are removed.",
             explanation_markdown="`arr.remove(x)` shifts every later element one index to the left, but the "
                                   "for-loop's internal position doesn't rewind -- so the element that just slid "
                                   "into the spot you already passed gets skipped. Run it and you'll see one of "
                                   "the 3s survives. Fix: iterate over a copy (`for x in list(arr)`), or build a "
                                   "new list, or walk by index from the end."),
    ],
    "two-pointers": [
        dict(kind="choose_pattern",
             prompt_markdown="You're given a sorted array and need to find whether any two numbers in it sum to "
                              "exactly a target value. Which approach fits best?",
             code=None,
             choices_json=[
                 "Nested loop checking every pair, O(n^2)",
                 "Two pointers starting at both ends, O(n)",
                 "Recursion with memoization",
                 "Sort it again first, then binary search each element",
             ],
             correct_answer="Two pointers starting at both ends, O(n)",
             explanation_markdown="It's already sorted and you're looking for a pair -- exactly the opposite-"
                                   "direction two-pointer setup. A nested loop would also work but throws away "
                                   "the sortedness you were handed for free; re-sorting is redundant work."),
        dict(kind="spot_bug",
             prompt_markdown="This is meant to find the container with the most water (classic two-pointer "
                              "problem) but returns the wrong (too-small) answer on some inputs. What's the bug?",
             code=(
                 "def max_area(height):\n"
                 "    left, right = 0, len(height) - 1\n"
                 "    best = 0\n"
                 "    while left < right:\n"
                 "        area = (right - left) * min(height[left], height[right])\n"
                 "        best = max(best, area)\n"
                 "        if height[left] > height[right]:\n"
                 "            left += 1\n"
                 "        else:\n"
                 "            right -= 1\n"
                 "    return best"
             ),
             choices_json=None,
             correct_answer="It moves the TALLER wall's pointer inward (height[left] > height[right] moves left) "
                             "instead of the shorter one -- that can only ever shrink the area, since the width "
                             "always drops and the height was already capped by the shorter wall.",
             explanation_markdown="The condition is backwards: it should move the pointer at the **shorter** wall "
                                   "(`height[left] < height[right]: left += 1`). Moving the taller wall's pointer "
                                   "keeps the same limiting (shorter) height while shrinking the width -- the "
                                   "area can only go down or stay the same, so a genuinely better answer can "
                                   "never be found that way."),
        dict(kind="predict_output",
             prompt_markdown="Trace this by hand -- what does it return?",
             code="def two_sum_sorted(nums, target):\n"
                  "    left, right = 0, len(nums) - 1\n"
                  "    while left < right:\n"
                  "        total = nums[left] + nums[right]\n"
                  "        if total == target:\n"
                  "            return [left, right]\n"
                  "        elif total < target:\n"
                  "            left += 1\n"
                  "        else:\n"
                  "            right -= 1\n"
                  "    return []\n\n"
                  "print(two_sum_sorted([1, 2, 3, 5, 8], 10))",
             choices_json=None,
             correct_answer="[1, 4]",
             explanation_markdown="1+8=9 (too small, left+=1) -> 2+8=10, match at left=1, right=4. Returns "
                                   "[1, 4] -- the INDICES of the pair (values 2 and 8), not the values themselves."),
        dict(kind="complexity",
             prompt_markdown="Once an array of size n is already sorted, what's the time complexity of the "
                              "opposite-direction two-pointer scan over it?",
             code=None,
             choices_json=None,
             correct_answer="O(n)",
             explanation_markdown="left only ever increases, right only ever decreases, and the loop stops the "
                                   "moment they meet -- so between them the pointers take at most n steps total, "
                                   "not n steps each nested inside another n. (Sorting first, if it isn't already "
                                   "sorted, adds O(n log n) on top -- worth naming out loud in an interview.)"),
    ],
}

CONCEPT_PRACTICE_EXERCISES = {
    "arrays": [
        dict(prompt_markdown="Write `is_palindrome(arr)` that returns True if the list reads the same forwards "
                              "and backwards -- without using slicing (`arr[::-1]`) or `reversed()`. Use "
                              "in-place-style index comparison instead.",
             starter_code="def is_palindrome(arr):\n    # compare arr[i] against arr[len(arr) - 1 - i]\n    pass",
             solution_code=(
                 "def is_palindrome(arr):\n"
                 "    for i in range(len(arr) // 2):\n"
                 "        if arr[i] != arr[len(arr) - 1 - i]:\n"
                 "            return False\n"
                 "    return True"
             ),
             hint_markdown="You only need to check the first half of the list against its mirrored position -- "
                            "once i passes the midpoint you'd just be re-checking pairs you already checked."),
    ],
    "two-pointers": [
        dict(prompt_markdown="Given a sorted array `nums` and an integer `k`, write `has_pair_with_diff(nums, k)` "
                              "that returns True if any two elements differ by exactly `k` (k >= 0). Use two "
                              "pointers -- don't check every pair.",
             starter_code="def has_pair_with_diff(nums, k):\n    # both pointers start near the beginning here --\n"
                          "    # this is a same-direction variant, not opposite-direction\n    pass",
             solution_code=(
                 "def has_pair_with_diff(nums, k):\n"
                 "    left, right = 0, 1\n"
                 "    while right < len(nums):\n"
                 "        diff = nums[right] - nums[left]\n"
                 "        if diff == k:\n"
                 "            return True\n"
                 "        elif diff < k:\n"
                 "            right += 1\n"
                 "        else:\n"
                 "            left += 1\n"
                 "    return False"
             ),
             hint_markdown="This one isn't opposite-direction -- both pointers start near the front. If the gap "
                            "between them is too small, which pointer should move to make it bigger?"),
    ],
}
