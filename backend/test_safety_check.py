"""
Standalone tests for execution/safety_check.py -- the static AST
defense-in-depth filter added ahead of public deployment. Two things this
file exists to prove, thoroughly:

1. Every one of the 109 curated problems' reference solutions, brute-force
   references, and starter code -- and every concept lesson's walkthrough
   code and practice-exercise starter/solution code -- still passes the
   filter untouched. This is the actual, automated version of "does not
   break any legitimate existing DSA submission or the 109 reference
   solutions," not a spot-check.
2. A representative sample of unsafe code (every category the filter is
   meant to catch: file access, process spawning, networking, dangerous
   imports, reflection/escape primitives) is correctly rejected, and a
   representative sample of ordinary-but-tricky-looking safe code
   (comprehensions, custom classes with dunders, nested functions,
   closures, decorators, generators, exceptions) is correctly allowed --
   run directly against the pure function, no server needed.

Run directly: `python3 test_safety_check.py` from backend/.
"""
import sys

sys.path.insert(0, ".")
from execution.safety_check import find_safety_violation
from db.seed_problems import PROBLEMS
from db.seed_concepts import CONCEPT_LESSONS, CONCEPT_PRACTICE_EXERCISES

FAILURES = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" -- {detail}" if detail else ""))
    if not condition:
        FAILURES.append(label)


# ---------------------------------------------------------------- part 1 --
# Every real piece of curated content must still pass.

print("=== Part 1: every curated problem/lesson code field must pass unmodified ===\n")

problem_code_fields = ["reference_solution", "brute_force_code", "starter_code", "stress_test_generator"]
checked = 0
for p in PROBLEMS:
    for field in problem_code_fields:
        code = p.get(field)
        if not code:
            continue
        checked += 1
        violation = find_safety_violation(code)
        check(f"problem '{p['slug']}'.{field} passes", violation is None, violation or "")

for c in CONCEPT_LESSONS:
    for field in ("walkthrough_code",):
        code = c.get(field)
        if not code:
            continue
        checked += 1
        violation = find_safety_violation(code)
        check(f"concept lesson '{c['slug']}'.{field} passes", violation is None, violation or "")

for slug, exercises in CONCEPT_PRACTICE_EXERCISES.items():
    for i, ex in enumerate(exercises):
        for field in ("starter_code", "solution_code"):
            code = ex.get(field)
            if not code:
                continue
            checked += 1
            violation = find_safety_violation(code)
            check(f"concept '{slug}' practice exercise #{i} .{field} passes", violation is None, violation or "")

print(f"\n{checked} curated code fields checked across {len(PROBLEMS)} problems and {len(CONCEPT_LESSONS)} concept lessons.\n")


# ---------------------------------------------------------------- part 2 --
# Representative unsafe code, one per category, must be rejected.

print("=== Part 2: representative unsafe code must be rejected ===\n")

UNSAFE_SAMPLES = [
    ("file access: open()", "f = open('/etc/passwd')\nprint(f.read())\n"),
    ("file access: open() as builtin, no import needed", "data = open('../../db/traceviz.db', 'rb').read()\n"),
    ("filesystem module: os", "import os\nprint(os.listdir('.'))\n"),
    ("filesystem module: os.path (dotted import)", "import os.path\nprint(os.path.exists('.'))\n"),
    ("filesystem module: from os import", "from os import listdir\nprint(listdir('.'))\n"),
    ("filesystem module: pathlib", "import pathlib\nprint(pathlib.Path('.').iterdir())\n"),
    ("filesystem module: shutil", "import shutil\nshutil.rmtree('/tmp')\n"),
    ("process spawning: subprocess", "import subprocess\nsubprocess.run(['ls'])\n"),
    ("process spawning: from subprocess import", "from subprocess import Popen\nPopen(['ls'])\n"),
    ("process spawning: multiprocessing", "import multiprocessing\nmultiprocessing.Process().start()\n"),
    ("networking: socket", "import socket\ns = socket.socket()\n"),
    ("networking: urllib", "import urllib.request\nurllib.request.urlopen('http://evil.example.com')\n"),
    ("networking: http.client", "import http.client\n"),
    ("dangerous import: sys", "import sys\nprint(sys.modules)\n"),
    ("dangerous import: importlib", "import importlib\nimportlib.import_module('os')\n"),
    ("dangerous import: pickle", "import pickle\npickle.loads(b'')\n"),
    ("dangerous import: ctypes", "import ctypes\n"),
    ("dangerous import: sqlite3", "import sqlite3\nsqlite3.connect('db/traceviz.db')\n"),
    ("reflection/escape: eval", "eval('1+1')\n"),
    ("reflection/escape: exec", "exec('print(1)')\n"),
    ("reflection/escape: compile", "compile('1+1', '<s>', 'eval')\n"),
    ("reflection/escape: __import__", "os_mod = __import__('os')\n"),
    ("reflection/escape: classic gadget chain", "x = ().__class__.__bases__[0].__subclasses__()\n"),
    ("reflection/escape: __globals__", "def f(): pass\nprint(f.__globals__)\n"),
    ("reflection/escape: __builtins__ attribute", "def f(): pass\nprint(f.__globals__['__builtins__'])\n"),
    ("reflection/escape: getattr gadget", "getattr(().__class__, '__bases__')\n"),
    ("reflection/escape: setattr with a literal dangerous attribute name",
     "def f(): pass\nsetattr(f, '__globals__', {})\n"),
    ("reflection/escape: dynamic type() construction", "Evil = type('Evil', (object,), {'x': 1})\n"),
    ("reflection/escape: globals()", "print(globals())\n"),
    ("reflection/escape: __subclasses__ direct", "class A: pass\nprint(A.__subclasses__())\n"),
]

