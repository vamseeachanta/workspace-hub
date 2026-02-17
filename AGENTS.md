# Workspace Hub Agent Contract

Contract-Version: 1.0.0
Last-Updated: 2026-02-17
Scope: workspace-hub + managed repositories

## Purpose

This is the provider-neutral source of truth for AI agent behavior across the workspace-hub ecosystem.
Provider-specific instruction files (for example `CLAUDE.md`) are generated adapters.

## Workflow Gates

1. Every non-trivial task MUST map to a `WRK-*` item in `.claude/work-queue/`.
2. Planning is mandatory before implementation for Route B/C work.
3. Explicit user approval is required before implementation, simulation runs, or commits.
4. Cross-review is mandatory before presenting significant implementation work.

## Work Item Policy

1. Work items live only in `.claude/work-queue/`.
2. Do not create `WRK-*.md` files in child repositories.
3. Track status transitions using queue scripts and regenerate `INDEX.md`.

## Skills Policy

1. `workspace-hub/.claude/skills/` is the canonical source of skill content.
2. Child repositories may not own standalone `SKILL.md` files.
3. Child-repo skill entries must be propagated links (symlink/junction) from workspace-hub.

## Plan Policy

1. Route A/B plans may live inside the WRK body under `## Plan`.
2. Route C plans/specs are centralized in workspace-hub:
- `specs/wrk/WRK-<id>/` for work-item execution specs.
- `specs/repos/<repo>/` for repository-level architectural/domain specs.
3. Use templates in `specs/templates/`.

## Review Policy

1. Use multi-provider cross-review for Route B/C work.
2. Normalize review verdicts to `APPROVE | MINOR | MAJOR | NO_OUTPUT | ERROR`.
3. Resolve all `MAJOR` findings before completion unless user approves explicit deferral.

## Execution Constraints

1. Use each repository's declared environment tooling (for example `uv` for Python repos).
2. Prefer deterministic scripts and avoid undocumented one-off execution paths.
3. Keep generated artifacts out of version control unless intentionally tracked.

## Compatibility Policy

1. `CLAUDE.md` remains supported as a generated adapter for Claude tooling.
2. Legacy `COMMANDS.md` and `AGENT_OS_COMMANDS.md` may remain as references during migration.
3. New standards and automation must target this `AGENTS.md` contract first.

## Repo Overrides

Repository-specific behavior may be added in each repo adapter section under:
`## Repo Overrides`

No override may weaken Workflow Gates, Work Item Policy, or Plan Policy.
