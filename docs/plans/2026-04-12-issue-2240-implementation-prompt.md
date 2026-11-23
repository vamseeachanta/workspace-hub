# Claude agent-team implementation prompt — Issue #2240

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Implementer
3. Adversarial Reviewer
4. Integrator

The user has approved implementation.
This issue is `status:plan-approved`, and `.planning/plan-approved/2240.md` exists.
Do not ask the user any questions.

Primary issue:
- #2240 https://github.com/vamseeachanta/workspace-hub/issues/2240

Related issues:
- #1583 Hermes baseline definition
- #2089 weekly review governance
- #2094 multi-machine readiness matrix
- #2239 completed weekly parity automation (already implemented; do not modify unless a test proves it is required)

Authoritative artifacts to consume first:
- `docs/plans/2026-04-12-issue-2240-macos-hermes-parity-install-config-and-tool-alignment.md`
- `scripts/review/results/2026-04-12-plan-2240-claude.md`
- `scripts/review/results/2026-04-12-plan-2240-codex.md`
- `scripts/review/results/2026-04-12-plan-2240-gemini.md`
- `scripts/review/results/2026-04-12-plan-2240-codex-rerun.md`
- `scripts/review/results/2026-04-12-plan-2240-gemini-rerun.md`
- `scripts/review/results/2026-04-12-plan-2240-codex-final-rerun.md`
- `scripts/review/results/2026-04-12-plan-2240-gemini-final-rerun.md`
- `config/agents/claude/memory-snapshots/network_machines.md`
- `config/workstations/registry.yaml`
- `scripts/readiness/harness-config.yaml`
- `scripts/_core/sync-agent-configs.sh`
- `scripts/readiness/nightly-readiness.sh`
- `scripts/maintenance/ai-tools-status.sh`
- `scripts/operations/workstation-status.sh`
- `scripts/monitoring/cron-health-check.sh`
- `docs/ops/hermes-weekly-cross-machine-parity-checklist.md`
- `tests/workstations/test_handoff_and_status.py`
- `tests/monitoring/test_cron_health_script.py`
- `tests/work-queue/test-harness-readiness.sh`

Implementation constraints:
- Implement ONLY issue #2240.
- Do NOT modify #2239 automation surfaces unless a directly related test proves it is necessary.
- Canonical macOS contract for this issue:
  - machine key: `macbook-portable`
  - hostname alias: `Vamsees-MacBook-Air.local`
  - canonical workspace path: `/Users/krishna/workspace-hub`
- Explicit consumer disposition:
  - in scope: `config/workstations/registry.yaml`, `scripts/readiness/harness-config.yaml`, `scripts/_core/sync-agent-configs.sh`, `scripts/readiness/nightly-readiness.sh`, `scripts/maintenance/ai-tools-status.sh`, `docs/ops/hermes-weekly-cross-machine-parity-checklist.md`, `tests/work-queue/test-harness-readiness.sh`, `tests/workstations/test_handoff_and_status.py`, `tests/monitoring/test_cron_health_script.py`
  - verify unchanged unless tests require edits: `scripts/operations/workstation-status.sh`, `scripts/monitoring/cron-health-check.sh`
  - explicitly out of scope: `scripts/readiness/compare-harness-state.sh`
- Keep `nightly-readiness.sh` changes narrowly scoped to macOS report naming, alias handling, and BSD-safe command paths needed here.

Allowed write paths:
- `config/workstations/registry.yaml`
- `scripts/readiness/harness-config.yaml`
- `scripts/_core/sync-agent-configs.sh`
- `scripts/readiness/nightly-readiness.sh`
- `scripts/maintenance/ai-tools-status.sh`
- `docs/ops/hermes-weekly-cross-machine-parity-checklist.md`
- `tests/work-queue/test-harness-readiness.sh`
- `tests/workstations/test_handoff_and_status.py`
- `tests/monitoring/test_cron_health_script.py`

Forbidden paths:
- `.claude/skills/**`
- `.claude/state/**`
- `.planning/**` except reading the approval marker
- `docs/plans/**`
- `scripts/readiness/compare-harness-state.sh`
- `config/scheduled-tasks/schedule-tasks.yaml`
- `docs/ops/scheduled-tasks.md`
- `scripts/cron/weekly-hermes-parity-review.sh`
- `tests/work-queue/test-weekly-hermes-parity-review.sh`
- any unrelated dirty or untracked files already present in the worktree

Dirty-worktree rule:
- First inspect `git status --short`.
- There are known unrelated dirty/untracked files outside your scope.
- Do not touch, stage, or normalize them.
- Use exact-path staging only. Never use `git add .`.

Success condition:
By the end of this run, the repo contains the approved macOS parity scaffolding and test coverage for #2240, only owned files are committed, the commit is pushed, and the issue receives a concise implementation summary comment. If any blocker prevents clean completion, stop honestly and report it.

Execution steps:
1. Read and ground in the approved plan and review artifacts.
2. Implement the canonical macOS workstation + readiness contract.
3. Add/adjust tests before and after code changes where practical.
4. Run required verification:
   - `bash tests/work-queue/test-harness-readiness.sh`
   - `pytest tests/workstations/test_handoff_and_status.py -q`
   - `pytest tests/monitoring/test_cron_health_script.py -q`
   - one focused check proving `sync-agent-configs.sh` resolves the macOS alias/path contract or a test that covers it
5. Run an internal adversarial self-review against the approved plan.
6. Stage only allowed write paths.
7. Commit with a focused message referencing #2240.
8. Push to `origin main`.
9. Post a concise GitHub comment on #2240 summarizing files changed, validations run, and explicit out-of-scope follow-up (`compare-harness-state.sh` if still unchanged).
10. Close #2240 only if the implementation fully satisfies the approved plan and validations.

Output requirements at the end of the Claude run:
1. What changed
2. Files changed
3. Validation performed
4. Commit SHA
5. Push status
6. GitHub comment URL
7. Whether issue #2240 was closed or left open
8. Residual blockers or follow-up notes
