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
    # ---- Batch 4: item 6 of the curriculum-ordered expansion -- stacks
    # and queues (Days 28-29). Only 4 curated problems each, so unlike
    # linked-lists/fast-slow this stays ONE lesson per topic rather than
    # splitting off a separate pattern lesson for monotonic stack/deque --
    # not enough curated backing to justify a second lesson, so that
    # technique is taught within the topic lesson's own recognize/
    # intuition sections instead. See docs/decisions.md "Teaching system
    # expansion: batch 4."
    dict(
        slug="stacks",
        kind="topic",
        topic="stacks",
        pattern_family=None,
        title="Stacks",
        display_order=1,
        estimated_minutes=16,
        summary="LIFO -- push and pop from one end only. Simple to implement, but the engine behind matching, "
                "nesting, and the monotonic-stack trick for 'nearest bigger/smaller element' problems.",
        prerequisite_slugs="arrays",
        what_markdown=(
            "A stack is a LIFO (last-in, first-out) sequence: you only ever add to (`push`) or remove from "
            "(`pop`) ONE end, called the top. Python's plain list already IS a stack -- `.append()` pushes, "
            "`.pop()` pops from the end -- no special class needed."
        ),
        why_markdown=(
            "A stack is the natural fit whenever \"what matters right now\" is whatever happened most recently "
            "and isn't resolved yet -- an open bracket waiting for its close, an operand waiting to be combined "
            "in an expression, an element waiting to find the next bigger value after it. Trying to answer "
            "those questions by re-scanning from the start every time is `O(n)` per question; a stack "
            "remembers exactly the unresolved things, in exactly the order that matters, for free."
        ),
        recognize_markdown=(
            "**Matching/nesting**: brackets, tags, or any \"every opener needs a corresponding closer, and they "
            "have to close in the reverse order they opened\" structure. **Expression evaluation**: postfix/RPN "
            "notation, or anything where you combine the two most-recently-seen operands. **Monotonic stack** "
            "-- the tell is \"for each element, find the nearest element to its right (or left) that's bigger "
            "(or smaller)\" -- e.g. daily temperatures until it gets warmer. The naive approach is a nested "
            "loop checking every pair after it, `O(n^2)`; a stack that stays sorted (monotonic) as you scan "
            "resolves every element in one pass, `O(n)` total."
        ),
        intuition_markdown=(
            "**Matching**: push every opener; when you see a closer, pop and check it matches -- an empty "
            "stack when you expect something to pop, or a leftover non-empty stack at the end, both mean "
            "unmatched. **Monotonic stack**: walk once, keeping the stack's values in increasing (or "
            "decreasing) order at all times. When the current value would break that order, pop entries off "
            "-- each pop is a \"found its answer\" event, since the current value IS that popped value's "
            "nearest bigger element -- before pushing the current value on. Multiple pops can happen for one "
            "new value, so this is a `while`, not an `if`. **Auxiliary stack** (e.g. min-stack): track a "
            "running minimum alongside each push, either a parallel min-stack or `(value, min_so_far)` tuples, "
            "so the current minimum is available in `O(1)` without rescanning."
        ),
        walkthrough_intro_markdown=(
            "Trace `next_greater(nums)` on `[3, 1, 4, 2]` -- for each value, find the nearest value to its "
            "right that's bigger (or `-1` if none exists). Only the stack itself is shown below; `i` and the "
            "current value are narrated in each caption, since the stack's push/pop behavior -- not array "
            "position -- is the whole point here."
        ),
        walkthrough_code=(
            "def next_greater(nums):\n"
            "    stack = []  # values still waiting to find something bigger\n"
            "    result = {}\n"
            "    for i, n in enumerate(nums):\n"
            "        while stack and stack[-1] < n:\n"
            "            result[stack.pop()] = n\n"
            "        stack.append(n)\n"
            "    for n in stack:\n"
            "        result[n] = -1  # nothing bigger ever showed up\n"
            "    return [result[n] for n in nums]"
        ),
        walkthrough_frames=[
            dict(caption="i=0, n=3. Stack is empty -- nothing to compare against yet. Push 3.",
                 locals={"stack": [3]}),
            dict(caption="i=1, n=1. Top of stack is 3; 3 is NOT less than 1, so 3 isn't resolved yet. Push 1.",
                 locals={"stack": [3, 1]}),
            dict(caption="i=2, n=4. Top of stack is 1; 1 < 4, so 1's next-greater element is 4 -- pop it. Top is now 3; 3 < 4 too, so the while loop keeps popping.",
                 locals={"stack": [3]}),
            dict(caption="3 < 4 as well -- pop it too (3's next-greater is also 4). Stack is now empty, so the while loop stops. Push 4.",
                 locals={"stack": [4]}),
            dict(caption="i=3, n=2. Top of stack is 4; 4 is NOT less than 2, so 4 isn't resolved. Push 2. Loop ends -- everything still on the stack (4 and 2) never found a bigger element to their right.",
                 locals={"stack": [4, 2]}),
        ],
        common_mistakes_markdown=(
            "Using `if` instead of `while` when popping in a monotonic stack -- one pop isn't always enough "
            "(see `i=2` in the walkthrough above, which needs two). Checking `stack[-1]` without first "
            "confirming the stack isn't empty -- `IndexError` on an empty stack; always guard with `if stack:` "
            "or `while stack and ...`. For matching/nesting problems: checking that pops never fail but "
            "forgetting a non-empty stack at the very end ALSO means something was never closed -- the correct "
            "check is `len(stack) == 0` after the whole scan, not just \"no error happened along the way\". "
            "And for min-stack: recomputing the minimum by scanning the whole stack on every query defeats the "
            "entire point -- track a running minimum alongside each push instead."
        ),
        complexity_markdown=(
            "Push/pop/peek: `O(1)` each -- Python's list `.append()`/`.pop()` from the end are both `O(1)`. A "
            "monotonic stack walk is still `O(n)` total despite the `while` nested inside the `for`: each "
            "element is pushed once and popped at most once across the ENTIRE scan -- the same amortized "
            "argument as two pointers and sliding windows. `O(n)` space in the worst case (nothing ever gets "
            "popped, e.g. a strictly decreasing sequence for `next_greater`)."
        ),
    ),
    dict(
        slug="queues",
        kind="topic",
        topic="queues",
        pattern_family=None,
        title="Queues",
        display_order=1,
        estimated_minutes=16,
        summary="FIFO -- add at the back, remove from the front. The backbone of BFS, and home to the "
                "monotonic deque for tracking a sliding window's max/min in O(1) amortized.",
        prerequisite_slugs="stacks",
        what_markdown=(
            "A queue is FIFO (first-in, first-out): add at the back (`enqueue`), remove from the front "
            "(`dequeue`) -- the opposite discipline from a stack's LIFO. A plain Python list CAN act as a "
            "queue but shouldn't for anything performance-sensitive: `list.pop(0)` is `O(n)` because every "
            "remaining element has to shift down one slot. `collections.deque` gives `O(1)` operations at "
            "BOTH ends instead."
        ),
        why_markdown=(
            "Anywhere \"process things in the order they arrived, layer by layer\" matters, a queue is the "
            "natural fit -- most visibly, BFS (visit everything one step away before anything two steps away). "
            "The less obvious use is the monotonic deque: tracking the max (or min) of a sliding window in one "
            "pass without rescanning the window every time it moves, the queue's own version of the monotonic "
            "stack's trick."
        ),
        recognize_markdown=(
            "**Process in arrival order**: BFS/level-order traversal, rate limiting over a rolling time window. "
            "**Monotonic deque**: the tell is \"track the max (or min) of every sliding window of size k as it "
            "moves across an array,\" in one pass. Recomputing each window's max directly is `O(n*k)`; a heap "
            "works but is `O(n log n)` and awkward to evict expired entries from. A deque that stays monotonic "
            "does it in `O(n)` total."
        ),
        intuition_markdown=(
            "**Basic FIFO**: `deque.append(x)` to enqueue, `deque.popleft()` to dequeue. **Monotonic deque "
            "(sliding-window maximum)**: the deque holds INDICES, not values -- a bare value can't tell you "
            "when it's aged out of the window, but an index can be compared against the current position. At "
            "each step: pop smaller values off the BACK before appending the current index (like a monotonic "
            "stack -- they can never be the max again once a bigger value has arrived), then check whether the "
            "FRONT has fallen outside the window and evict it if so. The front always holds the current "
            "window's max candidate, so reading it is `O(1)` -- no rescanning."
        ),
        walkthrough_intro_markdown=(
            "Trace the sliding-window-maximum technique on `nums = [4, 2, 5, 1]`, `k = 2` -- the max of every "
            "2-element window, in one pass. Only the deque is shown below (as the indices it actually holds, "
            "not the values); `i` and the current value are narrated in each caption."
        ),
        walkthrough_code=(
            "from collections import deque\n\n"
            "def max_sliding_window(nums, k):\n"
            "    dq = deque()  # indices; front always holds the current window's max candidate\n"
            "    result = []\n"
            "    for i, n in enumerate(nums):\n"
            "        while dq and nums[dq[-1]] < n:\n"
            "            dq.pop()\n"
            "        dq.append(i)\n"
            "        if dq[0] <= i - k:\n"
            "            dq.popleft()\n"
            "        if i >= k - 1:\n"
            "            result.append(nums[dq[0]])\n"
            "    return result"
        ),
        walkthrough_frames=[
            dict(caption="i=0, n=4. Deque is empty -- push index 0. deque(indices)=[0]. Window not complete yet (need k=2 values).",
                 locals={"deque": [0]}),
            dict(caption="i=1, n=2. Back-of-deque value (index 0 -> 4) is NOT less than 2, so no pop. Push index 1. deque(indices)=[0, 1]. Window [0,1] is now complete: max = nums[front] = nums[0] = 4.",
                 locals={"deque": [0, 1]}),
            dict(caption="i=2, n=5. Back of deque is index 1 (value 2); 2 < 5, so it can never be the max again once 5 is around -- pop it. deque(indices)=[0]. Still 5 > nums[0]=4, so the while loop keeps popping.",
                 locals={"deque": [0]}),
            dict(caption="Back is now index 0 (value 4); 4 < 5 too, so pop it as well. Deque is now empty. Push index 2. deque(indices)=[2]. Window [1,2]: max = nums[2] = 5.",
                 locals={"deque": [2]}),
            dict(caption="i=3, n=1. Back-of-deque value (index 2 -> 5) is NOT less than 1, so no pop. Push index 3. deque(indices)=[2, 3]. Window [2,3]: max = nums[2] = 5. Loop ends -- the front held each window's max the whole time, with no rescanning.",
                 locals={"deque": [2, 3]}),
        ],
        common_mistakes_markdown=(
            "Using a plain list with `.pop(0)` to dequeue -- `O(n)` per operation since everything shifts, "
            "silently turning an intended `O(n)` algorithm into `O(n^2)`. Use `collections.deque` instead. For "
            "a monotonic deque: forgetting it needs to hold INDICES, not raw values -- a value alone can't "
            "tell you whether it's aged out of the current window, but comparing an index against `i - k` can. "
            "Using `if` instead of `while` when popping smaller values off the back -- the same class of bug "
            "as monotonic stacks. And getting the three steps out of order: pop smaller values from the back, "
            "THEN push the current index, THEN evict an expired front -- doing them in a different order can "
            "let an already-expired index leak into the answer."
        ),
        complexity_markdown=(
            "`collections.deque` gives `O(1)` enqueue/dequeue at both ends. A monotonic deque walk is `O(n)` "
            "total for the whole array despite the `while` nested inside the `for`: each index is pushed once "
            "and popped (from either end) at most once across the entire scan -- the same amortized argument "
            "as monotonic stacks and sliding windows. Compare to `O(n*k)` for recomputing each window's max "
            "directly, or `O(n log n)` for a heap-based approach to the same problem."
        ),
    ),
    # ---- Batch 5: item 7 of the curriculum-ordered expansion -- recursion
    # and backtracking (Days 23-24). Back to the pilot's topic+pattern
    # split (6 curated problems share pattern_family_for's existing
    # "Backtracking" rule -- comparable scale to Two Pointers). See
    # docs/decisions.md "Teaching system expansion: batch 5" for the
    # walkthrough-format decision this batch made (a hand-authored call
    # stack rendered as an ordinary array, NOT CallStackView).
    dict(
        slug="recursion",
        kind="topic",
        topic="recursion",
        pattern_family=None,
        title="Recursion",
        display_order=1,
        estimated_minutes=18,
        summary="A function that calls itself on a smaller version of the same problem, until a base case "
                "stops it -- the foundation trees, backtracking, and DP all build on.",
        prerequisite_slugs="arrays",
        what_markdown=(
            "A recursive function calls itself on a smaller version of the same problem, until it reaches a "
            "**base case** simple enough to answer directly without calling itself again. Every call gets its "
            "own separate set of local variables -- they don't share or overwrite each other -- and Python "
            "tracks all the currently-active (not-yet-returned) calls on the **call stack**, one frame per "
            "call, growing with every call and shrinking with every return."
        ),
        why_markdown=(
            "Some problems have a structure that's naturally self-similar: a tree's subtree is itself a "
            "smaller tree; \"all ways to arrange the rest of the list\" is the same kind of problem as \"all "
            "ways to arrange the whole list\", just smaller. Recursion lets the code mirror that structure "
            "directly -- solve the small piece, trust that the recursive call correctly solves the "
            "smaller-still piece inside it, combine the results -- instead of manually managing an explicit "
            "stack or queue of what's left to do."
        ),
        recognize_markdown=(
            "The tell is a problem that's naturally defined IN TERMS OF a smaller version of itself: tree and "
            "graph traversal (a node's subtree is a smaller tree), \"generate every possible X\" (backtracking "
            "-- the rest of the choices form the same kind of problem as all the choices), and any \"solve for "
            "n using the answer for n-1 or smaller\" relationship (which also often signals dynamic "
            "programming once overlapping subproblems show up). If you find yourself writing \"and then do the "
            "same thing again, but smaller,\" that's recursion."
        ),
        intuition_markdown=(
            "Every recursive function needs two things: a **base case** (input small/simple enough to answer "
            "directly, no further recursion) and a **recursive case** that makes GENUINE progress toward that "
            "base case with each call (a smaller number, a shorter list, one fewer choice left to make) and "
            "combines its own work with the recursive call's result. Trust the recursive call: don't try to "
            "mentally unroll the whole chain of calls at once -- assume the recursive call correctly solves "
            "the smaller problem, and focus only on how THIS call uses that result. Code placed AFTER a "
            "recursive call only runs once that call (and everything it calls) has fully returned -- that's "
            "why a call stack unwinds in the exact reverse order it grew."
        ),
        walkthrough_intro_markdown=(
            "Trace `factorial(4)` -- watch the call stack grow one frame per call as it recurses toward the "
            "base case, then shrink one frame per return as it unwinds back out, each frame finishing its own "
            "multiplication using the value the call below it returned."
        ),
        walkthrough_code=(
            "def factorial(n):\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * factorial(n - 1)"
        ),
        walkthrough_frames=[
            dict(caption="factorial(4) is called. n=4 is not the base case (n <= 1), so it must call factorial(3) before it can return anything itself. The call stack grows by one frame.",
                 locals={"call_stack": ["factorial(4)"]}),
            dict(caption="factorial(3) is called, and itself needs factorial(2) before IT can finish. The stack keeps growing -- each call is 'on hold', waiting for the one below it to return first.",
                 locals={"call_stack": ["factorial(4)", "factorial(3)"]}),
            dict(caption="factorial(2) needs factorial(1) before it can finish.",
                 locals={"call_stack": ["factorial(4)", "factorial(3)", "factorial(2)"]}),
            dict(caption="factorial(1) is called. n=1 -- THIS is the base case. It returns 1 immediately, with no further recursive call. This is the bottom of the recursion; the stack now starts unwinding.",
                 locals={"call_stack": ["factorial(4)", "factorial(3)", "factorial(2)", "factorial(1)"]}),
            dict(caption="factorial(1) returned 1. factorial(2) resumes exactly where it left off, computes 2 * 1 = 2, and returns 2. Its frame is popped off the stack.",
                 locals={"call_stack": ["factorial(4)", "factorial(3)"]}),
            dict(caption="factorial(3) resumes, computes 3 * 2 = 6, and returns 6. Its frame is popped.",
                 locals={"call_stack": ["factorial(4)"]}),
            dict(caption="factorial(4) resumes, computes 4 * 6 = 24, and returns 24. The stack is empty -- every call has now returned, in the exact REVERSE order they were made.",
                 locals={"call_stack": []}),
        ],
        common_mistakes_markdown=(
            "Missing or wrong base case -- the recursion never stops, and Python's call-stack depth limit "
            "eventually raises `RecursionError` (rather than looping forever the way a bad `while` would). The "
            "recursive case not making genuine progress toward the base case (e.g. calling `factorial(n)` "
            "again instead of `factorial(n - 1)`) -- same infinite-recursion symptom, subtler cause. Expecting "
            "code placed AFTER a recursive call to run before deeper calls finish -- it doesn't; that line "
            "only runs once the recursive call (and everything IT calls) has fully returned. And confusing "
            "recursion with a loop that shares one mutable slot across iterations -- each call gets its OWN "
            "copy of its local variables, they don't overwrite each other the way a loop variable does."
        ),
        complexity_markdown=(
            "Linear recursion (each call makes at most one further recursive call, like `factorial`): `O(n)` "
            "time, `O(n)` space -- the space comes from the call stack itself, one frame per still-active "
            "call, unlike an equivalent loop's `O(1)` space. Branching recursion (each call makes 2+ further "
            "calls, e.g. naive Fibonacci recomputing the same values repeatedly) can blow up to `O(2^n)` time "
            "-- covered in more depth in Backtracking and Dynamic Programming."
        ),
    ),
    dict(
        slug="backtracking",
        kind="pattern",
        topic="recursion",
        pattern_family="Backtracking",
        title="Backtracking",
        display_order=2,
        estimated_minutes=20,
        summary="Recursion with an undo step: choose one option, recurse with it, then un-choose it before "
                "trying the next -- exhaustive search that shares work across branches instead of restarting.",
        prerequisite_slugs="recursion",
        what_markdown=(
            "Backtracking is recursion with an UNDO step. Build a partial solution one choice at a time, "
            "recurse deeper with that choice in place, and once that branch is fully explored (a complete "
            "answer was found, it was proven invalid, or every option from here was tried) -- undo the last "
            "choice (**backtrack**) before trying the next option at the same position."
        ),
        why_markdown=(
            "Problems asking for EVERY possible arrangement (every subset, permutation, valid combination) "
            "have no shortcut around exploring the space -- but building each candidate from scratch, from an "
            "empty list every time, wastes all the work shared between similar candidates. Backtracking builds "
            "ONE shared partial solution, extends it, and un-extends it to try the next option: the recursion "
            "tree IS the search space, and the call stack tracks exactly where you currently are inside it."
        ),
        recognize_markdown=(
            "The tell is being asked to enumerate ALL of something -- every subset, every permutation, every "
            "valid combination or arrangement meeting some constraint (N-Queens, valid parentheses) -- not "
            "just find one, and not just COUNT them without listing them (that's more often a dynamic-"
            "programming question). If you're building up a list of choices one at a time, and once a branch "
            "is a dead end or complete you need to step back and try a different choice at that SAME position, "
            "that stepping-back is backtracking."
        ),
        intuition_markdown=(
            "The shape is always the same: choose one option, recurse with it added to the current partial "
            "solution, then UN-choose it (remove it, so the next sibling option starts from a clean partial "
            "solution) before trying the next option. That un-choose step is what makes it backtracking rather "
            "than plain recursion -- skip it, and the partial solution silently corrupts every branch explored "
            "afterward with whatever the previous branch left behind. A base case (the partial solution is "
            "complete) records it and returns; everything else is \"try each remaining option, recurse, then "
            "undo.\""
        ),
        walkthrough_intro_markdown=(
            "Trace `subsets([1, 2])` -- every subset of a 2-element list, built by choosing to include or "
            "exclude each element in turn. `path` (the current partial subset) is shown below; `i` is narrated "
            "in each caption since it never becomes a meaningful array position on its own."
        ),
        walkthrough_code=(
            "def subsets(nums):\n"
            "    result = []\n"
            "    path = []\n"
            "    def backtrack(i):\n"
            "        if i == len(nums):\n"
            "            result.append(path[:])   # a COPY -- not path itself\n"
            "            return\n"
            "        path.append(nums[i])         # choose: include nums[i]\n"
            "        backtrack(i + 1)\n"
            "        path.pop()                   # un-choose\n"
            "        backtrack(i + 1)              # choose: exclude nums[i]\n"
            "    backtrack(0)\n"
            "    return result"
        ),
        walkthrough_frames=[
            dict(caption="backtrack(0): i=0, not yet at the end (len(nums)=2). Choose to include nums[0]=1. path=[1]. Recurse deeper: backtrack(1).",
                 locals={"path": [1]}),
            dict(caption="backtrack(1): i=1, still not at the end. Choose to include nums[1]=2. path=[1, 2]. Recurse deeper: backtrack(2).",
                 locals={"path": [1, 2]}),
            dict(caption="backtrack(2): i=2 == len(nums) -- base case! Record a COPY of path: [1, 2] is one full subset. Return, unwinding one level.",
                 locals={"path": [1, 2]}),
            dict(caption="Back in backtrack(1): the include-2 branch is done. UN-choose: pop 2 off path. path=[1]. Now try the exclude-2 branch: recurse again as backtrack(2), without re-adding 2.",
                 locals={"path": [1]}),
            dict(caption="backtrack(2) again: i=2 == len(nums) -- base case. Record path as-is: [1] is another subset. Return.",
                 locals={"path": [1]}),
            dict(caption="Back in backtrack(0): the include-1 branch is fully done. UN-choose: pop 1 off path. path=[]. Now try the exclude-1 branch: recurse as backtrack(1), with 1 never having been added.",
                 locals={"path": []}),
            dict(caption="backtrack(1) chooses to include nums[1]=2 (path=[2], records [2], then un-chooses back to path=[]), then excludes it too (records []). All four subsets found: [1, 2], [1], [2], [].",
                 locals={"path": []}),
        ],
        common_mistakes_markdown=(
            "Forgetting the UN-choose step itself (e.g. forgetting `path.pop()`) -- leaves stale state in "
            "`path` that corrupts every branch explored after it. Appending `path` directly to `result` "
            "instead of a COPY (`path[:]` or `list(path)`) -- `path` is the SAME mutable list reused "
            "throughout the whole search, so every recorded answer ends up pointing at that one object; later "
            "mutations silently change already-recorded answers too (by the end, everything in `result` "
            "reflects `path`'s FINAL state, not what it looked like when recorded). Not handling duplicate "
            "input values (e.g. Subsets II) -- naive backtracking over a list with repeats produces duplicate "
            "answers; the fix is sorting first and skipping a choice that repeats the immediately-preceding "
            "sibling choice at the same recursion depth. And a missing or wrong base case, same as with plain "
            "recursion -- the search either never terminates or terminates one level early or late."
        ),
        complexity_markdown=(
            "Exponential in general, because the answer itself is that large: enumerating every subset of an "
            "`n`-element set is `O(2^n)` (there are exactly `2^n` subsets); every permutation of `n` elements "
            "is `O(n!)`. The recursion's OWN depth -- and therefore its stack space -- is only `O(n)` though: "
            "one frame per element currently included in the partial solution, not one frame per final answer."
        ),
    ),
    # ---- Batch 6: item 8 of the curriculum-ordered expansion -- binary
    # search (Days 21-22). topic="binary-search" is already a narrow,
    # dedicated topic (not shared with another topic the way "arrays" is
    # shared with Prefix Sums), so both lessons below deliberately leave
    # pattern_family=None -- exactly mirroring the pilot's own
    # topic="two-pointer" / pattern_family=None choice for the Two Pointers
    # lesson -- and both naturally pick up all 7 curated binary-search
    # problems via the plain topic match, with no narrowing needed. See
    # docs/decisions.md "Teaching system expansion: batch 6".
    dict(
        slug="binary-search",
        kind="topic",
        topic="binary-search",
        pattern_family=None,
        title="Binary search",
        display_order=1,
        estimated_minutes=16,
        summary="Cut the search space in half every step instead of scanning linearly -- O(log n) instead of "
                "O(n), and the single most common sub-routine hiding inside harder problems.",
        prerequisite_slugs="arrays",
        what_markdown=(
            "Binary search finds a target in a **sorted** sequence by repeatedly checking the middle element "
            "and discarding the half that can't contain the answer. Keep two boundaries, `lo` and `hi`, "
            "spanning the range still worth checking; each step looks at `mid = (lo + hi) // 2`, compares "
            "`arr[mid]` to the target, and moves whichever boundary rules out the half that's now known to be "
            "wrong. The range shrinks by half every step, so it's gone in `O(log n)` steps."
        ),
        why_markdown=(
            "A linear scan checks every element -- `O(n)` -- because it has no way to rule anything out "
            "without looking at it. Sortedness is what makes ruling things out possible without looking: if "
            "`arr[mid]` is less than the target, EVERY element at or before `mid` is also too small (the "
            "array is sorted), so the entire left half can be discarded in one comparison. That's the whole "
            "trick -- one comparison eliminates half the remaining space, not just one element."
        ),
        recognize_markdown=(
            "The direct case: a sorted array and a target value to locate (or the nearest valid insertion "
            "point). The less obvious case, which shows up constantly in harder problems: any time you can "
            "phrase a question as \"what is the smallest/largest value for which some yes/no condition first "
            "becomes true (or stops being true)\", where that condition is **monotonic** -- true for every "
            "value on one side of a threshold, false on the other -- you can binary search over that value "
            "directly, even if it was never in an array to begin with. Sortedness is really just the simplest "
            "case of monotonicity."
        ),
        intuition_markdown=(
            "Keep the invariant \"the answer, if it exists, is somewhere in `arr[lo..hi]`\" true at every "
            "step. `while lo <= hi` (a closed interval -- `lo == hi` is still one element worth checking): "
            "compute `mid`, compare `arr[mid]` to the target, and move `lo` to `mid + 1` or `hi` to `mid - 1` "
            "-- never to `mid` itself, since `mid` has already been checked and ruled out. Getting that `+1` / "
            "`-1` right is what keeps the loop making progress every step instead of stalling."
        ),
        walkthrough_intro_markdown=(
            "Trace `binary_search([1, 3, 5, 7, 9, 11], 7)` -- watch how `lo` and `hi` close in on index 3 in "
            "three comparisons, instead of scanning up to six elements one at a time."
        ),
        walkthrough_code=(
            "def binary_search(arr, target):\n"
            "    lo, hi = 0, len(arr) - 1\n"
            "    while lo <= hi:\n"
            "        mid = (lo + hi) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            lo = mid + 1\n"
            "        else:\n"
            "            hi = mid - 1\n"
            "    return -1"
        ),
        walkthrough_frames=[
            dict(caption="Search for target=7 in [1, 3, 5, 7, 9, 11]. lo=0, hi=5 -- the whole array is still in play.",
                 locals={"arr": [1, 3, 5, 7, 9, 11], "lo": 0, "hi": 5}),
            dict(caption="mid=(0+5)//2=2. arr[2]=5 is less than target 7, so 7 (if present) must be to the right of mid. Move lo to mid+1=3.",
                 locals={"arr": [1, 3, 5, 7, 9, 11], "lo": 0, "hi": 5, "mid": 2}),
            dict(caption="lo is now 3. Range shrunk to arr[3..5] = [7, 9, 11].",
                 locals={"arr": [1, 3, 5, 7, 9, 11], "lo": 3, "hi": 5}),
            dict(caption="mid=(3+5)//2=4. arr[4]=9 is greater than target 7, so 7 must be to the left of mid. Move hi to mid-1=3.",
                 locals={"arr": [1, 3, 5, 7, 9, 11], "lo": 3, "hi": 5, "mid": 4}),
            dict(caption="hi is now 3. Range shrunk to just arr[3..3] = [7] -- one element left.",
                 locals={"arr": [1, 3, 5, 7, 9, 11], "lo": 3, "hi": 3}),
            dict(caption="mid=(3+3)//2=3. arr[3]=7 equals the target -- found at index 3. Return immediately.",
                 locals={"arr": [1, 3, 5, 7, 9, 11], "lo": 3, "hi": 3, "mid": 3}),
        ],
        common_mistakes_markdown=(
            "Moving a boundary TO `mid` instead of past it (`lo = mid` instead of `lo = mid + 1`) -- when "
            "`hi == lo + 1`, integer division rounds `mid` down to `lo`, so `lo = mid` leaves `lo` completely "
            "unchanged and the loop never makes progress (an infinite loop, not a wrong answer -- often the "
            "more confusing failure mode to debug). Using `while lo < hi` when the logic actually needs the "
            "closed-interval `lo <= hi` (or vice versa) -- the two conventions require different boundary "
            "updates and mixing them is the single most common source of off-by-one bugs here. And assuming "
            "the input is sorted without checking -- binary search on unsorted data doesn't error, it just "
            "silently returns a wrong answer, since the half-elimination logic quietly assumes sortedness."
        ),
        complexity_markdown=(
            "`O(log n)` time -- the search range is cut in half every step, so it takes about `log2(n)` steps "
            "to shrink from `n` elements down to one. `O(1)` extra space for the iterative version shown here "
            "(just `lo`, `hi`, `mid`); a recursive version would be `O(log n)` space for the call stack."
        ),
    ),
    dict(
        slug="binary-search-variants",
        kind="pattern",
        topic="binary-search",
        pattern_family=None,
        title="Binary search variants",
        display_order=2,
        estimated_minutes=18,
        summary="The textbook version rarely shows up as-is in interviews -- searching a rotated array and "
                "binary-searching a monotonic answer space (not an array at all) are the two variants worth "
                "knowing cold.",
        prerequisite_slugs="binary-search",
        what_markdown=(
            "Two variant shapes cover most real interview binary-search questions. **Searching a rotated "
            "sorted array**: the array was sorted, then rotated at some unknown pivot (e.g. `[4, 5, 6, 7, 0, "
            "1, 2]`), so it's no longer sorted end-to-end -- but at every `mid`, one of the two halves around "
            "it IS still fully sorted, and checking which one (and whether the target falls inside that "
            "sorted half's range) is enough to decide which way to go. **Binary search on the answer space**: "
            "there's no array at all -- just a range of candidate answers and a yes/no check function that's "
            "monotonic over that range, and you binary search directly over the candidate VALUES instead of "
            "array indices."
        ),
        why_markdown=(
            "Interviewers rarely hand you the textbook \"find x in a sorted array\" problem directly -- it's "
            "too mechanical to reveal whether you understand WHY binary search works, only whether you "
            "memorized it. Both variants here test the deeper idea (a monotonic property lets you eliminate "
            "half the space with one check) in a shape where the array is no longer sorted, or isn't an array "
            "at all."
        ),
        recognize_markdown=(
            "Rotated-array shape: the problem says a sorted array was \"rotated\" and asks you to search or "
            "find its minimum -- the array LOOKS unsorted overall but still has exploitable local structure. "
            "Answer-space shape: the problem asks for a minimum/maximum value satisfying some condition (\"the "
            "minimum speed such that...\", \"the smallest capacity such that...\"), and increasing the "
            "candidate value only ever makes the condition easier (or only ever harder) to satisfy -- never "
            "flips back and forth. That monotonic \"only easier / only harder as the candidate grows\" "
            "property is the real tell, not the presence of an array."
        ),
        intuition_markdown=(
            "Rotated array: at `mid`, compare `arr[lo]` to `arr[mid]`. If `arr[lo] <= arr[mid]`, the LEFT half "
            "(`lo..mid`) is the sorted one; otherwise the RIGHT half (`mid..hi`) is. Once you know which half "
            "is sorted, a normal range check (`is the target between its two ends?`) tells you whether the "
            "target could be in that sorted half -- if so, search there; if not, it must be in the other "
            "(unsorted-looking, but still valid) half. Answer space: write a helper `works(candidate) -> "
            "bool` that's monotonic over the candidate range, then binary search over the candidates "
            "themselves exactly like the classic version -- `lo`/`hi`/`mid` now hold candidate VALUES instead "
            "of array indices, and `works(mid)` replaces the `arr[mid]` comparison."
        ),
        walkthrough_intro_markdown=(
            "Trace `search_rotated([4, 5, 6, 7, 0, 1, 2], 0)` -- the array was `[0, 1, 2, 4, 5, 6, 7]` before "
            "being rotated. Watch which half gets identified as sorted at each step."
        ),
        walkthrough_code=(
            "def search_rotated(arr, target):\n"
            "    lo, hi = 0, len(arr) - 1\n"
            "    while lo <= hi:\n"
            "        mid = (lo + hi) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        if arr[lo] <= arr[mid]:        # left half is sorted\n"
            "            if arr[lo] <= target < arr[mid]:\n"
            "                hi = mid - 1\n"
            "            else:\n"
            "                lo = mid + 1\n"
            "        else:                           # right half is sorted\n"
            "            if arr[mid] < target <= arr[hi]:\n"
            "                lo = mid + 1\n"
            "            else:\n"
            "                hi = mid - 1\n"
            "    return -1"
        ),
        walkthrough_frames=[
            dict(caption="Search for target=0 in [4, 5, 6, 7, 0, 1, 2]. lo=0, hi=6.",
                 locals={"arr": [4, 5, 6, 7, 0, 1, 2], "lo": 0, "hi": 6}),
            dict(caption="mid=3. arr[3]=7. arr[lo]=4 <= arr[mid]=7, so the LEFT half (indices 0-3, values 4-7) is the sorted one. Is target 0 inside [4, 7)? No. So the target must be in the other half: lo = mid+1 = 4.",
                 locals={"arr": [4, 5, 6, 7, 0, 1, 2], "lo": 0, "hi": 6, "mid": 3}),
            dict(caption="lo is now 4. Range shrunk to arr[4..6] = [0, 1, 2].",
                 locals={"arr": [4, 5, 6, 7, 0, 1, 2], "lo": 4, "hi": 6}),
            dict(caption="mid=5. arr[5]=1. arr[lo]=arr[4]=0 <= arr[mid]=1, so the LEFT half (indices 4-5, values 0-1) is sorted. Is target 0 inside [0, 1)? Yes. Search there: hi = mid-1 = 4.",
                 locals={"arr": [4, 5, 6, 7, 0, 1, 2], "lo": 4, "hi": 6, "mid": 5}),
            dict(caption="hi is now 4. Range shrunk to just arr[4..4] = [0] -- one element left.",
                 locals={"arr": [4, 5, 6, 7, 0, 1, 2], "lo": 4, "hi": 4}),
            dict(caption="mid=4. arr[4]=0 equals the target -- found at index 4. Return immediately.",
                 locals={"arr": [4, 5, 6, 7, 0, 1, 2], "lo": 4, "hi": 4, "mid": 4}),
        ],
        common_mistakes_markdown=(
            "Rotated array: checking `arr[lo] < arr[mid]` (strict) instead of `arr[lo] <= arr[mid]` -- when "
            "the searched range has shrunk to exactly one element, `lo == mid`, and the strict version wrongly "
            "concludes \"neither half is sorted\" instead of correctly treating a single element as trivially "
            "sorted. Also using strict `<` in the target-range check (`arr[lo] < target < arr[mid]`) instead "
            "of `arr[lo] <= target < arr[mid]` -- misses the case where the target IS `arr[lo]` itself, "
            "routing it into the wrong half and losing it. Answer space: forgetting that `works()` needs to "
            "be genuinely monotonic over the WHOLE candidate range -- binary search silently gives a wrong "
            "answer (not an error) if the yes/no condition flips back and forth instead of crossing exactly "
            "one threshold."
        ),
        complexity_markdown=(
            "Rotated-array search stays `O(log n)` -- still one comparison eliminating half the range each "
            "step, just with an extra check first to figure out which half is sorted. Answer-space search is "
            "`O(log R)` steps, where `R` is the size of the candidate range, but each step also calls "
            "`works(candidate)` -- if that check itself costs `O(n)`, the total is `O(n log R)`, not `O(log "
            "R)` alone."
        ),
    ),
    # ---- Batch 7: item 9 of the curriculum-ordered expansion -- sorting
    # (Days 17-20). Days 17-18 (bubble, insertion -- both O(n^2)) and Days
    # 19-20 (merge sort, quicksort -- both O(n log n) divide-and-conquer)
    # are the curriculum's own conceptual split, matching
    # pattern_families.py's own two-family distinction for topic="sorting"
    # ("Sorting fundamentals" vs "Divide and conquer sorting"). The
    # divide-and-conquer walkthrough deliberately visualizes quicksort's
    # partition step, not merge sort's merge step -- merging reads from TWO
    # same-length arrays at once, and ArrayPointerView computes "is this
    # int a valid pointer" independently per rendered sequence (see the
    # Stacks/Queues/Recursion/Backtracking precedent in batches 4-5), so i
    # (a position in `left`) would ALSO render as a misleading chip on
    # `right` (same length, overlapping valid index range), and vice versa
    # for j -- unlike Prefix Sums' arr/prefix, where a shared index IS
    # meaningful on both sequences. Partition works on one array with i/j
    # as genuinely single-array pointers, sidestepping the hazard
    # entirely -- and it's the more forward-looking concept anyway (Day
    # 20's own curriculum content already calls out that partition logic
    # reappears in quickselect). See docs/decisions.md "Teaching system
    # expansion: batch 7".
    dict(
        slug="sorting",
        kind="topic",
        topic="sorting",
        pattern_family=None,
        title="Sorting: comparison-based fundamentals",
        display_order=1,
        estimated_minutes=16,
        summary="Bubble sort and insertion sort -- the two simplest ways to sort by repeated comparison and "
                "swap/shift, both O(n^2), and the baseline everything faster is measured against.",
        prerequisite_slugs="arrays",
        what_markdown=(
            "Two different O(n^2) strategies for sorting by comparing elements. **Bubble sort** repeatedly "
            "scans the array, swapping any ADJACENT pair that's out of order, so the largest unsorted element "
            "\"bubbles\" to its correct position each full pass. **Insertion sort** grows a sorted prefix one "
            "element at a time: it takes the next element (`key`) and SHIFTS everything in the sorted prefix "
            "that's bigger than it one slot to the right, opening up the correct gap to insert `key` into."
        ),
        why_markdown=(
            "Neither is what you'd reach for to sort a large array in practice (`arr.sort()` and the "
            "divide-and-conquer sorts exist for that) -- but both are the clearest possible illustration of "
            "\"an algorithm as a sequence of comparisons and swaps,\" and insertion sort specifically is the "
            "conceptual bridge to merge sort: merge sort is really just insertion sort's \"grow a sorted "
            "region\" idea, sped up by splitting the work recursively instead of growing one element at a "
            "time."
        ),
        recognize_markdown=(
            "You won't often reach for bubble or insertion sort to solve an interview problem directly -- the "
            "value here is recognizing their SHAPE inside other problems: a nested loop that compares "
            "adjacent elements and swaps (bubble sort's shape) shows up in problems about counting "
            "inversions or adjacent-swap distance; \"shift elements right to open a gap\" (insertion sort's "
            "shape) shows up anywhere you're inserting into an already-sorted structure one item at a time."
        ),
        intuition_markdown=(
            "Insertion sort's inner loop has to be a `while`, not an `if`, for the same reason a sliding "
            "window's shrink step does: opening up the correct gap for `key` can take more than one shift. If "
            "`key` needs to move all the way from the end of the array to the front, EVERY element in the "
            "sorted prefix shifts right by one, one comparison and one shift at a time, until `key` finally "
            "finds a spot (or the front of the array) where the element to its left is no longer bigger."
        ),
        walkthrough_intro_markdown=(
            "Trace `insertion_sort([5, 2, 4, 1, 3])`. Watch `i=3` (`key=1`) closely -- it takes three shifts "
            "to move `1` all the way from index 3 to the front, exactly the multi-step `while` case."
        ),
        walkthrough_code=(
            "def insertion_sort(arr):\n"
            "    for i in range(1, len(arr)):\n"
            "        key = arr[i]\n"
            "        j = i - 1\n"
            "        while j >= 0 and arr[j] > key:\n"
            "            arr[j + 1] = arr[j]\n"
            "            j -= 1\n"
            "        arr[j + 1] = key\n"
            "    return arr"
        ),
        walkthrough_frames=[
            dict(caption="i=1: the sorted prefix is just arr[0:1]=[5]. key=arr[1]=2. j starts at i-1=0. arr[0]=5 is greater than key -- shift it right and keep scanning left.",
                 locals={"arr": [5, 2, 4, 1, 3], "i": 1, "j": 0}),
            dict(caption="j has gone below 0 -- shifted past the start of the array. Place key=2 at arr[0]. arr=[2, 5, 4, 1, 3]. Sorted prefix is now [2, 5].",
                 locals={"arr": [2, 5, 4, 1, 3], "i": 1, "j": -1}),
            dict(caption="i=2: key=arr[2]=4. arr[1]=5 is greater than key -- one shift; then arr[0]=2 is not greater than key, so the while loop stops. Place key at arr[1]. arr=[2, 4, 5, 1, 3]. Sorted prefix is now [2, 4, 5].",
                 locals={"arr": [2, 4, 5, 1, 3], "i": 2, "j": 0}),
            dict(caption="i=3: key=arr[3]=1. arr[2]=5 > key -- shift. j becomes 1. arr[1]=4 is STILL greater than key -- one shift isn't enough, the while loop keeps going.",
                 locals={"arr": [2, 4, 5, 5, 3], "i": 3, "j": 1}),
            dict(caption="Shift again: arr[1]=4 > key, shift, j becomes 0. arr[0]=2 is ALSO greater than key -- a third shift is needed.",
                 locals={"arr": [2, 4, 4, 5, 3], "i": 3, "j": 0}),
            dict(caption="After the third shift j becomes -1 and the loop finally stops. Place key=1 at arr[0]. arr=[1, 2, 4, 5, 3]. Three shifts were needed to open a path all the way to the front -- exactly why this has to be a while loop, not an if.",
                 locals={"arr": [1, 2, 4, 5, 3], "i": 3, "j": -1}),
            dict(caption="i=4: key=arr[4]=3 needs two shifts to reach index 2. Final result: arr=[1, 2, 3, 4, 5] -- fully sorted.",
                 locals={"arr": [1, 2, 3, 4, 5], "i": 4, "j": 1}),
        ],
        common_mistakes_markdown=(
            "Writing the inner while condition as `while arr[j] > key` and forgetting the `j >= 0` check -- "
            "once `j` goes negative, Python doesn't error immediately: `arr[j]` silently wraps around and "
            "reads from the END of the list (`arr[-1]`, `arr[-2]`, ...), corrupting the shift with unrelated "
            "elements for several steps before eventually crashing once `j` passes `-len(arr)`. Confusing "
            "bubble sort's SWAP (exchange two adjacent elements) with insertion sort's SHIFT (move one "
            "element over, without touching the one it passed) -- they look superficially similar but are "
            "different operations with different costs. And assuming either is stable or fast enough for "
            "large inputs by default -- both are correct, but `O(n^2)` for arbitrary input, not a substitute "
            "for `arr.sort()` or the divide-and-conquer sorts in real code."
        ),
        complexity_markdown=(
            "`O(n^2)` in the worst case for both (`n` elements, each potentially needing up to `n` "
            "comparisons/shifts against every other element) -- reverse-sorted input is the worst case for "
            "insertion sort specifically, since every new element has to shift all the way to the front. "
            "`O(1)` extra space for both -- everything happens in place, no second array allocated."
        ),
    ),
    dict(
        slug="divide-and-conquer-sorting",
        kind="pattern",
        topic="sorting",
        pattern_family="Divide and conquer sorting",
        title="Divide-and-conquer sorting",
        display_order=2,
        estimated_minutes=20,
        summary="Merge sort and quicksort both break the array into smaller pieces first -- turning O(n^2) "
                "into O(n log n), and quicksort's partition step reappears constantly in its own right.",
        prerequisite_slugs="sorting,recursion",
        what_markdown=(
            "Both merge sort and quicksort are recursive: they split the array, recursively sort the pieces, "
            "then combine. **Merge sort** splits down the middle unconditionally (no comparisons needed to "
            "split), sorts each half recursively, then does the real work in a `merge` step that combines two "
            "already-sorted halves into one sorted array in a single linear pass. **Quicksort** does the "
            "opposite: the real work happens in a `partition` step BEFORE recursing -- pick a pivot, "
            "rearrange the array so everything `<= pivot` ends up to its left and everything greater ends up "
            "to its right (with the pivot landing in its final sorted position), then recurse on the two "
            "sides independently. Neither recursive call needs to touch the other side ever again."
        ),
        why_markdown=(
            "Both simple sorts (bubble, insertion) do `O(n)` work, `n` times over -- `O(n^2)` total. Splitting "
            "the array first is what breaks that: a problem of size `n` becomes two problems of size `n/2`, "
            "so the recursion is only `O(log n)` levels deep, and each level -- summed across every piece at "
            "that level -- still only does `O(n)` total work (a full merge, or a full partition). `O(log n)` "
            "levels times `O(n)` work per level is `O(n log n)`, which is the single biggest complexity jump "
            "in the whole curriculum: doubling the input size adds one more level of recursion, not double "
            "the work."
        ),
        recognize_markdown=(
            "You're very rarely asked to implement merge sort or quicksort from scratch as the actual "
            "interview question -- the reason this pattern matters is that PARTITION reappears constantly on "
            "its own, stripped of the recursion around it: \"find the kth smallest/largest element\" "
            "(quickselect -- partition, then recurse into only the ONE side that contains index k, never "
            "both), \"move all elements matching some condition to one side\" (Dutch national flag / "
            "partitioning problems), and the general idea of \"split, solve independently, no further work "
            "needed to combine\" is worth recognizing whenever a problem's brute force is `O(n^2)` but the two "
            "halves of a split genuinely don't interact."
        ),
        intuition_markdown=(
            "Partition's invariant, one comparison at a time: keep an index `i` marking the boundary of "
            "\"everything confirmed `<= pivot` so far\" (`arr[lo..i]`), and scan forward with `j`. Whenever "
            "`arr[j] <= pivot`, advance `i` and swap `arr[i]` with `arr[j]` -- this grows the confirmed region "
            "by exactly one element without disturbing its invariant. Once `j` has scanned the whole range, "
            "one final swap drops the pivot itself into position `i + 1`, which is now guaranteed correct: "
            "everything to its left is `<= pivot`, everything to its right is not."
        ),
        walkthrough_intro_markdown=(
            "Trace `partition([8, 3, 1, 9, 5, 4], lo=0, hi=5)` -- pivot is `arr[hi]=4`. Watch how `i` only "
            "advances (and a swap happens) exactly when `arr[j] <= pivot`."
        ),
        walkthrough_code=(
            "def partition(arr, lo, hi):\n"
            "    pivot = arr[hi]\n"
            "    i = lo - 1\n"
            "    for j in range(lo, hi):\n"
            "        if arr[j] <= pivot:\n"
            "            i += 1\n"
            "            arr[i], arr[j] = arr[j], arr[i]\n"
            "    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]\n"
            "    return i + 1"
        ),
        walkthrough_frames=[
            dict(caption="Partition arr around pivot=arr[hi]=4. i marks the boundary of the 'confirmed <= pivot' region (empty so far, since i starts at lo-1=-1). j=0: arr[0]=8 is greater than pivot -- leave it, move on.",
                 locals={"arr": [8, 3, 1, 9, 5, 4], "j": 0}),
            dict(caption="j=1: arr[1]=3 is <= pivot -- it belongs in the left region. Advance i to 0 and swap arr[i] with arr[j].",
                 locals={"arr": [8, 3, 1, 9, 5, 4], "i": 0, "j": 1}),
            dict(caption="After the swap: arr=[3, 8, 1, 9, 5, 4]. The confirmed region arr[0..i]=[3] now correctly holds only values <= pivot.",
                 locals={"arr": [3, 8, 1, 9, 5, 4], "i": 0, "j": 1}),
            dict(caption="j=2: arr[2]=1 is <= pivot -- advance i to 1 and swap arr[i] with arr[j].",
                 locals={"arr": [3, 8, 1, 9, 5, 4], "i": 1, "j": 2}),
            dict(caption="After the swap: arr=[3, 1, 8, 9, 5, 4]. Confirmed region arr[0..1]=[3, 1] is still all <= pivot.",
                 locals={"arr": [3, 1, 8, 9, 5, 4], "i": 1, "j": 2}),
            dict(caption="j=3 and j=4: arr[3]=9 and arr[4]=5 are both greater than pivot -- left in place, i doesn't move either time.",
                 locals={"arr": [3, 1, 8, 9, 5, 4], "i": 1, "j": 4}),
            dict(caption="Scan done. Final swap drops the pivot into its correct position i+1=2: arr=[3, 1, 4, 9, 5, 8]. Everything left of index 2 is <= 4; everything right is greater -- the pivot never needs to move again.",
                 locals={"arr": [3, 1, 4, 9, 5, 8], "i": 1, "j": 4}),
        ],
        common_mistakes_markdown=(
            "Forgetting the final swap (`arr[i + 1], arr[hi] = arr[hi], arr[i + 1]`) that actually moves the "
            "pivot from `arr[hi]` into its confirmed position -- the function still returns `i + 1` as if the "
            "pivot were there, but it isn't; the two recursive calls then split around the wrong index and "
            "silently produce a scrambled result, working correctly only on inputs where the pivot happened "
            "to already belong at `hi`. Always picking the LAST element as the pivot on already-sorted (or "
            "reverse-sorted) input -- every partition step splits off just one element instead of roughly "
            "half, degrading quicksort from `O(n log n)` to `O(n^2)`, which is why real implementations "
            "randomize the pivot choice or pick a median-of-three. And merge sort specifically: forgetting to "
            "copy the remaining tail of whichever half didn't run out first -- one side is always exhausted "
            "before the other, and its leftover elements (already sorted) just get appended, no more "
            "comparisons needed."
        ),
        complexity_markdown=(
            "`O(n log n)` average case for both: `O(log n)` levels of recursion (the array roughly halves, or "
            "partitions roughly in half on average, each level), and `O(n)` total work summed across every "
            "piece at a single level (a full merge, or a full partition pass). Quicksort's WORST case is "
            "`O(n^2)` -- a consistently bad pivot choice (e.g. always picking an extreme value on sorted "
            "input) turns `log n` levels into `n` levels. Merge sort has no such worst case (`O(n log n)` "
            "always) but needs `O(n)` extra space for the merge step; quicksort partitions in place, `O(log "
            "n)` extra space for the recursion stack."
        ),
    ),
    # ---- Batch 8: item 10 of the curriculum-ordered expansion -- trees
    # (Days 30-32). Three lessons, matching the curriculum's own three-day
    # split (structure/traversals, BSTs, height/level-order) rather than
    # pattern_families.py's coarser two-family split for topic="trees"
    # ("Tree DFS recursion" vs "Tree BFS / level order") -- BSTs have 3
    # dedicated curated problems (the same backing count that justified
    # Fast/Slow Pointers as its own lesson in batch 3) and a whole
    # dedicated curriculum day, but no clean pattern_family of their own
    # (their pattern strings -- "DFS with bounds", "in-order traversal for
    # rank" -- don't share a keyword pattern_families.py's rules match
    # distinctly from the general DFS bucket). Rather than invent a new
    # family rule just to serve lesson-narrowing (which would touch the
    # shared taxonomy every other feature reads too), all three lessons
    # below leave pattern_family unset for BSTs specifically and rely on
    # lesson content/walkthroughs to make clear which of the topic's
    # related problems are BST-specific -- see docs/decisions.md "Teaching
    # system expansion: batch 8" for the full reasoning.
    #
    # First topic needing TreeView (see ConceptWalkthrough.jsx's
    # buildTreeGraph adapter, added this batch, parallel to
    # buildLinkedListGraph from batch 3) -- trees, like linked lists,
    # aren't array-shaped, and TreeView shares LinkedListView's same
    # Map/roots graph shape and the same ordered-pointers-list requirement
    # (the tree's actual root must be authored FIRST in `pointers`).
    dict(
        slug="trees",
        kind="topic",
        topic="trees",
        pattern_family=None,
        title="Trees: structure and traversal",
        display_order=1,
        estimated_minutes=18,
        summary="A node holding a value plus references to its children -- the recursive base-case-is-null "
                "pattern this lesson builds, and the three DFS visiting orders (preorder/inorder/postorder).",
        prerequisite_slugs="recursion",
        what_markdown=(
            "A binary tree is a node structure: each node holds a value and up to two child references "
            "(`.left`, `.right`), each of which is either another node or `None`. There's no single \"first\" "
            "or \"last\" element the way an array has -- just a `root` node you reach every other node FROM, by "
            "following `.left`/`.right` references. **Traversal** means visiting every node in some order; the "
            "three DFS orders differ only in WHEN a node is visited relative to its children: **preorder** "
            "(node, then left subtree, then right subtree), **inorder** (left, then node, then right), "
            "**postorder** (left, then right, then node)."
        ),
        why_markdown=(
            "Trees are where recursion and node/reference structures combine -- almost every tree function has "
            "the exact same skeleton: `if node is None: return <base case>`, then recurse into `node.left` and "
            "`node.right`, then combine their results. Once that skeleton is second nature, the actual "
            "per-problem logic (what to do at each node, how to combine children's results) is usually the "
            "only real work left."
        ),
        recognize_markdown=(
            "Any problem operating on a binary tree (given as `root`) is reaching for this skeleton by "
            "default. The traversal ORDER matters for the specific problem: preorder is natural when you need "
            "the node's own value before its children's (e.g. copying/serializing a tree top-down); inorder "
            "is the one to reach for on a BST specifically (see the next lesson -- it visits nodes in sorted "
            "order); postorder is natural whenever a node needs its CHILDREN's answers before it can compute "
            "its own (height, diameter, \"is this subtree balanced\")."
        ),
        intuition_markdown=(
            "Every recursive tree function answers two questions: what's the base case (almost always `node "
            "is None` -- an empty subtree), and how do I combine this node's own value with whatever my "
            "recursive calls into `node.left` and `node.right` returned? Get comfortable with that shape and "
            "most tree problems become \"what do I compute at each node, and how do I combine\" instead of "
            "\"how do I even traverse this.\""
        ),
        walkthrough_intro_markdown=(
            "Trace `preorder(node, result)` on a small tree, collecting values into `result` as it visits each "
            "node BEFORE recursing into its children. `result`'s growing contents are narrated in each "
            "caption rather than rendered as a second view here, so the walkthrough can focus on how `node` "
            "moves around the tree structure itself."
        ),
        walkthrough_code=(
            "def preorder(node, result):\n"
            "    if node is None:\n"
            "        return\n"
            "    result.append(node.val)\n"
            "    preorder(node.left, result)\n"
            "    preorder(node.right, result)"
        ),
        walkthrough_frames=[
            dict(caption="Start at the root, node=1. Visit it FIRST (preorder visits before recursing): result=[1]. Then recurse left into node 2.",
                 locals={"nodes": [
                     {"id": 0, "val": 1, "left": 1, "right": 2},
                     {"id": 1, "val": 2, "left": 3, "right": 4},
                     {"id": 2, "val": 3, "left": None, "right": None},
                     {"id": 3, "val": 4, "left": None, "right": None},
                     {"id": 4, "val": 5, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 0]]}),
            dict(caption="node=2. Visit it: result=[1, 2]. Recurse left into node 4.",
                 locals={"nodes": [
                     {"id": 0, "val": 1, "left": 1, "right": 2},
                     {"id": 1, "val": 2, "left": 3, "right": 4},
                     {"id": 2, "val": 3, "left": None, "right": None},
                     {"id": 3, "val": 4, "left": None, "right": None},
                     {"id": 4, "val": 5, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 1]]}),
            dict(caption="node=4. Visit it: result=[1, 2, 4]. Both children are None -- base case, return immediately with nothing further added.",
                 locals={"nodes": [
                     {"id": 0, "val": 1, "left": 1, "right": 2},
                     {"id": 1, "val": 2, "left": 3, "right": 4},
                     {"id": 2, "val": 3, "left": None, "right": None},
                     {"id": 3, "val": 4, "left": None, "right": None},
                     {"id": 4, "val": 5, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 3]]}),
            dict(caption="Back at node 2 -- its left subtree (just node 4) is fully done. Recurse right into node 5.",
                 locals={"nodes": [
                     {"id": 0, "val": 1, "left": 1, "right": 2},
                     {"id": 1, "val": 2, "left": 3, "right": 4},
                     {"id": 2, "val": 3, "left": None, "right": None},
                     {"id": 3, "val": 4, "left": None, "right": None},
                     {"id": 4, "val": 5, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 1]]}),
            dict(caption="node=5. Visit it: result=[1, 2, 4, 5]. Both children are None -- return.",
                 locals={"nodes": [
                     {"id": 0, "val": 1, "left": 1, "right": 2},
                     {"id": 1, "val": 2, "left": 3, "right": 4},
                     {"id": 2, "val": 3, "left": None, "right": None},
                     {"id": 3, "val": 4, "left": None, "right": None},
                     {"id": 4, "val": 5, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 4]]}),
            dict(caption="Back at the root -- its entire left subtree (2, 4, 5) is fully done. Recurse right into node 3.",
                 locals={"nodes": [
                     {"id": 0, "val": 1, "left": 1, "right": 2},
                     {"id": 1, "val": 2, "left": 3, "right": 4},
                     {"id": 2, "val": 3, "left": None, "right": None},
                     {"id": 3, "val": 4, "left": None, "right": None},
                     {"id": 4, "val": 5, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 0]]}),
            dict(caption="node=3. Visit it: result=[1, 2, 4, 5, 3]. Both children are None -- return. Every node visited -- final preorder result: [1, 2, 4, 5, 3].",
                 locals={"nodes": [
                     {"id": 0, "val": 1, "left": 1, "right": 2},
                     {"id": 1, "val": 2, "left": 3, "right": 4},
                     {"id": 2, "val": 3, "left": None, "right": None},
                     {"id": 3, "val": 4, "left": None, "right": None},
                     {"id": 4, "val": 5, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 2]]}),
        ],
        common_mistakes_markdown=(
            "Forgetting the `if node is None: return` base case entirely -- the very next line almost always "
            "touches `node.val` or `node.left`, so a missing base case crashes with an `AttributeError` on "
            "`None` rather than silently doing nothing. Mixing up the three traversal orders -- inorder is "
            "specifically `left, node, right` (not `node, left, right`), and using the wrong one on a BST "
            "problem (see the next lesson) silently returns values in the wrong order rather than erroring. "
            "And building a NEW list at every recursive call instead of passing one accumulator down (or "
            "returning and concatenating, which is correct but easy to do inefficiently) -- concatenating "
            "lists at every level turns an `O(n)` traversal into `O(n^2)`."
        ),
        complexity_markdown=(
            "`O(n)` time -- every node is visited exactly once, regardless of traversal order. `O(h)` space "
            "for the recursion stack, where `h` is the tree's height: `O(log n)` for a balanced tree, but "
            "`O(n)` worst case for a completely skewed tree (every node has only one child, so it's really "
            "just a linked list in disguise)."
        ),
    ),
    dict(
        slug="binary-search-trees",
        kind="pattern",
        topic="trees",
        pattern_family=None,
        title="Binary search trees",
        display_order=2,
        estimated_minutes=18,
        summary="Every node's left subtree is smaller, right subtree is larger -- and validating that "
                "property correctly means tracking a (low, high) RANGE, not just comparing a node to its "
                "immediate parent.",
        prerequisite_slugs="trees,binary-search",
        what_markdown=(
            "A binary search tree (BST) is a binary tree with one extra invariant: for every node, EVERY "
            "value in its left subtree is less than the node's value, and EVERY value in its right subtree is "
            "greater -- not just the node's immediate children, the WHOLE subtree. That property is what "
            "connects BSTs back to binary search: at any node, comparing your target to `node.val` tells you "
            "which entire subtree to search next, discarding the other half in one comparison, the same "
            "`O(log n)` idea as searching a sorted array (on a balanced tree; a degenerate/skewed BST loses "
            "that guarantee)."
        ),
        why_markdown=(
            "The BST invariant makes three operations cheap on a balanced tree: search, insert, and delete "
            "are all `O(log n)`, versus `O(n)` for an unordered tree or a plain list. It also gives you a free "
            "side effect worth remembering: an INORDER traversal of a BST visits every node in sorted order, "
            "since inorder is `left, node, right` -- exactly \"everything smaller, then me, then everything "
            "bigger\", recursively."
        ),
        recognize_markdown=(
            "The tell is a tree that's explicitly described as (or built to be) a binary search tree, or a "
            "problem asking you to validate, search, insert into, or find the kth smallest/largest value in "
            "one. \"Kth smallest in a BST\" is really \"the kth value visited during an inorder traversal\" -- "
            "recognizing that connection turns a seemingly search-heavy problem into a straightforward "
            "traversal-with-a-counter."
        ),
        intuition_markdown=(
            "Validating a BST is the classic place a beginner's first instinct (compare each node to its "
            "immediate parent) goes wrong: it misses violations from an ANCESTOR further up the tree, not "
            "just the direct parent. The fix is to carry a `(low, high)` range down through the recursion -- "
            "every node must fall strictly inside its inherited range, and each recursive call narrows that "
            "range further (the left child's new upper bound becomes the current node's value; the right "
            "child's new lower bound does too). A node can satisfy its immediate parent while still violating "
            "a bound inherited from higher up -- the range is what catches that."
        ),
        walkthrough_intro_markdown=(
            "Trace `is_valid_bst(node, low, high)` on the same tree shape from the previous lesson. Watch how "
            "`low`/`high` (narrated in captions -- they're values, not tree positions) tighten as the walk "
            "goes deeper, and specifically why node 4's check needs BOTH its inherited bounds, not just a "
            "comparison to its parent."
        ),
        walkthrough_code=(
            "def is_valid_bst(node, low=float('-inf'), high=float('inf')):\n"
            "    if node is None:\n"
            "        return True\n"
            "    if not (low < node.val < high):\n"
            "        return False\n"
            "    return (is_valid_bst(node.left, low, node.val) and\n"
            "            is_valid_bst(node.right, node.val, high))"
        ),
        walkthrough_frames=[
            dict(caption="Start at the root, node=5, bounds (-inf, inf) -- no constraint yet. Is -inf < 5 < inf? Yes. Recurse left with an updated upper bound: everything in the left subtree must stay below 5.",
                 locals={"nodes": [
                     {"id": 0, "val": 5, "left": 1, "right": 2},
                     {"id": 1, "val": 3, "left": 3, "right": 4},
                     {"id": 2, "val": 8, "left": None, "right": None},
                     {"id": 3, "val": 1, "left": None, "right": None},
                     {"id": 4, "val": 4, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 0]]}),
            dict(caption="node=3, bounds (-inf, 5). Is -inf < 3 < 5? Yes. Recurse left with bounds (-inf, 3) -- 3's left subtree must stay below 3 too.",
                 locals={"nodes": [
                     {"id": 0, "val": 5, "left": 1, "right": 2},
                     {"id": 1, "val": 3, "left": 3, "right": 4},
                     {"id": 2, "val": 8, "left": None, "right": None},
                     {"id": 3, "val": 1, "left": None, "right": None},
                     {"id": 4, "val": 4, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 1]]}),
            dict(caption="node=1, bounds (-inf, 3). Is -inf < 1 < 3? Yes. Both children are None -- base case, return True immediately.",
                 locals={"nodes": [
                     {"id": 0, "val": 5, "left": 1, "right": 2},
                     {"id": 1, "val": 3, "left": 3, "right": 4},
                     {"id": 2, "val": 8, "left": None, "right": None},
                     {"id": 3, "val": 1, "left": None, "right": None},
                     {"id": 4, "val": 4, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 3]]}),
            dict(caption="Back at node 3 -- its left side checked out. Recurse right with bounds (3, 5): must stay ABOVE 3 (its own left-subtree floor) AND BELOW 5 (inherited from 5's own left-subtree ceiling).",
                 locals={"nodes": [
                     {"id": 0, "val": 5, "left": 1, "right": 2},
                     {"id": 1, "val": 3, "left": 3, "right": 4},
                     {"id": 2, "val": 8, "left": None, "right": None},
                     {"id": 3, "val": 1, "left": None, "right": None},
                     {"id": 4, "val": 4, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 1]]}),
            dict(caption="node=4, bounds (3, 5). Is 3 < 4 < 5? Yes -- this is exactly the check a PARENT-ONLY comparison would get right by luck here, but the bound (3, 5) is what actually GUARANTEES it, since it also remembers the constraint inherited from higher up. Both children are None -- return True.",
                 locals={"nodes": [
                     {"id": 0, "val": 5, "left": 1, "right": 2},
                     {"id": 1, "val": 3, "left": 3, "right": 4},
                     {"id": 2, "val": 8, "left": None, "right": None},
                     {"id": 3, "val": 1, "left": None, "right": None},
                     {"id": 4, "val": 4, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 4]]}),
            dict(caption="Back at the root -- its entire left subtree (3, 1, 4) checked out. Recurse right with bounds (5, inf): everything in the right subtree must be greater than 5.",
                 locals={"nodes": [
                     {"id": 0, "val": 5, "left": 1, "right": 2},
                     {"id": 1, "val": 3, "left": 3, "right": 4},
                     {"id": 2, "val": 8, "left": None, "right": None},
                     {"id": 3, "val": 1, "left": None, "right": None},
                     {"id": 4, "val": 4, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 0]]}),
            dict(caption="node=8, bounds (5, inf). Is 5 < 8 < inf? Yes. Both children are None -- return True. Every node satisfied its bounds -- the whole tree is a valid BST.",
                 locals={"nodes": [
                     {"id": 0, "val": 5, "left": 1, "right": 2},
                     {"id": 1, "val": 3, "left": 3, "right": 4},
                     {"id": 2, "val": 8, "left": None, "right": None},
                     {"id": 3, "val": 1, "left": None, "right": None},
                     {"id": 4, "val": 4, "left": None, "right": None},
                 ], "pointers": [["root", 0], ["node", 2]]}),
        ],
        common_mistakes_markdown=(
            "Comparing each node only to its immediate parent (`node.left.val < node.val < node.right.val`) "
            "instead of carrying bounds down -- this misses violations from an ancestor further up the tree: "
            "a node can be perfectly valid relative to its direct parent while still breaking the invariant "
            "relative to a grandparent or higher. Forgetting that BOTH bounds narrow as you descend, not just "
            "one -- a left child inherits a new upper bound (its parent's value) but keeps the SAME lower "
            "bound its parent had; a right child is the mirror image. And using `<=`/`>=` instead of strict "
            "`<`/`>` when the problem specifies no duplicate values are allowed -- an equal value should fail "
            "validation, not pass it."
        ),
        complexity_markdown=(
            "`O(n)` time -- still visits every node once. `O(h)` space for the recursion stack, same as any "
            "tree DFS (`O(log n)` balanced, `O(n)` worst case skewed). Search/insert/delete on an actual BST "
            "(not full validation) are `O(h)` each -- `O(log n)` on a balanced tree, but `O(n)` worst case if "
            "the tree has degenerated into a linked-list shape (e.g. built by inserting already-sorted data "
            "with no rebalancing)."
        ),
    ),
    dict(
        slug="tree-bfs",
        kind="pattern",
        topic="trees",
        pattern_family="Tree BFS / level order",
        title="Tree BFS: level order",
        display_order=3,
        estimated_minutes=16,
        summary="Process a tree level by level using a queue -- FIFO order naturally groups nodes by "
                "distance from the root, and this is the direct conceptual predecessor to graph BFS.",
        prerequisite_slugs="trees,queues",
        what_markdown=(
            "Level-order traversal visits every node breadth-first: the root first, then all of its "
            "children, then all of ITS children's children, and so on -- one full level at a time, left to "
            "right. Unlike the DFS traversals from the topic lesson (which dive all the way down one branch "
            "before backtracking), level order needs a QUEUE, not the recursion call stack: enqueue the root, "
            "then repeatedly dequeue a node, record it, and enqueue its children."
        ),
        why_markdown=(
            "A queue is FIFO -- first in, first out -- which is exactly what \"process in order of distance "
            "from the root\" needs: everything enqueued during level `k` (the children discovered while "
            "processing level `k`'s nodes) naturally comes out AFTER everything already in the queue from "
            "level `k` itself, since it was enqueued later. This is also the direct conceptual predecessor to "
            "graph BFS -- the exact same queue-based idea, generalized with a visited set once the structure "
            "being explored can have cycles."
        ),
        recognize_markdown=(
            "The tell is needing to group nodes by DEPTH/distance from the root -- \"return each level as its "
            "own list\", \"find the value at the last node of each level\" (right-side view), \"find the "
            "minimum depth\" (the FIRST leaf a level-order scan reaches). Any DFS traversal visits nodes in "
            "the wrong order for these -- depth-grouping is a breadth-first question, not a depth-first one."
        ),
        intuition_markdown=(
            "The one trick that makes level-by-level grouping possible with a plain queue (no per-node "
            "\"depth\" field needed): snapshot the queue's CURRENT length before the inner loop starts, then "
            "process exactly that many nodes. Everything already in the queue at that snapshot moment IS the "
            "current level, in full; anything enqueued DURING this pass (the current level's children) can't "
            "be processed until the next pass, because the snapshot count runs out first -- that's what keeps "
            "one level's nodes from bleeding into the next."
        ),
        walkthrough_intro_markdown=(
            "Trace `level_order(root)` on the same tree shape from the topic lesson. This walkthrough shows "
            "the QUEUE's contents (reusing the same array/pointer view every non-tree lesson uses, not the "
            "tree structure itself, since the topic lesson already covered that) -- watch it drain and refill "
            "as each level is processed."
        ),
        walkthrough_code=(
            "def level_order(root):\n"
            "    result = []\n"
            "    q = deque([root])\n"
            "    while q:\n"
            "        level_size = len(q)\n"
            "        level_vals = []\n"
            "        for _ in range(level_size):\n"
            "            node = q.popleft()\n"
            "            level_vals.append(node.val)\n"
            "            if node.left:\n"
            "                q.append(node.left)\n"
            "            if node.right:\n"
            "                q.append(node.right)\n"
            "        result.append(level_vals)\n"
            "    return result"
        ),
        walkthrough_frames=[
            dict(caption="Start: queue holds just the root, [1]. This is level 0 -- level_size will snapshot to 1.",
                 locals={"queue": [1]}),
            dict(caption="Dequeue 1, record it (level 0 = [1]). Enqueue its children left to right: 2, then 3.",
                 locals={"queue": [2, 3]}),
            dict(caption="Level 0's snapshot (1 node) is used up -- everything now in the queue is level 1. Dequeue 2, record it. Enqueue its children: 4, then 5.",
                 locals={"queue": [3, 4, 5]}),
            dict(caption="Dequeue 3, record it (level 1 = [2, 3] complete). 3 has no children -- nothing enqueued.",
                 locals={"queue": [4, 5]}),
            dict(caption="Level 1's snapshot (2 nodes) is used up -- everything now in the queue is level 2. Dequeue 4, record it. No children.",
                 locals={"queue": [5]}),
            dict(caption="Dequeue 5, record it (level 2 = [4, 5] complete). No children. Queue is now empty -- BFS is done.",
                 locals={"queue": []}),
            dict(caption="Final result, grouped level by level: [[1], [2, 3], [4, 5]]. The snapshot-then-drain trick is what separated each level without ever storing a depth on the nodes themselves.",
                 locals={"queue": []}),
        ],
        common_mistakes_markdown=(
            "Skipping the level-size snapshot entirely and just draining the queue node by node into one flat "
            "list -- this still visits every node in breadth-first ORDER, but loses the level GROUPING "
            "entirely, which is usually the actual point of the problem. Enqueueing `None` children -- "
            "checking `if node.left:` before appending (not appending unconditionally) keeps the queue from "
            "filling up with values that would crash the next `node.val` access. And confusing this with DFS "
            "level tracking (passing a `depth` parameter down a recursive call) -- that approach also works "
            "and is sometimes simpler for depth-only questions, but doesn't naturally give you \"stop after "
            "the first level satisfying some condition\" the way an explicitly queue-driven scan does, since "
            "it doesn't process strictly nearest-nodes-first."
        ),
        complexity_markdown=(
            "`O(n)` time -- every node is enqueued and dequeued exactly once. `O(n)` space worst case for the "
            "queue -- a tree's widest level can hold up to roughly `n/2` nodes (a complete binary tree's last "
            "level), so the queue's peak size scales with the tree's WIDTH, not its height, unlike DFS's "
            "stack which scales with height."
        ),
    ),
    # ---- Batch 9: item 11 of the curriculum-ordered expansion -- heaps
    # (Days 33-34). Two lessons, matching the curriculum's own two-day
    # split (heap concept/heapq, then the top-K pattern specifically) --
    # continuing the same departure from strict pattern_family-backing
    # that batch 8 made explicit for BSTs: pattern_families.py has only
    # ONE rule for topic="heaps" ("Heap / top-K selection", covering all 7
    # curated problems with no sub-split), so top-k-heap leaves
    # pattern_family unset like heaps itself, same tradeoff as
    # binary-search-trees. HeapView (Visualizers.jsx) needs no new
    # ConceptWalkthrough.jsx adapter at all -- unlike LinkedListView/
    # TreeView, it takes locals directly (any numeric-list-shaped local
    # is rendered as its own heap-tree via plain 2i+1/2i+2 index math, no
    # Map/graph construction), so both lessons just pass locals={"heap":
    # [...]} straight through, selected via topic === 'heaps'. See
    # docs/decisions.md "Teaching system expansion: batch 9".
    dict(
        slug="heaps",
        kind="topic",
        topic="heaps",
        pattern_family=None,
        title="Heaps: priority queues",
        display_order=1,
        estimated_minutes=17,
        summary="A binary tree (stored as a plain array) that only guarantees a parent is smaller than its "
                "children -- weaker than fully sorted, which is exactly why push/pop are O(log n) instead of "
                "needing a full re-sort.",
        prerequisite_slugs="trees",
        what_markdown=(
            "A (min-)heap is a complete binary tree where every parent is `<=` both of its children -- "
            "weaker than a sorted order (siblings and cousins have no guaranteed relationship to each other), "
            "which is exactly what makes it cheap to maintain. It's stored as a plain array: the node at "
            "index `i` has children at `2i + 1` and `2i + 2`, so no pointers or node objects are needed at "
            "all. Python's `heapq` module gives you a MIN-heap on a plain list: `heapq.heappush(heap, x)` "
            "adds `x` and restores the invariant; `heapq.heappop(heap)` removes and returns the smallest "
            "element, then restores the invariant among what's left."
        ),
        why_markdown=(
            "If you only need the min/max ONCE, sort or scan. But if you need to repeatedly pull the current "
            "min/max while the collection keeps changing (new elements arriving, or one at a time being "
            "removed), a heap keeps that operation at `O(log n)` every time, instead of `O(n)` per scan or "
            "`O(n log n)` to re-sort after every change. `heapq.heapify(list)` even converts an existing list "
            "into a valid heap in `O(n)`, not `O(n log n)` -- cheaper than pushing every element one at a "
            "time."
        ),
        recognize_markdown=(
            "The tell is needing the current smallest/largest of a collection repeatedly, especially while "
            "the collection keeps changing -- \"process tasks by priority\", \"merge K sorted lists/streams\", "
            "\"find the running median\", or the top-K pattern this batch's other lesson builds on top of "
            "this one. If you only need the min/max ONE time and the collection is static, a heap is overkill "
            "-- `min()`/`max()` or a single sort is simpler and just as fast."
        ),
        intuition_markdown=(
            "Both `heappush` and `heappop` work by fixing the invariant along a SINGLE path from root to leaf "
            "(or leaf to root), never touching the rest of the tree -- that's the whole reason they're "
            "`O(log n)` (the tree's height) instead of `O(n)`. Pushing: append the new value at the next open "
            "slot, then \"sift up\" -- repeatedly compare it to its parent and swap if it's smaller, stopping "
            "once it isn't (or it reaches the root). Popping: save the root (the value being returned), move "
            "the LAST element into the root's spot, then \"sift down\" -- repeatedly swap it with its smaller "
            "child, stopping once it's smaller than both children (or has none). Sift-up and sift-down are "
            "both loops for the same reason a sliding window's shrink step is: one swap doesn't always finish "
            "the job."
        ),
        walkthrough_intro_markdown=(
            "Trace four `heappush` calls building a heap from scratch, then one `heappop`. Watch the fourth "
            "push (`1`) closely -- it needs two separate sift-up swaps to bubble all the way to the root."
        ),
        walkthrough_code=(
            "import heapq\n"
            "heap = []\n"
            "heapq.heappush(heap, 5)\n"
            "heapq.heappush(heap, 3)\n"
            "heapq.heappush(heap, 8)\n"
            "heapq.heappush(heap, 1)\n"
            "heapq.heappop(heap)"
        ),
        walkthrough_frames=[
            dict(caption="heappush(heap, 5): heap starts empty, so 5 becomes the only element (trivially the root).",
                 locals={"heap": [5]}),
            dict(caption="heappush(heap, 3): 3 is appended at index 1. Its parent (index 0) is 5 -- 3 < 5, so sift up: swap.",
                 locals={"heap": [3, 5]}),
            dict(caption="heappush(heap, 8): 8 is appended at index 2. Its parent (index 0) is 3 -- 8 is NOT less than 3, so no swap needed. The invariant already holds.",
                 locals={"heap": [3, 5, 8]}),
            dict(caption="heappush(heap, 1): 1 is appended at index 3. Its parent (index 1) is 5. 1 < 5 -- sift up begins: swap.",
                 locals={"heap": [3, 5, 8, 1]}),
            dict(caption="1 is now at index 1. Its NEW parent (index 0) is 3. 1 < 3 -- sift up continues: swap again.",
                 locals={"heap": [3, 1, 8, 5]}),
            dict(caption="1 is now at index 0 (the root), which has no parent -- sift-up stops. Two swaps were needed to bubble 1 all the way up -- exactly why sift-up is a loop, not a single comparison.",
                 locals={"heap": [1, 3, 8, 5]}),
            dict(caption="heappop(heap): removes and returns the root, 1 (the minimum). The LAST element (5) moves into the root's spot, then sifts DOWN -- swapping with its smaller child (3, at index 1) since 5 > 3. Final heap: [3, 5, 8].",
                 locals={"heap": [3, 5, 8]}),
        ],
        common_mistakes_markdown=(
            "Building a heap by just `.append()`-ing values instead of `heapq.heappush()` (or `heapq.heapify()` "
            "once at the end) -- a list built this way LOOKS like a heap but never had its invariant "
            "established, so `heapq.heappop()` on it silently returns the wrong \"minimum\" instead of "
            "erroring, since `heappop` only fixes up the structure around the root it removes, not the whole "
            "list. Needing a MAX-heap and reaching for a different data structure -- `heapq` is min-heap only, "
            "but negating every value on the way in (and negating again on the way out) turns it into a "
            "working max-heap with no extra code. And assuming a heap is fully sorted -- popping repeatedly "
            "DOES yield sorted order, but the array itself, at any given moment, is only heap-valid, not "
            "sorted (compare `heap[1]` and `heap[2]` in any frame above -- neither is guaranteed smaller)."
        ),
        complexity_markdown=(
            "`O(log n)` per `heappush`/`heappop` (bounded by the tree's height). `O(n)` for `heapq.heapify()` "
            "on an existing list (cheaper than `n` individual pushes, which would be `O(n log n)`). Repeatedly "
            "extracting the min/max `n` times, one at a time, is therefore `O(n log n)` total -- better than "
            "`O(n^2)` from repeatedly scanning linearly for the min, and avoids re-sorting the whole "
            "collection (also `O(n log n)`, but redundantly, on every single change)."
        ),
    ),
    dict(
        slug="top-k-heap",
        kind="pattern",
        topic="heaps",
        pattern_family=None,
        title="Top-K with a bounded heap",
        display_order=2,
        estimated_minutes=16,
        summary="Find the K largest (or smallest) of n values by keeping a heap of size AT MOST K, evicting "
                "the current worst candidate whenever a better one arrives -- O(n log k), not O(n log n).",
        prerequisite_slugs="heaps",
        what_markdown=(
            "To find the K LARGEST values among n candidates, keep a MIN-heap bounded to size `k` -- not a "
            "max-heap, which is the intuitive-sounding but less efficient choice. Push every candidate; "
            "whenever the heap's size exceeds `k`, pop the minimum. That pop evicts the current WORST of your "
            "top-K candidates -- anything smaller than the heap's current minimum can't possibly belong in "
            "the true top K, so it's safe to discard. At the end, the heap holds exactly the K largest values "
            "seen, and its root is the Kth largest overall."
        ),
        why_markdown=(
            "Keeping every element in a full-size heap (or sorting everything) costs `O(n log n)`. Bounding "
            "the heap to size `k` keeps every push/pop to `O(log k)` instead of `O(log n)` -- when `k` is much "
            "smaller than `n` (the 5 largest among a million streaming values), that's a real difference, and "
            "the heap never needs to hold more than `k` elements at once."
        ),
        recognize_markdown=(
            "\"Find the K largest/smallest\", \"K closest points\", \"top K frequent elements\", \"Kth largest "
            "in a stream\" (where new values keep arriving and the answer must stay current) -- any \"best K "
            "of N\" question, especially when N is large or arrives incrementally, is reaching for a bounded "
            "heap. If K is close to N, a full sort is simpler and just as fast; the bounded-heap technique "
            "earns its complexity specifically when K is small relative to N."
        ),
        intuition_markdown=(
            "The counterintuitive part worth internalizing: for the K LARGEST values, you bound a MIN-heap "
            "(not a max-heap). The heap's root is always the SMALLEST of your current top-K candidates -- "
            "which is precisely the one value you want fast access to, since it's the one that gets evicted "
            "the moment something bigger shows up. A max-heap would put the wrong end (the current largest, "
            "which you never need to evict) at the root instead."
        ),
        walkthrough_intro_markdown=(
            "Trace finding the 3 largest values from the stream `[4, 1, 7, 3, 9, 2]` using a min-heap bounded "
            "to size 3. Watch the last push (`2`) closely -- it gets evicted immediately, since it's smaller "
            "than everything already confirmed to be in the top 3."
        ),
        walkthrough_code=(
            "def top_k_largest(nums, k):\n"
            "    heap = []\n"
            "    for n in nums:\n"
            "        heapq.heappush(heap, n)\n"
            "        if len(heap) > k:\n"
            "            heapq.heappop(heap)\n"
            "    return heap"
        ),
        walkthrough_frames=[
            dict(caption="Push 4. heap=[4], size 1 (<= k=3) -- no eviction needed.",
                 locals={"heap": [4]}),
            dict(caption="Push 1. heap=[1, 4], size 2 (<= 3) -- no eviction needed.",
                 locals={"heap": [1, 4]}),
            dict(caption="Push 7. heap=[1, 4, 7], size 3 (== k) -- the heap is now full, but still no eviction needed.",
                 locals={"heap": [1, 4, 7]}),
            dict(caption="Push 3. Size is now 4, exceeding k=3 -- pop the minimum (1). 1 is now confirmed NOT among the 3 largest, since 3 other values already beat it.",
                 locals={"heap": [3, 4, 7]}),
            dict(caption="Push 9. Size becomes 4 again -- pop the minimum (3). heap=[4, 9, 7].",
                 locals={"heap": [4, 9, 7]}),
            dict(caption="Push 2. Size becomes 4 again -- pop the minimum. Since 2 IS the new minimum, it gets evicted right back out, changing nothing.",
                 locals={"heap": [4, 9, 7]}),
            dict(caption="Every value processed. Final heap=[4, 9, 7] -- confirmed to be the 3 largest values seen: 9, 7, 4 (the heap's own array order isn't sorted order, just the heap invariant).",
                 locals={"heap": [4, 9, 7]}),
        ],
        common_mistakes_markdown=(
            "Using a MAX-heap instead of a bounded min-heap for \"K largest\" -- it works, but a full max-heap "
            "of all `n` elements costs `O(n log n)` and doesn't let you cheaply discard bad candidates the way "
            "a size-bounded min-heap does. Forgetting the `if len(heap) > k: heapq.heappop(heap)` check after "
            "every push -- without it the heap grows unbounded, silently returning ALL `n` elements instead "
            "of just the top `k`, and losing the entire `O(n log k)` benefit. And assuming the returned heap "
            "is already in sorted order -- it holds the right SET of values, but reading it out in ranked "
            "order needs additional pops (or a final `sorted()` call), same as any heap."
        ),
        complexity_markdown=(
            "`O(n log k)` time -- each of the `n` pushes (and the pops that follow when the heap overflows) "
            "costs `O(log k)`, since the heap never holds more than `k + 1` elements at once. `O(k)` space, "
            "regardless of how large `n` is -- the heap's size is capped by `k`, not by the input."
        ),
    ),
    # ---- Batch 10: item 12 of the curriculum-ordered expansion -- graphs
    # (Days 35-38). Four lessons, matching the curriculum's own four-day
    # split (representation, BFS, DFS, Dijkstra) -- pattern_families.py
    # actually has FOUR graph rules already (Grid BFS / Grid DFS-flood-fill
    # / Graph shortest paths / Graph DFS-cycle-detection), more granular
    # than heaps' single rule, but they don't line up cleanly with these
    # four LESSONS either: Day 36's own two curated problems (Number of
    # Islands = grid BFS, Rotting Oranges = multi-source BFS) land in TWO
    # different families under pattern_family_for's ordered rules, and Day
    # 37's two (Max Area of Island = grid DFS, Course Schedule = cycle
    # detection) likewise split across two families. Only graph-shortest-
    # paths gets a real pattern_family below ("Graph shortest paths" --
    # Network Delay Time, Rotting Oranges, Word Ladder, and Clone Graph all
    # land there under the existing rules, a reasonable "Apply it" list);
    # graphs/graph-bfs/graph-dfs leave it unset, same tradeoff as batches 8
    # and 9 -- see docs/decisions.md "Teaching system expansion: batch 10".
    #
    # Two different node shapes needed, both already distinguished by
    # detectPrimaryView (detect.js) in the REAL trace system: a node-and-
    # edge graph (GraphNodeView, needing a small adapter parallel to
    # buildTreeGraph/buildLinkedListGraph -- see buildGraphNodeGraph in
    # ConceptWalkthrough.jsx) for graphs and graph-dfs, and a grid
    # (GridGraphView, which -- like HeapView -- takes locals directly, no
    # adapter) for graph-bfs, matching which of Day 36's two problem shapes
    # each lesson's own walkthrough demonstrates. graph-shortest-paths also
    # uses GraphNodeView, encoding each node's live `dist` into its label
    # text (e.g. "A d=3") since GraphNodeView has no separate side-panel
    # for auxiliary state -- the same "narrate what the view can't render"
    # tradeoff graph-bfs makes for its queue and graph-dfs makes for its
    # on_stack (shown as pointer tags instead, since on_stack is a set of
    # NODES rather than a separate value).
    dict(
        slug="graphs",
        kind="topic",
        topic="graphs",
        pattern_family=None,
        title="Graphs: representation & terminology",
        display_order=1,
        estimated_minutes=13,
        summary="A graph is nodes plus edges -- the general structure trees, linked lists, and even grids "
                "are all special cases of. Build one as an adjacency list and read off a node's neighbors "
                "and degree.",
        prerequisite_slugs="trees",
        what_markdown=(
            "A graph is a set of nodes (vertices) plus a set of connections between them (edges). The "
            "cheapest common representation is an ADJACENCY LIST: a dict mapping each node to a list of its "
            "neighbors. For an UNDIRECTED edge (a connection with no direction, like a friendship or a road), "
            "record it in BOTH nodes' lists -- `graph.setdefault(a, []).append(b)` and the same with `a` and "
            "`b` swapped. A node's DEGREE is simply the length of its neighbor list."
        ),
        why_markdown=(
            "A tree only models strictly hierarchical relationships -- one parent per node, no cycles. Most "
            "real relationships aren't like that: road networks, course prerequisites, social connections, "
            "and word-transformation chains can all link back to something already seen, or have a node "
            "reachable through more than one path. A graph is what you reach for the moment a relationship "
            "isn't a strict hierarchy."
        ),
        recognize_markdown=(
            "\"model connections/relationships between items\", \"prerequisites\" (course A requires course "
            "B), \"friend network\", \"cities connected by roads\", \"can you get from X to Y\". The tell "
            "that distinguishes it from a tree: a node can have more than one incoming connection, or a path "
            "can loop back to somewhere it's already been."
        ),
        intuition_markdown=(
            "An adjacency list costs `O(V + E)` total -- it only stores edges that actually exist. The "
            "alternative, an ADJACENCY MATRIX (a `V x V` grid where cell `[i][j]` marks an edge from `i` to "
            "`j`), costs `O(V^2)` regardless of how few edges exist -- worth it only when the graph is dense "
            "(most possible edges exist) or you need O(1) \"is there an edge between i and j\" lookups. And a "
            "GRID (the next two lessons) is itself an implicit graph with no adjacency list ever built: each "
            "cell is a node, and each up/down/left/right step is an edge, all computed by index math."
        ),
        walkthrough_intro_markdown=(
            "Trace building an adjacency-list graph from an edge list one edge at a time, then look up a "
            "node's neighbors and degree."
        ),
        walkthrough_code=(
            "def build_graph(edges):\n"
            "    graph = {}\n"
            "    for a, b in edges:\n"
            "        graph.setdefault(a, []).append(b)\n"
            "        graph.setdefault(b, []).append(a)\n"
            "    return graph\n\n"
            "edges = [('A', 'B'), ('B', 'C'), ('A', 'C'), ('C', 'D')]\n"
            "graph = build_graph(edges)\n"
            "graph['C']  # C's neighbors"
        ),
        walkthrough_frames=[
            dict(caption="edges=[(A,B),(B,C),(A,C),(C,D)]. Process (A,B): append B to A's list AND A to B's "
                          "list -- both directions, since this is an undirected graph. graph={'A':['B'], "
                          "'B':['A']}.",
                 locals={"nodes": [{"id": 0, "val": "A", "neighbors": [1]}, {"id": 1, "val": "B", "neighbors": [0]}],
                         "pointers": []}),
            dict(caption="Process (B,C): B gets C appended (B=['A','C']), C gets B appended (C=['B']). "
                          "graph={'A':['B'], 'B':['A','C'], 'C':['B']}.",
                 locals={"nodes": [{"id": 0, "val": "A", "neighbors": [1]}, {"id": 1, "val": "B", "neighbors": [0, 2]},
                                    {"id": 2, "val": "C", "neighbors": [1]}],
                         "pointers": []}),
            dict(caption="Process (A,C): A=['B','C'], C=['B','A']. This closes a loop -- A connects to B, B "
                          "connects to C, and now C connects straight back to A. Unlike a tree, a graph "
                          "allows exactly this: a path that returns to where it started, called a CYCLE.",
                 locals={"nodes": [{"id": 0, "val": "A", "neighbors": [1, 2]}, {"id": 1, "val": "B", "neighbors": [0, 2]},
                                    {"id": 2, "val": "C", "neighbors": [1, 0]}],
                         "pointers": []}),
            dict(caption="Process (C,D): C=['B','A','D'], D=['C']. All 4 edges processed -- "
                          "graph={'A':['B','C'], 'B':['A','C'], 'C':['B','A','D'], 'D':['C']}.",
                 locals={"nodes": [{"id": 0, "val": "A", "neighbors": [1, 2]}, {"id": 1, "val": "B", "neighbors": [0, 2]},
                                    {"id": 2, "val": "C", "neighbors": [1, 0, 3]}, {"id": 3, "val": "D", "neighbors": [2]}],
                         "pointers": []}),
            dict(caption="graph['C'] -> ['B', 'A', 'D']. C's DEGREE (its neighbor count) is 3 -- more "
                          "connections than any other node here, since it sits at the junction of the cycle "
                          "and the branch to D.",
                 locals={"nodes": [{"id": 0, "val": "A", "neighbors": [1, 2]}, {"id": 1, "val": "B", "neighbors": [0, 2]},
                                    {"id": 2, "val": "C", "neighbors": [1, 0, 3]}, {"id": 3, "val": "D", "neighbors": [2]}],
                         "pointers": [["current", 2]]}),
            dict(caption="This dict-of-lists is an ADJACENCY LIST -- cheap (O(V+E) total) because it only "
                          "stores edges that actually exist. For GRID problems specifically (the next two "
                          "lessons), the grid itself already IS an implicit graph: each cell is a node, and "
                          "up/down/left/right moves are edges, with no adjacency list ever built explicitly.",
                 locals={"nodes": [{"id": 0, "val": "A", "neighbors": [1, 2]}, {"id": 1, "val": "B", "neighbors": [0, 2]},
                                    {"id": 2, "val": "C", "neighbors": [1, 0, 3]}, {"id": 3, "val": "D", "neighbors": [2]}],
                         "pointers": [["current", 2]]}),
        ],
        common_mistakes_markdown=(
            "Forgetting the reverse append for an undirected edge -- `graph.setdefault(a, []).append(b)` "
            "alone silently builds a DIRECTED graph (A -> B only); looking up B's neighbors then misses A "
            "entirely, with no error to catch it. Confusing degree (a node's OWN neighbor count) with the "
            "graph's total edge count. And assuming a graph has no cycles -- that's specifically a TREE; a "
            "general graph allows a path to loop back to somewhere it's already been."
        ),
        complexity_markdown=(
            "`O(V + E)` to build an adjacency list from `E` edges over `V` nodes -- every edge triggers a "
            "constant amount of work, and every node gets at least an empty list entry. `O(1)` average to "
            "look up a given node's neighbor list. An adjacency MATRIX instead costs `O(V^2)` memory "
            "regardless of how few edges exist -- only worth it for dense graphs or O(1) edge-existence checks."
        ),
    ),
    dict(
        slug="graph-bfs",
        kind="pattern",
        topic="graphs",
        pattern_family=None,
        title="Graph BFS: shortest paths in unweighted graphs",
        display_order=2,
        estimated_minutes=16,
        summary="BFS explores a graph (or grid) one full 'ring' of distance at a time -- so the FIRST time "
                "it reaches any node is guaranteed to be via the shortest possible path, as long as every "
                "edge costs the same.",
        prerequisite_slugs="graphs,queues",
        what_markdown=(
            "Graph BFS uses a queue (FIFO), exactly like Day 32's tree level-order, plus one addition: a "
            "VISITED set, since a graph (unlike a tree) can have cycles and multiple paths to the same node. "
            "Mark a node visited the MOMENT it's enqueued, not when it's dequeued -- that's what guarantees "
            "each node is only ever added to the queue once."
        ),
        why_markdown=(
            "DFS also visits every reachable node, but with no distance guarantee -- it can stumble onto a "
            "long, winding path to a node before ever trying the short direct one. BFS's FIFO order "
            "guarantees nodes are dequeued in nondecreasing distance from the source: every node at distance "
            "1 is dequeued before any node at distance 2, and so on. So the FIRST time BFS reaches any given "
            "node is always via the shortest possible path -- as long as every edge costs the same."
        ),
        recognize_markdown=(
            "\"fewest steps/minimum moves\" in an unweighted grid or graph, \"shortest path\" with no "
            "mention of varying costs, \"levels/rings outward from a start\", or just \"everything reachable "
            "from a start\" (a BFS flood-fill counts exactly like a DFS one would, just via a queue instead "
            "of the call stack). If edges have DIFFERENT costs, BFS alone no longer guarantees shortest -- "
            "that's the next lesson."
        ),
        intuition_markdown=(
            "The one detail that actually matters: mark a cell visited the moment you ENQUEUE it, not when "
            "you dequeue it. Marking at dequeue time still gives a correct final answer (with a guard that "
            "skips an already-visited pop), but the SAME cell can be pushed onto the queue multiple times -- "
            "once from each unvisited neighbor that reaches it -- before it's ever processed even once, doing "
            "far more work than necessary."
        ),
        walkthrough_intro_markdown=(
            "Trace a BFS flood-fill count from (0,0) over a small grid, counting every connected 1-cell "
            "reachable from the start."
        ),
        walkthrough_code=(
            "from collections import deque\n\n"
            "def bfs_count_island(grid, sr, sc):\n"
            "    rows, cols = len(grid), len(grid[0])\n"
            "    visited = {(sr, sc)}\n"
            "    queue = deque([(sr, sc)])\n"
            "    count = 0\n"
            "    while queue:\n"
            "        r, c = queue.popleft()\n"
            "        count += 1\n"
            "        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n"
            "            nr, nc = r + dr, c + dc\n"
            "            if (0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1\n"
            "                    and (nr, nc) not in visited):\n"
            "                visited.add((nr, nc))\n"
            "                queue.append((nr, nc))\n"
            "    return count"
        ),
        walkthrough_frames=[
            dict(caption="grid=[[1,1,0],[0,1,0],[0,1,1]]. Start: enqueue (0,0), mark it visited. "
                          "queue=[(0,0)].",
                 locals={"grid": [[1, 1, 0], [0, 1, 0], [0, 1, 1]], "r": 0, "c": 0}),
            dict(caption="Pop (0,0), count=1. Check its 4 neighbors: only (0,1) is an unvisited 1-cell -- "
                          "mark it visited, enqueue it. queue=[(0,1)].",
                 locals={"grid": [[1, 1, 0], [0, 1, 0], [0, 1, 1]], "r": 0, "c": 0}),
            dict(caption="Pop (0,1), count=2. Its only unvisited 1-neighbor is (1,1) -- enqueue it. "
                          "queue=[(1,1)].",
                 locals={"grid": [[1, 1, 0], [0, 1, 0], [0, 1, 1]], "r": 0, "c": 1}),
            dict(caption="Pop (1,1), count=3. Unvisited 1-neighbor: (2,1). queue=[(2,1)].",
                 locals={"grid": [[1, 1, 0], [0, 1, 0], [0, 1, 1]], "r": 1, "c": 1}),
            dict(caption="Pop (2,1), count=4. Unvisited 1-neighbor: (2,2). queue=[(2,2)].",
                 locals={"grid": [[1, 1, 0], [0, 1, 0], [0, 1, 1]], "r": 2, "c": 1}),
            dict(caption="Pop (2,2), count=5. No unvisited neighbors -- the queue is now empty.",
                 locals={"grid": [[1, 1, 0], [0, 1, 0], [0, 1, 1]], "r": 2, "c": 2}),
            dict(caption="queue empty -- BFS done, count=5 (this whole island). Because every cell was "
                          "enqueued the FIRST time it was reached, and BFS processes strictly in enqueue "
                          "order, tracking distance-from-start the same way would guarantee each cell's "
                          "first-recorded distance is its true shortest distance.",
                 locals={"grid": [[1, 1, 0], [0, 1, 0], [0, 1, 1]], "r": 2, "c": 2}),
        ],
        common_mistakes_markdown=(
            "Marking a cell visited at POP time instead of ENQUEUE time -- still correct with a guard, but "
            "lets the same cell get pushed onto the queue many times before it's ever processed once, doing "
            "needless extra work. Reaching for DFS when the problem specifically needs the SHORTEST path or "
            "fewest steps -- DFS finds A path to every reachable node, but not necessarily the shortest one. "
            "And forgetting the visited set entirely on a graph with cycles -- unlike a tree, a graph can "
            "send BFS back to a node it already processed, looping forever without one."
        ),
        complexity_markdown=(
            "`O(V + E)` for a general graph, or `O(rows * cols)` for a grid -- every node/cell is enqueued "
            "and dequeued at most once, and every edge (or grid neighbor) is examined a constant number of "
            "times."
        ),
    ),
    dict(
        slug="graph-dfs",
        kind="pattern",
        topic="graphs",
        pattern_family=None,
        title="Graph DFS: cycle detection with an explicit stack",
        display_order=3,
        estimated_minutes=17,
        summary="DFS explores as deep as possible before backtracking -- and for detecting a CYCLE in a "
                "directed graph, the key insight is tracking which nodes are on the CURRENT path (on_stack), "
                "not just which have ever been visited.",
        prerequisite_slugs="graphs,recursion",
        what_markdown=(
            "Recursive DFS visits a node, recurses into each unvisited neighbor, then backtracks. For cycle "
            "detection specifically, track TWO sets: `visited` (nodes ever fully explored) and `on_stack` "
            "(nodes on the CURRENT call chain, right now). A \"back edge\" -- an edge pointing to a node "
            "that's still in `on_stack` -- means the graph has a cycle."
        ),
        why_markdown=(
            "A plain `visited` set alone can't tell the difference between \"reached this node via a "
            "DIFFERENT path\" (completely normal in a graph, and NOT a cycle) and \"looped back to an "
            "ancestor on THIS exact path\" (a real cycle). Day 37's own framing is that this DFS uses an "
            "EXPLICIT stack, reinforcing Day 23's call-stack lesson: each nested `has_cycle` call is one more "
            "frame pushed, and `on_stack` is simply a set that mirrors, at any moment, exactly which frames "
            "are currently live."
        ),
        recognize_markdown=(
            "\"detect a cycle in a directed graph\", \"can these prerequisites/dependencies all be "
            "completed\", \"is a valid ordering (topological sort) even possible\" -- any \"is there a "
            "cycle\" question on a directed graph is this pattern."
        ),
        intuition_markdown=(
            "Picture a DAG shaped like a diamond: two different paths (through different intermediate nodes) "
            "both lead to the SAME downstream node. That downstream node gets visited twice, by two "
            "different ancestors -- completely normal, not a cycle. Checking \"have I EVER visited this "
            "node\" would wrongly flag it. Checking \"is this node on my CURRENT path right now\" correctly "
            "doesn't."
        ),
        walkthrough_intro_markdown=(
            "Trace has_cycle detecting a real cycle: D -> A -> B -> C -> A. Watch what happens when C looks "
            "at its neighbor A, which is still on the current call stack."
        ),
        walkthrough_code=(
            "def has_cycle(graph, node, on_stack, visited):\n"
            "    visited.add(node)\n"
            "    on_stack.add(node)\n"
            "    for nxt in graph[node]:\n"
            "        if nxt in on_stack:\n"
            "            return True\n"
            "        if nxt not in visited and has_cycle(graph, nxt, on_stack, visited):\n"
            "            return True\n"
            "    on_stack.discard(node)\n"
            "    return False\n\n"
            "graph = {'D': ['A'], 'A': ['B'], 'B': ['C'], 'C': ['A']}\n"
            "has_cycle(graph, 'D', set(), set())"
        ),
        walkthrough_frames=[
            dict(caption="has_cycle(graph, 'D', ...): visited={D}, on_stack={D} -- the tag marks it. D's "
                          "only neighbor is A, not yet visited -- recurse.",
                 locals={"nodes": [{"id": 0, "val": "D", "neighbors": [1]}, {"id": 1, "val": "A", "neighbors": [2]},
                                    {"id": 2, "val": "B", "neighbors": [3]}, {"id": 3, "val": "C", "neighbors": [1]}],
                         "pointers": [["on_stack: D", 0]]}),
            dict(caption="has_cycle(graph, 'A', ...): on_stack={D,A}. This is a NEW call frame -- exactly "
                          "the explicit-stack point from Day 23, one frame per node on the current path. A's "
                          "neighbor B isn't visited -- recurse.",
                 locals={"nodes": [{"id": 0, "val": "D", "neighbors": [1]}, {"id": 1, "val": "A", "neighbors": [2]},
                                    {"id": 2, "val": "B", "neighbors": [3]}, {"id": 3, "val": "C", "neighbors": [1]}],
                         "pointers": [["on_stack: D", 0], ["on_stack: A", 1]]}),
            dict(caption="has_cycle(graph, 'B', ...): on_stack={D,A,B}. B's neighbor C isn't visited -- "
                          "recurse.",
                 locals={"nodes": [{"id": 0, "val": "D", "neighbors": [1]}, {"id": 1, "val": "A", "neighbors": [2]},
                                    {"id": 2, "val": "B", "neighbors": [3]}, {"id": 3, "val": "C", "neighbors": [1]}],
                         "pointers": [["on_stack: D", 0], ["on_stack: A", 1], ["on_stack: B", 2]]}),
            dict(caption="has_cycle(graph, 'C', ...): on_stack={D,A,B,C}. C's only neighbor is A.",
                 locals={"nodes": [{"id": 0, "val": "D", "neighbors": [1]}, {"id": 1, "val": "A", "neighbors": [2]},
                                    {"id": 2, "val": "B", "neighbors": [3]}, {"id": 3, "val": "C", "neighbors": [1]}],
                         "pointers": [["on_stack: D", 0], ["on_stack: A", 1], ["on_stack: B", 2], ["on_stack: C", 3]]}),
            dict(caption="Is A in on_stack? YES -- A is still tagged 'on_stack: A', meaning it's an ancestor "
                          "on THIS exact path (D -> A -> B -> C -> A). That's a back edge -- a real cycle. "
                          "Return True immediately; no need to keep exploring.",
                 locals={"nodes": [{"id": 0, "val": "D", "neighbors": [1]}, {"id": 1, "val": "A", "neighbors": [2]},
                                    {"id": 2, "val": "B", "neighbors": [3]}, {"id": 3, "val": "C", "neighbors": [1]}],
                         "pointers": [["on_stack: D", 0], ["on_stack: A", 1], ["on_stack: B", 2], ["on_stack: C", 3]]}),
            dict(caption="Contrast: if C's only neighbor were some OTHER already-visited node reached via a "
                          "different branch (not currently on_stack), that would be a completely normal "
                          "shared descendant -- not a cycle. The check is specifically `nxt in on_stack`, "
                          "never just `nxt in visited`.",
                 locals={"nodes": [{"id": 0, "val": "D", "neighbors": [1]}, {"id": 1, "val": "A", "neighbors": [2]},
                                    {"id": 2, "val": "B", "neighbors": [3]}, {"id": 3, "val": "C", "neighbors": [1]}],
                         "pointers": [["on_stack: D", 0], ["on_stack: A", 1], ["on_stack: B", 2], ["on_stack: C", 3]]}),
        ],
        common_mistakes_markdown=(
            "Using `nxt in visited` instead of `nxt in on_stack` for the back-edge check -- flags a false "
            "cycle on any acyclic graph where a node is simply reachable via two different paths (a diamond "
            "shape), since the second path finds the node already in `visited` even though it's long since "
            "off the current stack. Forgetting `on_stack.discard(node)` when backtracking -- without it, "
            "EVERY previously-explored node still looks like it's on the current path, and the check quietly "
            "degrades into the same visited-only bug. And only starting DFS from ONE node -- a cycle in a "
            "disconnected part of the graph that start never reaches is missed entirely, unless every "
            "unvisited node is also tried as its own starting point."
        ),
        complexity_markdown=(
            "`O(V + E)` -- same as any DFS traversal: every node is visited once and every edge examined "
            "once (to check whether it points to something in `on_stack`), whether or not a cycle is "
            "ultimately found."
        ),
    ),
    dict(
        slug="graph-shortest-paths",
        kind="pattern",
        topic="graphs",
        pattern_family="Graph shortest paths",
        title="Dijkstra's algorithm: shortest paths with weighted edges",
        display_order=4,
        estimated_minutes=18,
        summary="When edges have different costs, BFS's 'first reached = shortest' guarantee breaks -- "
                "Dijkstra fixes it by always finalizing the CHEAPEST unfinalized node next, using a min-heap "
                "exactly like this batch's heaps lesson.",
        prerequisite_slugs="graph-bfs,heaps",
        what_markdown=(
            "Dijkstra keeps a `dist` dict (the best known distance to each node so far) and a min-heap of "
            "`(distance, node)` candidates. Repeatedly pop the cheapest candidate: if that node is already "
            "finalized, it's a stale leftover entry -- skip it. Otherwise, finalize it (the popped distance "
            "IS its true shortest distance now) and RELAX its neighbors -- for each one, if reaching it "
            "through this node is cheaper than its previously known distance, update `dist` and push the "
            "better candidate."
        ),
        why_markdown=(
            "This combines Day 36's BFS with the heaps lessons: BFS explores in \"ring\" order because every "
            "edge secretly costs 1, so FIFO order and distance order happen to be identical. Dijkstra "
            "generalizes that same guarantee to ANY nonnegative edge weights by swapping the FIFO queue for "
            "a min-heap ordered by actual accumulated distance, so the next node popped is always genuinely "
            "the cheapest reachable one, not just the next one that happened to be enqueued."
        ),
        recognize_markdown=(
            "\"shortest/cheapest path\" with weighted edges (costs, times, distances that DIFFER between "
            "edges), \"minimum cost to reach every node from a source\", \"network delay time\". If every "
            "edge costs the same, plain BFS is simpler and just as correct -- Dijkstra's extra dist-dict-plus-"
            "heap bookkeeping earns its keep specifically when weights vary."
        ),
        intuition_markdown=(
            "The popped distance is trustworthy the MOMENT it's popped: a min-heap always returns the "
            "smallest remaining candidate, and since every edge weight is nonnegative, every OTHER path to "
            "that node -- whether still sitting in the heap or not yet discovered -- can only be equal or "
            "LARGER. Nothing still unexplored can ever beat it. That's exactly why Dijkstra requires "
            "nonnegative weights: a negative edge could let a longer-looking path secretly end up cheaper "
            "later, breaking this guarantee (Bellman-Ford handles that case instead)."
        ),
        walkthrough_intro_markdown=(
            "Trace Dijkstra from S over a small weighted graph. Watch node A get relaxed TWICE -- once "
            "directly from S (distance 4), then again via B with a cheaper total (distance 3) -- before it's "
            "ever finalized."
        ),
        walkthrough_code=(
            "import heapq\n\n"
            "def dijkstra(graph, start):\n"
            "    dist = {start: 0}\n"
            "    heap = [(0, start)]\n"
            "    finalized = set()\n"
            "    while heap:\n"
            "        d, node = heapq.heappop(heap)\n"
            "        if node in finalized:\n"
            "            continue\n"
            "        finalized.add(node)\n"
            "        for nxt, w in graph[node]:\n"
            "            nd = d + w\n"
            "            if nxt not in dist or nd < dist[nxt]:\n"
            "                dist[nxt] = nd\n"
            "                heapq.heappush(heap, (nd, nxt))\n"
            "    return dist"
        ),
        walkthrough_frames=[
            dict(caption="graph: S->A(4), S->B(1), B->A(2), B->C(5), A->C(1). Pop (0,S) -- heap's smallest, "
                          "so S's distance (0) is now FINAL. Relax both neighbors: A candidate = 0+4=4 (new) "
                          "-- push (4,A). B candidate = 0+1=1 (new) -- push (1,B). heap=[(1,B),(4,A)].",
                 locals={"nodes": [{"id": 0, "val": "S d=0*", "neighbors": [1, 2]},
                                    {"id": 1, "val": "A d=4", "neighbors": [3]},
                                    {"id": 2, "val": "B d=1", "neighbors": [1, 3]},
                                    {"id": 3, "val": "C d=?", "neighbors": []}],
                         "pointers": [["popped (0)", 0]]}),
            dict(caption="Pop (1,B) -- next smallest. B's distance (1) is now final. Relax A: 1+2=3, cheaper "
                          "than A's current 4 -- UPDATE dist[A]=3, push (3,A) (the stale (4,A) entry stays in "
                          "the heap, ignored later). Relax C: 1+5=6 (new) -- push (6,C). "
                          "heap=[(3,A),(4,A) stale,(6,C)].",
                 locals={"nodes": [{"id": 0, "val": "S d=0*", "neighbors": [1, 2]},
                                    {"id": 1, "val": "A d=3", "neighbors": [3]},
                                    {"id": 2, "val": "B d=1*", "neighbors": [1, 3]},
                                    {"id": 3, "val": "C d=6", "neighbors": []}],
                         "pointers": [["popped (1)", 2]]}),
            dict(caption="Pop (3,A) -- the UPDATED, cheaper entry (not the stale 4). A's true shortest "
                          "distance is 3, confirmed now that it's the smallest remaining candidate. Relax C: "
                          "3+1=4, cheaper than C's current 6 -- update dist[C]=4, push (4,C). "
                          "heap=[(4,A) stale,(4,C),(6,C) stale].",
                 locals={"nodes": [{"id": 0, "val": "S d=0*", "neighbors": [1, 2]},
                                    {"id": 1, "val": "A d=3*", "neighbors": [3]},
                                    {"id": 2, "val": "B d=1*", "neighbors": [1, 3]},
                                    {"id": 3, "val": "C d=4", "neighbors": []}],
                         "pointers": [["popped (3)", 1]]}),
            dict(caption="Pop (4,A) -- but A is ALREADY in finalized. This is the earlier, worse candidate "
                          "left over from before A got its better distance -- skip it without doing any "
                          "work. This is exactly why finalized is checked on POP, not on push.",
                 locals={"nodes": [{"id": 0, "val": "S d=0*", "neighbors": [1, 2]},
                                    {"id": 1, "val": "A d=3*", "neighbors": [3]},
                                    {"id": 2, "val": "B d=1*", "neighbors": [1, 3]},
                                    {"id": 3, "val": "C d=4", "neighbors": []}],
                         "pointers": [["popped (4) STALE", 1]]}),
            dict(caption="Pop (4,C) -- C's true shortest distance is 4, confirmed. C has no outgoing edges, "
                          "so nothing to relax. heap=[(6,C) stale] remains but every node is now finalized.",
                 locals={"nodes": [{"id": 0, "val": "S d=0*", "neighbors": [1, 2]},
                                    {"id": 1, "val": "A d=3*", "neighbors": [3]},
                                    {"id": 2, "val": "B d=1*", "neighbors": [1, 3]},
                                    {"id": 3, "val": "C d=4*", "neighbors": []}],
                         "pointers": [["popped (4)", 3]]}),
            dict(caption="Final shortest distances from S: S=0, B=1, A=3, C=4. Notice A was relaxed TWICE "
                          "(4, then 3) before it was ever finalized -- flexibility BFS's plain FIFO queue "
                          "doesn't have, since BFS never revisits a distance once assigned. Dijkstra can, as "
                          "long as it always finalizes via the CHEAPEST remaining candidate.",
                 locals={"nodes": [{"id": 0, "val": "S d=0*", "neighbors": [1, 2]},
                                    {"id": 1, "val": "A d=3*", "neighbors": [3]},
                                    {"id": 2, "val": "B d=1*", "neighbors": [1, 3]},
                                    {"id": 3, "val": "C d=4*", "neighbors": []}],
                         "pointers": []}),
        ],
        common_mistakes_markdown=(
            "Only relaxing a neighbor the FIRST time it's seen (`if nxt not in dist`) instead of allowing a "
            "cheaper update later (`if nxt not in dist or nd < dist[nxt]`) -- silently locks in a worse "
            "distance forever the moment a node is first reached, even when a genuinely cheaper path through "
            "a later-popped node exists. This is the single most common real Dijkstra bug. Running Dijkstra "
            "with a NEGATIVE edge weight -- breaks the whole \"popped distance is final\" guarantee, since a "
            "longer-looking path could still end up cheaper (needs Bellman-Ford instead). And skipping the "
            "`if node in finalized: continue` stale-entry check -- not incorrect by itself (relaxing an "
            "already-final node just does no updates), but wastes redundant work reprocessing leftover "
            "entries."
        ),
        complexity_markdown=(
            "`O((V + E) log V)` with a binary heap -- each of up to `E` relax operations can push onto the "
            "heap (`O(log V)` each, since the heap holds at most `O(E)` entries), and each of the `V` nodes "
            "is popped and finalized exactly once."
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
    "stacks": [
        dict(kind="choose_pattern",
             prompt_markdown="For each element in an array, you need to find the nearest element to its right "
                              "that's strictly greater. What's the best approach?",
             code=None,
             choices_json=[
                 "Monotonic stack, O(n) total",
                 "Nested loop checking every pair to the right, O(n^2)",
                 "Sort the array first",
                 "Two pointers from opposite ends",
             ],
             correct_answer="Monotonic stack, O(n) total",
             explanation_markdown="'Nearest bigger/smaller element to the right' is the monotonic-stack tell. "
                                   "Keep a stack of values still waiting to be resolved; each new value pops "
                                   "and resolves everything smaller than it before being pushed itself -- one "
                                   "pass, O(n) total work."),
        dict(kind="spot_bug",
             prompt_markdown="This is meant to find each value's next-greater element, but it sometimes "
                              "leaves a value unresolved when it should have found one. What's the bug?",
             code="def next_greater(nums):\n"
                  "    stack = []\n"
                  "    result = {}\n"
                  "    for n in nums:\n"
                  "        if stack and stack[-1] < n:\n"
                  "            result[stack.pop()] = n\n"
                  "        stack.append(n)\n"
                  "    for n in stack:\n"
                  "        result[n] = -1\n"
                  "    return [result[n] for n in nums]",
             choices_json=None,
             correct_answer="It uses if instead of while, so it only pops ONE element even when several "
                             "stacked values are all smaller than the new value and should all be resolved "
                             "by it at once.",
             explanation_markdown="Trace nums=[3, 1, 4, 2]: at n=4, both 1 and 3 are smaller and should both "
                                   "resolve to 4. `if` pops only 1 and stops -- 3 never gets popped here, so "
                                   "it incorrectly waits for a LATER value instead of being resolved by 4. "
                                   "`while` keeps popping until the top is no longer smaller -- exactly the "
                                   "double-pop shown in this lesson's own walkthrough."),
        dict(kind="complexity",
             prompt_markdown="A monotonic stack walk has a while loop nested inside a for loop. What's the "
                              "overall time complexity for n elements, and why isn't it O(n^2)?",
             code=None,
             choices_json=None,
             correct_answer="O(n)",
             explanation_markdown="Each element is pushed exactly once and popped at most once across the "
                                   "ENTIRE scan -- at most 2n operations total, not n operations each nested "
                                   "inside another n. The same amortized argument as sliding windows and "
                                   "monotonic deques."),
    ],
    "queues": [
        dict(kind="choose_pattern",
             prompt_markdown="You need the maximum value in every sliding window of size k as it moves across "
                              "an array, computed in one pass. What's the right approach?",
             code=None,
             choices_json=[
                 "Monotonic deque, O(n) total",
                 "Recompute the max of each window directly, O(n*k)",
                 "A hash map of value counts",
                 "Sort each window before reading its max",
             ],
             correct_answer="Monotonic deque, O(n) total",
             explanation_markdown="A monotonic deque's front always holds the current window's max candidate "
                                   "-- no rescanning needed. Recomputing each window's max directly is O(n*k); "
                                   "a heap works but costs O(n log n) and can't cleanly evict expired entries."),
        dict(kind="spot_bug",
             prompt_markdown="This sliding-window-maximum can never correctly evict values that have aged out "
                              "of the window. What's the bug?",
             code="def max_sliding_window(nums, k):\n"
                  "    dq = deque()\n"
                  "    result = []\n"
                  "    for i, n in enumerate(nums):\n"
                  "        while dq and dq[-1] < n:\n"
                  "            dq.pop()\n"
                  "        dq.append(n)\n"
                  "        if i >= k - 1:\n"
                  "            result.append(dq[0])\n"
                  "    return result",
             choices_json=None,
             correct_answer="The deque stores raw VALUES (dq.append(n)) instead of indices, so there's no way "
                             "to tell whether the value at the front is still inside the current window or "
                             "fell out of it several steps ago -- a value alone carries no position "
                             "information.",
             explanation_markdown="Store indices instead (dq.append(i)), look up nums[dq[0]] for the value "
                                   "when needed, and compare dq[0] against i - k to know when the front has "
                                   "aged out and needs to be evicted -- exactly what this lesson's own "
                                   "walkthrough code does."),
        dict(kind="complexity",
             prompt_markdown="A monotonic deque used for sliding-window-maximum has a while loop nested "
                              "inside a for loop, just like a monotonic stack. What's the overall time "
                              "complexity for n elements?",
             code=None,
             choices_json=None,
             correct_answer="O(n)",
             explanation_markdown="Each index is pushed once and popped (from either end) at most once "
                                   "across the entire scan -- at most a constant multiple of n operations "
                                   "total, not n operations nested inside another n."),
    ],
    "recursion": [
        dict(kind="predict_output",
             prompt_markdown="What does this print?",
             code="def count_down(n):\n"
                  "    if n == 0:\n"
                  "        return\n"
                  "    print(n)\n"
                  "    count_down(n - 1)\n"
                  "    print('done', n)\n\n"
                  "count_down(3)",
             choices_json=None,
             correct_answer="3, 2, 1, done 1, done 2, done 3 (each on its own line)",
             explanation_markdown="The first print (n) happens BEFORE the recursive call, so 3, 2, 1 print "
                                   "on the way down. The second print ('done', n) happens AFTER the recursive "
                                   "call, so it only runs once that call has fully returned -- which happens "
                                   "in reverse order as the stack unwinds: done 1, then done 2, then done 3."),
        dict(kind="spot_bug",
             prompt_markdown="This is meant to count down from n to 0, but it never finishes. What's the bug?",
             code="def countdown(n):\n"
                  "    if n == 0:\n"
                  "        return\n"
                  "    print(n)\n"
                  "    countdown(n)",
             choices_json=None,
             correct_answer="The recursive call is countdown(n) -- it passes n unchanged instead of n - 1. "
                             "n never gets closer to the base case (n == 0), so the recursion never "
                             "terminates.",
             explanation_markdown="A base case alone isn't enough -- the recursive case also has to make "
                                   "GENUINE progress toward it every call. Since n is the same every time, "
                                   "the base case (n == 0) is never reached, and Python eventually raises "
                                   "RecursionError once the call stack hits its depth limit."),
        dict(kind="complexity",
             prompt_markdown="A recursive function where each call makes exactly one further recursive call "
                              "(like factorial) processes n total calls before the first one returns. What's "
                              "the SPACE complexity, and why isn't it O(1) like an equivalent loop?",
             code=None,
             choices_json=None,
             correct_answer="O(n)",
             explanation_markdown="Each active call keeps its own stack frame alive until it returns -- n "
                                   "nested calls means n frames alive at once, at the deepest point, versus a "
                                   "loop's single set of variables reused every iteration."),
    ],
    "backtracking": [
        dict(kind="choose_pattern",
             prompt_markdown="You need to list every possible subset of a list of n items (2^n total "
                              "subsets). What's the right approach?",
             code=None,
             choices_json=[
                 "Backtracking -- choose/recurse/un-choose each item",
                 "A single loop with a running count",
                 "Binary search",
                 "Sort the items first",
             ],
             correct_answer="Backtracking -- choose/recurse/un-choose each item",
             explanation_markdown="'Every possible X' with no shortcut around exploring the whole space is "
                                   "the backtracking tell. Build one shared partial solution, extend it, "
                                   "recurse, then un-extend it to try the next option -- instead of building "
                                   "each subset from scratch."),
        dict(kind="spot_bug",
             prompt_markdown="This subsets() sometimes returns a list of what LOOKS like the right subsets, "
                              "but every entry ends up identical (usually all empty). What's the bug?",
             code="def subsets(nums):\n"
                  "    result = []\n"
                  "    path = []\n"
                  "    def backtrack(i):\n"
                  "        if i == len(nums):\n"
                  "            result.append(path)\n"
                  "            return\n"
                  "        path.append(nums[i])\n"
                  "        backtrack(i + 1)\n"
                  "        path.pop()\n"
                  "        backtrack(i + 1)\n"
                  "    backtrack(0)\n"
                  "    return result",
             choices_json=None,
             correct_answer="result.append(path) appends the SAME mutable list object every time, not a "
                             "copy. path is reused and mutated throughout the entire search, so every entry "
                             "in result ends up pointing at that one object -- by the end, they all reflect "
                             "path's FINAL state, not what it looked like when each was recorded.",
             explanation_markdown="Fix: result.append(path[:]) (or list(path)) -- a real copy, frozen at "
                                   "that exact moment, unaffected by whatever path does afterward."),
        dict(kind="complexity",
             prompt_markdown="Enumerating every subset of an n-element list takes how much time, and why "
                              "can't it be faster?",
             code=None,
             choices_json=None,
             correct_answer="O(2^n)",
             explanation_markdown="There are exactly 2^n subsets of an n-element set, so any algorithm that "
                                   "actually LISTS all of them must take at least that long -- the answer "
                                   "itself is that size, regardless of how the search is implemented."),
    ],
    "binary-search": [
        dict(kind="choose_pattern",
             prompt_markdown="Binary search needs the data (or the answer space) to have which property "
                              "before you can use it?",
             code=None,
             choices_json=[
                 "Sorted, or otherwise monotonic, order",
                 "All unique values",
                 "A power-of-two length",
                 "Already stored as a linked list",
             ],
             correct_answer="Sorted, or otherwise monotonic, order",
             explanation_markdown="Each step eliminates half the remaining space based on ONE comparison at "
                                   "mid. That's only valid if you can be sure the discarded half genuinely "
                                   "can't contain the answer -- which requires sorted (or monotonic) order."),
        dict(kind="spot_bug",
             prompt_markdown="This binary search on [1, 2] for target=2 never terminates. What's the bug?",
             code="def binary_search(arr, target):\n"
                  "    lo, hi = 0, len(arr) - 1\n"
                  "    while lo <= hi:\n"
                  "        mid = (lo + hi) // 2\n"
                  "        if arr[mid] < target:\n"
                  "            lo = mid\n"
                  "        elif arr[mid] > target:\n"
                  "            hi = mid - 1\n"
                  "        else:\n"
                  "            return mid\n"
                  "    return -1",
             choices_json=None,
             correct_answer="lo = mid should be lo = mid + 1. When hi == lo + 1, integer division rounds mid "
                             "down to lo -- so lo = mid leaves lo completely unchanged, and the loop never "
                             "makes progress.",
             explanation_markdown="Moving a boundary TO mid (instead of past it) is the classic way to write "
                                   "an infinite loop rather than a wrong answer -- often more confusing to "
                                   "debug, since nothing crashes."),
        dict(kind="complexity",
             prompt_markdown="Binary searching a sorted array of n elements takes how much time?",
             code=None,
             choices_json=None,
             correct_answer="O(log n)",
             explanation_markdown="The remaining search range is cut in half every step, so it takes about "
                                   "log2(n) steps to shrink from n elements down to one."),
    ],
    "binary-search-variants": [
        dict(kind="choose_pattern",
             prompt_markdown="You need the minimum integer speed k such that Koko can eat all the piles "
                              "within h hours -- eating faster always finishes in the same or fewer hours, "
                              "never more. What's the right approach?",
             code=None,
             choices_json=[
                 "Binary search over candidate speeds k, using a hours-needed(k) check as the monotonic "
                 "predicate",
                 "Try every possible k starting from 1 upward",
                 "Sort the piles and take the median pile size",
                 "Two pointers over the pile sizes",
             ],
             correct_answer="Binary search over candidate speeds k, using a hours-needed(k) check as the "
                             "monotonic predicate",
             explanation_markdown="k is never an array index -- it's a candidate VALUE. \"Can Koko finish "
                                   "within h hours at speed k\" is a monotonic yes/no condition over k (true "
                                   "for every k above some threshold, false below), which is exactly what "
                                   "binary search needs -- no array required, just a monotonic predicate."),
        dict(kind="spot_bug",
             prompt_markdown="This rotated-array search sometimes fails to find a target that equals "
                              "arr[lo] itself, even though it's clearly in the array. What's the bug?",
             code="def search_rotated(arr, target):\n"
                  "    lo, hi = 0, len(arr) - 1\n"
                  "    while lo <= hi:\n"
                  "        mid = (lo + hi) // 2\n"
                  "        if arr[mid] == target:\n"
                  "            return mid\n"
                  "        if arr[lo] <= arr[mid]:\n"
                  "            if arr[lo] < target < arr[mid]:\n"
                  "                hi = mid - 1\n"
                  "            else:\n"
                  "                lo = mid + 1\n"
                  "        else:\n"
                  "            if arr[mid] < target <= arr[hi]:\n"
                  "                lo = mid + 1\n"
                  "            else:\n"
                  "                hi = mid - 1\n"
                  "    return -1",
             choices_json=None,
             correct_answer="arr[lo] < target < arr[mid] should be arr[lo] <= target < arr[mid]. With strict "
                             "<, a target equal to arr[lo] itself gets routed to the wrong half (lo = mid + "
                             "1), permanently discarding the very index where it lives, since arr[mid] was "
                             "already checked and ruled out.",
             explanation_markdown="Boundary inclusivity matters here exactly like the classic version's "
                                   "lo/hi updates -- the sorted-half range check has to include the endpoint "
                                   "you're actually standing on."),
        dict(kind="complexity",
             prompt_markdown="Binary searching over a numeric answer space of size R, where checking one "
                              "candidate costs O(n), takes how much total time?",
             code=None,
             choices_json=None,
             correct_answer="O(n log R)",
             explanation_markdown="Each of the O(log R) binary-search steps over the candidate range calls "
                                   "the O(n) predicate check once -- the two costs multiply, not add."),
    ],
    "sorting": [
        dict(kind="choose_pattern",
             prompt_markdown="Which of these sorts does much less work when the input is ALREADY nearly "
                              "sorted, compared to a random input of the same size?",
             code=None,
             choices_json=[
                 "Insertion sort",
                 "Selection sort",
                 "Any comparison sort -- they all do the same amount of work regardless of input order",
                 "None -- sorting algorithms ignore existing order",
             ],
             correct_answer="Insertion sort",
             explanation_markdown="Insertion sort's inner while loop only shifts as far as needed to find "
                                   "each element's correct spot -- on a nearly-sorted array most elements "
                                   "need zero or one shift, so it runs close to O(n) instead of O(n^2). "
                                   "Selection sort's inner scan for the next minimum is always the full "
                                   "remaining length regardless of how sorted the input already is -- it "
                                   "can't finish early."),
        dict(kind="spot_bug",
             prompt_markdown="This insertion sort usually works, but sometimes silently produces a wrong "
                              "result instead of an error, or occasionally crashes outright. What's the bug?",
             code="def insertion_sort(arr):\n"
                  "    for i in range(1, len(arr)):\n"
                  "        key = arr[i]\n"
                  "        j = i - 1\n"
                  "        while arr[j] > key:\n"
                  "            arr[j + 1] = arr[j]\n"
                  "            j -= 1\n"
                  "        arr[j + 1] = key\n"
                  "    return arr",
             choices_json=None,
             correct_answer="The while condition is missing j >= 0 -- it should be "
                             "while j >= 0 and arr[j] > key. Once j goes negative, Python doesn't error "
                             "immediately: arr[j] silently wraps around and reads from the END of the list "
                             "(arr[-1], arr[-2], ...), corrupting the shift with unrelated elements for "
                             "several steps before eventually crashing once j passes -len(arr).",
             explanation_markdown="A missing bounds check on a negative index is one of the sneakiest bugs "
                                   "in Python specifically, since arr[-1] is always valid -- it never raises "
                                   "an error to point you at the mistake, it just silently reads the wrong "
                                   "element."),
        dict(kind="complexity",
             prompt_markdown="What's the worst-case time complexity of insertion sort (and bubble sort), and "
                              "which input triggers it?",
             code=None,
             choices_json=None,
             correct_answer="O(n^2), triggered by reverse-sorted input",
             explanation_markdown="Reverse-sorted input forces every new element to shift/compare against "
                                   "everything already placed -- roughly n comparisons for each of n "
                                   "elements, the worst case for both algorithms."),
    ],
    "divide-and-conquer-sorting": [
        dict(kind="choose_pattern",
             prompt_markdown="You need the kth smallest element in an unsorted array, without needing the "
                              "rest of the array fully sorted. What's the most efficient approach covered so "
                              "far?",
             code=None,
             choices_json=[
                 "Quickselect -- partition like quicksort, but only recurse into the one side that contains "
                 "index k",
                 "Fully sort the array, then index into position k",
                 "Binary search directly over the unsorted array",
                 "Insertion sort until the kth element is in its final place",
             ],
             correct_answer="Quickselect -- partition like quicksort, but only recurse into the one side "
                             "that contains index k",
             explanation_markdown="Partition already tells you exactly where the pivot landed (index i+1) "
                                   "relative to k -- if that's k, you're done; otherwise only ONE side can "
                                   "possibly contain index k, so quickselect never wastes time recursing into "
                                   "the side that doesn't matter, unlike a full sort."),
        dict(kind="spot_bug",
             prompt_markdown="This quicksort usually sorts correctly, but sometimes silently produces a "
                              "scrambled (not fully sorted) result. What's the bug?",
             code="def partition(arr, lo, hi):\n"
                  "    pivot = arr[hi]\n"
                  "    i = lo - 1\n"
                  "    for j in range(lo, hi):\n"
                  "        if arr[j] <= pivot:\n"
                  "            i += 1\n"
                  "            arr[i], arr[j] = arr[j], arr[i]\n"
                  "    return i + 1\n\n"
                  "def quicksort(arr, lo=0, hi=None):\n"
                  "    if hi is None:\n"
                  "        hi = len(arr) - 1\n"
                  "    if lo < hi:\n"
                  "        p = partition(arr, lo, hi)\n"
                  "        quicksort(arr, lo, p - 1)\n"
                  "        quicksort(arr, p + 1, hi)\n"
                  "    return arr",
             choices_json=None,
             correct_answer="partition() never actually moves the pivot into its final position -- the line "
                             "arr[i + 1], arr[hi] = arr[hi], arr[i + 1] is missing. It returns i + 1 claiming "
                             "that's where the pivot now sits, but the pivot is still at arr[hi]. The "
                             "recursive calls then split around the wrong index, silently scrambling the "
                             "result -- and it happens to work by luck on inputs where the pivot already "
                             "belonged at hi, which is what makes it easy to miss.",
             explanation_markdown="Compare against this lesson's own walkthrough_code: the final swap line is "
                                   "exactly what's missing here."),
        dict(kind="complexity",
             prompt_markdown="Merge sort and (average-case) quicksort both take O(n log n). Where does the "
                              "log n factor come from specifically?",
             code=None,
             choices_json=None,
             correct_answer="O(log n) levels of recursion (the input roughly halves each level), each level "
                             "doing O(n) total work across all its pieces combined",
             explanation_markdown="The recursion tree's depth is log n because the input size halves (or "
                                   "partitions roughly in half, on average) at every level; the work summed "
                                   "across every piece AT one level is still O(n) total, no matter how many "
                                   "pieces that level has been split into."),
    ],
    "trees": [
        dict(kind="choose_pattern",
             prompt_markdown="Which traversal order visits a node BEFORE recursing into either of its "
                              "children?",
             code=None,
             choices_json=["Preorder", "Inorder", "Postorder", "Level-order"],
             correct_answer="Preorder",
             explanation_markdown="Preorder is node, then left subtree, then right subtree -- the node's own "
                                   "value is recorded before either recursive call runs. Inorder is left, "
                                   "node, right; postorder is left, right, node; level-order isn't a DFS "
                                   "order at all (it's the next lesson's technique)."),
        dict(kind="spot_bug",
             prompt_markdown="This preorder traversal crashes with an AttributeError partway through, "
                              "instead of completing. What's the bug?",
             code="def preorder(node, result):\n"
                  "    if node is None:\n"
                  "        pass\n"
                  "    result.append(node.val)\n"
                  "    preorder(node.left, result)\n"
                  "    preorder(node.right, result)",
             choices_json=None,
             correct_answer="The base case body is `pass` instead of `return`. When node IS None, execution "
                             "falls straight through to `result.append(node.val)` anyway, and None has no "
                             ".val attribute -- crashing instead of stopping the recursion.",
             explanation_markdown="A base case has to actually STOP the function, not just be checked -- "
                                   "`if node is None: pass` checks the condition but does nothing about it, "
                                   "which is functionally the same as having no base case at all."),
        dict(kind="complexity",
             prompt_markdown="Visiting every node of an n-node tree via DFS takes how much time, and how "
                              "much space (worst case) for the recursion stack?",
             code=None,
             choices_json=None,
             correct_answer="O(n) time, O(n) worst-case space",
             explanation_markdown="Every node is visited exactly once regardless of traversal order -- O(n) "
                                   "time. The recursion stack's depth equals the tree's height, which is "
                                   "O(log n) for a balanced tree but O(n) worst case for a completely skewed "
                                   "one (effectively a linked list)."),
    ],
    "binary-search-trees": [
        dict(kind="choose_pattern",
             prompt_markdown="Which of these correctly validates whether a binary tree is a valid BST?",
             code=None,
             choices_json=[
                 "Track a (low, high) range for each node, narrowing it as you recurse into children",
                 "Just compare each node to its immediate parent",
                 "Sort all the values with an inorder traversal and check they're already sorted",
                 "Check that node.left.val < node.right.val at every node",
             ],
             correct_answer="Track a (low, high) range for each node, narrowing it as you recurse into "
                             "children",
             explanation_markdown="Comparing only to the immediate parent misses violations from an "
                                   "ancestor further up the tree -- exactly what this lesson's own "
                                   "walkthrough demonstrates at node 4. An inorder-then-check-sorted approach "
                                   "actually does work correctly, but it's a different, less direct "
                                   "technique than the range-tracking one this lesson teaches."),
        dict(kind="spot_bug",
             prompt_markdown="This validator returns True (valid) for a tree that should actually be "
                              "INVALID: 10 with left child 5 and right child 15, where 15 has a left child "
                              "6 (6 is less than the root 10, which should make the tree invalid). What's "
                              "the bug?",
             code="def is_valid_bst(node):\n"
                  "    if node is None:\n"
                  "        return True\n"
                  "    if node.left and node.left.val >= node.val:\n"
                  "        return False\n"
                  "    if node.right and node.right.val <= node.val:\n"
                  "        return False\n"
                  "    return is_valid_bst(node.left) and is_valid_bst(node.right)",
             choices_json=None,
             correct_answer="It only compares each node to its DIRECT children, never checking against "
                             "ancestors further up. 6 is checked only against its immediate parent 15 (6 < "
                             "15, passes), but 6 is in node 10's RIGHT subtree, so it also needs to be "
                             "greater than 10 -- a check this code never makes.",
             explanation_markdown="This is precisely the bug the (low, high) bounds technique fixes: passing "
                                   "down an inherited range means every node is checked against every "
                                   "relevant ancestor, not just its parent."),
        dict(kind="complexity",
             prompt_markdown="On a BALANCED binary search tree with n nodes, what's the time complexity of "
                              "searching for a value?",
             code=None,
             choices_json=None,
             correct_answer="O(log n)",
             explanation_markdown="Each comparison against the current node eliminates one entire subtree "
                                   "from consideration -- the same halving idea as binary search on a sorted "
                                   "array, giving O(log n) comparisons on a balanced tree (O(n) worst case if "
                                   "the tree has degenerated into a skewed, linked-list-like shape)."),
    ],
    "tree-bfs": [
        dict(kind="choose_pattern",
             prompt_markdown="Level-order traversal processes nodes in FIFO order using a queue -- what's the "
                              "key trick that lets you tell WHERE one level ends and the next begins, without "
                              "storing a depth field on each node?",
             code=None,
             choices_json=[
                 "Snapshot the queue's current length before the inner loop starts, and process exactly that "
                 "many nodes",
                 "Add a sentinel None value between levels",
                 "Track a running maximum depth as a separate variable",
                 "Compare each node's value to the previous node dequeued",
             ],
             correct_answer="Snapshot the queue's current length before the inner loop starts, and process "
                             "exactly that many nodes",
             explanation_markdown="Everything already in the queue at that snapshot moment IS the current "
                                   "level in full; anything enqueued during this pass belongs to the next "
                                   "level, since the snapshot count runs out before those new entries get "
                                   "processed."),
        dict(kind="spot_bug",
             prompt_markdown="This level-order traversal visits every node in the correct breadth-first "
                              "ORDER, but its result isn't grouped by level the way the problem asks for. "
                              "What's missing?",
             code="def level_order(root):\n"
                  "    if root is None:\n"
                  "        return []\n"
                  "    result = []\n"
                  "    q = deque([root])\n"
                  "    while q:\n"
                  "        node = q.popleft()\n"
                  "        result.append(node.val)\n"
                  "        if node.left:\n"
                  "            q.append(node.left)\n"
                  "        if node.right:\n"
                  "            q.append(node.right)\n"
                  "    return result",
             choices_json=None,
             correct_answer="There's no level-size snapshot at all -- every node's value gets appended "
                             "directly to one flat list, so the result is a single list of all values in "
                             "breadth-first order (e.g. [1, 2, 3, 4, 5]) instead of grouped per level (e.g. "
                             "[[1], [2, 3], [4, 5]]).",
             explanation_markdown="The traversal ORDER is actually correct here -- what's missing is "
                                   "wrapping an inner loop around exactly level_size dequeues per pass, which "
                                   "is what turns a flat scan into level-grouped output."),
        dict(kind="complexity",
             prompt_markdown="Level-order traversal of an n-node tree takes O(n) time. What's the worst-case "
                              "space for the queue, and what determines it?",
             code=None,
             choices_json=None,
             correct_answer="O(n), determined by the tree's WIDTH (not its height)",
             explanation_markdown="A complete binary tree's last level can hold roughly n/2 nodes, all in "
                                   "the queue at once at that level's peak -- so the queue's peak size scales "
                                   "with how WIDE the tree gets, unlike DFS's recursion stack, which scales "
                                   "with how tall/deep it is."),
    ],
    "heaps": [
        dict(kind="choose_pattern",
             prompt_markdown="Python's heapq only gives you a MIN-heap. What's the standard trick for using "
                              "it as a max-heap?",
             code=None,
             choices_json=[
                 "Negate every value on the way in (and negate again on the way out)",
                 "Sort the whole list every time you need the max",
                 "heapq doesn't support this -- you must write a custom class",
                 "Call heapq.heappush twice for each value",
             ],
             correct_answer="Negate every value on the way in (and negate again on the way out)",
             explanation_markdown="Negating flips the ordering: the SMALLEST negated value corresponds to "
                                   "the LARGEST original value, so heapq's min-heap behavior gives you "
                                   "max-heap behavior for free, no extra code needed beyond negating on push "
                                   "and pop."),
        dict(kind="spot_bug",
             prompt_markdown="This code builds what looks like a heap, but heapq.heappop() on it returns the "
                              "wrong \"minimum\". What's the bug?",
             code="def build_heap_wrong(values):\n"
                  "    heap = []\n"
                  "    for v in values:\n"
                  "        heap.append(v)\n"
                  "    return heap\n\n"
                  "heap = build_heap_wrong([5, 3, 8, 1])\n"
                  "heapq.heappop(heap)  # returns 5, not 1",
             choices_json=None,
             correct_answer="heap.append(v) just adds values in input order -- it never establishes the "
                             "heap invariant. heapq.heappop() assumes the list it's given is ALREADY a valid "
                             "heap; it only fixes up the structure around the root it removes, not the whole "
                             "list, so popping an unheapified list returns whatever happens to be at index 0, "
                             "not the true minimum.",
             explanation_markdown="Fix: use heapq.heappush(heap, v) for each value (maintains the invariant "
                                   "incrementally), or build the plain list first and call "
                                   "heapq.heapify(heap) once afterward -- O(n), cheaper than n individual "
                                   "pushes."),
        dict(kind="complexity",
             prompt_markdown="Repeatedly extracting the min from a collection of n elements total, one "
                              "heappush/heappop at a time, costs how much total time?",
             code=None,
             choices_json=None,
             correct_answer="O(n log n)",
             explanation_markdown="Each push/pop is O(log n) (bounded by the tree's height), and there are n "
                                   "of them -- O(n log n) total, versus O(n^2) from repeatedly scanning "
                                   "linearly for the min."),
    ],
    "top-k-heap": [
        dict(kind="choose_pattern",
             prompt_markdown="You need the 5 largest numbers from a stream of a million values, without "
                              "storing all million. What's the efficient approach?",
             code=None,
             choices_json=[
                 "A MIN-heap bounded to size 5 -- push each value, evict the minimum whenever size exceeds 5",
                 "A MAX-heap containing all million values",
                 "Sort the entire stream, then take the last 5",
                 "Track only the single largest value seen so far",
             ],
             correct_answer="A MIN-heap bounded to size 5 -- push each value, evict the minimum whenever "
                             "size exceeds 5",
             explanation_markdown="Bounding the heap to size 5 keeps every push/pop at O(log 5) instead of "
                                   "O(log n), and the heap never needs to hold more than 5 elements at a "
                                   "time -- the min-heap's root is exactly the one value worth cheap access "
                                   "to, since it's the first to get evicted."),
        dict(kind="spot_bug",
             prompt_markdown="This is meant to return the 3 largest values from nums, but it silently "
                              "returns ALL of them instead. What's missing?",
             code="def top_k_largest(nums, k):\n"
                  "    heap = []\n"
                  "    for n in nums:\n"
                  "        heapq.heappush(heap, n)\n"
                  "    return heap",
             choices_json=None,
             correct_answer="The eviction check is missing entirely -- there's no `if len(heap) > k: "
                             "heapq.heappop(heap)` after each push, so the heap just keeps growing to hold "
                             "every element that was ever pushed, silently returning the whole input instead "
                             "of only the top k.",
             explanation_markdown="Without bounding the heap's size, this technique degrades back into a "
                                   "full heap-sort -- the entire point of the bounded-heap pattern is "
                                   "discarding candidates that can no longer possibly be in the top k."),
        dict(kind="complexity",
             prompt_markdown="Finding the k largest of n values with a bounded min-heap takes how much time "
                              "and space?",
             code=None,
             choices_json=None,
             correct_answer="O(n log k) time, O(k) space",
             explanation_markdown="Each of the n pushes (and the pops that follow when the heap overflows) "
                                   "costs O(log k), since the heap is never allowed to hold more than k + 1 "
                                   "elements -- and its size never exceeds k regardless of how large n is."),
    ],
    "graphs": [
        dict(kind="choose_pattern",
             prompt_markdown="Representing a large, sparse graph (few edges relative to the number of "
                              "possible node pairs) -- e.g. a road network with a few thousand cities, each "
                              "connected to only a handful of neighbors. Which representation uses less "
                              "memory?",
             code=None,
             choices_json=[
                 "Adjacency list",
                 "Adjacency matrix",
                 "They always use the same amount of memory",
                 "Neither -- you'd need a spanning tree",
             ],
             correct_answer="Adjacency list",
             explanation_markdown="An adjacency list only stores edges that actually exist -- O(V+E) total. "
                                   "An adjacency matrix allocates a full V x V grid regardless of how sparse "
                                   "the graph is -- O(V^2), wasteful when E is much smaller than V^2."),
        dict(kind="spot_bug",
             prompt_markdown="This is meant to build an undirected graph, but looking up a node's neighbors "
                              "after building it gives the wrong answer. What's the bug?",
             code="def build_graph(edges):\n"
                  "    graph = {}\n"
                  "    for a, b in edges:\n"
                  "        graph.setdefault(a, []).append(b)\n"
                  "    return graph\n\n"
                  "graph = build_graph([('A', 'B')])\n"
                  "graph.get('B')  # returns None, not ['A']",
             choices_json=None,
             correct_answer="Only graph[a].append(b) runs -- the reverse graph[b].append(a) is missing. For "
                             "an UNDIRECTED edge, both directions need to be recorded; as written this "
                             "silently builds a DIRECTED graph (A -> B only), so looking up B's neighbors "
                             "misses A entirely.",
             explanation_markdown="Fix: add graph.setdefault(b, []).append(a) right alongside the first "
                                   "line, exactly like the lesson's own build_graph. This is easy to miss "
                                   "because the code still runs without error -- it just silently produces "
                                   "the wrong graph shape."),
        dict(kind="complexity",
             prompt_markdown="Building an adjacency list from an edge list with V nodes and E edges takes "
                              "how much time and space?",
             code=None,
             choices_json=None,
             correct_answer="O(V + E)",
             explanation_markdown="Every edge is processed once (O(E) total appends), and every node gets "
                                   "at least an empty list entry (O(V)) -- both time and memory scale with "
                                   "V+E, not V^2 the way a matrix would."),
    ],
    "graph-bfs": [
        dict(kind="choose_pattern",
             prompt_markdown="You need the minimum number of moves from a start cell to a target cell in a "
                              "grid, where every move costs the same. BFS or DFS?",
             code=None,
             choices_json=["BFS", "DFS", "Either works identically", "Neither -- you need Dijkstra"],
             correct_answer="BFS",
             explanation_markdown="BFS dequeues nodes in nondecreasing distance from the source, so the "
                                   "FIRST time it reaches the target is guaranteed to be via the shortest "
                                   "path. DFS reaches every node too, but with no such guarantee -- it can "
                                   "stumble onto a long path before a short one."),
        dict(kind="spot_bug",
             prompt_markdown="This BFS still returns the correct final count, but does noticeably more work "
                              "than necessary. What's the inefficiency?",
             code="def bfs_count_wasteful(grid, sr, sc):\n"
                  "    rows, cols = len(grid), len(grid[0])\n"
                  "    visited = set()\n"
                  "    queue = deque([(sr, sc)])\n"
                  "    count = 0\n"
                  "    while queue:\n"
                  "        r, c = queue.popleft()\n"
                  "        if (r, c) in visited:\n"
                  "            continue\n"
                  "        visited.add((r, c))\n"
                  "        count += 1\n"
                  "        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n"
                  "            nr, nc = r + dr, c + dc\n"
                  "            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:\n"
                  "                queue.append((nr, nc))",
             choices_json=None,
             correct_answer="visited.add((r, c)) only happens when a cell is POPPED, not when it's "
                             "enqueued -- so the same cell can be pushed onto the queue multiple times (once "
                             "from each unvisited neighbor that reaches it) before it's ever processed once. "
                             "The `if (r,c) in visited: continue` guard keeps the final count correct, but "
                             "the queue does far more work than necessary.",
             explanation_markdown="Fix: mark a cell visited the moment you enqueue it (right before "
                                   "queue.append(...)), not when you dequeue it -- guarantees each cell is "
                                   "only ever added to the queue once, matching the lesson's own "
                                   "bfs_count_island."),
        dict(kind="complexity",
             prompt_markdown="BFS over a grid with R rows and C columns visits at most how many cells, and "
                              "what's the total time?",
             code=None,
             choices_json=None,
             correct_answer="O(R*C) cells, O(R*C) time",
             explanation_markdown="Every cell is enqueued (and dequeued) at most once, and checking a "
                                   "cell's 4 neighbors is O(1) work -- so total time is proportional to the "
                                   "number of cells, R*C."),
    ],
    "graph-dfs": [
        dict(kind="choose_pattern",
             prompt_markdown="Detecting whether a directed graph has a cycle needs a set of nodes CURRENTLY "
                              "on the DFS path, separate from the set of ALL nodes ever visited. What's this "
                              "extra set usually called?",
             code=None,
             choices_json=["on_stack (or \"in progress\")", "visited", "frontier", "queue"],
             correct_answer="on_stack (or \"in progress\")",
             explanation_markdown="'visited' alone only tells you a node has been fully explored at some "
                                   "point -- it can't distinguish a harmless shared descendant (reached via "
                                   "two different paths) from a real back edge to an ancestor on the CURRENT "
                                   "path. on_stack tracks exactly the second thing."),
        dict(kind="spot_bug",
             prompt_markdown="This is meant to detect a cycle, but it reports True on the graph "
                              "D->A, D->B, A->C, B->C -- which has NO cycle (C just has two ancestors). "
                              "What's the bug?",
             code="def has_cycle_wrong(graph, node, visited, path):\n"
                  "    visited.add(node)\n"
                  "    path.append(node)\n"
                  "    for nxt in graph[node]:\n"
                  "        if nxt in visited:\n"
                  "            return True\n"
                  "        if has_cycle_wrong(graph, nxt, visited, path):\n"
                  "            return True\n"
                  "    path.pop()\n"
                  "    return False",
             choices_json=None,
             correct_answer="The back-edge check is `if nxt in visited: return True` -- checking whether a "
                             "neighbor has EVER been visited, not whether it's on the CURRENT path "
                             "(on_stack). On the acyclic diamond D->A->C, D->B->C, C gets visited once via "
                             "A, then DFS backtracks to D and explores B -> C again; C is already in "
                             "visited (from the first path), so this wrongly reports a cycle that doesn't "
                             "exist.",
             explanation_markdown="Fix: track a separate on_stack set, added when entering a node and "
                                   "removed (discard) when backtracking out of it, and check `nxt in "
                                   "on_stack` instead of `nxt in visited` -- exactly this lesson's "
                                   "has_cycle."),
        dict(kind="complexity",
             prompt_markdown="DFS cycle detection over a directed graph with V nodes and E edges costs how "
                              "much time?",
             code=None,
             choices_json=None,
             correct_answer="O(V + E)",
             explanation_markdown="Same as any DFS traversal -- every node is visited once and every edge "
                                   "examined once (to check whether it points to something in on_stack), "
                                   "regardless of whether a cycle is ultimately found."),
    ],
    "graph-shortest-paths": [
        dict(kind="choose_pattern",
             prompt_markdown="All edges in your graph cost exactly 1. Do you need Dijkstra, or is something "
                              "simpler correct?",
             code=None,
             choices_json=[
                 "Plain BFS is enough and simpler",
                 "Dijkstra is required even here",
                 "Neither works -- you'd need Bellman-Ford",
                 "You need DFS instead",
             ],
             correct_answer="Plain BFS is enough and simpler",
             explanation_markdown="When every edge costs the same, FIFO order and distance order are "
                                   "identical -- Dijkstra's extra dist dict and heap earn their keep "
                                   "specifically when weights DIFFER. With uniform weights, plain BFS gives "
                                   "the same correct shortest distances with less bookkeeping."),
        dict(kind="spot_bug",
             prompt_markdown="This Dijkstra returns {'S':0,'A':4,'B':1,'C':6} on graph S->A(4), S->B(1), "
                              "B->A(2), B->C(5), A->C(1) -- but the correct answer is "
                              "{'S':0,'A':3,'B':1,'C':4}. What's the bug?",
             code="def dijkstra_wrong(graph, start):\n"
                  "    dist = {start: 0}\n"
                  "    heap = [(0, start)]\n"
                  "    while heap:\n"
                  "        d, node = heapq.heappop(heap)\n"
                  "        for nxt, w in graph.get(node, []):\n"
                  "            if nxt not in dist:\n"
                  "                dist[nxt] = d + w\n"
                  "                heapq.heappush(heap, (d + w, nxt))\n"
                  "    return dist",
             choices_json=None,
             correct_answer="The relax check is `if nxt not in dist`, which only ever sets a neighbor's "
                             "distance the FIRST time it's reached -- it never updates dist[nxt] again even "
                             "when a cheaper path through a later-popped node is found. Here A gets locked "
                             "in at distance 4 (via S directly) and never gets updated to the true shortest "
                             "distance 3 (via S -> B -> A), and C similarly gets stuck at 6 instead of the "
                             "true 4.",
             explanation_markdown="Fix: relax whenever a CHEAPER candidate is found, not just when the "
                                   "neighbor is unseen -- `if nxt not in dist or nd < dist[nxt]:` -- exactly "
                                   "this lesson's dijkstra. This is the single most common real bug in "
                                   "hand-written Dijkstra."),
        dict(kind="complexity",
             prompt_markdown="Dijkstra with a binary min-heap on a graph with V nodes and E edges costs how "
                              "much time?",
             code=None,
             choices_json=None,
             correct_answer="O((V + E) log V)",
             explanation_markdown="Each of the up to E relax operations can push onto the heap (O(log V) "
                                   "each, since the heap holds at most O(E) entries), and each of the V "
                                   "nodes is popped and finalized exactly once -- both bounded by "
                                   "O((V+E) log V) total."),
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
    "stacks": [
        dict(prompt_markdown="Write `remove_adjacent_duplicates(s)` that repeatedly removes pairs of adjacent "
                              "equal characters until none remain (e.g. `'abbaca'` -> `'ca'`: removing `bb` "
                              "makes the `a`s on either side newly adjacent, so they remove too, leaving "
                              "`'ca'`). Use a stack -- don't rebuild the string from scratch on every removal.",
             starter_code="def remove_adjacent_duplicates(s):\n    # push each character; if it matches the\n"
                          "    # top of the stack, pop instead of pushing\n    pass",
             solution_code=(
                 "def remove_adjacent_duplicates(s):\n"
                 "    stack = []\n"
                 "    for c in s:\n"
                 "        if stack and stack[-1] == c:\n"
                 "            stack.pop()\n"
                 "        else:\n"
                 "            stack.append(c)\n"
                 "    return ''.join(stack)"
             ),
             hint_markdown="For each character: if it equals the top of the stack, that's a fresh adjacent "
                            "pair -- pop instead of pushing (the pop can expose a NEW adjacent pair with "
                            "what's now on top, which the next character will catch). Otherwise push it."),
    ],
    "queues": [
        dict(prompt_markdown="Write `first_negative_in_each_window(nums, k)` that returns the first negative "
                              "number in every window of size k (0 if the window has none). Use a deque of "
                              "indices -- don't rescan each window from scratch.",
             starter_code="from collections import deque\n\ndef first_negative_in_each_window(nums, k):\n"
                          "    # track indices of negative numbers currently inside the window,\n"
                          "    # oldest first; evict from the front once an index ages out\n    pass",
             solution_code=(
                 "from collections import deque\n\n"
                 "def first_negative_in_each_window(nums, k):\n"
                 "    dq = deque()\n"
                 "    result = []\n"
                 "    for i, n in enumerate(nums):\n"
                 "        if n < 0:\n"
                 "            dq.append(i)\n"
                 "        if dq and dq[0] <= i - k:\n"
                 "            dq.popleft()\n"
                 "        if i >= k - 1:\n"
                 "            result.append(nums[dq[0]] if dq else 0)\n"
                 "    return result"
             ),
             hint_markdown="Only negative indices ever go in the deque, and they're always added in "
                            "increasing order -- so the front is always the FIRST negative number still "
                            "inside the window. Evict the front when its index is k or more behind i."),
    ],
    "recursion": [
        dict(prompt_markdown="Write `sum_digits(n)` that returns the sum of a non-negative integer's digits "
                              "using recursion -- no loops, and no converting to a string.",
             starter_code="def sum_digits(n):\n    # base case: a single digit (n < 10) is its own digit sum\n"
                          "    # recursive case: last digit (n % 10) + sum_digits of the rest (n // 10)\n    pass",
             solution_code=(
                 "def sum_digits(n):\n"
                 "    if n < 10:\n"
                 "        return n\n"
                 "    return n % 10 + sum_digits(n // 10)"
             ),
             hint_markdown="n % 10 peels off the last digit; n // 10 is everything else, a strictly smaller "
                            "number -- genuine progress toward the base case (a single digit)."),
    ],
    "backtracking": [
        dict(prompt_markdown="Write `letter_combinations(digits)` that returns every letter combination a "
                              "phone-keypad string of digits (2-9) could represent -- e.g. `'23'` -> "
                              "`['ad','ae','af','bd','be','bf','cd','ce','cf']` (2='abc', 3='def'). Use "
                              "backtracking.",
             starter_code="def letter_combinations(digits):\n    if not digits:\n        return []\n"
                          "    mapping = {'2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno',\n"
                          "               '7':'pqrs','8':'tuv','9':'wxyz'}\n"
                          "    # for each digit's position, try every one of its letters,\n"
                          "    # recurse into the next position, then un-choose\n    pass",
             solution_code=(
                 "def letter_combinations(digits):\n"
                 "    if not digits:\n"
                 "        return []\n"
                 "    mapping = {'2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno',\n"
                 "               '7':'pqrs','8':'tuv','9':'wxyz'}\n"
                 "    result = []\n"
                 "    path = []\n"
                 "    def backtrack(i):\n"
                 "        if i == len(digits):\n"
                 "            result.append(''.join(path))\n"
                 "            return\n"
                 "        for ch in mapping[digits[i]]:\n"
                 "            path.append(ch)\n"
                 "            backtrack(i + 1)\n"
                 "            path.pop()\n"
                 "    backtrack(0)\n"
                 "    return result"
             ),
             hint_markdown="Unlike subsets' include/exclude (2 choices per position), here each position has "
                            "as many choices as its digit has letters (3 or 4) -- loop over them, choosing "
                            "and un-choosing each one before moving to the next position."),
    ],
    "binary-search": [
        dict(prompt_markdown="Write `find_first_occurrence(arr, target)` that returns the index of the "
                              "FIRST occurrence of target in a sorted array that may contain duplicates, or "
                              "-1 if it's not present -- e.g. `find_first_occurrence([1,2,2,2,3,4,5], 2)` "
                              "returns `1`.",
             starter_code="def find_first_occurrence(arr, target):\n    lo, hi = 0, len(arr) - 1\n"
                          "    result = -1\n    # when you find target, don't stop -- record it and keep\n"
                          "    # searching the LEFT half for an even earlier occurrence\n    pass",
             solution_code=(
                 "def find_first_occurrence(arr, target):\n"
                 "    lo, hi = 0, len(arr) - 1\n"
                 "    result = -1\n"
                 "    while lo <= hi:\n"
                 "        mid = (lo + hi) // 2\n"
                 "        if arr[mid] == target:\n"
                 "            result = mid\n"
                 "            hi = mid - 1   # keep searching left for an earlier one\n"
                 "        elif arr[mid] < target:\n"
                 "            lo = mid + 1\n"
                 "        else:\n"
                 "            hi = mid - 1\n"
                 "    return result"
             ),
             hint_markdown="A normal binary search returns the instant it finds target. Here, finding it "
                            "isn't the end -- record the index, then keep narrowing toward the LEFT (hi = "
                            "mid - 1) in case an even earlier occurrence exists."),
    ],
    "binary-search-variants": [
        dict(prompt_markdown="Write `find_rotation_point(arr)` that returns the index of the minimum "
                              "element in a rotated sorted array with no duplicates -- e.g. "
                              "`find_rotation_point([4,5,6,7,0,1,2])` returns `4` (the array was originally "
                              "sorted, then rotated so it starts at index 4).",
             starter_code="def find_rotation_point(arr):\n    lo, hi = 0, len(arr) - 1\n"
                          "    # compare arr[mid] to arr[hi] to decide which half the minimum is in\n"
                          "    pass",
             solution_code=(
                 "def find_rotation_point(arr):\n"
                 "    lo, hi = 0, len(arr) - 1\n"
                 "    while lo < hi:\n"
                 "        mid = (lo + hi) // 2\n"
                 "        if arr[mid] > arr[hi]:\n"
                 "            lo = mid + 1   # minimum is to the right of mid\n"
                 "        else:\n"
                 "            hi = mid       # minimum is at mid or to its left\n"
                 "    return lo"
             ),
             hint_markdown="Compare arr[mid] against arr[hi], not arr[lo] -- if arr[mid] > arr[hi], the "
                            "rotation point (and the minimum) must be somewhere to the right of mid; "
                            "otherwise mid itself could BE the minimum, so hi shrinks down to mid, not past "
                            "it."),
    ],
    "sorting": [
        dict(prompt_markdown="Write `selection_sort(arr)` -- repeatedly find the MINIMUM of the unsorted "
                              "remainder and swap it into place at the front. Unlike bubble sort or "
                              "insertion sort (both curated as their own problems), this is a third "
                              "comparison-based approach: exactly one swap per pass, no matter how far out "
                              "of place the minimum was.",
             starter_code="def selection_sort(arr):\n    n = len(arr)\n    for i in range(n):\n"
                          "        # find the index of the minimum value in arr[i:], then swap it to arr[i]\n"
                          "        pass\n    return arr",
             solution_code=(
                 "def selection_sort(arr):\n"
                 "    n = len(arr)\n"
                 "    for i in range(n):\n"
                 "        min_idx = i\n"
                 "        for j in range(i + 1, n):\n"
                 "            if arr[j] < arr[min_idx]:\n"
                 "                min_idx = j\n"
                 "        arr[i], arr[min_idx] = arr[min_idx], arr[i]\n"
                 "    return arr"
             ),
             hint_markdown="Two nested loops, but a different shape than insertion sort's: the OUTER index i "
                            "marks the next position to fill; the INNER loop just scans arr[i+1:] to find "
                            "which index currently holds the smallest value, then one swap places it at i."),
    ],
    "divide-and-conquer-sorting": [
        dict(prompt_markdown="Write `quickselect(arr, k)` that returns the kth smallest element (0-indexed) "
                              "in arr WITHOUT fully sorting it -- e.g. `quickselect([7,2,9,4,1], 2)` returns "
                              "`4` (the 3rd smallest). Reuse this lesson's own `partition` function.",
             starter_code="def partition(arr, lo, hi):\n    pivot = arr[hi]\n    i = lo - 1\n"
                          "    for j in range(lo, hi):\n        if arr[j] <= pivot:\n            i += 1\n"
                          "            arr[i], arr[j] = arr[j], arr[i]\n"
                          "    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]\n    return i + 1\n\n"
                          "def quickselect(arr, k):\n    lo, hi = 0, len(arr) - 1\n"
                          "    # partition, then recurse into ONLY the side that contains index k\n    pass",
             solution_code=(
                 "def partition(arr, lo, hi):\n"
                 "    pivot = arr[hi]\n"
                 "    i = lo - 1\n"
                 "    for j in range(lo, hi):\n"
                 "        if arr[j] <= pivot:\n"
                 "            i += 1\n"
                 "            arr[i], arr[j] = arr[j], arr[i]\n"
                 "    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]\n"
                 "    return i + 1\n"
                 "\n"
                 "def quickselect(arr, k):\n"
                 "    lo, hi = 0, len(arr) - 1\n"
                 "    while True:\n"
                 "        p = partition(arr, lo, hi)\n"
                 "        if p == k:\n"
                 "            return arr[p]\n"
                 "        elif p < k:\n"
                 "            lo = p + 1\n"
                 "        else:\n"
                 "            hi = p - 1"
             ),
             hint_markdown="After one partition call, arr[p] is ALREADY in its final sorted position -- "
                            "compare p to k directly: if p == k you're done, if p < k the answer is "
                            "somewhere in the right side (lo = p + 1), otherwise it's in the left side "
                            "(hi = p - 1). Never recurse into both sides like quicksort does."),
    ],
    "trees": [
        dict(prompt_markdown="Write `count_leaves(values)` that returns the number of LEAF nodes (nodes "
                              "with no children) in the tree -- e.g. `count_leaves([1,2,3,4,5])` returns `3` "
                              "(nodes 4, 5, and 3 are the leaves; `values` is a level-order list, `None` for "
                              "a missing child, same as the curated tree problems use).",
             starter_code="class TreeNode:\n    def __init__(self, val):\n        self.val = val\n"
                          "        self.left = None\n        self.right = None\n\n"
                          "def build_tree(values):\n    if not values or values[0] is None:\n"
                          "        return None\n    root = TreeNode(values[0])\n    queue = [root]\n"
                          "    i = 1\n    while queue and i < len(values):\n        node = queue.pop(0)\n"
                          "        if i < len(values):\n            lv = values[i]; i += 1\n"
                          "            if lv is not None:\n                node.left = TreeNode(lv)\n"
                          "                queue.append(node.left)\n        if i < len(values):\n"
                          "            rv = values[i]; i += 1\n            if rv is not None:\n"
                          "                node.right = TreeNode(rv)\n                queue.append(node.right)\n"
                          "    return root\n\n"
                          "def count_leaves(values):\n    root = build_tree(values)\n"
                          "    # a leaf has BOTH node.left and node.right equal to None\n    pass",
             solution_code=(
                 "class TreeNode:\n"
                 "    def __init__(self, val):\n"
                 "        self.val = val\n"
                 "        self.left = None\n"
                 "        self.right = None\n"
                 "\n"
                 "def build_tree(values):\n"
                 "    if not values or values[0] is None:\n"
                 "        return None\n"
                 "    root = TreeNode(values[0])\n"
                 "    queue = [root]\n"
                 "    i = 1\n"
                 "    while queue and i < len(values):\n"
                 "        node = queue.pop(0)\n"
                 "        if i < len(values):\n"
                 "            lv = values[i]; i += 1\n"
                 "            if lv is not None:\n"
                 "                node.left = TreeNode(lv)\n"
                 "                queue.append(node.left)\n"
                 "        if i < len(values):\n"
                 "            rv = values[i]; i += 1\n"
                 "            if rv is not None:\n"
                 "                node.right = TreeNode(rv)\n"
                 "                queue.append(node.right)\n"
                 "    return root\n"
                 "\n"
                 "def count_leaves(values):\n"
                 "    root = build_tree(values)\n"
                 "    def helper(node):\n"
                 "        if node is None:\n"
                 "            return 0\n"
                 "        if node.left is None and node.right is None:\n"
                 "            return 1\n"
                 "        return helper(node.left) + helper(node.right)\n"
                 "    return helper(root)"
             ),
             hint_markdown="Base case: an empty subtree (None) contributes 0 leaves. Second case worth "
                            "checking BEFORE recursing: a node with no children IS a leaf, contributing 1 "
                            "on its own, with no need to recurse further. Otherwise, combine both children's "
                            "leaf counts."),
    ],
    "binary-search-trees": [
        dict(prompt_markdown="Write `search_bst(values, target)` that returns True if target exists in the "
                              "BST, False otherwise -- using the BST property to skip an entire subtree at "
                              "each step, not a full O(n) scan.",
             starter_code="class TreeNode:\n    def __init__(self, val):\n        self.val = val\n"
                          "        self.left = None\n        self.right = None\n\n"
                          "def build_tree(values):\n    if not values or values[0] is None:\n"
                          "        return None\n    root = TreeNode(values[0])\n    queue = [root]\n"
                          "    i = 1\n    while queue and i < len(values):\n        node = queue.pop(0)\n"
                          "        if i < len(values):\n            lv = values[i]; i += 1\n"
                          "            if lv is not None:\n                node.left = TreeNode(lv)\n"
                          "                queue.append(node.left)\n        if i < len(values):\n"
                          "            rv = values[i]; i += 1\n            if rv is not None:\n"
                          "                node.right = TreeNode(rv)\n                queue.append(node.right)\n"
                          "    return root\n\n"
                          "def search_bst(values, target):\n    root = build_tree(values)\n"
                          "    # compare target to node.val to decide whether to go left, right, or stop\n"
                          "    pass",
             solution_code=(
                 "class TreeNode:\n"
                 "    def __init__(self, val):\n"
                 "        self.val = val\n"
                 "        self.left = None\n"
                 "        self.right = None\n"
                 "\n"
                 "def build_tree(values):\n"
                 "    if not values or values[0] is None:\n"
                 "        return None\n"
                 "    root = TreeNode(values[0])\n"
                 "    queue = [root]\n"
                 "    i = 1\n"
                 "    while queue and i < len(values):\n"
                 "        node = queue.pop(0)\n"
                 "        if i < len(values):\n"
                 "            lv = values[i]; i += 1\n"
                 "            if lv is not None:\n"
                 "                node.left = TreeNode(lv)\n"
                 "                queue.append(node.left)\n"
                 "        if i < len(values):\n"
                 "            rv = values[i]; i += 1\n"
                 "            if rv is not None:\n"
                 "                node.right = TreeNode(rv)\n"
                 "                queue.append(node.right)\n"
                 "    return root\n"
                 "\n"
                 "def search_bst(values, target):\n"
                 "    node = build_tree(values)\n"
                 "    while node is not None:\n"
                 "        if node.val == target:\n"
                 "            return True\n"
                 "        elif target < node.val:\n"
                 "            node = node.left\n"
                 "        else:\n"
                 "            node = node.right\n"
                 "    return False"
             ),
             hint_markdown="No recursion needed -- this can be a plain while loop, since at each node there's "
                            "only ONE subtree worth continuing into (the BST property already tells you "
                            "which), not two. That's the whole reason it's O(log n) on a balanced tree "
                            "instead of O(n)."),
    ],
    "tree-bfs": [
        dict(prompt_markdown="Write `right_side_view(values)` that returns the value of the LAST node at "
                              "each level -- what you'd see looking at the tree from the right side -- e.g. "
                              "`right_side_view([1,2,3,None,5,None,4])` returns `[1, 3, 4]`.",
             starter_code="class TreeNode:\n    def __init__(self, val):\n        self.val = val\n"
                          "        self.left = None\n        self.right = None\n\n"
                          "def build_tree(values):\n    if not values or values[0] is None:\n"
                          "        return None\n    root = TreeNode(values[0])\n    queue = [root]\n"
                          "    i = 1\n    while queue and i < len(values):\n        node = queue.pop(0)\n"
                          "        if i < len(values):\n            lv = values[i]; i += 1\n"
                          "            if lv is not None:\n                node.left = TreeNode(lv)\n"
                          "                queue.append(node.left)\n        if i < len(values):\n"
                          "            rv = values[i]; i += 1\n            if rv is not None:\n"
                          "                node.right = TreeNode(rv)\n                queue.append(node.right)\n"
                          "    return root\n\n"
                          "def right_side_view(values):\n    root = build_tree(values)\n"
                          "    # level-order scan; within each level's snapshot, only the LAST node dequeued matters\n"
                          "    pass",
             solution_code=(
                 "class TreeNode:\n"
                 "    def __init__(self, val):\n"
                 "        self.val = val\n"
                 "        self.left = None\n"
                 "        self.right = None\n"
                 "\n"
                 "def build_tree(values):\n"
                 "    if not values or values[0] is None:\n"
                 "        return None\n"
                 "    root = TreeNode(values[0])\n"
                 "    queue = [root]\n"
                 "    i = 1\n"
                 "    while queue and i < len(values):\n"
                 "        node = queue.pop(0)\n"
                 "        if i < len(values):\n"
                 "            lv = values[i]; i += 1\n"
                 "            if lv is not None:\n"
                 "                node.left = TreeNode(lv)\n"
                 "                queue.append(node.left)\n"
                 "        if i < len(values):\n"
                 "            rv = values[i]; i += 1\n"
                 "            if rv is not None:\n"
                 "                node.right = TreeNode(rv)\n"
                 "                queue.append(node.right)\n"
                 "    return root\n"
                 "\n"
                 "def right_side_view(values):\n"
                 "    root = build_tree(values)\n"
                 "    if root is None:\n"
                 "        return []\n"
                 "    result = []\n"
                 "    q = [root]\n"
                 "    while q:\n"
                 "        level_size = len(q)\n"
                 "        for i in range(level_size):\n"
                 "            node = q.pop(0)\n"
                 "            if i == level_size - 1:\n"
                 "                result.append(node.val)\n"
                 "            if node.left:\n"
                 "                q.append(node.left)\n"
                 "            if node.right:\n"
                 "                q.append(node.right)\n"
                 "    return result"
             ),
             hint_markdown="This is the exact same level_size-snapshot technique from the lesson's own "
                            "walkthrough -- the only new part is checking `i == level_size - 1` inside the "
                            "inner loop to know when you've reached the LAST node of the current level."),
    ],
    "heaps": [
        dict(prompt_markdown="Write `is_min_heap(arr)` that returns True if arr satisfies the min-heap "
                              "property (every parent <= both of its children) at every index -- e.g. "
                              "`is_min_heap([1, 3, 8, 5])` returns `True`, but `is_min_heap([5, 3, 8, 1])` "
                              "returns `False`.",
             starter_code="def is_min_heap(arr):\n    n = len(arr)\n    for i in range(n):\n"
                          "        left, right = 2 * i + 1, 2 * i + 2\n"
                          "        # check arr[i] against arr[left] and arr[right], when those indices exist\n"
                          "        pass\n    return True",
             solution_code=(
                 "def is_min_heap(arr):\n"
                 "    n = len(arr)\n"
                 "    for i in range(n):\n"
                 "        left, right = 2 * i + 1, 2 * i + 2\n"
                 "        if left < n and arr[left] < arr[i]:\n"
                 "            return False\n"
                 "        if right < n and arr[right] < arr[i]:\n"
                 "            return False\n"
                 "    return True"
             ),
             hint_markdown="For every index i, its children live at 2i+1 and 2i+2 -- the exact same index "
                            "math HeapView uses to lay out the tree diagram above. A child index only needs "
                            "checking if it's actually within bounds (< n); if a check ever fails, you can "
                            "return False immediately, no need to keep scanning."),
    ],
    "top-k-heap": [
        dict(prompt_markdown="Write `k_closest_to_zero(nums, k)` that returns the k values closest to 0, "
                              "sorted -- e.g. `k_closest_to_zero([4, -1, 7, -3, 9, 2], 3)` returns "
                              "`[-3, -1, 2]`. Use a bounded heap, evicting the FARTHEST point (not the "
                              "smallest value) whenever size exceeds k.",
             starter_code="def k_closest_to_zero(nums, k):\n    heap = []\n    for n in nums:\n"
                          "        # push a tuple so the heap orders by DISTANCE from zero, not raw value --\n"
                          "        # this lesson's own max-heap-via-negation trick applies here too\n"
                          "        pass\n    return sorted(v for _, v in heap)",
             solution_code=(
                 "def k_closest_to_zero(nums, k):\n"
                 "    heap = []\n"
                 "    for n in nums:\n"
                 "        heapq.heappush(heap, (-abs(n), n))\n"
                 "        if len(heap) > k:\n"
                 "            heapq.heappop(heap)\n"
                 "    return sorted(v for _, v in heap)"
             ),
             hint_markdown="Push (-abs(n), n) instead of just n -- negating the distance means the point "
                            "FARTHEST from zero (largest abs(n)) becomes the SMALLEST tuple, which is what "
                            "heapq's min-heap evicts first. That's exactly the eviction you want: discard "
                            "the current worst (farthest) candidate whenever the heap grows past k."),
    ],
    "graphs": [
        dict(prompt_markdown="Write `common_neighbors(graph, a, b)` that returns a sorted list of nodes "
                              "adjacent to BOTH a and b -- e.g. with graph={'A':['B','C'], 'B':['A','C'], "
                              "'C':['B','A','D'], 'D':['C']}, `common_neighbors(graph, 'A', 'B')` returns "
                              "`['C']`.",
             starter_code="def common_neighbors(graph, a, b):\n"
                          "    # graph[a] and graph[b] are each a list of neighbor names --\n"
                          "    # turn both into sets and intersect them\n"
                          "    pass",
             solution_code=(
                 "def common_neighbors(graph, a, b):\n"
                 "    return sorted(set(graph[a]) & set(graph[b]))"
             ),
             hint_markdown="set(graph[a]) & set(graph[b]) gives you exactly the nodes present in BOTH "
                            "neighbor lists -- Python's set intersection operator does the comparison for "
                            "you in one line. sorted() just gives a predictable, testable order back."),
    ],
    "graph-bfs": [
        dict(prompt_markdown="Write `shortest_steps(grid, sr, sc, tr, tc)` that returns the minimum number "
                              "of moves from (sr,sc) to (tr,tc), moving only through 1-cells (up/down/left/"
                              "right), or -1 if the target is unreachable -- e.g. on "
                              "`grid=[[1,1,0],[0,1,0],[0,1,1]]`, `shortest_steps(grid, 0, 0, 2, 2)` returns "
                              "`4`.",
             starter_code="from collections import deque\n\n"
                          "def shortest_steps(grid, sr, sc, tr, tc):\n"
                          "    rows, cols = len(grid), len(grid[0])\n"
                          "    visited = {(sr, sc)}\n"
                          "    queue = deque([(sr, sc, 0)])\n"
                          "    while queue:\n"
                          "        r, c, d = queue.popleft()\n"
                          "        # check if (r, c) is the target; if not, enqueue unvisited\n"
                          "        # 1-neighbors with distance d + 1\n"
                          "        pass\n"
                          "    return -1",
             solution_code=(
                 "from collections import deque\n\n"
                 "def shortest_steps(grid, sr, sc, tr, tc):\n"
                 "    rows, cols = len(grid), len(grid[0])\n"
                 "    visited = {(sr, sc)}\n"
                 "    queue = deque([(sr, sc, 0)])\n"
                 "    while queue:\n"
                 "        r, c, d = queue.popleft()\n"
                 "        if (r, c) == (tr, tc):\n"
                 "            return d\n"
                 "        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n"
                 "            nr, nc = r + dr, c + dc\n"
                 "            if (0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1\n"
                 "                    and (nr, nc) not in visited):\n"
                 "                visited.add((nr, nc))\n"
                 "                queue.append((nr, nc, d + 1))\n"
                 "    return -1"
             ),
             hint_markdown="Check for the target the moment you POP a cell, not before enqueueing it -- "
                            "that's what guarantees the first time you reach it, d is its true shortest "
                            "distance. Mark a neighbor visited the moment you enqueue it (this lesson's own "
                            "duplicate-enqueue bug otherwise)."),
    ],
    "graph-dfs": [
        dict(prompt_markdown="Write `has_cycle_directed(graph)` that returns True if ANY part of the "
                              "(possibly disconnected) directed graph contains a cycle -- unlike the "
                              "lesson's has_cycle, which only checks reachability from one given start, "
                              "this needs to try DFS from every node that hasn't been visited yet.",
             starter_code="def has_cycle_directed(graph):\n"
                          "    visited = set()\n\n"
                          "    def dfs(node, on_stack):\n"
                          "        visited.add(node)\n"
                          "        on_stack.add(node)\n"
                          "        for nxt in graph[node]:\n"
                          "            # check nxt against on_stack (cycle) and visited (skip if\n"
                          "            # already fully explored)\n"
                          "            pass\n"
                          "        on_stack.discard(node)\n"
                          "        return False\n\n"
                          "    for node in graph:\n"
                          "        # try dfs from every node not yet visited\n"
                          "        pass\n"
                          "    return False",
             solution_code=(
                 "def has_cycle_directed(graph):\n"
                 "    visited = set()\n\n"
                 "    def dfs(node, on_stack):\n"
                 "        visited.add(node)\n"
                 "        on_stack.add(node)\n"
                 "        for nxt in graph[node]:\n"
                 "            if nxt in on_stack:\n"
                 "                return True\n"
                 "            if nxt not in visited and dfs(nxt, on_stack):\n"
                 "                return True\n"
                 "        on_stack.discard(node)\n"
                 "        return False\n\n"
                 "    for node in graph:\n"
                 "        if node not in visited:\n"
                 "            if dfs(node, set()):\n"
                 "                return True\n"
                 "    return False"
             ),
             hint_markdown="The inner dfs is identical to the lesson's has_cycle. The new part is the outer "
                            "loop: a graph can have multiple disconnected pieces, so a single DFS from one "
                            "start might never reach a cycle hiding in another piece -- loop over every node "
                            "in graph, and only start a fresh DFS (with a fresh on_stack) from ones not "
                            "already in visited."),
    ],
    "graph-shortest-paths": [
        dict(prompt_markdown="Write `cheapest_flight(graph, start, end)` that returns the shortest total "
                              "weight from start to end using Dijkstra, or -1 if end is unreachable -- e.g. "
                              "with `graph={'S': [('A', 4), ('B', 1)], 'B': [('A', 2), ('C', 5)], "
                              "'A': [('C', 1)], 'C': []}`, `cheapest_flight(graph, 'S', 'C')` returns `4`.",
             starter_code="import heapq\n\n"
                          "def cheapest_flight(graph, start, end):\n"
                          "    dist = {start: 0}\n"
                          "    heap = [(0, start)]\n"
                          "    finalized = set()\n"
                          "    while heap:\n"
                          "        d, node = heapq.heappop(heap)\n"
                          "        # skip if already finalized; otherwise finalize it, and return d\n"
                          "        # if node == end -- then relax every (neighbor, weight) pair in\n"
                          "        # graph.get(node, [])\n"
                          "        pass\n"
                          "    return -1",
             solution_code=(
                 "import heapq\n\n"
                 "def cheapest_flight(graph, start, end):\n"
                 "    dist = {start: 0}\n"
                 "    heap = [(0, start)]\n"
                 "    finalized = set()\n"
                 "    while heap:\n"
                 "        d, node = heapq.heappop(heap)\n"
                 "        if node in finalized:\n"
                 "            continue\n"
                 "        finalized.add(node)\n"
                 "        if node == end:\n"
                 "            return d\n"
                 "        for nxt, w in graph.get(node, []):\n"
                 "            nd = d + w\n"
                 "            if nxt not in dist or nd < dist[nxt]:\n"
                 "                dist[nxt] = nd\n"
                 "                heapq.heappush(heap, (nd, nxt))\n"
                 "    return -1"
             ),
             hint_markdown="Check node == end right after finalizing it, not before -- popping the heap "
                            "already guarantees d is the CHEAPEST possible way to reach node, since every "
                            "other candidate still in the heap (or not yet discovered) can only be equal or "
                            "worse. Skip an already-finalized node the same way the lesson's dijkstra does, "
                            "via a stale-entry check on pop."),
    ],
}
