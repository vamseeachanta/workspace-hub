# Execution Pack: Subsea Architecture Patterns (#2058)

| Field | Value |
|---|---|
| Issue | [#2058](https://github.com/vamseeachanta/workspace-hub/issues/2058) |
| Title | feat(field-dev): subsea architecture patterns — flowline trends and layout classification |
| Labels | `enhancement`, `cat:engineering`, `agent:claude` |
| State | OPEN — **no `status:plan-approved`** |
| Depends On | #1861 (scaffold — merged, commit `aaf90c8e`) |
| Stage-1 Dossier | `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-5-architecture-patterns.md` |
| Generated | 2026-04-09 (stage-2) |

---

## 1. Fresh Status Check Since Stage-1 Dossier

### 1.1 What Changed Since Dossier Was Written

The stage-1 dossier assumed `benchmarks.py` at ~241 lines. Two commits landed after the dossier snapshot:

| Commit | Issue | Effect |
|---|---|---|
| `77b47195` | #2053 | Added `concept_probability_matrix()` (line 231), `predict_concept_type()` (line 282), `validate_against_cases()` (line 433), `ConceptPrediction` dataclass (line 79) |
| `526e2352` | #1861 | Hardened `load_projects()` against junk values |

**Current line counts (verified 2026-04-09):**

| File | Dossier Claim | Actual | Delta |
|---|---|---|---|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | 241 | **572** | +331 from #2053 |
| `digitalmodel/tests/field_development/test_benchmarks.py` | 417 | **763** | +346 from #2053 |
| `worldenergydata/subseaiq/analytics/normalize.py` | 130 | **129** | unchanged |

### 1.2 #2058 Implementation Delta — Still Valid

All 6 features from the dossier remain unimplemented (verified via grep):

- **3 new `SubseaProject` fields:** `flowline_diameter_in`, `flowline_material`, `layout_type` — **not present** (dataclass ends at `region` on line 75)
- **4 new public functions:** `layout_distribution`, `tieback_stats_segmented`, `equipment_stats_by_concept`, `flowline_trends_by_depth` — **none exist**
- **3 new normalize aliases:** — **not in `_FIELD_ALIASES`** (dict has 10 entries, lines 31–54)

### 1.3 Current Function Inventory in benchmarks.py

| Function | Line | Added By |
|---|---|---|
| `load_projects()` | 104 | #1861 |
| `concept_benchmark_bands()` | 149 | #1861 |
| `subsea_architecture_stats()` | 184 | #1861 |
| `concept_probability_matrix()` | 231 | #2053 (NEW since dossier) |
| `predict_concept_type()` | 282 | #2053 (NEW since dossier) |
| `validate_against_cases()` | 433 | #2053 (NEW since dossier) |
| `_classify_depth()` | 535 | #1861 |
| `_describe()` | 543 | #1861 |
| `_opt_float()` | 555 | #1861 |
| `_opt_int()` | 565 | #1861 |

### 1.4 Test Class Inventory in test_benchmarks.py

| Test Class | Line | Tests |
|---|---|---|
| `TestLoadProjects` | 142 | 8 |
| `TestConceptBenchmarkBands` | 186 | 8 |
| `TestSubseaArchitectureStats` | 258 | 6 |
| `TestJunkValues` | 317 | 3 |
| `TestNormalizeIntegration` | 359 | 1 |
| `TestConceptProbabilityMatrix` | 471 | NEW since dossier |
| `TestPredictConceptType` | 546 | NEW since dossier |
| `TestCaseStudyValidation` | 707 | NEW since dossier |

### 1.5 Contention Check

| Issue | Status | Conflict Risk |
|---|---|---|
| #2055 (subsea cost benchmarking) | `wip:ace-linux-1` — **actively in flight** | **MEDIUM** — may touch `benchmarks.py` concurrently |
| #2053 (concept probability matrix) | Implemented | CLEAR — already merged |
| #2060 (project timeline benchmarks) | OPEN, no WIP label | LOW — different SubseaIQ dimensions |

---

## 2. Minimal Plan-Review Packet

### 2.1 Scope Summary

Add flowline-level architecture analytics to the SubseaIQ benchmark bridge. All changes are additive — no existing behavior modified. Three files touched:

1. **`digitalmodel/src/digitalmodel/field_development/benchmarks.py`** — 3 new dataclass fields + 4 new public functions + update `load_projects()` field mapping
2. **`digitalmodel/tests/field_development/test_benchmarks.py`** — ~15-20 new test methods across 6 new test classes, extended fixtures
3. **`worldenergydata/subseaiq/analytics/normalize.py`** — 3 new alias groups + coercion for `flowline_diameter_in`

### 2.2 Acceptance Criteria

- [ ] `SubseaProject` has `flowline_diameter_in`, `flowline_material`, `layout_type` fields
- [ ] `normalize.py` maps raw SubseaIQ variants for all 3 new fields
- [ ] `layout_distribution()` returns `{concept_type: {layout_type: count}}`
- [ ] `tieback_stats_segmented()` returns `{depth_band: {fluid_type: {count, min, max, mean}}}`
- [ ] `equipment_stats_by_concept()` returns `{concept_type: {metric: {count, min, max, mean}}}`
- [ ] `flowline_trends_by_depth()` returns `{depth_band: {diameter stats, material counts}}`
- [ ] All existing tests still pass (zero regressions)
- [ ] All new tests pass
- [ ] No file exceeds 500 lines (see §3.1 — requires splitting)

### 2.3 Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| `benchmarks.py` already at 572 lines (exceeds 500-line limit) | **HIGH** | Split new functions into `architecture_patterns.py` (see §3.1) |
| #2055 WIP may create merge conflicts in `benchmarks.py` | MEDIUM | Coordinate: #2058 touches `SubseaProject` dataclass + new functions only; #2055 should use separate functions |
| SubseaIQ raw data may lack flowline/material fields | MEDIUM | New fields default to `None`; analytics functions gracefully skip missing data |
| Layout type values not standardized in SubseaIQ | LOW | Normalize in alias mapping; canonical values: `daisy_chain`, `star`, `direct_tieback`, `hub_spoke` |

---

## 3. Issue Refinement Recommendations

### 3.1 CRITICAL: File Split Required

`benchmarks.py` is already at 572 lines — exceeding the worldenergydata CLAUDE.md 500-line constraint. Adding 4 new functions (~80-120 lines) would push to ~650-700 lines. **Recommend updating #2058 body** to specify:

> New functions (`layout_distribution`, `tieback_stats_segmented`, `equipment_stats_by_concept`, `flowline_trends_by_depth`) go in a **new module** `digitalmodel/src/digitalmodel/field_development/architecture_patterns.py` that imports `SubseaProject` and helpers from `benchmarks.py`. The 3 new dataclass fields and `load_projects()` update remain in `benchmarks.py`.

This adds a 4th file to the change set:
- `digitalmodel/src/digitalmodel/field_development/architecture_patterns.py` (NEW — ~120 lines)
- Corresponding test file: `digitalmodel/tests/field_development/test_architecture_patterns.py` (NEW — ~200 lines)

### 3.2 Suggested Label Addition

Add `priority:medium` — this unblocks richer field development analytics but has no urgent downstream consumers.

### 3.3 Suggested Body Patch

Add to the issue body:

```markdown
## Implementation Notes (from stage-2 review)
- benchmarks.py already at 572 lines (500-line limit); new functions go in `architecture_patterns.py`
- #2053 added concept_probability_matrix/predict_concept_type since original scope — no conflict
- Coordinate with #2055 (subsea cost benchmarking, wip:ace-linux-1) on SubseaProject field additions
```

---

## 4. Operator Command Pack

### 4.1 Label and Triage

```bash
# Add plan-review label to trigger review workflow
gh issue edit 2058 --add-label "status:plan-review"

# Add priority (optional, recommended)
gh issue edit 2058 --add-label "priority:medium"
```

### 4.2 Post Plan-Review Comment

```bash
gh issue comment 2058 --body "$(cat <<'EOF'
## Stage-2 Plan Review — Ready for Approval

**Dossier:** `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-5-architecture-patterns.md`
**Execution Pack:** `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-5-architecture-patterns-execution-pack.md`

### Key Findings
- All 6 features from dossier remain unimplemented (verified 2026-04-09)
- `benchmarks.py` grew to 572 lines via #2053 — **exceeds 500-line limit**
- Recommend splitting new functions into `architecture_patterns.py`
- #2055 (subsea cost) is `wip:ace-linux-1` — coordinate on `SubseaProject` field additions

### Files to Change
1. `digitalmodel/src/digitalmodel/field_development/benchmarks.py` — 3 new dataclass fields + `load_projects()` update
2. `digitalmodel/src/digitalmodel/field_development/architecture_patterns.py` — NEW: 4 analytical functions
3. `digitalmodel/tests/field_development/test_architecture_patterns.py` — NEW: ~15-20 tests
4. `worldenergydata/subseaiq/analytics/normalize.py` — 3 new alias groups

### Action Required
Add `status:plan-approved` to proceed with implementation.
EOF
)"
```

### 4.3 Approve for Implementation (when ready)

```bash
# Only after human review of the plan
gh issue edit 2058 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

---

## 5. Self-Contained Implementation Prompt for Claude

```
You are implementing GitHub issue #2058: feat(field-dev): subsea architecture patterns — flowline trends and layout classification.

## Context

The SubseaIQ benchmark bridge has grown since the original dossier:
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py` (572 lines) — `SubseaProject` (10 fields), `load_projects()`, `concept_benchmark_bands()`, `subsea_architecture_stats()`, `concept_probability_matrix()`, `predict_concept_type()`, `validate_against_cases()`, plus helpers `_classify_depth()`, `_describe()`, `_opt_float()`, `_opt_int()`.
- `digitalmodel/tests/field_development/test_benchmarks.py` (763 lines) — 8 test classes, 25+ tests, `FIXTURE_RECORDS` (8 projects) + `SPARSE_RECORDS` (4 projects).
- `worldenergydata/subseaiq/analytics/normalize.py` (129 lines) — 10 canonical field aliases.

**IMPORTANT:** benchmarks.py is at 572 lines (exceeds 500-line limit). All 4 new analytical functions MUST go in a NEW module `architecture_patterns.py`. Only the 3 new dataclass fields and `load_projects()` update stay in benchmarks.py.

## What To Build (TDD — tests first)

### Step 1: Extend test fixtures
In `digitalmodel/tests/field_development/test_benchmarks.py`, add `flowline_diameter_in`, `flowline_material`, and `layout_type` to 4+ of the 8 `FIXTURE_RECORDS` entries (starts at line 20). Example values:
- Bravo: flowline_diameter_in=8.0, flowline_material="Carbon Steel", layout_type="direct_tieback"
- Delta: flowline_diameter_in=10.75, flowline_material="Duplex", layout_type="daisy_chain"
- Foxtrot: flowline_diameter_in=12.0, flowline_material="Flexible", layout_type="star"
- Golf: flowline_diameter_in=6.0, flowline_material="Carbon Steel", layout_type="direct_tieback"

### Step 2: Write failing tests for benchmarks.py changes
Add to `test_benchmarks.py`:
- `TestSubseaProjectNewFields` — 4 tests: load each new field, defaults to None for sparse records

### Step 3: Write failing tests for new module
Create `digitalmodel/tests/field_development/test_architecture_patterns.py`:
- `TestLayoutDistribution` — 4 tests: dict keyed by concept, counts per concept, skips None, empty
- `TestTiebackStatsSegmented` — 5 tests: nested dict, by depth band, by fluid type, skips missing, empty
- `TestEquipmentStatsByConcept` — 4 tests: by concept, trees/manifold per concept, skips zero, empty
- `TestFlowlineTrendsByDepth` — 4 tests: diameter stats per band, material distribution, skips None, empty

### Step 4: Write failing tests for normalize
Add to an appropriate normalize test file or create one:
- `TestNormalizeNewFields` — 3 tests: `flowline_diameter_in` float coercion, `flowline_material` passthrough, `layout_type` passthrough

### Step 5: Implement normalize changes
`worldenergydata/subseaiq/analytics/normalize.py` — add 3 alias groups to `_FIELD_ALIASES` (after line 54):
```python
"flowline_diameter_in": [
    "flowline_diameter_in", "Flowline Diameter (in)", "flowline_diameter",
    "pipe_diameter_in", "Pipe Diameter", "flowline_od_in",
],
"flowline_material": [
    "flowline_material", "Flowline Material", "pipe_material",
    "Pipeline Material", "material", "Material",
],
"layout_type": [
    "layout_type", "Layout Type", "layout", "Layout",
    "subsea_layout", "Subsea Layout", "architecture_type",
],
```
Add float coercion for `flowline_diameter_in` in `normalize_project()`.

### Step 6: Implement benchmarks.py changes
`digitalmodel/src/digitalmodel/field_development/benchmarks.py`:
- Add 3 fields to `SubseaProject` dataclass after `region` (line 75):
  ```python
  flowline_diameter_in: Optional[float] = None
  flowline_material: Optional[str] = None
  layout_type: Optional[str] = None
  ```
- Update `load_projects()` (around line 128-141) to map the 3 new fields from input dict

### Step 7: Implement new module
Create `digitalmodel/src/digitalmodel/field_development/architecture_patterns.py`:
```python
"""Subsea architecture pattern analytics (#2058).

Split from benchmarks.py to respect the 500-line file limit.
Imports SubseaProject and helpers from the benchmark bridge.
"""
from digitalmodel.field_development.benchmarks import (
    SubseaProject, _classify_depth, _describe, DEPTH_BANDS,
)
```
Implement these 4 functions:
1. `layout_distribution(projects) -> dict[str, dict[str, int]]` — {concept_type: {layout_type: count}}, skip None layout
2. `tieback_stats_segmented(projects) -> dict[str, dict[str, dict[str, float]]]` — {depth_band: {fluid_type: {count, min, max, mean}}}
3. `equipment_stats_by_concept(projects) -> dict[str, dict[str, dict[str, float]]]` — {concept_type: {"trees_per_manifold": stats, "manifolds_per_host": stats}}
4. `flowline_trends_by_depth(projects) -> dict[str, dict[str, Any]]` — {depth_band: {"diameter": stats, "materials": {material: count}}}

### Step 8: Verify
```bash
uv run pytest digitalmodel/tests/field_development/test_benchmarks.py -v
uv run pytest digitalmodel/tests/field_development/test_architecture_patterns.py -v
uv run pytest digitalmodel/tests/field_development/ -v --tb=short
```

### Step 9: Final checks
```bash
# Verify all new fields exist
uv run python -c "
from digitalmodel.field_development.benchmarks import SubseaProject
import dataclasses
fields = {f.name for f in dataclasses.fields(SubseaProject)}
required = {'flowline_diameter_in', 'flowline_material', 'layout_type'}
missing = required - fields
print(f'Missing fields: {missing}' if missing else 'All new fields present')
"

# Verify new functions importable
uv run python -c "
from digitalmodel.field_development.architecture_patterns import (
    layout_distribution, tieback_stats_segmented,
    equipment_stats_by_concept, flowline_trends_by_depth,
)
print('All new functions importable')
"

# Verify no file exceeds 500 lines
wc -l digitalmodel/src/digitalmodel/field_development/benchmarks.py digitalmodel/src/digitalmodel/field_development/architecture_patterns.py worldenergydata/subseaiq/analytics/normalize.py
```

## Acceptance Criteria
- [ ] `SubseaProject` has `flowline_diameter_in`, `flowline_material`, `layout_type` fields
- [ ] `normalize.py` maps raw SubseaIQ variants for all 3 new fields
- [ ] `layout_distribution()` returns concept_type -> layout_type -> count
- [ ] `tieback_stats_segmented()` returns depth_band -> fluid_type -> {count, min, max, mean}
- [ ] `equipment_stats_by_concept()` returns concept_type -> metric -> {count, min, max, mean}
- [ ] `flowline_trends_by_depth()` returns depth_band -> {diameter stats, material counts}
- [ ] New module `architecture_patterns.py` stays under 500 lines
- [ ] `benchmarks.py` does NOT grow beyond current ~580 lines (only 3 field additions + load_projects update)
- [ ] All existing tests pass (zero regressions)
- [ ] All new tests pass

## Cross-Review Requirements
- Post `gh issue comment 2058 --body "..."` with implementation summary
- Run `uv run pytest digitalmodel/tests/field_development/ -v` and include output
- Verify normalize integration test still passes end-to-end
```

---

## 6. Morning Handoff

### For the Operator (Human Review)

1. **Read this pack** — the stage-1 dossier was accurate on implementation delta but stale on line counts.
2. **Key decision required:** Approve the file-split strategy (new `architecture_patterns.py` module) — or grant a 500-line exception for `benchmarks.py`.
3. **Check #2055 status** — if subsea cost benchmarking is still in progress on ace-linux-1, coordinate `SubseaProject` field additions to avoid merge conflicts.
4. **Run the `gh` commands in §4** to label and comment.
5. **When ready,** add `status:plan-approved` to unblock implementation.

### For the Implementation Agent

- The self-contained prompt in §5 has everything needed — no external context required.
- The TDD sequence in §5 follows the established pattern from #1861/#2053.
- The `architecture_patterns.py` split is the only structural deviation from the stage-1 dossier — it's forced by the 500-line constraint that wasn't visible when `benchmarks.py` was at 241 lines.

### Key File Paths

| File | Current Lines | Role |
|---|---|---|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | 572 | Dataclass + field mapping (modify) |
| `digitalmodel/src/digitalmodel/field_development/architecture_patterns.py` | — | New analytical functions (create) |
| `digitalmodel/tests/field_development/test_benchmarks.py` | 763 | Existing tests + new field tests (modify) |
| `digitalmodel/tests/field_development/test_architecture_patterns.py` | — | New function tests (create) |
| `worldenergydata/subseaiq/analytics/normalize.py` | 129 | Alias mapping (modify) |

---

## 7. Final Recommendation

**READY FOR PLAN-REVIEW → PLAN-APPROVED GATE.** All #1861 prerequisites are met. The only architectural update from stage-1 is a mandatory file split (`architecture_patterns.py`) forced by benchmarks.py exceeding the 500-line limit after #2053 landed. No blockers remain once the operator adds `status:plan-approved`.
