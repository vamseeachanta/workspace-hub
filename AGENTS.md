# Workspace Hub
> Engineering workspace with sub shared utilities to perform work in a given repositories (tier-1 repositories). Cross-provider identity + per-message rules baseline: `config/agents/SHARED_SOUL.md` (materialized into `config/agents/<provider>/SOUL.runtime.md` artifacts via `scripts/agents/build-soul-runtime.sh`).
## Retrieval
- Consult `docs/` for reference maps, coverage reports, and domain guides before searching
## Hard Gates
1. Plan ALL issues: Issue → Resource Intel → Plan (`docs/plans/_template-issue-plan.md`) → Adversarial Review → `status:plan-review` → USER APPROVES → `status:plan-approved` → Implement (TDD) → Close. Skill: `.claude/skills/coordination/issue-planning-mode/SKILL.md` | Guide: `docs/plans/README.md` | Policy: [Hard-Stop Policy](docs/standards/HARD-STOP-POLICY.md)
2. TDD mandatory — tests before implementation; no exceptions
3. Gate order: Issue → Plan → USER APPROVES → Implement → Cross-review → Close
## Engineering-Critical Labels
`cat:engineering`, `cat:engineering-calculations`, `cat:engineering-methodology`, `cat:data-pipeline`
## Workflow
- Tasks tracked as GitHub issues via GSD framework; no local work-queue. Use `/gsd:help` for commands, `/gsd:new-project` to initialize
## Commands
- Python: `uv run` always — never bare `python3`
- Git: commit to `main` + push; branch only for multi-session work
## Policies
- Reviews: APPROVE|MINOR|MAJOR; resolve MAJOR; default 3-agent adversarial review per [AI Review Policy](docs/standards/AI_REVIEW_ROUTING_POLICY.md) (Claude orchestrates)
- Subagent isolation: fresh context via subagents — [convention](docs/standards/SUBAGENT_CONTEXT_ISOLATION.md)
- Readiness: [Model-Release Readiness Contract](docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md) + [Upgrade Playbook](docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md)
- Secrets: never hardcode API keys/tokens — use environment variables
