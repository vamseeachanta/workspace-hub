# Workspace Hub
> Shared identity and authority: config/agents/SHARED_SOUL.md; provider runtimes inherit this contract.
## Retrieval and planning
- Consult docs/ and existing code; track meaningful work with GitHub issues and proportionate plans.
- Newsletter articles, their review copies, LinkedIn drafts and website pages: read fleet-ops docs/newsletter-playbook.md before touching any of them.
- Authority routing: docs/standards/HARD-STOP-POLICY.md and config/agents/SHARED_SOUL.md; guide: docs/plans/README.md; readiness: docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md and docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md; smoke schema/interface: docs/standards/MODEL_RELEASE_SMOKE_RUNNER_CONTRACT.md.
## Required controls
- The user's task request authorizes implementation within scope; no separate plan approval is required, including substantial work.
- Verify standing authorization or task scope. The team decides irreversible steps: log the step on fleet-ops #577 before running it, back up first, keep the machine reachable, and never put tokens or secrets anywhere. Client-facing emails and messages, and spending money, stay with the owner.
- TDD: tests before implementation. Preserve legal/security and engineering requirements.
- Adversarial plan/code review is advisory (docs/standards/AI_REVIEW_ROUTING_POLICY.md): fix the real bugs it finds. PRs merge on green required checks.
## Execution
- Classify execution per docs/standards/PARALLEL_FIRST_EXECUTION.md; concurrent sessions use ../llm-wiki/scripts/coordination/claim.py and ../llm-wiki/coordination/AGENT_SESSION_PROTOCOL.md from this hub root. Verify the issue repository/backend and shared lock root; held claims or unavailable coordination block affected shared work. Write a handoff before stopping.
- Objectives (lane:* x dispatch:* issues) run through one coordinator: docs/standards/COORDINATOR_PROTOCOL.md (role agents in .claude/agents/, host routing in config/agents/host-role-routing.yaml).
- Isolate disjoint write lanes per docs/standards/SUBAGENT_CONTEXT_ISOLATION.md; verify outputs and serialize integration/commit/push/closeout.
- Use uv run for Python. Commit/push within authorization; use isolated worktrees for parallel work.
- Git path to main: branch → PR → merge per .claude/rules/merge-authorization.md. Never push to or rewrite main except the registered exemptions in .claude/rules/merge-authorization.md; --force-with-lease only on the dedicated CAS state refs (equivalence-state, dispatch-leader-state); never bypass hooks (--no-verify, core.hooksPath) except an explicitly user-authorized recovery documented in the repo-sync skill.
## Data and closeout
- Follow docs/architecture/agent-data-handling-contract.md before discovering, saving or using data.
- Keep secrets out of code; verify results and run the pre-completion cleanup audit before closeout.
