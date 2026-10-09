---
name: repo-cleanup-1-build-artifacts
description: 'Sub-skill of repo-cleanup: 1. Build Artifacts (+5).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# 1. Build Artifacts (+5)

## 1. Build Artifacts


Files generated during build/install processes that should not be tracked.

| Pattern | Description | Location |
|---------|-------------|----------|
| `*.egg-info/` | Python package metadata | `src/*/` |
| `__pycache__/` | Python bytecode cache | Throughout |
| `.pytest_cache/` | Pytest cache | Root and test dirs |
| `build/` | Build output directory | Root |
| `dist/` | Distribution packages | Root |
| `*.pyc` | Compiled Python files | Throughout |

*See sub-skills for full details.*

## 2. Log Files


Generated log files that accumulate during development and testing.

| Pattern | Description |
|---------|-------------|
| `*.log` | General log files |
| `*LogFile.txt` | OrcaFlex log files |
| `*.log.*` | Rotated log files |
| `debug.log` | Debug output |

**Cleanup commands:**

*See sub-skills for full details.*

## 3. Temp Files


Temporary files created during processing or editing.

| Pattern | Description |
|---------|-------------|
| `*.tmp` | Temporary files |
| `.temp/` | Temp directories |
| `cache/` | Cache directories |
| `*.bak` | Backup files |
| `*.swp` | Vim swap files |
| `*~` | Editor backup files |

*See sub-skills for full details.*

## 4. Coverage Reports


Test coverage artifacts that can be regenerated.

| Pattern | Description |
|---------|-------------|
| `htmlcov/` | HTML coverage reports |
| `.coverage` | Coverage data file |
| `.coverage.*` | Parallel coverage data |
| `coverage.xml` | XML coverage report |

**Cleanup commands:**
```bash
# Remove coverage artifacts
rm -rf htmlcov/
rm -f .coverage .coverage.* coverage.xml
```

## 5. IDE Artifacts


Editor and IDE generated files.

| Pattern | Description |
|---------|-------------|
| `.idea/` | PyCharm/IntelliJ |
| `.vscode/` | VS Code (keep settings.json) |
| `*.code-workspace` | VS Code workspaces |
| `.spyproject/` | Spyder IDE |

**Note:** Some IDE settings may be intentionally tracked. Check `.gitignore` first.

## 6. Benchmark Artifacts


Benchmark directories often contain mixed content that needs separation.

| Pattern | Description | Action |
|---------|-------------|--------|
| `benchmarks/reports/` | Timestamped HTML reports | Add to .gitignore |
| `benchmarks/results/` | Timestamped CSV/JSON | Add to .gitignore |
| `benchmarks/legacy_projects/` | Reference test data | Move to tests/fixtures/ |
| `benchmarks/*.py` | Benchmark scripts | Keep tracked |

**Cleanup commands:**

*See sub-skills for full details.*
