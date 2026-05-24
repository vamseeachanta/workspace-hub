# Issue #2775 Plan Revision Notes — 2026-05-21

## Work performed

- Delegated approval-safe hardening to Claude CLI and Codex CLI.
- Patched the local #2775 plan draft and `docs/plans/README.md` row.
- Did not implement code, modify sibling repos, touch live `~/.hermes`, change GitHub labels, or apply repairs.

## Key plan changes

- Made `config/workstations/registry.yaml` the authoritative topology source for machine roots and sibling repo scope.
- Reframed `scripts/_core/sync-agent-configs.sh` work as a structural resolver change, not a token-only change: registry-first resolver, `--machine`, `__TIER1_REPO_ROOT__`, unresolved-token scan, stale nested path scan, divergence checks.
- Removed local approval-marker requirements from #2775 apply semantics. `--apply` now requires live GitHub `status:plan-approved` only and explicitly ignores local marker files.
- Added dev-secondary ground-truth gate before mutating registry values for ace-linux-2.
- Documented `IntxLNK` root cause and apply behavior: classify as corrupted NTFS symlink artifact, refuse on `ntfs3`, unlink+symlink+verify only after approval and clean-state gates.
- Corrected tests from `tests/harness/` to `tests/readiness/` and `tests/workstations/`.
- Made `docs/standards/CONTROL_PLANE_CONTRACT.md` update required.
- Added cross-repo clean-state/dirty/ahead/detached/ntfs3/nested-worktree preflight requirements before any sibling writes.
- Added re-review precondition: commit and push revised plan artifacts to `main` before dispatching Claude/Codex/Gemini reviewers.

## Current gate state

- Issue #2775 remains implementation-blocked.
- Plan is still `draft-needs-revision` locally until committed/pushed and fresh T3 adversarial re-review clears without MAJOR.
- No `status:plan-review` or `status:plan-approved` label changes were made.
