> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_epic_wrapup_issues_then_parallel_agents.md

---
name: feedback_epic_wrapup_issues_then_parallel_agents
description: "At epic/feature wrap-up, open issues for follow-on candidates and pursue them via parallel agents + dynamic workflows"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: cca00540-68dc-418e-a942-2d1fd62ff157
---

2026-06-26 directive (during field-development epic [[project_field_development_playbook_epic]]): when a body of work wraps up and I list "candidate next work", don't just leave the list — **open GitHub issues for the candidates and actively pursue them using parallel agents + dynamic workflows**, rather than stopping to ask which one.

**Why:** the user wants momentum and breadth; a documented candidate list is not the deliverable — shipped (or at least issue-tracked + in-progress) work is. He is comfortable with multi-lane parallel execution and the merge-race machinery (`gh pr merge --auto` + update-branch-on-BEHIND).

**How to apply:**
- Turn each candidate into a GitHub issue (clear problem + proposed API + acceptance criteria) so nothing is lost even if not built immediately.
- Use a **dynamic workflow** (Workflow tool) for the design/scoping/research fan-out where independent perspectives or structured specs add value (de-risks fuzzy product-line work before building).
- Use **parallel background Agent lanes** for the actual build→PR→merge (reliable for cross-turn git/PR ops; Workflow-tool agents are better for in-context reasoning/structured return than long stateful git builds).
- Pre-create worktrees sequentially (avoid index.lock race); brief each agent with env gotchas (monorepo PYTHONPATH, venv path, push --no-verify, ≤500-line files, TDD, PR title ≤80, auto-merge loop).
- Don't over-fan: ~3 concurrent build lanes is the sweet spot; open the rest as issues for later. Skip/flag candidates that need investigation-first or risk a dishonest solution (e.g. spar-vs-semisub split would need a leaky downstream signal).
