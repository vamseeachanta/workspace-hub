# Workspace Hub Agent Contract
Contract-Version: 1.0.2 | Last-Updated: 2026-03-04 | Canonical source for all AI agent behavior.
## Workflow Gates
1. Every task maps to WRK-* in `.claude/work-queue/`
2. All routes require WRK item + plan before execution
3. Approval must name the WRK id — "go ahead"/"tackle all" = intent, not approval
4. Cross-review mandatory before presenting significant implementation
5. Workflow governance is mandatory across all WRK lifecycle stages; inferred signals never count as measured compliance
## Enforcement
- Sequence: WRK item → plan → explicit ✓ naming WRK id → execute; no shortcuts
- No multi-step work without WRK id in scope; casual approval does not count
## Policies
- **Work items**: `.claude/work-queue/` only; no WRK-*.md in child repos; regenerate INDEX.md on changes
- **Workflow skills**: canonical WRK lifecycle governance skills are `/work-queue-workflow` and `/workflow-gatepass`; use them for workflow governance execution
- **Plans**: Route A/B in WRK body; Route C in `specs/wrk/WRK-<id>/`; templates in `specs/templates/`
- **Reviews**: multi-provider; verdicts APPROVE|MINOR|MAJOR; resolve MAJOR before completion; peer logs: `logs/orchestrator/<agent>/`
- **Next-work disposition**: follow stage-15/17 rule in `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`; record the choice in evidence
- **Signal metrics**: inferred signals are diagnostic only and must never be counted as measured gate compliance
- **Adapters**: CLAUDE.md/CODEX.md/GEMINI.md are adapters; AGENTS.md canonical; no override weakens gates
- **Dev**: `uv run` for ALL Python execution — never bare `python3` or `pip install`; see `.claude/rules/python-runtime.md` for per-repo commands; skills in `.claude/skills/`
