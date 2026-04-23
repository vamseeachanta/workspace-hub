Work in `/mnt/local-analysis/worktrees/ws-2437`.

Mission: execute workspace-hub issue #2437 in an isolated workspace-hub worktree, including any required local plan-approval marker, verification, issue closeout, and the two follow-on child issues under #2424 that the plan explicitly calls for.

Hard rules:
- Use `uv run` for Python.
- Do NOT ask the user any questions.
- Respect workspace-hub plan gate. Because this is an implementation worktree, ensure `.planning/plan-approved/2437.md` exists locally in this worktree before code changes; if missing, create a neutral approval marker and commit it first in this worktree.
- Do not touch files outside the owned path set.
- Final landing target is `origin/main`; this worktree branch is only an isolation boundary.

Owned paths:
- `.planning/plan-approved/2437.md`
- `.github/workflows/baseline-check.yml`
- `.pre-commit-config.yaml`
- `scripts/work-queue/whats-next.sh`
- `scripts/work-queue/verify-gate-evidence.py`

Read-only context:
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-21-issue-2437-workspace-hub-prune.md`
- `/mnt/local-analysis/workspace-hub/docs/handoffs/2026-04-22-ecosystem-ci-queue-execution.md`
- `docs/ops/legacy-claude-reference-map.md`
- `docs/plans/README.md`

Forbidden paths:
- any files under `docs/plans/` other than the approval marker if needed
- any `.claude/` runtime/state files
- any files owned by the planning stream (`docs/plans/2026-04-21-issue-2441-*`, `...2443-*`, `...2444-*`, `scripts/review/results/2026-04-21-plan-244*.md`)

Required workflow:
1. Post a start comment on issue `#2437`.
2. Verify the issue is still implementation-ready and that the orphan refs still exist.
3. If `.planning/plan-approved/2437.md` is missing in this worktree, create it with neutral wording tied to the existing user-approved status, commit that marker first, and continue.
4. Implement the plan exactly:
   - remove the dangling shell-test / WRK gate steps from `.github/workflows/baseline-check.yml`
   - remove the dangling `validate-work-queue-state` hook block from `.pre-commit-config.yaml`
   - delete `scripts/work-queue/whats-next.sh`
   - delete `scripts/work-queue/verify-gate-evidence.py`
5. TDD/validation gates before commit:
   - grep proves the dangling refs are gone
   - `uv run python -c` or the best available YAML parser check proves both YAML files parse
   - run the most relevant pre-commit / config validation you can without widening scope unnecessarily
   - verify no live callers remain except legacy docs references
6. Create the two follow-on child issues under `#2424` called for by the plan, with precise titles:
   - `chore(ci-health): audit .planning/templates/ orphan refs from WRK→GSD migration`
   - `chore(ci-health): triage tests/work-queue/ — port to GSD or delete`
   Mention in each body that it was split from #2437 / parent #2424.
7. Commit the implementation change, rebase if needed, and push to `origin/main` via `git push origin HEAD:main`.
8. Monitor the resulting `Baseline Testing` workflow enough to confirm the missing-script failure mode is gone or to capture the next blocker precisely.
9. Post a final comment on `#2437` with validation evidence, child issue links, and commit hash. Close `#2437` if acceptance is met.

Required closeout block:
- Result
- Files changed/deleted
- Validation commands/results
- CI run id / relevant status
- Child issues created
- Commit hash pushed
- Residual risk

Do not end before push + issue comment + child-issue creation + close/no-close decision.
