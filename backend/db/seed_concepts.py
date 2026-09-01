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

    # ---- Batch 2 (Arrays/Strings/Hashing block, days 9-12) -----------------
    # Continues the pilot's own architecture and pacing: one topic or
    # pattern per curriculum day-cluster, hung off the SAME problems.topic/
    # pattern_family vocabulary the pilot established, reviewed as its own
    # batch before continuing further down the curriculum. See
    # docs/decisions.md "Teaching system expansion: batch 2".
    dict(
        slug="prefix-sums",
        kind="pattern",
        topic="arrays",
        pattern_family="Prefix sums",
        title="Prefix sums",
        display_order=2,
        estimated_minutes=15,
        summary="Precompute cumulative sums once so any range-sum query afterward is O(1) instead of "
                "re-adding the range every time.",
        prerequisite_slugs="arrays",
        what_markdown=(
            "A prefix-sum array stores running totals: `prefix[i]` is the sum of `arr[0]` through `arr[i]`. "
            "Once you have it, the sum of any contiguous range `arr[left..right]` is a single subtraction -- "
            "`prefix[right] - prefix[left - 1]` -- instead of walking the range and adding it up again."
        ),
        why_markdown=(
            "\"Precompute now, pay less later\" is one of the most common optimization shapes in interview "
            "problems. If you're going to ask the same kind of question (a range sum) many times against the "
            "same fixed array, doing `O(n)` work once beats doing `O(n)` work on every single query."
        ),
        recognize_markdown=(
            "Reach for prefix sums when you see repeated range-sum queries on a fixed array, or when \"sum of a "
            "contiguous subarray\" shows up more than once against the same data. A running/cumulative total is "
            "often already the natural way you'd describe the problem out loud (\"how much has accumulated by "
            "this point?\"). A related variant -- prefix sums combined with a hash map, remembering every prefix "
            "total seen so far rather than just the running one -- turns \"does some contiguous subarray sum to "
            "exactly k?\" into one pass too; see the Hashing lesson's \"prefix sum + hashmap\" note."
        ),
        intuition_markdown=(
            "Build the prefix array once: `prefix[0] = arr[0]`, then `prefix[i] = prefix[i-1] + arr[i]` for "
            "everything after. Answering a range query is then just `prefix[right] - prefix[left - 1]` -- "
            "subtracting off everything before `left` leaves exactly the range you want -- with a special case "
            "for `left == 0` (there's nothing before it to subtract). The same running-total idea, applied "
            "column-by-column instead of cell-by-cell, is also what makes \"product of every element except "
            "this one\" solvable in one pass each direction (a prefix product times a suffix product)."
        ),
        walkthrough_intro_markdown=(
            "Build the prefix-sum array for `[3, 1, 4, 1, 5]`, then use it to answer a range query in O(1)."
        ),
        walkthrough_code=(
            "def build_prefix_sums(arr):\n"
            "    prefix = [0] * len(arr)\n"
            "    prefix[0] = arr[0]\n"
            "    for i in range(1, len(arr)):\n"
            "        prefix[i] = prefix[i - 1] + arr[i]\n"
            "    return prefix\n\n"
            "def range_sum(prefix, left, right):\n"
            "    if left == 0:\n"
            "        return prefix[right]\n"
            "    return prefix[right] - prefix[left - 1]"
        ),
        walkthrough_frames=[
            dict(caption="prefix[0]=arr[0]=3 (base case, already set). Now compute prefix[1] = prefix[0] + arr[1] = 3 + 1 = 4.",
                 locals={"arr": [3, 1, 4, 1, 5], "prefix": [3, 0, 0, 0, 0], "i": 1}),
            dict(caption="prefix[1]=4. Compute prefix[2] = prefix[1] + arr[2] = 4 + 4 = 8.",
                 locals={"arr": [3, 1, 4, 1, 5], "prefix": [3, 4, 0, 0, 0], "i": 2}),
            dict(caption="prefix[2]=8. Compute prefix[3] = prefix[2] + arr[3] = 8 + 1 = 9.",
                 locals={"arr": [3, 1, 4, 1, 5], "prefix": [3, 4, 8, 0, 0], "i": 3}),
            dict(caption="prefix[3]=9. Compute prefix[4] = prefix[3] + arr[4] = 9 + 5 = 14. The prefix array is done: [3, 4, 8, 9, 14].",
                 locals={"arr": [3, 1, 4, 1, 5], "prefix": [3, 4, 8, 9, 0], "i": 4}),
            dict(caption="Now any range sum is O(1): sum of arr[1..3] = prefix[3] - prefix[0] = 9 - 3 = 6 -- matches 1+4+1 directly, with no need to re-add the range.",
                 locals={"arr": [3, 1, 4, 1, 5], "prefix": [3, 4, 8, 9, 14]}),
        ],
        common_mistakes_markdown=(
            "Forgetting the `left == 0` special case in the range-sum formula -- `prefix[left - 1]` silently "
            "becomes `prefix[-1]` in Python (the LAST element, not zero), giving a wrong answer with no crash "
            "to warn you. Rebuilding the prefix array inside the query function instead of once up front -- that "
            "throws away the entire point of precomputing. And confusing the prefix array with the original one: "
            "`prefix[i]` is a running total, not `arr[i]`."
        ),
        complexity_markdown=(
            "`O(n)` time and `O(n)` space to build the prefix array once. Each range-sum query afterward is "
            "`O(1)`. Compare that to the naive approach of re-summing each queried range directly: `O(n)` per "
            "query, `O(qn)` total for `q` queries -- prefix sums turn repeated linear work into one linear "
            "precompute plus constant-time lookups."
        ),
    ),
    dict(
        slug="strings",
        kind="topic",
        topic="strings",
        pattern_family=None,
        title="Strings",
        display_order=1,
        estimated_minutes=15,
        summary="Python strings are sequences like lists -- almost every string problem reduces to either "
                "comparing characters or counting them.",
        prerequisite_slugs="arrays",
        what_markdown=(
            "A Python string is an ordered, indexable sequence of characters -- `s[0]`, slicing, `len(s)`, "
            "iteration all work exactly like a list. The one real difference: strings are **immutable**. "
            "`s[0] = 'x'` raises a `TypeError` -- there's no in-place character write. To \"modify\" a string "
            "you build a new one (directly, or via a list of characters joined at the end)."
        ),
        why_markdown=(
            "String problems are extremely common in interviews, and nearly all of them reduce to one of two "
            "shapes: **comparing characters** (is this a palindrome? are these two strings anagrams of each "
            "other?) or **counting characters** (which character appears most? build a frequency signature). "
            "Recognizing which shape you're in early cuts the problem down fast."
        ),
        recognize_markdown=(
            "Comparing-characters signals: a symmetric check (palindrome -- reads the same forwards and "
            "backwards), a same-letters-different-order check (anagram) -- these often want two pointers (from "
            "both ends, or expanding outward from a center) or a sorted/canonical form. Counting-characters "
            "signals: \"which character appears most/least,\" a frequency or multiset comparison, building a "
            "signature from a string to use as a lookup key -- these want the hashing patterns covered in the "
            "next lesson."
        ),
        intuition_markdown=(
            "Because strings are immutable, building one up with `result += c` inside a loop is a trap: every "
            "`+=` copies everything accumulated so far into a brand-new string, making an `n`-character loop do "
            "`O(n^2)` work in total, not `O(n)`. Collect characters into a list and `''.join(list)` once at the "
            "end instead. For comparing characters, one particularly useful technique is **expanding around a "
            "center**: to find the longest palindrome, try every possible center position and grow outward "
            "while the characters on both sides keep matching -- covering both odd-length palindromes (one "
            "character center) and even-length ones (a center between two characters)."
        ),
        walkthrough_intro_markdown=(
            "Trace `expand_around_center(\"babad\", 1, 1)` -- starting at the odd-length center on index 1 "
            "(the first 'a'), growing outward while the characters on both sides match."
        ),
        walkthrough_code=(
            "def expand_around_center(s, left, right):\n"
            "    while left >= 0 and right < len(s) and s[left] == s[right]:\n"
            "        left -= 1\n"
            "        right += 1\n"
            "    # the palindrome found is s[left+1 : right]\n"
            "    return s[left + 1:right]"
        ),
        walkthrough_frames=[
            dict(caption="Start at the center (odd length: left and right both point at the same index). s[1]==s[1] trivially -- expand outward.",
                 locals={"s": "babad", "left": 1, "right": 1}),
            dict(caption="s[0]='b', s[2]='b' -- match. Keep expanding.",
                 locals={"s": "babad", "left": 0, "right": 2}),
            dict(caption="left has gone out of bounds (-1, so no pointer chip shows for it) -- the while loop's bounds check stops the expansion. The palindrome is s[left+1:right] = s[0:3] = 'bab'.",
                 locals={"s": "babad", "right": 3}),
        ],
        common_mistakes_markdown=(
            "Building a string with `+=` in a loop instead of collecting into a list and joining once -- works, "
            "but silently `O(n^2)` instead of `O(n)` for long inputs. Checking `s[left] == s[right]` before "
            "confirming `left >= 0 and right < len(s)` -- Python's `and` short-circuits left to right, so the "
            "bounds check has to come first or you'll index out of range (or, worse, wrap around silently with a "
            "negative index). And only handling one of odd-length vs. even-length centers -- a real "
            "longest-palindrome solution tries both `(i, i)` and `(i, i+1)` as starting centers."
        ),
        complexity_markdown=(
            "Expand-around-center: `O(n)` possible centers, each expanding up to `O(n)` in the worst case, so "
            "`O(n^2)` time overall, `O(1)` extra space -- worse than the ideal `O(n)` but much better than "
            "checking all `O(n^2)` substrings individually for palindrome-ness (which would be `O(n^3)` total). "
            "Frequency-based comparisons (anagram checks, etc.) are `O(n)` time, `O(1)` space if the alphabet is "
            "a fixed size like lowercase English letters."
        ),
    ),
    dict(
        slug="hashing",
        kind="topic",
        topic="hashing",
        pattern_family=None,
        title="Hashing",
        display_order=1,
        estimated_minutes=18,
        summary="Trade space for time: a hash map/set turns \"have I seen this before?\" from an O(n) scan "
                "into an O(1) lookup -- the most common way to cut a nested loop down to one pass.",
        prerequisite_slugs="arrays",
        what_markdown=(
            "A hash map (`dict`) or hash set (`set`) computes a hash of each key to jump (roughly) straight to "
            "where it lives, instead of scanning to find it. That makes insert, lookup, and delete `O(1)` on "
            "average, versus `O(n)` to search a plain list for the same thing."
        ),
        why_markdown=(
            "A nested-loop brute force that asks \"does some pair or value exist elsewhere in this data\" is "
            "almost always improvable to one pass, because a hash map lets you remember what you've already "
            "seen instead of re-scanning for it every time. This is the single most common way an `O(n^2)` "
            "interview solution turns into an `O(n)` one."
        ),
        recognize_markdown=(
            "Two core shapes. **Lookup/membership** -- \"have I seen this value, or its complement/pair, "
            "before?\" Two Sum is the textbook case: for each number, check whether `target - number` was "
            "already seen. **Frequency/grouping** -- \"count occurrences\" or \"group things that share a "
            "computed key,\" e.g. counting characters, grouping strings by their sorted form, finding the top-K "
            "most frequent values. The tell for either: your brute force is checking \"does X exist elsewhere\" "
            "or \"how many times does X occur\" *inside a loop* -- both are exactly what a hash map remembers "
            "for free."
        ),
        intuition_markdown=(
            "For lookup: walk the data once, and for each element, FIRST check whether you already have what "
            "you need, THEN record the current element -- in that order, not reversed, so an element doesn't "
            "accidentally pair with itself unless that's genuinely intended. For frequency: walk once, "
            "incrementing a count per key (`collections.Counter` does this in one line); the counts themselves "
            "often become the thing you sort, filter, or compare next. A useful hybrid: remembering EVERY prefix "
            "sum seen so far (not just the running total) turns \"does some contiguous subarray sum to exactly "
            "k?\" into one pass too, since two equal prefix sums bracket a subarray that sums to zero -- see "
            "Subarray Sum Equals K in the problem bank."
        ),
        walkthrough_intro_markdown=(
            "Trace `two_sum([3, 5, 2, 9, 7], 12)` -- the lookup shape. `seen` isn't rendered visually here (this "
            "walkthrough reuses the array/pointer view, which doesn't have a dedicated dict renderer), so its "
            "contents are called out in each step's caption instead."
        ),
        walkthrough_code=(
            "def two_sum(nums, target):\n"
            "    seen = {}  # value -> index\n"
            "    for i, n in enumerate(nums):\n"
            "        complement = target - n\n"
            "        if complement in seen:\n"
            "            return [seen[complement], i]\n"
            "        seen[n] = i\n"
            "    return []"
        ),
        walkthrough_frames=[
            dict(caption="i=0, n=3. complement = 12-3 = 9. seen is empty -- 9 not found. Record seen[3] = 0.",
                 locals={"nums": [3, 5, 2, 9, 7], "target": 12, "i": 0}),
            dict(caption="i=1, n=5. complement = 12-5 = 7. seen = {3: 0} -- 7 not there. Record seen[5] = 1.",
                 locals={"nums": [3, 5, 2, 9, 7], "target": 12, "i": 1}),
            dict(caption="i=2, n=2. complement = 12-2 = 10. seen = {3: 0, 5: 1} -- 10 not there. Record seen[2] = 2.",
                 locals={"nums": [3, 5, 2, 9, 7], "target": 12, "i": 2}),
            dict(caption="i=3, n=9. complement = 12-9 = 3. seen = {3: 0, 5: 1, 2: 2} -- 3 WAS already seen, at index 0! Return [0, 3] -- values 3 and 9 sum to 12.",
                 locals={"nums": [3, 5, 2, 9, 7], "target": 12, "i": 3}),
        ],
        common_mistakes_markdown=(
            "Recording `seen[n] = i` BEFORE checking for the complement -- lets an element pair with itself when "
            "`target == 2 * n` (e.g. `nums=[5], target=10` would wrongly report `[0, 0]`, the same index twice). "
            "Using a list and checking `complement in some_list` -- that's back to an `O(n)` scan per check, "
            "defeating the entire point (list membership is `O(n)`, dict/set membership is `O(1)`). And "
            "mutating a dict while iterating over it directly -- the same class of bug as the Arrays lesson's "
            "list-mutation-during-iteration mistake."
        ),
        complexity_markdown=(
            "`O(n)` time, `O(n)` space -- one pass, at the cost of a second data structure sized to the input. "
            "Compare that to the `O(n^2)` nested-loop brute force this replaces (checking every pair directly). "
            "The prefix-sum + hashmap variant (Subarray Sum Equals K) makes the same trade: `O(n)` time/space "
            "instead of checking every `O(n^2)` subrange."
        ),
    ),
    # ---- Batch 1 addition: item 4 of the curriculum-ordered expansion --
    # "two pointers and sliding windows beyond the pilot material." Sliding
    # window is its own topic in problems.topic (distinct from
    # 'two-pointer'), matching Days 15-16, so this is a separate lesson
    # rather than folded into the Two Pointers pilot -- prerequisite_slugs
    # points back at it since a sliding window IS a same-direction
    # two-pointer technique specialized to a contiguous range. See
    # docs/decisions.md "Teaching system expansion: batch 2".
    dict(
        slug="sliding-window",
        kind="topic",
        topic="sliding-window",
        pattern_family=None,
        title="Sliding window",
        display_order=1,
        estimated_minutes=18,
        summary="A contiguous window that grows (and sometimes shrinks) as you scan once -- turns "
                "\"check every contiguous subarray/substring\" brute force into a single O(n) pass.",
        prerequisite_slugs="two-pointers",
        what_markdown=(
            "A sliding window is a contiguous range `[left, right]` of an array or string that moves forward as "
            "you scan once, instead of re-examining elements you've already looked at. Two shapes: "
            "**fixed-size** -- the window size `k` is given directly, so `right - left + 1 == k` always, and you "
            "slide one step at a time (add the new `right`, drop the old `left`). **Variable-size** -- `right` "
            "always advances, but `left` only advances when the window becomes invalid, so the window's size "
            "changes as you scan."
        ),
        why_markdown=(
            "The brute-force instinct for \"find the best/longest/shortest contiguous subarray or substring "
            "meeting some condition\" is to check every one directly -- `O(n^2)` windows, and recomputing each "
            "window's sum/count from scratch is itself `O(n)`, so `O(n^3)` isn't unusual. A sliding window "
            "exploits that adjacent windows only differ by one element (the one that just entered, the one "
            "that just left), so you update state incrementally instead of recomputing it -- the same "
            "\"don't redo work you already did\" idea as prefix sums and two pointers, specialized to "
            "contiguous ranges."
        ),
        recognize_markdown=(
            "Reach for a sliding window when: the problem asks about a **contiguous** subarray or substring "
            "(not any subset -- contiguous is the key word). You're optimizing something -- longest, shortest, "
            "max sum, count of windows meeting a condition. And the condition is well-behaved as the window "
            "grows or shrinks: adding an element to the window and removing one from it are both cheap, "
            "incremental updates (a running sum, a character-frequency count, a count of distinct values), not "
            "something that forces a full recheck. If the window size is stated directly (\"every k consecutive "
            "elements\"), it's fixed-size; if it depends on a condition (\"longest substring with at most k "
            "distinct characters\"), it's variable-size."
        ),
        intuition_markdown=(
            "A sliding window is a same-direction two-pointer technique where both pointers only ever move "
            "forward and `left <= right` always holds, carving out a moving contiguous range instead of "
            "converging from both ends. **Fixed-size**: first fill a window of exactly `k` elements, then each "
            "step adds one new element on the right and removes exactly one old element on the left -- the size "
            "never changes. **Variable-size**: `right` drives the scan forward (usually the loop variable "
            "itself); `left` only moves when the window has become invalid, and critically, it moves in a "
            "`while` loop, not an `if` -- restoring validity can take more than one step, since removing a "
            "single element from the left doesn't always fix things in one shot."
        ),
        walkthrough_intro_markdown=(
            "Trace `longest_unique_substring(\"abba\")` -- a variable-size window that grows to include new "
            "characters and shrinks (by more than one step, in this case) whenever a duplicate shows up. Watch "
            "`right=2` closely: one shrink isn't enough there, which is exactly the case a common bug (using "
            "`if` instead of `while`) gets wrong."
        ),
        walkthrough_code=(
            "def longest_unique_substring(s):\n"
            "    seen = set()\n"
            "    left = 0\n"
            "    best = 0\n"
            "    for right in range(len(s)):\n"
            "        while s[right] in seen:\n"
            "            seen.remove(s[left])\n"
            "            left += 1\n"
            "        seen.add(s[right])\n"
            "        best = max(best, right - left + 1)\n"
            "    return best"
        ),
        walkthrough_frames=[
            dict(caption="right=0, char='a'. seen is empty -- no duplicate. Add 'a' to seen. Window is s[0:1]='a', best=1.",
                 locals={"s": "abba", "left": 0, "right": 0}),
            dict(caption="right=1, char='b'. Not in seen -- grow. seen={'a','b'}. Window is s[0:2]='ab', best=2.",
                 locals={"s": "abba", "left": 0, "right": 1}),
            dict(caption="right=2, char='b' is ALREADY in seen -- duplicate. Shrink: remove s[0]='a', left becomes 1. seen={'b'} still contains 'b', so the while loop keeps shrinking.",
                 locals={"s": "abba", "left": 1, "right": 2}),
            dict(caption="Shrink again: remove s[1]='b', left becomes 2. seen is now empty -- duplicate cleared, while loop stops. Add s[2]='b'. Window is s[2:3]='b' (size 1); best stays 2.",
                 locals={"s": "abba", "left": 2, "right": 2}),
            dict(caption="right=3, char='a'. Not in seen -- grow. seen={'a','b'}. Window is s[2:4]='ba' (size 2); best stays 2. Loop ends -- return best=2.",
                 locals={"s": "abba", "left": 2, "right": 3}),
        ],
        common_mistakes_markdown=(
            "Using `if s[right] in seen` instead of `while` -- one shrink step isn't always enough (see "
            "`right=2` in the walkthrough above, which needs two). Recomputing the window's sum/count/frequency "
            "map from scratch on every step instead of updating it incrementally (add what just entered, remove "
            "what just left) -- this quietly turns an intended `O(n)` scan back into `O(n^2)`. Off-by-one on the "
            "window size: it's `right - left + 1`, not `right - left`. And for fixed-size windows, forgetting to "
            "fill the initial window of size `k` before starting to slide -- the first `k - 1` steps are setup, "
            "not sliding."
        ),
        complexity_markdown=(
            "`O(n)` time despite the `while` nested inside the `for`: `left` only ever increases and `right` "
            "only ever increases, so between them they take at most `2n` steps total across the ENTIRE scan, "
            "not `n` steps each nested inside another `n` -- the same amortized argument as two pointers. Space "
            "is `O(1)` for a running sum/count, or `O(k)`/`O(alphabet size)` for a frequency map, versus the "
            "`O(n^2)` or worse time of checking every contiguous window directly."
        ),
    ),
    # ---- Batch 3: item 5 of the curriculum-ordered expansion -- linked
    # lists (Days 25-27). First topic whose primary data structure isn't
    # array-shaped, so ConceptWalkthrough.jsx gained a small adapter that
    # builds LinkedListView's graph shape from a much simpler
    # {nodes: [{id, val, next}], pointers: [[name, id], ...]} authoring
    # format (pointers is an ORDERED list of pairs, not a dict -- Flask's
    # JSON serializer sorts dict keys alphabetically, which would silently
    # scramble which pointer becomes the rendered chain's starting point;
    # see ConceptWalkthrough.jsx's own comment) --
    # see that file's comment and docs/decisions.md "Teaching system
    # expansion: batch 3."
    dict(
        slug="linked-lists",
        kind="topic",
        topic="linked-lists",
        pattern_family=None,
        title="Linked lists",
        display_order=1,
        estimated_minutes=18,
        summary="A chain of node objects linked by .next references instead of one contiguous block of "
                "memory -- O(1) insertion/deletion once you're at the right node, but no random access.",
        prerequisite_slugs="arrays",
        what_markdown=(
            "A linked list is a sequence built from individual node objects, each holding a value and a "
            "reference (`.next`) to the following node -- unlike a Python list, which is one contiguous block "
            "of memory. The list itself is just a reference to the first node (`head`); walking it means "
            "following `.next` one node at a time until you reach `None`."
        ),
        why_markdown=(
            "Arrays give `O(1)` random access but `O(n)` insertion/deletion in the middle -- everything after "
            "the insertion point has to shift. Linked lists flip that trade: `O(n)` to reach a given position "
            "(no shortcuts, you have to walk there one node at a time), but `O(1)` insertion/deletion ONCE "
            "you're already at the right node -- no shifting, just rewiring a couple of `.next` references. "
            "That's why linked lists show up wherever insertion/removal happens far more often than random "
            "lookup by position."
        ),
        recognize_markdown=(
            "The tell isn't just \"the input is a linked list\" -- it's being asked to manipulate node "
            "references directly: reverse it, remove a specific node, merge two lists by splicing their nodes "
            "together, detect whether it loops back on itself. If the problem only needed a sequence you could "
            "index into or scan, an array would already do the job. A `dummy head` node (a throwaway node "
            "placed before the real head) is worth reaching for whenever the node you might insert/remove could "
            "be the head itself -- it turns \"the head is a special case\" into \"every node is rewired the "
            "same way.\""
        ),
        intuition_markdown=(
            "**Traversal**: `current = head`, then `while current is not None: ... current = current.next` -- "
            "one step at a time, no shortcuts. **Deletion**: `prev.next = prev.next.next` skips over the "
            "unwanted node entirely; the deleted node itself doesn't need to be touched, Python's garbage "
            "collector reclaims it once nothing references it anymore. **Insertion**: rewire the new node's "
            "`.next` FIRST (pointing it at what comes after), THEN point the previous node at the new one -- "
            "reversed order loses the rest of the list. **Reversal**: walk with three references at once -- "
            "`prev`, `curr`, and a temporary `next_node` -- and save `next_node = curr.next` BEFORE overwriting "
            "`curr.next`, or the rest of the original list becomes unreachable forever."
        ),
        walkthrough_intro_markdown=(
            "Trace `reverse_list(head)` on a 3-node list (values 1, 2, 3) -- the classic three-pointer in-place "
            "reversal. Watch how the picture splits as it runs: the growing chain from `prev` shows the "
            "already-reversed portion; any node not yet reachable from `prev` (still only referenced via "
            "`curr`) renders separately below as \"not reachable from the main chain\" -- that's not a "
            "rendering glitch, it's genuinely a separate, not-yet-relinked piece of the list until the loop "
            "reaches it."
        ),
        walkthrough_code=(
            "class Node:\n"
            "    def __init__(self, val):\n"
            "        self.val = val\n"
            "        self.next = None\n\n"
            "def reverse_list(head):\n"
            "    prev = None\n"
            "    curr = head\n"
            "    while curr is not None:\n"
            "        next_node = curr.next\n"
            "        curr.next = prev\n"
            "        prev = curr\n"
            "        curr = next_node\n"
            "    return prev"
        ),
        walkthrough_frames=[
            dict(caption="Before the loop: prev=None, curr=head (value 1). The list is untouched: 1 -> 2 -> 3 -> None.",
                 locals={"nodes": [{"id": 0, "val": 1, "next": 1}, {"id": 1, "val": 2, "next": 2}, {"id": 2, "val": 3, "next": None}],
                         "pointers": [["prev", None], ["curr", 0]]}),
            dict(caption="First node reversed: node value 1's .next now points to prev (None) -- it's cut loose from the old chain, becoming the new tail. prev advances to it; curr advances to value 2. Values 2 and 3 are still linked to each other but no longer reachable from prev, so they render separately below.",
                 locals={"nodes": [{"id": 0, "val": 1, "next": None}, {"id": 1, "val": 2, "next": 2}, {"id": 2, "val": 3, "next": None}],
                         "pointers": [["prev", 0], ["curr", 1]]}),
            dict(caption="Second node reversed: node value 2's .next now points to node value 1 -- two nodes are correctly reversed (2 -> 1 -> None). prev advances to value 2; curr advances to value 3, the last original node.",
                 locals={"nodes": [{"id": 0, "val": 1, "next": None}, {"id": 1, "val": 2, "next": 0}, {"id": 2, "val": 3, "next": None}],
                         "pointers": [["prev", 1], ["curr", 2]]}),
            dict(caption="Third and final node reversed: node value 3's .next now points to node value 2. curr becomes None (the original last node had no next) -- the while loop ends. Return prev = node value 3, the new head. The list is now 3 -> 2 -> 1 -> None, fully reversed in place with zero new nodes allocated.",
                 locals={"nodes": [{"id": 0, "val": 1, "next": None}, {"id": 1, "val": 2, "next": 0}, {"id": 2, "val": 3, "next": 1}],
                         "pointers": [["prev", 2], ["curr", None]]}),
        ],
        common_mistakes_markdown=(
            "Overwriting `curr.next` before saving it -- `curr.next = prev` first, THEN `curr = curr.next`, "
            "reads back the value you just overwrote (`prev`), not the original next node, silently truncating "
            "the list after one node. Always save `next_node = curr.next` before mutating `curr.next` (see this "
            "lesson's walkthrough). Forgetting to check for `None` while walking -- accessing `.next` on a "
            "`None` current node raises an `AttributeError`. Forgetting the head itself needs special handling "
            "on insertion/deletion at the front (there's no \"previous node\" to rewire) -- a dummy head node "
            "sidesteps this entirely. And comparing nodes with `==` when you meant `.val ==` -- a hand-rolled "
            "class with no `__eq__` compares object identity by default, so two different nodes holding the "
            "same value are never `==` to each other."
        ),
        complexity_markdown=(
            "Traversal: `O(n)` to reach a given position, no shortcuts. Insertion/deletion: `O(1)` once you're "
            "already at the right node (just rewire a couple of `.next` references), versus `O(n)` for the same "
            "operation in the middle of a Python list, which has to shift every following element. Reversal: "
            "`O(n)` time (visit every node once), `O(1)` extra space -- no new nodes are created, only existing "
            "`.next` references are rewired."
        ),
    ),
    dict(
        slug="linked-list-fast-slow",
        kind="pattern",
        topic="linked-lists",
        pattern_family="Fast/slow pointers",
        title="Fast/slow pointers",
        display_order=2,
        estimated_minutes=16,
        summary="Two pointers moving through the same list at different speeds -- the fast one laps the slow "
                "one if (and only if) there's a cycle, or reaches the end exactly when slow reaches the middle.",
        prerequisite_slugs="linked-lists,two-pointers",
        what_markdown=(
            "Two pointers, `slow` and `fast`, start at the same node and both move forward by following "
            "`.next` -- but `fast` moves two steps for every one step `slow` takes. That speed difference is "
            "the whole trick: it lets you answer questions about a linked list's SHAPE (does it loop back on "
            "itself? where's the middle?) in a single pass, without counting the list's length first."
        ),
        why_markdown=(
            "Both questions this pattern answers -- \"is there a cycle?\" and \"what's the middle node?\" -- "
            "look like they need two passes: count the length first, then walk again to the right spot (or "
            "walk the whole list storing every visited node just to check for a repeat, `O(n)` space). "
            "Fast/slow answers both in ONE pass with `O(1)` extra space, because the speed difference itself "
            "carries the information a length-count or a visited-set would otherwise be needed for."
        ),
        recognize_markdown=(
            "The tell is needing to know something about a linked list's structure without being told its "
            "length up front: does it cycle back on itself, where's its midpoint, is it a palindrome (walk to "
            "the middle, reverse the second half, compare halves). If your first instinct is \"I'd need to "
            "know the length first\" or \"I'd need to remember every node I've already visited,\" fast/slow is "
            "very often the `O(1)`-space alternative -- this is a same-direction two-pointer technique, just "
            "with an unequal step size instead of an unequal start condition."
        ),
        intuition_markdown=(
            "**Cycle detection**: if there's no cycle, `fast` (moving 2 steps at a time) reaches `None` first "
            "and the loop simply ends -- no cycle. If there IS a cycle, `fast` enters it and, being faster, "
            "eventually LAPS `slow` from behind -- they land on the same node at the same step. That's "
            "guaranteed, not just likely: once both pointers are inside the cycle, the gap between them "
            "(measured going forward around the loop) shrinks by exactly one node every step, and a shrinking "
            "gap around a finite loop must eventually hit zero. **Finding the middle**: when `fast` reaches the "
            "end (or one node before it), `slow` -- moving half as fast -- has covered exactly half the "
            "distance, landing on the middle node."
        ),
        walkthrough_intro_markdown=(
            "Trace `has_cycle(head)` on a 4-node list where the last node's `.next` loops back to the SECOND "
            "node (not the first) -- a genuine cycle, not just a long list. Watch the gap between `slow` and "
            "`fast` close by one node every step once both are inside the loop."
        ),
        walkthrough_code=(
            "class Node:\n"
            "    def __init__(self, val):\n"
            "        self.val = val\n"
            "        self.next = None\n\n"
            "def has_cycle(head):\n"
            "    slow = fast = head\n"
            "    while fast is not None and fast.next is not None:\n"
            "        slow = slow.next\n"
            "        fast = fast.next.next\n"
            "        if slow is fast:\n"
            "            return True\n"
            "    return False"
        ),
        walkthrough_frames=[
            dict(caption="Both pointers start at head (value 10). slow will move 1 step at a time; fast will move 2.",
                 locals={"nodes": [{"id": 0, "val": 10, "next": 1}, {"id": 1, "val": 20, "next": 2}, {"id": 2, "val": 30, "next": 3}, {"id": 3, "val": 40, "next": 1}],
                         "pointers": [["slow", 0], ["fast", 0]]}),
            dict(caption="One iteration: slow moves 1 step (10 -> 20), fast moves 2 steps (10 -> 20 -> 30). fast is now ahead by one full node -- no match yet. (Value 10 no longer appears in either pointer's trail below -- the list itself hasn't changed, neither pointer references it anymore.)",
                 locals={"nodes": [{"id": 0, "val": 10, "next": 1}, {"id": 1, "val": 20, "next": 2}, {"id": 2, "val": 30, "next": 3}, {"id": 3, "val": 40, "next": 1}],
                         "pointers": [["slow", 1], ["fast", 2]]}),
            dict(caption="Second iteration: slow moves to value 30. fast moves 2 more steps, wrapping around the cycle back to value 20 -- fast has gone around and is 'behind' slow in list order, but it's still gaining: the forward gap between them has shrunk by one node since the last step.",
                 locals={"nodes": [{"id": 0, "val": 10, "next": 1}, {"id": 1, "val": 20, "next": 2}, {"id": 2, "val": 30, "next": 3}, {"id": 3, "val": 40, "next": 1}],
                         "pointers": [["slow", 2], ["fast", 1]]}),
            dict(caption="Third iteration: slow moves to value 40. fast moves 2 more steps and lands on the SAME node -- slow is fast. The gap has closed to zero: a cycle is confirmed. Return True.",
                 locals={"nodes": [{"id": 0, "val": 10, "next": 1}, {"id": 1, "val": 20, "next": 2}, {"id": 2, "val": 30, "next": 3}, {"id": 3, "val": 40, "next": 1}],
                         "pointers": [["slow", 3], ["fast", 3]]}),
        ],
        common_mistakes_markdown=(
            "Checking only `while fast.next is not None` -- on a list with NO cycle and an even number of "
            "nodes, `fast` itself can become `None` (after landing exactly on the last node's `.next`), and the "
            "next loop check crashes with `AttributeError: 'NoneType' object has no attribute 'next'`. The "
            "condition needs both: `while fast is not None and fast.next is not None`. Using `==` instead of "
            "`is` to compare `slow` and `fast` -- for hand-rolled node classes with no `__eq__`, `is` (identity) "
            "is what actually means \"the same node,\" and happens to be what `==` falls back to anyway, but "
            "`is` states the intent directly. And initializing `slow` and `fast` to different starting points "
            "when the problem calls for both starting at `head` -- an off-by-one start throws off exactly when "
            "(or whether) they meet."
        ),
        complexity_markdown=(
            "`O(n)` time, `O(1)` space. Even though `fast` moves 2 steps at a time, the total work stays "
            "bounded by a constant factor of `n`: with no cycle, `fast` reaches the end in at most `n/2` "
            "iterations; with a cycle, `fast` is guaranteed to catch `slow` within at most one full lap of the "
            "cycle. Either way, `O(n)` time -- versus `O(n)` space (not just time) for a visited-set approach "
            "that stores every node to check for a repeat."
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
    "prefix-sums": [
        dict(kind="choose_pattern",
             prompt_markdown="You'll be asked the sum of many different ranges of the same fixed array, over and "
                              "over. Which approach fits best?",
             code=None,
             choices_json=[
                 "Nested loop re-summing each queried range, O(n) per query",
                 "Precompute a prefix-sum array once, then O(1) per query",
                 "Sort the array first",
                 "Two pointers from both ends",
             ],
             correct_answer="Precompute a prefix-sum array once, then O(1) per query",
             explanation_markdown="Repeated range queries against a fixed array is exactly the \"precompute now, "
                                   "pay less later\" shape prefix sums exist for -- one O(n) precompute turns "
                                   "every future query into O(1)."),
        dict(kind="spot_bug",
             prompt_markdown="This range_sum is meant to return the sum of arr[left..right] using a prefix array. "
                              "It's wrong specifically when left=0. What's the bug?",
             code="def range_sum(prefix, left, right):\n    return prefix[right] - prefix[left - 1]",
             choices_json=None,
             correct_answer="When left=0, prefix[left - 1] becomes prefix[-1] in Python -- which silently wraps "
                             "around to the LAST element of the array, not zero. There's no crash, just a wrong "
                             "answer. A left==0 special case (returning prefix[right] directly) is needed.",
             explanation_markdown="Python allows negative indices as \"count from the end,\" so `prefix[-1]` is "
                                   "valid syntax that quietly returns the wrong value instead of raising an error "
                                   "-- exactly the kind of bug that's easy to miss because nothing crashes."),
        dict(kind="complexity",
             prompt_markdown="Building a prefix-sum array for n elements takes O(n). Once it's built, what's the "
                              "time to answer a single range-sum query?",
             code=None,
             choices_json=None,
             correct_answer="O(1)",
             explanation_markdown="One subtraction, prefix[right] - prefix[left-1] -- no loop, regardless of how "
                                   "wide the queried range is."),
    ],
    "strings": [
        dict(kind="choose_pattern",
             prompt_markdown="You need to check whether two strings are anagrams of each other (same letters, "
                              "any order). Which approach is most natural?",
             code=None,
             choices_json=[
                 "Compare the strings character-by-character in original order",
                 "Count each string's character frequencies and compare the counts",
                 "Two pointers from both ends",
                 "Binary search",
             ],
             correct_answer="Count each string's character frequencies and compare the counts",
             explanation_markdown="\"Same letters, any order\" is a counting-characters problem, not a "
                                   "comparing-in-order one -- two strings are anagrams exactly when their "
                                   "character frequency counts are identical (equivalently: their sorted forms "
                                   "match, a slower but simpler variant)."),
        dict(kind="spot_bug",
             prompt_markdown="This builds a string by appending one character at a time. It's correct, but "
                              "surprisingly slow on long inputs. What's the issue?",
             code="def build_string(chars):\n    result = \"\"\n    for c in chars:\n        result += c\n    return result",
             choices_json=None,
             correct_answer="Strings are immutable in Python -- every result += c creates a brand-new string, "
                             "copying everything accumulated so far. For n characters that's O(n^2) total work, "
                             "not O(n). Collect into a list and use ''.join(list) once at the end instead.",
             explanation_markdown="Each `+=` looks like an in-place update but isn't one -- it allocates a new "
                                   "string of length k+1 and copies the old k characters into it, every single "
                                   "time. A list append is O(1) amortized, and .join() does the final copy once."),
        dict(kind="complexity",
             prompt_markdown="Expand-around-center tries every possible center in a string of length n and grows "
                              "outward from each. In the worst case (e.g. a string of all the same character), "
                              "what's the total time complexity?",
             code=None,
             choices_json=None,
             correct_answer="O(n^2)",
             explanation_markdown="O(n) possible centers, each expanding up to O(n) in the worst case -- O(n^2) "
                                   "total. Still better than checking all O(n^2) substrings individually for "
                                   "palindrome-ness, which would cost O(n) per check, O(n^3) overall."),
    ],
    "hashing": [
        dict(kind="choose_pattern",
             prompt_markdown="For each element in an array, you need to know whether its complement "
                              "(target - element) has already appeared earlier in the array. What's the right "
                              "tool?",
             code=None,
             choices_json=[
                 "Nested loop checking every pair, O(n^2)",
                 "A hash map remembering every value seen so far, O(n)",
                 "Sort the array first",
                 "A stack",
             ],
             correct_answer="A hash map remembering every value seen so far, O(n)",
             explanation_markdown="This is the canonical hash-map lookup shape -- remember what you've seen, "
                                   "check the complement in O(1) as you go. (If the array happened to already be "
                                   "sorted, opposite-direction two pointers would also work in O(n) -- but "
                                   "hashing works whether or not it's sorted, the more general case.)"),
        dict(kind="spot_bug",
             prompt_markdown="This two_sum sometimes returns the SAME index twice instead of two different "
                              "elements. What's the bug?",
             code="def two_sum(nums, target):\n"
                  "    seen = {}\n"
                  "    for i, n in enumerate(nums):\n"
                  "        seen[n] = i\n"
                  "        complement = target - n\n"
                  "        if complement in seen:\n"
                  "            return [seen[complement], i]\n"
                  "    return []",
             choices_json=None,
             correct_answer="It records seen[n] = i BEFORE checking for the complement, so an element can match "
                             "against itself when target == 2*n (e.g. nums=[5], target=10 wrongly returns "
                             "[0, 0]). The check must happen before the record.",
             explanation_markdown="Swap the two lines: check `if complement in seen` first, THEN do "
                                   "`seen[n] = i` -- so the current element is never available to match against "
                                   "itself, only elements seen on earlier iterations."),
        dict(kind="complexity",
             prompt_markdown="What's the time complexity of the hash-map lookup pattern -- one pass over an "
                              "array of size n, checking membership in a dict/set at each step?",
             code=None,
             choices_json=None,
             correct_answer="O(n)",
             explanation_markdown="One pass, O(1) average-case dict lookup per element -- O(n) total, versus "
                                   "O(n^2) for the nested-loop brute force checking every pair directly."),
    ],
    "sliding-window": [
        dict(kind="choose_pattern",
             prompt_markdown="You need the length of the longest contiguous substring that contains at most 2 "
                              "distinct characters. Which approach fits best?",
             code=None,
             choices_json=[
                 "Variable-size sliding window, O(n)",
                 "Check every substring directly, O(n^2) or worse",
                 "Opposite-direction two pointers from both ends",
                 "Sort the string first",
             ],
             correct_answer="Variable-size sliding window, O(n)",
             explanation_markdown="'Contiguous substring' plus 'longest... meeting a condition' is the sliding-"
                                   "window shape. It's variable-size, not fixed-size, because the window's "
                                   "length isn't given -- it depends on when the distinct-character count "
                                   "exceeds 2. Opposite-direction two pointers doesn't apply here: this isn't a "
                                   "sorted-array pair search, it's a single forward scan."),
        dict(kind="spot_bug",
             prompt_markdown="This is meant to find the longest substring with no repeated characters, but it "
                              "sometimes returns a window that still contains a duplicate. What's the bug?",
             code="def longest_unique_substring(s):\n"
                  "    seen = set()\n"
                  "    left = 0\n"
                  "    best = 0\n"
                  "    for right in range(len(s)):\n"
                  "        if s[right] in seen:\n"
                  "            seen.remove(s[left])\n"
                  "            left += 1\n"
                  "        seen.add(s[right])\n"
                  "        best = max(best, right - left + 1)\n"
                  "    return best",
             choices_json=None,
             correct_answer="It uses `if` instead of `while` to shrink the window. Removing just one character "
                             "from the left isn't always enough to clear the duplicate -- sometimes the window "
                             "needs to shrink by more than one step before s[right] is no longer in seen.",
             explanation_markdown="Trace s='abba' at right=2: seen={'a','b'} and s[2]='b' is a duplicate. `if` "
                                   "removes s[0]='a' once and immediately adds 'b' back in -- but 'b' is STILL "
                                   "in seen (it was never removed), so the window still has a duplicate. `while` "
                                   "keeps shrinking until the duplicate is actually gone -- exactly the double-"
                                   "shrink shown in this lesson's own walkthrough."),
        dict(kind="complexity",
             prompt_markdown="A variable-size sliding window has a `while` loop nested inside a `for` loop. "
                              "What's the overall time complexity, and why isn't it O(n^2)?",
             code=None,
             choices_json=None,
             correct_answer="O(n)",
             explanation_markdown="left only ever increases and right only ever increases -- combined, they "
                                   "take at most 2n steps total across the WHOLE scan, not n steps each nested "
                                   "inside another n. The same amortized argument that makes two pointers O(n) "
                                   "applies here."),
    ],
    "linked-lists": [
        dict(kind="choose_pattern",
             prompt_markdown="You need to delete a specific node from a singly linked list, given only a "
                              "pointer to the head. What do you actually need in hand to delete it in O(1) "
                              "once you've found the right spot?",
             code=None,
             choices_json=[
                 "A pointer to the node BEFORE the one you want to delete",
                 "A pointer to the node you want to delete itself",
                 "The value stored in the node you want to delete",
                 "Convert the whole list to an array first",
             ],
             correct_answer="A pointer to the node BEFORE the one you want to delete",
             explanation_markdown="Deletion is prev.next = prev.next.next -- you rewire the PREVIOUS node's "
                                   "pointer. A singly linked list has no way to reach backward, so a reference "
                                   "to the node itself isn't enough to unlink it."),
        dict(kind="spot_bug",
             prompt_markdown="This is meant to reverse a linked list in place, but it returns just the first "
                              "node -- the rest of the list is gone. What's the bug?",
             code="def reverse_list(head):\n"
                  "    prev = None\n"
                  "    curr = head\n"
                  "    while curr is not None:\n"
                  "        curr.next = prev\n"
                  "        prev = curr\n"
                  "        curr = curr.next\n"
                  "    return prev",
             choices_json=None,
             correct_answer="curr.next is overwritten (curr.next = prev) BEFORE the original next node is "
                             "read. By the time curr = curr.next runs, curr.next is now prev, not the "
                             "original next node -- the rest of the list is lost after the very first node.",
             explanation_markdown="Save next_node = curr.next as a separate variable BEFORE mutating "
                                   "curr.next, then advance curr = next_node at the end -- exactly the order "
                                   "shown in this lesson's own walkthrough."),
        dict(kind="complexity",
             prompt_markdown="Reversing an n-node linked list in place with the three-pointer technique takes "
                              "how much extra space, beyond the list itself?",
             code=None,
             choices_json=None,
             correct_answer="O(1)",
             explanation_markdown="No new nodes are allocated -- only existing .next references are rewired "
                                   "using a constant number of pointer variables (prev, curr, next_node), "
                                   "regardless of how long the list is."),
    ],
    "linked-list-fast-slow": [
        dict(kind="choose_pattern",
             prompt_markdown="You need to find the middle node of a singly linked list in one pass, without "
                              "knowing its length in advance. What's the right technique?",
             code=None,
             choices_json=[
                 "Fast/slow pointers -- fast moves 2 steps for every 1 slow takes",
                 "Two pointers from opposite ends of the list",
                 "Count the length first, then walk halfway",
                 "Convert the list to an array and index into the middle",
             ],
             correct_answer="Fast/slow pointers -- fast moves 2 steps for every 1 slow takes",
             explanation_markdown="Opposite-ends two pointers doesn't apply to a singly linked list -- there's "
                                   "no O(1) way to start from the end without already having it reversed or in "
                                   "an array. Counting the length first works, but takes two passes; fast/slow "
                                   "finds the middle in one."),
        dict(kind="spot_bug",
             prompt_markdown="This cycle-detection sometimes crashes with an AttributeError on lists that have "
                              "NO cycle. What's the bug?",
             code="def has_cycle(head):\n"
                  "    slow = fast = head\n"
                  "    while fast.next is not None:\n"
                  "        slow = slow.next\n"
                  "        fast = fast.next.next\n"
                  "        if slow is fast:\n"
                  "            return True\n"
                  "    return False",
             choices_json=None,
             correct_answer="The loop only checks fast.next is not None, not fast itself. On a cycle-free "
                             "list with an even number of nodes, fast can land exactly on None -- then the "
                             "next iteration's fast.next crashes, since None has no .next.",
             explanation_markdown="The condition needs both: while fast is not None and fast.next is not "
                                   "None. Checking fast.next alone assumes fast is always a real node when the "
                                   "check runs, which stops being true the moment fast itself becomes None."),
        dict(kind="complexity",
             prompt_markdown="Fast/slow cycle detection visits nodes with fast moving 2 steps per iteration. "
                              "What's the overall time complexity for a list of n nodes, with or without a "
                              "cycle?",
             code=None,
             choices_json=None,
             correct_answer="O(n)",
             explanation_markdown="With no cycle, fast reaches the end in at most n/2 iterations. With a "
                                   "cycle, fast is guaranteed to catch slow within at most one full lap of the "
                                   "cycle. Either way, O(n) time -- and O(1) space, versus O(n) space for a "
                                   "visited-set approach that stores every node to check for a repeat."),
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
    "prefix-sums": [
        dict(prompt_markdown="Write `range_sum_queries(arr, queries)` where `queries` is a list of `(left, "
                              "right)` tuples (inclusive), returning a list of the sum for each range -- using a "
                              "single O(n) prefix-sum precompute, not re-summing each query from scratch.",
             starter_code="def range_sum_queries(arr, queries):\n    # build the prefix array once, then answer\n"
                          "    # every query in O(1) using it\n    pass",
             solution_code=(
                 "def range_sum_queries(arr, queries):\n"
                 "    prefix = [0] * len(arr)\n"
                 "    prefix[0] = arr[0]\n"
                 "    for i in range(1, len(arr)):\n"
                 "        prefix[i] = prefix[i - 1] + arr[i]\n"
                 "    results = []\n"
                 "    for left, right in queries:\n"
                 "        if left == 0:\n"
                 "            results.append(prefix[right])\n"
                 "        else:\n"
                 "            results.append(prefix[right] - prefix[left - 1])\n"
                 "    return results"
             ),
             hint_markdown="Build the prefix array exactly once, before looking at any query. Then each query is "
                            "just the range-sum formula -- watch the left==0 special case from the lesson."),
    ],
    "strings": [
        dict(prompt_markdown="Write `is_rotation(s1, s2)` that returns True if s2 is a rotation of s1 (e.g. "
                              "'abcde' and 'cdeab'). Hint: think about what appears inside `s1 + s1`.",
             starter_code="def is_rotation(s1, s2):\n    # every rotation of s1 is a contiguous substring of s1+s1\n    pass",
             solution_code=(
                 "def is_rotation(s1, s2):\n"
                 "    if len(s1) != len(s2):\n"
                 "        return False\n"
                 "    return s2 in (s1 + s1)"
             ),
             hint_markdown="Write s1 twice in a row (s1 + s1). Every possible rotation of s1 appears somewhere "
                            "inside that doubled string as a contiguous substring -- so a plain substring check "
                            "answers the question, once the lengths are confirmed equal."),
    ],
    "hashing": [
        dict(prompt_markdown="Write `first_unique_char(s)` that returns the index of the first character in a "
                              "string that appears exactly once (or -1 if none does), using a frequency count.",
             starter_code="def first_unique_char(s):\n    # count every character's frequency first, then scan\n"
                          "    # again for the first one with count == 1\n    pass",
             solution_code=(
                 "from collections import Counter\n\n"
                 "def first_unique_char(s):\n"
                 "    counts = Counter(s)\n"
                 "    for i, c in enumerate(s):\n"
                 "        if counts[c] == 1:\n"
                 "            return i\n"
                 "    return -1"
             ),
             hint_markdown="This needs two passes: one to count every character's total frequency, a second to "
                            "find the first character whose count is exactly 1 -- the first pass has to finish "
                            "before the second one can trust any count."),
    ],
    "sliding-window": [
        dict(prompt_markdown="Write `max_ones_after_flip(bits, k)` where `bits` is a list of 0s and 1s. You may "
                              "flip at most `k` zeros to ones. Return the length of the longest contiguous run "
                              "of 1s you can get. Use a variable-size window -- track how many zeros are "
                              "currently inside it.",
             starter_code="def max_ones_after_flip(bits, k):\n    # grow right every step; shrink left only when\n"
                          "    # the window's zero count exceeds k\n    pass",
             solution_code=(
                 "def max_ones_after_flip(bits, k):\n"
                 "    left = 0\n"
                 "    zeros = 0\n"
                 "    best = 0\n"
                 "    for right in range(len(bits)):\n"
                 "        if bits[right] == 0:\n"
                 "            zeros += 1\n"
                 "        while zeros > k:\n"
                 "            if bits[left] == 0:\n"
                 "                zeros -= 1\n"
                 "            left += 1\n"
                 "        best = max(best, right - left + 1)\n"
                 "    return best"
             ),
             hint_markdown="The window is always valid as long as zeros <= k. Grow right unconditionally each "
                            "step; only shrink left (in a while, not an if) when zeros exceeds k."),
    ],
    "linked-lists": [
        dict(prompt_markdown="Write `remove_value(head, target)` that removes the FIRST node whose `.val == "
                              "target` and returns the (possibly new) head. Use a dummy node before `head` so "
                              "removing the actual head isn't a special case separate from removing any other "
                              "node.",
             starter_code="class Node:\n    def __init__(self, val):\n        self.val = val\n        self.next = None\n\n"
                          "def remove_value(head, target):\n    # dummy.next = head means 'skip the node after prev'\n"
                          "    # is always the same operation, even when the node to remove IS head\n"
                          "    dummy = Node(0)\n    dummy.next = head\n    pass",
             solution_code=(
                 "class Node:\n"
                 "    def __init__(self, val):\n"
                 "        self.val = val\n"
                 "        self.next = None\n\n"
                 "def remove_value(head, target):\n"
                 "    dummy = Node(0)\n"
                 "    dummy.next = head\n"
                 "    prev = dummy\n"
                 "    while prev.next is not None:\n"
                 "        if prev.next.val == target:\n"
                 "            prev.next = prev.next.next\n"
                 "            break\n"
                 "        prev = prev.next\n"
                 "    return dummy.next"
             ),
             hint_markdown="prev starts at dummy, one step before head. Walk prev forward until "
                            "prev.next.val == target, then skip over it: prev.next = prev.next.next. Return "
                            "dummy.next, not head -- head itself might be the node you removed."),
    ],
    "linked-list-fast-slow": [
        dict(prompt_markdown="Write `find_middle_val(head)` that returns the value of the middle node of a "
                              "non-empty linked list in one pass, without computing the length first. For an "
                              "even-length list, return the SECOND of the two middle nodes.",
             starter_code="def find_middle_val(head):\n    # fast moves 2 steps for every 1 slow takes --\n"
                          "    # when fast runs out of room, slow is at the middle\n    pass",
             solution_code=(
                 "def find_middle_val(head):\n"
                 "    slow = fast = head\n"
                 "    while fast is not None and fast.next is not None:\n"
                 "        slow = slow.next\n"
                 "        fast = fast.next.next\n"
                 "    return slow.val"
             ),
             hint_markdown="Both start at head. Each iteration: slow advances one node, fast advances two. "
                            "Stop as soon as fast can't take a full 2-step move (fast is None or fast.next is "
                            "None) -- slow is sitting on the middle at that point."),
    ],
}
