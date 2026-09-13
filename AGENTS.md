# Workspace Hub
> Shared identity and authority: config/agents/SHARED_SOUL.md; provider runtimes inherit this contract.
## Retrieval and planning
- Consult docs/ and existing code; track meaningful work with GitHub issues and proportionate plans.
- Authority routing: docs/standards/HARD-STOP-POLICY.md and SHARED_SOUL.md; guide: docs/plans/README.md.
## Required controls
- Bounded routine reversible work may proceed under independently established standing authorization.
- Substantial scope and consequential actions require matching explicit approval; reassess changed scope.
- TDD: tests before implementation. Preserve legal/security and engineering requirements.
- Adversarial plan/code review: docs/standards/AI_REVIEW_ROUTING_POLICY.md; resolve blocking findings.
- Never self-label status:plan-approved; markers, receipts and handoffs do not authenticate approval.
## Execution
- Classify execution per docs/standards/PARALLEL_FIRST_EXECUTION.md; concurrent sessions must acquire a shared unit via scripts/coordination/claim.py (BLOCKED if held) and write a handoff before stopping; see llm-wiki coordination/AGENT_SESSION_PROTOCOL.md.
- Isolate disjoint write lanes per docs/standards/SUBAGENT_CONTEXT_ISOLATION.md; verify outputs and serialize integration/commit/push/closeout.
- Use uv run for Python. Commit/push within authorization; use isolated worktrees for parallel work.
- Readiness: docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md and docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md.
## Data and closeout
- Follow docs/architecture/agent-data-handling-contract.md before discovering, saving or using data.
- Keep secrets out of code; verify results and run the pre-completion cleanup audit before closeout.
