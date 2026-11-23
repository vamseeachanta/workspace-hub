# Workspace File-Structure Taxonomy

> Standard classification of workspace-hub top-level directories for consistent human and AI navigation.
>
> Version: 1.0.0 | Date: 2026-03-31 | Issue: #1533

---

## Directory Classification

### Child Repositories (managed git repos)

These are independent git repositories managed under the workspace-hub umbrella. See [WORKSPACE_HUB_REPOSITORY_OVERVIEW.md](../WORKSPACE_HUB_REPOSITORY_OVERVIEW.md) for the full list (25 repos).

### Source & Build

| Directory | Purpose | Tracking |
|-----------|---------|----------|
| `src/` | Workspace-hub source code | Git-tracked |
| `tests/` | Test suite | Git-tracked |
| `dist/` | Build output | Gitignored |
| `node_modules/` | Node dependencies | Gitignored |
| `workspace_hub.egg-info/` | Python package metadata | Gitignored |

### Configuration

| Directory | Purpose | Tracking |
|-----------|---------|----------|
| `config/` | Shared configurations | Git-tracked |
| `.github/` | GitHub Actions, templates | Git-tracked |
| `.vscode/` | VS Code workspace settings | Git-tracked (selective) |

### Control Plane (AI Agent)

| Directory | Purpose | Tracking |
|-----------|---------|----------|
| `.claude/` | Claude provider adapter (skills, rules, docs, hooks) | Git-tracked (selective) |
| `.codex/` | Codex provider adapter | Git-tracked |
| `.gemini/` | Gemini provider adapter | Git-tracked |

### Documentation

| Directory | Purpose | Tracking |
|-----------|---------|----------|
| `docs/` | All persistent documentation (guides, standards, reports, plans) | Git-tracked |
| `knowledge/` | Domain knowledge seeds and references | Git-tracked |
| `knowledge-base/` | Structured knowledge base | Git-tracked |
| `examples/` | Usage examples | Git-tracked |
| `templates/` | Document and project templates | Git-tracked |

### Operational Infrastructure

| Directory | Purpose | Tracking |
|-----------|---------|----------|
| `modules/` | Functional modules (git-management, automation, ci-cd, etc.) | Git-tracked |
| `scripts/` | Automation and utility scripts | Git-tracked |
| `tools/` | Development tools | Git-tracked |
| `docker/` | Container definitions | Git-tracked |
| `admin/` | Administrative tools | Git-tracked |
| `assets/` | Static assets | Git-tracked |
| `data/` | Data files | Git-tracked (selective) |

### Runtime & Transient State

| Directory | Purpose | Tracking |
|-----------|---------|----------|
| `state/` | Runtime state files | Gitignored |
| `logs/` | Log output | Gitignored |
| `queue/` | Work queue (solver queue) | Gitignored |
| `reports/` | Generated reports | Gitignored |
| `notes/` | Scratch notes | Gitignored |
| `coordination/` | Multi-agent coordination state | Gitignored |
| `monitoring-dashboard/` | Monitoring UI | Gitignored |

### Planning & Workflow

| Directory | Purpose | Tracking |
|-----------|---------|----------|
| `.planning/` | GSD planning artifacts (phase plans, research, codebase maps) | Git-tracked (selective) |
| `.worktrees/` | Git worktree workspace metadata | Gitignored |
| `specs/` | Legacy specs (migrated to .planning/ as of 2026-03-26) | Gitignored |

### Archive & Historical

| Directory | Purpose | Tracking |
|-----------|---------|----------|
| `_archive/` | Archived/completed milestone artifacts | Git-tracked |

### Legacy (to be evaluated)

| Directory | Purpose | Disposition |
|-----------|---------|-------------|
| `.swarm/` | Legacy swarm coordination | Evaluate for removal |
| `.hive-mind/` | Legacy multi-agent orchestration | Evaluate for removal |
| `.sync-reports/` | Sync report output | Evaluate for removal |
| `.SLASH_COMMAND_ECOSYSTEM/` | Legacy slash command registry | Evaluate for removal |
| `pyproject-starter/` | Template directory (not a git repo) | Keep as template or move to templates/ |

### Cache (auto-generated, all gitignored)

`.baseline-cache/`, `.cache/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.uv-cache/`, `.venv/`, `.venv-test/`

---

## Naming Conventions

| Category | Convention | Examples |
|----------|-----------|----------|
| Child repos | lowercase, hyphenated | `digitalmodel`, `world-energy-data` |
| Operational dirs | lowercase, no prefix | `docs/`, `scripts/`, `config/` |
| Hidden config | dot-prefix | `.claude/`, `.github/` |
| Archive | underscore-prefix | `_archive/` |
| Generated/transient | lowercase | `logs/`, `state/`, `queue/` |
| Legacy/evaluate | dot-prefix, CAPS for emphasis | `.SLASH_COMMAND_ECOSYSTEM/` |

---

## Starter Repo Taxonomy Expectations

For each starter repo (digitalmodel, worldenergydata, assethold, assetutilities), the expected top-level structure:

```
repo-name/
├── AGENTS.md              # Required — workflow contract
├── CLAUDE.md              # Required — Claude config
├── README.md              # Required — project overview
├── .claude/               # Required — Claude adapter
├── .codex/                # Required — Codex adapter (can be minimal)
├── .gemini/               # Required — Gemini adapter (can be minimal)
├── .gitignore             # Required
├── src/ or repo_name/     # Source code (Python packages use package name)
├── tests/                 # Test suite
├── docs/                  # Documentation (if substantial)
├── pyproject.toml         # Python project metadata
└── .mcp.json              # Where applicable
```

---

## Migration Recommendations

1. **`pyproject-starter/`**: Move to `templates/pyproject-starter/` or remove if unused
2. **`.swarm/`, `.hive-mind/`**: Archive or remove after confirming no active dependencies
3. **`.SLASH_COMMAND_ECOSYSTEM/`**: Archive — replaced by .claude/skills/
4. **`.sync-reports/`**: Move to `_archive/` or remove if no longer generated
5. **`specs/`**: Already migrated to `.planning/` — confirm empty and remove
