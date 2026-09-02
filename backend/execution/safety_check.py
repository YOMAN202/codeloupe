"""
Static, pre-execution safety filter for learner-submitted code.

Read this module's docstring in full before changing the denylists below --
what this is, and just as importantly, what it explicitly is NOT.

WHAT THIS IS: a defense-in-depth filter, not a security boundary. It walks
the submission's AST (never executes anything, never even imports the
submission) and rejects code that imports a denylisted module, calls or
references a denylisted builtin, or touches a denylisted dunder attribute --
the small, well-known set of primitives Python code actually needs to touch
the filesystem, spawn a process, reach the network, or climb the object
graph to something more powerful than what it was handed (the classic
`().__class__.__bases__[0].__subclasses__()`-style gadget chains). Combined
with execution/sandbox.py's OS-level resource limits (memory/CPU/process-
count/file-size) and its process-group timeout kill, this closes the one
attack that's both catastrophic and trivial for this project's specific
deployment target: on PythonAnywhere's free tier, a submission's subprocess
runs as the exact same account/filesystem as the Flask app itself (no
chroot or container available to a free-tier account -- see
docs/architecture.md's "Deployment" section), so a single
`open(<path to traceviz.db or app.py>)` call -- no skill or exploit
required -- would otherwise read or corrupt every visitor's data and the
app's own source. That specific, trivial, zero-skill path is what this
filter is built to close.

WHAT THIS IS NOT: airtight. A static denylist over names is a known-
incomplete defense against a Turing-complete language -- Python's dynamic
name/attribute resolution means a sufficiently determined attacker can
sometimes reach the same primitives through a path this filter doesn't
happen to recognize (building a name at runtime via string concatenation,
an unusual reflection route this list doesn't name, a future CPython
internal this list predates). This raises the bar from "any anonymous
visitor, zero skill, one line" to "a skilled attacker who specifically sets
out to bypass a denylist" -- a materially different, and for a single-
operator public demo defensible, risk level. It is explicitly NOT a claim
that arbitrary code execution has been made safe in general, and it is not
a substitute for the real fix (a container/VM boundary, or moving execution
somewhere it's genuinely isolated, e.g. client-side) if this project's
threat model ever needs to change. See docs/architecture.md's sandbox
caveat for the fuller threat-model statement this filter is one layer of.

Runs ONLY against the learner's own raw submission, and only ever gets
CALLED before that submission is concatenated with any of this app's own
trusted harness/runner code (test_runner.py's grading harness, tracer.py's
trace harness, the appended test-case call in app.py's trace_problem) --
those legitimately use sys/json/types/traceback/collections/time
internally, so checking post-concatenation would flag Codeloupe's own
trusted code, not just a learner's. See app.py's `require_safe_code`
decorator for where this is actually invoked: once per API entry point
that accepts learner code, all seven of them, always before that code
reaches any harness or the sandbox.
"""
import ast

