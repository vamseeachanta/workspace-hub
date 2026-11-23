# Operator Note — Promote Enforcement Fix 07e7e7d07

Date: 2026-04-20
Commit: `07e7e7d07` — `fix(enforcement): avoid plan-gate false negative with many markers`

## Recommendation
Yes — promote this fix into the main workspace-hub line before relying on further plan-gated implementation work.

## Why
This was a real blocker, not speculative cleanup.

Verified behavior from the handback + review trail:
- Stage 1 Task 11 commit was initially blocked by a false negative in `scripts/enforcement/require-plan-approval.sh`.
- Root cause was a `find ... | grep -q .` check running under `set -euo pipefail`.
- With many `.planning/plan-approved/*.md` markers, `grep -q` exited early after the first match and upstream `find` could surface non-zero via SIGPIPE, causing a false failure.

## What the fix changed
`07e7e7d07` replaces the approval-marker probe with a safer early-exit form:
- from: `find ... | grep -q .`
- to: `find ... -print -quit | grep -q .`

It also adds targeted regression coverage in:
- `tests/hooks/test-require-plan-approval.sh`

That test synthesizes a repo with 5000 approval markers and verifies `scripts/enforcement/require-plan-approval.sh --strict` exits 0 when approval evidence is valid.

## Promotion scope
Recommended scope:
- promote/cherry-pick `07e7e7d07` into `main` for `workspace-hub`
- treat it as an enforcement reliability fix, not as ecosystem-sync-only feature work

Not recommended scope:
- do not describe it as a cross-repo change for other repositories unless they share this exact enforcement script
- do not bundle unrelated Stage 1 feature commits with it if the goal is fast risk reduction

## Operator guidance
If the main checkout does not yet contain `07e7e7d07`, prefer landing that commit before more approved implementation sessions depend on the plan gate. It is small, verified, and directly reduces false-negative governance failures.
