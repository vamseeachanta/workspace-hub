# Coding Style Rules — Universal

## Edit Safety
- Prefer targeted single-site edits over bulk find-replace — verify each change site
- After edits: confirm imports not mangled, no duplicate definitions, no deleted adjacent code
- Multi-file refactors: edit one file at a time, run tests between files

## Path Handling
- In scripts: use relative paths or `$(git rev-parse --show-toplevel)` / `${REPO_ROOT}` — never hardcode absolute paths
- Absolute paths permitted only when a tool call explicitly requires them (e.g., `file_path` parameter)

## Agent Harness Files
CLAUDE.md, MEMORY.md, AGENTS.md, GEMINI.md must not exceed 20 lines. Migrate excess to a skill or doc.