# Each entry: denylisted top-level module name -> one-line human reason.
# Matches the TOP-LEVEL package only ('os.path' is caught by 'os') --
# Python's import machinery always touches the top-level package first
# (import os.path binds `os` in the namespace, not `os.path` directly), so
# there's no dotted submodule form that bypasses a top-level-name check.
_DENYLISTED_MODULES = {
    "os": "filesystem/process access (the 'os' module)",
    "posix": "low-level OS access (the 'posix' module)",
    "nt": "low-level OS access (the 'nt' module)",
    "io": "low-level file access (the 'io' module)",
    "pathlib": "filesystem access (the 'pathlib' module)",
    "shutil": "filesystem access (the 'shutil' module)",
    "tempfile": "filesystem access (the 'tempfile' module)",
    "glob": "filesystem access (the 'glob' module)",
    "fileinput": "filesystem access (the 'fileinput' module)",
    "fcntl": "low-level file/process control (the 'fcntl' module)",
    "subprocess": "process spawning (the 'subprocess' module)",
    "multiprocessing": "process spawning (the 'multiprocessing' module)",
    "pty": "process spawning (the 'pty' module)",
    "signal": "process/signal control (the 'signal' module)",
    "resource": "process resource-limit control (the 'resource' module)",
    "ctypes": "low-level system access (the 'ctypes' module)",
    "cffi": "low-level system access (the 'cffi' module)",
    "socket": "network access (the 'socket' module)",
    "socketserver": "network access (the 'socketserver' module)",
    "asyncio": "network/process access (the 'asyncio' module)",
    "ssl": "network access (the 'ssl' module)",
    "urllib": "network access (the 'urllib' module)",
    "http": "network access (the 'http' module)",
    "ftplib": "network access (the 'ftplib' module)",
    "smtplib": "network access (the 'smtplib' module)",
    "poplib": "network access (the 'poplib' module)",
    "imaplib": "network access (the 'imaplib' module)",
    "telnetlib": "network access (the 'telnetlib' module)",
    "xmlrpc": "network access (the 'xmlrpc' module)",
    "requests": "network access (the 'requests' module)",
    "httpx": "network access (the 'httpx' module)",
    "sys": "interpreter/reflection access (the 'sys' module)",
    "importlib": "dynamic import/reflection (the 'importlib' module)",
    "runpy": "dynamic code execution (the 'runpy' module)",
    "pkgutil": "import-system introspection (the 'pkgutil' module)",
    "imp": "dynamic import/reflection (the 'imp' module)",
    "inspect": "reflection/introspection (the 'inspect' module)",
    "gc": "runtime object-graph introspection (the 'gc' module)",
    "code": "dynamic code execution (the 'code' module)",
    "codeop": "dynamic code execution (the 'codeop' module)",
    "ast": "code introspection/construction (the 'ast' module)",
    "pickle": "arbitrary deserialization (the 'pickle' module)",
    "marshal": "arbitrary deserialization (the 'marshal' module)",
    "shelve": "arbitrary deserialization (the 'shelve' module)",
    "dbm": "filesystem-backed storage (the 'dbm' module)",
    "sqlite3": "database file access (the 'sqlite3' module)",
    "mmap": "low-level memory/file mapping (the 'mmap' module)",
    "platform": "system/environment introspection (the 'platform' module)",
    "getpass": "system/user introspection (the 'getpass' module)",
    "pwd": "system account introspection (the 'pwd' module)",
    "grp": "system account introspection (the 'grp' module)",
}

# Bare names (builtins, mostly) that reach dangerous functionality
# regardless of any import statement -- these are always available in
# ordinary Python without importing anything, so they need their own check
# independent of _DENYLISTED_MODULES above.
_DENYLISTED_NAMES = {
    "open": "opens files",
    "__import__": "dynamically imports modules",
    "eval": "evaluates arbitrary code",
    "exec": "executes arbitrary code",
    "compile": "compiles arbitrary code",
    "globals": "accesses the global namespace",
    "vars": "accesses an object's/module's namespace dict",
    "breakpoint": "drops into an interactive debugger",
    "__builtins__": "direct access to the builtins namespace",
}

