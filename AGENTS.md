# Workspace Hub
> Engineering workspace with sub shared utilities to perform work in a given repositories (tier-1 repositories)
## Retrieval
- Consult `docs/` for reference maps, coverage reports, and domain guides before searching
## Hard Gates
1. Plan before acting — user approval for engineering-critical issues. See [Hard-Stop Policy](docs/standards/HARD-STOP-POLICY.md)
2. TDD mandatory — tests before implementation; no exceptions
3. Gate order (engineering-critical): Issue → Plan → USER APPROVES → Implement → Cross-review → Close
## Engineering-Critical Labels
`cat:engineering`, `cat:engineering-calculations`, `cat:engineering-methodology`, `cat:data-pipeline`
## Workflow
- GSD framework: `/gsd:help` for commands, `/gsd:new-project` to initialize; tasks as GitHub issues
## Commands
- Python: `uv run` always — never bare `python3`
- Git: commit to `main` + push; branch only for multi-session work
## Policies
- Reviews: APPROVE|MINOR|MAJOR; resolve MAJOR; default 3-agent adversarial review
- Routing: [AI Review Policy](docs/standards/AI_REVIEW_ROUTING_POLICY.md) — Claude orchestrates
- Subagent isolation: fresh context via subagents — [convention](docs/standards/SUBAGENT_CONTEXT_ISOLATION.md)
- Secrets: never hardcode API keys/tokens — use environment variables
