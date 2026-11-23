# Dispatch/readiness review gotchas

Use this reference when executing approved GitHub issues that add multi-machine dispatch, readiness, or control-plane checks.

## What triggered this note

A multi-machine Telegram/Hermes dispatch issue passed targeted tests, but adversarial review still found MAJOR blockers because tests did not yet cover all emitted surfaces and Git worktree shapes.

## Durable lessons

1. **Redaction must cover every output surface**
   - Do not test only the direct validation-error formatter.
   - Also test the generic status renderer, CLI output, evidence files, warning/failure/missing-data lists, registry-derived text, and any closeout/status summaries.
   - Add negative assertions for private Telegram/user metadata and credential-like fragments in all of those surfaces.

2. **Token-fragment leakage can survive full-token redaction**
   - A helper that redacts the full token or token-aware validation reason is not enough if other status paths can carry phrases such as `token tail <fragment>` or `token fragment <fragment>`.
   - Prefer contextual redaction of high-risk phrases rather than broad substring deletion that corrupts ordinary words or the `[REDACTED]` marker.

3. **Git readiness must not assume `.git` is a directory**
   - Valid Git worktrees often have `.git` as a file pointing to common metadata.
   - Use `git rev-parse --is-inside-work-tree`, `git rev-parse --git-dir`, and upstream/ahead/behind commands instead of filesystem-shape checks.
   - Add a regression test that creates a linked worktree and proves readiness treats a clean/synced worktree as Git-backed, not non-git.

4. **MAJOR review means no commit/push/closeout**
   - Passing targeted tests is not enough after a MAJOR review.
   - Fix the blocker, regenerate the review prompt from the latest diff, rerun adversarial review, then commit only on PASS or documented MINOR.

## Suggested test checklist

- CLI output redacts token fragments and Telegram identifiers.
- Evidence JSON/YAML redacts token fragments and Telegram identifiers.
- Failure/warning/missing-data strings are rendered through the same redaction path.
- Safe operational slugs remain readable.
- `[REDACTED]` is not corrupted by fragment redaction.
- Linked Git worktree with `.git` file passes Git detection when clean/synced.
- Dirty, ahead, behind, no-upstream, and non-git states fail closed.
