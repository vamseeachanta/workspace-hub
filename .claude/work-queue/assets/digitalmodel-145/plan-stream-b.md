# Stream B: Calculation Coverage — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Map all calculations that should exist across 4 public repos, implement the highest-value ones, capture gaps as WRK items, and write the calculations vision doc.

**Architecture:** Three-phase approach: (1) audit existing calculations against standards in the capability map and ledger, (2) implement highest-value calculations using TDD and the calculation-report skill, (3) capture remaining gaps as WRK items and write the vision doc in digitalmodel.

**Tech Stack:** Python (uv run), PyYAML, pytest, calculation-report schema, existing capability maps

**Parent WRK:** WRK-1179 (Feature WRK)

**Mandatory:** All calculations MUST follow the `calculation-report` skill (`.claude/skills/data/calculation-report/SKILL.md`). Every implementation produces a YAML validated against `config/reporting/calculation-report-schema.yaml`.

---

## Chunk 1: Audit & Gap Map (Days 1–3)

### Task 1: Audit digitalmodel Calculations

**Files:**
- Read: `digitalmodel/src/digitalmodel/` (all subdirectories)
- Read: `specs/capability-map/digitalmodel.yaml` (27 modules, 17,799 standards mapped)
- Read: `data/document-index/standards-transfer-ledger.yaml`
- Create: `specs/capability-map/audit/digitalmodel-calc-audit.md`

- [ ] **Step 1: Catalog all existing calculation functions**

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
uv run python -c "
import ast, os, sys
results = []
for root, dirs, files in os.walk('src/digitalmodel'):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if not f.endswith('.py') or f.startswith('_'):
            continue
        path = os.path.join(root, f)
        try:
            tree = ast.parse(open(path).read())
            funcs = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.name.startswith('_')]
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if funcs or classes:
                rel = path.replace('src/digitalmodel/', '')
                results.append({'file': rel, 'functions': funcs, 'classes': classes})
        except:
            pass
print(f'Files with public functions/classes: {len(results)}')
for r in sorted(results, key=lambda x: x['file'])[:30]:
    print(f\"  {r['file']}: {len(r['functions'])} funcs, {len(r['classes'])} classes\")
print(f'  ... (showing first 30)')
"
```
Expected: catalog of all calculation modules with function counts

- [ ] **Step 2: Cross-reference with capability map**

For each of the 27 modules in `specs/capability-map/digitalmodel.yaml`:
- Does the source module exist?
- How many standards are mapped (gap vs. done)?
- What calculations are already implemented?

```bash
uv run --no-project python -c "
import yaml
with open('specs/capability-map/digitalmodel.yaml') as f:
    data = yaml.safe_load(f)
for m in data['modules']:
    standards = m.get('standards', [])
    gap = sum(1 for s in standards if s.get('status') == 'gap')
    done = sum(1 for s in standards if s.get('status') == 'done')
    total = m.get('standards_count', len(standards))
    pct = done*100//total if total else 0
    print(f'{m[\"module\"]:40s} total={total:5d}  done={done:3d}  gap={gap:3d}  ({pct}%)')
"
```

- [ ] **Step 3: Identify calculation disciplines in digitalmodel**

Map source directories to engineering disciplines:

| Directory | Discipline | Key Calculations Expected |
|-----------|-----------|--------------------------|
| structural/ | Structural engineering | Fatigue (S-N, Miner), member capacity, buckling, stress |
| subsea/ | Subsea engineering | Pipeline wall thickness, collapse, stability, riser config |
| cathodic_protection/ | Corrosion | Anode design, coating breakdown, CP assessment |
| hydrodynamics/ | Hydrodynamics | Wave spectra, RAO, diffraction, Morison loading |
| marine_ops/ | Marine operations | Installation analysis, lifting, vessel ops |
| asset_integrity/ | Asset integrity | API 579 FFS, fracture mechanics, corrosion allowance |
| well/ | Well engineering | Casing design, hydraulics, torque & drag |
| drilling_riser/ | Drilling | Riser analysis, BOP stack |
| field_development/ | Field development | Concept screening, economics |
| naval_architecture/ | Naval architecture | Stability, hull design |
| geotechnical/ | Geotechnical | Pile capacity, scour, anchoring |

- [ ] **Step 4: Write audit report**

Create `specs/capability-map/audit/digitalmodel-calc-audit.md`:
- Per-discipline: existing functions, standards coverage, gap count
- Priority ranking: which gaps are highest value to implement
- Design data availability: which gaps have standard docs in the index

- [ ] **Step 5: Commit audit**

```bash
git add specs/capability-map/audit/
git commit -m "docs(WRK-1179): digitalmodel calculation audit" && git push
```

---

### Task 2: Audit assethold Calculations

**Files:**
- Read: `assethold/src/assethold/`
- Create: `specs/capability-map/audit/assethold-calc-audit.md`

- [ ] **Step 1: Catalog existing calculations**

```bash
cd /mnt/local-analysis/workspace-hub/assethold
uv run python -c "
import ast, os
for root, dirs, files in os.walk('src/assethold'):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if not f.endswith('.py') or f.startswith('_'):
            continue
        path = os.path.join(root, f)
        try:
            tree = ast.parse(open(path).read())
            funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and not n.name.startswith('_')]
            if funcs:
                print(f'{path.replace(\"src/assethold/\",\"\")}: {funcs}')
        except:
            pass
