# Issue #1839 — Remaining Acceptance Items Extraction

## Context

Issue #1839 ("Workflow hard-stops and session governance") has 10 acceptance criteria (ACs) and a 4-phase implementation plan. Phases 1, 2, and 2b landed on 2026-04-09 across commits `e69473081`, `fdb7c5cf0`, and `76c7af5ce`. This extraction identifies what concrete work remains.

## Why #1839 stays open

The checkpoint data model and tool-call ceiling hook are operational, but 8 of 10 acceptance criteria remain unmet — the three user hard-stops lack hook-level enforcement, TDD/review gates are advisory-only, and the four Phase 3/4 skills and Hermes orchestration haven't been started.

## Remaining concrete items

### Phase 3 — Restore lost infrastructure & wire remaining enforcement

1. **Wire `plan-approval` hard-stop into a PreToolUse hook** — block `Write|Edit` when no plan-approval marker exists (e.g., `.planning/plan-approved/<issue>.md`). Currently only a YAML entry; no hook prevents implementation without approval. *(AC #1)*

2. **Wire `review-verdict` hard-stop into a pre-push or PreToolUse hook** — block `git push` (or Bash push commands) when cross-review has not been completed. Currently advisory only. *(AC #1)*

3. **Promote `session-close` checkpoint to `enforced: true`** in `governance-checkpoints.yaml` and add a Stop hook that requires user confirmation of session summary before ending. *(AC #1)*

4. **Enforce TDD gate via pre-commit hook** — add a pre-commit script that checks for test files modified alongside implementation files, or integrate into `gsd-validate-commit.sh`. Currently `tdd-red` is `enforced: true` in YAML but has zero runtime enforcement. *(AC #3)*

5. **Wire consecutive-error tracking into `session-governor-check.sh`** — currently passes `--consecutive-errors 0` hardcoded. Needs to read from `.claude/state/session-signals/` or session log to count repeated identical errors. *(error-loop-breaker gap from Phase 2b)*

6. **Promote review gate to strict mode** — set `REVIEW_GATE_STRICT=1` as default in `cross-review-gate.sh` and flip `pre-push-review` to `enforced: true` in `governance-checkpoints.yaml`. *(AC #7)*

7. **Align or remove old `tool-call-ceiling.sh` (PostToolUse, 500 ceiling)** — redundant with new `session-governor-check.sh` (PreToolUse, 200 ceiling). Either remove entirely or align to 200. *(known gap from Phase 2b)*

8. **Rebuild `session-start-routine` skill** in `.claude/skills/` — pre-flight checks, context loading, prior-state validation, tool readiness. Was lost during GSD migration. *(AC #4)*

9. **Create `session-corpus-audit` skill** — analyze session quality trends, identify high-churn patterns, report waste metrics. Never existed. *(AC #5)*

10. **Promote `comprehensive-learning` into skills tree** — currently runs via cron (`scripts/cron/`) but is invisible to skill discovery. Needs a skill wrapper. *(AC #6)*

11. **Create `cross-review-policy` skill** — actionable skill wrapping `docs/standards/AI_REVIEW_ROUTING_POLICY.md`. Referenced but never created.

12. **Create `dev-workflow` skill** — encapsulates the full Issue-to-Close lifecycle as an invocable skill. Referenced but never created.

### Phase 4 — Hermes orchestration

13. **Hermes gate-transition management** — Hermes orchestrates session lifecycle gates (plan-approval, review-verdict, session-close) and enforces hard-stops. *(AC #1 full completion)*

14. **Hermes session metrics + report generation** — track tool calls, time, credits, gate pass/fail per session; generate structured report at session close. *(AC #8)*

15. **Inter-session state validation** — Hermes checks last session state (orphaned work, uncommitted changes, pending reviews) before starting new work. *(AC #10)*

16. **Multi-provider dispatch** — Hermes routes to Claude/Codex/Gemini per the routing matrix defined in `AI_REVIEW_ROUTING_POLICY.md`. Ties to #1838.

## Acceptance criteria coverage

| AC | Description | Status | Remaining Item(s) |
|----|-------------|--------|--------------------|
| 1 | 3 hard stops non-bypassable | Partial | #1, #2, #3, #13 |
| 2 | Tool-call ceiling (200) operational | **Done** | — |
| 3 | TDD gate via pre-commit hook | Not started | #4 |
| 4 | session-start-routine skill | Not started | #8 |
| 5 | session-corpus-audit skill | Not started | #9 |
| 6 | comprehensive-learning in skill tree | Not started | #10 |
| 7 | Review gate strict by default | Not started | #6 |
| 8 | Hermes session report at close | Not started | #14 |
| 9 | Zero runaway sessions (>500 calls) | Measurable | #7 (align ceilings) |
| 10 | Inter-session state validation | Not started | #15 |

## Recommendation — next best implementation slice

**Items #1 + #6 + #7** are the highest-value next slice:

- **#1 (plan-approval hook)** — directly prevents the most damaging failure mode (implementing the wrong thing). The approval-marker pattern (`.planning/plan-approved/<issue>.md` checked by PreToolUse hook) is already sketched in the Apr 5 comment and follows the existing `session-governor-check.sh` convention.
- **#6 (review gate strict)** — a one-line flip (`enforced: false` to `true` in YAML + env default change) that closes the biggest compliance gap (542 commits without review).
- **#7 (remove old 500-ceiling hook)** — pure cleanup, eliminates confusion between two competing ceiling mechanisms.

These three can land in a single commit, touch only hook/config files, and close AC #7 plus advance AC #1 — the best effort-to-impact ratio of any remaining work.
