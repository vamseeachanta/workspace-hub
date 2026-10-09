---
name: hidden-folder-audit-common-hidden-folders-reference
description: 'Sub-skill of hidden-folder-audit: Common Hidden Folders Reference.'
version: 1.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Common Hidden Folders Reference

## Common Hidden Folders Reference


Based on actual cleanup sessions, this table provides verified recommendations.

| Folder | Purpose | Action | Notes |
|--------|---------|--------|-------|
| `.claude/` | Claude Code configuration, agents, skills, docs | **KEEP** | Authoritative for AI tools |
| `.githooks/` | Git hooks | **KEEP** | Standard location |
| `.github/` | GitHub workflows, templates | **KEEP** | Required by GitHub |
| `.git/` | Git repository data | **NEVER TOUCH** | - |
| `.gitignore` | Git ignore patterns | **KEEP** | Update as needed |
| `.vscode/` | VS Code settings | **KEEP** | Team settings if tracked |
| `.idea/` | JetBrains IDE settings | **KEEP** | Or add to .gitignore |
| `.env` | Environment variables | **KEEP** | Must be in .gitignore |
| `.agent-os/` | Legacy agent OS configuration | **CONSOLIDATE** | Merge into `.claude/` |
| `.ai/` | Legacy AI configuration | **CONSOLIDATE** | Merge into `.claude/` |
| `.drcode/` | External tool (Dr. Code) config | **DELETE** | Legacy AI config, confirmed deletable |
| `.slash-commands/` | Command registry | **CONSOLIDATE** | Move to `.claude/docs/commands/` |
| `.git-commands/` | Git helper scripts | **CONSOLIDATE** | Move to `scripts/git/` |
| `.benchmarks/` | Benchmark data | **DELETE** | Usually empty, delete if so |
| `benchmarks/` | Benchmark data and reports | **SPLIT** | Move fixtures to tests/fixtures/, gitignore reports/results |
| `.agent-runtime/` | Dead symlinks, orphaned state | **DELETE** | After verifying dead links |
| `.common/` | Orphaned utilities | **DELETE** | Relocate useful scripts first |
| `.specify/` | Stale specification templates | **DELETE** | Migrate to `specs/templates/` |
| `.pytest_cache/` | Pytest cache | **DELETE** | Regenerated automatically |
| `.ruff_cache/` | Ruff linter cache | **DELETE** | Regenerated automatically |
| `.mypy_cache/` | MyPy type checker cache | **DELETE** | Regenerated automatically |