"
```

- [ ] **Step 2: Identify financial calculation gaps**

Expected calculations for an energy portfolio tool:
- VaR (Value at Risk) — parametric and historical
- CVaR (Conditional VaR / Expected Shortfall)
- Sharpe ratio and Sortino ratio
- Maximum drawdown
- GICS sector classification
- Covered call premium calculator
- Portfolio correlation matrix
- Beta calculation (vs. benchmark)
- Arps decline curves (if not in worldenergydata)

- [ ] **Step 3: Write audit report**

Create `specs/capability-map/audit/assethold-calc-audit.md`

- [ ] **Step 4: Commit**

```bash
git add specs/capability-map/audit/assethold-calc-audit.md
git commit -m "docs(WRK-1179): assethold calculation audit" && git push
```

---

### Task 3: Audit assetutilities Calculations

**Files:**
- Read: `assetutilities/src/assetutilities/`
- Create: `specs/capability-map/audit/assetutilities-calc-audit.md`

- [ ] **Step 1: Catalog existing utilities**

```bash
cd /mnt/local-analysis/workspace-hub/assetutilities
uv run python -c "
import ast, os
for root, dirs, files in os.walk('src/assetutilities'):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if not f.endswith('.py') or f.startswith('_'):
            continue
        path = os.path.join(root, f)
        try:
            tree = ast.parse(open(path).read())
            funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and not n.name.startswith('_')]
            if funcs:
                print(f'{path.replace(\"src/assetutilities/\",\"\")}: {funcs}')
        except:
            pass
"
```

- [ ] **Step 2: Identify shared utility gaps**

Expected shared utilities:
- Unit conversion library (SI ↔ Imperial, engineering units)
- Material properties (API 5L steel grades, seawater properties)
- Engineering constants (g, rho_seawater, etc.)
- Common math helpers (interpolation, integration)

- [ ] **Step 3: Write audit report and commit**

```bash
git add specs/capability-map/audit/assetutilities-calc-audit.md
git commit -m "docs(WRK-1179): assetutilities calculation audit" && git push
```

---

### Task 4: Audit worldenergydata Calculations

**Files:**
- Read: `worldenergydata/src/worldenergydata/`
- Create: `specs/capability-map/audit/worldenergydata-calc-audit.md`

- [ ] **Step 1: Catalog existing data analysis functions**

Focus on modules that do calculations (not just data loading):
- `production/` — decline curve analysis?
- `economics/` — NPV, MIRR, IRR?
- `cost/` — cost benchmarking formulas?
- `well_bore_design/` — casing design calculations?

- [ ] **Step 2: Identify calculation gaps**

Expected calculations:
- Arps decline curves (exponential, hyperbolic, harmonic) — WRK-318
- Type curve matching
- NPV/MIRR with carbon cost sensitivity — WRK-321
- Drilling cost per foot benchmarking
- Production forecasting
- Resource estimation (probabilistic — P10/P50/P90)

- [ ] **Step 3: Write audit report and commit**

```bash
git add specs/capability-map/audit/worldenergydata-calc-audit.md
git commit -m "docs(WRK-1179): worldenergydata calculation audit" && git push
```

---

### Task 5: Day 3 Checkpoint — Consolidated Gap Map

- [ ] **Step 1: Merge all audit reports into a priority table**

Create `specs/capability-map/audit/consolidated-gap-priority.md`:
- All gaps across 4 repos ranked by:
  1. Standard doc available in index? (can implement now)
  2. Workflow pattern dependency (unlocks Pattern 1–4?)
  3. Complexity (low/medium/high)
  4. Test data availability

- [ ] **Step 2: Present to user for priority confirmation**

Show top 20 gaps recommended for implementation in Days 4–12.

- [ ] **Step 3: Commit consolidated map**

```bash
git add specs/capability-map/audit/consolidated-gap-priority.md
git commit -m "docs(WRK-1179): consolidated calculation gap priority map" && git push
```

---

## Chunk 2: Implement Calculations (Days 4–12)

### Task 6: Implement digitalmodel Calculations (Structural)

For each prioritized structural calculation gap:

- [ ] **Step 1: Write failing test**

```python
# digitalmodel/tests/test_<module>_<calc>.py
def test_<calc>_worked_example():
    """Worked example from <STANDARD> Section <X.Y>"""
    from digitalmodel.<discipline>.<module> import <calc_function>
    result = <calc_function>(
        # inputs from standard worked example
    )
    assert abs(result.value - <expected>) < <tolerance>
    assert result.standard == "<STANDARD-ID>"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
