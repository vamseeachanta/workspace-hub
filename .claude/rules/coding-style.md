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

Claude will use repository `AGENTS.md` through verified native discovery. The shared user contract will load through a real `~/.claude/rules/workspace-soul.md` symlink to `config/agents/claude/SOUL.runtime.md` after an exact reviewed migration and live verification. Provider-specific content stays in its delta/runtime; common AGENTS content remains provider-neutral.

During staged migration, `scripts/agents/claude_runtime_state.py` will distinguish LEGACY, DUAL_VERIFIED, NATIVE_VERIFIED and BLOCKED. Existing managed `~/.claude/CLAUDE.md` links will remain on unverified hosts. Generic installation/bootstrap will neither recreate a missing Claude file nor retire the legacy link. A new path alone is not successful loading: source, provider version, protected configuration and saved evidence must still match. Real symlinks are required; copies or path-text stubs do not qualify. Sibling, private-policy and fleet retirement require their own exact scoped authority.
