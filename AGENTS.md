# Workspace Hub Agent Contract
Contract-Version: 1.0.3 | Last-Updated: 2026-03-04 | Canonical for all AI agent behavior.
## Workflow Gates
1. Every task maps to WRK-* in `.claude/work-queue/`
2. WRK item + plan + explicit approval (naming WRK id) before execution
3. Cross-review mandatory (multi-provider) before presenting significant implementation
4. Governance skills: `/work-queue-workflow` + `/workflow-gatepass`; inferred signals ≠ compliance
## Policies
- **Work items**: `.claude/work-queue/` only; no WRK-*.md in child repos; regenerate INDEX.md on changes
- **Plans**: Route A/B in WRK body; Route C in `specs/wrk/WRK-<id>/`; templates in `specs/templates/`
- **Reviews**: verdicts APPROVE|MINOR|MAJOR; resolve MAJOR before completion
- **Adapters**: CLAUDE.md/CODEX.md/GEMINI.md are adapters; AGENTS.md canonical; no override weakens gates
- **Dev**: `uv run` for ALL Python — never bare `python3`; see `.claude/rules/python-runtime.md`
- **Parallel-agent side effects**: out-of-WRK-scope changes are non-blocking; document under Out-of-Scope Side Effects
- **Scope**: planning restricted to WRK locations; cross-domain execution requires explicit user permission