PYTHONPATH=src uv run python -m pytest tests/test_<module>_<calc>.py -v
```
Expected: FAIL

- [ ] **Step 3: Implement calculation**

Create/modify `digitalmodel/src/digitalmodel/<discipline>/<module>.py`:
- Function with typed inputs and outputs
- Standard reference in docstring
- Traceable to specific clause

- [ ] **Step 4: Run test to verify it passes**

```bash
PYTHONPATH=src uv run python -m pytest tests/test_<module>_<calc>.py -v
```
Expected: PASS

- [ ] **Step 5: Create calculation report YAML**

Create `examples/reporting/<calc-name>.yaml` following @calculation-report skill:
```yaml
metadata:
  title: "<Calculation Name>"
  doc_id: "CALC-<NNN>"
  revision: "A"
  date: "2026-03-XX"
  author: "ACE Engineering"
  status: draft
inputs:
  - name: "<input name>"
    symbol: "<LaTeX symbol>"
    value: <value>
    unit: "<unit>"
    source: "<STANDARD> Table X.Y"
methodology:
  description: "<what this calculates>"
  standard: "<STANDARD-ID>"
  equations:
    - id: eq1
      name: "<equation name>"
      latex: "<LaTeX formula>"
      description: "<what it computes>"
outputs:
  - name: "<output name>"
    symbol: "<LaTeX symbol>"
    value: <value>
    unit: "<unit>"
    pass_fail: pass
    limit: <limit_value>
assumptions:
  - "<assumption 1>"
references:
  - "<STANDARD full title>, Section X.Y"
```

- [ ] **Step 6: Validate YAML against schema**

```bash
uv run --no-project python -c "
import yaml

with open('config/reporting/calculation-report-schema.yaml') as f:
    schema = yaml.safe_load(f)
with open('examples/reporting/<calc-name>.yaml') as f:
    report = yaml.safe_load(f)

# Check required top-level sections
required = ['metadata', 'inputs', 'methodology', 'outputs', 'assumptions', 'references']
for section in required:
    assert section in report, f'Missing section: {section}'

# Check metadata required fields
meta_required = ['title', 'doc_id', 'revision', 'date', 'author', 'status']
for field in meta_required:
    assert field in report['metadata'], f'Missing metadata field: {field}'
assert report['metadata']['status'] in ('draft', 'reviewed', 'approved')

# Check inputs have required fields
for inp in report['inputs']:
    for field in ('name', 'symbol', 'value', 'unit'):
        assert field in inp, f'Input missing field: {field}'

# Check methodology has standard reference
assert 'standard' in report['methodology'], 'Missing standard reference'
assert 'equations' in report['methodology'], 'Missing equations'

