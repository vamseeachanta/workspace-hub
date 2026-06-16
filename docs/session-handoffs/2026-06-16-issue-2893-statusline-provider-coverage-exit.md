# Issue 2893 Statusline Provider Coverage Exit Handoff

Date: 2026-06-16
Branch: `plan/2893-statusline-provider-coverage`
Repository: `vamseeachanta/workspace-hub`

## Active Task

Implement [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893): cross-provider statusline parity for Claude/Codex/Gemini/Hermes.

## Current State

- Branch pushed: `plan/2893-statusline-provider-coverage`
- Head commit: `1df0f9897 feat: add statusline provider coverage`
- Approval marker commit: `6688ec4a5 docs: record 2893 plan approval`
- Plan evidence commit: `247746897 docs: add statusline provider coverage plan`
- Implementation evidence comment: <https://github.com/vamseeachanta/workspace-hub/issues/2893#issuecomment-4719091972>
- [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) remains open with `status:plan-approved`.
- [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) is open and remains the closeout blocker.

## Completed Actions

- Added compact provider statusline rendering for `C|O|G|H=O`.
- Preserved live Claude `rate_limits.seven_day` as authoritative and added marked local stats-cache fallback.
- Added Codex weekly reset plus 5-hour remaining headroom.
- Marked estimate/stale sources visibly and prevented fresh estimates from hiding authoritative cache telemetry.
- Rendered Hermes as an explicit `H=O` alias instead of a fabricated independent quota pool.
- Added `scripts/readiness/statusline_provider_coverage.py`.
- Added the repo-level `statusline:provider-coverage` row to `scripts/readiness/build-equality-matrix.py`.
- Added `docs/standards/statusline-provider-coverage.md`.
- Posted implementation evidence to [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893).

## Verification Evidence

- RED was observed before implementation:
  - new Bats tests failed on missing Claude fallback, Codex 5h, and `H=O` behavior.
  - new readiness/matrix pytest tests failed on missing helper and matrix row.
- GREEN after implementation and review fixes:
  - `bats tests/statusline/test_claude_usage_visibility.bats tests/statusline/test_codex_burst_and_provider_coverage.bats tests/statusline/test_weekly_reset.bats tests/statusline/test_quota_staleness.bats tests/statusline/test_combined_wrapper.bats` -> 34/34 pass.
  - `uv run pytest tests/readiness/test_statusline_provider_coverage.py tests/readiness/test_build_equality_matrix.py -q` -> 77 passed.
  - `bash -n .claude/statusline-command.sh .claude/statusline-combined.sh scripts/ai/assessment/lib/providers.sh && python -m py_compile scripts/readiness/statusline_provider_coverage.py scripts/readiness/build-equality-matrix.py` -> pass.
  - `bash scripts/legal/legal-sanity-scan.sh --diff-only` -> PASS.
- Code-stage review:
  - r1: Claude MAJOR, Codex MAJOR, Gemini unavailable due CLI trust gate.
  - r2 after fixes: Claude APPROVE, Gemini APPROVE, Codex unavailable/no verdict due timeout/stdin regression.

## Verified Repo And Issue State

- Worktree was clean and pushed at `1df0f9897` before this handoff was written.
- `git rev-parse --short HEAD` and upstream both resolved to `1df0f9897`.
- Live [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893): OPEN, `status:plan-approved`.
- Live [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894): OPEN, `status:needs-plan`.
- `STATUSLINE_R6_BLOCKER_STATE=open python scripts/readiness/statusline_provider_coverage.py` reported:
  - `renderer_contract_verdict: COMPLETE`
  - `contract_verdict: PARTIAL`
  - `dirty: false`
  - `missing_paths: []`
  - `output_sample: C:95%?|O:35%·2.5d·5h99%|G:100%·6.6d|H=O $0.00 ctx:10%`

## Residue And Blockers

- Expected residue: this handoff file until committed and pushed.
- No known uncommitted implementation residue.
- No known `/tmp/2893-code-review*.md` scratch files remain.
- Closeout blocker: [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) must be resolved or explicitly lifted before [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) can be closed.

## Suggested Skills

- `github:github` for issue state and comment updates.
- `github:gh-address-comments` if review feedback is added to the branch.
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` before executing [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894).
- `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md` before any final closeout.

## Next Checkpoint

Resolve or lift [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894), then rerun:

```bash
STATUSLINE_R6_BLOCKER_STATE=closed python scripts/readiness/statusline_provider_coverage.py
```

If the helper reports `contract_verdict: COMPLETE` on a clean tree, close [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) with the implementation comment linked above.
