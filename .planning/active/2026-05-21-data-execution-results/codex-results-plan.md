You are working in vamseeachanta/workspace-hub. Follow AGENTS.md hard gates. Do not self-apply status:plan-approved. TDD is mandatory for implementation. Re-check live GitHub issue labels/comments before action. Preserve unrelated dirty changes. Use uv run for Python. Post durable GitHub issue comments with evidence. Never expose credentials. User update: llm-wiki is now private; ACMA/client data can be stored more fully with key-information abstractions and lesser restrictions than public-wiki routing. For destructive filesystem/data operations, stop at dry-run evidence unless the exact destructive action is explicitly authorized in an approved plan.

TASK: Plan result/output layer without implementation for issues #2389, #2747, #2748, #2122, #2147, #2154, #2165, #2171.

Scope:
- Worktree: /mnt/local-analysis/agent-worktrees/workspace-hub-results-plan-2389-2747-2748-codex
- Branch: agent/results-plan-2389-2747-2748-codex

Hard boundary: These issues do NOT currently have status:plan-approved. Do not implement. Do not add status:plan-approved.

Required workflow:
1. Read each issue and relevant repo docs/plans.
2. Draft or update plan artifacts using docs/plans/_template-issue-plan.md.
3. Use dependency order: #2389 → #2747 → #2748 → #2122 → #2154/#2147 → #2165 → #2171.
4. Make plans testable: include acceptance criteria, TDD tests, owned/read-only/forbidden paths, dependencies, review prompts, and rollback.
5. Post issue comments with plan artifact links and recommend status:plan-review where appropriate.
6. Commit/push planning artifacts if safe.
7. Final response: created/updated plans, issue comment URLs, branch/SHA, blockers.