print('Schema validation: PASS')
"
```

- [ ] **Step 7: Generate HTML report**

First verify the CLI interface:
```bash
uv run --no-project python scripts/reporting/generate-calc-report.py --help
```
Then generate (the script accepts `<input.yaml> [--format html|md] [--output <path>]`):
```bash
uv run --no-project python scripts/reporting/generate-calc-report.py examples/reporting/<calc-name>.yaml
```
Expected: HTML report generated

- [ ] **Step 8: Commit**

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
git add src/digitalmodel/<discipline>/<module>.py tests/test_<module>_<calc>.py
git commit -m "feat(WRK-1179): implement <calc> per <STANDARD>" && git push
cd /mnt/local-analysis/workspace-hub
git add examples/reporting/<calc-name>.yaml
git commit -m "docs(WRK-1179): calculation report for <calc>" && git push
```

**Repeat Steps 1–8 for each calculation.** Priority order by discipline:

**Structural (digitalmodel):**
1. S-N curve library expansion (BS 7608, additional DNV-RP-C203 curves)
2. Spectral fatigue completion
3. Member capacity checks (ISO 19902)
4. Plate buckling (DNV-RP-C201)

**Subsea (digitalmodel):**
5. On-bottom stability (DNV-RP-F109)
6. Pipeline collapse check enhancement
7. Buckle propagation (DNV-ST-F101 Sec 5.4.5)

**Cathodic Protection (digitalmodel):**
8. Anode design (DNV-RP-B401) — if not already complete
9. Coating breakdown factor calculations

**Well/Drilling (digitalmodel):**
10. Casing/tubing triaxial stress (WRK-376)
11. Wellbore hydraulics (WRK-378)
12. Torque and drag model

**Geotechnical (digitalmodel):**
13. Pile axial capacity (API RP 2GEO)
14. On-bottom stability (DNV-RP-F109)
15. Scour assessment

---

### Task 7: Enhance assethold Calculations

**Note:** assethold already has VaR, CVaR, Sharpe, Sortino, max drawdown, options pricing
(Black-Scholes + Greeks), and portfolio optimization (Markowitz, CAPM) in
`assethold/src/assethold/risk_metrics.py`, `analysis/`, and `options/`.

Focus on **gaps and enhancements**, not re-implementation:

**Files:**
- Read: `assethold/src/assethold/risk_metrics.py`
- Read: `assethold/src/assethold/analysis/`
- Read: `assethold/src/assethold/fundamentals.py`
- Modify/Create: files in `assethold/src/assethold/` as needed

