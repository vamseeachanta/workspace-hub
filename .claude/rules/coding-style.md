# Coding Style Rules — Universal

## Edit Safety
- Prefer targeted single-site edits over bulk find-replace — verify each change site
- After edits: confirm imports not mangled, no duplicate definitions, no deleted adjacent code
- Multi-file refactors: edit one file at a time, run tests between files

## Path Handling
- In scripts: use relative paths or `$(git rev-parse --show-toplevel)` / `${REPO_ROOT}` — never hardcode absolute paths (enforced: `scripts/enforcement/check-no-abs-paths.sh`)
- Absolute paths permitted only when a tool call explicitly requires them (e.g., `file_path` parameter)

## Agent Harness Files
AGENTS.md is the canonical contract. It, MEMORY.md, and GEMINI.md must not exceed 20 lines. Migrate excess to a skill or doc. (enforced: `scripts/enforcement/check-harness-file-size.sh`)

CLAUDE.md is retired **as a repo file** (2026-08-01) — do not reintroduce one. The cap still applies to sibling repos that carry one.

Claude's auto-load is a machine-level **symlink**: `~/.claude/CLAUDE.md` → `config/agents/claude/SOUL.runtime.md`, installed by `scripts/agents/install-soul-runtime.sh` (same shape as `~/.hermes/SOUL.md` and `~/.codex/AGENTS.md`). It loads in every cwd, unlike the old repo adapter's `@import`. Never replace that link with a regular file — the content must live in exactly one drift-checked place.
