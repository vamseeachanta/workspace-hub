You are working in vamseeachanta/workspace-hub. Follow AGENTS.md hard gates. Do not self-apply status:plan-approved. TDD is mandatory for implementation. Re-check live GitHub issue labels/comments before action. Preserve unrelated dirty changes. Use uv run for Python. Post durable GitHub issue comments with evidence. Never expose credentials. User update: llm-wiki is now private; ACMA/client data can be stored more fully with key-information abstractions and lesser restrictions than public-wiki routing. For destructive filesystem/data operations, stop at dry-run evidence unless the exact destructive action is explicitly authorized in an approved plan.

TASK: Execute approved issue #2746: "feat(acma): create private llm-wiki repo target llm-wiki-acma".

Scope:
- Worktree: /mnt/local-analysis/agent-worktrees/workspace-hub-issue-2746-private-wiki-claude
- Branch: agent/issue-2746-private-wiki-claude
- Plan artifact: docs/plans/2026-05-20-issue-2746-llm-wiki-acma.md
- GitHub issue: https://github.com/vamseeachanta/workspace-hub/issues/2746

User update to incorporate:
- llm-wiki is now private.
- Data can be stored as much as possible with useful key-info abstractions and lesser restrictions than public wiki.

Required workflow:
1. Verify issue has status:plan-approved; read plan + recent issue comments.
2. Resolve title/body naming drift in the issue comments if still present: `llm-wiki-acma` vs `acma-llm-wiki`. Do not guess silently.
3. Implement repo-side target/scaffolding/config/docs only as authorized by plan; avoid leaking secrets.
4. Tests first for any scripts/config validators.
5. Run validations.
6. Commit on branch, push if safe, comment on #2746 with evidence.
7. Final response: status, evidence, branch/SHA, issue comment URL, blockers.