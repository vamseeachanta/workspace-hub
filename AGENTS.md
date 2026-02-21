# Workspace Hub Agent Contract

Contract-Version: 1.0.1 | Last-Updated: 2026-02-21 | Canonical source for all AI agent behavior.

## Workflow Gates
1. Every task maps to WRK-* in `.claude/work-queue/`
2. All routes require WRK item + plan before execution
3. Approval must name the WRK id — "go ahead"/"tackle all" = intent, not approval
4. Cross-review mandatory before presenting significant implementation

## Enforcement
- Sequence: WRK item → plan → explicit ✓ naming WRK id → execute; no shortcuts
- No multi-step work without WRK id in scope; casual approval does not count

## Policies
- **Work items**: `.claude/work-queue/` only; no WRK-*.md in child repos; regenerate INDEX.md on changes
- **Plans**: Route A/B in WRK body; Route C in `specs/wrk/WRK-<id>/`; templates in `specs/templates/`
- **Reviews**: multi-provider; verdicts APPROVE|MINOR|MAJOR; resolve MAJOR before completion
- **Adapters**: CLAUDE.md/CODEX.md/GEMINI.md are adapters; AGENTS.md canonical; no override weakens gates
- **Dev**: repo tooling only (`uv` for Python); skills in `.claude/skills/` with child-repo symlinks
