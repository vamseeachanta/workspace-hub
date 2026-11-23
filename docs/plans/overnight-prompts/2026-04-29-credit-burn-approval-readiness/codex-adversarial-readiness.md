You are Codex acting as an adversarial approval-readiness reviewer inside /mnt/local-analysis/workspace-hub.

Context: User confirmed provider credits are not the bottleneck. Harness throughput is. Weekly usage should be spent on useful plan prep/review/execution, and the user can tolerate up to ~2 days of depleted credits near reset.

Task:
1. Audit current plan-review / plan-draft materials to prevent false promotion of issues to status:plan-approved.
2. Focus candidate issues: #2540, #2541, #2542, #2543, #2544, #2490, #2510, #2370, #2375, #2378, #2538, #2509, #2474, #2363.
3. Read docs/plans, scripts/review/results, and docs/plans/overnight-prompts/2026-04-28-12h-continuation/results where useful.
4. Produce a markdown report at docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/results/codex-adversarial-readiness.md.

Report schema:
- Executive verdict: how many can be honestly considered ready now vs approval-prep only.
- Table: issue, plan path, latest valid review, blockers, legal gate needed, ready_now yes/no.
- False-positive risks.
- Exact next actions for Hermes to get to 10 promotion-ready issues.

Rules:
- Do not mutate GitHub labels.
- Do not close/reopen/comment on GitHub.
- Do not implement code.
- Legal sanity gate is mandatory for any raw data/client/public llm-wiki/artifact promotion.
- Prefer writing only the requested output file.
