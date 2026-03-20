# Workspace Hub
> Engineering workspace — shared utilities, digital twin, energy data, asset portfolio
## Hard Gates
1. Orchestrate, don't execute — delegate execution to subagents
2. Plan before acting — explicit plan + user approval before implementation
3. TDD mandatory — tests before implementation; no exceptions
4. WRK gate — every task maps to WRK-* in `.claude/work-queue/`
5. Gate evidence — run `scripts/work-queue/verify-gate-evidence.py WRK-xxx` before claim/close
## Commands
- Python: `uv run` always — never bare `python3`
- Git: commit to `main` + push immediately; branch only for multi-session WRKs
- Cross-review: `scripts/review/cross-review.sh <file> all` — multi-provider mandatory
- Work: `scripts/agents/work.sh --provider <name> run` — dispatches to group runners
## Policies
- Plans: Route A/B in WRK body; Route C in `specs/wrk/WRK-<id>/`
- Reviews: verdicts APPROVE|MINOR|MAJOR; resolve MAJOR before completion
- Scope: planning restricted to WRK locations; cross-domain requires explicit permission
- Secrets: never hardcode API keys/tokens — use environment variables
