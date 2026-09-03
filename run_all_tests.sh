#!/usr/bin/env bash
# Runs the full regression suite in one shot: backend smoke/live-grading
# checks, then every Playwright E2E suite, each against a freshly reseeded
# database (see docs/decisions.md's "reseed before each exact-count-
# assertion suite" convention -- several E2E suites assert exact counts,
# e.g. "exactly 2 mistakes logged this session", which would be corrupted
# by attempts left over from a previous suite's run).
#
# Requires the backend (port 5001) and frontend (port 5173) already
# running -- this script doesn't manage their lifecycle, since how you
# start them (plain `python3 app.py` / `npm run dev`, a process manager,
# etc.) is your choice, not this script's. See README.md's "Running it
# locally" section.
#
# Usage: ./run_all_tests.sh   (from the repo root)

set -uo pipefail
cd "$(dirname "$0")"

BACKEND_URL="http://127.0.0.1:5001/api/health"
FRONTEND_URL="http://127.0.0.1:5173/"
PASS=0
FAIL=0
FAILED_NAMES=()

log() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }

if ! curl -sf "$BACKEND_URL" > /dev/null; then
  echo "Backend not reachable at $BACKEND_URL -- start it first (cd backend && python3 app.py)." >&2
  exit 1
fi
if ! curl -sf "$FRONTEND_URL" > /dev/null; then
  echo "Frontend not reachable at $FRONTEND_URL -- start it first (cd frontend && npm run dev)." >&2
  exit 1
fi

reseed() {
  (cd backend && rm -f db/traceviz.db && python3 db/init_db.py) > /tmp/run_all_tests_reseed.log 2>&1
  if [ $? -ne 0 ]; then
    echo "Reseed failed -- see /tmp/run_all_tests_reseed.log" >&2
    cat /tmp/run_all_tests_reseed.log >&2
    exit 1
  fi
}

run() {
  local name="$1"
  local cmd="$2"
  log "$name"
  reseed
  if eval "$cmd"; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    FAILED_NAMES+=("$name")
  fi
}

# ---- backend-only checks (no browser) -----------------------------------
run "backend smoke tests (test_endpoints.py)"              "(cd backend && python3 test_endpoints.py)"
run "DB migration path (test_migration.py)"                "(cd backend && python3 test_migration.py)"
run "live grading verification (verify_all_live.py)"       "(cd backend && python3 verify_all_live.py)"
run "approach-comparison baselines (verify_approach_baselines.py)" "(cd backend && python3 verify_approach_baselines.py)"

# ---- Playwright E2E suites (frontend + backend together) ----------------
run "core E2E (e2e_test.py)"                                "python3 e2e_test.py"
run "central workflow, 4 variants (e2e_central_workflow_test.py)" "python3 e2e_central_workflow_test.py"
run "learning features (e2e_learning_features_test.py)"    "python3 e2e_learning_features_test.py"
run "visualizers, all 9 kinds (e2e_visualizers_test.py)"    "python3 e2e_visualizers_test.py"
run "mistake journal / revision / practice (e2e_mistake_journal_test.py)" "python3 e2e_mistake_journal_test.py"
run "approach comparison (e2e_approach_comparison_test.py)" "python3 e2e_approach_comparison_test.py"
run "teaching system (e2e_teaching_test.py)"                "python3 e2e_teaching_test.py"
run "production-fix verification (e2e_production_fixes_test.py)" "python3 e2e_production_fixes_test.py"

# Leave a pristine, freshly seeded DB behind rather than whatever state
# the last suite left it in.
reseed

log "SUMMARY"
echo "$PASS suites passed, $FAIL suites failed."
if [ $FAIL -gt 0 ]; then
  printf 'Failed: %s\n' "${FAILED_NAMES[@]}"
  exit 1
fi
echo "All suites passed."
