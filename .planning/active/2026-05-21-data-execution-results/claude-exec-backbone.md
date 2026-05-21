You are working in vamseeachanta/workspace-hub. Follow AGENTS.md hard gates. Do not self-apply status:plan-approved. TDD is mandatory for implementation. Re-check live GitHub issue labels/comments before action. Preserve unrelated dirty changes. Use uv run for Python. Post durable GitHub issue comments with evidence. Never expose credentials. User update: llm-wiki is now private; ACMA/client data can be stored more fully with key-information abstractions and lesser restrictions than public-wiki routing. For destructive filesystem/data operations, stop at dry-run evidence unless the exact destructive action is explicitly authorized in an approved plan.

TASK: Execute approved execution-layer backbone issues where possible: #2738, #2739, #2754, #2665. Monitor #2755 only because it is already status:working.

Scope:
- Worktree: /mnt/local-analysis/agent-worktrees/workspace-hub-exec-backbone-2738-2739-2754-2665-claude
- Branch: agent/exec-backbone-2738-2739-2754-2665-claude
- Plans: docs/plans/2026-05-18-issue-2738-ace-linux-1-telegram-dispatch-coordinator.md; docs/plans/2026-05-18-issue-2739-ace-linux-2-telegram-dispatch-worker.md; docs/plans/2026-05-19-issue-2754-ace-linux-1-throughput-lane-tier1-baseline.md; docs/plans/2026-05-12-issue-2665-provider-credit-approval-dashboard-dispatch-gates.md

Required workflow:
1. Verify each issue still has status:plan-approved before executing.
2. Determine if these can be implemented together without path/semantic conflict. If not, pick the highest-leverage single issue and comment why the rest should be separate.
3. Tests first for any changed scripts/config/report generation.
4. Implement only bounded repo-side work. Do not change local secrets or live gateway credentials.
5. Monitor #2755 by reading status/comments; do not duplicate active worker work.
6. Run validations, commit branch, push if safe, comment on affected issues with evidence.
7. Final response: status by issue, evidence, branch/SHA, issue comment URLs, blockers.