for label, code in UNSAFE_SAMPLES:
    violation = find_safety_violation(code)
    check(f"rejected: {label}", violation is not None, violation or "NOT REJECTED (should have been)")


# ---------------------------------------------------------------- part 3 --
# Representative safe-but-tricky-looking code must be allowed.

print("\n=== Part 3: legitimate, sometimes tricky-looking DSA code must pass ===\n")

SAFE_SAMPLES = [
    ("plain loop/recursion", "def fib(n):\n    if n < 2: return n\n    return fib(n-1) + fib(n-2)\nprint(fib(10))\n"),
    ("heapq", "import heapq\nh = []\nheapq.heappush(h, 3)\nheapq.heappush(h, 1)\nprint(heapq.heappop(h))\n"),
    ("collections.deque/Counter", "from collections import deque, Counter\nq = deque([1,2,3])\nq.popleft()\nc = Counter('aabbc')\nprint(c)\n"),
    ("math module", "import math\nprint(math.sqrt(16), math.gcd(12, 18))\n"),
    ("bisect/itertools/functools (common, not in seed data but legitimate)",
     "import bisect, itertools, functools\nprint(bisect.bisect_left([1,2,3], 2))\nprint(list(itertools.combinations([1,2,3], 2)))\n@functools.lru_cache\ndef f(n): return n\n"),
    ("custom class with __init__/__repr__/__eq__/__lt__/__hash__",
     "class Node:\n    def __init__(self, val, next=None):\n        self.val = val\n        self.next = next\n    def __repr__(self):\n        return f'Node({self.val})'\n    def __eq__(self, other):\n        return self.val == other.val\n    def __lt__(self, other):\n        return self.val < other.val\n    def __hash__(self):\n        return hash(self.val)\nn = Node(1)\nprint(n)\n"),
    ("__class__ used harmlessly (isinstance-style check)",
     "class A: pass\nclass B(A): pass\nb = B()\nprint(b.__class__)\nprint(isinstance(b, A))\n"),
    ("list/dict/set comprehensions + generator", "squares = [x*x for x in range(10)]\ng = (x for x in range(5))\nd = {x: x*x for x in range(5)}\nprint(squares, list(g), d)\n"),
    ("nested functions, closures, decorators",
     "def make_counter():\n    count = 0\n    def inc():\n        nonlocal count\n        count += 1\n        return count\n    return inc\nc = make_counter()\nprint(c(), c())\n"),
    ("exception handling", "try:\n    1/0\nexcept ZeroDivisionError as e:\n    print('caught', e)\nfinally:\n    print('done')\n"),
    ("type() single-argument form (common, must NOT be flagged)", "x = [1,2,3]\nprint(type(x))\nif type(x) is list:\n    print('ok')\n"),
    ("string formatting/manipulation", "s = 'hello world'\nprint(s.split(), s.upper(), f'{s!r}')\n"),
    ("recursion with a class-based structure (tree)",
     "class TreeNode:\n    def __init__(self, val, left=None, right=None):\n        self.val, self.left, self.right = val, left, right\ndef inorder(root):\n    if not root: return []\n    return inorder(root.left) + [root.val] + inorder(root.right)\nprint(inorder(TreeNode(1)))\n"),
    ("dynamic method dispatch via getattr with a non-literal/ordinary name "
     "(the exact shape of Codeloupe's own design-circular-queue problem)",
     "class Q:\n    def push(self, x): return x\n    def pop(self): return None\nq = Q()\nfor op, arg in [('push', 1), ('pop', None)]:\n    method = getattr(q, op)\n    method(arg) if arg is not None else method()\n"),
]

for label, code in SAFE_SAMPLES:
    violation = find_safety_violation(code)
    check(f"allowed: {label}", violation is None, violation or "")

# Syntax errors must not crash the filter -- they're not this filter's job.
check("syntax error does not crash the filter (returns None)",
      find_safety_violation("def f(:\n    pass\n") is None)


print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S):")
    for f in FAILURES:
        print(" -", f)
    sys.exit(1)
else:
    print("ALL SAFETY-CHECK TESTS PASSED")
