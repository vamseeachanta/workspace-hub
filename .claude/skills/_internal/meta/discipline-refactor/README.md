# Discipline-Based Refactor (v2.0)

Reorganize any repository to **module-based, discipline-aligned structure**.

## Quick Start

Invoke with:
- "refactor by discipline"
- "module-based organization"
- "restructure repository"

## Core Principles

1. **All folders are module-based** - `<folder>/modules/<discipline>/`
2. **Code lives in modules** - `src/<pkg>/modules/<discipline>/`
3. **Documents mirror code** - Same discipline names everywhere
4. **Consistent taxonomy** - Same disciplines across all folders

## Target Structure

```
<repo>/
├── src/<package>/modules/<discipline>/
├── tests/modules/<discipline>/
├── docs/modules/<discipline>/
├── specs/modules/<discipline>/
├── data/modules/<discipline>/
├── .claude/skills/<discipline>/
└── pyproject.toml
```

## Phases

| Phase | Subagent | Skills Called |
|-------|----------|---------------|
| 1. Analysis | Explore | - |
| 2. Planning | Plan | skill-creator |
| 3. Execution | general-purpose | git-sync-manager, parallel-batch-executor |
| 4. Validation | Bash | - |

## Standard Disciplines

| Discipline | Purpose |
|------------|---------|
| `_core` | Shared utilities, base classes |
| `engineering` | Domain expertise |
| `data` | ETL, storage, visualization |
| `api` | External interfaces |
| `automation` | Workflows, CI/CD |
| `_internal` | Meta tools, guidelines |

## Exceptions (Keep Flat)

- `specs/templates/` - Shared templates
- `docs/assets/` - Shared images
- `scripts/` - Build scripts
- `config/` - Configuration
- `.claude/state/` - Runtime state

## Rollback

```bash
git checkout pre-module-refactor-{date}
```

## Full Documentation

See [SKILL.md](./SKILL.md) for complete workflow and examples.
