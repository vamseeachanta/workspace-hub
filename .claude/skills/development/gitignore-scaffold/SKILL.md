---
name: gitignore-scaffold
description: Gitignore pattern setup and directory scaffolding — covers negation patterns, .gitkeep tracking, and git check-ignore verification workflows
type: reference
version: 1.0.0
category: development
capabilities:
  - gitignore_pattern_design
  - directory_scaffolding
  - negation_patterns
tools: [Bash, Read, Edit, Grep]
related_skills: [shell-tdd, tdd-obra]
requires: []
see_also: []
tags: []
---

# gitignore-scaffold

## Quick Start

When adding directories that must exist in git but whose contents should be ignored,
use the `directory/*` pattern (not `directory/`) combined with `.gitkeep` negation.

```gitignore
data/standards/promoted/*          # ignore contents
!data/standards/promoted/.gitkeep  # but track .gitkeep
```

## When to Use

- Setting up empty directory structures that must persist in version control
- Adding gitignore rules for data directories, build outputs, or cache folders
- Troubleshooting why `.gitkeep` files are not being tracked

## Workflow

### 1. Create directory structure

```bash
mkdir -p data/standards/promoted
```

### 2. Add `.gitkeep` to empty directories

```bash
touch data/standards/promoted/.gitkeep
```

### 3. Add gitignore patterns

Use `directory/*` form — **never** `directory/` when `.gitkeep` must be tracked.

```gitignore
data/standards/promoted/*
!data/standards/promoted/.gitkeep
```

### 4. Verify with `git check-ignore`

```bash
# Should be ignored (exit 0):
git check-ignore -q "data/standards/promoted/example.csv"

# Should NOT be ignored (exit 1):
git check-ignore -q "data/standards/promoted/.gitkeep"
```

### 5. Regression-test existing patterns

After modifying `.gitignore`, confirm pre-existing patterns still work:

```bash
git check-ignore -q "path/to/known-ignored-file"
```

## Pattern Types — Critical Distinction

| Pattern | Ignores | Negation works? |
|---------|---------|-----------------|
| `directory/` | Directory AND everything inside | No — git skips the entire tree |
| `directory/*` | Only the contents | Yes — individual files can be negated |

**Rule:** Always use `directory/*` when you need to negate specific files inside.

## Common Gotchas

1. **`directory/` kills negation** — the most common mistake. Git never looks inside
   a fully-ignored directory, so `!directory/.gitkeep` has no effect.
2. **Order matters** — the negation line (`!`) must appear *after* the ignore line.
3. **Nested negation** — for deeply nested paths, every ancestor directory must use
   the `/*` form, not the `/` form.
4. **Cached files** — if a file was already tracked before the ignore rule was added,
   `git rm --cached <file>` is required to stop tracking it.
5. **Always verify** — never trust visual inspection of `.gitignore`; run
   `git check-ignore -q` to confirm behavior programmatically.
