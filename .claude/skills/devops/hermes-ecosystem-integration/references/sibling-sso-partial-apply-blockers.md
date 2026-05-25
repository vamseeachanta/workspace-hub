# Sibling SSoT Partial-Apply Blockers

Use this when implementing or reviewing sibling-repo single-source-of-truth repair flows for Hermes/Codex/Gemini/AGENTS wiring.

## Durable lesson

A fail-closed repair command can still be too coarse if it groups safe repairable actions and unresolved blockers into one per-repo `blocked_actions` bucket. In sibling SSoT work, this commonly appears when a repo has:

- repairable `.codex/skills` or `.gemini/skills` symlink rewrites, and
- an unresolved `AGENTS.md` blocker such as a missing contract file.

If `--apply` aborts before applying the safe symlink repairs, the ecosystem remains red even though some state could have been safely advanced. Treat this as an execution-design question, not as proof that the whole issue is blocked.

## Preferred design

1. Build a manifest with explicit action classes:
   - `repairable_actions`: deterministic, reversible, path-scoped repairs such as rewriting known skill symlinks.
   - `blocked_actions`: missing/non-regular/symlinked `AGENTS.md`, ambiguous prose references, unsafe ownership, or anything outside approved scope.
2. In `--apply`, apply only `repairable_actions` when all of the following are true:
   - action path is inside the intended sibling repo,
   - action kind is allowlisted,
   - rollback/backup behavior is defined where needed,
   - post-apply verification checks the exact repaired path.
3. Preserve unresolved `blocked_actions` in the final report and non-zero exit/status summary when acceptance criteria require all repos green.
4. Do not close the issue until the live checker distinguishes:
   - repaired state,
   - residual blockers,
   - out-of-scope follow-up items.

## Review questions

- Does the manifest separate safe repairs from blockers, or does one blocker prevent every repair in that repo?
- Does `--apply` fail closed for unsafe contract changes while still allowing allowlisted symlink repairs?
- Does closeout evidence include both targeted tests and the full live checker for the named machine?
- Are missing `AGENTS.md` contracts handled by approved scope, follow-up issue creation, or explicit residual blocker reporting?

## Anti-pattern

Do not report SSoT as fixed after targeted unit tests pass if `check-sibling-sso-flow.py --machine <machine>` still reports `skills: fail` or `harness_contracts: fail`. Targeted tests validate mechanics; the full registry checker validates ecosystem readiness.
