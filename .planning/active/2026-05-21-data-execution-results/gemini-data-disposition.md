You are working in vamseeachanta/workspace-hub. Follow AGENTS.md hard gates. Do not self-apply status:plan-approved. TDD is mandatory for implementation. Re-check live GitHub issue labels/comments before action. Preserve unrelated dirty changes. Use uv run for Python. Post durable GitHub issue comments with evidence. Never expose credentials. User update: llm-wiki is now private; ACMA/client data can be stored more fully with key-information abstractions and lesser restrictions than public-wiki routing. For destructive filesystem/data operations, stop at dry-run evidence unless the exact destructive action is explicitly authorized in an approved plan.

TASK: Read-only inventory/planning for data disposition issues #2767 and #2769, plus note any implications for #2731/#2732/#2745.

Scope:
- Worktree: /mnt/local-analysis/agent-worktrees/workspace-hub-data-disposition-2767-2769-gemini
- Branch: agent/data-disposition-2767-2769-gemini

Hard boundary: planning/inventory only. Do not move, delete, or rewrite large data. Do not implement.

Required output:
1. Live issue state for #2767/#2769.
2. Overlap matrix: whether #2769 is a child/special case of #2767 or independent.
3. Non-destructive inventory commands that future workers should run, including expected outputs and safety checks.
4. Disposition decision matrix for keep/archive/dedup/delete candidates.
5. Draft plan skeletons or issue-comment-ready text moving both issues toward plan-review.
6. Final response: findings, recommended labels/stage, blockers, and exact next commands.