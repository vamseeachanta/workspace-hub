# Module-Based Refactor — Reference Patterns

Supporting detail for `../SKILL.md`. Contains checklists, hidden-folder
consolidation patterns, cleanup category tables, benchmark reorganization,
complete session workflow, metrics tracking, and common issues.

---

## Checklist

### Pre-Refactor
- [ ] Git working directory is clean
- [ ] All tests pass before refactor
- [ ] Created backup branch
- [ ] Documented current structure
- [ ] Pre-flight checks completed (SKILL.md §Pre-flight Checks)
- [ ] Duplicate directories identified
- [ ] Runtime vs config files categorized
- [ ] Hidden folders inventoried

### During Refactor — Module Structure
- [ ] All modules moved to modules/ subdirectory using `git mv`
- [ ] tests/modules/ created and populated
- [ ] specs/modules/ created (with .gitkeep if empty)
- [ ] docs/modules/ created (with .gitkeep if empty)
- [ ] examples/modules/ created (with .gitkeep if empty)

### During Refactor — Root-Level Artifact Cleanup
- [ ] Log files removed (*.log)
- [ ] Temp files removed (*.tmp, *.temp)
- [ ] Build artifacts removed (dist/, build/, *.egg-info/)
- [ ] Cache files removed (__pycache__/, .pytest_cache/)
- [ ] Test output files relocated or removed
- [ ] Prototype/experimental code relocated to examples/ or removed

### During Refactor — Directory Consolidation
- [ ] agents/ content moved to .claude/agent-library/
- [ ] Duplicate skill directories merged
- [ ] Empty directories removed

### During Refactor — Hidden Folder Review
- [ ] .agent-os/ — reviewed and cleaned (usually remove)
- [ ] .ai/ — reviewed and cleaned (usually remove)
- [ ] .drcode/ — reviewed and cleaned (usually remove)
- [ ] .claude/ — kept and organized
- [ ] .venv/ — confirmed in .gitignore

### During Refactor — Test Output Relocation
- [ ] HTML reports moved to tests/reports/ or removed
- [ ] Coverage reports moved to tests/coverage/ or removed
- [ ] Benchmark results moved to tests/benchmarks/ or removed

### During Refactor — Plan File Archival
- [ ] Completed plan files archived to specs/archive/
- [ ] Plan files checked for `status: completed` in YAML frontmatter

### During Refactor — Benchmark Reorganization
- [ ] Benchmark test fixtures moved to tests/fixtures/<tool_name>/
- [ ] Benchmark generated outputs (reports/, results/) added to .gitignore
- [ ] Empty benchmark structure maintained with .gitkeep

### Post-Refactor
- [ ] `__init__.py` files created with proper exports
- [ ] All import references updated
- [ ] `pyproject.toml` updated if needed
- [ ] Tests pass after refactor
- [ ] No broken imports found
- [ ] Git history preserved (verify with `git log --follow`)
- [ ] .gitignore updated with new patterns
- [ ] No untracked files at root level (except intended ones)

---

## Cleanup Categories Quick Reference

| Category | Examples | Action |
|----------|----------|--------|
| Root-level artifacts | *.log, *.tmp, *.html | Delete or move to outputs/ |
| Build artifacts | dist/, build/, *.egg-info | Delete (regenerated on build) |
| Cache files | __pycache__/, .pytest_cache/ | Delete and .gitignore |
| Duplicate dirs | agents/, .claude/agents/ | Consolidate to .claude/agent-library/ |
| Legacy hidden | .agent-os/, .ai/, .drcode/ | Review and usually delete |
| Test outputs | reports/, coverage/, snapshots/ | Move under tests/ |
| Prototype code | scratch_*.py, experimental/ | Move to examples/ |
| Test data | *.csv, *.json at root | Move to tests/test_data/ |
| Config files | *.yaml, *.toml, *.json | Keep at root or move to config/ |
| Benchmark fixtures | legacy test data files | Move to tests/fixtures/<tool_name>/ |
| Benchmark outputs | timestamped reports/results | Add to .gitignore |
| Completed plans | status: completed in frontmatter | Archive to specs/archive/ |

---

## Common Patterns Found During Reorganization

### 1. Duplicate Agent Directories

```
agents/                          # Root-level (often untracked)
.claude/agents/                  # Claude-specific
.claude/agent-library/           # Preferred location
.agent-os/agents/                # Legacy AI OS structure

# Resolution: Consolidate to .claude/agent-library/
git mv agents/* .claude/agent-library/
rm -rf agents/
```

