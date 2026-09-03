"""
Approved 150-problem expansion (Codeloupe, Sept 2026) -- adds exactly 41
new problems on top of the original 109 in seed_problems.py, to close
category x difficulty coverage gaps (a genuine Hard problem in every
topic, a genuine Complex problem in every topic, and a brand-new
'greedy' topic covering Easy/Medium/Hard/Complex) plus 15 high-value
discretionary picks. See deliverables/EXPANSION_PLAN.md for the full
rationale and coverage matrix this file was derived from.

Kept as a separate module (NEW_PROBLEMS, imported and concatenated onto
PROBLEMS at the bottom of seed_problems.py) rather than hand-merged into
that file, so this specific addition stays independently reviewable and
diffable.

Every reference solution here is verified the same way as the original
109 -- init_db.py's _seed_problems() runs each one against its own
test_inputs at seed time and stores whatever it actually returns as the
expected output, so a wrong reference solution cannot silently ship.
"""

NEW_PROBLEMS = [

    # ---------------------------------------------------------------
    # Mandatory: Hard problem for the 7 topics that had none.
    # ---------------------------------------------------------------

    dict(
        slug="lru-cache",
        title="LRU Cache",
        day=44,
        topic="hashing",
        pattern="hashmap + ordered eviction",
        difficulty="Hard",
        interview_priority="Core",
        estimated_solve_minutes=30,
        progression_stage="variation",
        canonical_reference="LeetCode 146: LRU Cache",
        path_tier="advanced",
        description=(
            "Design a fixed-capacity Least Recently Used (LRU) cache. `get(key)` returns the value for "
            "`key` (or -1 if absent) and marks it as most-recently-used; `put(key, value)` inserts or "
            "updates a key (also marking it most-recently-used) and, if this pushes the cache over "
            "capacity, evicts the least-recently-used key. Both operations must run in O(1). This "
            "exercise checks a scripted sequence of operations end to end -- the first op is always "
            "`'LRUCache'` with `[capacity]` as its args."
        ),
        constraints="1 <= capacity <= 3000; at most 2*10^4 total calls to get/put.",
        function_signature="def lru_cache_ops(ops, args):",
        starter_code=(
            "class LRUCache:\n"
            "    def __init__(self, capacity):\n"
            "        from collections import OrderedDict\n"
            "        self.capacity = capacity\n"
            "        self.data = OrderedDict()\n"
            "\n"
            "    def get(self, key):\n"
            "        # Miss -> -1. Hit -> mark key as most-recently-used, then return its value.\n"
            "        pass\n"
            "\n"
            "    def put(self, key, value):\n"
            "        # Insert/update, mark most-recently-used, then evict the LRU key if over capacity.\n"
            "        pass\n"
            "\n"
            "\n"
            "def lru_cache_ops(ops, args):\n"
            "    cache = None\n"
            "    results = []\n"
            "    for op, arg in zip(ops, args):\n"
            "        if op == 'LRUCache':\n"
            "            cache = LRUCache(arg[0])\n"
            "            results.append(None)\n"
            "        elif op == 'get':\n"
            "            results.append(cache.get(arg[0]))\n"
            "        else:\n"
            "            cache.put(arg[0], arg[1])\n"
            "            results.append(None)\n"
            "    return results\n"
        ),
        expected_time_complexity="O(1) per get/put",
        expected_space_complexity="O(capacity)",
        brute_force_approach="A plain dict tracks values in O(1), but has no notion of recency -- finding the least-recently-used key to evict would require an O(n) scan of every access, unless recency is tracked separately.",
        optimal_approach="An OrderedDict (or a hashmap + doubly linked list, which is what OrderedDict does internally) lets you both look up a key in O(1) AND move it to the 'most recent' end in O(1). On put, if over capacity, popitem(last=False) evicts the least-recently-used (front) entry in O(1).",
        common_mistakes="Forgetting that get() ALSO counts as a use and must refresh recency, not just put(); evicting on every put() unconditionally instead of only when actually over capacity; using a plain dict and an O(n) scan to find the LRU key (technically correct, but violates the O(1) requirement this problem is specifically testing).",
        edge_cases="capacity == 1 (every put evicts the previous key); updating an existing key's value (must not count as inserting a new one for eviction purposes); get() on a key that was already evicted.",
        test_inputs=[
            (["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"],
             [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]),
            (["LRUCache", "put", "get", "put", "get", "get"],
             [[1], [1, 10], [1], [2, 20], [1], [2]]),
            (["LRUCache", "put", "put", "put", "get", "get"],
             [[2], [1, 1], [2, 2], [3, 3], [1], [2]]),
        ],
        test_labels=[None, "capacity of 1 (every put evicts the previous key)", "put beyond capacity evicts the true LRU key, not just the oldest-inserted one"],
        reference_solution=(
            "class LRUCache:\n"
            "    def __init__(self, capacity):\n"
            "        from collections import OrderedDict\n"
            "        self.capacity = capacity\n"
            "        self.data = OrderedDict()\n"
            "\n"
            "    def get(self, key):\n"
            "        if key not in self.data:\n"
            "            return -1\n"
            "        self.data.move_to_end(key)\n"
            "        return self.data[key]\n"
            "\n"
            "    def put(self, key, value):\n"
            "        if key in self.data:\n"
            "            self.data.move_to_end(key)\n"
            "        self.data[key] = value\n"
            "        if len(self.data) > self.capacity:\n"
            "            self.data.popitem(last=False)\n"
            "\n"
            "\n"
            "def lru_cache_ops(ops, args):\n"
            "    cache = None\n"
            "    results = []\n"
            "    for op, arg in zip(ops, args):\n"
            "        if op == 'LRUCache':\n"
            "            cache = LRUCache(arg[0])\n"
            "            results.append(None)\n"
            "        elif op == 'get':\n"
            "            results.append(cache.get(arg[0]))\n"
            "        else:\n"
            "            cache.put(arg[0], arg[1])\n"
            "            results.append(None)\n"
            "    return results\n"
        ),
        hints=[
            "You need O(1) lookup (a hashmap) AND an O(1) way to know which key was used longest ago. Neither one alone is enough -- you need both working together.",
            "Python's OrderedDict gives you both for free: move_to_end(key) shifts a key to the 'most recent' end in O(1), and popitem(last=False) pops the 'least recent' end in O(1).",
            "get: if key not in data, return -1; else move_to_end(key) and return data[key]. put: if key in data, move_to_end(key); set data[key]=value; if len(data) > capacity, popitem(last=False).",
        ],
    ),

    dict(
        slug="reverse-nodes-k-group",
        title="Reverse Nodes in k-Group",
        day=None,
        topic="linked-lists",
        pattern="in-place reversal by segment",
        difficulty="Hard",
        interview_priority="Important",
        estimated_solve_minutes=30,
        progression_stage="variation",
        canonical_reference="LeetCode 25: Reverse Nodes in k-Group",
        path_tier="advanced",
        description=(
            "Given a linked list (as `values`) and an integer `k`, reverse the nodes of the list `k` at a "
            "time and return the resulting list. If the number of remaining nodes is fewer than `k`, leave "
            "that final group as-is (unreversed). You may not just reorder the `values`; the reference "
            "solution must actually rewire node pointers."
        ),
        constraints="1 <= len(values) <= 5000; 1 <= k <= len(values).",
        function_signature="def reverse_nodes_k_group(values, k):",
        starter_code=(
            "class Node:\n"
            "    def __init__(self, val):\n"
            "        self.val = val\n"
            "        self.next = None\n"
            "\n"
            "def build_list(values):\n"
            "    head = None\n"
            "    for v in reversed(values):\n"
            "        node = Node(v)\n"
            "        node.next = head\n"
            "        head = node\n"
            "    return head\n"
            "\n"
            "def to_list(head):\n"
            "    result = []\n"
            "    while head:\n"
            "        result.append(head.val)\n"
            "        head = head.next\n"
            "    return result\n"
            "\n"
            "def reverse_nodes_k_group(values, k):\n"
            "    head = build_list(values)\n"
            "    # For each group of k nodes: first check there ARE k more nodes left\n"
            "    # (otherwise leave the tail alone), then reverse just that segment's\n"
            "    # internal pointers and splice it back into the list.\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(1) extra (excluding the list itself)",
        brute_force_approach="Convert to a plain list, reverse each k-sized chunk with slicing, rebuild the linked list from scratch -- correct, but sidesteps the actual pointer-rewiring skill this problem is testing.",
        optimal_approach="Use a dummy node before head. For each group: walk forward k nodes to find the group's end (if fewer than k remain, stop and leave the rest untouched). Reverse the internal next pointers of just that segment, then reconnect the previous group's tail to the new head of this segment, and this segment's new tail to whatever comes next.",
        common_mistakes="Losing the link to the node after the group before reversing (must be saved first); reversing a final partial group that has fewer than k nodes (must be left in original order); off-by-one when checking whether k more nodes actually exist before committing to a reversal.",
        edge_cases="k == 1 (no-op, list unchanged); k == len(values) (the whole list reverses as one group); a list whose length isn't a multiple of k (final group stays unreversed).",
        test_inputs=[([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4, 5], 3), ([1, 2], 1), ([1], 1), ([1, 2, 3, 4, 5, 6], 6)],
        test_labels=[None, None, "k=1 (no-op)", "single node", "k equals the full length (whole list reverses as one group)"],
        reference_solution=(
            "class Node:\n"
            "    def __init__(self, val):\n"
            "        self.val = val\n"
            "        self.next = None\n"
            "\n"
            "def build_list(values):\n"
            "    head = None\n"
            "    for v in reversed(values):\n"
            "        node = Node(v)\n"
            "        node.next = head\n"
            "        head = node\n"
            "    return head\n"
            "\n"
            "def to_list(head):\n"
            "    result = []\n"
            "    while head:\n"
            "        result.append(head.val)\n"
            "        head = head.next\n"
            "    return result\n"
            "\n"
            "def reverse_nodes_k_group(values, k):\n"
            "    head = build_list(values)\n"
            "\n"
            "    def get_kth(node, k):\n"
            "        while node and k > 0:\n"
            "            node = node.next\n"
            "            k -= 1\n"
            "        return node\n"
            "\n"
            "    dummy = Node(0)\n"
            "    dummy.next = head\n"
            "    group_prev = dummy\n"
            "    while True:\n"
            "        kth = get_kth(group_prev, k)\n"
            "        if not kth:\n"
            "            break\n"
            "        group_next = kth.next\n"
            "        prev, curr = group_next, group_prev.next\n"
            "        while curr != group_next:\n"
            "            nxt = curr.next\n"
            "            curr.next = prev\n"
            "            prev = curr\n"
            "            curr = nxt\n"
            "        tmp = group_prev.next\n"
            "        group_prev.next = kth\n"
            "        group_prev = tmp\n"
            "    return to_list(dummy.next)\n"
        ),
        hints=[
            "Handle one group of k nodes at a time. For each group, first walk forward to check there really are k more nodes -- if not, stop and leave the rest of the list exactly as it is.",
            "Reversing a group is the same three-pointer technique as reversing a whole list, just bounded to that segment -- the tricky part is reconnecting the group BEFORE it to the new head of the reversed segment, and the reversed segment's new tail to whatever comes after.",
            "Use a dummy node before head, and a group_prev pointer. get_kth(group_prev, k) finds the group's last node (or None if short). Reverse group_prev.next..kth in place, then set group_prev.next to kth (the new head) and continue with group_prev = the old group_prev.next (now the new tail).",
        ],
    ),

    dict(
        slug="shortest-subarray-sum-at-least-k",
        title="Shortest Subarray with Sum at Least K",
        day=None,
        topic="queues",
        pattern="monotonic deque over prefix sums",
        difficulty="Hard",
        interview_priority="Optional",
        estimated_solve_minutes=30,
        progression_stage="variation",
        canonical_reference="LeetCode 862: Shortest Subarray with Sum at Least K",
        path_tier="advanced",
        description=(
            "Given an integer array `nums` (values may be negative) and an integer `k`, return the length "
            "of the shortest contiguous subarray whose sum is >= k, or -1 if no such subarray exists."
        ),
        constraints="1 <= len(nums) <= 10^5; -10^5 <= nums[i] <= 10^5; 1 <= k <= 10^9.",
        function_signature="def shortest_subarray(nums, k):",
        starter_code=(
            "from collections import deque\n"
            "\n"
            "def shortest_subarray(nums, k):\n"
            "    # Because values can be NEGATIVE, the sliding-window-with-two-pointers\n"
            "    # trick from Minimum Size Subarray Sum doesn't work here (growing the\n"
            "    # window doesn't monotonically increase the sum). Instead: build a\n"
            "    # prefix-sum array, then use a monotonic (increasing) deque of prefix\n"
            "    # indices so you can always compare the current prefix against the\n"
            "    # smallest usable earlier one in O(1) amortized.\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(n)",
        brute_force_approach="Check every subarray's sum directly (or via prefix sums with a nested loop) -- O(n^2).",
        optimal_approach="Build prefix sums (prefix[0]=0). Maintain a deque of indices with strictly increasing prefix values. For each new index i: while the front of the deque gives a sum >= k, record the length and pop it (it can never help a LATER i, since i only grows and shrinking the window from the front is always at least as good); then, before pushing i, pop any back entries whose prefix >= prefix[i] (they're strictly worse than i as a future left boundary, since i is both later AND has a smaller-or-equal prefix).",
        common_mistakes="Trying to reuse the non-negative sliding-window two-pointer trick (it silently gives wrong answers once negative numbers are allowed, since the window sum is no longer monotonic as it grows); forgetting the deque holds INDICES, not prefix values, so you can compute the subarray length as i - popped_index.",
        edge_cases="No subarray reaches k (return -1); the single best answer is the entire array; negative numbers that make a longer window sum smaller than a shorter one starting later.",
        test_inputs=[([1], 1), ([1, 2], 4), ([2, -1, 2], 3), ([84, -37, 32, 40, 95], 167), ([-28, 81, -20, 28, -29], 89)],
        test_labels=[None, None, None, "requires skipping past a negative dip to find the true shortest window", "negative numbers throughout"],
        reference_solution=(
            "from collections import deque\n"
            "\n"
            "def shortest_subarray(nums, k):\n"
            "    n = len(nums)\n"
            "    prefix = [0] * (n + 1)\n"
            "    for i in range(n):\n"
            "        prefix[i + 1] = prefix[i] + nums[i]\n"
            "    dq = deque()\n"
            "    best = n + 1\n"
            "    for i in range(n + 1):\n"
            "        while dq and prefix[i] - prefix[dq[0]] >= k:\n"
            "            best = min(best, i - dq.popleft())\n"
            "        while dq and prefix[i] <= prefix[dq[-1]]:\n"
            "            dq.pop()\n"
            "        dq.append(i)\n"
            "    return best if best <= n else -1\n"
        ),
        hints=[
            "Negative numbers break the usual grow/shrink two-pointer window (a bigger window no longer means a bigger sum), so reach for prefix sums instead: subarray(i,j] sums to prefix[j] - prefix[i].",
            "Keep a deque of candidate LEFT boundaries (indices into prefix) with strictly increasing prefix values. If the current prefix minus the deque's front is already >= k, that front index can never do better later (the window can only get wider from here) -- record the length and pop it. Separately, any earlier index with a prefix >= the current one is now strictly worse than the current index as a future left boundary, so pop those from the back before pushing.",
            "prefix[0]=0, prefix[i+1]=prefix[i]+nums[i]. For i in range(n+1): while dq and prefix[i]-prefix[dq[0]]>=k: best=min(best, i-dq.popleft()). while dq and prefix[i]<=prefix[dq[-1]]: dq.pop(). dq.append(i). Return best if found else -1.",
        ],
    ),

    dict(
        slug="count-smaller-after-self",
        title="Count of Smaller Numbers After Self",
        day=None,
        topic="sorting",
        pattern="modified merge sort with index tracking",
        difficulty="Hard",
        interview_priority="Optional",
        estimated_solve_minutes=30,
        progression_stage="variation",
        canonical_reference="LeetCode 315: Count of Smaller Numbers After Self",
        path_tier="advanced",
        description=(
            "Given an integer array `nums`, return an array `counts` where `counts[i]` is the number of "
            "elements to the RIGHT of index i that are strictly smaller than `nums[i]`."
        ),
        constraints="1 <= len(nums) <= 10^5; -10^4 <= nums[i] <= 10^4.",
        function_signature="def count_smaller(nums):",
        starter_code=(
            "def count_smaller(nums):\n"
            "    # A standard merge sort already counts 'how many elements from the\n"
            "    # right half got placed before this left-half element' as a side\n"
            "    # effect of merging -- that count IS the answer for that element,\n"
            "    # as long as you track original indices through the sort so the\n"
            "    # counts land back on the right positions.\n"
            "    n = len(nums)\n"
            "    counts = [0] * n\n"
            "    indices = list(range(n))\n"
            "    pass\n"
            "    return counts\n"
        ),
        expected_time_complexity="O(n log n)",
        expected_space_complexity="O(n)",
        brute_force_approach="For each index, scan every index to its right and count smaller values -- O(n^2), too slow for n up to 10^5.",
        optimal_approach="Merge sort an array of INDICES (not values) by their nums[] values. During each merge step, whenever an element from the right half is placed before an element from the left half still waiting, that's proof every element still waiting in the left half is greater than it -- credit each left-half element, when it's finally placed, with however many right-half elements were already placed ahead of it.",
        common_mistakes="Sorting the values directly and losing track of which original index each count belongs to (must sort/merge an index array, writing results back to counts[original_index]); forgetting counts accumulate ACROSS multiple merge levels, so it must be a running += not an overwrite.",
        edge_cases="Already sorted ascending (every count is 0); sorted descending (counts are n-1, n-2, ..., 0); all equal values (every count is 0, since the count is for STRICTLY smaller).",
        test_inputs=[([5, 2, 6, 1],), ([-1],), ([-1, -1],), ([2, 0, 1],)],
        reference_solution=(
            "def count_smaller(nums):\n"
            "    n = len(nums)\n"
            "    counts = [0] * n\n"
            "    indices = list(range(n))\n"
            "\n"
            "    def merge_sort(lo, hi):\n"
            "        if hi - lo <= 1:\n"
            "            return\n"
            "        mid = (lo + hi) // 2\n"
            "        merge_sort(lo, mid)\n"
            "        merge_sort(mid, hi)\n"
            "        merged = []\n"
            "        i, j = lo, mid\n"
            "        while i < mid and j < hi:\n"
            "            if nums[indices[i]] <= nums[indices[j]]:\n"
            "                counts[indices[i]] += j - mid\n"
            "                merged.append(indices[i])\n"
            "                i += 1\n"
            "            else:\n"
            "                merged.append(indices[j])\n"
            "                j += 1\n"
            "        while i < mid:\n"
            "            counts[indices[i]] += j - mid\n"
            "            merged.append(indices[i])\n"
            "            i += 1\n"
            "        while j < hi:\n"
            "            merged.append(indices[j])\n"
            "            j += 1\n"
            "        indices[lo:hi] = merged\n"
            "\n"
            "    merge_sort(0, n)\n"
            "    return counts\n"
        ),
        hints=[
            "This is Merge Intervals-style sorting, but you need to sort INDICES by their nums[] values, not the values themselves -- you need to remember which original position each count belongs to.",
            "The insight is in the merge step: when you take an element from the right half because it's smaller than what's waiting on the left, every element still waiting on the left is provably greater than it. So each time you finally place a left-half element, add however many right-half elements have already been placed ahead of it.",
            "counts[indices[i]] += j - mid whenever you place indices[i] from the left half during a merge (mid is the boundary, j is how far into the right half you've already consumed). Recurse merge_sort(lo,mid) and merge_sort(mid,hi) before merging, same as standard merge sort.",
        ],
    ),

    dict(
        slug="largest-rectangle-histogram",
        title="Largest Rectangle in Histogram",
        day=47,
        topic="stacks",
        pattern="monotonic stack",
        difficulty="Hard",
        interview_priority="Core",
        estimated_solve_minutes=30,
        progression_stage="variation",
        canonical_reference="LeetCode 84: Largest Rectangle in Histogram",
        path_tier="advanced",
        description=(
            "Given an array `heights` representing a histogram's bar heights (each bar has width 1), "
            "return the area of the largest rectangle that can be formed within the histogram's outline."
        ),
        constraints="1 <= len(heights) <= 10^5; 0 <= heights[i] <= 10^4.",
        function_signature="def largest_rectangle_area(heights):",
        starter_code=(
            "def largest_rectangle_area(heights):\n"
            "    # Monotonic increasing stack of indices. When a bar shorter than the\n"
            "    # stack's top shows up, that top bar can never extend any further right\n"
            "    # -- pop it and compute the biggest rectangle IT could form, using the\n"
            "    # new stack top (if any) as its left boundary and the current index as\n"
            "    # its right boundary.\n"
            "    stack = []\n"
            "    best = 0\n"
            "    pass\n"
            "    return best\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(n)",
        brute_force_approach="For each bar, expand left and right as far as possible while every bar in between is >= this bar's height, tracking the resulting width -- O(n^2) worst case.",
        optimal_approach="Keep a stack of indices with strictly increasing heights. Walk left to right (with one extra pass using height 0 at the end to flush everything): whenever the current bar is shorter than the stack's top, pop the top and compute the rectangle it could form -- its height is heights[popped], its width spans from just after the new stack top to just before the current index.",
        common_mistakes="Getting the width calculation wrong after popping (it's current_index - new_stack_top - 1, or current_index if the stack is now empty -- NOT current_index - popped_index); forgetting the final sentinel pass (height 0) needed to flush any bars still on the stack at the end.",
        edge_cases="A single bar (answer is just its height); all bars the same height (answer is height * len(heights)); strictly increasing or strictly decreasing heights (stresses the push-only / pop-heavy paths respectively).",
        test_inputs=[([2, 1, 5, 6, 2, 3],), ([2, 4],), ([1],), ([0, 0],), ([5, 5, 5, 5],)],
        test_labels=[None, None, "single bar", "zero-height bars", "all bars equal height"],
        reference_solution=(
            "def largest_rectangle_area(heights):\n"
            "    stack = []\n"
            "    best = 0\n"
            "    n = len(heights)\n"
            "    for i in range(n + 1):\n"
            "        h = heights[i] if i < n else 0\n"
            "        while stack and heights[stack[-1]] >= h:\n"
            "            height = heights[stack.pop()]\n"
            "            width = i if not stack else i - stack[-1] - 1\n"
            "            best = max(best, height * width)\n"
            "        stack.append(i)\n"
            "    return best\n"
        ),
        hints=[
            "For any single bar, the biggest rectangle it can anchor extends left and right as far as neighbors stay >= its own height. A monotonic (increasing) stack of indices lets you find exactly where that stretch ends, in one pass.",
            "When the current bar is shorter than the bar at the top of the stack, the top bar's stretch just ended -- pop it and compute its rectangle: height = that bar's height, width = (current index) - (new stack top index) - 1, or just the current index if the stack is now empty.",
            "Loop i from 0 to len(heights) INCLUSIVE, treating a virtual height of 0 past the end so every remaining bar gets flushed. while stack and heights[stack[-1]] >= h: pop and compute width/height as above; best = max(best, height*width). Then push i.",
        ],
    ),

    dict(
        slug="basic-calculator",
        title="Basic Calculator",
        day=48,
        topic="strings",
        pattern="stack-based expression evaluation",
        difficulty="Hard",
        interview_priority="Optional",
        estimated_solve_minutes=30,
        progression_stage="variation",
        canonical_reference="LeetCode 224: Basic Calculator",
        path_tier="advanced",
        description=(
            "Given a string `s` representing a valid mathematical expression containing non-negative "
            "integers, `+`, `-`, parentheses, and spaces (no `*` or `/`), evaluate and return the result."
        ),
        constraints="1 <= len(s) <= 3*10^5; s consists of digits, '+', '-', '(', ')', and ' '.",
        function_signature="def calculate(s):",
        starter_code=(
            "def calculate(s):\n"
            "    # Track a running result, the current number being built digit by digit,\n"
            "    # and the sign that applies to it. A stack holds (result-so-far, sign)\n"
            "    # pairs so entering '(' can start a fresh sub-expression, and ')' can\n"
            "    # fold that sub-expression's result back into what was paused outside it.\n"
            "    stack = []\n"
            "    result = 0\n"
            "    number = 0\n"
            "    sign = 1\n"
            "    pass\n"
            "    return result\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(n) worst case (deeply nested parentheses)",
        brute_force_approach="Recursively evaluate each parenthesized sub-expression as its own string -- correct, but repeatedly re-scans and re-slices the string rather than a single linear pass.",
        optimal_approach="Single pass, tracking result, the number currently being built, and sign (+1/-1). On '+'/'-', commit the pending number*sign into result, reset number, and set the new sign. On '(', push (result, sign) and reset both -- you're now accumulating the sub-expression fresh. On ')', commit the pending number, then pop the paused (outer_result, outer_sign) and fold: result = outer_result + outer_sign * result.",
        common_mistakes="Forgetting to commit the pending `number` before hitting `(` or `)` or the end of the string (it only gets added to result on the NEXT operator, so the very last number needs an explicit flush after the loop); pushing/popping in the wrong order around parentheses.",
        edge_cases="Nested parentheses several levels deep; a leading unary minus like '-(2+3)'; extra spaces scattered throughout (must be ignored, not treated as separators between multi-digit numbers).",
        test_inputs=[("1 + 1",), (" 2-1 + 2 ",), ("(1+(4+5+2)-3)+(6+8)",), ("2-(5-6)",)],
        test_labels=[None, None, "nested parentheses several levels deep", "subtraction of a parenthesized negative-net expression"],
        reference_solution=(
            "def calculate(s):\n"
            "    stack = []\n"
            "    result = 0\n"
            "    number = 0\n"
            "    sign = 1\n"
            "    for ch in s:\n"
            "        if ch.isdigit():\n"
            "            number = number * 10 + int(ch)\n"
            "        elif ch == '+':\n"
            "            result += sign * number\n"
            "            number = 0\n"
            "            sign = 1\n"
            "        elif ch == '-':\n"
            "            result += sign * number\n"
            "            number = 0\n"
            "            sign = -1\n"
            "        elif ch == '(':\n"
            "            stack.append(result)\n"
            "            stack.append(sign)\n"
            "            result = 0\n"
            "            sign = 1\n"
            "        elif ch == ')':\n"
            "            result += sign * number\n"
            "            number = 0\n"
            "            result *= stack.pop()\n"
            "            result += stack.pop()\n"
            "    result += sign * number\n"
            "    return result\n"
        ),
        hints=[
            "Build the current number digit by digit as you scan. A number only gets 'committed' into the running result when you hit the operator (or closing paren, or end of string) that follows it -- that's when you finally know its full value and its sign.",
            "Parentheses are the hard part: when you see '(', you need to pause the OUTER result and sign somewhere, then start fresh for the inner sub-expression. A stack of (paused_result, paused_sign) pairs is exactly that -- push on '(', and on ')' commit the pending number, then pop and fold: result = paused_result + paused_sign * result.",
            "On digit: number = number*10+int(ch). On +/-: result += sign*number; number=0; sign=+1/-1. On '(': push result and sign, reset both to 0/1. On ')': commit number into result first, then result = stack.pop() (sign) * result + stack.pop() (outer result). Flush number into result once more after the loop ends.",
        ],
    ),

    dict(
        slug="smallest-range-k-lists",
        title="Smallest Range Covering Elements from K Lists",
        day=None,
        topic="two-pointer",
        pattern="multi-pointer smallest range",
        difficulty="Hard",
        interview_priority="Optional",
        estimated_solve_minutes=30,
        progression_stage="variation",
        canonical_reference="LeetCode 632: Smallest Range Covering Elements from K Lists",
        path_tier="advanced",
        description=(
            "Given `k` lists of integers, each sorted in ascending order, find the smallest range `[start, "
            "end]` such that at least one number from EACH of the `k` lists falls within `[start, end]` "
            "(inclusive)."
        ),
        constraints="1 <= k <= 3500; 1 <= len(list) <= 50 per list; each list is sorted ascending.",
        function_signature="def smallest_range(nums):",
        starter_code=(
            "def smallest_range(nums):\n"
            "    # One pointer per list, all starting at index 0. At every step, find\n"
            "    # whichever pointer currently holds the SMALLEST value across all k\n"
            "    # lists -- that's always the bottleneck limiting how tight the current\n"
            "    # range can be, so advance exactly that one pointer forward.\n"
            "    pointers = [0] * len(nums)\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n * k) where n is the total number of elements across all lists",
        expected_space_complexity="O(k)",
        brute_force_approach="Merge all k lists into one sorted list tagged with their source list, then slide a window over it checking 'does this window include all k sources' -- also valid, but a min-heap of the k pointers' current values (O(n log k)) is the standard faster version of the same idea.",
        optimal_approach="Track one pointer per list and the current max across all k pointers' values. At each step, find the list holding the current MINIMUM value (it's the one holding back how tight the range can be), record the range [current_min, current_max] if it beats the best found so far, then advance only that list's pointer -- if that list runs out, no better range remains.",
        common_mistakes="Advancing every pointer at once instead of just the one holding the minimum (that's what actually keeps this a valid smallest-range search rather than an arbitrary walk); forgetting to update current_max as pointers advance (it can only grow or stay the same, never needs recomputing from scratch).",
        edge_cases="k == 1 (the answer is a single-element range, the smallest value in that one list); all lists identical; a list with only one element (that value is fixed in the range forever).",
        test_inputs=[([[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]],), ([[1, 2, 3], [1, 2, 3], [1, 2, 3]],), ([[10, 10], [11, 11]],), ([[1], [1], [1]],)],
        test_labels=[None, None, None, "every list has exactly one element"],
        reference_solution=(
            "def smallest_range(nums):\n"
            "    pointers = [0] * len(nums)\n"
            "    best_range = [float('-inf'), float('inf')]\n"
            "    while True:\n"
            "        current_min = float('inf')\n"
            "        current_max = float('-inf')\n"
            "        min_list = -1\n"
            "        for i, p in enumerate(pointers):\n"
            "            val = nums[i][p]\n"
            "            if val < current_min:\n"
            "                current_min = val\n"
            "                min_list = i\n"
            "            if val > current_max:\n"
            "                current_max = val\n"
            "        if current_max - current_min < best_range[1] - best_range[0]:\n"
            "            best_range = [current_min, current_max]\n"
            "        pointers[min_list] += 1\n"
            "        if pointers[min_list] == len(nums[min_list]):\n"
            "            break\n"
            "    return best_range\n"
        ),
        hints=[
            "At any moment you have one 'active' value per list. The range [min of those k values, max of those k values] always covers all k lists -- your job is to shrink that range as much as possible over time.",
            "The list holding the current MINIMUM is always the one worth advancing: since every list is sorted, advancing anything else can only ever make the range worse (its value can only go up), while advancing the minimum's list is the only move that can shrink the low end.",
            "Track pointers[i] per list, and current_max across all active values (it only ever grows). Loop: find current_min and which list it's in; compare current_max - current_min to the best found so far; advance that list's pointer; stop when any list runs out (no better answer can exist past that).",
        ],
    ),

    # ---------------------------------------------------------------
    # Mandatory: one Complex problem per existing topic (15). "Complex"
    # sits above Hard -- genuinely harder, high-value, recognizable
    # interview problems, spread across categories rather than
    # concentrated in one.
    # ---------------------------------------------------------------

    dict(
        slug="trapping-rain-water-ii",
        title="Trapping Rain Water II",
        day=47,
        topic="arrays",
        pattern="2D trapped water via heap + BFS",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=40,
        progression_stage="variation",
        canonical_reference="LeetCode 407: Trapping Rain Water II",
        path_tier="advanced",
        description=(
            "Given an `m x n` integer grid `heightMap` representing a 2D elevation map, return the total "
            "volume of water it can trap after rain (the 2D generalization of Trapping Rain Water -- water "
            "can now flow off any of the four sides of the grid, not just left/right)."
        ),
        constraints="1 <= m, n <= 200; 0 <= heightMap[i][j] <= 2*10^4.",
        function_signature="def trap_rain_water_2d(height_map):",
        starter_code=(
            "import heapq\n"
            "\n"
            "def trap_rain_water_2d(height_map):\n"
            "    # Every border cell is a 'spillway' -- water there just flows off the\n"
            "    # grid. Start a min-heap seeded with all border cells. Repeatedly pop\n"
            "    # the lowest boundary cell: any unvisited neighbor traps water up to\n"
            "    # THAT boundary height (if the neighbor is lower), then joins the\n"
            "    # boundary itself at max(popped height, its own height).\n"
            "    if not height_map or not height_map[0]:\n"
            "        return 0\n"
            "    pass\n"
        ),
        expected_time_complexity="O(m*n log(m*n))",
        expected_space_complexity="O(m*n)",
        brute_force_approach="Repeatedly do a full-grid pass computing each cell's trapped water as min(max-height-reachable-in-every-direction) - own height, like the 1D two-pointer idea extended naively -- correct in spirit but doesn't generalize efficiently to 4 directions without the heap/BFS 'shrinking boundary' idea below.",
        optimal_approach="Push every border cell into a min-heap (by height), marking it visited -- the border is where water can escape, so it defines the initial 'boundary' of the flood-fill. Repeatedly pop the LOWEST boundary cell (it's the weakest point the water could escape through); for each unvisited neighbor, it traps water up to max(0, popped height - neighbor height), then joins the boundary at height max(popped height, neighbor height) and gets pushed onto the heap.",
        common_mistakes="Only considering left/right neighbors like the 1D version (this problem needs all 4 directions, which is why two-pointer alone no longer works and a heap-driven boundary/BFS approach is needed instead); forgetting that a newly-absorbed cell's OWN boundary height is the max of the popped height and its own height, not just its own height (water can't be lower than the wall that's currently containing it).",
        edge_cases="Every cell on the border (nothing to trap, answer 0); a completely flat grid (answer 0); a small interior 'pit' surrounded by tall walls on all sides.",
        test_inputs=[
            ([[1, 4, 3, 1, 3, 2], [3, 2, 1, 3, 2, 4], [2, 3, 3, 2, 3, 1]],),
            ([[3, 3, 3, 3, 3], [3, 2, 2, 2, 3], [3, 2, 1, 2, 3], [3, 2, 2, 2, 3], [3, 3, 3, 3, 3]],),
            ([[1, 1], [1, 1]],),
            ([[12, 13, 1, 12], [13, 4, 13, 12], [13, 8, 10, 12], [12, 13, 12, 12], [13, 13, 13, 13]],),
        ],
        test_labels=[None, "a single-cell pit surrounded by walls on all sides", "no interior cells at all (nothing to trap)", None],
        reference_solution=(
            "import heapq\n"
            "\n"
            "def trap_rain_water_2d(height_map):\n"
            "    if not height_map or not height_map[0]:\n"
            "        return 0\n"
            "    m, n = len(height_map), len(height_map[0])\n"
            "    visited = [[False] * n for _ in range(m)]\n"
            "    heap = []\n"
            "    for i in range(m):\n"
            "        for j in range(n):\n"
            "            if i == 0 or i == m - 1 or j == 0 or j == n - 1:\n"
            "                heapq.heappush(heap, (height_map[i][j], i, j))\n"
            "                visited[i][j] = True\n"
            "    water = 0\n"
            "    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]\n"
            "    while heap:\n"
            "        height, i, j = heapq.heappop(heap)\n"
            "        for di, dj in directions:\n"
            "            ni, nj = i + di, j + dj\n"
            "            if 0 <= ni < m and 0 <= nj < n and not visited[ni][nj]:\n"
            "                visited[ni][nj] = True\n"
            "                water += max(0, height - height_map[ni][nj])\n"
            "                heapq.heappush(heap, (max(height, height_map[ni][nj]), ni, nj))\n"
            "    return water\n"
        ),
        hints=[
            "In 1D, two pointers work because the lower of the two outer walls always decides how much water is trapped. In 2D there's no single 'left wall' and 'right wall' anymore -- the boundary is the entire border, and it shrinks inward as you process it.",
            "Seed a min-heap with every border cell (they're all places water can escape). Always process the CURRENT lowest point of the boundary first -- that's the weakest point water could leak through, so it correctly limits how much its neighbors can hold.",
            "Pop the lowest (height,i,j) from the heap. For each unvisited neighbor: water += max(0, height - neighbor_height); push the neighbor with height max(height, neighbor_height) (the boundary can never get lower as it advances inward) and mark it visited.",
        ],
    ),

    dict(
        slug="split-array-largest-sum",
        title="Split Array Largest Sum",
        day=47,
        topic="binary-search",
        pattern="binary search on the answer + greedy feasibility check",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=35,
        progression_stage="variation",
        canonical_reference="LeetCode 410: Split Array Largest Sum",
        path_tier="advanced",
        description=(
            "Given an integer array `nums` and an integer `k`, split `nums` into `k` non-empty contiguous "
            "subarrays so as to MINIMIZE the largest sum among the `k` subarrays. Return that minimized "
            "largest sum."
        ),
        constraints="1 <= len(nums) <= 1000; 0 <= nums[i] <= 10^6; 1 <= k <= min(50, len(nums)).",
        function_signature="def split_array(nums, k):",
        starter_code=(
            "def split_array(nums, k):\n"
            "    # Binary search over the ANSWER itself (the largest-subarray-sum cap),\n"
            "    # not over the array. For a candidate cap, a greedy check tells you\n"
            "    # in O(n) whether nums can be split into <= k pieces each summing to\n"
            "    # at most that cap -- and 'is this cap feasible' is monotonic, which\n"
            "    # is exactly what makes binary search valid here.\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n log(sum(nums)))",
        expected_space_complexity="O(1)",
        brute_force_approach="Try every way to place k-1 dividers among the array -- exponential; a DP over (index, pieces-used-so-far) works in polynomial time but is slower and more complex than binary search on the answer.",
        optimal_approach="The answer (minimized largest sum) lies between max(nums) (each element its own piece can't do worse than this as a lower bound) and sum(nums) (one single piece, the upper bound). Binary search that range: for a candidate cap, greedily walk the array accumulating a running sum, starting a new piece whenever adding the next element would exceed the cap -- if the number of pieces needed is <= k, the cap is feasible (search lower); otherwise it's too tight (search higher).",
        common_mistakes="Binary searching over array indices instead of over the ANSWER VALUE (the largest-sum cap) -- the whole trick is that feasibility of a cap is monotonic, not the array itself; getting the lower bound wrong (it must be max(nums), not 0 -- a single element larger than any candidate cap can never fit in one piece).",
        edge_cases="k == 1 (the whole array is one piece, answer is sum(nums)); k == len(nums) (every element is its own piece, answer is max(nums)); an array where one element is much larger than all others combined.",
        test_inputs=[([7, 2, 5, 10, 8], 2), ([1, 2, 3, 4, 5], 2), ([1, 4, 4], 3), ([2, 3, 1, 1, 1, 1, 1], 4)],
        reference_solution=(
            "def split_array(nums, k):\n"
            "    def can_split(max_sum):\n"
            "        pieces = 1\n"
            "        current = 0\n"
            "        for n in nums:\n"
            "            if current + n > max_sum:\n"
            "                pieces += 1\n"
            "                current = n\n"
            "                if pieces > k:\n"
            "                    return False\n"
            "            else:\n"
            "                current += n\n"
            "        return True\n"
            "\n"
            "    lo, hi = max(nums), sum(nums)\n"
            "    while lo < hi:\n"
            "        mid = (lo + hi) // 2\n"
            "        if can_split(mid):\n"
            "            hi = mid\n"
            "        else:\n"
            "            lo = mid + 1\n"
            "    return lo\n"
        ),
        hints=[
            "You're not searching the array -- you're searching the SPACE OF POSSIBLE ANSWERS. The answer (the minimized largest-subarray-sum) is some value between max(nums) and sum(nums); binary search that range instead.",
            "For any candidate cap, you can check feasibility greedily in O(n): walk the array, keep a running sum, and start a new piece the moment adding the next element would exceed the cap. If that produces <= k pieces total, the cap works.",
            "lo, hi = max(nums), sum(nums). While lo < hi: mid = (lo+hi)//2; if can_split(mid): hi = mid (try tighter); else: lo = mid + 1 (too tight, relax). Return lo. can_split greedily counts pieces as described above.",
        ],
    ),

    dict(
        slug="regular-expression-matching",
        title="Regular Expression Matching",
        day=47,
        topic="dynamic-programming",
        pattern="2D DP over string positions",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=40,
        progression_stage="variation",
        canonical_reference="LeetCode 10: Regular Expression Matching",
        path_tier="advanced",
        description=(
            "Implement regular expression matching supporting `.` (matches any single character) and `*` "
            "(matches zero or more of the PRECEDING element) against a full string `s` and pattern `p`. The "
            "match must cover the entire string, not just part of it."
        ),
        constraints="1 <= len(s) <= 20; 1 <= len(p) <= 30; p only contains lowercase letters, '.', and '*'; every '*' has a preceding element.",
        function_signature="def is_match(s, p):",
        starter_code=(
            "def is_match(s, p):\n"
            "    # dp[i][j] = does s[:i] fully match p[:j]?\n"
            "    # The tricky transition is '*': p[j-1]=='*' means \"zero or more of\n"
            "    # p[j-2]\", so dp[i][j] can succeed either by using ZERO of that\n"
            "    # element (fall back to dp[i][j-2]) or by using ONE MORE of it\n"
            "    # (dp[i-1][j], if s[i-1] actually matches p[j-2]).\n"
            "    m, n = len(s), len(p)\n"
            "    dp = [[False] * (n + 1) for _ in range(m + 1)]\n"
            "    dp[0][0] = True\n"
            "    pass\n"
            "    return dp[m][n]\n"
        ),
        expected_time_complexity="O(m*n)",
        expected_space_complexity="O(m*n)",
        brute_force_approach="Plain recursion trying each choice at every position without memoization -- correct, but re-explores the same (i,j) states exponentially many times.",
        optimal_approach="Bottom-up DP where dp[i][j] means 's[:i] matches p[:j]'. Base case dp[0][0]=True. For a literal or '.', dp[i][j]=dp[i-1][j-1] (both fully matched) if that character matches. For a trailing '*' in the pattern, dp[i][j] is True if EITHER dp[i][j-2] (treat the starred element as matching zero times) OR (the preceding pattern char matches s[i-1] AND dp[i-1][j] -- treat it as matching one more copy).",
        common_mistakes="Forgetting the 'zero occurrences' case for '*' (a*b* can match an empty string!); not initializing row 0 correctly for patterns like a*b*c* that can match an empty string even though the pattern itself is non-empty; treating '*' as matching any characters like a wildcard glob (`*` here always applies to the PRECEDING element specifically, unlike shell globbing).",
        edge_cases="Pattern that can match empty string (e.g. 'a*') against an empty-equivalent prefix; '.' combined with '*' (matches any run of any characters); a pattern longer than the string that still needs to match via zero-occurrence stars.",
        test_inputs=[("aa", "a"), ("aa", "a*"), ("ab", ".*"), ("aab", "c*a*b"), ("mississippi", "mis*is*p*.")],
        test_labels=[None, None, None, None, "a deliberately tricky mismatch -- correctly returns False"],
        reference_solution=(
            "def is_match(s, p):\n"
            "    m, n = len(s), len(p)\n"
            "    dp = [[False] * (n + 1) for _ in range(m + 1)]\n"
            "    dp[0][0] = True\n"
            "    for j in range(1, n + 1):\n"
            "        if p[j - 1] == '*':\n"
            "            dp[0][j] = dp[0][j - 2]\n"
            "    for i in range(1, m + 1):\n"
            "        for j in range(1, n + 1):\n"
            "            if p[j - 1] == '.' or p[j - 1] == s[i - 1]:\n"
            "                dp[i][j] = dp[i - 1][j - 1]\n"
            "            elif p[j - 1] == '*':\n"
            "                dp[i][j] = dp[i][j - 2]\n"
            "                if p[j - 2] == '.' or p[j - 2] == s[i - 1]:\n"
            "                    dp[i][j] = dp[i][j] or dp[i - 1][j]\n"
            "    return dp[m][n]\n"
        ),
        hints=[
            "Define dp[i][j] as 'does the first i characters of s match the first j characters of p, entirely'. Fill it bottom-up from dp[0][0]=True (empty matches empty).",
            "The hard case is p[j-1]=='*': it means 'zero or more of p[j-2]'. Zero occurrences means dp[i][j] can just fall back to dp[i][j-2] (ignore the starred pair entirely). One more occurrence means dp[i][j] can also succeed if p[j-2] matches s[i-1] AND dp[i-1][j] was already true.",
            "For j in range(1,n+1) initialize dp[0][j] (empty string vs prefix of pattern) using the '*' zero-occurrence rule. Then for each i,j: if p[j-1] is '.' or equals s[i-1]: dp[i][j]=dp[i-1][j-1]. Elif p[j-1]=='*': dp[i][j] = dp[i][j-2] or (matches(p[j-2],s[i-1]) and dp[i-1][j]).",
        ],
    ),

    dict(
        slug="alien-dictionary",
        title="Alien Dictionary",
        day=47,
        topic="graphs",
        pattern="topological sort from ordering constraints",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=35,
        progression_stage="variation",
        canonical_reference="LeetCode 269: Alien Dictionary",
        path_tier="advanced",
        description=(
            "You're given a list of `words` from an alien language, sorted lexicographically according to "
            "that language's OWN (unknown) alphabet ordering. Derive one valid character ordering of that "
            "alphabet consistent with the given words, or return `\"\"` if the words are inconsistent with "
            "any valid ordering (a cycle) or otherwise invalid (a word appears before its own prefix)."
        ),
        constraints="1 <= len(words) <= 100; every word is lowercase letters only.",
        function_signature="def alien_order(words):",
        starter_code=(
            "from collections import defaultdict, deque\n"
            "\n"
            "def alien_order(words):\n"
            "    # Compare each ADJACENT pair of words: the first position where they\n"
            "    # differ tells you one letter comes before another in the alien\n"
            "    # alphabet -- that's one directed edge in a graph over letters. Once\n"
            "    # you have all such edges, a topological sort of that graph IS the\n"
            "    # alphabet (or proves no valid alphabet exists, if there's a cycle).\n"
            "    graph = defaultdict(set)\n"
            "    in_degree = {c: 0 for word in words for c in word}\n"
            "    pass\n"
        ),
        expected_time_complexity="O(C) where C is the total length of all words",
        expected_space_complexity="O(1) alphabet-bounded, or O(U) for U unique letters",
        brute_force_approach="Try every permutation of the alphabet's letters and check which one is consistent with all adjacent word-pair comparisons -- factorial time, infeasible past a handful of letters.",
        optimal_approach="Build a directed graph: for each adjacent pair of words, find the first differing character and add an edge from the earlier language's letter to the later one. Also detect the invalid case where a word is a prefix of an earlier word that appears before it. Then run Kahn's algorithm (BFS topological sort using in-degree counts) -- if the resulting order doesn't include every letter, a cycle exists and there's no valid ordering.",
        common_mistakes="Only comparing the first character of each word pair instead of the first character where they actually DIFFER (words can share a long common prefix); forgetting the special invalid case where a longer word appears immediately before its own shorter prefix (e.g. ['abc','ab'] is never valid in any lexicographic ordering); missing letters that never get an edge (an isolated letter still needs to appear somewhere in the final order, with in_degree 0).",
        edge_cases="A single word (any letter ordering works -- return its letters in appearance order); words that produce a cycle (return \"\"); a word that's an invalid prefix violation (return \"\").",
        test_inputs=[(["wrt", "wrf", "er", "ett", "rftt"],), (["z", "x"],), (["z", "x", "z"],), (["abc", "ab"],)],
        test_labels=[None, None, "a cycle -- no valid ordering exists", "invalid: a word appears directly before its own prefix"],
        reference_solution=(
            "from collections import defaultdict, deque\n"
            "\n"
            "def alien_order(words):\n"
            "    graph = defaultdict(set)\n"
            "    in_degree = {c: 0 for word in words for c in word}\n"
            "    for w1, w2 in zip(words, words[1:]):\n"
            "        min_len = min(len(w1), len(w2))\n"
            "        found_diff = False\n"
            "        for i in range(min_len):\n"
            "            if w1[i] != w2[i]:\n"
            "                if w2[i] not in graph[w1[i]]:\n"
            "                    graph[w1[i]].add(w2[i])\n"
            "                    in_degree[w2[i]] += 1\n"
            "                found_diff = True\n"
            "                break\n"
            "        if not found_diff and len(w1) > len(w2):\n"
            "            return ''\n"
            "    queue = deque([c for c in in_degree if in_degree[c] == 0])\n"
            "    order = []\n"
            "    while queue:\n"
            "        c = queue.popleft()\n"
            "        order.append(c)\n"
            "        for nxt in graph[c]:\n"
            "            in_degree[nxt] -= 1\n"
            "            if in_degree[nxt] == 0:\n"
            "                queue.append(nxt)\n"
            "    if len(order) < len(in_degree):\n"
            "        return ''\n"
            "    return ''.join(order)\n"
        ),
        hints=[
            "You don't need to know the WHOLE alphabet order at once -- you only get partial-order hints, one per adjacent word pair, from the first character where they differ. That's a set of directed edges: 'this letter comes before that letter'.",
            "Once you have the edges, this is exactly the Course Schedule cycle-detection problem, one level further: instead of just detecting a cycle, you need the actual topological order (via Kahn's algorithm/BFS with in-degree counts), and a leftover letter with nonzero in-degree at the end means a cycle exists.",
            "Build graph[c1].add(c2) and in_degree[c2]+=1 for the first differing letter of each adjacent word pair (watch for the invalid 'word before its own prefix' case). Then BFS from every letter with in_degree 0, appending to order and decrementing neighbors' in_degree as you go. If order doesn't cover every letter, return ''.",
        ],
    ),

    dict(
        slug="substring-concat-all-words",
        title="Substring with Concatenation of All Words",
        day=None,
        topic="hashing",
        pattern="fixed-size window of exact word counts",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=35,
        progression_stage="variation",
        canonical_reference="LeetCode 30: Substring with Concatenation of All Words",
        path_tier="advanced",
        description=(
            "Given a string `s` and a list `words` of same-length words, return the starting indices of "
            "every substring in `s` that is exactly a concatenation of ALL words in `words`, each used "
            "exactly once, in any order (no characters in between)."
        ),
        constraints="1 <= len(s) <= 10^4; 1 <= len(words) <= 5000; every word has the same length, 1-30; words may repeat.",
        function_signature="def find_substring(s, words):",
        starter_code=(
            "def find_substring(s, words):\n"
            "    # Every valid window has the exact same total length (word_len * len(words)).\n"
            "    # For each possible starting index, chop the window into word-length\n"
            "    # chunks and check whether the resulting multiset of chunks exactly\n"
            "    # matches the multiset of `words` -- a hashmap of word -> required count\n"
            "    # makes that check fast, and lets you bail out the instant a chunk is\n"
            "    # wrong or over-used.\n"
            "    if not words:\n"
            "        return []\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n * k) where n = len(s), k = len(words)",
        expected_space_complexity="O(k)",
        brute_force_approach="Generate every permutation of words, concatenate each into a candidate string, and search for it in s directly -- factorial in len(words), infeasible past a handful of words.",
        optimal_approach="Precompute word_count, a hashmap of word -> how many times it should appear. For each candidate start index, walk forward one word-length chunk at a time: if the chunk isn't a valid word, or would exceed its required count, bail out immediately; if all len(words) chunks are consumed validly, record the start index.",
        common_mistakes="Not bailing out early on an invalid or over-used chunk (turns an O(n*k) scan into something much slower by always checking the full window); forgetting `words` can contain DUPLICATE words, so this is a multiset-count problem, not a set-membership one.",
        edge_cases="`words` contains duplicate words (the multiset-count check specifically protects against over-counting them); no valid substring exists anywhere (empty result); the entire string s is itself exactly one valid concatenation.",
        test_inputs=[("barfoothefoobarman", ["foo", "bar"]), ("wordgoodgoodgoodbestword", ["word", "good", "best", "word"]), ("barfoofoobarthefoobarman", ["bar", "foo", "the"]), ("a", ["a"])],
        reference_solution=(
            "def find_substring(s, words):\n"
            "    if not words:\n"
            "        return []\n"
            "    word_len = len(words[0])\n"
            "    total_len = word_len * len(words)\n"
            "    if total_len > len(s):\n"
            "        return []\n"
            "    word_count = {}\n"
            "    for w in words:\n"
            "        word_count[w] = word_count.get(w, 0) + 1\n"
            "    result = []\n"
            "    for i in range(len(s) - total_len + 1):\n"
            "        seen = {}\n"
            "        j = 0\n"
            "        while j < len(words):\n"
            "            start = i + j * word_len\n"
            "            word = s[start:start + word_len]\n"
            "            if word not in word_count:\n"
            "                break\n"
            "            seen[word] = seen.get(word, 0) + 1\n"
            "            if seen[word] > word_count[word]:\n"
            "                break\n"
            "            j += 1\n"
            "        if j == len(words):\n"
            "            result.append(i)\n"
            "    return result\n"
        ),
        hints=[
            "Every valid answer has exactly the same total length: word_len * len(words). That bounds which starting indices are even worth checking.",
            "At each candidate start, don't build the concatenated string and search for it -- instead chop the window into word_len-sized chunks and count them, comparing against a hashmap of how many times each word is ALLOWED to appear (built once, up front, from `words`).",
            "word_count = {w: words.count(w) ...} (built with a dict, once). For each start i: walk j from 0 to len(words), slicing s[i+j*word_len : i+(j+1)*word_len]; track a local `seen` count; break immediately if the chunk isn't in word_count or seen exceeds word_count. If you consume all len(words) chunks without breaking, record i.",
        ],
    ),

    dict(
        slug="ipo-maximize-capital",
        title="IPO",
        day=None,
        topic="heaps",
        pattern="two-heap greedy project selection",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=35,
        progression_stage="variation",
        canonical_reference="LeetCode 502: IPO",
        path_tier="advanced",
        description=(
            "You start with capital `w` and can complete at most `k` projects. Project `i` requires "
            "`capital[i]` to start and yields `profits[i]` on completion (added to your capital). Choose up "
            "to `k` projects (each at most once) to MAXIMIZE your final capital, only ever starting a "
            "project you currently have enough capital for."
        ),
        constraints="1 <= k <= 10^5; 0 <= w <= 10^9; len(profits) == len(capital); 0 <= profits[i], capital[i] <= 10^9.",
        function_signature="def find_maximized_capital(k, w, profits, capital):",
        starter_code=(
            "import heapq\n"
            "\n"
            "def find_maximized_capital(k, w, profits, capital):\n"
            "    # Greedy: at every step, among all projects you can currently AFFORD,\n"
            "    # taking the most PROFITABLE one is always at least as good as taking\n"
            "    # any other affordable one -- it only grows your capital more, which\n"
            "    # can only unlock more (or equally many) future options.\n"
            "    projects = sorted(zip(capital, profits))\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n log n)",
        expected_space_complexity="O(n)",
        brute_force_approach="At each of the k rounds, scan every not-yet-used project to find the most profitable affordable one -- O(k*n), too slow for the given constraints.",
        optimal_approach="Sort projects by required capital. Use a max-heap of profits for 'currently affordable' projects: at each of the k rounds, first push every project whose capital requirement is now <= your current capital (advancing a pointer through the capital-sorted list), then pop the single most profitable one from the max-heap and add its profit to your capital.",
        common_mistakes="Re-sorting or re-scanning all projects every round instead of maintaining a pointer into the capital-sorted list plus a heap of currently-affordable profits (defeats the whole point of the heap); stopping early when the heap is momentarily empty at some round instead of just breaking out (once nothing is affordable, more capital won't appear since no more projects will be added).",
        edge_cases="k larger than the number of profitable opportunities actually reachable (stop early once no project is affordable); w already enough to afford everything (greedily take the k most profitable outright); a project with capital requirement of 0 (always affordable).",
        test_inputs=[(2, 0, [1, 2, 3], [0, 1, 1]), (3, 0, [1, 2, 3], [0, 1, 2]), (1, 0, [1, 2, 3], [1, 1, 2])],
        test_labels=[None, None, "capital never reaches the higher-capital-requirement projects -- only 1 project is ever reachable"],
        reference_solution=(
            "import heapq\n"
            "\n"
            "def find_maximized_capital(k, w, profits, capital):\n"
            "    projects = sorted(zip(capital, profits))\n"
            "    n = len(projects)\n"
            "    available = []\n"
            "    i = 0\n"
            "    for _ in range(k):\n"
            "        while i < n and projects[i][0] <= w:\n"
            "            heapq.heappush(available, -projects[i][1])\n"
            "            i += 1\n"
            "        if not available:\n"
            "            break\n"
            "        w += -heapq.heappop(available)\n"
            "    return w\n"
        ),
        hints=[
            "At any point, among the projects you can currently afford, always taking the one with the biggest profit is never a mistake -- it maximizes capital gained this round, which can only help (never hurt) what becomes affordable next round.",
            "Sort projects by their capital requirement once, up front. Keep a pointer into that sorted list and a max-heap (Python's heapq is a min-heap, so push negated profits) of profits for every project that's become affordable so far.",
            "For each of k rounds: advance the pointer, pushing -profit for every project whose capital requirement is now <= w. If the heap is empty, break (nothing left is affordable). Otherwise pop the heap (most profit) and add it to w.",
        ],
    ),

    dict(
        slug="lfu-cache",
        title="LFU Cache",
        day=None,
        topic="linked-lists",
        pattern="hashmap + frequency buckets of ordered keys",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=40,
        progression_stage="variation",
        canonical_reference="LeetCode 460: LFU Cache",
        path_tier="advanced",
        description=(
            "Design a fixed-capacity Least Frequently Used (LFU) cache. `get(key)` returns the value for "
            "`key` (or -1 if absent) and increments its use frequency; `put(key, value)` inserts or updates "
            "a key (also incrementing its frequency) and, if this pushes the cache over capacity, evicts "
            "the LEAST FREQUENTLY used key -- ties broken by evicting the LEAST RECENTLY used among them. "
            "The first op is always `'LFUCache'` with `[capacity]` as its args."
        ),
        constraints="0 <= capacity <= 10^4; at most 2*10^5 total calls to get/put.",
        function_signature="def lfu_cache_ops(ops, args):",
        starter_code=(
            "from collections import defaultdict, OrderedDict\n"
            "\n"
            "class LFUCache:\n"
            "    def __init__(self, capacity):\n"
            "        self.capacity = capacity\n"
            "        self.min_freq = 0\n"
            "        self.key_to_val_freq = {}\n"
            "        # freq -> OrderedDict of keys currently at that frequency, in\n"
            "        # least-to-most-recently-used order (so popitem(last=False) always\n"
            "        # gives the right eviction victim within a frequency bucket).\n"
            "        self.freq_to_keys = defaultdict(OrderedDict)\n"
            "\n"
            "    def get(self, key):\n"
            "        pass\n"
            "\n"
            "    def put(self, key, value):\n"
            "        pass\n"
            "\n"
            "\n"
            "def lfu_cache_ops(ops, args):\n"
            "    cache = None\n"
            "    results = []\n"
            "    for op, arg in zip(ops, args):\n"
            "        if op == 'LFUCache':\n"
            "            cache = LFUCache(arg[0])\n"
            "            results.append(None)\n"
            "        elif op == 'get':\n"
            "            results.append(cache.get(arg[0]))\n"
            "        else:\n"
            "            cache.put(arg[0], arg[1])\n"
            "            results.append(None)\n"
            "    return results\n"
        ),
        expected_time_complexity="O(1) per get/put",
        expected_space_complexity="O(capacity)",
        brute_force_approach="Track frequency in a plain dict and scan all keys for the minimum frequency (with a secondary recency check for ties) on every eviction -- correct, but O(n) per eviction instead of O(1).",
        optimal_approach="Two maps: key -> (value, freq), and freq -> an OrderedDict of keys currently at that frequency (insertion order doubling as recency order). A 'touch' (on get, or put of an existing key) removes the key from its current frequency bucket, bumps its freq by 1, and re-inserts it at the END of the new bucket -- and if that empties the OLD bucket and it was the current min_freq, min_freq increments. On eviction, pop the FRONT (least-recently-used) key of the min_freq bucket.",
        common_mistakes="Forgetting to update min_freq when a frequency bucket becomes empty (it can only mean the minimum frequency present just increased); breaking ties by insertion order globally instead of RECENCY WITHIN the tied frequency (LFU ties break by LRU, not by original insertion order); not handling capacity == 0 (every put should be a no-op).",
        edge_cases="capacity == 0 (nothing is ever actually stored); two keys with equal frequency, tie broken by which was used more recently; get() on an absent key must NOT insert anything or affect any frequency bucket.",
        test_inputs=[
            (["LFUCache", "put", "put", "get", "put", "get", "get", "put", "get", "get", "get"],
             [[2], [1, 1], [2, 2], [1], [3, 3], [2], [3], [4, 4], [1], [3], [4]]),
            (["LFUCache", "put", "get"], [[0], [0, 0], [0]]),
            (["LFUCache", "put", "put", "put", "get", "get", "get"],
             [[2], [1, 1], [2, 2], [3, 3], [1], [2], [3]]),
        ],
        test_labels=[None, "capacity 0 -- every put is a no-op", "a frequency tie (both untouched, same freq) broken by recency -- the untouched-longest key is evicted"],
        reference_solution=(
            "from collections import defaultdict, OrderedDict\n"
            "\n"
            "class LFUCache:\n"
            "    def __init__(self, capacity):\n"
            "        self.capacity = capacity\n"
            "        self.min_freq = 0\n"
            "        self.key_to_val_freq = {}\n"
            "        self.freq_to_keys = defaultdict(OrderedDict)\n"
            "\n"
            "    def _touch(self, key):\n"
            "        value, freq = self.key_to_val_freq[key]\n"
            "        del self.freq_to_keys[freq][key]\n"
            "        if not self.freq_to_keys[freq]:\n"
            "            del self.freq_to_keys[freq]\n"
            "            if self.min_freq == freq:\n"
            "                self.min_freq += 1\n"
            "        self.freq_to_keys[freq + 1][key] = None\n"
            "        self.key_to_val_freq[key] = (value, freq + 1)\n"
            "\n"
            "    def get(self, key):\n"
            "        if key not in self.key_to_val_freq:\n"
            "            return -1\n"
            "        self._touch(key)\n"
            "        return self.key_to_val_freq[key][0]\n"
            "\n"
            "    def put(self, key, value):\n"
            "        if self.capacity <= 0:\n"
            "            return\n"
            "        if key in self.key_to_val_freq:\n"
            "            _, freq = self.key_to_val_freq[key]\n"
            "            self.key_to_val_freq[key] = (value, freq)\n"
            "            self._touch(key)\n"
            "            return\n"
            "        if len(self.key_to_val_freq) >= self.capacity:\n"
            "            evict_key, _ = self.freq_to_keys[self.min_freq].popitem(last=False)\n"
            "            del self.key_to_val_freq[evict_key]\n"
            "        self.key_to_val_freq[key] = (value, 1)\n"
            "        self.freq_to_keys[1][key] = None\n"
            "        self.min_freq = 1\n"
            "\n"
            "\n"
            "def lfu_cache_ops(ops, args):\n"
            "    cache = None\n"
            "    results = []\n"
            "    for op, arg in zip(ops, args):\n"
            "        if op == 'LFUCache':\n"
            "            cache = LFUCache(arg[0])\n"
            "            results.append(None)\n"
            "        elif op == 'get':\n"
            "            results.append(cache.get(arg[0]))\n"
            "        else:\n"
            "            cache.put(arg[0], arg[1])\n"
            "            results.append(None)\n"
            "    return results\n"
        ),
        hints=[
            "LFU needs TWO axes tracked at once: frequency (which key to evict) and recency (how to break frequency ties). One hashmap of key -> (value, freq), plus one hashmap of freq -> an ordered collection of keys currently at that frequency, covers both.",
            "Whenever a key is touched (get, or put of an existing key), it moves from its current frequency bucket to the next one up -- remove it from the old OrderedDict, and if that bucket is now empty AND was the minimum frequency, min_freq must increase. Insert it at the end of the new bucket (so within a bucket, order is oldest-to-newest-touched, which is exactly LRU order for tie-breaking).",
            "_touch(key): pop key from freq_to_keys[old_freq]; if that bucket's now empty and was min_freq, min_freq += 1; add key to freq_to_keys[old_freq+1]; update key_to_val_freq. On eviction: popitem(last=False) from freq_to_keys[min_freq] (the LRU key at the true minimum frequency).",
        ],
    ),

    dict(
        slug="constrained-subsequence-sum",
        title="Constrained Subsequence Sum",
        day=49,
        topic="queues",
        pattern="monotonic deque driving a DP recurrence",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=35,
        progression_stage="variation",
        canonical_reference="LeetCode 1425: Constrained Subsequence Sum",
        path_tier="advanced",
        description=(
            "Given an integer array `nums` and an integer `k`, return the maximum sum of a non-empty "
            "SUBSEQUENCE of `nums` such that for every two consecutive chosen elements (at indices `i` "
            "and `j`, i < j), `j - i <= k` (no two consecutively-chosen elements are more than k apart)."
        ),
        constraints="1 <= len(nums) <= 10^5; -10^4 <= nums[i] <= 10^4; 1 <= k <= len(nums).",
        function_signature="def constrained_subset_sum(nums, k):",
        starter_code=(
            "from collections import deque\n"
            "\n"
            "def constrained_subset_sum(nums, k):\n"
            "    # dp[i] = best subsequence sum ENDING exactly at index i. dp[i] =\n"
            "    # nums[i] + max(0, best dp[j] for j in the last k indices) -- and\n"
            "    # 'best dp[j] in a sliding window of size k' is exactly Sliding\n"
            "    # Window Maximum's job, so a monotonic decreasing deque of indices\n"
            "    # (by dp value) makes each step O(1) amortized instead of O(k).\n"
            "    n = len(nums)\n"
            "    dp = [0] * n\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(n)",
        brute_force_approach="For each index, scan back up to k previous indices to find the best dp value to extend from -- O(n*k).",
        optimal_approach="dp[i] = nums[i] + max(0, best dp[j] among the last k indices) -- the max(...,0) lets you 'restart' the subsequence at i if every recent dp value is negative. Maintaining 'the best dp value among the last k indices' incrementally is exactly the Sliding Window Maximum pattern: a deque of indices with strictly decreasing dp values, popped from the front when they fall outside the k-window and from the back when a new value would make them useless.",
        common_mistakes="Forgetting the max(0, ...) term (without it, you'd be forced to always extend the previous chosen element even when doing so hurts, instead of being allowed to start a fresh subsequence at the current index); letting the deque grow unbounded by not evicting indices that have fallen more than k positions behind.",
        edge_cases="All negative numbers (the answer is just the single largest, i.e. least negative, element -- you're never forced to pick more than one); k >= len(nums) (every previous index is always in range, so this degenerates to plain unconstrained 'best previous nonnegative dp'); k == 1 (equivalent to the classic Maximum Subarray, adjacent-only).",
        test_inputs=[([10, 2, -10, 5, 20], 2), ([-1, -2, -3], 1), ([10, -2, -10, -5, 20], 2)],
        test_labels=[None, "all negative -- answer is just the single largest (least negative) element", None],
        reference_solution=(
            "from collections import deque\n"
            "\n"
            "def constrained_subset_sum(nums, k):\n"
            "    n = len(nums)\n"
            "    dp = [0] * n\n"
            "    dq = deque()\n"
            "    best = float('-inf')\n"
            "    for i in range(n):\n"
            "        while dq and dq[0] < i - k:\n"
            "            dq.popleft()\n"
            "        dp[i] = nums[i] + (dp[dq[0]] if dq and dp[dq[0]] > 0 else 0)\n"
            "        while dq and dp[dq[-1]] <= dp[i]:\n"
            "            dq.pop()\n"
            "        dq.append(i)\n"
            "        best = max(best, dp[i])\n"
            "    return best\n"
        ),
        hints=[
            "Think of dp[i] as 'the best subsequence sum if the LAST chosen element is index i'. Every dp[i] only depends on the best dp value among the k indices immediately before it (plus the option to just start fresh at i).",
            "'Best value in the last k positions, updated as you slide forward' is exactly the Sliding Window Maximum problem -- reuse that same monotonic deque idea, but the values being compared are dp[] entries instead of nums[] entries directly.",
            "Keep a deque of indices with strictly decreasing dp values, front = the max in the current k-window. Pop expired front indices (more than k behind i). dp[i] = nums[i] + max(0, dp[dq[0]] if dq else 0). Pop worse-or-equal back entries before appending i. Track the running best over all dp[i].",
        ],
    ),

    dict(
        slug="word-break-ii",
        title="Word Break II",
        day=None,
        topic="recursion",
        pattern="backtracking with memoization",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=35,
        progression_stage="variation",
        canonical_reference="LeetCode 140: Word Break II",
        path_tier="advanced",
        description=(
            "Given a string `s` and a dictionary `word_dict` of valid words, return ALL ways to segment "
            "`s` into a space-separated sequence of one or more dictionary words (order of the returned "
            "sentences does not matter)."
        ),
        constraints="1 <= len(s) <= 20; 1 <= len(word_dict) <= 1000; every word_dict entry is 1-10 lowercase letters.",
        function_signature="def word_break_ii(s, word_dict):",
        starter_code=(
            "def word_break_ii(s, word_dict):\n"
            "    # backtrack(start) returns every way to segment s[start:]. Try every\n"
            "    # possible next word (a dictionary word that s starts with, from\n"
            "    # position `start`), and for each one, recursively combine it with\n"
            "    # every way to segment the rest of the string. Memoize on `start` --\n"
            "    # the SAME suffix can be reached via many different earlier splits.\n"
            "    word_set = set(word_dict)\n"
            "    memo = {}\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n^2) states with memoization, times the branching factor for building sentences",
        expected_space_complexity="O(n^2) for the memo table plus the output",
        brute_force_approach="The same backtracking without memoization re-solves the same suffix of s over and over from different starting splits -- exponential blowup for strings with many valid segmentations sharing suffixes.",
        optimal_approach="Recursive backtrack(start): if start==len(s), the empty segmentation [[]] is the base case. Otherwise, try every end position where s[start:end] is a dictionary word, recursively get every segmentation of the rest via backtrack(end), and prepend the current word to each. Memoize on `start` alone (the return value only depends on the remaining suffix, not on how you got there).",
        common_mistakes="Memoizing on (start, path-so-far) instead of just `start` (the whole point of memoization here is that the SAME suffix, reached via different prefixes, gives the same set of remaining segmentations); forgetting the base case must be [[]] (a list containing one empty list), not [] (no segmentations) -- those mean very different things.",
        edge_cases="A string with no valid segmentation at all (returns an empty list); a string that IS itself a single dictionary word (one trivial one-word sentence); a string with many overlapping valid segmentations (stresses the memoization).",
        test_inputs=[("catsanddog", ["cat", "cats", "and", "sand", "dog"]), ("pineapplepenapple", ["apple", "pen", "applepen", "pine", "pineapple"]), ("catsandog", ["cats", "dog", "sand", "and", "cat"])],
        test_labels=[None, None, "no valid segmentation covers the entire string -- correctly returns []"],
        comparison_mode="unordered_list",
        reference_solution=(
            "def word_break_ii(s, word_dict):\n"
            "    word_set = set(word_dict)\n"
            "    memo = {}\n"
            "\n"
            "    def backtrack(start):\n"
            "        if start == len(s):\n"
            "            return [[]]\n"
            "        if start in memo:\n"
            "            return memo[start]\n"
            "        results = []\n"
            "        for end in range(start + 1, len(s) + 1):\n"
            "            word = s[start:end]\n"
            "            if word in word_set:\n"
            "                for rest in backtrack(end):\n"
            "                    results.append([word] + rest)\n"
            "        memo[start] = results\n"
            "        return results\n"
            "\n"
            "    sentences = backtrack(0)\n"
            "    return [' '.join(words) for words in sentences]\n"
        ),
        hints=[
            "This is Word Break (the yes/no version) but instead of just asking 'can this be segmented', you need to actually COLLECT every valid segmentation -- so it's backtracking that builds and returns full sentences, not just a boolean.",
            "Without memoization, the same suffix of s gets fully re-explored every time a different earlier split reaches it -- memoize backtrack(start) so each starting position's full list of possible segmentations is computed exactly once.",
            "backtrack(start): if start==len(s): return [[]]. Otherwise for each end where s[start:end] is a dictionary word, recursively call backtrack(end) and prepend s[start:end] to each returned segmentation. Memoize the whole results list per start. Finally join each segmentation's words with spaces.",
        ],
    ),

    dict(
        slug="sliding-window-median",
        title="Sliding Window Median",
        day=None,
        topic="sliding-window",
        pattern="fixed-size window with an ordered structure",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=35,
        progression_stage="variation",
        canonical_reference="LeetCode 480: Sliding Window Median",
        path_tier="advanced",
        description=(
            "Given an integer array `nums` and a window size `k`, return the median of every contiguous "
            "window of size `k` as it slides from the start of the array to the end (one median per "
            "window position)."
        ),
        constraints="1 <= k <= len(nums) <= 2000; -2^31 <= nums[i] <= 2^31 - 1.",
        function_signature="def median_sliding_window(nums, k):",
        starter_code=(
            "import bisect\n"
            "\n"
            "def median_sliding_window(nums, k):\n"
            "    # Keep a SORTED window (not the original left-to-right order -- you\n"
            "    # only need to read the middle value(s), never the original\n"
            "    # positions). bisect.insort/bisect_left let you insert the newly\n"
            "    # entering element and remove the newly exiting one in O(k) each\n"
            "    # (or O(log k) to locate, O(k) to shift), which is fine at this\n"
            "    # problem's constraints.\n"
            "    window = sorted(nums[:k])\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n*k)",
        expected_space_complexity="O(k)",
        brute_force_approach="Re-sort each window of size k from scratch as it slides -- O(n*k log k), noticeably slower than maintaining one already-sorted window incrementally.",
        optimal_approach="Maintain `window`, the current k elements in SORTED order (not original array order). Compute the median directly from the middle (or average of the two middle) values. When the window slides: use bisect to remove the element that just left (by value, not index) and bisect.insort to insert the element that just entered, keeping `window` sorted throughout.",
        common_mistakes="Removing by INDEX instead of by VALUE when the window slides (the sorted window's positions don't correspond to the original array's positions at all); recomputing the whole median from scratch with a full sort every step instead of maintaining sortedness incrementally.",
        edge_cases="k == 1 (the 'median' of each window is just that single element); k == len(nums) (only one window, spanning the whole array); duplicate values inside the window (bisect must still remove exactly one occurrence, not all of them).",
        test_inputs=[([1, 3, -1, -3, 5, 3, 6, 7], 3), ([1, 2, 3, 4, 2, 3, 1, 4, 2], 3), ([1, 2], 1), ([1, 2], 2)],
        reference_solution=(
            "import bisect\n"
            "\n"
            "def median_sliding_window(nums, k):\n"
            "    window = sorted(nums[:k])\n"
            "\n"
            "    def get_median(w):\n"
            "        n = len(w)\n"
            "        if n % 2 == 1:\n"
            "            return float(w[n // 2])\n"
            "        return (w[n // 2 - 1] + w[n // 2]) / 2.0\n"
            "\n"
            "    result = [get_median(window)]\n"
            "    for i in range(k, len(nums)):\n"
            "        window.pop(bisect.bisect_left(window, nums[i - k]))\n"
            "        bisect.insort(window, nums[i])\n"
            "        result.append(get_median(window))\n"
            "    return result\n"
        ),
        hints=[
            "You never actually need the window in its original left-to-right order -- only its SORTED order, to read off the middle value(s). Maintain that sorted copy directly instead of re-deriving it every step.",
            "bisect_left finds where a value sits in a sorted list in O(log k); pop() by that position removes it. bisect.insort inserts a new value while keeping the list sorted. Together they let a sliding window update its sorted copy without a full re-sort each time.",
            "window = sorted(nums[:k]) to start. Each slide: window.pop(bisect.bisect_left(window, the value leaving)); bisect.insort(window, the value entering). Median: middle element if k is odd, average of the two middle elements if k is even.",
        ],
    ),

    dict(
        slug="maximum-gap",
        title="Maximum Gap",
        day=None,
        topic="sorting",
        pattern="bucket sort via pigeonhole reasoning",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=30,
        progression_stage="variation",
        canonical_reference="LeetCode 164: Maximum Gap",
        path_tier="advanced",
        description=(
            "Given an integer array `nums`, return the maximum difference between two SUCCESSIVE elements "
            "in its sorted form, in O(n) time (a plain O(n log n) sort followed by a scan is a valid "
            "starting point, but the intended solution avoids comparison sorting entirely). Return 0 if "
            "the array has fewer than 2 elements."
        ),
        constraints="1 <= len(nums) <= 10^5; 0 <= nums[i] <= 10^9.",
        function_signature="def maximum_gap(nums):",
        starter_code=(
            "def maximum_gap(nums):\n"
            "    # Pigeonhole insight: with n numbers spanning a range of (max-min),\n"
            "    # if you split that range into n-1 equal-width buckets, at least one\n"
            "    # bucket must be EMPTY (n numbers, n-1 buckets... wait, n numbers into\n"
            "    # n-1 buckets guarantees a collision, not an empty bucket -- the real\n"
            "    # insight is that the maximum gap can never occur BETWEEN two numbers\n"
            "    # placed in the same bucket, only between a bucket's max and the next\n"
            "    # non-empty bucket's min).\n"
            "    n = len(nums)\n"
            "    if n < 2:\n"
            "        return 0\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n) average (bucket sort), O(n log n) if you fall back to a comparison sort",
        expected_space_complexity="O(n)",
        brute_force_approach="Sort with a comparison sort (O(n log n)) and scan adjacent differences -- perfectly correct and much simpler; the bucket-based O(n) approach below is the 'intended' optimization the problem is really testing.",
        optimal_approach="With n numbers spanning [lo, hi], bucket width = max(1, (hi-lo) // (n-1)) guarantees the maximum possible gap can never occur BETWEEN two numbers placed in the SAME bucket (each bucket's span is smaller than the guaranteed minimum possible max-gap) -- so you only need to track each bucket's min and max, then scan gaps between one bucket's max and the NEXT non-empty bucket's min.",
        common_mistakes="Trying to find the maximum gap by comparing adjacent elements WITHIN the same bucket (never necessary, and the whole point of the bucket sizing is that it can't be the answer); off-by-one in bucket_count/bucket index math when hi==lo (must special-case: all elements equal means the answer is trivially 0).",
        edge_cases="Fewer than 2 elements (0); all elements identical (0, no gap at all); exactly 2 elements (the gap is just their difference).",
        test_inputs=[([3, 6, 9, 1],), ([10],), ([1, 1, 1, 1],), ([1, 10000000],), ([9, 3, 1, 10],)],
        test_labels=[None, "fewer than 2 elements", "all elements identical", "two elements spanning a huge range", None],
        reference_solution=(
            "def maximum_gap(nums):\n"
            "    n = len(nums)\n"
            "    if n < 2:\n"
            "        return 0\n"
            "    lo, hi = min(nums), max(nums)\n"
            "    if lo == hi:\n"
            "        return 0\n"
            "    bucket_size = max(1, (hi - lo) // (n - 1))\n"
            "    bucket_count = (hi - lo) // bucket_size + 1\n"
            "    buckets_min = [None] * bucket_count\n"
            "    buckets_max = [None] * bucket_count\n"
            "    for num in nums:\n"
            "        idx = (num - lo) // bucket_size\n"
            "        if buckets_min[idx] is None or num < buckets_min[idx]:\n"
            "            buckets_min[idx] = num\n"
            "        if buckets_max[idx] is None or num > buckets_max[idx]:\n"
            "            buckets_max[idx] = num\n"
            "    result = 0\n"
            "    prev_max = lo\n"
            "    for i in range(bucket_count):\n"
            "        if buckets_min[i] is None:\n"
            "            continue\n"
            "        result = max(result, buckets_min[i] - prev_max)\n"
            "        prev_max = buckets_max[i]\n"
            "    return result\n"
        ),
        hints=[
            "A full comparison sort works and is a perfectly reasonable place to start (O(n log n), scan adjacent gaps). The deeper insight the problem is really after: with n numbers and a known min/max, you can guarantee the true maximum gap is never hiding INSIDE a small-enough bucket -- only between buckets.",
            "Size each bucket so it's guaranteed smaller than what the maximum gap must be (bucket_size = (max-min)//(n-1), at least 1). Then you only need each bucket's min and max, not every individual value inside it.",
            "Compute lo, hi, bucket_size, bucket_count. Drop every number into buckets_min[idx]/buckets_max[idx] by idx=(num-lo)//bucket_size. Then walk buckets left to right, comparing each non-empty bucket's min against the PREVIOUS non-empty bucket's max, tracking the largest such gap.",
        ],
    ),

    dict(
        slug="maximal-rectangle",
        title="Maximal Rectangle",
        day=49,
        topic="stacks",
        pattern="per-row histogram + monotonic stack",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=35,
        progression_stage="variation",
        canonical_reference="LeetCode 85: Maximal Rectangle",
        path_tier="advanced",
        description=(
            "Given a 2D binary matrix `matrix` (rows of 0/1 integers), return the area of the largest "
            "rectangle containing only 1s."
        ),
        constraints="1 <= rows, cols <= 200; matrix[i][j] is 0 or 1.",
        function_signature="def maximal_rectangle(matrix):",
        starter_code=(
            "def maximal_rectangle(matrix):\n"
            "    # Treat each ROW as the base of a histogram: heights[j] = how many\n"
            "    # consecutive 1s are stacked directly above (and including) this row\n"
            "    # at column j (resetting to 0 the instant a 0 appears). Run Largest\n"
            "    # Rectangle in Histogram on that heights array after EVERY row -- the\n"
            "    # biggest rectangle overall is the biggest histogram answer seen\n"
            "    # across all rows.\n"
            "    if not matrix or not matrix[0]:\n"
            "        return 0\n"
            "    n = len(matrix[0])\n"
            "    heights = [0] * n\n"
            "    best = 0\n"
            "    pass\n"
            "    return best\n"
        ),
        expected_time_complexity="O(rows * cols)",
        expected_space_complexity="O(cols)",
        brute_force_approach="For every possible rectangle (defined by choosing top-left and bottom-right corners), check whether it's all 1s -- O((rows*cols)^2) or worse, far too slow.",
        optimal_approach="Reduce to Largest Rectangle in Histogram, run once per row. Maintain a running heights[] array where heights[j] is the number of consecutive 1s ending at the current row in column j (heights[j] = heights[j]+1 if matrix[row][j]==1 else 0). After updating heights for a row, run the histogram algorithm on it -- the largest rectangle 'ending' at that row (using that row as its bottom edge) is exactly the histogram's answer for that heights array.",
        common_mistakes="Resetting heights fully every row instead of accumulating a RUNNING count (the whole trick is that heights[j] carries forward how many 1s have stacked so far, resetting to 0 only on an actual 0); forgetting the histogram algorithm needs to run on every row, not just the last one -- the maximal rectangle could 'end' anywhere.",
        edge_cases="A single row (degenerates to plain Largest Rectangle in Histogram); an all-0 matrix (answer 0); an all-1 matrix (answer is rows*cols, the whole matrix).",
        test_inputs=[([[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1], [1, 0, 0, 1, 0]],), ([[0]],), ([[1]],), ([[1, 1], [1, 1]],)],
        test_labels=[None, "all zeros", "single cell, all 1s", None],
        reference_solution=(
            "def maximal_rectangle(matrix):\n"
            "    if not matrix or not matrix[0]:\n"
            "        return 0\n"
            "    n = len(matrix[0])\n"
            "    heights = [0] * n\n"
            "    best = 0\n"
            "\n"
            "    def largest_rectangle(heights):\n"
            "        stack = []\n"
            "        max_area = 0\n"
            "        for i in range(len(heights) + 1):\n"
            "            h = heights[i] if i < len(heights) else 0\n"
            "            while stack and heights[stack[-1]] >= h:\n"
            "                height = heights[stack.pop()]\n"
            "                width = i if not stack else i - stack[-1] - 1\n"
            "                max_area = max(max_area, height * width)\n"
            "            stack.append(i)\n"
            "        return max_area\n"
            "\n"
            "    for row in matrix:\n"
            "        for j in range(n):\n"
            "            heights[j] = heights[j] + 1 if row[j] else 0\n"
            "        best = max(best, largest_rectangle(heights))\n"
            "    return best\n"
        ),
        hints=[
            "This directly builds on Largest Rectangle in Histogram -- the trick is realizing every ROW of the matrix can be treated as the base of its own histogram, where each bar's height is how many 1s have stacked up in that column so far.",
            "Keep a running heights[] array across rows: heights[j] becomes heights[j]+1 if the current row's column j is 1, or resets to 0 if it's 0. After updating for a row, run the histogram algorithm on the CURRENT heights[] and compare against the best area seen.",
            "For each row: for j in range(n): heights[j] = heights[j]+1 if row[j] else 0. Then best = max(best, largest_rectangle(heights)), reusing the exact same monotonic-stack histogram function from Largest Rectangle in Histogram.",
        ],
    ),

    dict(
        slug="text-justification",
        title="Text Justification",
        day=49,
        topic="strings",
        pattern="greedy line-fitting + space distribution",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=35,
        progression_stage="variation",
        canonical_reference="LeetCode 68: Text Justification",
        path_tier="advanced",
        description=(
            "Given a list of `words` and a line width `max_width`, format the text into lines that are "
            "fully (left AND right) justified to exactly `max_width` characters -- pack as many words as "
            "fit per line, distribute extra spaces as evenly as possible (extra space goes to the "
            "LEFTMOST gaps first when it can't divide evenly), except the LAST line, which is left-"
            "justified with single spaces between words and padded with trailing spaces."
        ),
        constraints="1 <= len(words) <= 300; 1 <= len(words[i]) <= 20; 1 <= max_width <= 100; every word fits within max_width alone.",
        function_signature="def full_justify(words, max_width):",
        starter_code=(
            "def full_justify(words, max_width):\n"
            "    # Greedily pack words onto a line until the NEXT word wouldn't fit\n"
            "    # (accounting for at least one space between each pair). Then\n"
            "    # distribute max_width's leftover space across the gaps between\n"
            "    # words as evenly as possible -- any remainder (spaces that don't\n"
            "    # divide evenly) goes to the leftmost gaps first.\n"
            "    result = []\n"
            "    current_line = []\n"
            "    current_len = 0\n"
            "    pass\n"
        ),
        expected_time_complexity="O(total characters across all words)",
        expected_space_complexity="O(total characters, for the output)",
        brute_force_approach="There isn't a meaningfully different 'brute force' here -- the greedy line-packing IS the natural approach; the subtlety is entirely in getting the space-distribution arithmetic exactly right, not in the algorithm's overall shape.",
        optimal_approach="Greedily add words to the current line while they fit (current_len + len(current_line) spaces-so-far + len(next_word) <= max_width). When a word wouldn't fit, justify the current line: if it has only one word, left-justify with trailing spaces; otherwise distribute (max_width - total_word_length) spaces across (word_count - 1) gaps using divmod, giving any remainder to the leftmost gaps one at a time. The very last line is always left-justified with single spaces and trailing padding, regardless of word count.",
        common_mistakes="Justifying the LAST line the same way as every other line (it must be left-justified, not space-stretched, even if it has multiple words); getting the extra-space distribution backwards (remainder spaces go to the leftmost gaps first, not spread from the right or all dumped at the end); off-by-one when checking whether a word fits (must account for at least one space before each word after the first).",
        edge_cases="A single word on the last line (or any line -- gets padded with trailing spaces, no internal justification needed since there's no gap to stretch); a line where the words exactly fill max_width with single spaces (no extra distribution needed); max_width barely fitting one very long word alone on its own line.",
        test_inputs=[
            (["This", "is", "an", "example", "of", "text", "justification."], 16),
            (["a"], 3),
            (["ab", "cd", "ef"], 8),
        ],
        comparison_mode="unordered_list",
        reference_solution=(
            "def full_justify(words, max_width):\n"
            "    result = []\n"
            "    current_line = []\n"
            "    current_len = 0\n"
            "    for word in words:\n"
            "        if current_len + len(current_line) + len(word) > max_width:\n"
            "            if len(current_line) == 1:\n"
            "                result.append(current_line[0] + ' ' * (max_width - current_len))\n"
            "            else:\n"
            "                spaces_needed = max_width - current_len\n"
            "                gaps = len(current_line) - 1\n"
            "                base, extra = divmod(spaces_needed, gaps)\n"
            "                line = ''\n"
            "                for i, w in enumerate(current_line):\n"
            "                    line += w\n"
            "                    if i < gaps:\n"
            "                        line += ' ' * (base + (1 if i < extra else 0))\n"
            "                result.append(line)\n"
            "            current_line = []\n"
            "            current_len = 0\n"
            "        current_line.append(word)\n"
            "        current_len += len(word)\n"
            "    last_line = ' '.join(current_line)\n"
            "    last_line += ' ' * (max_width - len(last_line))\n"
            "    result.append(last_line)\n"
            "    return result\n"
        ),
        hints=[
            "Pack words onto a line greedily -- keep adding the next word as long as it (plus at least one space before it) still fits within max_width. The moment it wouldn't fit, that line is done and needs to be justified before moving on.",
            "For a finished (non-last) line: one word means just pad it with trailing spaces. Multiple words means distributing (max_width - total word length) spaces across (word_count - 1) gaps -- divmod gives you the base amount per gap plus a remainder, and that remainder goes one extra space to each of the LEFTMOST gaps.",
            "current_len + len(current_line) + len(word) > max_width means the current word doesn't fit (the +len(current_line) accounts for one space before each already-placed word). On overflow: justify current_line as above, reset, then start the new line with the current word. After the loop, the final current_line is always left-justified with single spaces and trailing padding -- never space-stretched.",
        ],
    ),

    dict(
        slug="binary-tree-cameras",
        title="Binary Tree Cameras",
        day=47,
        topic="trees",
        pattern="post-order greedy with 3-state tree DP",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=35,
        progression_stage="variation",
        canonical_reference="LeetCode 968: Binary Tree Cameras",
        path_tier="advanced",
        description=(
            "You want to monitor every node of a binary tree using the minimum number of cameras. A "
            "camera placed at a node can monitor that node, its parent, and its direct children. Given the "
            "tree (level-order array, `None` for missing nodes), return the minimum number of cameras "
            "needed to monitor every node."
        ),
        constraints="1 <= number of nodes <= 1000; node values are 0.",
        function_signature="def min_camera_cover(values):",
        starter_code=(
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
            "def min_camera_cover(values):\n"
            "    root = build_tree(values)\n"
            "    cameras = [0]\n"
            "    # Post-order DFS returning one of 3 states for each node: NOT_COVERED,\n"
            "    # COVERED_NO_CAMERA, or HAS_CAMERA. A greedy rule (place a camera at\n"
            "    # a node the INSTANT any child is not-yet-covered) turns out to always\n"
            "    # be optimal, because delaying would leave that child unmonitored\n"
            "    # with no future chance to fix it from below.\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(h) recursion depth",
        brute_force_approach="Try every subset of nodes as camera placements and check coverage -- exponential, infeasible past tiny trees.",
        optimal_approach="Post-order DFS returning one of three states per subtree: 0 = not covered, 1 = covered but no camera here, 2 = has a camera here. A None child counts as state 1 (already 'covered' so it never forces its parent to place a camera). If either child is state 0, this node MUST get a camera (greedily -- there's no better time to cover that child). If either child has a camera (state 2), this node is covered by it (state 1) without needing its own. Otherwise (both children state 1), this node is NOT covered (state 0) and depends on ITS parent. After the DFS, if the root itself ends up state 0, one final camera is needed at the root.",
        common_mistakes="Treating a None (missing) child as state 0 instead of state 1 (a missing child needs no coverage at all, and treating it as uncovered would wrongly force cameras onto every leaf's parent); forgetting the special check after the full DFS -- the root has no parent to rely on, so if it comes back as state 0 it needs its own camera that the recursion alone wouldn't have placed.",
        edge_cases="A single node (needs exactly 1 camera, since nothing else can cover it); a tree where cameras alternate perfectly with parents (minimal cameras, testing the greedy state 2 propagation); a long single-child chain (tests state transitions propagating correctly up several levels).",
        test_inputs=[([0, 0, None, 0, 0, None, None, None, None],), ([0, 0, None, 0, None, 0, None, None, 0],), ([0],), ([0, None, 0, None, 0],)],
        test_labels=[None, None, "a single node -- needs exactly one camera", "a right-skewed chain of 3 nodes"],
        reference_solution=(
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
            "def min_camera_cover(values):\n"
            "    root = build_tree(values)\n"
            "    cameras = [0]\n"
            "\n"
            "    def dfs(node):\n"
            "        if not node:\n"
            "            return 1\n"
            "        left = dfs(node.left)\n"
            "        right = dfs(node.right)\n"
            "        if left == 0 or right == 0:\n"
            "            cameras[0] += 1\n"
            "            return 2\n"
            "        if left == 2 or right == 2:\n"
            "            return 1\n"
            "        return 0\n"
            "\n"
            "    if dfs(root) == 0:\n"
            "        cameras[0] += 1\n"
            "    return cameras[0]\n"
        ),
        hints=[
            "Think bottom-up (post-order): by the time you're deciding whether a node needs a camera, you already know the coverage state of both its children. A leaf's children are None -- treat that as 'already covered' so leaves themselves aren't forced to have cameras just because they have no children.",
            "The greedy rule: if either child is NOT YET covered, you must place a camera at the current node right now -- there will never be a better (lower) opportunity to cover that child. If neither child is uncovered but one already HAS a camera, the current node is covered for free. Otherwise, the current node itself is left uncovered, waiting on its own parent.",
            "dfs(node): if node is None, return 1 (covered). left, right = dfs(node.left), dfs(node.right). If left==0 or right==0: cameras+=1; return 2. Elif left==2 or right==2: return 1. Else: return 0. After calling dfs(root), if it returned 0, add one final camera (the root has no parent to rely on).",
        ],
    ),

    dict(
        slug="minimum-window-subsequence",
        title="Minimum Window Subsequence",
        day=None,
        topic="two-pointer",
        pattern="expand-then-backtrack two-pointer scan",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=35,
        progression_stage="variation",
        canonical_reference="LeetCode 727: Minimum Window Subsequence",
        path_tier="advanced",
        description=(
            "Given strings `s` and `t`, return the minimum-length substring `w` of `s` such that `t` is a "
            "SUBSEQUENCE of `w` (t's characters appear in `w` in order, not necessarily contiguously). "
            "Return `\"\"` if no such window exists. Unlike Minimum Window Substring, order matters here -- "
            "t's characters must appear in exactly t's order within the window."
        ),
        constraints="1 <= len(s), len(t) <= 2*10^4.",
        function_signature="def min_window_subsequence(s, t):",
        starter_code=(
            "def min_window_subsequence(s, t):\n"
            "    # Two passes per candidate window: scan FORWARD from some start to\n"
            "    # find the first place t is fully matched as a subsequence (greedily\n"
            "    # consuming the earliest possible match for each character), then\n"
            "    # scan BACKWARD from there to find the LATEST possible start that\n"
            "    # still keeps t matched -- that backward pass is what makes the\n"
            "    # window minimal, since the greedy forward match isn't always tight.\n"
            "    best_start, best_len = -1, float('inf')\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n * m) worst case (n = len(s), m = len(t)), though it behaves much closer to O(n) in practice",
        expected_space_complexity="O(1)",
        brute_force_approach="Check every possible substring of s for whether t is a subsequence of it -- O(n^2 * m), far too slow.",
        optimal_approach="Two-pointer, two-pass per found match: scan forward through s matching t's characters greedily (as soon as s[i]==t[j], advance both). Once t is fully matched (found a valid window ending at some index), scan BACKWARD from there matching t's characters in reverse to find the tightest possible start for THIS particular ending point. Record the window if it's the best so far, then continue the forward scan from just past this window's start to look for the next candidate.",
        common_mistakes="Only doing the forward greedy match and using its start directly (the greedy forward scan finds *a* valid window, but not necessarily the TIGHTEST one ending at that point -- the backward pass is what shrinks it to the true minimum for that ending index); forgetting to resume the forward scan from the right place afterward (must continue looking for further, possibly better, matches rather than stopping at the first one found).",
        edge_cases="t is a single character (the answer is just that character, wherever it first appears); t doesn't appear as a subsequence anywhere in s (return \"\"); s equals t exactly (the whole string is the minimal window).",
        test_inputs=[("abcdebdde", "bde"), ("abc", "ac"), ("abc", "d"), ("a", "a"), ("cnhczmccqouqadqtmiecczna", "mm")],
        test_labels=[None, None, "t never appears as a subsequence -- correctly returns \"\"", "single character", "t never appears as a subsequence (repeated letters trap) -- correctly returns \"\""],
        reference_solution=(
            "def min_window_subsequence(s, t):\n"
            "    best_start, best_len = -1, float('inf')\n"
            "    n, m = len(s), len(t)\n"
            "    i = 0\n"
            "    while i < n:\n"
            "        j = 0\n"
            "        while i < n and j < m:\n"
            "            if s[i] == t[j]:\n"
            "                j += 1\n"
            "            i += 1\n"
            "        if j < m:\n"
            "            break\n"
            "        end = i\n"
            "        i -= 1\n"
            "        j -= 1\n"
            "        while j >= 0:\n"
            "            if s[i] == t[j]:\n"
            "                j -= 1\n"
            "            i -= 1\n"
            "        i += 1\n"
            "        if end - i < best_len:\n"
            "            best_len = end - i\n"
            "            best_start = i\n"
            "        i += 1\n"
            "    return s[best_start:best_start + best_len] if best_start != -1 else ''\n"
        ),
        hints=[
            "Unlike Minimum Window Substring, order matters -- t must appear as an in-order subsequence, not just have all its characters present. That means a simple character-count hashmap approach doesn't apply here.",
            "First scan forward, greedily matching t's characters against s one at a time (advance s's pointer always, advance t's pointer only on a match). The moment all of t is matched, you've found A valid window -- but it might not be the tightest one ending there.",
            "From that match's end, scan BACKWARD matching t in reverse to find the latest possible start that still fully matches t -- that backward-found start is the true minimal window for this end point. Record it if it beats the best so far, then resume the forward scan just past this window's start to look for further matches.",
        ],
    ),

    # ---------------------------------------------------------------
    # Mandatory: brand-new 'greedy' topic, full Easy/Medium/Hard/Complex
    # spread. The 4 existing greedy-flavored problems (max-area-container,
    # jump-game, boats-to-save-people, task-scheduler) deliberately keep
    # their current topic (see deliverables/EXPANSION_PLAN.md) rather than
    # being reassigned here -- reassigning them would move their curriculum
    # day placement / concept-lesson auto-linking, which the approved scope
    # says not to touch without a genuine regression. They're referenced by
    # name/link in the new Greedy concept lesson's prose instead.
    # ---------------------------------------------------------------

    dict(
        slug="assign-cookies",
        title="Assign Cookies",
        day=None,
        topic="greedy",
        pattern="greedy two-pointer matching",
        difficulty="Easy",
        interview_priority="Important",
        estimated_solve_minutes=15,
        progression_stage="core",
        canonical_reference="LeetCode 455: Assign Cookies",
        path_tier="extended",
        description=(
            "Each child `i` has a greed factor `g[i]` (the minimum cookie size that will satisfy them), "
            "and each cookie `j` has a size `s[j]`. Each cookie can satisfy at most one child, and a child "
            "is satisfied only if given a cookie of size >= their greed factor. Return the maximum number "
            "of content (satisfied) children."
        ),
        constraints="1 <= len(g), len(s) <= 3.4*10^4; 1 <= g[i], s[j] <= 2^31 - 1.",
        function_signature="def find_content_children(g, s):",
        starter_code=(
            "def find_content_children(g, s):\n"
            "    # Sort both. Try to satisfy the LEAST greedy child first with the\n"
            "    # SMALLEST cookie that can satisfy them -- giving a bigger cookie to\n"
            "    # an easily-satisfied child would only waste a cookie that a\n"
            "    # greedier child might have needed.\n"
            "    g = sorted(g)\n"
            "    s = sorted(s)\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n log n)",
        expected_space_complexity="O(1) extra (excluding the sort)",
        brute_force_approach="Try every way to assign cookies to children (a matching/assignment search) -- exponential, and completely unnecessary once you notice sorting exposes the greedy structure.",
        optimal_approach="Sort both g and s ascending. Walk both with two pointers: if the current smallest unassigned cookie satisfies the current least-greedy unsatisfied child, that's a match -- give it to them and advance both pointers. Otherwise this cookie is too small for ANY remaining child (they're all at least as greedy), so advance only the cookie pointer.",
        common_mistakes="Trying to match the biggest cookie to the biggest greed factor first (works, but is a different, less intuitive greedy direction than smallest-to-smallest, and easier to get the pointer-advancing logic backwards on); advancing the child pointer without actually having satisfied them (a child pointer should only advance on an actual successful match).",
        edge_cases="More cookies than children, or vice versa (extras are simply never used); no cookie can satisfy any child at all (answer 0); every cookie exactly meets every child's greed factor.",
        test_inputs=[([1, 2, 3], [1, 1]), ([1, 2], [1, 2, 3]), ([10, 9, 8, 7], [5, 6, 7, 8])],
        reference_solution=(
            "def find_content_children(g, s):\n"
            "    g = sorted(g)\n"
            "    s = sorted(s)\n"
            "    i = j = 0\n"
            "    while i < len(g) and j < len(s):\n"
            "        if s[j] >= g[i]:\n"
            "            i += 1\n"
            "        j += 1\n"
            "    return i\n"
        ),
        hints=[
            "Sorting both lists turns this into a matching problem you can solve greedily left to right, instead of searching over assignments.",
            "Always try to satisfy the LEAST greedy remaining child with the SMALLEST cookie that could work -- if that cookie doesn't even satisfy the least greedy child, it can't satisfy anyone left (they're all at least as greedy), so it's simply wasted.",
            "i=j=0 (i indexes g, j indexes s, both sorted). While both in range: if s[j] >= g[i], that's a match -- increment i (and always increment j, since this cookie is now used either way). Return i (the count of matched/satisfied children).",
        ],
    ),

    dict(
        slug="jump-game-ii",
        title="Jump Game II",
        day=None,
        topic="greedy",
        pattern="greedy reachability, minimize jump count",
        difficulty="Medium",
        interview_priority="Core",
        estimated_solve_minutes=25,
        progression_stage="core",
        canonical_reference="LeetCode 45: Jump Game II",
        path_tier="extended",
        description=(
            "Given an array where `nums[i]` is the maximum jump length from index i, starting at index 0, "
            "return the MINIMUM number of jumps needed to reach the last index (unlike Jump Game, which "
            "only asks whether it's reachable -- here you also have to minimize how many jumps it takes, "
            "and you're guaranteed the last index is always reachable)."
        ),
        constraints="1 <= len(nums) <= 10^4; 0 <= nums[i] <= 1000; the last index is always reachable.",
        function_signature="def jump(nums):",
        starter_code=(
            "def jump(nums):\n"
            "    # Think in terms of 'levels', like BFS on an implicit graph: from your\n"
            "    # CURRENT jump's reach, track the FARTHEST index reachable with one\n"
            "    # more jump. The instant you've scanned up to the current jump's edge,\n"
            "    # you must commit to a new jump -- and the greedy choice is: you\n"
            "    # already know the farthest that jump can reach.\n"
            "    jumps = 0\n"
            "    current_end = 0\n"
            "    farthest = 0\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(1)",
        brute_force_approach="BFS/DP where dp[i] = minimum jumps to reach index i, trying every possible previous jump into i -- O(n^2) worst case.",
        optimal_approach="Greedy 'implicit BFS levels': current_end marks the farthest index reachable with the jumps used SO FAR; farthest tracks the farthest index reachable with ONE MORE jump, updated as you scan. The moment your scan index reaches current_end, you must take that extra jump (jumps += 1) and current_end becomes farthest -- you're now 'inside' the next level.",
        common_mistakes="Incrementing jumps every time farthest is updated instead of only when the scan index actually reaches current_end (that's the real signal a new jump is being committed to); off-by-one from Jump Game's loop bound -- this one stops scanning BEFORE the last index (range(len(nums)-1)), since you never need to 'commit' a jump once you've already arrived.",
        edge_cases="A single-element array (0 jumps needed, already there); every element is exactly the minimum needed to barely reach the next one (every index is its own 'level'); a large nums[0] that reaches the end in a single jump.",
        test_inputs=[([2, 3, 1, 1, 4],), ([2, 3, 0, 1, 4],), ([1],), ([1, 2, 1, 1, 1],), ([5, 1, 1, 1, 1],)],
        reference_solution=(
            "def jump(nums):\n"
            "    jumps = 0\n"
            "    current_end = 0\n"
            "    farthest = 0\n"
            "    for i in range(len(nums) - 1):\n"
            "        farthest = max(farthest, i + nums[i])\n"
            "        if i == current_end:\n"
            "            jumps += 1\n"
            "            current_end = farthest\n"
            "    return jumps\n"
        ),
        hints=[
            "Think of it like BFS spreading outward in 'levels' from index 0, where each level represents 'everything reachable in exactly k jumps' -- you don't need to track the whole level explicitly, just its farthest edge.",
            "As you scan left to right, keep extending `farthest` (the best reach if you take one more jump from anywhere you've scanned so far in this level). The moment your scan position reaches `current_end` (the edge of the CURRENT level), you're forced to commit to the next jump.",
            "For i in range(len(nums)-1): farthest = max(farthest, i+nums[i]). If i == current_end: jumps += 1; current_end = farthest. Return jumps once the loop (which stops one short of the last index) finishes.",
        ],
    ),

    dict(
        slug="candy",
        title="Candy",
        day=48,
        topic="greedy",
        pattern="two-pass greedy local comparison",
        difficulty="Hard",
        interview_priority="Optional",
        estimated_solve_minutes=30,
        progression_stage="core",
        canonical_reference="LeetCode 135: Candy",
        path_tier="advanced",
        description=(
            "There are `n` children standing in a line, each with a rating in `ratings`. You must give "
            "each child at least 1 candy, and any child with a higher rating than an immediate neighbor "
            "must get MORE candies than that neighbor. Return the minimum total candies needed."
        ),
        constraints="1 <= n <= 2*10^4; 0 <= ratings[i] <= 2*10^4.",
        function_signature="def candy(ratings):",
        starter_code=(
            "def candy(ratings):\n"
            "    # The 'higher rating than a neighbor -> more candy' rule applies in\n"
            "    # BOTH directions at once, which is exactly what makes one single pass\n"
            "    # insufficient. Two passes, each enforcing the rule against only ONE\n"
            "    # neighbor at a time, is what makes this tractable.\n"
            "    n = len(ratings)\n"
            "    candies = [1] * n\n"
            "    pass\n"
            "    return sum(candies)\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(n)",
        brute_force_approach="Repeatedly scan and bump any child violating the rule relative to either neighbor, looping until no violations remain -- correct but potentially many passes before it stabilizes, instead of exactly two.",
        optimal_approach="Start every child at 1 candy. Left-to-right pass: if ratings[i] > ratings[i-1], candies[i] = candies[i-1] + 1 (only enforces the LEFT-neighbor rule). Right-to-left pass: if ratings[i] > ratings[i+1], candies[i] = max(candies[i], candies[i+1] + 1) (enforces the RIGHT-neighbor rule, taking the max so the left pass's result is never accidentally lowered). Sum the result.",
        common_mistakes="Only doing a single left-to-right pass (fails whenever a rating peak needs more candy than its RIGHT neighbor, which a left-to-right-only pass can never see coming); overwriting instead of taking max() on the second pass (can wrongly undo a valid, larger value the first pass already established).",
        edge_cases="All ratings equal (every child gets exactly 1 candy, minimum possible); strictly increasing or strictly decreasing ratings (one direction dominates, stress-tests each pass individually); a single 'peak' in the middle needing extra candy relative to BOTH neighbors.",
        test_inputs=[([1, 0, 2],), ([1, 2, 2],), ([1, 3, 4, 5, 2],), ([1],), ([1, 1, 1],)],
        reference_solution=(
            "def candy(ratings):\n"
            "    n = len(ratings)\n"
            "    candies = [1] * n\n"
            "    for i in range(1, n):\n"
            "        if ratings[i] > ratings[i - 1]:\n"
            "            candies[i] = candies[i - 1] + 1\n"
            "    for i in range(n - 2, -1, -1):\n"
            "        if ratings[i] > ratings[i + 1]:\n"
            "            candies[i] = max(candies[i], candies[i + 1] + 1)\n"
            "    return sum(candies)\n"
        ),
        hints=[
            "The rule compares each child against BOTH neighbors at once, which makes a single left-to-right (or right-to-left) pass insufficient on its own -- a rating 'peak' needs to satisfy both sides.",
            "Split it into two independent passes, each only enforcing the rule against ONE direction: left-to-right only checks 'am I greater than the person to my LEFT', right-to-left only checks 'am I greater than the person to my RIGHT'.",
            "candies = [1]*n. Left-to-right: if ratings[i] > ratings[i-1]: candies[i] = candies[i-1]+1. Right-to-left (i from n-2 down to 0): if ratings[i] > ratings[i+1]: candies[i] = max(candies[i], candies[i+1]+1) -- the max() is essential so this pass never shrinks what the first pass already guaranteed.",
        ],
    ),

    dict(
        slug="course-schedule-iii",
        title="Course Schedule III",
        day=49,
        topic="greedy",
        pattern="greedy scheduling with a max-heap of taken durations",
        difficulty="Complex",
        interview_priority="Optional",
        estimated_solve_minutes=35,
        progression_stage="variation",
        canonical_reference="LeetCode 630: Course Schedule III",
        path_tier="advanced",
        description=(
            "You're given `courses`, where `courses[i] = [duration, deadline]` means the course takes "
            "`duration` days and must be FINISHED by day `deadline` (you can only take one course at a "
            "time, starting the next immediately after finishing the previous). Return the maximum number "
            "of courses you can take."
        ),
        constraints="1 <= len(courses) <= 10^4; 1 <= duration <= deadline <= 10^4.",
        function_signature="def schedule_course(courses):",
        starter_code=(
            "import heapq\n"
            "\n"
            "def schedule_course(courses):\n"
            "    # Sort by deadline -- always consider the most urgent course next.\n"
            "    # Greedily take every course you can (accumulating time taken so\n"
            "    # far). The moment you'd MISS a deadline, you don't just skip the new\n"
            "    # course -- you retroactively drop whichever ALREADY-taken course cost\n"
            "    # the most time, if doing so is what's actually blocking you (a\n"
            "    # max-heap of taken durations makes 'the most expensive course so\n"
            "    # far' instantly available).\n"
            "    courses.sort(key=lambda c: c[1])\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n log n)",
        expected_space_complexity="O(n)",
        brute_force_approach="Try every subset of courses and check whether some ordering of it meets all deadlines -- exponential, infeasible past a handful of courses.",
        optimal_approach="Sort courses by deadline (most urgent first). Greedily attempt to take each course, adding its duration to a running total time. If total time ever exceeds the current course's deadline, it doesn't necessarily mean skip THIS course -- instead, compare it against the LONGEST-duration course taken so far (tracked in a max-heap): if the current course is shorter than that longest one, swap them (drop the longest, keep the current), since that strictly reduces total time used while keeping the same COUNT of courses taken. The final answer is simply how many courses ended up in the heap.",
        common_mistakes="Simply skipping any course that would blow the deadline instead of considering whether it should REPLACE a longer course already taken (a shorter course is always at least as good to keep, since it frees up more room for future courses, without reducing the count taken); forgetting to sort by deadline first (the greedy exchange argument only works when courses are considered in deadline order).",
        edge_cases="A single course that fits exactly at its deadline; a course that could never be taken alone (duration > deadline, always excluded); many courses with the same deadline (order among ties doesn't affect the final count).",
        test_inputs=[([[100, 200], [200, 1300], [1000, 1250], [2000, 3200]],), ([[1, 2]],), ([[3, 2], [4, 3]],), ([[5, 5], [4, 6], [2, 6]],)],
        test_labels=[None, None, "every course individually exceeds feasibility once combined -- answer 0", None],
        reference_solution=(
            "import heapq\n"
            "\n"
            "def schedule_course(courses):\n"
            "    courses.sort(key=lambda c: c[1])\n"
            "    heap = []\n"
            "    time = 0\n"
            "    for duration, deadline in courses:\n"
            "        heapq.heappush(heap, -duration)\n"
            "        time += duration\n"
            "        if time > deadline:\n"
            "            time += heapq.heappop(heap)\n"
            "    return len(heap)\n"
        ),
        hints=[
            "Process courses in deadline order -- the most urgent commitments have to be decided about first, which is what makes a greedy, non-backtracking approach valid here.",
            "Tentatively take every course, tracking total time spent. If total time ever exceeds the current deadline, don't just refuse the new course -- ask whether swapping OUT the single longest-duration course taken so far (in favor of keeping the current shorter one) would fix things, since that keeps the same count of courses while freeing up time.",
            "Sort by deadline. Keep a max-heap (negate durations) of taken courses' durations and a running `time`. For each course: push -duration, time += duration. If time > deadline: time += heapq.heappop(heap) (removes the longest course, since it was pushed negated -- adding a negative number back subtracts it from time). Return len(heap) at the end.",
        ],
    ),

    # ---------------------------------------------------------------
    # Discretionary (15): highest-value remaining interview patterns and
    # curriculum-evidenced gaps (see EXPANSION_PLAN.md for the reasoning
    # behind each pick, e.g. Day 41's lesson title promising an LIS
    # problem that didn't exist until this one).
    # ---------------------------------------------------------------

    dict(
        slug="longest-increasing-subsequence",
        title="Longest Increasing Subsequence",
        day=None,
        topic="dynamic-programming",
        pattern="patience sorting / binary search on tails",
        difficulty="Medium",
        interview_priority="Core",
        estimated_solve_minutes=25,
        progression_stage="core",
        canonical_reference="LeetCode 300: Longest Increasing Subsequence",
        path_tier="extended",
        description=(
            "Given an integer array `nums`, return the length of the longest STRICTLY increasing "
            "subsequence (elements don't need to be contiguous, but must keep their relative order)."
        ),
        constraints="1 <= len(nums) <= 2500; -10^4 <= nums[i] <= 10^4.",
        function_signature="def length_of_lis(nums):",
        starter_code=(
            "def length_of_lis(nums):\n"
            "    # tails[k] = the SMALLEST possible tail value of any increasing\n"
            "    # subsequence of length k+1 found so far. tails is always sorted, so\n"
            "    # binary search finds where each new number belongs: it either\n"
            "    # extends the longest subsequence found so far, or improves\n"
            "    # (lowers) an existing tail, keeping future extensions easier.\n"
            "    tails = []\n"
            "    pass\n"
            "    return len(tails)\n"
        ),
        expected_time_complexity="O(n log n) with binary search; O(n^2) with the simpler DP",
        expected_space_complexity="O(n)",
        brute_force_approach="dp[i] = length of the longest increasing subsequence ENDING at index i = 1 + max(dp[j] for j < i where nums[j] < nums[i]) -- correct and much easier to reason about, but O(n^2).",
        optimal_approach="Maintain `tails`, where tails[k] is the smallest tail value achievable for an increasing subsequence of length k+1, kept sorted as you go. For each new number, binary search for its position in tails: if it extends past the end, it genuinely grows the longest subsequence found so far (append it); otherwise it REPLACES the first tail >= it, which doesn't change the current best length but keeps a smaller tail available for future extensions. The final length of `tails` is the answer -- note tails itself is not necessarily a real subsequence, only its LENGTH is meaningful.",
        common_mistakes="Assuming `tails` IS the actual longest increasing subsequence found (it's not -- it's a bookkeeping structure that only tracks the best possible TAIL VALUE per length, the real subsequence isn't reconstructed by this approach without extra bookkeeping); using a non-strict comparison (bisect_right instead of bisect_left) which would silently solve the non-decreasing variant instead of the strictly-increasing one asked for here.",
        edge_cases="Strictly increasing array already (answer is the full length); strictly decreasing array (answer is 1, every subsequence of length > 1 is impossible); all elements equal (answer is 1, since the subsequence must be STRICTLY increasing).",
        test_inputs=[([10, 9, 2, 5, 3, 7, 101, 18],), ([0, 1, 0, 3, 2, 3],), ([7, 7, 7, 7],), ([1, 2, 3, 4],), ([4, 3, 2, 1],)],
        reference_solution=(
            "import bisect\n"
            "\n"
            "def length_of_lis(nums):\n"
            "    tails = []\n"
            "    for n in nums:\n"
            "        idx = bisect.bisect_left(tails, n)\n"
            "        if idx == len(tails):\n"
            "            tails.append(n)\n"
            "        else:\n"
            "            tails[idx] = n\n"
            "    return len(tails)\n"
        ),
        hints=[
            "Start with the simpler O(n^2) idea to build intuition: dp[i] = longest increasing subsequence ending exactly at index i, built from every valid dp[j] with a smaller value at an earlier index. The faster approach below builds on the SAME idea, just tracked differently.",
            "Instead of tracking a subsequence ending at every index, track the smallest possible TAIL value for every achievable LENGTH so far, in a list kept sorted as you go (`tails`). A new number either extends this list (a genuinely longer subsequence exists now) or replaces an existing tail with something smaller (same best length, but easier to extend later).",
            "For each n in nums: idx = bisect_left(tails, n). If idx == len(tails): tails.append(n) (n extends the longest subsequence found so far). Else: tails[idx] = n (n improves an existing tail). Return len(tails) -- the count of tails IS the answer length, even though tails itself isn't a real subsequence.",
        ],
    ),

    dict(
        slug="non-overlapping-intervals",
        title="Non-overlapping Intervals",
        day=46,
        topic="arrays",
        pattern="sort by end, greedy interval scheduling",
        difficulty="Medium",
        interview_priority="Core",
        estimated_solve_minutes=20,
        progression_stage="variation",
        canonical_reference="LeetCode 435: Non-overlapping Intervals",
        path_tier="extended",
        description=(
            "Given an array of intervals `[start, end]`, return the minimum number of intervals you'd need "
            "to remove so that none of the remaining intervals overlap (touching at a single point, i.e. "
            "one interval's end equals another's start, does NOT count as overlapping)."
        ),
        constraints="1 <= len(intervals) <= 10^5; intervals[i].length == 2.",
        function_signature="def erase_overlap_intervals(intervals):",
        starter_code=(
            "def erase_overlap_intervals(intervals):\n"
            "    # Sort by END time (not start!). Greedily keep an interval whenever it\n"
            "    # starts at or after the previously KEPT interval's end -- otherwise\n"
            "    # it overlaps, and you should always be the one removed, since the\n"
            "    # interval that ends EARLIEST leaves the most room for everything\n"
            "    # still to come.\n"
            "    intervals.sort(key=lambda x: x[1])\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n log n)",
        expected_space_complexity="O(1) extra",
        brute_force_approach="Try every subset of intervals to keep and check which largest subset has no overlaps -- exponential.",
        optimal_approach="This is classic interval scheduling: sort by END time. Greedily keep the interval with the earliest end whenever it doesn't overlap the last KEPT interval (start >= previous kept end); whenever the next interval DOES overlap, it must be the one removed (never the previously kept one), because the already-kept interval ends earlier and can only leave MORE room for future intervals, never less.",
        common_mistakes="Sorting by START instead of END (this specific greedy exchange argument only holds when you process intervals in order of when they finish, not when they begin); when an overlap is found, removing the WRONG interval (accidentally 'keeping' the later-ending one and discarding the earlier-ending one -- always keep the earlier end).",
        edge_cases="No intervals overlap at all (answer 0); every interval overlaps every other (answer len(intervals) - 1, only one survives); intervals that merely touch at a single point (end of one equals start of next -- NOT an overlap, both can be kept).",
        test_inputs=[([[1, 2], [2, 3], [3, 4], [1, 3]],), ([[1, 2], [1, 2], [1, 2]],), ([[1, 2], [2, 3]],)],
        reference_solution=(
            "def erase_overlap_intervals(intervals):\n"
            "    intervals.sort(key=lambda x: x[1])\n"
            "    count = 0\n"
            "    prev_end = float('-inf')\n"
            "    for start, end in intervals:\n"
            "        if start >= prev_end:\n"
            "            prev_end = end\n"
            "        else:\n"
            "            count += 1\n"
            "    return count\n"
        ),
        hints=[
            "This is the classic 'activity selection' scheduling problem in disguise -- minimizing removals to eliminate overlaps is the same as maximizing how many intervals you can keep.",
            "Sort by END time specifically (not start). Greedily keeping whichever already-kept interval ends earliest always leaves at least as much room for the rest as any other choice would -- that's the exchange argument that makes this greedy approach provably optimal.",
            "Sort by end. Track prev_end (starts at -infinity). For each interval: if start >= prev_end, keep it (update prev_end = end). Otherwise it overlaps the last kept interval -- count it as removed, and do NOT update prev_end (the earlier-ending interval you already kept is still the better anchor).",
        ],
    ),

    dict(
        slug="gas-station",
        title="Gas Station",
        day=44,
        topic="greedy",
        pattern="single-pass greedy with a running deficit",
        difficulty="Medium",
        interview_priority="Important",
        estimated_solve_minutes=20,
        progression_stage="variation",
        canonical_reference="LeetCode 134: Gas Station",
        path_tier="extended",
        description=(
            "There are `n` gas stations in a circle. Starting at station `i` with an empty tank, you gain "
            "`gas[i]` fuel and spend `cost[i]` fuel to reach the next station. Return the starting station "
            "index that lets you complete the full circuit (guaranteed unique if it exists), or -1 if no "
            "such start exists."
        ),
        constraints="1 <= len(gas) == len(cost) <= 10^5; 0 <= gas[i], cost[i] <= 10^4.",
        function_signature="def can_complete_circuit(gas, cost):",
        starter_code=(
            "def can_complete_circuit(gas, cost):\n"
            "    # Two facts make this a single greedy pass: (1) a solution exists at\n"
            "    # all only if total gas >= total cost overall. (2) if your running\n"
            "    # tank ever goes negative starting from some candidate start, NONE of\n"
            "    # the stations between that start and the point of failure could have\n"
            "    # worked either -- so you can safely jump your candidate start past\n"
            "    # the failure point and keep going, in one single pass.\n"
            "    total = 0\n"
            "    tank = 0\n"
            "    start = 0\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(1)",
        brute_force_approach="Try starting from every station and simulate the full circuit to check feasibility -- O(n^2).",
        optimal_approach="Walk the stations once, tracking a running tank (gas[i]-cost[i] accumulated since the current candidate start) and a running total across the WHOLE circuit. Whenever the tank goes negative, the current candidate start (and every station between it and here) is provably impossible -- reset the candidate start to the next station and reset the tank to 0. At the end, if total >= 0, the last candidate start is guaranteed to work; otherwise no valid start exists.",
        common_mistakes="Not realizing WHY skipping straight past every intermediate failed station is valid (it relies on a real proof -- any station between the old start and the failure point would run out of gas even sooner, since it inherits a smaller or equal deficit) -- without that insight it's tempting to (incorrectly) re-try every single station individually; forgetting the final total >= 0 check (a candidate start can 'survive' to the end of the scan without the ENTIRE circuit actually being completable, unless total gas covers total cost overall).",
        edge_cases="Total gas exactly equal to total cost (a solution exists, using every drop); total gas less than total cost (no solution, must return -1); the answer is index 0 itself (no reset ever needed).",
        test_inputs=[([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]), ([2, 3, 4], [3, 4, 3]), ([5, 1, 2, 3, 4], [4, 4, 1, 5, 1])],
        reference_solution=(
            "def can_complete_circuit(gas, cost):\n"
            "    total = 0\n"
            "    tank = 0\n"
            "    start = 0\n"
            "    for i in range(len(gas)):\n"
            "        diff = gas[i] - cost[i]\n"
            "        total += diff\n"
            "        tank += diff\n"
            "        if tank < 0:\n"
            "            start = i + 1\n"
            "            tank = 0\n"
            "    return start if total >= 0 else -1\n"
        ),
        hints=[
            "First check the easy necessary condition: if total gas across the whole circuit is less than total cost, no starting point can possibly work, full stop.",
            "As you scan and your running tank (since the current candidate start) goes negative, none of the stations you just passed through could have been a valid start either -- each of them handed off a tank that was already too small, so jumping your candidate straight to the next station after the failure is always safe, never a missed opportunity.",
            "total=tank=0, start=0. For each i: diff=gas[i]-cost[i]; total+=diff; tank+=diff. If tank<0: start=i+1, tank=0. After the loop, return start if total>=0 else -1.",
        ],
    ),

    dict(
        slug="partition-labels",
        title="Partition Labels",
        day=None,
        topic="greedy",
        pattern="greedy window extension via last-occurrence tracking",
        difficulty="Medium",
        interview_priority="Important",
        estimated_solve_minutes=20,
        progression_stage="variation",
        canonical_reference="LeetCode 763: Partition Labels",
        path_tier="extended",
        description=(
            "Given a string `s`, partition it into as many parts as possible so that each letter appears "
            "in at most one part, and return the list of each part's length. Parts must be formed from "
            "contiguous substrings covering the entire string."
        ),
        constraints="1 <= len(s) <= 500; s is lowercase English letters.",
        function_signature="def partition_labels(s):",
        starter_code=(
            "def partition_labels(s):\n"
            "    # First find every character's LAST occurrence index. Then scan left\n"
            "    # to right, extending the current partition's boundary to cover the\n"
            "    # last occurrence of every character seen so far in it. The instant\n"
            "    # your scan position reaches that boundary, the partition is complete\n"
            "    # -- nothing still inside it needs to reappear later.\n"
            "    last = {c: i for i, c in enumerate(s)}\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(1) (bounded alphabet)",
        brute_force_approach="Try every possible set of cut points and check whether each resulting part is 'clean' (no character split across two parts) -- exponential in the number of possible cuts.",
        optimal_approach="Precompute each character's LAST index in s. Scan left to right maintaining `end` = the farthest index the current partition must extend to (the max of every character's last-occurrence seen so far in this partition). When the scan position reaches `end`, the partition can close -- record its length and start a new one.",
        common_mistakes="Only checking a character's FIRST occurrence when deciding partition boundaries (the partition needs to extend to the LAST occurrence, since that's what determines when it's finally safe to close); forgetting the current character's own last-occurrence must be folded into `end` as you scan, not just characters seen before it.",
        edge_cases="Every character appears exactly once (n single-character partitions); the whole string uses characters that only ever appear together (one single partition covering everything); repeated characters scattered far apart forcing one very large partition.",
        test_inputs=[("ababcbacadefegdehijhklij",), ("eccbbbbdec",), ("a",), ("abab",)],
        reference_solution=(
            "def partition_labels(s):\n"
            "    last = {c: i for i, c in enumerate(s)}\n"
            "    result = []\n"
            "    start = end = 0\n"
            "    for i, c in enumerate(s):\n"
            "        end = max(end, last[c])\n"
            "        if i == end:\n"
            "            result.append(end - start + 1)\n"
            "            start = i + 1\n"
            "    return result\n"
        ),
        hints=[
            "A partition can only close once you're certain nothing inside it will reappear later in the string -- which means you need to know, for every character, the LAST place it shows up.",
            "Precompute last-occurrence indices with a single pass. Then scan again, tracking the current partition's required end (the max last-occurrence among everything seen in it so far). The moment your scan position catches up to that required end, the partition is safe to close.",
            "last = {c: i for i, c in enumerate(s)}. start=end=0. For i, c in enumerate(s): end = max(end, last[c]). If i == end: record length end-start+1, then start = i+1 for the next partition.",
        ],
    ),

    dict(
        slug="word-search",
        title="Word Search",
        day=45,
        topic="recursion",
        pattern="grid backtracking with visited-marking",
        difficulty="Medium",
        interview_priority="Core",
        estimated_solve_minutes=25,
        progression_stage="variation",
        canonical_reference="LeetCode 79: Word Search",
        path_tier="extended",
        description=(
            "Given an `m x n` grid of characters `board` and a string `word`, return True if `word` can be "
            "formed by a path of adjacent cells (up/down/left/right, no diagonal, no cell reused within one "
            "path)."
        ),
        constraints="1 <= m, n <= 6; 1 <= len(word) <= 15.",
        function_signature="def exist(board, word):",
        starter_code=(
            "def exist(board, word):\n"
            "    # From every starting cell, backtrack: does board[r][c] match the\n"
            "    # NEXT needed letter? If so, temporarily mark it used (so the path\n"
            "    # can't reuse it) and recurse into all 4 neighbors for the letter\n"
            "    # after that -- then UNDO the marking on the way back out, so other\n"
            "    # starting points/paths can still use this cell.\n"
            "    rows, cols = len(board), len(board[0])\n"
            "    pass\n"
        ),
        expected_time_complexity="O(m*n*4^L) worst case, L = len(word)",
        expected_space_complexity="O(L) recursion depth",
        brute_force_approach="There isn't a meaningfully simpler approach -- backtracking IS the natural approach here; the only real choice is how you mark/unmark visited cells.",
        optimal_approach="Try every cell as a potential starting point. Recursive backtrack(r, c, i): fails immediately if out of bounds or board[r][c] != word[i]; succeeds if i has reached the end of word. Otherwise, temporarily mark board[r][c] as used (e.g. overwrite with a sentinel character), recurse into all 4 neighbors looking for word[i+1], then restore board[r][c] before returning (regardless of the result) so other paths can still use that cell.",
        common_mistakes="Forgetting to UNDO the visited-marking after backtracking out of a cell (a cell used by one failed path attempt must become available again for a different path attempt, or even a different starting cell entirely); using a separate visited set instead of mutating the board in place (works too, but is easy to forget to update consistently -- in-place marking/unmarking is simpler to get right here given the small grid size).",
        edge_cases="The word's first letter doesn't appear anywhere in the grid (immediately False, no search needed); a word that reuses the same letter multiple times in valid but non-obvious paths; a 1x1 grid.",
        test_inputs=[([["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCCED"), ([["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "SEE"), ([["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCB"), ([["A"]], "A"), ([["A"]], "AB")],
        test_labels=[None, None, "would require reusing a cell -- correctly False", "single cell, matching", "single cell, word longer than the grid can ever supply"],
        reference_solution=(
            "def exist(board, word):\n"
            "    rows, cols = len(board), len(board[0])\n"
            "\n"
            "    def backtrack(r, c, i):\n"
            "        if i == len(word):\n"
            "            return True\n"
            "        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != word[i]:\n"
            "            return False\n"
            "        temp = board[r][c]\n"
            "        board[r][c] = '#'\n"
            "        found = (backtrack(r + 1, c, i + 1) or backtrack(r - 1, c, i + 1) or\n"
            "                 backtrack(r, c + 1, i + 1) or backtrack(r, c - 1, i + 1))\n"
            "        board[r][c] = temp\n"
            "        return found\n"
            "\n"
            "    for r in range(rows):\n"
            "        for c in range(cols):\n"
            "            if backtrack(r, c, 0):\n"
            "                return True\n"
            "    return False\n"
        ),
        hints=[
            "Try starting the search from every cell in the grid -- the word could begin anywhere. From each start, this is a classic backtracking search: extend the path one matching letter at a time.",
            "The key correctness detail is 'no cell reused within one path' -- temporarily mark a cell as used the moment you step onto it (e.g. overwrite it with a sentinel), and make sure you UNDO that marking when backtracking out, whether the recursive search succeeded or failed.",
            "backtrack(r,c,i): if i==len(word): return True. If out of bounds or board[r][c]!=word[i]: return False. Otherwise, save board[r][c], overwrite with a sentinel, recurse into all 4 directions for i+1, restore the original value, and return whether any direction succeeded.",
        ],
    ),

    dict(
        slug="rotate-image",
        title="Rotate Image",
        day=45,
        topic="arrays",
        pattern="in-place transpose + reverse",
        difficulty="Medium",
        interview_priority="Important",
        estimated_solve_minutes=20,
        progression_stage="variation",
        canonical_reference="LeetCode 48: Rotate Image",
        path_tier="extended",
        description=(
            "Given an `n x n` 2D matrix `matrix`, rotate it 90 degrees clockwise IN PLACE (don't allocate "
            "another 2D matrix)."
        ),
        constraints="1 <= n <= 20; -1000 <= matrix[i][j] <= 1000.",
        function_signature="def rotate(matrix):",
        starter_code=(
            "def rotate(matrix):\n"
            "    # A 90-degree clockwise rotation is exactly the same as: transpose\n"
            "    # the matrix (flip across the main diagonal), then reverse each row.\n"
            "    # Both steps can be done in place with no extra matrix.\n"
            "    n = len(matrix)\n"
            "    pass\n"
            "    return matrix\n"
        ),
        expected_time_complexity="O(n^2)",
        expected_space_complexity="O(1) extra",
        brute_force_approach="Build a brand-new matrix where new_matrix[j][n-1-i] = matrix[i][j], then copy it back over the original -- correct, but uses O(n^2) extra space, which this problem specifically asks you to avoid.",
        optimal_approach="Two in-place steps: (1) transpose the matrix (swap matrix[i][j] with matrix[j][i] for every i < j), which flips it across the main diagonal; (2) reverse each row. The composition of those two operations is mathematically identical to a 90-degree clockwise rotation, and neither step needs extra space.",
        common_mistakes="Swapping every (i,j) pair TWICE during the transpose (once as (i,j) and again as (j,i)), which undoes the swap -- the inner loop must only go from i+1 to n, not the full range, so each pair is swapped exactly once; forgetting the second step (reversing each row) entirely, which leaves you with a transpose, not a rotation.",
        edge_cases="A 1x1 matrix (trivially already 'rotated'); a 2x2 matrix (smallest case where the transpose+reverse composition is easy to verify by hand); rotating a matrix that's already symmetric (still needs the reversal step to actually rotate).",
        test_inputs=[([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), ([[1]],), ([[1, 2], [3, 4]],), ([[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]],)],
        reference_solution=(
            "def rotate(matrix):\n"
            "    n = len(matrix)\n"
            "    for i in range(n):\n"
            "        for j in range(i + 1, n):\n"
            "            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]\n"
            "    for row in matrix:\n"
            "        row.reverse()\n"
            "    return matrix\n"
        ),
        hints=[
            "A direct rotation formula (new[j][n-1-i] = old[i][j]) works, but forces you to build a second matrix. Two simpler, well-known IN-PLACE transformations compose into exactly the same result.",
            "Transposing (flipping across the main diagonal, matrix[i][j] <-> matrix[j][i]) followed by reversing every row gives you a 90-degree clockwise rotation, with no extra matrix needed at any point.",
            "For i in range(n): for j in range(i+1, n): swap matrix[i][j] and matrix[j][i] (transpose -- note j starts at i+1, not 0, so each pair is only swapped once). Then for each row in matrix: row.reverse().",
        ],
    ),

    dict(
        slug="spiral-matrix",
        title="Spiral Matrix",
        day=None,
        topic="arrays",
        pattern="shrinking boundary traversal",
        difficulty="Medium",
        interview_priority="Important",
        estimated_solve_minutes=25,
        progression_stage="variation",
        canonical_reference="LeetCode 54: Spiral Matrix",
        path_tier="extended",
        description=(
            "Given an `m x n` matrix, return all its elements in spiral order (right across the top, down "
            "the right side, left across the bottom, up the left side, then repeat on the shrinking inner "
            "boundary)."
        ),
        constraints="1 <= m, n <= 10; -100 <= matrix[i][j] <= 100.",
        function_signature="def spiral_order(matrix):",
        starter_code=(
            "def spiral_order(matrix):\n"
            "    # Track four shrinking boundaries: top, bottom, left, right. Walk each\n"
            "    # of the 4 edges of the current boundary in order (top row left-to-\n"
            "    # right, right column top-to-bottom, bottom row right-to-left, left\n"
            "    # column bottom-to-top), moving that boundary inward after each edge,\n"
            "    # and stop once the boundaries cross.\n"
            "    result = []\n"
            "    if not matrix:\n"
            "        return result\n"
            "    top, bottom = 0, len(matrix) - 1\n"
            "    left, right = 0, len(matrix[0]) - 1\n"
            "    pass\n"
            "    return result\n"
        ),
        expected_time_complexity="O(m*n)",
        expected_space_complexity="O(1) extra (excluding the output)",
        brute_force_approach="Simulate a walking pointer with a direction that changes whenever the next step would go out of bounds or revisit a cell, tracking visited cells explicitly -- works, but needs an extra visited grid; the boundary-shrinking approach below needs none.",
        optimal_approach="Maintain four boundaries (top, bottom, left, right). Each 'lap': walk the top row left-to-right then increment top; walk the right column top-to-bottom then decrement right; if top<=bottom still, walk the bottom row right-to-left then decrement bottom; if left<=right still, walk the left column bottom-to-top then increment left. Repeat while top<=bottom and left<=right.",
        common_mistakes="Forgetting the guard checks (`if top <= bottom` / `if left <= right`) before the THIRD and FOURTH edges of each lap -- without them, a single-row or single-column matrix gets some elements visited twice; mixing up which boundary moves after which edge (each of the 4 edges shrinks exactly one boundary, always the one it just finished walking along).",
        edge_cases="A single row (only the 'top row left-to-right' edge ever fires, thanks to the guards); a single column (only the first two edges ever fire); a non-square (m != n) matrix.",
        test_inputs=[([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],), ([[1, 2, 3]],), ([[1], [2], [3]],)],
        test_labels=[None, None, "single row", "single column"],
        reference_solution=(
            "def spiral_order(matrix):\n"
            "    result = []\n"
            "    if not matrix:\n"
            "        return result\n"
            "    top, bottom = 0, len(matrix) - 1\n"
            "    left, right = 0, len(matrix[0]) - 1\n"
            "    while top <= bottom and left <= right:\n"
            "        for c in range(left, right + 1):\n"
            "            result.append(matrix[top][c])\n"
            "        top += 1\n"
            "        for r in range(top, bottom + 1):\n"
            "            result.append(matrix[r][right])\n"
            "        right -= 1\n"
            "        if top <= bottom:\n"
            "            for c in range(right, left - 1, -1):\n"
            "                result.append(matrix[bottom][c])\n"
            "            bottom -= 1\n"
            "        if left <= right:\n"
            "            for r in range(bottom, top - 1, -1):\n"
            "                result.append(matrix[r][left])\n"
            "            left += 1\n"
            "    return result\n"
        ),
        hints=[
            "Instead of tracking a single walking position and direction, track the four EDGES of the region not yet visited (top, bottom, left, right) -- each full lap around shrinks all four inward by one.",
            "The tricky part is single-row or single-column matrices: after walking the top row and the right column, you need to check whether there's still a genuine bottom row / left column left to walk (top<=bottom, left<=right) before doing so, or you'll double-visit cells.",
            "While top<=bottom and left<=right: walk row `top` left-to-right (then top+=1); walk column `right` top-to-bottom (then right-=1); IF top<=bottom, walk row `bottom` right-to-left (then bottom-=1); IF left<=right, walk column `left` bottom-to-top (then left+=1).",
        ],
    ),

    dict(
        slug="kth-smallest-sorted-matrix",
        title="Kth Smallest Element in a Sorted Matrix",
        day=None,
        topic="heaps",
        pattern="k-way merge via heap over sorted rows",
        difficulty="Medium",
        interview_priority="Important",
        estimated_solve_minutes=25,
        progression_stage="variation",
        canonical_reference="LeetCode 378: Kth Smallest Element in a Sorted Matrix",
        path_tier="extended",
        description=(
            "Given an `n x n` matrix where every ROW and every COLUMN is sorted ascending, return the "
            "`k`-th smallest element in the matrix (counted across the whole matrix, 1-indexed)."
        ),
        constraints="1 <= n <= 300; 1 <= k <= n^2.",
        function_signature="def kth_smallest(matrix, k):",
        starter_code=(
            "import heapq\n"
            "\n"
            "def kth_smallest(matrix, k):\n"
            "    # Since every ROW is already individually sorted, this is really a\n"
            "    # k-way-merge problem: seed a min-heap with the first element of each\n"
            "    # of the first min(n,k) rows, then pop the smallest k times, each\n"
            "    # time pushing that row's next element (columns being sorted isn't\n"
            "    # actually needed by this particular approach, just a bonus fact).\n"
            "    n = len(matrix)\n"
            "    pass\n"
        ),
        expected_time_complexity="O(min(n,k) + k log(min(n,k)))",
        expected_space_complexity="O(min(n,k))",
        brute_force_approach="Flatten the entire matrix into one list, sort it, and index k-1 -- correct and simple, O(n^2 log n), but ignores the fact that each row is already sorted.",
        optimal_approach="Treat each row as its own sorted list and merge them k-way with a min-heap, exactly like Merge K Sorted Lists: seed the heap with (value, row, col) for the first element of each row, then k times pop the smallest and push that row's next element (if any). The k-th pop is the answer.",
        common_mistakes="Seeding the heap with every single element instead of just one per row (defeats the point -- the heap should only ever hold at most one 'candidate' per row at a time, refilled as each row's elements get consumed); forgetting the column-sortedness isn't actually required by the row-based k-way-merge approach (a common point of confusion, since the problem statement emphasizes both).",
        edge_cases="k == 1 (the answer is simply the matrix's minimum, top-left element); k == n^2 (the answer is the matrix's maximum, bottom-right element); a 1x1 matrix.",
        test_inputs=[([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8), ([[-5]], 1), ([[1, 2], [1, 3]], 2)],
        reference_solution=(
            "import heapq\n"
            "\n"
            "def kth_smallest(matrix, k):\n"
            "    n = len(matrix)\n"
            "    heap = [(matrix[i][0], i, 0) for i in range(min(n, k))]\n"
            "    heapq.heapify(heap)\n"
            "    result = None\n"
            "    for _ in range(k):\n"
            "        result, r, c = heapq.heappop(heap)\n"
            "        if c + 1 < len(matrix[r]):\n"
            "            heapq.heappush(heap, (matrix[r][c + 1], r, c + 1))\n"
            "    return result\n"
        ),
        hints=[
            "Every row is already sorted on its own -- that's the whole hint. Merging several already-sorted sequences to find the k-th smallest overall is exactly the Merge K Sorted Lists pattern.",
            "You don't need more than one 'currently available' candidate value per row at any moment. A min-heap holding (value, row, col) for the current front of each row lets you always pop the true smallest available value in O(log n).",
            "Seed the heap with (matrix[i][0], i, 0) for each row i (or just min(n,k) rows, since you'll never need more than k candidates total). Pop k times; each pop, if that row has a next column, push it. The k-th popped value is the answer.",
        ],
    ),

    dict(
        slug="course-schedule-ii",
        title="Course Schedule II",
        day=45,
        topic="graphs",
        pattern="topological sort via Kahn's algorithm (BFS)",
        difficulty="Medium",
        interview_priority="Core",
        estimated_solve_minutes=25,
        progression_stage="variation",
        canonical_reference="LeetCode 210: Course Schedule II",
        path_tier="extended",
        description=(
            "Given `num_courses` (labeled 0 to num_courses-1) and a list of prerequisite pairs "
            "`[course, prereq]` meaning `prereq` must be taken before `course`, return ONE valid order to "
            "take all courses, or `[]` if it's impossible (a cycle exists)."
        ),
        constraints="1 <= num_courses <= 2000; 0 <= len(prerequisites) <= 5000.",
        function_signature="def find_order(num_courses, prerequisites):",
        starter_code=(
            "from collections import deque, defaultdict\n"
            "\n"
            "def find_order(num_courses, prerequisites):\n"
            "    # This is Course Schedule's cycle-detection question, one step\n"
            "    # further: instead of just True/False, you need the ACTUAL order.\n"
            "    # Kahn's algorithm (BFS from every 0-in-degree node) both detects a\n"
            "    # cycle AND produces a valid order in the same pass.\n"
            "    graph = defaultdict(list)\n"
            "    in_degree = [0] * num_courses\n"
            "    pass\n"
        ),
        expected_time_complexity="O(V + E)",
        expected_space_complexity="O(V + E)",
        brute_force_approach="Repeatedly scan for any course whose prerequisites are all already scheduled, add it, and repeat -- correct, but the naive version rescans everything each round, O(V^2) instead of O(V+E).",
        optimal_approach="Build a graph of prereq -> course edges and each course's in-degree (number of unmet prerequisites). Start a BFS queue with every course that has in-degree 0 (no prerequisites at all). Repeatedly pop a course, append it to the order, and decrement the in-degree of every course it unlocks -- pushing any that reach 0. If the final order includes every course, it's valid; otherwise a cycle blocked some courses from ever reaching in-degree 0.",
        common_mistakes="Building the edge in the wrong direction (an edge should point FROM the prerequisite TO the course it unlocks, matching how in-degree is being used); forgetting to check that the final order actually contains ALL num_courses courses (a cycle silently leaves some courses permanently stuck at nonzero in-degree, never entering the queue).",
        edge_cases="No prerequisites at all (any order works, e.g. 0..num_courses-1 in the order courses are discovered with in-degree 0); a direct cycle (A requires B, B requires A -- returns []); a single course with no prerequisites.",
        test_inputs=[(2, [[1, 0]]), (4, [[1, 0], [2, 1], [3, 2]]), (2, [[1, 0], [0, 1]]), (1, [])],
        test_labels=[None, "a straight prerequisite chain -- one forced valid order", "a cycle -- impossible, returns []", "a single course, no prerequisites"],
        reference_solution=(
            "from collections import deque, defaultdict\n"
            "\n"
            "def find_order(num_courses, prerequisites):\n"
            "    graph = defaultdict(list)\n"
            "    in_degree = [0] * num_courses\n"
            "    for course, pre in prerequisites:\n"
            "        graph[pre].append(course)\n"
            "        in_degree[course] += 1\n"
            "    queue = deque([c for c in range(num_courses) if in_degree[c] == 0])\n"
            "    order = []\n"
            "    while queue:\n"
            "        c = queue.popleft()\n"
            "        order.append(c)\n"
            "        for nxt in graph[c]:\n"
            "            in_degree[nxt] -= 1\n"
            "            if in_degree[nxt] == 0:\n"
            "                queue.append(nxt)\n"
            "    return order if len(order) == num_courses else []\n"
        ),
        hints=[
            "You've already seen the cycle-detection version of this problem (Course Schedule) -- this is the same graph, just asking you to also PRODUCE a valid order instead of only checking feasibility.",
            "Kahn's algorithm does both at once: repeatedly take any course with zero remaining unmet prerequisites (in-degree 0), 'complete' it, and see which further courses that unlocks (decrementing their in-degree). If a cycle exists, some courses will never reach in-degree 0 and never get added.",
            "Build graph[prereq].append(course) and in_degree[course]+=1 for each pair. Start a queue with every course at in_degree 0. BFS: pop, append to order, decrement neighbors' in_degree, push any that hit 0. Return order if it has num_courses entries, else [].",
        ],
    ),

    dict(
        slug="next-permutation",
        title="Next Permutation",
        day=None,
        topic="arrays",
        pattern="find pivot, swap, reverse suffix",
        difficulty="Medium",
        interview_priority="Important",
        estimated_solve_minutes=25,
        progression_stage="variation",
        canonical_reference="LeetCode 31: Next Permutation",
        path_tier="extended",
        description=(
            "Given an array `nums` representing a permutation, rearrange it IN PLACE into the next "
            "lexicographically greater permutation. If no such permutation exists (it's already the "
            "highest possible), rearrange it into the lowest possible order (fully ascending) instead. "
            "Return the modified array."
        ),
        constraints="1 <= len(nums) <= 100.",
        function_signature="def next_permutation(nums):",
        starter_code=(
            "def next_permutation(nums):\n"
            "    # Scan from the right for the first place the sequence stops being\n"
            "    # non-increasing (the 'pivot') -- everything to its right is already\n"
            "    # the LARGEST possible arrangement of those elements, so it needs to\n"
            "    # become the SMALLEST instead, and the pivot needs to grow just\n"
            "    # slightly by swapping with the smallest element to its right that's\n"
            "    # still bigger than it.\n"
            "    n = len(nums)\n"
            "    pass\n"
            "    return nums\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(1) extra",
        brute_force_approach="Generate every permutation, sort them lexicographically, and find the one right after the current one -- factorial time, wildly impractical.",
        optimal_approach="Scan from the right to find the first index `i` where nums[i] < nums[i+1] (the 'pivot' -- everything after it is non-increasing, i.e. already at its maximum arrangement). If no such index exists, the whole array is the max permutation -- just reverse it entirely. Otherwise, scan from the right again to find the smallest value greater than nums[i] (guaranteed to exist in the non-increasing suffix), swap it with nums[i], then reverse everything after index i (since that suffix, still non-increasing, needs to become ascending -- the smallest valid next step).",
        common_mistakes="Reversing the suffix BEFORE finding the swap partner (the suffix search specifically relies on it still being non-increasing, so you can scan from the right and stop at the FIRST value bigger than nums[i]); using the first bigger-than-pivot value found scanning from the LEFT instead of the right (in a non-increasing suffix, scanning from the right finds the smallest such value first, which is what minimizes the resulting permutation).",
        edge_cases="Already the highest permutation, e.g. strictly descending (wraps around to the fully ascending order); a single element (no-op, trivially 'already' both min and max); an array with duplicate values (still works correctly since the comparisons use < / >, not identity).",
        test_inputs=[([1, 2, 3],), ([3, 2, 1],), ([1, 1, 5],), ([1],), ([1, 3, 2],)],
        reference_solution=(
            "def next_permutation(nums):\n"
            "    n = len(nums)\n"
            "    i = n - 2\n"
            "    while i >= 0 and nums[i] >= nums[i + 1]:\n"
            "        i -= 1\n"
            "    if i >= 0:\n"
            "        j = n - 1\n"
            "        while nums[j] <= nums[i]:\n"
            "            j -= 1\n"
            "        nums[i], nums[j] = nums[j], nums[i]\n"
            "    nums[i + 1:] = reversed(nums[i + 1:])\n"
            "    return nums\n"
        ),
        hints=[
            "Think about what makes a suffix 'already at its maximum arrangement': it's non-increasing. The place where that non-increasing run BEGINS (scanning from the right) is exactly where the next permutation needs to make its one small change.",
            "Once you've found that pivot index i, you want the SMALLEST possible increase to nums[i] -- scan from the right (through the non-increasing suffix) for the first value greater than nums[i], swap it in, then the suffix (still non-increasing after the swap) needs to be reversed to become ascending, which is the smallest possible arrangement of what's left.",
            "i = n-2; while i>=0 and nums[i]>=nums[i+1]: i-=1. If i>=0: find j from the right where nums[j]>nums[i], swap nums[i] and nums[j]. Either way, reverse nums[i+1:] at the end (if i==-1, this reverses the entire array).",
        ],
    ),

    dict(
        slug="decode-ways",
        title="Decode Ways",
        day=46,
        topic="dynamic-programming",
        pattern="1D DP over string positions (Fibonacci-shaped)",
        difficulty="Medium",
        interview_priority="Core",
        estimated_solve_minutes=25,
        progression_stage="variation",
        canonical_reference="LeetCode 91: Decode Ways",
        path_tier="extended",
        description=(
            "A message of digits can be decoded back to letters via 'A'->1, 'B'->2, ..., 'Z'->26. Given a "
            "digit string `s`, return the number of ways it can be decoded (leading zeros make a substring "
            "invalid -- '06' is not a valid encoding of anything)."
        ),
        constraints="1 <= len(s) <= 100; s consists of digits only.",
        function_signature="def num_decodings(s):",
        starter_code=(
            "def num_decodings(s):\n"
            "    # dp[i] = number of ways to decode s[:i]. At each position, you can\n"
            "    # EITHER decode the single digit s[i-1] alone (if it's not '0'), OR\n"
            "    # decode the last TWO digits together as one letter (if that 2-digit\n"
            "    # number is between 10 and 26) -- add up however many ways each\n"
            "    # choice contributes.\n"
            "    if not s or s[0] == '0':\n"
            "        return 0\n"
            "    n = len(s)\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(1) with rolling variables",
        brute_force_approach="Recursively try both the 1-digit and 2-digit decode choices at every position without memoization -- exponential (it's really the same shape as counting Fibonacci recursively).",
        optimal_approach="dp[i] = ways to decode the first i characters. dp[0]=1 (empty prefix, one trivial way). For each position, add dp[i-1] if the single digit s[i-1] is valid (nonzero), and add dp[i-2] if the two-digit number s[i-2:i] is between 10 and 26. This is structurally identical to counting paths up stairs where you can take 1 or 2 steps, just with validity conditions gating each choice.",
        common_mistakes="Forgetting a '0' can ONLY ever be used as the second digit of a valid 2-digit pairing (10 or 20), never alone and never as the leading digit of a 2-digit pair (so '30' is invalid, contributing 0 ways) -- a lone '0' anywhere with no valid 2-digit interpretation kills the whole count from that point; not short-circuiting to 0 the moment a position has NO valid decoding (both choices fail) instead of letting a zero silently propagate through arithmetic.",
        edge_cases="A string starting with '0' (immediately 0 ways, no valid decoding exists at all); '10' and '20' (each has exactly one way -- must be decoded as the two-digit pair, since the second digit alone, '0', is never valid alone); a run of digits where every position offers both a valid 1-digit and 2-digit choice (Fibonacci-like growth).",
        test_inputs=[("12",), ("226",), ("06",), ("0",), ("10",), ("100",)],
        test_labels=[None, None, "leading zero -- immediately 0 ways", "a single '0' -- 0 ways", "must use the two-digit pairing, '0' alone is never valid", "a '0' with no valid 2-digit pairing available -- 0 ways"],
        reference_solution=(
            "def num_decodings(s):\n"
            "    if not s or s[0] == '0':\n"
            "        return 0\n"
            "    n = len(s)\n"
            "    prev2, prev1 = 1, 1\n"
            "    for i in range(1, n):\n"
            "        current = 0\n"
            "        if s[i] != '0':\n"
            "            current += prev1\n"
            "        two_digit = int(s[i - 1:i + 1])\n"
            "        if 10 <= two_digit <= 26:\n"
            "            current += prev2\n"
            "        if current == 0:\n"
            "            return 0\n"
            "        prev2, prev1 = prev1, current\n"
            "    return prev1\n"
        ),
        hints=[
            "This has the exact same shape as counting ways to climb stairs taking 1 or 2 steps at a time -- except here, whether a '1-step' (single digit) or '2-step' (digit pair) move is even ALLOWED depends on validity rules ('0' alone is never valid; a pair must be 10-26).",
            "Track two rolling values: ways to decode up through the position 2 back (prev2) and 1 back (prev1). At each new position, add prev1 if the single current digit is valid, and add prev2 if the current digit plus the one before it forms a valid 10-26 pair.",
            "prev2, prev1 = 1, 1 (base cases for the first character, already validated as non-zero). For i in range(1, n): current = prev1 if s[i]!='0' else 0; current += prev2 if 10<=int(s[i-1:i+1])<=26 else 0; if current==0: return 0 (dead end). prev2, prev1 = prev1, current. Return prev1.",
        ],
    ),

    dict(
        slug="remove-k-digits",
        title="Remove K Digits",
        day=45,
        topic="stacks",
        pattern="monotonic stack with a removal budget",
        difficulty="Medium",
        interview_priority="Important",
        estimated_solve_minutes=25,
        progression_stage="variation",
        canonical_reference="LeetCode 402: Remove K Digits",
        path_tier="extended",
        description=(
            "Given a non-negative integer as a string `num` and an integer `k`, remove exactly `k` digits "
            "from `num` so that the remaining digits (kept in their original order) form the SMALLEST "
            "possible number. Return it as a string, with no leading zeros (unless the result is \"0\" "
            "itself)."
        ),
        constraints="1 <= len(num) <= 10^5; 0 <= k <= len(num); num consists of digits only.",
        function_signature="def remove_k_digits(num, k):",
        starter_code=(
            "def remove_k_digits(num, k):\n"
            "    # Build the result with a monotonic (non-decreasing) stack: whenever\n"
            "    # the next digit is SMALLER than the stack's top, popping that top\n"
            "    # digit strictly improves the number (a smaller digit earlier always\n"
            "    # beats a bigger one) -- as long as you still have removals left in\n"
            "    # your budget k.\n"
            "    stack = []\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n)",
        expected_space_complexity="O(n)",
        brute_force_approach="Try every combination of k digits to remove and compare the resulting numbers -- combinatorially explosive.",
        optimal_approach="Greedy monotonic stack: walk the digits left to right. While the stack isn't empty, the top is greater than the current digit, and you still have removals left (k > 0), pop the stack (removing that larger, earlier digit strictly helps) and decrement k. Push the current digit. If removals remain after the full scan (the number was non-decreasing throughout), remove them from the END. Finally strip any leading zeros (keeping at least one digit).",
        common_mistakes="Forgetting the leftover-k-at-the-end case (a strictly non-decreasing input like '12345' never triggers a pop during the scan, so any remaining k must be trimmed from the back afterward); not stripping leading zeros from the result (e.g. num='10200', k=1 must produce '200', not '0200'); returning an empty string instead of '0' when every digit gets removed.",
        edge_cases="k == len(num) (every digit removed, result is '0'); a strictly increasing number (all removals happen at the end, none during the scan); a result that would have leading zeros after removal (must be stripped, but ONLY down to a single '0' if that's all that's left).",
        test_inputs=[("1432219", 3), ("10200", 1), ("10", 2), ("112", 1)],
        reference_solution=(
            "def remove_k_digits(num, k):\n"
            "    stack = []\n"
            "    for digit in num:\n"
            "        while k > 0 and stack and stack[-1] > digit:\n"
            "            stack.pop()\n"
            "            k -= 1\n"
            "        stack.append(digit)\n"
            "    if k > 0:\n"
            "        stack = stack[:-k]\n"
            "    result = ''.join(stack).lstrip('0')\n"
            "    return result if result else '0'\n"
        ),
        hints=[
            "A smaller digit earlier in the number always beats a larger digit earlier, regardless of what comes after -- that's the greedy insight: whenever you can strictly improve the result by removing a recently-placed larger digit in favor of the current smaller one, you always should (as long as you still have removals left).",
            "This is the same monotonic-stack shape as other 'keep it non-decreasing, pop when violated' problems -- push digits, but pop the stack's top first whenever it's bigger than the digit you're about to add AND you still have budget k remaining.",
            "For each digit: while k>0 and stack and stack[-1] > digit: pop, k-=1. Push digit. After the full scan, if k>0 still remains (nothing triggered enough pops), trim k digits off the END of the stack. Join, strip leading zeros, and default to '0' if empty.",
        ],
    ),

    dict(
        slug="bst-iterator",
        title="Binary Search Tree Iterator",
        day=46,
        topic="trees",
        pattern="controlled in-order traversal via an explicit stack",
        difficulty="Medium",
        interview_priority="Important",
        estimated_solve_minutes=25,
        progression_stage="variation",
        canonical_reference="LeetCode 173: Binary Search Tree Iterator",
        path_tier="extended",
        description=(
            "Design an iterator over a binary search tree's in-order traversal. `next()` returns the next "
            "smallest value, and `hasNext()` reports whether one remains. Both must run in amortized O(1) "
            "time and O(h) extra memory (h = tree height), NOT by precomputing the entire traversal up "
            "front. This exercise checks a scripted sequence: the first op is always `'values'` carrying "
            "the tree's level-order array, followed by `'next'`/`'hasNext'` calls."
        ),
        constraints="1 <= number of nodes <= 10^5; at most 10^5 total next()/hasNext() calls.",
        function_signature="def bst_iterator_ops(values, ops, args):",
        starter_code=(
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
            "class BSTIterator:\n"
            "    def __init__(self, root):\n"
            "        # Push the leftmost path from root onto a stack -- the smallest\n"
            "        # value is always whatever's on top.\n"
            "        self.stack = []\n"
            "        pass\n"
            "\n"
            "    def next(self):\n"
            "        pass\n"
            "\n"
            "    def hasNext(self):\n"
            "        pass\n"
            "\n"
            "\n"
            "def bst_iterator_ops(values, ops, args):\n"
            "    root = build_tree(values)\n"
            "    it = BSTIterator(root)\n"
            "    results = []\n"
            "    for op in ops:\n"
            "        results.append(it.next() if op == 'next' else it.hasNext())\n"
            "    return results\n"
        ),
        expected_time_complexity="O(1) amortized per next()/hasNext() call",
        expected_space_complexity="O(h)",
        brute_force_approach="Do a full in-order traversal up front, store all values in a list, and serve next()/hasNext() from a plain index into that list -- correct and simple, but uses O(n) memory even if the caller only ever asks for the first few values, violating the O(h)-space intent.",
        optimal_approach="Maintain an explicit stack representing 'the leftmost path not yet fully visited'. Initialize by pushing every node from the root down its left spine. next() pops the top (the current smallest unvisited value) -- if that node has a right child, push that child's ENTIRE left spine before returning. hasNext() is just whether the stack is non-empty.",
        common_mistakes="Precomputing the whole in-order list up front (defeats the O(h)-space intent of the problem, even though it 'works'); forgetting that after popping a node with a right child, you need to push that right child's FULL left spine (not just the right child itself) to maintain the invariant that the stack top is always the next smallest value.",
        edge_cases="A tree that's a single node (one next() call, then hasNext() is False); a completely left-skewed tree (the whole tree gets pushed onto the stack up front, stack acts like a simple pop-through list); a completely right-skewed tree (stack never holds more than 1 node at a time, next() repeatedly pushes one right child's left spine, which is just that child itself).",
        test_inputs=[
            ([7, 3, 15, None, None, 9, 20], ["next", "next", "hasNext", "next", "hasNext", "next", "hasNext", "next", "hasNext"], [[], [], [], [], [], [], [], [], []]),
            ([1], ["hasNext", "next", "hasNext"], [[], [], []]),
            ([1, None, 2, None, 3], ["next", "next", "next", "hasNext"], [[], [], [], []]),
        ],
        test_labels=[None, "a single-node tree", "a right-skewed chain -- stresses repeated push-left-of-right-child"],
        reference_solution=(
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
            "class BSTIterator:\n"
            "    def __init__(self, root):\n"
            "        self.stack = []\n"
            "        self._push_left(root)\n"
            "\n"
            "    def _push_left(self, node):\n"
            "        while node:\n"
            "            self.stack.append(node)\n"
            "            node = node.left\n"
            "\n"
            "    def next(self):\n"
            "        node = self.stack.pop()\n"
            "        if node.right:\n"
            "            self._push_left(node.right)\n"
            "        return node.val\n"
            "\n"
            "    def hasNext(self):\n"
            "        return len(self.stack) > 0\n"
            "\n"
            "\n"
            "def bst_iterator_ops(values, ops, args):\n"
            "    root = build_tree(values)\n"
            "    it = BSTIterator(root)\n"
            "    results = []\n"
            "    for op in ops:\n"
            "        results.append(it.next() if op == 'next' else it.hasNext())\n"
            "    return results\n"
        ),
        hints=[
            "In-order traversal (left, node, right) is normally done recursively -- this problem wants you to pause and resume it on demand, which means making the recursion's call stack EXPLICIT instead.",
            "The invariant to maintain: the top of your explicit stack is always the next smallest unvisited value. Initially, that means pushing the entire leftmost path from the root. After popping a node, if it has a right child, that child's own leftmost path needs to be pushed next (its left subtree's smallest values come before it).",
            "_push_left(node): push node, move to node.left, repeat while not None. __init__: self.stack=[]; self._push_left(root). next(): node=self.stack.pop(); if node.right: self._push_left(node.right); return node.val. hasNext(): bool(self.stack).",
        ],
    ),

    dict(
        slug="reorganize-string",
        title="Reorganize String",
        day=None,
        topic="heaps",
        pattern="greedy max-heap character interleaving",
        difficulty="Medium",
        interview_priority="Important",
        estimated_solve_minutes=25,
        progression_stage="variation",
        canonical_reference="LeetCode 767: Reorganize String",
        path_tier="extended",
        description=(
            "Given a string `s`, rearrange its characters so that no two adjacent characters are the same, "
            "and return any one valid rearrangement. Return `\"\"` if no valid rearrangement exists."
        ),
        constraints="1 <= len(s) <= 500; s is lowercase English letters.",
        function_signature="def reorganize_string(s):",
        starter_code=(
            "import heapq\n"
            "from collections import Counter\n"
            "\n"
            "def reorganize_string(s):\n"
            "    # Feasibility check first: if any character's count exceeds\n"
            "    # (len(s)+1)//2, it's mathematically impossible to space it out\n"
            "    # enough (it would need to occupy more than every-other slot).\n"
            "    # Otherwise, greedily always place the CURRENTLY most frequent\n"
            "    # remaining character -- a max-heap makes 'most frequent remaining'\n"
            "    # instantly available every step.\n"
            "    counts = Counter(s)\n"
            "    max_count = max(counts.values())\n"
            "    if max_count > (len(s) + 1) // 2:\n"
            "        return ''\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n log(alphabet size))",
        expected_space_complexity="O(alphabet size)",
        brute_force_approach="Try every permutation of the string's characters and check adjacency -- factorial time, wildly impractical.",
        optimal_approach="Feasibility first: no valid arrangement exists if any character needs to appear in more than half (rounded up) of the positions. Otherwise, greedily build the result by always placing the currently-most-frequent remaining character (a max-heap keyed by count), while holding the just-placed character 'on deck' for one step so it can't be placed twice in a row -- then feed it back into the heap.",
        common_mistakes="Forgetting the feasibility check entirely and attempting to greedily build a result that can't actually exist (silently producing an invalid or incomplete string instead of returning ''); placing the most-frequent character twice in a row by re-adding it to the heap too early (it must sit out for exactly one placement before it's eligible again).",
        edge_cases="A single character (trivially valid, itself is the only 'arrangement'); a character appearing more than half the total length (impossible, returns ''); exactly two distinct characters that must strictly alternate.",
        test_inputs=[("aab",), ("aaab",), ("aa",), ("a",)],
        test_labels=["a forced-unique valid rearrangement", "impossible -- one character exceeds half the length", "impossible -- two identical characters, nothing to separate them with", "trivial single character"],
        reference_solution=(
            "import heapq\n"
            "from collections import Counter\n"
            "\n"
            "def reorganize_string(s):\n"
            "    counts = Counter(s)\n"
            "    max_count = max(counts.values())\n"
            "    if max_count > (len(s) + 1) // 2:\n"
            "        return ''\n"
            "    heap = [(-cnt, ch) for ch, cnt in counts.items()]\n"
            "    heapq.heapify(heap)\n"
            "    result = []\n"
            "    prev = None\n"
            "    while heap:\n"
            "        cnt, ch = heapq.heappop(heap)\n"
            "        result.append(ch)\n"
            "        if prev and prev[0] < 0:\n"
            "            heapq.heappush(heap, prev)\n"
            "        cnt += 1\n"
            "        prev = (cnt, ch) if cnt < 0 else None\n"
            "    return ''.join(result)\n"
            "\n"
        ),
        hints=[
            "Before trying to build anything, check whether it's even possible: if the most frequent character shows up more than (len(s)+1)//2 times, there's no way to keep it from being adjacent to itself somewhere -- return '' immediately.",
            "Greedily place the most frequent remaining character every step (a max-heap makes this O(log k) per step). The one wrinkle: the character you JUST placed can't be placed again immediately, so hold it out of the heap for exactly one step before feeding it back in.",
            "heap of (-count, char) tuples, heapified. Each step: pop the most frequent, append to result, decrement its count (increment since negated), and re-push the PREVIOUSLY popped character (if it still has remaining count) now that a different character has been placed since it.",
        ],
    ),

    dict(
        slug="meeting-rooms-ii",
        title="Meeting Rooms II",
        day=44,
        topic="heaps",
        pattern="min-heap of active end times",
        difficulty="Medium",
        interview_priority="Core",
        estimated_solve_minutes=20,
        progression_stage="variation",
        canonical_reference="LeetCode 253: Meeting Rooms II",
        path_tier="extended",
        description=(
            "Given an array of meeting time intervals `[start, end]`, return the MINIMUM number of "
            "conference rooms required so that every meeting can be held without overlapping another in "
            "the same room."
        ),
        constraints="1 <= len(intervals) <= 10^4; 0 <= start < end <= 10^6.",
        function_signature="def min_meeting_rooms(intervals):",
        starter_code=(
            "import heapq\n"
            "\n"
            "def min_meeting_rooms(intervals):\n"
            "    # Sort by start time. A min-heap holds the END times of every\n"
            "    # meeting currently occupying a room. Before starting a new meeting,\n"
            "    # check whether the room that frees up SOONEST (heap's top) is\n"
            "    # already free by this meeting's start time -- if so, reuse that\n"
            "    # room; otherwise, a genuinely new room is needed.\n"
            "    if not intervals:\n"
            "        return 0\n"
            "    intervals.sort(key=lambda x: x[0])\n"
            "    pass\n"
        ),
        expected_time_complexity="O(n log n)",
        expected_space_complexity="O(n)",
        brute_force_approach="For every meeting, check it against every other currently-active meeting to count overlaps directly -- O(n^2).",
        optimal_approach="Sort meetings by start time. Use a min-heap of the END times of meetings currently occupying a room. For each meeting (in start order): if the heap's smallest end time is <= this meeting's start, that room has freed up -- pop it (reuse) before pushing the new end time; otherwise push without popping (a new room is needed). The heap's final size is never checked directly -- rather, its size at the point of maximum overlap, tracked as you go, or simply its size after processing every meeting (since a popped-and-repushed room keeps the heap size constant, and only a genuinely new room grows it) IS the answer.",
        common_mistakes="Popping the heap unconditionally on every meeting instead of only when the earliest-ending room is actually free by the new meeting's start time (that conditional check is the entire point -- it's what decides 'reuse' vs 'need a new room'); sorting by END time instead of START time (unlike Non-overlapping Intervals, this problem needs to process meetings in the order they BEGIN, since you're allocating rooms as time moves forward).",
        edge_cases="No meetings overlap at all (answer 1, one room suffices, reused for everything); every meeting overlaps every other (answer equals the number of meetings, one room each); meetings that touch exactly at an endpoint (one ending exactly when another starts -- NOT an overlap, the room can be reused).",
        test_inputs=[([[0, 30], [5, 10], [15, 20]],), ([[7, 10], [2, 4]],), ([[1, 5], [8, 9], [8, 9]],), ([[1, 10]],)],
        test_labels=[None, "no overlap at all -- one room suffices", "a tie -- two meetings needing simultaneous rooms", "a single meeting"],
        reference_solution=(
            "import heapq\n"
            "\n"
            "def min_meeting_rooms(intervals):\n"
            "    if not intervals:\n"
            "        return 0\n"
            "    intervals.sort(key=lambda x: x[0])\n"
            "    heap = [intervals[0][1]]\n"
            "    for start, end in intervals[1:]:\n"
            "        if start >= heap[0]:\n"
            "            heapq.heapreplace(heap, end)\n"
            "        else:\n"
            "            heapq.heappush(heap, end)\n"
            "    return len(heap)\n"
        ),
        hints=[
            "Sort meetings by start time, and think of the heap as 'the end times of rooms currently in use', with the smallest end time always on top -- that's the room that will free up soonest.",
            "Before allocating a room for the next meeting, check whether the soonest-freeing room is already free (its end time <= this meeting's start). If so, that same room can be reused -- no growth in room count needed. If not, a genuinely new room must be added.",
            "heap = [intervals[0][1]] after sorting by start. For each remaining (start, end): if start >= heap[0] (smallest end time), heapreplace (pop the freed room's end, push the new end -- reuse, room count unchanged). Otherwise heappush (grow the room count). Return len(heap) at the end.",
        ],
    ),
]
