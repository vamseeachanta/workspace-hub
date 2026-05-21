You are working in vamseeachanta/workspace-hub. Follow AGENTS.md hard gates. Do not self-apply status:plan-approved. TDD is mandatory for implementation. Re-check live GitHub issue labels/comments before action. Preserve unrelated dirty changes. Use uv run for Python. Post durable GitHub issue comments with evidence. Never expose credentials. User update: llm-wiki is now private; ACMA/client data can be stored more fully with key-information abstractions and lesser restrictions than public-wiki routing. For destructive filesystem/data operations, stop at dry-run evidence unless the exact destructive action is explicitly authorized in an approved plan.

TASK: Execute approved issue #2745: "feat(acma): freeze acma-projects and move to local-only archive posture".

Scope:
- Worktree: /mnt/local-analysis/agent-worktrees/workspace-hub-issue-2745-data-freeze-codex
- Branch: agent/issue-2745-data-freeze-codex
- Plan artifact: docs/plans/2026-05-20-issue-2745-acma-projects-freeze.md
- GitHub issue: https://github.com/vamseeachanta/workspace-hub/issues/2745

Required workflow:
1. Verify issue has status:plan-approved and read the plan + recent issue comments.
2. Write failing tests first for the planned repo-side behavior.
3. Implement only repo-side guardrails/scripts/docs needed for freeze/archive posture.
4. Do NOT delete or move large /mnt/ace data; if storage actions are needed, produce dry-run evidence and comment with next required human approval.
5. Run targeted tests and any relevant validation.
6. Commit on the agent branch, push branch if safe, and comment on #2745 with files changed, tests run, commit SHA, blockers, and next step.
7. Final response must include: status, evidence, branch/SHA, issue comment URL if posted, and any blocker.