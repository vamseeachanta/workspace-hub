# Workspace Hub Memory

> Full memory: `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/`

## Quick Refs
- Hub scripts: `uv run --no-project python` | Legal scan: `scripts/legal/legal-sanity-scan.sh`
- Cross-review (HARD GATE): `scripts/review/cross-review.sh <file> all`
- Work queue: `.claude/work-queue/` | All tasks need WRK-* item

## Submodules
- 23 active submodules; `achantas-media` + `investments` untracked (add when ready)
- Commit inside submodule first, then update hub pointer

## Rules
- CLAUDE.md / MEMORY.md / AGENTS.md / CODEX.md / GEMINI.md ≤ 20 lines
- Shell scripts: LF only (no CRLF); no client identifiers in ported code

*Docs: `.claude/docs/` | Rules: `.claude/rules/`*
