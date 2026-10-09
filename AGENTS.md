# Workspace Hub
> Engineering workspace with sub shared utilities to perform work in a given repositories (tier-1 repositories). Cross-provider identity + per-message rules baseline: `config/agents/SHARED_SOUL.md` (materialized into `config/agents/<provider>/SOUL.runtime.md` artifacts via `scripts/agents/build-soul-runtime.sh`).
## Retrieval — Consult `docs/` for reference maps, coverage reports, and domain guides before searching
## Hard Gates
1. Plan proportionately, review adversarially, and implement within task/standing authority; no separate user plan approval is required. Preserve TDD and required domain decisions.
2. TDD mandatory — tests before implementation; no exceptions
3. Gate order: Issue → Plan → Adversarial Review → Implement (TDD) → Cross-review → Close. Honor planning-only requests and consequential-action boundaries.
## Engineering-Critical Labels
`cat:engineering`, `cat:engineering-calculations`, `cat:engineering-methodology`, `cat:data-pipeline`
## Workflow
- Tasks tracked as GitHub issues via GSD; no local work-queue. Canonical execution is parallel-first gated execution: classify non-trivial work as `single-lane`, `parallel-readonly`, or `parallel-worktree` before starting. Reference: [Parallel-First Execution Standard](docs/standards/PARALLEL_FIRST_EXECUTION.md). **Concurrent sessions (any provider): claim a shared autonomous-loop unit before starting** (`scripts/coordination/claim.py` → BLOCKED if held) and write a handoff before stopping — spec: llm-wiki `coordination/AGENT_SESSION_PROTOCOL.md`.
## Commands
- Python: `uv run` always — never bare `python3`
- Git: commit to `main` + push; branch only for multi-session work
## Policies
- Reviews: APPROVE|MINOR|MAJOR; resolve MAJOR; default 3-agent adversarial review per [AI Review Policy](docs/standards/AI_REVIEW_ROUTING_POLICY.md) (Claude orchestrates)
- Parallelization never bypasses gates: planning/review/recon may run in parallel; implementation requires task/standing authority, review and TDD; no approval label or marker is required; write-capable parallel lanes require isolated worktrees, explicit owned/read-only/forbidden paths, orchestrator verification, and serialized commit/push/closeout.
- Subagent isolation: fresh context via subagents — [convention](docs/standards/SUBAGENT_CONTEXT_ISOLATION.md)
- Readiness: [Model-Release Readiness Contract](docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md) + [Upgrade Playbook](docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md)
- Secrets: never hardcode API keys/tokens — use environment variables
