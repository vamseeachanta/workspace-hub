# Workspace Hub
> Engineering workspace with sub shared utilities to perform work in a given repositories (tier-1 repositories)
## Retrieval
- Consult `docs/` for reference maps, coverage reports, and domain guides before searching
## Hard Gates
1. Plan before acting — explicit plan + user approval before implementation
2. TDD mandatory — tests before implementation; no exceptions
## Workflow
- GSD framework: `/gsd:help` for commands, `/gsd:new-project` to initialize
- Tasks tracked as GitHub issues — no local work-queue
## Commands
- Python: `uv run` always — never bare `python3`
- Git: commit to `main` + push immediately; branch only for multi-session work
## Policies
- Reviews: verdicts APPROVE|MINOR|MAJOR; resolve MAJOR before completion
- Review routing: [AI Review Routing Policy](docs/standards/AI_REVIEW_ROUTING_POLICY.md) — Claude orchestrates, Codex reviews, Gemini on triggers only
- Subagent isolation: execution stages use fresh context via subagents — [convention](docs/standards/SUBAGENT_CONTEXT_ISOLATION.md)
- Secrets: never hardcode API keys/tokens — use environment variables
