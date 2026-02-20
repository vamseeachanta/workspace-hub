# Workspace Hub Agent Contract

Contract-Version: 1.0.0 | Last-Updated: 2026-02-20 | Canonical source for all AI agent behavior.

## Workflow Gates

1. Every task maps to WRK-* in `.claude/work-queue/`
2. Plan before implementation for Route B/C work
3. Explicit user approval before implementation, simulations, or commits
4. Cross-review mandatory before presenting significant implementation

## Policies

- **Work items**: `.claude/work-queue/` only; no WRK-*.md in child repos; regenerate `INDEX.md` on status changes
- **Skills**: `.claude/skills/` canonical; child repos use symlinks — no standalone SKILL.md in child repos
- **Plans**: Route A/B plan in WRK body; Route C in `specs/wrk/WRK-<id>/`; templates in `specs/templates/`
- **Reviews**: multi-provider; verdicts: APPROVE|MINOR|MAJOR|NO_OUTPUT|ERROR; resolve MAJOR before completion
- **Execution**: use repo's declared tooling (`uv` for Python repos); no undocumented one-off paths
- **Adapters**: CLAUDE.md, CODEX.md, GEMINI.md are generated adapters; AGENTS.md is canonical

## Repo Overrides

Repo-specific behavior under `## Repo Overrides` in each adapter. No override weakens Workflow Gates.
