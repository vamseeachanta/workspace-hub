# Plan for #3316: SessionEnd hook auto-emits the live-link review

> **Status:** plan-approved (user directed "perform next logical step" 2026-06-28)
> **Complexity:** T1 · **Date:** 2026-06-28 · **Lane:** lane:claude
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3316
> **Closes the loop on:** #3298 (render) → #3306 (lean) → #3311 (--from-git) ; slice of #2110

## Resource Intelligence
- Found: `scripts/workflow/build_session_review.py --from-git` (#3311) — the deriver the hook invokes.
- Found existing hooks: `session-review.sh` (Stop — raw learning-signal capture, UNRELATED), `session-logger.sh` (raw session log → `.claude/state/sessions/`). New hook is distinctly named `session-review-page.sh`.
- Found hook conventions: `.claude/settings.json` registers SessionStart/Stop/Pre/PostToolUse; hooks resolve `${WORKSPACE_HUB:-…}`, append `2>/dev/null || true`, carry `timeout`. notify.sh signature `<source> <job> <status> [details]`.
- Gap: no SessionEnd auto-emit; payloads are hand-run.

## Implementation (TDD) — DONE in this PR
1. `.claude/hooks/session-review-page.sh` (two modes): `start` records `origin/main` base; `emit` derives `<base>..origin/main` → renders the lean page → notifies. **Fail-open (always exit 0)**, **no commit/push** (opt-in `SESSION_REVIEW_STAGE=1` only stages; `SESSION_REVIEW_PAGE=false` disables).
2. Docs + the exact registration snippet in `SESSION-GOVERNANCE.md`.
3. Tests: existence/executable, disable switch, fail-open outside a repo, unknown mode, **never commits/pushes by default**, activation documented.

## Deliberately NOT auto-done
- **Registering the hooks in `.claude/settings.json`** auto-executes commands at session start/end → a user-approved activation step. The script ships **inert**; the snippet is in the docs/PR for the user to apply. (Auto-registration was correctly blocked by the self-modification guard.)

## Acceptance criteria
- Hook generates the lean page from git at session end and notifies; never blocks a session (fail-open); no auto-commit. ✓
- Tests cover fail-open + guards + no-commit-default + documented activation. ✓
- Activation is an explicit, documented user step. ✓
