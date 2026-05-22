# Sibling SSoT Validation and Closeout Gate

Use this reference when sibling repositories are expected to consume workspace-hub as the single source of truth (SSoT) for Hermes/Codex/Gemini skills, agent contract pointers, or memory flow.

## Minimum validation bundle

Before claiming sibling SSoT access is complete, verify all relevant channels separately:

1. `git status --short` in the implementation worktree, with generated review artifacts separated from intended code/test/config changes.
2. Full diff inspection for:
   - Hermes config template rendering and placeholder resolution.
   - workstation registry authority for sibling repo skill roots.
   - readiness/harness contracts.
   - repair/check scripts.
   - tests covering stale path and symlink safety cases.
3. Targeted tests for sync, registry completeness, sibling topology, Hermes path rendering, repair dry-run, and remote/workstation ground truth.
4. Runtime dry-runs for local and non-local machine profiles, including at least:
   - `bash scripts/_core/sync-agent-configs.sh --machine <local> --dry-run`
   - `bash scripts/_core/sync-agent-configs.sh --machine <remote-or-licensed> --dry-run`
   - `uv run python scripts/readiness/check-sibling-sso-flow.py --machine <local>`
   - `uv run python scripts/readiness/repair-sibling-sso-flow.py --machine <local> --dry-run`
5. Post-fix adversarial re-review after the final code changes, even when targeted tests are green.

## Review focus after green tests

Ask reviewers to explicitly check:

- Registry authority: sibling paths are generated from `config/workstations/registry.yaml`, not hardcoded stale nested paths.
- Target-machine truthfulness: `--machine <remote>` does not silently run local probes and report a false pass.
- Symlink overwrite safety: repair scripts block symlinked/missing/non-regular `AGENTS.md` before rewriting stale pointers.
- Repair-manifest completeness: dry-run and apply output identify exactly what would change.
- Rollback/dirty scope: unrelated dirty files are preserved; touched dirty paths fail closed.
- Memory drift: `.claude/memory/**` changes are reviewed separately and not staged as incidental SSoT fixes.

## If interrupted by tool budget or compaction

Do not summarize the issue as complete. Emit a resume checkpoint with:

- Current worktree and branch.
- Passed test/runtime commands with observed result.
- Remaining blocker: usually post-fix adversarial review, commit/push, and GitHub closeout.
- Exact next commands/checkpoints for the next session.

This prevents a future agent from closing an issue based on pre-review local validation only.