# Post-redraft adversarial cross-review summary — 2026-04-22

## Scope
Fresh approval-stage rerun after redrafting the following plans:
- #2311 — `docs/plans/2026-04-17-issue-2311-stage-transition-stale-reference-cleanup.md`
- #2312 — `docs/plans/2026-04-17-issue-2312-lifecycle-script-authority-cleanup.md`
- #2332 — `docs/plans/2026-04-22-issue-2332-provider-audit-python3-runtime-cleanup.md`
- #2333 — `docs/plans/2026-04-22-issue-2333-provider-audit-drift-classification-expansion.md`

Review providers:
- Codex
- Gemini

## Verdict matrix

| Issue | Codex | Gemini | Approval-stage status |
|---|---|---|---|
| #2311 | MAJOR | APPROVE | blocked (single MAJOR rule) |
| #2312 | MAJOR | MAJOR | blocked |
| #2332 | MAJOR | MINOR | blocked (single MAJOR rule) |
| #2333 | MAJOR | MAJOR | blocked |

## Net result
All four plans remain blocked for approval-stage advancement.

## What improved
- #2311 improved from MAJOR/MAJOR to MAJOR/APPROVE.
- #2332 improved from MAJOR/MAJOR to MAJOR/MINOR.
- #2312 and #2333 remain MAJOR/MAJOR, but the blocker set is narrower and more concrete than before the redraft.

## Current blocker summary by issue

### #2311
Remaining Codex blockers:
- tooling/test-source bucket still unresolved:
  - `tests/helpers/stale_reference_docs.py`
  - `scripts/analysis/provider_session_ecosystem_audit.py`
  both still intentionally contain the stale names, but the plan taxonomy does not classify them clearly.
- some scan claims are still asserted rather than carried by attested evidence.
- the `.claude/docs/data-format-guide.md` rewrite target still leaves the replacement direction partly open.

### #2312
Remaining blockers from Codex/Gemini:
- evidence is still not tight enough for several content-based claims in the plan.
- the plan references latest review artifacts as if they were established evidence, but the cited `2026-04-22` review files were empty at review time.
- test design still has a scope contradiction:
  - it claims to scan only a fixed protected set,
  - while also claiming to exclude/classify broader surfaces that would not be scanned.
- control-plane surfaces (`docs/standards/CONTROL_PLANE_CONTRACT.md`, `config/agents/...`) are not yet classified consistently enough.

### #2332
Remaining blockers:
- deliverable / acceptance framing still contradicts approval readiness by saying success is to remain `draft`.
- weekly publication surface is still partly open in the plan.
- `AGENTS.md` remains conditional (`if needed`) rather than decided.
- prior-audit delta source / no-history behavior is still not concretely locked.
- Gemini only returned MINOR; Codex is the remaining blocker.

### #2333
Remaining blockers from Codex/Gemini:
- approval-state contradiction remains (`approval-ready` vs `remain in draft`).
- plan still cites review artifacts that were empty at review time.
- TDD coverage still misses some required contract assertions:
  - zero-gap reconciliation case
  - JSON scope-note assertions
  - direct precedence guards across `symbolic`, `sibling_repo`, `repo`
- Gemini flagged a scope mismatch: issue title emphasizes transient worktree/scratch-path separation, while the plan over-focuses on generated-site/non-repo artifact classification unless scratch/worktree matchers are made explicit.

## Artifacts
- `scripts/review/results/2026-04-22-plan-2311-codex.md`
- `scripts/review/results/2026-04-22-plan-2311-gemini.md`
- `scripts/review/results/2026-04-22-plan-2312-codex.md`
- `scripts/review/results/2026-04-22-plan-2312-gemini.md`
- `scripts/review/results/2026-04-22-plan-2332-codex.md`
- `scripts/review/results/2026-04-22-plan-2332-gemini.md`
- `scripts/review/results/2026-04-22-plan-2333-codex.md`
- `scripts/review/results/2026-04-22-plan-2333-gemini.md`

## Recommended next move
Do not surface any of these four for approval yet.
If continuing, the highest-leverage next pass is:
1. finalize the remaining open taxonomy/contract decisions in #2311, #2332, and #2333,
2. fix evidence-tightness and review-artifact references in #2312 and #2333,
3. rerun cross-review once more only after those exact blockers are patched.
