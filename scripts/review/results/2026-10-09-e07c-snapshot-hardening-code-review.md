# E07/W05 Snapshot Hardening Code Review

Branch: `codex/e07c-snapshot-hardening`
Base: `origin/codex/e07-memory-snapshots` because PR #3982 remained open.
Reviewer: Codex subagent `01a1209d-8951-75d0-9cdd-242518c12595`

## Round 1

Verdict: MAJOR

Findings:
- `scripts/cron/commit-learning-artifacts.sh` did not check host resolution before constructing the private snapshot host path.
- `scripts/cron/commit-learning-artifacts.sh` legacy verification did not fail on an invalid public ref before private commit/push.
- `scripts/_core/sync-agent-configs.sh` restored the lexicographically first host snapshot instead of the current resolved host.

## Fixes

- Added explicit host-resolution and public-ref failure checks before private snapshot commit/push.
- Added explicit status checks around private legacy verification inputs and outputs.
- Changed restore selection to prefer the resolved `hosts/<role>/...` path, with legacy fallback only when the resolved host path is absent.
- Added regressions for failed `rsync`, invalid host, invalid public ref, exact private origin, PRIVATE visibility, and host-over-legacy restore precedence.

## Round 2

Verdict: APPROVE

Reviewer checks:
- `bash -n` passed on target scripts.
- Focused pytest regressions passed.
- Manual invalid-host and invalid-ref probes did not change private HEAD and did not push.
- `test_sync_agent_helpers.sh` passed 22/22.
- `test_sync_agent_configs.sh` passed 24/24.
- Redaction suite passed 11/11.
- Baseline removal was limited to `config/agents/claude/memory-snapshots/` rows.
