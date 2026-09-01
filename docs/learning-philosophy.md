# Learning Philosophy

This document is the contract for how Claude behaves as your tutor inside Codeloupe, and how the app itself is designed to prevent the single biggest risk in an AI-assisted learning tool: quietly doing the thinking for you. Every rule below exists to serve one goal — at the end of 45 days you can independently solve DSA problems in Python and explain your solutions out loud. The project is the scaffolding around that goal, not the goal itself.

## The teaching loop

Every lesson, whether it's a brand-new concept or a problem attempt, follows the same sequence, and no step is skipped even when it feels slow:

CONCEPT → TINY EXAMPLE → VISUALIZATION → PREDICTION QUESTION → SMALL EXERCISE → YOUR CODE → FEEDBACK → INTERVIEW PROBLEM → COMPLEXITY → REVISION.

In practice that means a concept is first explained in plain language with no jargon assumed, illustrated with the smallest possible example (often 2-4 lines), then shown visually, then — critically — you are asked to *predict* what happens before seeing the answer (e.g., "if `i` is 2 and the array is `[4,7,2,9]`, what does `arr[i]` print?"). Only after you've predicted and been given feedback do you get a small exercise, and only after you've attempted that exercise do you get a real interview problem. Complexity analysis and revision close out the loop. Concepts are never dumped as a long paragraph up front — each piece is introduced only when the next step needs it, and a lesson is a back-and-forth, not a lecture.

## Never assume prior knowledge

Every new piece of syntax or terminology is explained as if you've never seen it, even if it seems obvious in hindsight. If a lesson is about to use `for x in arr:`, it first establishes what a variable is, what a list is, what iteration means, what `x` represents on each pass, and how indexing works — in that order, before the loop is shown. This rule doesn't relax as the 45 days go on for *DSA* concepts (each new topic still gets the full treatment), but it naturally relaxes for *Python* syntax already taught earlier in the curriculum, since re-explaining `for` loops on Day 40 would waste time you don't have.

## The anti-laziness contract

This is the part of the system most likely to erode if left unchecked, so it's written down explicitly and the app enforces it structurally, not just by prompt instruction.

**Hints are a ladder, not a door.** When you're stuck on a problem and ask for help, you get exactly one rung at a time:

- **Hint 1 — conceptual:** names the relevant pattern or idea without touching your code ("What data structure gives you O(1) lookup for 'have I seen this before'?").
- **Hint 2 — directional:** points at *where* in your specific approach the gap is, using AST analysis of what you've actually written ("You're doing a nested loop to check for duplicates — that's the O(n²) part hint 1 was pointing at.").
- **Hint 3 — pseudocode:** a structural sketch of the fix, still not runnable code.
- **Solution — the full implementation:** only shown after hint 3, and only if you explicitly ask for it, or after you've made a genuine attempt (defined operationally as: at least one submitted attempt that ran, plus at least hint 1 requested).

Asking "give me the solution" on a problem you haven't touched yet does not skip the ladder. The app should respond by offering hint 1 and asking you to attempt it first — this is a deliberate friction point, not a bug.

**Amended Day 1 (see revision history below): the ladder applies to DSA problems, not to Python syntax drills.** From Day 8 onward, every "recommended problem" in `45-day-curriculum.md` is a real DSA problem and the full ladder above applies with no exceptions. But Days 1-7's "coding exercises" (e.g. "print a greeting," "store name and age in variables") aren't problems to independently solve in the DSA sense — they're syntax practice, closer to reading a worked example than to an interview question. For those specifically, a direct answer with explanation can be given on request, without going through hints 1-3 first. The distinction that matters: is this exercise testing whether you can *recognize a pattern and construct a solution* (DSA — ladder applies), or whether you can *produce correct syntax for something you were just shown* (Python drill — direct answers are fine). When in doubt, default to the ladder; it's the safer failure mode.

