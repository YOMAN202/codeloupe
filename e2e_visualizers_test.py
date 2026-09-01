"""
Targeted verification of the new data-structure-aware trace visualizers
(Phase 1 of the current work plan). Not a replacement for e2e_test.py --
a focused check that each specialized view actually renders for real
correct/incorrect submissions across the categories it's meant to cover,
with zero console errors, before moving on to the next category.
"""
import sys
import time
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5173"
console_errors = []
failures = []


def check(label, cond, extra=None):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {label}" + (f" -- {extra}" if extra and not cond else ""))
    if not cond:
        failures.append(label)


def run_case(page, slug, code, label, expect_classes, test_case_index=None):
    page.goto(f"{BASE}/#/problems/{slug}")
    page.wait_for_selector(".workspace-page", timeout=10000)
    page.wait_for_timeout(300)
    page.evaluate("() => window.__tracevizEditor && window.__tracevizEditor.setValue('')")
    page.wait_for_timeout(100)
    page.evaluate("(code) => window.__tracevizEditor.setValue(code)", code)
    page.wait_for_timeout(100)
    if test_case_index is not None:
        # switch to the Trace tab first so the test-case picker exists
        page.get_by_role("button", name="Trace", exact=True).click()
        page.wait_for_timeout(100)
        picker = page.locator(".trace-testcase-picker select")
        if picker.count() > 0:
            picker.select_option(index=test_case_index)
            page.wait_for_timeout(100)
    # switch to Trace tab
    page.get_by_role("button", name="Trace", exact=True).click()
    page.wait_for_timeout(100)
    page.get_by_role("button", name="Trace my code").click()
    page.wait_for_selector(".trace-viewer", timeout=15000)
    page.wait_for_timeout(400)
    # Step 0 is always the bare module-level "call" event with empty
    # locals (nothing to visualize yet) -- step forward partway through
    # the trace before checking, and take the best of a few positions
    # since a specialized view's data may only be present on some steps
    # (e.g. a recursive call stack only exists past the first call).
    best_found = {cls: False for cls in expect_classes}
    max_index = int(page.locator(".trace-scrubber").get_attribute("max") or 0)
    # Sample across the WHOLE trace (not just the first few steps) via the
    # scrubber directly -- a plain step-forward loop is too slow to reach
    # anything meaningful in a long trace (e.g. a truncated infinite loop
    # can be thousands of steps deep before the interesting state shows
    # up), and jumping is also just a more realistic stand-in for a
    # learner scrubbing straight to wherever they want to look.
    sample_points = sorted(set([0, max_index] + [round(max_index * f) for f in (0.05, 0.15, 0.3, 0.5, 0.7, 0.85, 0.95, 0.99)]))
    for idx in sample_points:
        page.evaluate(
            """(idx) => {
                const el = document.querySelector('.trace-scrubber');
                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                setter.call(el, idx);
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }""",
            idx,
        )
        page.wait_for_timeout(50)
        for cls in expect_classes:
            if not best_found[cls] and page.locator(f".{cls}").count() > 0:
                best_found[cls] = True
    check(f"{label}: some visualizer content present", any(best_found.values()), best_found)
    return best_found


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: console_errors.append(str(exc)))

    # ---- 1. Array / pointer / sliding window (correct + buggy) ----------
    correct_two_ptr = "def two_sum_sorted(numbers, target):\n    left, right = 0, len(numbers) - 1\n    while left < right:\n        s = numbers[left] + numbers[right]\n        if s == target:\n            return [left, right]\n        elif s < target:\n            left += 1\n        else:\n            right -= 1\n    return []\n"
    run_case(page, "two-sum-sorted", correct_two_ptr, "Array/pointer (correct two-pointer)", ["seq-boxes", "pointer-chip"])

    buggy_sliding = "def max_sum_subarray(arr, k):\n    window_sum = 0\n    for i in range(len(arr)):\n        window_sum += arr[i]\n    return window_sum\n"
    run_case(page, "max-sum-subarray-k", buggy_sliding, "Array/pointer (buggy sliding window)", ["seq-boxes"])

    # ---- 2. Linked lists (correct + buggy) -------------------------------
    ll_helpers = (
        "class Node:\n"
        "    def __init__(self, val):\n"
        "        self.val = val\n"
        "        self.next = None\n\n"
        "def build_list(values):\n"
        "    head = None\n"
        "    for v in reversed(values):\n"
        "        node = Node(v)\n"
        "        node.next = head\n"
        "        head = node\n"
        "    return head\n\n"
        "def to_list(head):\n"
        "    result = []\n"
        "    while head:\n"
        "        result.append(head.val)\n"
        "        head = head.next\n"
        "    return result\n\n"
    )
    correct_reverse = ll_helpers + (
        "def reverse_list(values):\n"
        "    head = build_list(values)\n"
        "    prev = None\n"
        "    curr = head\n"
        "    while curr:\n"
        "        nxt = curr.next\n"
        "        curr.next = prev\n"
        "        prev = curr\n"
        "        curr = nxt\n"
        "    return to_list(prev)\n"
    )
    run_case(page, "reverse-linked-list", correct_reverse, "Linked list (correct reversal)", ["ll-chain", "ll-node"])

    buggy_reverse = ll_helpers + (
        "def reverse_list(values):\n"
        "    head = build_list(values)\n"
        "    curr = head\n"
        "    while curr:\n"
        "        curr.next = curr\n"
        "        curr = curr.next\n"
        "    return to_list(curr)\n"
    )
    run_case(page, "reverse-linked-list", buggy_reverse, "Linked list (buggy - self cycle)", ["ll-chain", "viz-warning"])

    # ---- 3. Recursion / call stack ---------------------------------------
    correct_fact = "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n"
    run_case(page, "factorial-recursive", correct_fact, "Recursion (correct factorial)", ["call-stack", "call-frame"])

    buggy_fact = "def factorial(n):\n    return n * factorial(n - 1)\n"
    run_case(page, "factorial-recursive", buggy_fact, "Recursion (buggy - no base case, should truncate)", ["call-stack", "call-frame"])

    # ---- 4. Trees ---------------------------------------------------------
    tree_helpers = (
        "class TreeNode:\n"
        "    def __init__(self, val):\n"
        "        self.val = val\n"
        "        self.left = None\n"
        "        self.right = None\n\n"
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
        "    return root\n\n"
    )
    correct_maxdepth = tree_helpers + (
        "def max_depth(values):\n"
        "    root = build_tree(values)\n"
        "    def helper(node):\n"
        "        if node is None:\n"
        "            return 0\n"
        "        return 1 + max(helper(node.left), helper(node.right))\n"
        "    return helper(root)\n"
    )
    run_case(page, "max-depth-binary-tree", correct_maxdepth, "Tree (correct max depth)", ["tree-node", "tree-canvas"])

    # ---- 5. Stacks / queues -------------------------------------------------
    correct_valid_paren = "def is_valid_parens(s):\n    stack = []\n    pairs = {')': '(', ']': '[', '}': '{'}\n    for c in s:\n        if c in pairs:\n            if not stack or stack.pop() != pairs[c]:\n                return False\n        else:\n            stack.append(c)\n    return not stack\n"
    run_case(page, "valid-parentheses", correct_valid_paren, "Stack (correct valid parens)", ["sq-stack", "sq-cell"])

    # ---- 6. Sorting -------------------------------------------------------
    correct_bubble = "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n    return arr\n"
    run_case(page, "bubble-sort", correct_bubble, "Sorting (correct bubble sort)", ["sort-bars", "sort-bar"])

    # ---- 7. Graphs (grid) --------------------------------------------------
    correct_flood = "def flood_fill(image, sr, sc, color):\n    old = image[sr][sc]\n    if old == color:\n        return image\n    def dfs(r, c):\n        if r < 0 or r >= len(image) or c < 0 or c >= len(image[0]) or image[r][c] != old:\n            return\n        image[r][c] = color\n        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)\n    dfs(sr, sc)\n    return image\n"
    run_case(page, "flood-fill", correct_flood, "Graph/grid (correct flood fill)", ["grid-cell", "grid-rows"])

    # ---- 7b. Graphs (grid BFS with a queue, correct + buggy) ---------------
    correct_islands = (
        "from collections import deque\n\n"
        "def num_islands(grid):\n"
        "    rows, cols = len(grid), len(grid[0])\n"
        "    visited = set()\n"
        "    count = 0\n"
        "    for r in range(rows):\n"
        "        for c in range(cols):\n"
        "            if grid[r][c] == 1 and (r, c) not in visited:\n"
        "                count += 1\n"
        "                q = deque([(r, c)])\n"
        "                visited.add((r, c))\n"
        "                while q:\n"
        "                    cr, cc = q.popleft()\n"
        "                    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n"
        "                        nr, nc = cr+dr, cc+dc\n"
        "                        if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==1 and (nr,nc) not in visited:\n"
        "                            visited.add((nr,nc))\n"
        "                            q.append((nr,nc))\n"
        "    return count\n"
    )
    run_case(page, "number-of-islands", correct_islands, "Graph/grid (correct BFS island count)", ["grid-cell", "sq-queue", "seq-boxes"])

    buggy_islands = (
        "from collections import deque\n\n"
        "def num_islands(grid):\n"
        "    rows, cols = len(grid), len(grid[0])\n"
        "    count = 0\n"
        "    for r in range(rows):\n"
        "        for c in range(cols):\n"
        "            if grid[r][c] == 1:\n"
        "                count += 1\n"
        "    return count\n"
    )
    run_case(page, "number-of-islands", buggy_islands, "Graph/grid (buggy - counts cells not islands)", ["grid-cell"])

    # ---- 7c. Graphs (node graph, correct + buggy) ---------------------------
    correct_clone = (
        "class GNode:\n"
        "    def __init__(self, val):\n"
        "        self.val = val\n"
        "        self.neighbors = []\n\n"
        "def clone_graph_roundtrip(adj_list):\n"
        "    if not adj_list:\n"
        "        return []\n"
        "    nodes = {i + 1: GNode(i + 1) for i in range(len(adj_list))}\n"
        "    for i, neighbors in enumerate(adj_list):\n"
        "        nodes[i + 1].neighbors = [nodes[nv] for nv in neighbors]\n"
        "    visited = {}\n"
        "    def clone(node):\n"
        "        if node in visited:\n"
        "            return visited[node]\n"
        "        copy = GNode(node.val)\n"
        "        visited[node] = copy\n"
        "        for nb in node.neighbors:\n"
        "            copy.neighbors.append(clone(nb))\n"
        "        return copy\n"
        "    cloned_start = clone(nodes[1])\n"
        "    result = {}\n"
        "    stack = [cloned_start]\n"
        "    seen_ids = set()\n"
        "    while stack:\n"
        "        n = stack.pop()\n"
        "        if id(n) in seen_ids:\n"
        "            continue\n"
        "        seen_ids.add(id(n))\n"
        "        result[n.val] = sorted(nb.val for nb in n.neighbors)\n"
        "        for nb in n.neighbors:\n"
        "            if id(nb) not in seen_ids:\n"
        "                stack.append(nb)\n"
        "    return [result[i + 1] for i in range(len(adj_list))]\n"
    )
    run_case(page, "clone-graph", correct_clone, "Graph/node (correct clone-graph)", ["graph-node", "graph-canvas"])

    buggy_clone = (
        "class GNode:\n"
        "    def __init__(self, val):\n"
        "        self.val = val\n"
        "        self.neighbors = []\n\n"
        "def clone_graph_roundtrip(adj_list):\n"
        "    if not adj_list:\n"
        "        return []\n"
        "    nodes = {i + 1: GNode(i + 1) for i in range(len(adj_list))}\n"
        "    for i, neighbors in enumerate(adj_list):\n"
        "        nodes[i + 1].neighbors = [nodes[nv] for nv in neighbors]\n"
        "    def clone(node):\n"
        "        # bug: no visited map -- infinite recursion on any cycle\n"
        "        copy = GNode(node.val)\n"
        "        copy.neighbors = [clone(nb) for nb in node.neighbors]\n"
        "        return copy\n"
        "    cloned_start = clone(nodes[1])\n"
        "    return cloned_start.val\n"
    )
    run_case(page, "clone-graph", buggy_clone, "Graph/node (buggy - no visited map, should truncate/crash)", ["graph-node", "graph-canvas", "trace-status-error", "trace-status-warning"])

    # ---- 8. Heaps -----------------------------------------------------------
    correct_laststone = "import heapq\ndef last_stone_weight(stones):\n    heap = [-s for s in stones]\n    heapq.heapify(heap)\n    while len(heap) > 1:\n        a = -heapq.heappop(heap)\n        b = -heapq.heappop(heap)\n        if a != b:\n            heapq.heappush(heap, -(a - b))\n    return -heap[0] if heap else 0\n"
    run_case(page, "last-stone-weight", correct_laststone, "Heap (correct last stone weight)", ["tree-node", "heap-node"])

    # ---- 9. DP tables ---------------------------------------------------
    correct_climb = "def climb_stairs(n):\n    if n <= 2:\n        return n\n    dp = [0] * (n + 1)\n    dp[1] = 1\n    dp[2] = 2\n    for i in range(3, n + 1):\n        dp[i] = dp[i - 1] + dp[i - 2]\n    return dp[n]\n"
    run_case(page, "climbing-stairs", correct_climb, "DP (correct climbing stairs)", ["dp-cell", "dp-view"], test_case_index=3)

    print()
    print(f"Console errors captured: {len(console_errors)}")
    for e in console_errors[:20]:
        print("  CONSOLE:", e[:300])
    check("No console errors across all visualizer checks", len(console_errors) == 0)

    browser.close()

print()
if failures:
    print(f"{len(failures)} FAILURE(S):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("ALL VISUALIZER CHECKS PASSED")
