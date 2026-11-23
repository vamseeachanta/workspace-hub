# WRK-1112 Plan — feat(review): Limit Cross-Review Iterations to 3

## Context

Unbounded cross-review loops waste AI quota and dilute feedback quality. Reviewers iterate
indefinitely rather than front-loading critical findings. This WRK caps all review cycles
at 3 iterations and surfaces that constraint in the reviewer prompt so feedback is
prioritised by impact.

## Approach (Route B — Medium)

### Phase 1 — Iteration tracking and cap enforcement

**`scripts/review/cross-review.sh`** (already implemented)
- `MAX_REVIEW_ITERATIONS=3` constant declared at top
- `get_review_iteration(WRK)` reads `assets/WRK-NNN/review-iteration.yaml`
- `increment_review_iteration(WRK)` writes/updates the YAML; returns new count
- Pre-dispatch check: if `current_iter >= 3` → exit 1 with explanatory message
- `increment_review_iteration` called before submit; new count drives preamble

**`scripts/review/submit-to-codex.sh`** (already implemented)
- Secondary guard: reads `review-iteration.yaml` from `REPO_ROOT`; exits 1 if `iteration >= 3`
- Prevents bypass of `cross-review.sh` by direct invocation

**`scripts/review/submit-to-gemini.sh`** (already implemented)
- Same secondary guard pattern as codex

### Phase 2 — Reviewer budget preamble

Injected into `PROMPT` after the template file is loaded in `cross-review.sh`:

```
You are reviewing WRK-NNN — iteration N of 3 (maximum).
This is a hard budget. After iteration 3 no further review passes will be accepted.
  * Iteration 1: blockers and security issues only — nothing else
  * Iteration 2: major design / correctness issues
  * Iteration 3: minor / style / nice-to-haves
Front-load your most critical finding first. Do not save critical issues for a later pass.
```

Preamble is skipped when `WRK_ID` is not set (non-WRK reviews remain unaffected).

### Phase 3 — SKILL.md documentation

- `work-queue/SKILL.md` §Cross-Review: "Maximum 3 iterations per WRK. Enforced by `review-iteration.yaml` in assets."
- `work-queue-workflow/SKILL.md` Stage 13 gate table: "cross-review iteration ≤ 3 (`review-iteration.yaml`)"
- `workflow-gatepass/SKILL.md` R-28: "cross-review iteration count ≤ 3, verified via `review-iteration.yaml`"

## Files Modified

| File | Change |
|------|--------|
| `scripts/review/cross-review.sh` | Cap check, iteration tracking, preamble injection |
| `scripts/review/submit-to-codex.sh` | Secondary cap guard |
| `scripts/review/submit-to-gemini.sh` | Secondary cap guard |
| `.claude/skills/coordination/workspace/work-queue/SKILL.md` | §Cross-Review updated |
| `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` | Stage 13 gate |
| `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` | R-28 added |

## TDD

`scripts/review/tests/test-wrk1112-iteration-cap.sh` — 5 test groups, 14 assertions:

1. `yaml_created_on_first_pass` — file exists, returns 1
2. `iteration_increments_correctly` — 1→2
3. `fourth_iteration_blocked_with_error` — exit 1 when iter==3
4. `preamble_includes_iteration_number_and_budget` — verifies "hard budget", "Front-load"
5. `cap_applies_to_codex_and_gemini_wrappers` — direct invocation blocked with REVIEW_ITERATION_CAP_EXCEEDED

**Current result: 14/14 PASS**

## Verification

```bash
bash scripts/review/tests/test-wrk1112-iteration-cap.sh
```

Expected: `Results: 14/14 passed, 0 failed`