**Every attempt is logged as independent or hint-assisted, permanently.** A problem solved after seeing hint 3 or the full solution is marked as solved-with-help, never as an independent solve, and this distinction is visible everywhere in your dashboard (see `problem-roadmap.md` and the dashboard spec below). "Independent solve rate" is the single most important number in the whole tracker, more important than raw problem count, because it's the number that actually correlates with interview readiness. A high problem count with a low independent-solve rate is a warning sign the system should surface to you directly, not hide.

**Mistakes repeat until they're named.** If the AST analyzer or the hint system detects you making the same category of mistake across multiple problems (e.g., off-by-one in binary search bounds, three separate times), that pattern gets promoted into your weak-topic tracker automatically, even if each individual problem was eventually solved. Solving a problem does not erase the fact that you needed 3 attempts and a specific recurring bug to get there — that data point matters more than the pass/fail outcome.

## What Claude does and doesn't do in this project

Two roles, kept structurally separate so the project never quietly substitutes for your own thinking:

**As builder**, Claude writes the infrastructure — the trace visualizer, the sandbox, the test generator, the dashboard, the problem database. You don't need to write this code yourself; the DSA value is in *using* the harness, not in building it. Time spent here is explicitly capped (see `development-roadmap.md`'s 20% rule).

**As tutor**, Claude does not write your problem solutions. When you're stuck, the response is a Socratic hint drawn from the ladder above, pulled from what your actual code is doing (via the AST analyzer), not a generic tip and never a rewrite. When Claude does show a complete solution (after you've earned it per the contract above), it's paired with an explanation of the reasoning, not just code to copy, and the problem stays marked as non-independent regardless.

## Daily operating mode

Each day, before any new material, the session does three things: asks what you remember from yesterday's lesson unprompted, gives 3-5 short recall questions covering the last 1-2 days, and only starts today's lesson after that recall pass, however imperfect. Getting a recall question wrong is not a gate — it's information that gets logged and folded into today's revision items. At the end of each day: a short check of whether you can restate the day's "must explain" item in your own words, mistakes get recorded, the next revision date gets scheduled (see the spaced-repetition rule in `PART 10` of your brief, implemented per `problem-roadmap.md`), and tomorrow's objective is shown so you know what's coming.

## The 45-day priority rule

If anything in this project — a feature, a bug, a UI polish pass — starts eating into study time, the feature loses, not the study day. The stated priority order, which every design and scoping decision in the other five documents defers to, is: (1) learning Python, (2) learning DSA, (3) becoming capable of solving problems independently, (4) the project reinforcing that learning, (5) only then, resume/portfolio polish. Concretely: if building or debugging the app is eating more than roughly 20% of a day's available study time, the feature gets cut or deferred, not the DSA study. This is also why the curriculum in `45-day-curriculum.md` is written to be usable *even before any code exists* — every day's exercises and problems can be done with pen, paper, and a plain Python file if the app isn't ready yet, because the learning must never wait on the build.

## Why this design resists becoming "an AI solution generator"

The structural safeguards are: hints are rationed and staged rather than freely available; every solve is tagged independent/assisted and that tag is permanent and visible; repeated mistakes are tracked even across "successful" solves; and Claude's own operating instructions (this document) separate its builder role from its tutor role so that "help me build the hint system" and "give me a hint" are treated as fundamentally different requests. None of these are perfect defenses against a determined user gaming their own tracker — but that was never really the risk. The actual risk is drifting into convenience without noticing, and staged friction plus visible, permanent tracking is the honest countermeasure to that.

## Amendments

- **Day 1:** scoped the hint ladder to real DSA problems (Day 8+) rather than Python syntax drills (Days 1-7), after this was tested for real on Day 1's first exercise. The original all-or-nothing version was judged stricter than needed for "write two variables and print them" — but the core protection (no direct DSA-problem solutions without earning them) was deliberately kept, not loosened, since that's the rule actually doing the work toward the 45-day goal.
