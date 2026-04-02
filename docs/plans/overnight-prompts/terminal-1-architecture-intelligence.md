# Terminal 1 — Claude — Architecture Intelligence + Roadmaps

We are in /mnt/local-analysis/workspace-hub. Execute these 3 tasks in order.
Use `uv run` for all Python — never bare `python3` or `pip`.
Commit to main and push after each task. Do not branch.
Run `git pull origin main` before every push.
TDD: write tests before implementation.
Do NOT ask the user any questions — make reasonable decisions and document them.

## TASK 1: Architecture Scanner — API Surface + Import Dependency Graph (GH #1604)

### Context
The digitalmodel repo at /mnt/local-analysis/workspace-hub/digitalmodel/ has 1,594 Python source files
across 31+ packages under digitalmodel/src/digitalmodel/. The packages include:
ansys, asset_integrity, benchmarks, cathodic_protection, data_models, data_systems,
drilling_riser, fatigue, field_development, geotechnical, gis, hydrodynamics,
infrastructure, marine_ops, naval_architecture, nde, orcaflex, orcawave, power,
production_engineering, reservoir, signal_processing, solvers, specialized, specs,
structural, subsea, visualization, web, well, workflows.

### What to do
1. Write a Python script `scripts/analysis/architecture-scanner.py` that:
   - Walks all .py files under digitalmodel/src/digitalmodel/
   - For each package: counts modules, classes, functions, lines of code
   - Detects public API surface (functions/classes not prefixed with _)
   - Builds an import dependency graph (which package imports which)
   - Outputs a structured YAML report
2. Write tests first in `tests/analysis/test_architecture_scanner.py`
3. Run the scanner and save output to `docs/architecture/api-surface-map.md`
4. Include a mermaid dependency graph in the output

### Acceptance criteria
- Scanner script exists and runs with `uv run python scripts/analysis/architecture-scanner.py`
- Tests pass with `uv run pytest tests/analysis/test_architecture_scanner.py -v`
- docs/architecture/api-surface-map.md contains package-level summary table + dependency graph
- At least 31 packages enumerated with class/function/LOC counts

### Commit message
feat(arch): add architecture scanner with API surface + dependency graph (#1604)

---

## TASK 2: Consolidated Module Status Matrix (GH #1567)

### Context
Feature #1567 needs "consolidated cross-repo module status view". The maturity tracker
already classifies packages into SKELETON, DEVELOPMENT, PRODUCTION. Existing data is
in docs/modules/ and .planning/archive/. The goal is a single consolidated view.

### What to do
1. Extend the architecture scanner or write a companion script `scripts/analysis/module-status-matrix.py`
2. For each package under digitalmodel, determine:
   - Has tests? (check tests/ directory for matching test files)
   - Has docstrings? (sample 3 files per package, check for module/class docstrings)
   - Has __init__.py with __all__?
   - Classify as SKELETON (no tests), DEVELOPMENT (some tests), or PRODUCTION (tests + docstrings + __all__)
3. Output to `docs/architecture/module-status-matrix.md` as a table
4. Include summary counts: N PRODUCTION, M DEVELOPMENT, P SKELETON

### Acceptance criteria
- docs/architecture/module-status-matrix.md exists with all 31+ packages classified
- Summary line at top: "X/31 PRODUCTION, Y/31 DEVELOPMENT, Z/31 SKELETON"

### Commit message
feat(arch): consolidated module status matrix across digitalmodel packages (#1567)

---

## TASK 3: Domain-Specific Capability Roadmap — OrcaWave/OrcaFlex (GH #1572)

### Context
The workspace-hub has extensive OrcaWave/OrcaFlex integration. Key files:
- digitalmodel/src/digitalmodel/orcawave/ (13 source files)
- digitalmodel/src/digitalmodel/orcaflex/ (check for files)
- scripts/solver/ (git-based job dispatch)
- hull_library/ (20+ modules incl. rao_database.py)
- 13 live spec.yml files (L00-L04 cases)
Open engineering issues: #1595-#1598, #1605-#1607, #1586, #1588, #1592

### What to do
1. Read all orcawave/ and orcaflex/ source files to understand current capabilities
2. Read all open issues tagged cat:engineering + domain:marine
3. Produce `docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` containing:
   - Current capabilities (what works today, with file references)
   - Known gaps (from open issues)
   - Recommended priority order for closing gaps
   - Dependency chain (which issues unblock which)
   - Timeline estimate (near-term vs medium-term vs long-term)

### Acceptance criteria
- Roadmap references at least 10 specific source files
- Maps at least 8 open issues to capability gaps
- Has clear near/medium/long-term sections

### Commit message
docs(roadmap): OrcaWave/OrcaFlex domain capability roadmap (#1572)

---

## After all tasks
Post a brief progress comment on each GitHub issue (#1604, #1567, #1572) in repo vamseeachanta/workspace-hub:
"Overnight agent run (2026-04-01): [artifact] committed. See [path]."
