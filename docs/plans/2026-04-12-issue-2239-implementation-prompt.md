# Claude agent-team implementation prompt — Issue #2239

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Implementer
3. Adversarial Reviewer
4. Integrator

The user has approved implementation.
This issue is `status:plan-approved`, and `.planning/plan-approved/2239.md` exists.
Do not ask the user any questions.

Primary issue:
- #2239 https://github.com/vamseeachanta/workspace-hub/issues/2239

Related issues:
- #1583 Hermes baseline definition
- #2089 weekly review governance
- #2094 multi-machine readiness matrix
- #2240 macOS parity scaffolding (NOT part of this implementation)

Authoritative artifacts to consume first:
- `docs/plans/2026-04-12-issue-2239-automate-weekly-hermes-cross-machine-parity-review.md`
- `scripts/review/results/2026-04-12-plan-2239-claude.md`
- `scripts/review/results/2026-04-12-plan-2239-codex.md`
- `scripts/review/results/2026-04-12-plan-2239-gemini.md`
- `scripts/review/results/2026-04-12-plan-2239-codex-rerun.md`
- `scripts/review/results/2026-04-12-plan-2239-gemini-rerun.md`
- `scripts/review/results/2026-04-12-plan-2239-codex-final-rerun.md`
- `scripts/review/results/2026-04-12-plan-2239-gemini-final-rerun.md`
- `docs/ops/hermes-weekly-cross-machine-parity-checklist.md`
- `config/scheduled-tasks/schedule-tasks.yaml`
- `docs/ops/scheduled-tasks.md`
- `config/workstations/registry.yaml`
- `scripts/readiness/harness-config.yaml`

Implementation constraints:
- Implement ONLY issue #2239.
- Do NOT pull #2240 work into this run.
- In v1:
  - `dev-primary` / `ace-linux-1` = direct local probes
  - `dev-secondary` / `ace-linux-2` = timeout-wrapped SSH probes
  - `licensed-win-1` = explicit readiness artifact `.claude/state/harness-readiness-licensed-win-1.yaml`
  - `licensed-win-2` = explicitly reported as `blocked` until canonical artifact path exists
  - `macbook-portable` = explicitly reported as `unsupported` or `blocked` until #2240 lands
- GitHub commenting must be OFF by default and enabled only by explicit flag/option in the script.
- Do NOT auto-create GitHub follow-on issues in v1.

Allowed write paths:
- `scripts/cron/weekly-hermes-parity-review.sh`
- `config/scheduled-tasks/schedule-tasks.yaml`
- `docs/ops/scheduled-tasks.md`
- `tests/work-queue/test-weekly-hermes-parity-review.sh`
- if strictly needed for test support only: `scripts/monitoring/tests/test_cron_health_check.sh`

Read-only paths:
- everything else needed for grounding

Forbidden paths:
- `.claude/skills/**`
- `.claude/state/**`
- `.planning/**` except reading the approval marker
- `docs/plans/**`
- `docs/ops/hermes-weekly-cross-machine-parity-checklist.md`
- issue #2240 implementation surfaces (`config/workstations/registry.yaml`, `scripts/readiness/harness-config.yaml`, `scripts/_core/sync-agent-configs.sh`, `scripts/readiness/nightly-readiness.sh`, `scripts/maintenance/ai-tools-status.sh`)
- any unrelated dirty or untracked files already present in the worktree

Dirty-worktree rule:
- First inspect `git status --short`.
- There are known unrelated dirty/untracked files outside your scope.
- Do not touch, stage, or normalize them.
- Use exact-path staging only. Never use `git add .`.

Success condition:
By the end of this run, the repo contains a working weekly parity review implementation for #2239, tests/validation pass, only owned files are committed, the commit is pushed, and the issue receives a concise implementation summary comment. If any blocker prevents complete delivery, stop honestly and report it without faking completion.

Execution steps:
1. Read and ground in the approved plan and review artifacts.
2. Inspect current code and design the smallest compliant implementation.
3. Write/adjust tests first where practical, then implement.
4. Run required verification:
   - `bash tests/work-queue/test-weekly-hermes-parity-review.sh`
   - `uv run --no-project python scripts/cron/validate-schedule.py`
   - `bash scripts/cron/setup-cron.sh --dry-run | grep weekly-hermes-parity-review`
   - one manual script run that writes a dated artifact under `logs/weekly-parity/` or clearly proves artifact generation
5. Run an internal adversarial self-review against the approved plan.
6. Stage only allowed write paths.
7. Commit with a focused message referencing #2239.
8. Push to `origin main`.
9. Post a concise GitHub comment on #2239 summarizing:
   - files changed
   - validations run
   - any explicitly deferred items (`licensed-win-2`, `macbook-portable` scope)
10. Close #2239 only if the implementation fully satisfies the approved plan and validations.

Output requirements at the end of the Claude run:
1. What changed
2. Files changed
3. Validation performed
4. Commit SHA
5. Push status
6. GitHub comment URL
7. Whether issue #2239 was closed or left open
8. Residual blockers or follow-up notes
