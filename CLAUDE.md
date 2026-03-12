# Workspace Hub
> Context budget: 4KB | Rules: `.claude/rules/` | Docs: `.claude/docs/`
## Hard Gates
1. **Orchestrate, don't execute** — delegate all execution via Task tool; subagents isolate context pollution
2. **Plan before acting** — explicit plan + user approval before implementation or commits
3. **TDD mandatory** — tests before implementation; no exceptions
4. **WRK gate** — every task maps to WRK-* in `.claude/work-queue/`; never execute multi-step without approval
5. **Retrieval first** — consult `.claude/docs/`, `.claude/rules/`, memory before training knowledge
6. **Gate evidence verification** — run `scripts/work-queue/verify-gate-evidence.py WRK-xxx` before claiming or closing a WRK so every cross-review (Claude/Codex/Gemini), plan approval, TDD, legal artifact, and required `.claude/work-queue/logs/WRK-*-<stage>.log` audit signal is recorded.
## Quick Reference
- Skills: `/skills` — on-demand only | Session start: `/session-start` before any work request | Terminology: `/ecosystem-terminology`
- Git: `.claude/rules/git-workflow.md` | Python: `.claude/rules/python-runtime.md` (uv always) | Plans: `specs/modules/`
- Cross-review (MANDATORY): `scripts/review/cross-review.sh <file> all` — Codex is hard gate
- Workflow lifecycle skills (MANDATORY): `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` and `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
- Context: Global 2KB + Workspace 4KB + Project 8KB + Local 2KB = 16KB max
- Dep graph: @config/deps/cross-repo-graph.yaml | Repo map: @config/onboarding/repo-map.yaml
*Delegation: `.claude/docs/orchestrator-pattern.md` | Full docs: `.claude/docs/`*
