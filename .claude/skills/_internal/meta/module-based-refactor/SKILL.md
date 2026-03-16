---
name: module-based-refactor
description: >
  Reorganize a repository from flat structure to a module-based 5-layer
  architecture (src/tests/specs/docs/examples) while preserving git history.
  Use when restructuring a codebase into modules, migrating import paths,
  cleaning up hidden folders, consolidating duplicate directories, removing
  root-level artifacts, or archiving completed plan files. Capabilities:
  parallel agent spawn strategy, hidden-folder consolidation patterns,
  benchmark fixture separation, 4-phase atomic commit workflow.
version: 3.2.0
updated: 2026-01-20
category: _internal
triggers:
- repository reorganization
- flat to module structure
- codebase restructuring
- module-based architecture
- import path migration
- git mv refactor
- 5-layer architecture
- artifact cleanup
- directory consolidation
- hidden folder cleanup
- hidden folder consolidation
- merge hidden folders
tags: []
---

# Module-Based Refactor Skill

Reorganize a repository from flat to a consistent module-based 5-layer
architecture while preserving git history. Handles cleanup of artifacts,
runtime data, and hidden folders.

See `references/patterns.md` for: full checklists, hidden-folder
consolidation patterns, cleanup categories table, benchmark reorganization,
complete session workflow, metrics tracking, and common issues/solutions.

## When to Use

- Reorganizing a flat repository to module-based layout
- Consolidating scattered modules into a unified hierarchy
- Migrating import paths while preserving git history
- Cleaning up root-level artifacts (logs, temp files, build artifacts)
- Consolidating duplicate directories (agents/, coordination/, memory/)
- Reviewing and removing obsolete hidden folders

## Pre-flight Checks

Run before starting any reorganization:

```bash
# Git tracking status
git ls-files | head -50
git ls-files --others --exclude-standard | grep -v "/"

# Duplicate directory detection
find . -type d -name "skills" -o -name "agents" 2>/dev/null

# Hidden folder inventory
ls -la .* 2>/dev/null | grep "^d"

# Stale artifacts at root
ls *.log *.tmp *.html *.sim 2>/dev/null
```

## Target Structure

```
src/<package>/modules/<module_name>/
tests/modules/<module_name>/
specs/modules/<module_name>/
docs/modules/<module_name>/
examples/modules/<module_name>/
```

## Process Steps

**Phase 1 — Analysis (parallel):** List directories, inventory root
artifacts, audit hidden folders.

**Phase 2 — Directory creation (sequential):**
```bash
mkdir -p src/<pkg>/modules tests/modules specs/modules docs/modules examples/modules
touch specs/modules/.gitkeep docs/modules/.gitkeep examples/modules/.gitkeep
```

**Phase 3 — Module moves (parallel per module):** Always use `git mv`.
```bash
git mv src/<pkg>/<module> src/<pkg>/modules/<module>
git mv tests/<module> tests/modules/<module>
```

**Phase 3.5 — Hidden folder consolidation (parallel per folder):**
See `references/patterns.md` §Hidden Folder Consolidation.

**Phase 4 — Import updates (parallel by file type):**
```bash
find . -name "*.py" -exec sed -i \
  's/from <pkg>\.<mod>/from <pkg>.modules.<mod>/g' {} \;
```

**Phase 5 — Cleanup (parallel):** Remove root artifacts, consolidate
agent dirs, update `.gitignore`.

**Phase 6 — Verification (parallel then sequential):**
```bash
uv run pytest tests/ -v
git log --follow --oneline -- src/<pkg>/modules/<module>/<file>.py
```

## Quick Start

```bash
# Pre-flight
git status && git ls-files --others --exclude-standard | wc -l

# Create module structure
mkdir -p src/<pkg>/modules tests/modules specs/modules docs/modules examples/modules

# Archive completed plan files
git mv specs/modules/<completed-plan>.md specs/archive/

# Verify after cleanup
uv run pytest tests/ -v && git status
```

## Atomic Commit Strategy

| Phase | Commit Message Pattern |
|-------|------------------------|
| 1 | `refactor: Reorganize to module-based 5-layer architecture` |
| 2 | `refactor: Consolidate <folders> into .claude (N files)` |
| 3 | `chore: Delete legacy config and consolidate scripts` |
| 4 | `docs: Update README structure and skill documentation` |

## Related Skills

- `../context-management/SKILL.md` — Managing context during large refactors
- `../meta/session-start-routine/SKILL.md` — Session initialization