# Dunder ATTRIBUTES (obj.__xxx__, not the bare name) that are the actual
# load-bearing steps of the classic Python sandbox-escape gadget chains --
# walking from any ordinary object to a live reference to something like
# os.system without ever writing the word "os". Deliberately NOT a blanket
# dunder ban: plenty of dunders (__init__, __repr__, __eq__, __lt__,
# __len__, __iter__, __hash__, __class__ itself, ...) are ordinary,
# legitimate Python that real DSA solutions define and use constantly --
# custom Node/comparator classes especially (see backend/db/seed_problems.py
# -- every linked-list/tree problem's reference solution defines its own
# __init__). Only the specific handful of attributes that are actually
# dangerous are listed here.
_DENYLISTED_ATTRS = {
    "__globals__": "reaches a function's global namespace",
    "__builtins__": "reaches the builtins namespace",
    "__subclasses__": "walks the live class hierarchy (a classic sandbox-escape gadget)",
    "__bases__": "walks the live class hierarchy (a classic sandbox-escape gadget)",
    "__base__": "walks the live class hierarchy (a classic sandbox-escape gadget)",
    "__mro__": "walks the live class hierarchy (a classic sandbox-escape gadget)",
    "__code__": "reaches a function's raw bytecode object",
    "__closure__": "reaches a function's captured closure cells",
    "__func__": "unwraps a bound method to its underlying function",
    "__self__": "reaches the object a bound method is attached to",
    "__getattribute__": "overrides/reaches low-level attribute lookup",
    "__reduce__": "a pickle-protocol hook, a known deserialization gadget",
    "__reduce_ex__": "a pickle-protocol hook, a known deserialization gadget",
    "__loader__": "reaches the module import machinery",
    "__spec__": "reaches the module import machinery",
    "__dict__": "reaches an object's/class's/module's raw namespace dict",
}


def find_safety_violation(code: str) -> str | None:
    """Returns a short, human-readable reason the submission was rejected,
    or None if it passes this filter.

    Never raises: code that doesn't even parse isn't a safety concern for
    THIS filter specifically -- it can't call anything, safe or not -- so a
    SyntaxError here just means "no violation found," and the normal
    execution path reports the syntax error to the learner exactly as it
    already does today (this filter is additive, never a replacement for
    that existing error reporting)."""
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError):
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in _DENYLISTED_MODULES:
                    return f"imports a disallowed module ({_DENYLISTED_MODULES[top]})"
        elif isinstance(node, ast.ImportFrom):
            top = (node.module or "").split(".")[0]
            if top in _DENYLISTED_MODULES:
                return f"imports a disallowed module ({_DENYLISTED_MODULES[top]})"
        elif isinstance(node, ast.Name):
            if node.id in _DENYLISTED_NAMES:
                return f"uses a disallowed name ({_DENYLISTED_NAMES[node.id]})"
        elif isinstance(node, ast.Attribute):
            if node.attr in _DENYLISTED_ATTRS:
                return f"accesses a disallowed attribute ({_DENYLISTED_ATTRS[node.attr]})"
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            # type(name, bases, namespace) -- the 3-argument form --
            # dynamically constructs a brand-new class at runtime, the same
            # category of risk as the denylisted names above. The single-
            # argument form (type(x), by far the common case in ordinary
            # code, e.g. checking type(x) is list) is completely untouched
            # by this check.
            if node.func.id == "type" and (len(node.args) >= 3 or len(node.keywords) > 0):
                return "uses the 3-argument form of type() to construct a class dynamically"

            # getattr(obj, name)/setattr(obj, name, val)/delattr(obj, name)
            # are, on their own, completely ordinary Python -- one of
            # Codeloupe's own curated problems (design-circular-queue)
            # legitimately dispatches to a method by name this way
            # (`getattr(queue, op_name)`), and blanket-banning the name
            # would break it. What's actually dangerous is reaching for one
            # of the SPECIFIC denylisted attributes above THIS way instead
            # of via `.` -- so this only fires when the attribute-name
            # argument is a literal string matching that same list, not
            # for a dynamic/variable name (which can't be inspected
            # statically anyway, and is exactly the legitimate-dispatch
            # shape).
            if node.func.id in ("getattr", "setattr", "delattr") and len(node.args) >= 2:
                attr_arg = node.args[1]
                if (
                    isinstance(attr_arg, ast.Constant)
                    and isinstance(attr_arg.value, str)
                    and attr_arg.value in _DENYLISTED_ATTRS
                ):
                    return (
                        f"uses {node.func.id}() to reach a disallowed attribute "
                        f"({_DENYLISTED_ATTRS[attr_arg.value]})"
                    )

    return None
