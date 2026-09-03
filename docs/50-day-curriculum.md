# Codeloupe — 50-Day Python + DSA Curriculum

**Starting point:** zero Python, zero DSA except basic Big-O intuition.
**Target:** independently solve placement-level DSA problems in Python and explain the solution out loud.
**Pace:** ~3-4 hours/day, 50 consecutive days.

> **Status note (Sept 2026 expansion):** this doc was originally written and shipped as a 45-day/109-problem plan; it's now updated in place for the approved 45→50 day / 109→150 problem expansion (see `deliverables/EXPANSION_PLAN.md` for the full rationale). Renamed from `45-day-curriculum.md` for the same reason. Days 1-42 are content-identical to the original plan — nothing about the first 42 days changed. Days 43-50 (Block 7, was Days 43-45) are new/rewritten. See "Canonical curriculum vs. the Problem Bank pool" below for how the 150-problem bank relates to this day-by-day sequence.

## How to read each day

Every day lists exactly the 12 fields you asked for, in order:
1. Python concept(s) — new Python syntax/stdlib needed today (often "none new" — most days after Day 7 teach zero new Python and are pure DSA, deliberately, so Python fluency and DSA fluency don't fight for attention on the same day).
2. DSA concept(s)
3. Why — why this earns a day, and how it connects to what came before/after
4. Visual concept — what the trace visualizer / diagram should show you (built progressively as the app is built; usable as a paper-sketch even before the tool exists)
5. Coding exercises — small warm-ups before the named problems
6. Recommended problems
7. Difficulty (relative to a beginner's Day N, not absolute LeetCode difficulty — see the difficulty-labels note below for how this relates to the shipped product's actual Easy/Medium/Hard/Complex field)
8. Number of problems
9. What you must be able to explain before moving on — your own daily "exit ticket"
10. Common beginner mistakes — the specific bugs to watch for
11. Revision from previous days
12. Estimated time

**On revision (field 11):** each day gets a lightweight revision item — a 5-10 minute recall of the previous day's core idea, restated in your own words or by re-solving one small exercise from memory. Every block (roughly weekly) ends in a dedicated checkpoint/review day covering the whole block. This manual rule is intentionally simple; once the app's progress tracker (see `problem-roadmap.md` and `learning-philosophy.md`) has real performance data on you, it takes over with the adaptive 1-day/3-day/7-day/14-day schedule from `PART 10` of your brief — a fixed manual schedule can't do that well because it doesn't know yet what *you* actually struggle with, and that personalization is the entire point of the tracker.

**On difficulty labels:** Beginner-Easy < Easy < Easy-Medium < Medium < Medium-Hard, calibrated to where you are in the curriculum, not to LeetCode's absolute scale — a "Medium" on Day 20 and a "Medium" on Day 40 are not the same in absolute terms, but both should feel like a fair stretch at that point in your journey. **This is a relative, narrative label describing how a day's problems feel at that point in the plan — it is a separate thing from the shipped product's `problems.difficulty` database field**, which is a fixed, four-level scale used for real filtering/sorting/badges in the app: **Easy / Medium / Hard / Complex**, the same for every problem regardless of curriculum day. Complex is the newest of those four (added alongside the 109→150 expansion) — a genuine step above Hard, reserved for problems that are hard even by Advanced-tier standards; it is a difficulty level, not a topic or category, and every one of the app's 16 topics (including Greedy) has at least one Complex-difficulty problem.

**Topic-order note:** your brief listed two pointers/sliding window before sorting/binary search, but also grouped days 17-24 as "sorting, binary search, recursion, two pointers, sliding window." I resolved this by teaching two pointers and sliding window inside the Days 8-16 block (right after hashing, since they're array/string patterns and build directly on hashing's "have I seen this before" intuition), so Days 17-24 is purely sorting → binary search → recursion. This keeps every day building on the *immediately preceding* day rather than skipping around.

**Greedy note:** Greedy was added as the product's 16th topic in the same expansion that added the Complex difficulty. It does not get its own dedicated day-block the way two-pointer/sliding-window do — it's taught as a cross-curriculum pattern instead, via its own concept lesson (Learn hub) covering local-vs-global choice, recognition signals, and the exchange-argument intuition for *why* a greedy choice is safe. Some greedy-flavored problems already sit inside the day sequence below under their original topic (Day 8's Jump Game is an `arrays` problem that also demonstrates greedy reachability; Day 14's Container With Most Water similarly demonstrates greedy two-pointer reasoning under `two-pointer`) — their primary topic is deliberately unchanged, since that's still where they best teach their *day's* lesson, but the app's Greedy concept lesson surfaces them too as worked cross-topic examples. The rest of the Greedy-topic problem pool (Assign Cookies, Jump Game II, Gas Station, Partition Labels, Candy, Course Schedule III — spanning Easy through Complex) lives in the Problem Bank pool; see the canonical-vs-pool section below.

## Canonical curriculum vs. the Problem Bank pool

This document describes the day-by-day **teaching sequence** — what's introduced, in what order, and why. The shipped Problem Bank is larger than that sequence: **150 total problems**, of which a **day-tied subset** (currently 82 problems across Days 8-49) is what this doc walks through below, either as `path_tier='core'` (required for "Core Path" completion — Easy/Medium only, by design; see `decisions.md`) or as a specific day's *recommended, optional* pick from the Extended/Advanced pool (Days 44-49's mock-interview and advanced-practice problems — see Block 7 below). The remaining problems are **pool-only**: `path_tier='extended'` or `'advanced'`, `day=NULL`, browsable any time from the Problem Bank, never required, and never counted toward Core Path completion regardless of whether a day recommends one of their pool-mates. A problem having a day set is a "this is a good fit for that point in the plan" signal, not a completion requirement — only `path_tier='core'` gates Core Path completion.

---

## Block 1 — Days 1-7: Python Fundamentals (genuinely from zero)

### Day 1 — Variables, print, data types
1. **Python:** variables and assignment, `print()`, `input()`, core types (`int`, `float`, `str`, `bool`), comments (`#`).
2. **DSA:** what DSA is and why it matters for interviews; re-anchor your existing Big-O intuition as "the language we'll use every day from here on."
3. **Why:** you can't reason about algorithms without being able to write and run instructions. Naming Big-O vocabulary on Day 1 means every later day can use it naturally instead of re-teaching it.
4. **Visual:** a variable as a labeled box holding a value — `x` holds `5`, then `x` holds `10` after reassignment (the box's label doesn't change, its contents do).
5. **Exercises:** print a greeting; store name+age in variables and print a sentence using them; swap two variables' values; do simple arithmetic; read `input()` and print a doubled value.
6. **Recommended problems:** print "Hello, World"; sum of two user-input numbers; simple-interest calculator; Celsius→Fahrenheit converter. (Drills, not LeetCode — Day 1 has no LeetCode-style problems yet.)
7. **Difficulty:** Beginner-Easy.
8. **Number of problems:** 4 drills.
9. **Must explain:** what a variable is; the difference between `int`/`float`/`str`/`bool`; what `print()`/`input()` do; what a comment is.
10. **Common mistakes:** confusing `=` (assignment) with `==` (comparison, tomorrow's topic); forgetting quotes around strings; mixing `int` and `str` in `print` causing a `TypeError`; inconsistent indentation.
11. **Revision:** none (Day 1).
12. **Estimated time:** ~3-3.5h.

### Day 2 — Operators, conditionals, booleans
1. **Python:** arithmetic/comparison/logical operators, `if`/`elif`/`else`, truthiness.
2. **DSA:** none new — conditionals are how algorithms make decisions; this foreshadows how binary search/sorting use comparisons.
3. **Why:** almost every algorithm is "loop + condition." Fluency here is a prerequisite for everything else.
4. **Visual:** a decision-tree diagram showing which `if`/`elif`/`else` branch fires for a given input.
5. **Exercises:** even/odd checker; largest of 3 numbers; grade calculator via `if`/`elif` chain; FizzBuzz-style checks on 5 hardcoded numbers (no loop yet).
6. **Recommended problems:** leap-year checker; simple calculator (`+ - * /` via `if`/`elif`); FizzBuzz on hardcoded values.
7. **Difficulty:** Beginner-Easy.
8. **Number of problems:** 4.
9. **Must explain:** `=` vs `==`; how `elif` chains evaluate top-to-bottom; what `and`/`or`/`not` do; what "truthy/falsy" means in Python.
10. **Common mistakes:** using `=` instead of `==` in a condition; forgetting colons; misordering `elif` branches so an earlier one always matches; comparing floats for exact equality.
11. **Revision:** Day 1 (variables/types) — 5-minute recall before starting.
12. **Estimated time:** ~3.5h.

### Day 3 — Loops
1. **Python:** `while`, `for`, `range()`, `break`, `continue`, nested loops.
2. **DSA:** iteration as a core building block; loop count ↔ time complexity (one loop over n = O(n); nested loops foreshadow O(n²)).
3. **Why:** array/string algorithms are built almost entirely from loops. This is the day complexity stops being abstract and becomes "count the loop."
4. **Visual:** a loop counter animating `i` from `0 → 1 → 2 → ... → n-1` with a highlighted "current position" marker — this is literally the seed idea behind the trace visualizer you'll use later; worth noticing explicitly.
5. **Exercises:** print 1-10 with `while`, then `for`+`range`; sum of 1..n; multiplication table; count vowels in a hardcoded string; nested loop to print a small triangle of stars.
6. **Recommended problems:** print all even numbers up to N; factorial via loop; count digits of a number; reverse a number via loop (arithmetic, not string).
7. **Difficulty:** Beginner-Easy.
8. **Number of problems:** 4-5.
9. **Must explain:** `while` vs `for`; what `range(a,b)` actually generates (exclusive of `b`); when `break` vs `continue` fires; why nested loops multiply iteration count.
10. **Common mistakes:** off-by-one with `range()`; infinite `while` loops from forgetting to update the condition variable; confusing `break` (exits loop) with `continue` (skips iteration).
11. **Revision:** Day 2 (conditionals).
12. **Estimated time:** ~4h (loops are the single most important beginner concept — don't rush).

### Day 4 — Lists (arrays)
1. **Python:** list creation, indexing (incl. negative), slicing, `append`/`insert`/`pop`/`remove`/`len`/`in`/`sort`/`reverse`.
2. **DSA:** this *is* the array data structure — first real DSA structure. Vocabulary: index, element, contiguous. Python lists are dynamic arrays.
3. **Why:** nearly every early DSA problem is "do something to a list" — this is the bridge from Python syntax to DSA problems.
4. **Visual:** array-as-boxes-in-a-row with index labels above each box; show what visually changes on `append`/`pop`/`insert`.
5. **Exercises:** build a list from user inputs; access first/last/middle elements; slice sub-lists; find max/min with a manual loop (not `max()`, to force understanding); reverse manually with a loop, then compare to `.reverse()`.
6. **Recommended problems:** largest element in an array; second largest element; sum of array; count of even numbers; reverse an array in place.
7. **Difficulty:** Easy.
8. **Number of problems:** 5.
9. **Must explain:** 0-based indexing and negative indices; what `arr[a:b]` returns (a new list, exclusive of `b`); `append` vs `insert`; why "index out of range" happens.
10. **Common mistakes:** off-by-one on slicing; mutating a list while iterating it with `for`; confusing `append(x)` with `append([x])`; assuming `b = a` copies the list (it aliases — same object, a classic silent bug).
11. **Revision:** Day 3 (loops) — redo one loop exercise from memory.
12. **Estimated time:** ~4h.

### Day 5 — Strings
1. **Python:** indexing/slicing, immutability, `split`/`join`/`strip`/`replace`/`upper`/`lower`/`find`, f-strings.
2. **DSA:** strings as array-like-but-immutable — sets up two-pointer/sliding-window work later.
3. **Why:** string manipulation is one of the most common interview categories; understanding immutability prevents a whole class of bugs.
4. **Visual:** string-as-array-of-characters, same visual style as Day 4's array — reinforcing "a string is an array you can't modify in place."
5. **Exercises:** reverse a string with a manual loop (then compare to `s[::-1]`); palindrome check via manual loop; count each character's occurrences; split a sentence into words and count them.
6. **Recommended problems:** reverse a string; check palindrome; count vowels/consonants; find first non-repeating character (brute-force OK); check anagram (sort-and-compare version).
7. **Difficulty:** Easy.
8. **Number of problems:** 5.
9. **Must explain:** why strings are immutable and what that implies for building new strings; what `s[::-1]` does mechanically; `==` vs `is` for strings.
10. **Common mistakes:** trying to mutate a string in place; building strings with `+=` in a loop without knowing the performance cost (flagged now, formalized later); case-sensitivity bugs.
11. **Revision:** Day 4 (lists).
12. **Estimated time:** ~4h.

### Day 6 — Functions
1. **Python:** `def`, parameters, default arguments, `return` vs `print`, local vs global scope.
2. **DSA:** functions are how every interview solution is structured (`def twoSum(nums, target):`) — adopt this convention starting now.
3. **Why:** from tomorrow on, every problem is "write a function that takes X, returns Y" — the actual format of interview platforms and of this app's automated testing.
4. **Visual:** a function-call diagram — arguments flow in, a return value flows out, like a small black box (foreshadowing: the trace visualizer will let you see *inside* that box).
5. **Exercises:** function returning max of two numbers; function checking primality; parameterized sum-of-array function (reusing Day 4's exercise); a function with a default argument.
6. **Recommended problems:** rewrite 3 problems from Days 4-5 (largest element, palindrome check, anagram check) as proper functions with clean signatures; 2 new small functions.
7. **Difficulty:** Easy.
8. **Number of problems:** 5 (3 rewrites + 2 new).
9. **Must explain:** `return` vs `print`; what happens to a variable defined inside a function once it returns (scope); what a function signature is and why matching it matters for automated testing.
10. **Common mistakes:** using `print()` instead of `return` in a function meant to produce a value (breaks automated testing — call this out explicitly); not handling empty-list/empty-string input; shadowing a built-in name (`list`, `sum`) as a variable.
11. **Revision:** Days 4-5 combined (arrays + strings).
12. **Estimated time:** ~4h.

### Day 7 — Dictionaries, sets, Week 1 checkpoint
1. **Python:** dict creation, `in` membership, `.get()`, `.keys()`/`.values()`/`.items()`, sets.
2. **DSA:** on-ramp to hashing (Days 11-12) — a dict *is* Python's hash map. Contrast O(1)-average dict lookup against Day 4's O(n) list search.
3. **Why:** hashing is one of the highest-frequency interview patterns, and everything from here depends on dict/set fluency.
4. **Visual:** side-by-side — a list scanned linearly (arrow moving element-by-element) vs a dict looked up directly (arrow jumping straight to the value).
5. **Exercises:** word-frequency counter using a dict; duplicate check in a list using a set; simple name→number phonebook with add/lookup/delete.
6. **Recommended problems:** Two Sum (brute-force O(n²) only — optimal version comes Day 11); Contains Duplicate; first repeated element in an array.
7. **Difficulty:** Easy.
8. **Number of problems:** 3.
9. **Must explain:** list membership check vs dict/set membership check, mechanically (linear scan vs hash lookup); what a dict key must satisfy (hashable — no lists as keys); `[]` vs `.get()` on a missing key.
10. **Common mistakes:** using a list where a set fits better for membership checks; `KeyError` instead of `.get()`; relying on dict ordering without understanding why it's guaranteed (Python ≥3.7) instead of just assuming it.
11. **Revision:** **Week 1 checkpoint** — one 5-minute recall question per Day 1-6 topic.
12. **Estimated time:** ~3.5-4h (lighter on new material, heavier on review).

---

## Block 2 — Days 8-16: Arrays, Strings, Hashing, Two Pointers, Sliding Window

### Day 8 — Array patterns I: traversal & in-place modification
1. **Python:** list comprehensions (intro), `enumerate()`.
2. **DSA:** in-place modification, O(1) extra-space constraint.
3. **Why:** list comprehensions/`enumerate` are used in nearly every array solution from here; "solve in O(1) extra space" is a very common interview constraint.
4. **Visual:** array boxes with a "read pointer" and "write pointer" moving at different speeds during in-place removal.
5. **Exercises:** remove duplicates from a sorted array in place; move zeroes to the end in place; rotate an array by k (brute-force).
6. **Recommended problems:** Remove Duplicates from Sorted Array; Move Zeroes; Rotate Array (brute force).
7. **Difficulty:** Easy.
8. **Number of problems:** 3.
9. **Must explain:** what "in-place"/"O(1) extra space" concretely mean; how `enumerate()` replaces manual index tracking; why `arr = arr[1:]` is *not* in-place.
10. **Common mistakes:** mutating a list mid-iteration with `for x in arr` (index-skipping bug); confusing reassignment with in-place mutation.
11. **Revision:** Day 7 (hashing/dicts).
12. **Estimated time:** ~3.5h.

### Day 9 — Array patterns II: prefix sums
1. **Python:** `zip()`, tuple unpacking.
2. **DSA:** prefix-sum technique for O(1) range-sum queries after O(n) precompute.
3. **Why:** first "precompute now, save time later" lesson — a very common optimization shape.
4. **Visual:** a running-total bar building left-to-right beneath the array: `prefix[i] = prefix[i-1] + arr[i]`.
5. **Exercises:** build a prefix-sum array by hand; answer 3 range-sum queries with it; compare cost against recomputing each time.
6. **Recommended problems:** Running Sum of 1d Array; Find Pivot Index; single-query Range Sum.
7. **Difficulty:** Easy.
8. **Number of problems:** 3.
9. **Must explain:** how `prefix[i]` derives from `prefix[i-1]`; why this converts O(n)-per-query into O(1)-per-query after an O(n) precompute.
10. **Common mistakes:** off-by-one mapping a prefix-array index to the original range; mishandling index 0 as base case.
11. **Revision:** Day 8.
12. **Estimated time:** ~3.5h.

### Day 10 — Strings deep dive
1. **Python:** `''.join()`, `list(s)`, `sorted()` on strings.
2. **DSA:** character-comparison and character-frequency patterns.
3. **Why:** string problems recur constantly and nearly always reduce to "compare characters" or "count characters."
4. **Visual:** two strings side-by-side, matches green / mismatches red; pointers converging from both ends for palindrome checks.
5. **Exercises:** palindrome check without slicing (two-pointer style, foreshadowing Day 13); anagram check via sorting; anagram check via counting (compare complexity of both).
6. **Recommended problems:** Valid Palindrome; Valid Anagram; Longest Common Prefix.
7. **Difficulty:** Easy.
8. **Number of problems:** 3.
9. **Must explain:** two anagram-check approaches and their complexity tradeoff (O(n log n) sort vs O(n) counting); why `''.join(list)` beats repeated `+=` for building strings.
10. **Common mistakes:** ignoring case/whitespace/punctuation in palindrome checks without being told to; assuming `sorted()` on a string returns a string (it returns a list).
11. **Revision:** Day 9 (prefix sums).
12. **Estimated time:** ~3.5h.

### Day 11 — Hashing I: Two Sum pattern
1. **Python:** dict comprehensions, `collections.defaultdict` (intro).
2. **DSA:** "have I seen this value/complement before?" — the canonical hashing pattern.
3. **Why:** Two Sum's hash-map solution is the textbook example of trading space for time and one of the most-asked patterns in existence.
4. **Visual:** array traversal with a live dict panel beside it, showing key:value pairs inserted as the loop runs, and a lookup flash when a complement is found.
5. **Exercises:** implement Two Sum brute-force (O(n²)) then optimal (O(n)); implement Contains Duplicate with a set.
6. **Recommended problems:** Two Sum (optimal); Contains Duplicate; Single Number.
7. **Difficulty:** Easy.
8. **Number of problems:** 3.
9. **Must explain:** why storing "value seen so far → index" gives O(1) complement lookup instead of re-scanning; the O(n)-time/O(n)-space tradeoff vs brute force's O(n²)/O(1).
10. **Common mistakes:** checking for the complement *before* inserting the current element and getting indices wrong; accidentally reusing the same element twice.
11. **Revision:** Day 10, plus a Days 8-9 spot check (block checkpoint approaching).
12. **Estimated time:** ~4h.

### Day 12 — Hashing II: frequency & grouping
1. **Python:** `collections.Counter`, sorting dict items by value.
2. **DSA:** frequency-map pattern, group-by-key pattern.
3. **Why:** "count occurrences then decide" is the second core hashing pattern; `Counter` is what real code uses (after understanding how to build one by hand).
4. **Visual:** bar-chart-style frequency panel updating live as elements are scanned.
5. **Exercises:** first unique character in a string; top-k frequent elements (sort-based brute force); group anagrams (brute force).
6. **Recommended problems:** First Unique Character in a String; Group Anagrams; Top K Frequent Elements (sort-based).
7. **Difficulty:** Easy-Medium.
8. **Number of problems:** 3.
9. **Must explain:** how a sorted-tuple/frequency-tuple can serve as a dict key for grouping; manual frequency dict vs `Counter`.
10. **Common mistakes:** using a mutable type (list) as a dict key (fails — needs a tuple); off-by-one between "first" and "any" unique element.
11. **Revision:** Day 11.
12. **Estimated time:** ~4h.

### Day 13 — Two pointers I: opposite-direction on sorted data
1. **Python:** none new — pattern-focused, reusing Day 3's `while`.
2. **DSA:** two-pointer technique on sorted arrays.
3. **Why:** converts many O(n²) brute forces into O(n); one of the most-tested placement patterns.
4. **Visual:** two arrows (left, right) moving toward each other on the array, with the running comparison shown at each step.
5. **Exercises:** pair-with-target-sum on sorted array via two pointers (compare against Day 11's hashmap approach — discuss when each is better); redo Day 8's duplicate-removal with explicit two-pointer framing.
6. **Recommended problems:** Two Sum II (sorted input); Remove Duplicates from Sorted Array (revisited); Squares of a Sorted Array.
7. **Difficulty:** Easy.
8. **Number of problems:** 3.
9. **Must explain:** why two pointers needs sorted (or sortable) data; how to decide which pointer to move based on a comparison; O(n)/O(1) vs the hashmap's O(n)/O(n).
10. **Common mistakes:** forgetting to sort first; pointers crossing incorrectly or missing the last valid pair (off-by-one).
11. **Revision:** Day 12.
12. **Estimated time:** ~3.5h.

### Day 14 — Two pointers II: same-direction / container problems
1. **Python:** none new.
2. **DSA:** same-direction two pointers, greedy pointer movement.
3. **Why:** this variant reappears in linked-list problems (Day 27) — building intuition now pays off twice.
4. **Visual:** two vertical "wall" bars on a bar-chart array, shaded area between them shrinking as the shorter wall moves inward.
5. **Exercises:** Container With Most Water brute-force (O(n²)) then two-pointer (O(n)), compared explicitly; Move Zeroes reframed through the same-direction lens.
6. **Recommended problems:** Container With Most Water; Move Zeroes (reframed); Valid Palindrome II (optional stretch).
7. **Difficulty:** Easy-Medium.
8. **Number of problems:** 2-3.
9. **Must explain:** why moving the pointer at the *shorter* wall is the only move that can possibly improve the area (the greedy proof, not just the rule).
10. **Common mistakes:** moving the taller wall (can never improve the answer); off-by-one on width calculation.
11. **Revision:** Day 13.
12. **Estimated time:** ~3.5h.

### Day 15 — Sliding window I: fixed size
1. **Python:** none new.
2. **DSA:** fixed-size sliding window — incremental update instead of recompute.
3. **Why:** natural next step after prefix sums and two pointers — "two pointers plus a running aggregate," very common in arrays and strings.
4. **Visual:** a highlighted "window" rectangle sliding across the array one step at a time, sum updating incrementally (subtract outgoing, add incoming) rather than recomputed.
5. **Exercises:** maximum sum subarray of fixed size k; average of subarrays of size k.
6. **Recommended problems:** Maximum Average Subarray I; Maximum Sum Subarray of Size K (classic pattern problem).
7. **Difficulty:** Easy.
8. **Number of problems:** 2-3.
9. **Must explain:** why sliding (subtract outgoing + add incoming) is O(1) per step vs O(k) recomputation, giving O(n) total instead of O(n·k).
10. **Common mistakes:** recomputing the full window sum every slide instead of updating incrementally (correct but defeats the purpose — the app's complexity checker should flag this); off-by-one on window boundaries.
11. **Revision:** Day 14, plus a Days 8-9 spot check.
12. **Estimated time:** ~3.5h.

### Day 16 — Sliding window II: variable size; Block 2 checkpoint
1. **Python:** none new.
2. **DSA:** variable-size sliding window (grow/shrink based on a condition).
3. **Why:** the more powerful, more commonly tested sliding-window variant, combining directly with Days 7/11-12's hashing.
4. **Visual:** window rectangle that grows right / shrinks left independently, with a dict panel showing in-window character counts.
5. **Exercises:** longest substring without repeating characters; minimum-size subarray with sum ≥ target.
6. **Recommended problems:** Longest Substring Without Repeating Characters; Minimum Size Subarray Sum.
7. **Difficulty:** Medium.
8. **Number of problems:** 2.
9. **Must explain:** the grow/shrink invariant (when to expand right vs contract left), and why this is still O(n) total despite looking nested (informal amortized-analysis intuition).
10. **Common mistakes:** shrinking with `if` instead of `while` (misses cases needing multiple shrinks per step); updating "best answer so far" at the wrong point relative to shrinking.
11. **Revision:** **Block 2 checkpoint** — one recall question for each of: arrays, prefix sums, strings, hashing, two pointers, sliding window.
12. **Estimated time:** ~4h.

---

## Block 3 — Days 17-24: Sorting, Binary Search, Recursion

### Day 17 — Sorting I: bubble sort, selection sort
1. **Python:** tuple-swap (`a, b = b, a`).
2. **DSA:** comparison-based sorting, stability concept (intro).
3. **Why:** simplest sorts to implement/reason about — the first "algorithm as a sequence of comparisons/swaps," exactly what the trace visualizer will show.
4. **Visual:** bar-chart array, two bars highlighted (comparing), then animated swap, pass by pass.
5. **Exercises:** implement bubble sort; implement selection sort; count swaps/comparisons each makes on the same input.
6. **Recommended problems:** implement bubble sort; implement selection sort (self-implementation is the "problem" today).
7. **Difficulty:** Easy.
8. **Number of problems:** 2 implementation exercises.
9. **Must explain:** how bubble sort's "bubbling" works pass by pass; why selection sort swaps less but compares the same amount; both are O(n²)/O(1).
10. **Common mistakes:** skipping bubble sort's early-exit optimization (no swaps ⇒ already sorted); off-by-one in inner-loop bounds.
11. **Revision:** Block 2 checkpoint recall (one question per Block 2 topic).
12. **Estimated time:** ~3.5h.

### Day 18 — Sorting II: insertion sort, built-in `sort`
1. **Python:** `sorted(iterable, key=..., reverse=...)`, `list.sort()`.
2. **DSA:** insertion sort mechanics; when built-in Timsort (O(n log n)) is appropriate vs your own.
3. **Why:** insertion sort is the best mental bridge to merge sort; `key=` fluency is used constantly in real interview code.
4. **Visual:** a growing "sorted portion" (shaded, left side) as each new element is inserted at its correct position — card-sorting style.
5. **Exercises:** implement insertion sort; sort tuples by second element with `key=`; sort strings by length.
6. **Recommended problems:** implement insertion sort; sort `(name, score)` pairs by score descending via `sorted(..., key=..., reverse=True)`.
7. **Difficulty:** Easy.
8. **Number of problems:** 2.
9. **Must explain:** why insertion sort is efficient (adaptive) on nearly-sorted data despite O(n²) worst case; what `key=` actually does (compares `key(x)`, doesn't sort by the key's value directly).
10. **Common mistakes:** `arr = arr.sort()` (returns `None` — sort is in-place); backwards `key=` lambda.
11. **Revision:** Day 17.
12. **Estimated time:** ~3.5h.

### Day 19 — Sorting III: merge sort
1. **Python:** none new (uses recursion practically before it's formally named on Day 23 — intentional: see it work first).
2. **DSA:** divide-and-conquer, merge step, O(n log n).
3. **Why:** the first "smart" algorithm you'll build — the jump from O(n²) to O(n log n) is the most important complexity lesson in the curriculum.
4. **Visual:** recursive split diagram (array halving down to single elements) followed by a merge-back-up animation zippering two sorted halves together.
5. **Exercises:** implement the merge step alone (merge two sorted arrays); then implement full merge sort using it.
6. **Recommended problems:** implement merge sort; merge two sorted arrays/lists (independently interview-relevant on its own).
7. **Difficulty:** Medium.
8. **Number of problems:** 2.
9. **Must explain:** why halving repeatedly gives `log n` levels, why each level does O(n) total merge work, hence O(n log n) overall — must be able to sketch this on paper.
10. **Common mistakes:** off-by-one on the midpoint; missing base case (length ≤ 1) causing infinite recursion; mishandling leftover elements when one half empties first during merge.
11. **Revision:** Day 18, plus Day 17.
12. **Estimated time:** ~4h.

### Day 20 — Sorting IV: quicksort
1. **Python:** none new.
2. **DSA:** partition-based divide-and-conquer, pivot choice, average vs worst case.
3. **Why:** the most commonly discussed sort in interviews; its partition logic directly reappears in quickselect-style "kth largest" problems.
4. **Visual:** pivot highlighted, elements sliding left/right of it as compared, recursive zoom-in on each partition.
5. **Exercises:** implement partition alone; then full quicksort; discuss why a bad pivot (sorted input + always-first-element pivot) degrades to O(n²).
6. **Recommended problems:** implement quicksort; Kth Largest Element in an Array (full-sort brute force — quickselect optional/stretch).
7. **Difficulty:** Medium.
8. **Number of problems:** 2.
9. **Must explain:** how one partition pass rearranges elements around a pivot; why average case is O(n log n) but worst case O(n²); why random/median pivot selection mitigates the worst case.
10. **Common mistakes:** infinite loop from incorrect partition pointer movement; mishandling duplicate values; off-by-one on swap boundaries.
11. **Revision:** Day 19 — explicit merge-sort-vs-quicksort tradeoff comparison as the recall question.
12. **Estimated time:** ~4h.

### Day 21 — Binary search I: classic
1. **Python:** none new.
2. **DSA:** O(log n) search — the second core "smart algorithm."
3. **Why:** appears constantly, directly and as a sub-pattern ("binary search the answer") in medium/hard problems; also a great debugging lesson since it's easy to get subtly wrong.
4. **Visual:** sorted array with low/mid/high pointers; search space shrinking (grayed out) by half each step.
5. **Exercises:** implement iteratively, then recursively (foreshadowing Day 23); trace by hand on a 7-element array before coding.
6. **Recommended problems:** Binary Search (classic); Search Insert Position.
7. **Difficulty:** Easy.
8. **Number of problems:** 2.
9. **Must explain:** why the data must be sorted; why `mid = low + (high-low)//2` is preferred (overflow reasoning, still expected knowledge even though Python ints don't overflow); why this is O(log n).
10. **Common mistakes:** `low <= high` vs `low < high` confusion; off-by-one on `low = mid+1`/`high = mid-1`; a branch that fails to shrink the range (infinite loop).
11. **Revision:** Days 20 and 19 — "how does binary search's halving relate to merge sort's halving?"
12. **Estimated time:** ~3.5h.

### Day 22 — Binary search II: variants
1. **Python:** none new.
2. **DSA:** binary search on modified conditions; "binary search the answer" (intro concept).
3. **Why:** real interview binary-search questions are almost always a variant — this builds template flexibility instead of memorization.
4. **Visual:** same halving visual applied to a "rotated" array, showing how to determine which half is still sorted at each step.
5. **Exercises:** first/last occurrence of a target with duplicates present; search in a rotated sorted array.
6. **Recommended problems:** Find First and Last Position of Element in Sorted Array; Search in Rotated Sorted Array.
7. **Difficulty:** Medium.
8. **Number of problems:** 2.
9. **Must explain:** how to modify the base template to keep searching after a match (first/last occurrence); how to decide which half of a rotated array is sorted.
10. **Common mistakes:** returning too early on first match instead of continuing to search; wrong condition for identifying the sorted half.
11. **Revision:** Day 21.
12. **Estimated time:** ~4h.

### Day 23 — Recursion I: call stack, base case (major topic — take your time)
1. **Python:** functions calling themselves — formal recursion rules.
2. **DSA:** recursion as a paradigm. This is a major beginner hurdle and gets its own unhurried day rather than being folded into sorting.
3. **Why:** recursion underlies trees, backtracking, and DP — arguably the single hardest concept in the whole curriculum, worth full attention now.
4. **Visual:** the recursion-tree/call-stack visualizer — stacked boxes appearing as calls go deeper (each showing its parameters), then popping and returning values back up as base cases resolve. Trace `factorial(4)` by hand, frame by frame, *before* writing code.
5. **Exercises:** implement factorial recursively; sum of first n numbers recursively; naive recursive Fibonacci (deliberately — sets up Day 39's "this is slow" lesson).
6. **Recommended problems:** Factorial (recursive); Sum of Digits (recursive); Fibonacci (naive recursive) — trace by hand first, then code.
7. **Difficulty:** conceptually simple, but genuinely Medium to *truly* understand.
8. **Number of problems:** 3.
9. **Must explain:** what a base case is and why every recursive function needs one; what happens on the call stack as calls deepen then return; why naive Fibonacci is exponential (draw the tree, count nodes).
10. **Common mistakes:** missing/incorrect base case → infinite recursion / `RecursionError`; calling the recursive call but discarding its return value; off-by-one in the base-case boundary.
11. **Revision:** Day 22.
12. **Estimated time:** ~4h (budget extra — do not rush recursion).

### Day 24 — Recursion II: branching recursion, intro backtracking; Block 3 checkpoint
1. **Python:** none new.
2. **DSA:** multiple recursive calls per invocation; backtracking as "recursion + undo."
3. **Why:** bridges into tree/graph traversal (Weeks 4-5); backtracking is a common interview topic in its own right, even in basic form.
4. **Visual:** a branching recursion tree (2+ children per node) for generating subsets of a 3-element set, showing "include"/"exclude" branches.
5. **Exercises:** generate all subsets of a small set (≤4 elements); generate all permutations of a small set (≤3 elements).
6. **Recommended problems:** Subsets; Permutations (small inputs — correctness over performance).
7. **Difficulty:** Medium.
8. **Number of problems:** 2.
9. **Must explain:** the "choose / explore / un-choose" backtracking pattern; why the subset count is 2ⁿ (ties directly to the tree's branching factor).
10. **Common mistakes:** forgetting to copy the current path before saving it to results (appending a reference that later mutates); not "undoing" a choice before the next branch.
11. **Revision:** **Block 3 checkpoint** — one recall question per topic across Days 17-23 (sorting ×4, binary search ×2, recursion).
12. **Estimated time:** ~4h.

---

## Block 4 — Days 25-32: Linked Lists, Stacks, Queues, Trees

### Day 25 — Linked lists I: nodes, references, traversal
1. **Python:** classes (`class`, `__init__`, `self`) — first real OOP, taught minimally and just-in-time.
2. **DSA:** node + `next`-pointer structure; contrast with arrays (no random access, O(1) head insertion).
3. **Why:** first "build your own data structure" topic and the natural home for a first real class; also where the trace visualizer becomes essential — pointers are invisible without a diagram.
4. **Visual:** boxes connected by arrows (`node → next → node → next → None`), current traversal pointer highlighted as it moves.
5. **Exercises:** define a `Node` class; build a 4-node list by hand; write a traversal-and-print function; compute list length.
6. **Recommended problems:** traverse and print a linked list; compute its length (implementation exercises).
7. **Difficulty:** conceptually Easy, unfamiliarity-wise Medium (first OOP + first pointer structure together).
8. **Number of problems:** 2.
9. **Must explain:** what `self` refers to; what `.next` actually stores (a reference to another `Node`, not a copy); why moving a traversal pointer forward without saving a reference loses access to earlier nodes.
10. **Common mistakes:** losing the head reference by reassigning it during traversal (always use a separate `current` pointer); forgetting the final node's `.next` must be `None`; confusing a `Node` with its `.val`.
11. **Revision:** Day 24, plus a light Days 17-23 spot check.
12. **Estimated time:** ~4h.

### Day 26 — Linked lists II: insertion, deletion
1. **Python:** none new.
2. **DSA:** pointer rewiring for insert/delete at head/tail/middle/by-value.
3. **Why:** this is where linked lists' O(1)-insertion advantage over arrays (no shifting) becomes concrete; a very common interview sub-routine.
4. **Visual:** arrow-rewiring animation — old arrow fading, new arrow appearing, showing exactly which `.next` values change.
5. **Exercises:** insert at head/tail/after a given node; delete by value; delete the head.
6. **Recommended problems:** insert into a linked list at position k; delete a node by value (implementation exercises).
7. **Difficulty:** Medium.
8. **Number of problems:** 2.
9. **Must explain:** why head insertion is O(1) but tail insertion is O(n) without a tail pointer; the exact operation order needed to avoid losing the rest of the list.
10. **Common mistakes:** overwriting a `.next` before saving the reference it pointed to (loses the rest of the list); not special-casing head deletion; off-by-one on "insert after position k."
11. **Revision:** Day 25.
12. **Estimated time:** ~4h.

### Day 27 — Linked lists III: reversal, cycle detection
1. **Python:** none new.
2. **DSA:** in-place reversal; Floyd's cycle detection (fast/slow, "tortoise and hare").
3. **Why:** reverse-a-linked-list is one of the single most-asked interview questions everywhere; fast/slow pointers reappear constantly (middle-of-list, cycle detection, palindrome check) and directly extend Day 14's same-direction two-pointer intuition.
4. **Visual:** reversal shown as arrows flipping direction one at a time via three pointers (`prev`, `curr`, `next`); cycle detection shown as two pointers at different speeds meeting inside a loop.
5. **Exercises:** reverse a list iteratively; trace fast/slow pointers by hand on a small cyclic list before coding; implement cycle detection.
6. **Recommended problems:** Reverse Linked List; Linked List Cycle (Floyd's); Middle of the Linked List (fast/slow variant).
7. **Difficulty:** Medium.
8. **Number of problems:** 3.
9. **Must explain:** the three-pointer reversal mechanics step by step; why fast/slow pointers must eventually meet if a cycle exists; why this achieves O(1) space (no visited-set needed).
10. **Common mistakes:** losing the rest of the list by not saving `next` before reversing `curr.next`; off-by-one dropping the last node; using a set to "detect cycles" (defeats the point of the O(1)-space technique).
11. **Revision:** Day 26.
12. **Estimated time:** ~4h.

### Day 28 — Stacks
1. **Python:** list as a stack (`append`/`pop`), or `collections.deque` as an alternative.
2. **DSA:** LIFO structure and its canonical uses (matching/nesting, undo, DFS foreshadowing).
3. **Why:** simple to implement but powers a disproportionate number of interview problems.
4. **Visual:** a vertical stack of plates — push adds to top, pop removes from top, "top" pointer highlighted; walked through live for parentheses matching.
5. **Exercises:** implement a stack with a list; trace valid-parentheses matching by hand on `"({[]})"` and a broken example before coding.
6. **Recommended problems:** Valid Parentheses; Min Stack (optional stretch); Baseball Game (optional stretch).
7. **Difficulty:** Easy.
8. **Number of problems:** 1-2 core + optional stretch.
9. **Must explain:** why LIFO order is exactly what nested-structure matching needs; why counters alone fail (ordering, e.g. `"])("`).
10. **Common mistakes:** popping from an empty stack (`IndexError`); forgetting to check the stack is empty at the end (unmatched opens remaining).
11. **Revision:** Day 27, and a natural moment to compare "linked list as an alternative stack implementation."
12. **Estimated time:** ~3.5h.

### Day 29 — Queues
1. **Python:** `collections.deque` properly (`popleft`, `appendleft`, O(1) both ends vs list's O(n) `pop(0)`).
2. **DSA:** FIFO structure; why `deque` over a plain list for queues.
3. **Why:** queues are the backbone of BFS (Day 36) — today exists specifically to make BFS easy later.
4. **Visual:** a horizontal line, new items entering right, served from left — contrasted directly with yesterday's single-ended stack visual.
5. **Exercises:** implement a queue with `deque`; simulate a ticket queue; compare `list.pop(0)` cost vs `deque.popleft()` conceptually.
6. **Recommended problems:** Implement Queue using two Stacks (reinforces both structures at once); Design Circular Queue (optional stretch).
7. **Difficulty:** Easy-Medium.
8. **Number of problems:** 1-2.
9. **Must explain:** FIFO vs LIFO, compared directly to yesterday's stack; why `list.pop(0)` is O(n) (shifting) but `deque.popleft()` is O(1); why this matters for BFS later.
10. **Common mistakes:** using a plain list with `pop(0)` in performance-sensitive code (works, but slow — the complexity benchmarker should catch this); circular-queue index-wraparound off-by-one, if attempted.
11. **Revision:** Day 28 — direct stack-vs-queue compare/contrast.
12. **Estimated time:** ~3.5h.

### Day 30 — Trees I: structure, traversals
1. **Python:** none new — heavy reuse of Day 25's classes and Day 23's recursion.
2. **DSA:** binary tree structure; preorder/inorder/postorder traversal and their uses. (The app's mock-interview mode unlocks around this point per your spec — light/optional use only; the dedicated mock-interview days are 43-45.)
3. **Why:** trees are where recursion and node/reference structures combine — if those two topics genuinely landed, this day should feel like a satisfying click, not new difficulty.
4. **Visual:** a small binary tree with nodes highlighting in visit order per traversal type, shown alongside a recursion-tree/call-stack view (echoing Day 23) so the connection is explicit.
5. **Exercises:** define a `TreeNode` class; build a ≤7-node tree by hand; implement all three traversals recursively; predict traversal output on paper before running code.
6. **Recommended problems:** Binary Tree Preorder/Inorder/Postorder Traversal; Maximum Depth of Binary Tree.
7. **Difficulty:** Medium.
8. **Number of problems:** 3-4.
9. **Must explain:** the difference between the three traversal orders and when inorder specifically matters (BST → sorted order, tomorrow's topic); how recursive traversal implicitly uses the call stack the same way Day 23's factorial did.
10. **Common mistakes:** swapping the order of recursive calls vs the "visit" step (mixing up pre/in/post); missing the `None`-node base case (`AttributeError` instead of a clean stop).
11. **Revision:** Days 29 and 28 — "which of these two would you use to do a tree traversal iteratively?" as a forward-looking prediction question.
12. **Estimated time:** ~4h.

### Day 31 — Trees II: Binary Search Trees
1. **Python:** none new.
2. **DSA:** BST ordering invariant; why inorder traversal of a BST yields sorted order (ties directly to Day 30).
3. **Why:** BSTs are the most commonly tested tree variant and connect trees back to binary search (Day 21) — "binary search where the data structure itself is shaped like the search."
4. **Visual:** BST diagram shading the valid region for where a new value can go; insertion animated as a root-to-leaf path.
5. **Exercises:** implement BST insertion and search recursively; trace inserting 5 values into an empty BST by hand first; verify inorder gives sorted output.
6. **Recommended problems:** Insert into a Binary Search Tree; Search in a Binary Search Tree; Validate Binary Search Tree.
7. **Difficulty:** Medium.
8. **Number of problems:** 3.
9. **Must explain:** the BST invariant applies to the *entire* left/right subtree, not just immediate children (a very common beginner misunderstanding — stress-test it directly); why BST ops are O(log n) balanced but O(n) on a degenerate (linked-list-shaped) tree.
10. **Common mistakes:** validating a BST by only checking immediate children instead of the inherited valid-range constraint; not handling insertion into an empty tree/subtree.
11. **Revision:** Day 30.
12. **Estimated time:** ~4h.

### Day 32 — Trees III: height, level order (tree BFS); Block 4 checkpoint
1. **Python:** none new — reuses Day 29's `deque`.
2. **DSA:** height/depth calculation; level-order (BFS) traversal — first fusion of two prior topics (trees + queues).
3. **Why:** level-order traversal is the direct conceptual predecessor to graph BFS (Day 36).
4. **Visual:** the tree shown level by level, each level highlighting together, with a queue panel beside it showing dequeues/enqueues — first time two structural visualizations run side by side.
5. **Exercises:** recursive height/max-depth (revisit Day 30's Maximum Depth through this lens); level-order traversal via `deque`; predict output by hand first.
6. **Recommended problems:** Maximum Depth of Binary Tree (revisited); Binary Tree Level Order Traversal; Minimum Depth of Binary Tree (optional stretch).
7. **Difficulty:** Medium.
8. **Number of problems:** 2-3.
9. **Must explain:** why level-order needs a queue specifically, not a stack (predict what a stack-based version would produce, as contrast); how height is computed bottom-up (`1 + max(left, right)`).
10. **Common mistakes:** forgetting to track level boundaries when output must be grouped by level; using recursion for level-order without a clear reason (works, but misses the point of the queue-based approach).
11. **Revision:** **Block 4 checkpoint** — one recall question per topic across Days 25-31 (linked lists ×3, stacks, queues, trees ×2).
12. **Estimated time:** ~4h.

---

## Block 5 — Days 33-38: Heaps and Graphs

### Day 33 — Heaps I: concept, `heapq`
1. **Python:** `heapq` (`heappush`, `heappop`, `heapify`), `(priority, value)` tuples in a heap.
2. **DSA:** heap/priority-queue structure — partial ordering, not full sorting.
3. **Why:** solves "give me the smallest/largest repeatedly" more efficiently than re-sorting every time; `heapq` is the standard Python tool.
4. **Visual:** binary-tree-shaped heap next to its array representation, showing "bubble up" (push) and "bubble down" (pop) — explicitly contrasted with Day 31's BST (a heap is *not* a BST — a common confusion worth addressing head-on).
5. **Exercises:** push 6 values one at a time, tracing bubble-up by hand; implement "kth smallest element" via heap; compare "find min repeatedly" via heap vs re-sorting each time.
6. **Recommended problems:** Kth Largest Element in a Stream; Last Stone Weight.
7. **Difficulty:** Medium.
8. **Number of problems:** 2.
9. **Must explain:** the heap invariant (parent ≤ both children for a min-heap — *not* left<node<right like a BST); why Python's `heapq` is always a min-heap (negate-values trick for a max-heap); O(log n) push/pop vs O(1) peek.
10. **Common mistakes:** confusing heap ordering with BST ordering (assuming siblings/cousins are ordered — they aren't); forgetting the max-heap negation trick.
11. **Revision:** Day 32 spot check.
12. **Estimated time:** ~3.5h.

### Day 34 — Heaps II: top-K pattern
1. **Python:** none new.
2. **DSA:** top-K via a size-bounded heap (O(n log k) instead of O(n log n)).
3. **Why:** "top K" is an extremely common interview family, and the bounded-heap trick is a genuine, teachable optimization insight.
4. **Visual:** a size-limited heap where each new element competes against the heap's current worst element for a spot.
5. **Exercises:** top-K frequent elements via heap (revisit Day 12's brute-force sort version, compare complexity explicitly); K Closest Points to Origin (simplified distance).
6. **Recommended problems:** Top K Frequent Elements (heap version); K Closest Points to Origin.
7. **Difficulty:** Medium.
8. **Number of problems:** 2.
9. **Must explain:** why bounding the heap to size k gives O(n log k) instead of O(n log n) — compare against Day 12's full-sort approach as a "same problem, three ways, three complexities" exercise.
10. **Common mistakes:** forgetting to pop when the heap exceeds size k (unbounded growth, optimization lost); comparison errors on tuple-typed heap elements.
11. **Revision:** Day 33.
12. **Estimated time:** ~3.5h.

### Day 35 — Graphs I: representation & terminology
1. **Python:** dict-of-lists as adjacency list.
2. **DSA:** vertices/edges, directed vs undirected, weighted vs unweighted, adjacency list vs matrix.
3. **Why:** a tree is just a graph with no cycles — graphs generalize what you already know. This day is pure vocabulary/representation fluency, since most graph bugs trace back to a shaky mental model of the representation itself.
4. **Visual:** a small graph drawn as nodes-and-edges, then shown side-by-side as an adjacency list and matrix, making the equivalence concrete.
5. **Exercises:** build an adjacency list from an edge list (directed and undirected versions); convert list↔matrix by hand for a 4-node example.
6. **Recommended problems:** build a graph from an edge list (implementation exercise); Find if Path Exists in Graph (brute-force reachability OK).
7. **Difficulty:** Easy-Medium.
8. **Number of problems:** 2.
9. **Must explain:** when adjacency list beats adjacency matrix (sparse vs dense, O(V+E) vs O(V²) space); what "directed"/"weighted" change about the representation.
10. **Common mistakes:** forgetting to add the edge both directions for undirected graphs; confusing "neighbors" with "all nodes."
11. **Revision:** Day 34, plus Day 33 spot check.
12. **Estimated time:** ~3.5h.

### Day 36 — Graphs II: BFS
1. **Python:** none new — reuses Day 29's `deque`, Day 32's level-order pattern.
2. **DSA:** graph BFS — shortest path in unweighted graphs, visited-set tracking.
3. **Why:** direct generalization of Day 32's tree level-order to graphs, plus one crucial addition (a visited set, since graphs — unlike trees — can have cycles). Framing it this way should make it feel like a small step.
4. **Visual:** same queue-and-highlighting style as Day 32, now with a "visited" grayed-out overlay, explicitly narrated as "the one new thing trees didn't need."
5. **Exercises:** trace BFS by hand on a small cyclic graph before coding (predict visit order); implement BFS from a start node; find shortest path length in an unweighted graph.
6. **Recommended problems:** Number of Islands (BFS version — grid-as-graph, a very common framing); Shortest Path in Binary Matrix.
7. **Difficulty:** Medium.
8. **Number of problems:** 2.
9. **Must explain:** why BFS explores level-by-level (guaranteeing shortest path in unweighted graphs); why the visited set is mandatory here but wasn't for tree BFS; how a 2D grid maps to graph vocabulary (cell = node, adjacency = edge).
10. **Common mistakes:** forgetting the visited set (infinite loop on cycles), or marking visited at dequeue time instead of enqueue time (causes duplicate enqueues); missing grid-boundary checks before visiting a neighbor.
11. **Revision:** Day 35 — "redraw yesterday's graph and predict BFS order."
12. **Estimated time:** ~4h.

### Day 37 — Graphs III: DFS
1. **Python:** none new.
2. **DSA:** graph DFS — recursive vs explicit-stack iterative, connected components.
3. **Why:** BFS's natural counterpart, often the more intuitive starting point for connected components and cycle detection; teaching both versions reinforces Day 23's call-stack lesson with an explicit stack achieving the same thing.
4. **Visual:** the same graph as Day 36, explored depth-first — one path plunging deep before backtracking, shown directly against yesterday's level-by-level spread on the identical graph.
5. **Exercises:** trace DFS by hand on the same graph used for yesterday's BFS trace and compare visit orders; implement DFS recursively; implement DFS iteratively with an explicit stack.
6. **Recommended problems:** Number of Islands (DFS version — same problem, different technique, explicit compare/contrast); Connected Components count (or Clone Graph as optional stretch).
7. **Difficulty:** Medium.
8. **Number of problems:** 2.
9. **Must explain:** recursive DFS's implicit call-stack use vs the iterative version's explicit stack (tie back to Days 23 and 28); why BFS and DFS give different visit orders on the same graph but both correctly visit every reachable node.
10. **Common mistakes:** missing the visited check in recursive DFS (infinite recursion/stack overflow on cycles); marking visited after the recursive call instead of before.
11. **Revision:** Day 36 — direct BFS-vs-DFS compare/contrast on the same example graph.
12. **Estimated time:** ~4h.

### Day 38 — Shortest paths: Dijkstra; Block 5 checkpoint
1. **Python:** none new — reuses `heapq` from Day 33.
2. **DSA:** weighted shortest-path problem; why plain BFS fails on weighted graphs; Dijkstra's greedy + heap approach.
3. **Why:** the natural capstone combining graphs (35-37), heaps (33-34), and BFS's level-by-level intuition (36): "BFS, but a priority queue replaces the plain queue because edges now cost different amounts."
4. **Visual:** same graph-exploration visual as BFS/DFS, edges now labeled with weights, with a running "shortest distance so far" table updating as the heap pops the next-closest node each step.
5. **Exercises:** trace Dijkstra by hand on a small (5-node) weighted graph before coding; implement it with `heapq`; construct an example where plain BFS gives the wrong answer on a weighted graph.
6. **Recommended problems:** Network Delay Time; Path With Minimum Effort (optional stretch, simplified).
7. **Difficulty:** Medium-Hard (hardest single day so far — budget extra time; full fluency by the revision days is fine).
8. **Number of problems:** 1-2.
9. **Must explain:** why BFS's level-guarantee breaks with weighted edges; why the heap always expands the currently-closest unvisited node next (the greedy property); why a node's distance, once popped, is final (assuming non-negative weights).
10. **Common mistakes:** using a plain queue instead of a heap (silently *wrong*, not crashing — a dangerous, quiet bug worth deliberately stress-testing); not skipping a node popped with a stale (already-improved) distance.
11. **Revision:** **Block 5 checkpoint** — one recall question per topic across Days 33-37 (heaps ×2, graph representation, BFS, DFS).
12. **Estimated time:** ~4-4.5h.

---

## Block 6 — Days 39-42: Intro Dynamic Programming

### Day 39 — DP I: overlapping subproblems, memoization vs tabulation
1. **Python:** `functools.lru_cache` (after building a memo dict by hand first — order matters).
2. **DSA:** what gives a problem "DP structure" (overlapping subproblems + optimal substructure); top-down vs bottom-up.
3. **Why:** the payoff for Day 23's "naive recursive Fibonacci is slow" cliffhanger — DP is "recursion, but remember answers you've already computed," an extension of something already understood, not a new alien topic.
4. **Visual:** the exact Day 23 Fibonacci recursion tree, now with repeated subtrees grayed out once memoized (visually showing how much redundant work memoization removes), alongside a simple 1D table filling left-to-right for tabulation.
5. **Exercises:** implement naive recursive Fibonacci and time it at n=30 (feel the slowness); add a manual memo dict and re-time it; rewrite bottom-up as tabulation; finally show `@lru_cache` as the real-code shortcut.
6. **Recommended problems:** Fibonacci Number (naive, memoized, and tabulated versions); Climbing Stairs.
7. **Difficulty:** Medium.
8. **Number of problems:** 2 (each solved 2-3 ways).
9. **Must explain:** why naive Fibonacci is O(2ⁿ) (tie to Days 23-24's branching recursion tree); why memoization brings it to O(n); the mechanical difference between top-down (recursion+cache) and bottom-up (iterative fill).
10. **Common mistakes:** memoizing with a mutable default argument (classic Python gotcha) instead of an explicit dict/decorator; off-by-one in tabulation array sizing (need n+1 slots, not n).
11. **Revision:** Day 38, plus Days 23-24 explicitly resurfaced as required prerequisite review.
12. **Estimated time:** ~4h.

### Day 40 — DP II: 1D DP (decision at each step)
1. **Python:** none new.
2. **DSA:** 1D DP where each state depends on a small, fixed number of previous states.
3. **Why:** House Robber's `dp[i] = max(dp[i-1], dp[i-2] + val)`-style recurrence is simple but generalizes to a large family of interview questions.
4. **Visual:** a 1D table filling left to right, arrows from `dp[i-1]`/`dp[i-2]` into `dp[i]` at each step.
5. **Exercises:** write the recurrence in plain English *before* coding (required, not optional); implement House Robber bottom-up; implement Climbing Stairs variants with different step sizes.
6. **Recommended problems:** House Robber; Min Cost Climbing Stairs.
7. **Difficulty:** Medium.
8. **Number of problems:** 2.
9. **Must explain:** how to derive a recurrence from a plain-language problem description (the real transferable skill); why this can't be solved greedily (construct a counterexample where greedy fails).
10. **Common mistakes:** writing code before stating the recurrence in words (skips the transferable-skill step); off-by-one on base cases `dp[0]`/`dp[1]`.
11. **Revision:** Day 39.
12. **Estimated time:** ~4h.

### Day 41 — DP III: coin change, LIS intro
1. **Python:** none new.
2. **DSA:** minimization DP (coin change) and sequence DP (LIS, O(n²) version only).
3. **Why:** coin change introduces "try every choice at this step, take the best" (richer than Day 40's fixed lookback); LIS is one of the most iconic DP interview questions — taught here only in its O(n²) form (the O(n log n) optimization is explicitly deferred, not needed for a strong baseline).
4. **Visual:** for coin change, a table showing which previous cells were checked across denominations before taking the min; for LIS, arrows showing which earlier "increasing" elements each position could extend from.
5. **Exercises:** state each recurrence in plain English first; implement coin change (minimum coins) bottom-up; implement LIS in O(n²).
6. **Recommended problems:** Coin Change (minimum coins); Longest Increasing Subsequence (O(n²)).
7. **Difficulty:** Medium.
8. **Number of problems:** 2.
9. **Must explain:** why coin change tries every denomination at each amount instead of a fixed lookback; why LIS's O(n²) checks every earlier index for each position (and, at a high level only, that a faster approach exists but is out of scope now).
10. **Common mistakes:** not initializing unreachable amounts to infinity/sentinel before taking a min; off-by-one in LIS's inner loop bounds.
11. **Revision:** Day 40.
12. **Estimated time:** ~4h.

### Day 42 — DP IV: 2D DP intro; Block 6 checkpoint
1. **Python:** none new.
2. **DSA:** 2D DP (state depends on two dimensions — grid position, or item-index + remaining capacity).
3. **Why:** the final new concept of the core curriculum — a natural extension of this whole block. Stopping here (rather than pushing into harder DP) respects depth-over-breadth for a 45-day beginner timeline.
4. **Visual:** a 2D grid table filling in reading order, arrows from the cell(s) above/left it depends on — generalizing Days 40-41's 1D visual to two dimensions.
5. **Exercises:** state the 2D recurrence in plain English first; implement Unique Paths bottom-up; implement basic 0/1 Knapsack if time allows.
6. **Recommended problems:** Unique Paths (required); 0/1 Knapsack basic version (optional if time-constrained).
7. **Difficulty:** Medium-Hard.
8. **Number of problems:** 1-2.
9. **Must explain:** how a 2D table cell depends on specific neighbors (above/left, or include/exclude for knapsack); that a 2D table can often be compressed to 1D as a space optimization (concept only — implementing it is optional stretch).
10. **Common mistakes:** incorrect first-row/first-column base-case initialization; in knapsack, iterating items/capacity in the wrong order and accidentally allowing item reuse (0/1 vs unbounded confusion).
11. **Revision:** **Block 6 checkpoint** — all of Days 39-41, plus a look back across the recursion→DP throughline (Day 23 → Day 39 → today).
12. **Estimated time:** ~4h.

---

## Block 7 — Days 43-50: Revision & Mock Interviews

**Rewritten for the 45→50 day expansion.** The original plan's Block 7 was 3 days (43-45: one revision day, one double mock-interview day, one final mock+wrapup day). The approved expansion stretches the same idea across 8 days, with two changes worth naming explicitly: (1) there is no "Mock Interview Mode" feature in the shipped product — every "mock interview" below means *using the existing Problem Workspace yourself*, under a self-set timer, with hints deliberately not opened until time is up, exactly like any other problem attempt; and (2) Days 44-49 each now point to a **specific, curated set of recommended problems** (pulled from the Extended/Advanced pool, `path_tier` unchanged, so none of them count toward or are required for Core Path completion) rather than only a vague "pick something" — chosen so the new Hard/Complex-difficulty problems from the 150-problem expansion land specifically here, where deliberate exposure to hard material under support makes sense, instead of being scattered arbitrarily across the plan.

### Day 43 — Full revision day
1. **Python:** none new.
2. **DSA:** none new — entirely revision, driven by the app's tracked weak topics rather than a fixed list.
3. **Why:** skills fade without deliberate revisit — a full sweep before the mock-interview days that follow.
4. **Visual:** whichever visualizations correspond to your specific weak topics.
5. **Exercises:** re-solve one problem from each of the 6 block checkpoints (Days 7, 16, 24, 32, 38, 42) from scratch, prioritizing your weakest topics per the dashboard.
6. **Recommended problems:** none new — this day revisits Days 1-42's own checkpoint problems, not new material.
7. **Difficulty:** Mixed Easy-Medium, matched to weak areas.
8. **Number of problems:** 6 (one per checkpoint).
9. **Must explain:** for each revised topic, restate the core pattern/recurrence/invariant from memory.
10. **Common mistakes:** whatever your tracker shows most frequently — treated as the day's content.
11. **Revision:** the entire 42-day curriculum, filtered to weak topics.
12. **Estimated time:** ~4h.

### Day 44 — Mock interviews 1 and 2
1. **Python:** none new.
2. **DSA:** none new — interview conditions (self-set timer, no hints during the attempt).
3. **Why:** solving under a clock while narrating your thinking is a different skill from solving alone.
4. **Visual:** the Problem Workspace, used deliberately under real-interview conditions — pick a problem you haven't solved, start your own timer, don't open hints until time is up.
5. **Exercises:** two full mock interviews (30-45 min each) using the Problem Workspace under self-imposed interview conditions, followed by an honest post-interview review each time.
6. **Recommended problems:** a curated menu of 3 to pick two from — **Meeting Rooms II** (Medium, heaps) and **Gas Station** (Medium, greedy) as realistic single-session interview problems, plus **LRU Cache** (Hard, hashing/design) as a stretch option for a second, tougher session. Pick your own from the Problem Bank instead if you'd rather.
7. **Difficulty:** Medium, with one Hard option.
8. **Number of problems:** 2 attempted, from a menu of 3.
9. **Must explain:** a full walkthrough of your approach after each interview, as if speaking to an interviewer.
10. **Common mistakes:** whatever the post-interview review surfaces.
11. **Revision:** none scheduled — this day is itself the revision mechanism for everything prior.
12. **Estimated time:** ~4h.

### Day 45 — Mixed-problem interview practice
1. **Python:** none new.
2. **DSA:** none new — pattern recognition without a topic label as a hint.
3. **Why:** real interviews don't announce the topic in advance — practicing on a mixed, unlabeled set builds actual pattern-recognition speed, not just topic recall.
4. **Visual:** the Problem Bank's Difficulty sort view, used to pick problems without leaning on the Topic column as a hint.
5. **Exercises:** pick 3-4 problems spanning different topics and solve each under a self-set timer, narrating your approach before writing code.
6. **Recommended problems:** a curated menu spanning four different topics — **Rotate Image** (Medium, arrays/grid), **Word Search** (Medium, recursion/backtracking), **Remove K Digits** (Medium, stacks), **Course Schedule II** (Medium, graphs). Pick 3-4 of these, or substitute your own mixed set from the Problem Bank.
7. **Difficulty:** Medium.
8. **Number of problems:** 3-4.
9. **Must explain:** for each problem, the moment you recognized which pattern applied and what tipped you off.
10. **Common mistakes:** choosing problems from one familiar topic instead of genuinely mixing categories.
11. **Revision:** none scheduled.
12. **Estimated time:** ~3.5h.

### Day 46 — Weak-area revision
1. **Python:** none new.
2. **DSA:** none new — targeted revision driven by tracked weak topics.
3. **Why:** a second, more targeted revision pass — Day 43 covered everything broadly; this goes deep specifically on whatever the dashboard shows as weakest after two mock interviews' worth of fresh data.
4. **Visual:** the dashboard's per-topic accuracy/attempt breakdown, sorted worst-first.
5. **Exercises:** re-solve 2-3 problems from your single weakest topic from scratch, unassisted first, hints if stuck, then a second unassisted problem on the same topic to confirm it actually transferred.
6. **Recommended problems:** three fresh-material options in case your weak topic matches one — **Decode Ways** (Medium, DP), **Binary Search Tree Iterator** (Medium, trees), **Non-overlapping Intervals** (Medium, arrays). Otherwise, pick from your own weak topic in the Problem Bank.
7. **Difficulty:** Medium.
8. **Number of problems:** 2-3.
9. **Must explain:** the specific pattern/recurrence/invariant for your weakest topic, restated from memory, plus what specifically went wrong earlier.
10. **Common mistakes:** re-solving a problem you already know well instead of genuinely targeting the weak topic; skipping the confirming second problem.
11. **Revision:** Days 1-45, filtered to your single weakest topic.
12. **Estimated time:** ~3h.

### Day 47 — Advanced and Complex problem practice
1. **Python:** none new.
2. **DSA:** none new — deliberate exposure to Hard/Complex-tier problems.
3. **Why:** the Complex difficulty tier and the Advanced tier's Hard problems are optional by design, but for anyone aiming past entry-level interviews, deliberate practice on genuinely hard problems now, with full support available, beats encountering one cold in a real interview. This is the plan's intended home for the 150-problem expansion's Hard/Complex material.
4. **Visual:** the Problem Bank filtered to the Advanced tier, sorted by Difficulty (Hard, then Complex).
5. **Exercises:** attempt 2 Hard or Complex problems, ideally outside your strongest topic. Full hint ladder and reveal-solution are both fair game — today's goal is exposure, not solving unaided.
6. **Recommended problems:** a curated menu of 6, spanning 6 different topics — **Trapping Rain Water II** (Complex, arrays), **Split Array Largest Sum** (Complex, binary search), **Regular Expression Matching** (Complex, DP), **Alien Dictionary** (Complex, graphs), **Binary Tree Cameras** (Complex, trees), **Largest Rectangle in Histogram** (Hard, stacks). Pick 2, ideally outside your strongest topic.
7. **Difficulty:** Hard/Complex.
8. **Number of problems:** 2, from a menu of 6.
9. **Must explain:** what made each problem hard specifically, and what would help you recognize it faster next time.
10. **Common mistakes:** treating a Complex problem as only "counting" if solved unaided — for this optional advanced practice, using hints and the reference solution to actually learn the technique is the intended use.
11. **Revision:** none scheduled.
12. **Estimated time:** ~3.5h.

### Day 48 — Mock interview 4
1. **Python:** none new.
2. **DSA:** none new — interview conditions, incorporating recent weak-area and advanced practice.
3. **Why:** a fourth timed mock interview, now incorporating everything the weak-area and advanced-practice days surfaced.
4. **Visual:** the same self-timed Problem Workspace setup as Days 44-45.
5. **Exercises:** one full mock interview (Medium-Hard) under a strict self-set timer (35-45 min), followed by the same honest post-interview review as previous mock interviews.
6. **Recommended problems:** two Medium-Hard options — **Candy** (Hard, greedy) or **Basic Calculator** (Hard, strings). Pick one, or substitute your own.
7. **Difficulty:** Medium-Hard.
8. **Number of problems:** 1, from a menu of 2.
9. **Must explain:** a full spoken-style walkthrough of your approach, including the parts that didn't go smoothly.
10. **Common mistakes:** skipping the post-interview review because the interview itself felt fine.
11. **Revision:** none scheduled.
12. **Estimated time:** ~3h.

### Day 49 — Full-length final interview simulation
1. **Python:** none new.
2. **DSA:** none new — a full back-to-back interview loop simulation.
3. **Why:** the closest approximation this curriculum can offer to a real interview loop: two back-to-back timed problems with no break, no hints, and no reference solution until both are fully attempted.
4. **Visual:** the same Problem Workspace setup, run twice in immediate succession.
5. **Exercises:** two consecutive mock interviews (30-40 min each, back to back, no break), covering two different topics chosen without looking ahead. No hints, no solution reveal until BOTH are attempted — then review both together.
6. **Recommended problems:** a curated menu of 4 Complex-tier problems spanning 4 topics for the two slots — **Maximal Rectangle** (stacks), **Text Justification** (strings), **Constrained Subsequence Sum** (queues), **Course Schedule III** (greedy). Pick any two from different topics.
7. **Difficulty:** Complex.
8. **Number of problems:** 2, from a menu of 4.
9. **Must explain:** for each of the two problems, your approach, its correctness, and its time/space complexity, stated the way you would out loud in a real interview.
10. **Common mistakes:** taking a break between the two problems, or peeking at hints mid-attempt.
11. **Revision:** none scheduled.
12. **Estimated time:** ~4h.

### Day 50 — Final review and wrap-up
1. **Python:** none new.
2. **DSA:** none new.
3. **Why:** one final, honest, data-backed look back at the full curriculum before moving on to independent practice.
4. **Visual:** the dashboard's final view — problems solved, independent-solve rate, topics mastered vs weak, across the entire 50-day path.
5. **Exercises:** write a short self-assessment — your 3 strongest topics and 2-3 to keep practicing, checked against the dashboard's actual data — then set a concrete post-Day-50 practice plan (e.g. 2 problems/week from your weakest topics, revisited monthly).
6. **Recommended problems:** none new — this day is assessment and planning, not new problems.
7. **Difficulty:** n/a.
8. **Number of problems:** 0.
9. **Must explain:** an honest, data-backed self-assessment, and a concrete, specific post-Day-50 practice plan.
10. **Common mistakes:** a vague plan ("keep practicing") instead of a specific, schedulable one; self-assessing from memory/feeling alone instead of checking the dashboard.
11. **Revision:** none scheduled — Day 50 is the terminal review.
12. **Estimated time:** ~3h.

---

## Coverage summary

Python fundamentals (Days 1-7) → arrays/strings/hashing/two pointers/sliding window (8-16) → sorting/binary search/recursion (17-24) → linked lists/stacks/queues/trees (25-32) → heaps/graphs/BFS/DFS/Dijkstra (33-38) → intro DP, 1D and 2D (39-42) → revision, mock interviews, weak-area/advanced practice, and a final simulation (43-50). Greedy is taught as a cross-curriculum concept lesson rather than its own block (see the Greedy note above) — its problem pool spans Easy through Complex.

Deliberately excluded, matching the original 45-day scope and unchanged by the 50-day expansion: advanced DP (bitmask, digit DP, DP-on-trees), segment trees/Fenwick trees, tries, union-find/DSU, advanced graph algorithms (Bellman-Ford, Floyd-Warshall, MST, topological sort beyond a brief DFS-based mention if it comes up naturally in Day 37), and bit manipulation beyond what a couple of problems touch incidentally. These remain excellent *next* topics after Day 50, not before it — the additional 5 days and 41 problems went toward deeper practice and a genuine Complex difficulty tier within the existing 16 topics, not toward these excluded structures.