### 2. Scattered Runtime Data

```
coordination/                    # Untracked runtime state
memory/                          # Untracked memory store

# Resolution: Delete untracked coordination/ and memory/
```

### 3. Untracked Artifacts in Root

```
*.log *.html *_output.* *.sim *.dat

# Resolution:
# - Delete if not needed
# - Move to inputs/ or outputs/ if needed
# - Add patterns to .gitignore
```

### 4. Multiple Skill/Command Locations

```
.claude/skills/ skills/ .agent-os/skills/ commands/

# Resolution: Consolidate to .claude/skills/
```

### 5. Legacy Hidden Folders

```
.agent-os/ .ai/ .drcode/ .cursor/ .vscode/

# Resolution:
# - .vscode/, .cursor/ - keep if used, add to .gitignore
# - .agent-os/, .ai/, .drcode/ - usually safe to remove after audit
```

### 6. Test Data in Wrong Locations

```
test_data/ fixtures/ data/  # Root level (wrong)
tests/test_data/            # Correct location

# Resolution: Move all to tests/test_data/ or tests/fixtures/
```

### 7. Prototype Code Mixed with Production

```
src/package/experimental/     # Should be separate
scripts/scratch_*.py          # Should be in examples/experiments/

# Resolution: Move to examples/experiments/ or examples/prototypes/
```

---

## Hidden Folder Consolidation Patterns

When consolidating multiple hidden folders into `.claude/`:

### Pre-consolidation Analysis

```bash
# Count tracked files per hidden folder
git ls-files .claude/ | wc -l
git ls-files .agent-os/ | wc -l
git ls-files .ai/ | wc -l

# Identify overlapping content
comm -12 <(ls .claude/ | sort) <(ls .agent-os/ | sort)

# Determine authoritative source
git log --oneline -5 -- .claude/
git log --oneline -5 -- .agent-os/
```

### Create Merge Plan

| Source Folder | Destination | Strategy | Reason |
|---------------|-------------|----------|--------|
| .agent-os/commands/ | .claude/commands/legacy-scripts/ | Rename | .claude/commands/ already exists |
| .agent-os/hooks/ | .claude/hooks/legacy/ | Rename | .claude/hooks/ already exists |
| .agent-os/docs/ | .claude/docs/ | Merge | Unique documentation content |
| .agent-os/standards/ | .claude/standards/ | Direct move | Does not exist in .claude/ |
| .ai/implementation-history/ | .claude/implementation-history/ | Direct move | Unique content |
| Conflicting README.md | README-legacy.md | Rename | Preserve both versions |

### Merge Pattern 1 — Conflicting Directories (Rename)

```bash
git mv .agent-os/commands .claude/commands/legacy-scripts
git mv .agent-os/hooks .claude/hooks/legacy
```

### Merge Pattern 2 — Non-Conflicting Directories (Direct Move)

```bash
git mv .agent-os/standards .claude/standards
git mv .ai/implementation-history .claude/implementation-history
```

### Merge Pattern 3 — Mergeable Directories (Combine Content)

```bash
git mv .agent-os/docs/unique-file.md .claude/docs/
git mv .ai/docs/another-file.md .claude/docs/
```

### Merge Pattern 4 — Conflicting Files (Rename with Suffix)

```bash
git mv .agent-os/README.md .claude/README-agent-os-legacy.md
git mv .ai/README.md .claude/README-ai-legacy.md
```

### Real-World Example: digitalmodel Repository

Before: `.claude/` 519 files + `.agent-os/` 129 files + `.ai/` 52 files
After: `.claude/` 670 files (30 were duplicates/merged)

### Consolidation Checklist

- [ ] Count files in each source folder: `git ls-files <dir> | wc -l`
- [ ] Identify overlapping directory names
- [ ] Identify overlapping file names
- [ ] Create merge plan with conflict resolution strategy
- [ ] Execute moves in parallel per source folder
- [ ] Verify no files were lost: compare totals
- [ ] Remove empty source folders
- [ ] Update any references to old paths
- [ ] Commit with descriptive message noting file counts

---

## Benchmark Directory Reorganization

Benchmark directories often contain mixed content: test fixtures that should
be tracked vs generated outputs that should be gitignored.

