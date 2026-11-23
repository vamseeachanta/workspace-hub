Work in `/mnt/local-analysis/worktrees/ws-plan-2441-2444`.

Mission: planning-only overnight stream for workspace-hub issues #2441, #2443, and #2444. These are NOT implementation-approved. Revise each plan against the latest Wave-2 MAJOR findings, rerun adversarial plan review, post issue comments summarizing the fresh verdicts, and stop. No self-approval, no implementation.

Hard rules:
- Use `uv run` for Python.
- Do NOT ask the user any questions.
- Planning-only: do not modify implementation files in `digitalmodel/`, `achantas-data/`, or `aceengineer-admin/`.
- Do not self-approve or create `.planning/plan-approved/*` markers for these issues.
- If a plan still has MAJOR findings after one serious revision + fresh review wave, leave it in `status:plan-review` and document the blockers clearly.

Owned paths:
- `docs/plans/2026-04-21-issue-2441-digitalmodel-pylife.md`
- `docs/plans/2026-04-21-issue-2443-achantas-data-ci.md`
- `docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`
- matching review artifacts under `scripts/review/results/2026-04-21-plan-2441-*`, `...2443-*`, `...2444-*`
- `docs/plans/README.md` if a status/summary row truly needs refresh

Read-only context:
- `/mnt/local-analysis/workspace-hub/docs/handoffs/2026-04-22-ecosystem-ci-queue-execution.md`
- existing Wave-2 review artifacts for 2441/2443/2444
- issue comments and labels on those three issues

Forbidden paths:
- `.github/workflows/baseline-check.yml`
- `.pre-commit-config.yaml`
- `scripts/work-queue/`
- any implementation files in the tier-1 repos
- `.planning/plan-approved/*`

Execution order:
1. #2441
2. #2443
3. #2444

For each issue:
1. Re-read the current plan and the latest Claude/Codex/Gemini review artifacts.
2. Perform a live reality check against the repo state for the claims the reviewers challenged.
3. Revise the plan once, carefully, to retire the MAJOR findings without introducing new contradictions.
4. Run a fresh adversarial review wave (`scripts/review/cross-review.sh <plan> all --type plan` or the repo-standard equivalent).
5. Summarize the new verdicts directly on the GitHub issue with explicit APPROVE/MINOR/MAJOR status.
6. Ensure the issue remains correctly labeled `status:plan-review` unless the fresh review is actually approval-ready and your workflow only requires surfacing to the user; even then, do NOT self-approve.

Final deliverable by morning:
- all three plans revised or explicitly left blocked
- fresh review artifacts committed/pushed
- issue comments posted with the latest blocker/approval-readiness state
- a short final comment on one of the issues or a concise final log section summarizing which of the three is closest to user approval

Commiting/pushing:
- You may use one commit per issue or one final combined docs-only commit if that is cleaner.
- Push to `origin/main` via `git push origin HEAD:main` only after review artifacts and issue comments are complete.

Do not stop after editing local plan files. Finish fresh review artifacts + issue comments + push.