- [ ] **Step 1: Audit existing risk_metrics.py and analysis/**

```bash
cd /mnt/local-analysis/workspace-hub/assethold
PYTHONPATH=src uv run python -c "
from assethold import risk_metrics
print([f for f in dir(risk_metrics) if not f.startswith('_')])
"
```
Document which calculations exist and which are missing.

- [ ] **Step 2: Identify gaps — likely candidates**

- GICS sector auto-classification (if not implemented)
- Portfolio beta vs. energy benchmark (XLE, XOP)
- Covered call premium calculator (WRK-325)
- Dividend yield forecasting

For each gap, follow the TDD + calc-report pattern (Steps 1–8 from Task 6):
- Test: `assethold/tests/test_<calc>.py`
- Implementation: `assethold/src/assethold/<module>.py`
- Calc report: `examples/reporting/<calc-name>.yaml`

```bash
cd /mnt/local-analysis/workspace-hub/assethold
uv run python -m pytest tests/ --noconftest -v
```

- [ ] **Step 3: Commit each calculation**

```bash
cd /mnt/local-analysis/workspace-hub/assethold
git add src/assethold/<module>.py tests/test_<calc>.py
git commit -m "feat(WRK-1179): implement <calc> in assethold" && git push
```

---

### Task 8: Implement worldenergydata Calculations

**Files:**
- Read: `worldenergydata/src/worldenergydata/production/`
- Read: `worldenergydata/src/worldenergydata/economics/`
- Read: `worldenergydata/src/worldenergydata/cost/`
- Create/Modify: calculation modules as needed

For each calculation, follow the full TDD + calc-report pattern (Steps 1–8 from Task 6).

**Priority 1: Arps decline curves (WRK-318)**

- [ ] **Step 1: Write failing test**

```python
# worldenergydata/tests/test_arps_decline.py
def test_exponential_decline():
    from worldenergydata.production.decline_curves import exponential_decline
    # qi=1000 bopd, Di=0.1/year, t=5 years
    result = exponential_decline(qi=1000, di=0.1, t=5)
    assert abs(result.rate - 606.5) < 1.0  # q = qi * exp(-Di*t)

def test_hyperbolic_decline():
    from worldenergydata.production.decline_curves import hyperbolic_decline
    result = hyperbolic_decline(qi=1000, di=0.1, b=0.5, t=5)
    assert result.rate > 0
    assert result.cumulative > 0
```

- [ ] **Step 2: Run test — expected FAIL**

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
PYTHONPATH="src:../assetutilities/src" uv run python -m pytest tests/test_arps_decline.py -v --noconftest
```

- [ ] **Step 3: Implement**

Create `worldenergydata/src/worldenergydata/production/decline_curves.py`

- [ ] **Step 4: Run test — expected PASS, then commit**

```bash
PYTHONPATH="src:../assetutilities/src" uv run python -m pytest tests/test_arps_decline.py -v --noconfest
git add src/worldenergydata/production/decline_curves.py tests/test_arps_decline.py
git commit -m "feat(WRK-1179): Arps decline curves — exponential, hyperbolic, harmonic" && git push
```

**Priority 2: NPV/MIRR with carbon cost sensitivity (WRK-321)**

- [ ] **Step 5: Write failing test**

```python
# worldenergydata/tests/test_field_economics.py
def test_npv_with_carbon_cost():
    from worldenergydata.economics.field_npv import calculate_npv
    result = calculate_npv(
        capex=500e6, opex_annual=30e6, production_bopd=10000,
        oil_price=70, discount_rate=0.10, years=20,
        carbon_cost_per_tonne=50
    )
    assert result.npv > 0 or result.npv <= 0  # calculation runs
    assert hasattr(result, 'npv_no_carbon')
    assert result.npv < result.npv_no_carbon  # carbon cost reduces NPV
```

- [ ] **Step 6: Implement, test, commit**

Create `worldenergydata/src/worldenergydata/economics/field_npv.py`

```bash
git add src/worldenergydata/economics/field_npv.py tests/test_field_economics.py
git commit -m "feat(WRK-1179): field NPV with carbon cost sensitivity" && git push
```

**Priority 3–4:** Drilling cost benchmarking, resource estimation (P10/P50/P90) — same pattern.

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
PYTHONPATH="src:../assetutilities/src" uv run python -m pytest --noconftest -v
```

---

### Task 9: Implement assetutilities Shared Constants

- [ ] **Step 1: Write failing test for constants**

```python
# assetutilities/tests/test_constants.py
def test_steel_grades_api_5l():
    from assetutilities.constants import STEEL_GRADES
    assert "X65" in STEEL_GRADES
    assert STEEL_GRADES["X65"]["smys_mpa"] == 448

def test_seawater_properties():
    from assetutilities.constants import SEAWATER
    assert SEAWATER["density_kg_m3"] == 1025
    assert SEAWATER["kinematic_viscosity_m2_s"] > 0
```

- [ ] **Step 2–5: Implement, test, commit**

```bash
cd /mnt/local-analysis/workspace-hub/assetutilities
uv run python -m pytest tests/test_constants.py --noconftest -v
```

---

## Chunk 3: Capture & Vision (Days 13–15)

### Task 10: Create WRK Items for Remaining Gaps

**Files:**
- Read: `specs/capability-map/audit/consolidated-gap-priority.md`
- Create: `.claude/work-queue/pending/WRK-*.md` (multiple)

- [ ] **Step 1: List all unimplemented gaps from audit**

From the consolidated gap map, extract every calculation that was NOT implemented in Days 4–12.

- [ ] **Step 2: Create WRK items**

For each remaining gap:
```yaml
---
id: WRK-<ID>
title: "Implement <STANDARD> <calculation> in <repo>/<module>"
status: pending
priority: <from audit>
complexity: <from audit>
created_at: "2026-03-2X"
target_repos:
  - <repo>
category: engineering
subcategory: calculation
parent: WRK-1179
---

## Mission
Implement <calculation> per <STANDARD> Section <X.Y> in <repo>/<module>.

## Design Data
- Standard: <STANDARD full title>
- Section: <specific clause>
- Doc path: <path in index>
- SHA: <content hash from capability map>

## Acceptance Criteria
1. Function with typed inputs/outputs in `<repo>/src/<module>.py`
2. Test with worked example from standard
3. Calculation report YAML in `examples/reporting/`
4. Validated against `config/reporting/calculation-report-schema.yaml`
```

- [ ] **Step 3: Update capability map status**

For each calculation implemented, update status from `gap` to `done` in:
- `specs/capability-map/digitalmodel.yaml`
- `specs/capability-map/worldenergydata.yaml`
- `specs/capability-map/assetutilities.yaml`

**Note:** No `specs/capability-map/assethold.yaml` exists. If assethold calculations were
added, create one following the same YAML structure as the other capability maps, or skip
if no standards-based calculations were added (assethold calcs are finance-theory-based,
not standards-based).

- [ ] **Step 4: Commit all WRK items and updates**

Stage WRK files individually to avoid picking up unrelated pending items:
```bash
git add specs/capability-map/
# Stage only WRK items created during this sprint (parent: WRK-1179)
grep -rl "parent: WRK-1179" .claude/work-queue/pending/ | xargs git add
git commit -m "feat(WRK-1179): WRK items for calculation gaps + capability map updates" && git push
```

---

### Task 11: Write Calculations Vision Document

**Files:**
- Create: `digitalmodel/docs/vision/CALCULATIONS-VISION.md`

- [ ] **Step 1: Write the vision document**

Structure:
```markdown
# Calculations Vision — ACE Engineering Ecosystem

## Current State
- digitalmodel: N modules, X calculation functions, Y% standards coverage
- assethold: N financial calculations implemented
- worldenergydata: N data analysis calculations
- assetutilities: N shared utilities

## Coverage by Discipline
| Discipline | Module | Standards Mapped | Implemented | Gap | Coverage % |
|-----------|--------|:---:|:---:|:---:|:---:|
| Structural / Fatigue | structural/fatigue | 117 | X | Y | Z% |
| ... | ... | ... | ... | ... | ... |

## Tier Progression
How each discipline advances from Tier 1 → Tier 2:
- Tier 1 (Calculator): function exists, tested, standard referenced
- Tier 2 (Assistant): agent API, natural language routing, report generation
- Current tier per discipline and what's needed to advance

## Priority Framework
Which calculations unlock which workflow patterns:
- Pattern 1 (Subsea Fatigue): requires spectral fatigue, wave spectra, SCF
- Pattern 2 (Pipeline Feasibility): requires wall thickness, collapse, stability
- Pattern 3 (Field Screening): requires decline curves, NPV, metocean
- Pattern 4 (Portfolio Risk): requires VaR, CVaR, Sharpe, sector classification

## Gap Register
- Total gaps remaining: N
- By discipline (link to WRK items)
- By priority (high/medium/low)
- Estimated effort to close all gaps

## Calculation Report Standard
All calculations follow the calculation-report skill:
- YAML schema: config/reporting/calculation-report-schema.yaml
- Generator: scripts/reporting/generate-calc-report.py
- Examples: examples/reporting/
```

- [ ] **Step 2: Commit vision document**

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
git add docs/vision/CALCULATIONS-VISION.md
git commit -m "docs(WRK-1179): calculations vision document" && git push
```

- [ ] **Step 3: Update hub submodule pointers**

```bash
cd /mnt/local-analysis/workspace-hub
git add digitalmodel assethold assetutilities worldenergydata
git commit -m "chore(WRK-1179): update all submodule pointers" && git push
```

---

### Task 12: Final Day 15 Review

- [ ] **Step 1: Count implementations completed**

```bash
# Count new test files added during sprint
cd /mnt/local-analysis/workspace-hub/digitalmodel
git log --oneline --since="2026-03-14" --name-only | grep "^tests/" | sort -u | wc -l
```

- [ ] **Step 2: Compare before/after capability map**

```bash
uv run --no-project python -c "
import yaml
with open('specs/capability-map/digitalmodel.yaml') as f:
    data = yaml.safe_load(f)
total_gap = 0
total_done = 0
for m in data['modules']:
    standards = m.get('standards', [])
    gap = sum(1 for s in standards if s.get('status') == 'gap')
    done = sum(1 for s in standards if s.get('status') == 'done')
    total_gap += gap
    total_done += done
print(f'Done: {total_done}  Gap: {total_gap}  Coverage: {total_done*100//(total_done+total_gap)}%')
"
```

- [ ] **Step 3: Present results to user**

Summary: calculations implemented, WRK items created, coverage % change, link to CALCULATIONS-VISION.md