```bash
# 1. Move test fixtures to tests/fixtures/
git mv benchmarks/legacy_projects/ tests/fixtures/orcaflex/

# 2. Add generated output directories to .gitignore
cat >> .gitignore << 'EOF'
benchmarks/reports/
benchmarks/results/
EOF

# 3. Create .gitkeep for empty benchmark structure
mkdir -p benchmarks/reports benchmarks/results
touch benchmarks/.gitkeep
```

### Benchmark Content Classification

| Content Type | Examples | Action |
|--------------|----------|--------|
| Test fixtures | legacy_projects/*.dat | `git mv` to tests/fixtures/<tool_name>/ |
| Generated reports | *_report_YYYYMMDD.html | Add to .gitignore |
| Generated results | results_YYYYMMDD.csv | Add to .gitignore |
| Benchmark scripts | run_benchmarks.py | Keep in benchmarks/ |

---

## Complete Refactor Session Workflow

### Phase 1 — Module Reorganization

```bash
git mv src/<pkg>/<module> src/<pkg>/modules/<module>
git mv tests/<module> tests/modules/<module>
git mv specs/<module> specs/modules/<module>
find . -name "*.py" -exec sed -i 's/from <pkg>.<mod>/from <pkg>.modules.<mod>/g' {} \;
git commit -m "refactor: Reorganize repository to module-based 5-layer architecture"
```

### Phase 2 — Hidden Folder Consolidation

```bash
git mv .agent-os/commands .claude/commands/legacy-scripts
git mv .agent-os/standards .claude/standards
git mv .ai/implementation-history .claude/implementation-history
rm -rf .agent-runtime .common .specify
git commit -m "refactor: Consolidate .agent-os + .ai into .claude (670 files)"
```

### Phase 3 — Final Cleanup

```bash
rm -rf .drcode/ .benchmarks/
git mv .git-commands/* scripts/git/
rm -rf .git-commands/
git commit -m "chore: Delete legacy config and consolidate scripts"
```

### Phase 4 — Documentation and Archival

```bash
grep -l "status: completed" specs/modules/*.md
git mv specs/modules/<completed-plan>.md specs/archive/
git commit -m "docs: Update README structure and skill documentation"
```

---

## Metrics Tracking

```bash
# Pre-consolidation baseline
echo ".claude/: $(git ls-files .claude/ | wc -l) files"
echo ".agent-os/: $(git ls-files .agent-os/ | wc -l) files"
git ls-files .claude/ .agent-os/ .ai/ | wc -l > /tmp/pre_consolidation_count.txt

# Post-consolidation verification
actual=$(git ls-files .claude/ | wc -l)
expected=$(cat /tmp/pre_consolidation_count.txt)
[ "$actual" -ge "$expected" ] && echo "SUCCESS" || echo "WARNING: missing files"
```

---

## Post-cleanup Verification

### 1. Import Verification

```bash
uv run --no-project python -c "
import sys; sys.path.insert(0, 'src')
modules = ['<pkg>', '<pkg>.modules', '<pkg>.modules.<mod>']
for m in modules:
    try: __import__(m); print(f'OK {m}')
    except ImportError as e: print(f'FAIL {m}: {e}')
"
```

### 2. Git Status Review

```bash
git status
git ls-files --others --exclude-standard
git log --follow --oneline -- src/<pkg>/modules/<mod>/<file>.py
```

### 3. Test Suite Execution

```bash
uv run pytest tests/ -v
uv run pytest tests/ --cov=src/<pkg> --cov-report=term-missing
```

### 4. Gitignore Verification

Recommended patterns:
```
*.log
*.tmp
__pycache__/
.pytest_cache/
dist/
build/
*.egg-info/
.coverage
htmlcov/
benchmarks/reports/
benchmarks/results/
```

---

## Common Issues and Solutions

**Circular imports after refactor:**
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from digitalmodel.modules.other import OtherClass
```

**Relative imports broken:** Convert to absolute imports.

**Test discovery fails:** Ensure `conftest.py` at `tests/modules/` level:
```python
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
```

**Package not found after move:** Update `pyproject.toml`:
```toml
[tool.setuptools.packages.find]
where = ["src"]
include = ["<pkg>*"]
```

---

## Version History

- **3.2.0** (2026-01-20): Added Plan File Archival and Benchmark Reorganization
- **3.1.0** (2026-01-20): Added Complete Refactor Session Workflow
- **3.0.0** (2026-01-20): Added Hidden Folder Consolidation Patterns
- **2.0.0** (2025-01-20): Added Pre-flight Checks, Parallel Execution Strategy,
  Common Patterns, Post-cleanup Verification
