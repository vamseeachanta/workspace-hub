# Stage-2 Execution Pack — #2055 Subsea Cost Benchmarking

| Field | Value |
|---|---|
| **Issue** | [#2055](https://github.com/vamseeachanta/workspace-hub/issues/2055) |
| **Title** | feat(field-dev): subsea cost benchmarking from SubseaIQ equipment counts |
| **Labels** | enhancement, priority:high, cat:engineering, dark-intelligence, agent:claude, wip:ace-linux-1 |
| **Depends On** | #1861 (scaffold — DONE), SubseaIQ equipment count data (NOT MET) |
| **Status** | OPEN — no `status:plan-approved` label, planning-only |
| **Stage-1 Dossier** | `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md` |
| **Pack Date** | 2026-04-09 |

---

## 1. Fresh Status Check Since Stage-1

The stage-1 dossier was produced on 2026-04-09. The following deltas were verified against the live repo on the same date.

### 1.1 What Changed (Stale in Stage-1)

| Item | Dossier Said | Repo Reality Now | Impact |
|---|---|---|---|
| `benchmarks.py` line count | 241 lines | **572 lines** — #2053 added `concept_probability_matrix`, `predict_concept_type`, `validate_against_cases` | Cost functions will extend a richer module; insertion point shifts to after line ~570 |
| `test_benchmarks.py` line count | 417 lines, 4 test classes | **763 lines, 7 test classes** — added `TestConceptProbabilityMatrix`, `TestPredictConceptType`, `TestCaseStudyValidation` | New cost test classes append after line ~763 |
| `__init__.py` exports | "Does NOT export benchmarks" | **NOW exports**: `SubseaProject`, `ConceptPrediction`, `concept_probability_matrix`, `predict_concept_type`, `validate_against_cases`, `concept_benchmark_bands`, `load_projects`, `DEPTH_BANDS` | **Eliminates dossier task #9** — no longer need to add benchmarks to `__init__.py` |

### 1.2 What Remains Accurate

| Item | Status | Confirmed |
|---|---|---|
| `subseaiq-scan-latest.json` has 0 equipment count fields | **STILL TRUE** — 10 GoM fields with only: name, operator, water_depth_m, host, year, capacity_bopd | Data gap is the primary blocker |
| `CostDataPoint` schema has 0 equipment count fields | **STILL TRUE** — checked `calibration_schema.py`, no num_trees/num_manifolds/tieback fields | Schema extension or band-level aggregation still required |
| `SubseaProject` has no `cost_usd_mm` field | **STILL TRUE** — dataclass at `benchmarks.py:59-75` ends with `region: Optional[str]` | Must add optional cost field |
| `worldenergydata/subseaiq/analytics/cost_correlation.py` does not exist | **STILL TRUE** — directory contains only `__init__.py`, `normalize.py` | New file creation still in scope |
| 71 sanctioned cost records in `public_dataset.py` | **STILL TRUE** — 71 occurrences of `cost_usd_mm` confirmed | Cost data source intact |
| No `status:plan-approved` label | **STILL TRUE** — labels: enhancement, priority:high, cat:engineering, wip:ace-linux-1, dark-intelligence, agent:claude | Cannot implement without user approval |

---

## 2. Minimal Plan-Review Packet

### 2.1 Scope Summary

Add cost correlation layer to `digitalmodel.field_development.benchmarks` that joins SubseaIQ equipment counts with sanctioned project cost data to produce unit cost curves (cost/tree, cost/km-flowline, cost/manifold) and cost benchmark bands by water depth and concept type.

### 2.2 Architecture Decision: Band-Level vs Per-Project Correlation

The stage-1 dossier recommended **Option 3 (band-level aggregation)** as the primary approach. This recommendation stands, with updated rationale:

| Approach | Feasibility | Data Required | Status |
|---|---|---|---|
| **Option 3 — Band-level aggregation** | HIGH — aggregate equipment stats by depth band, aggregate costs by depth band, derive unit cost ratios at band granularity | Existing `SubseaProject` equipment fields + existing 71 `CostDataPoint` records | **Feasible now** if equipment counts backfilled for GoM fields |
| **Option 1 — Schema extension** | MEDIUM — extend `CostDataPoint` with equipment fields, backfill 71 records | Per-project equipment counts for all 71 sanctioned projects | **Not feasible** — 71 projects need individual research |
| **Option 2 — Join table** | LOW — project-name fuzzy match between two schemas | Reliable name mapping across SubseaIQ and sanctioned datasets | **Fragile** — naming conventions differ |

**Recommendation**: Implement Option 3 first. Gate Option 1 behind a follow-up issue.

### 2.3 Files In Scope

| File | Action | Notes |
|---|---|---|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | EXTEND | Add `cost_usd_mm` to `SubseaProject`, add 5 cost functions after line ~570 |
| `digitalmodel/tests/field_development/test_benchmarks.py` | EXTEND | Add 4 cost test classes after line ~763 |
| `worldenergydata/subseaiq/analytics/cost_correlation.py` | CREATE | Cost correlation helpers: `correlate_equipment_costs()`, `aggregate_costs_by_depth_band()` |
| `worldenergydata/subseaiq/analytics/__init__.py` | EXTEND | Export cost correlation module |
| `data/field-development/subseaiq-scan-latest.json` | EXTEND | Backfill equipment count fields (num_trees, num_manifolds, tieback_distance_km) for 10 GoM fields |
| `digitalmodel/src/digitalmodel/field_development/__init__.py` | EXTEND | Add new cost function exports (cost_per_tree, cost_benchmark_bands, etc.) |

### 2.4 Functions to Implement

| Function | Signature | Returns |
|---|---|---|
| `cost_per_tree` | `(projects: list[SubseaProject]) -> dict[str, dict[str, float]]` | `{depth_band: {"mean": float, "min": float, "max": float}}` |
| `cost_per_km_flowline` | `(projects: list[SubseaProject]) -> dict[str, dict[str, float]]` | Same structure |
| `cost_per_manifold` | `(projects: list[SubseaProject]) -> dict[str, dict[str, float]]` | Same structure |
| `unit_cost_curves` | `(projects: list[SubseaProject]) -> dict[str, dict[str, dict[str, float]]]` | `{metric: {depth_band: stats}}` |
| `cost_benchmark_bands` | `(projects: list[SubseaProject]) -> dict[str, dict[str, dict[str, float]]]` | `{depth_band: {concept_type: {low, base, high}}}` |
| `cross_validate_costs` | `(projects, sanctioned: list[CostDataPoint]) -> list[dict]` | Per-project comparison with delta and outlier flag |

### 2.5 Blocker: Equipment Count Data

The issue body says "Depends on SubseaIQ scraping with equipment count fields." This dependency is **NOT MET**:

- `subseaiq-scan-latest.json` has 6 keys per record: `name`, `operator`, `water_depth_m`, `host`, `year`, `capacity_bopd`. Zero equipment counts.
- The `normalize.py` pipeline can handle equipment fields if present — but the upstream scraping has never populated them.
- **Minimum viable unblock**: Manually backfill equipment counts for the 10 GoM reference fields from public-domain data (SubseaIQ public pages, operator FIDs, trade press).

---

## 3. Issue Refinement Recommendations

Before applying `status:plan-approved`, the operator should resolve these open questions:

### 3.1 Required Decisions

| # | Decision | Options | Recommended |
|---|---|---|---|
| 1 | Equipment count data source | (a) Manual backfill for 10 GoM fields, (b) Wait for SubseaIQ scraping pipeline, (c) Use synthetic/estimated counts | **(a) Manual backfill** — fastest unblock, 10 fields is manageable |
| 2 | Correlation architecture | (a) Band-level only, (b) Per-project join, (c) Both | **(a) Band-level only** for MVP; per-project as follow-up |
| 3 | `CostDataPoint` schema extension | (a) Add equipment fields now, (b) Defer to follow-up | **(b) Defer** — avoids touching 71 hardcoded records in `public_dataset.py` |
| 4 | Where does `cost_correlation.py` live | (a) `worldenergydata/subseaiq/analytics/`, (b) `digitalmodel/src/digitalmodel/field_development/` | **(a)** — consistent with existing `normalize.py` pattern |

### 3.2 Suggested Issue Body Update

Add to the issue body:

```markdown
## Scoping Decisions (stage-2)
- [ ] Equipment data: manual backfill for 10 GoM fields (not waiting for scraping pipeline)
- [ ] Architecture: band-level aggregation first; per-project correlation deferred
- [ ] CostDataPoint schema: unchanged for this issue
- [ ] Cost correlation helpers: placed in worldenergydata/subseaiq/analytics/
```

### 3.3 Suggested New Labels

```
status:needs-refinement  → until decisions above are resolved
```

---

## 4. Operator Command Pack

All commands are draft-only. Execute after reviewing each one.

### 4.1 Issue Label Management

```bash
# Add refinement label (issue needs scoping decisions before plan-approved)
gh issue edit 2055 --add-label "status:needs-refinement"

# After resolving Section 3.1 decisions, upgrade to plan-review
gh issue edit 2055 --remove-label "status:needs-refinement" --add-label "status:plan-review"

# After user reviews plan, approve for implementation
gh issue edit 2055 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

### 4.2 Issue Body Update (Post Scoping Decisions)

```bash
# Add scoping decisions to the issue body
gh issue comment 2055 --body "$(cat <<'EOF'
## Stage-2 Scoping Decisions (2026-04-09)

### Resolved
1. **Equipment data source**: Manual backfill for 10 GoM fields in `subseaiq-scan-latest.json`
2. **Correlation architecture**: Band-level aggregation (MVP); per-project join deferred to follow-up issue
3. **CostDataPoint schema**: No changes — use depth-band-level join instead
4. **cost_correlation.py location**: `worldenergydata/subseaiq/analytics/cost_correlation.py`

### Updated Scope
- Add `cost_usd_mm` optional field to `SubseaProject`
- Implement 5 cost functions in `benchmarks.py` + 1 cross-validation function
- Create `cost_correlation.py` with band-level equipment-cost merge helpers
- Backfill equipment counts for 10 GoM fields in `subseaiq-scan-latest.json`
- TDD: 4 new test classes (~15 tests) in `test_benchmarks.py`

### Stage-2 Artifacts
- Execution pack: `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-8-subsea-cost-execution-pack.md`
- Stage-1 dossier: `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md`
EOF
)"
```

### 4.3 Verification Commands (Pre-Implementation Sanity)

```bash
# 1. Verify benchmarks.py current exports
cd digitalmodel && uv run python -c "from digitalmodel.field_development.benchmarks import SubseaProject, load_projects, DEPTH_BANDS; print(f'SubseaProject fields: {[f.name for f in SubseaProject.__dataclass_fields__.values()]}'); print(f'Depth bands: {DEPTH_BANDS}')"

# 2. Verify 71 cost records still load
cd worldenergydata && uv run python -c "from worldenergydata.cost import load_public_dataset; d=load_public_dataset(); print(f'{len(d)} cost records loaded')"

# 3. Verify existing benchmarks tests pass (baseline)
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -v --tb=short

# 4. Verify normalize.py handles equipment fields
cd worldenergydata && uv run python -c "from worldenergydata.subseaiq.analytics.normalize import normalize_project; p = normalize_project({'Project Name': 'Test', 'Number of Trees': '6', 'Number of Manifolds': '2'}); print(p)"

# 5. Verify subseaiq-scan-latest.json schema
python3 -c "import json; d=json.load(open('data/field-development/subseaiq-scan-latest.json')); print(f'Records: {len(d[\"gom_fields\"])}'); print(f'Keys: {list(d[\"gom_fields\"][0].keys())}')"
```

---

## 5. Self-Contained Future Implementation Prompt

```
You are implementing GitHub issue #2055: feat(field-dev): subsea cost benchmarking from SubseaIQ equipment counts.

## Context
- Workspace: /mnt/local-analysis/workspace-hub
- Issue depends on #1861 (scaffold — DONE, merged)
- Stage-1 dossier: docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md
- Stage-2 pack: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-8-subsea-cost-execution-pack.md

## Current State (verified 2026-04-09)
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py` (572 lines)
  - SubseaProject dataclass (line 59-75) — has equipment fields, NO cost_usd_mm
  - Functions: load_projects, concept_benchmark_bands, subsea_architecture_stats,
    concept_probability_matrix, predict_concept_type, validate_against_cases
  - NO cost functions exist
- `digitalmodel/tests/field_development/test_benchmarks.py` (763 lines, 7 test classes)
  - Tests cover #1861 scaffold + #2053 probability/prediction
  - NO cost-related tests
- `worldenergydata/src/worldenergydata/cost/data_collection/public_dataset.py` (1643 lines)
  - 71 sanctioned project cost records as CostDataPoint Pydantic objects
  - Has cost_usd_mm, region, water_depth_m, water_depth_band — NO equipment counts
- `worldenergydata/subseaiq/analytics/normalize.py` (130 lines)
  - Normalizes raw SubseaIQ keys; ready to consume equipment fields
- `worldenergydata/subseaiq/analytics/cost_correlation.py` — DOES NOT EXIST (create it)
- `data/field-development/subseaiq-scan-latest.json`
  - 10 GoM fields, keys: name, operator, water_depth_m, host, year, capacity_bopd
  - NO equipment counts — must backfill num_trees, num_manifolds, tieback_distance_km
- `digitalmodel/src/digitalmodel/field_development/__init__.py`
  - Already exports benchmarks module symbols — add new cost functions to exports

## Architecture Decision
Use band-level aggregation (Option 3 from stage-1 dossier):
- Aggregate equipment stats per depth band from SubseaIQ data
- Aggregate costs per depth band from 71 CostDataPoint records
- Derive unit cost ratios (cost/tree, cost/km, cost/manifold) at band granularity
- Do NOT modify CostDataPoint schema

## TDD Implementation Order

### Phase 1 — Failing Tests First
Add to `digitalmodel/tests/field_development/test_benchmarks.py` after line ~763:

```python
class TestSubseaProjectCostFields:
    def test_cost_field_present(self):
        """SubseaProject should accept optional cost_usd_mm."""
    def test_cost_field_defaults_to_none(self):
        """cost_usd_mm should default to None when not provided."""
    def test_load_projects_parses_cost(self):
        """load_projects should parse cost_usd_mm from raw dict."""

class TestUnitCostCurves:
    def test_cost_per_tree_by_depth_band(self):
        """cost_per_tree() returns dict[depth_band -> {mean, min, max}]."""
    def test_cost_per_tree_excludes_zero_trees(self):
        """Projects with 0 or None trees excluded from cost/tree calc."""
    def test_cost_per_km_flowline_by_depth_band(self):
        """cost_per_km_flowline() returns dict[depth_band -> {mean, min, max}]."""
    def test_cost_per_manifold_by_depth_band(self):
        """cost_per_manifold() returns dict[depth_band -> {mean, min, max}]."""
    def test_unit_cost_curves_structure(self):
        """unit_cost_curves() returns all 3 metrics keyed by depth band."""
    def test_sparse_data_handled(self):
        """Missing cost or equipment data → excluded, not crashed."""

class TestCostBenchmarkBands:
    def test_returns_bands_by_depth_and_concept(self):
        """cost_benchmark_bands_with_costs() returns nested dict[depth_band][concept] -> {low, base, high}."""
    def test_band_values_are_positive(self):
        """All cost band values should be > 0 where data exists."""
    def test_empty_bands_for_no_data(self):
        """Depth/concept combos with no data return empty or None."""

class TestCrossValidation:
    def test_cross_validate_returns_comparison(self):
        """cross_validate_costs() returns per-project comparison with delta."""
    def test_cross_validate_flags_outliers(self):
        """Projects where equipment-derived cost differs >50% from sanctioned flagged."""
```

### Phase 2 — Data Backfill
Extend `data/field-development/subseaiq-scan-latest.json` GoM fields with:
- `num_trees` (int) — Christmas tree count
- `num_manifolds` (int) — subsea manifold count
- `tieback_distance_km` (float) — tieback to host distance
Use public-domain data from SubseaIQ project pages and operator FIDs.

### Phase 3 — Implementation
1. Add `cost_usd_mm: Optional[float] = None` to SubseaProject (benchmarks.py:75)
2. Update load_projects() to parse cost_usd_mm (benchmarks.py:130-141)
3. Create `worldenergydata/subseaiq/analytics/cost_correlation.py`:
   - `correlate_equipment_costs(subseaiq_records, cost_records)` — band-level merge
   - `aggregate_costs_by_depth_band(merged)` — band-level cost stats
4. Implement cost functions in benchmarks.py (after line ~570):
   - cost_per_tree(projects) -> dict
   - cost_per_km_flowline(projects) -> dict
   - cost_per_manifold(projects) -> dict
   - unit_cost_curves(projects) -> dict
   - cost_benchmark_bands_with_costs(projects) -> dict
   - cross_validate_costs(projects, sanctioned) -> list
5. Update __init__.py exports with new cost functions
6. Update worldenergydata/subseaiq/analytics/__init__.py exports

### Phase 4 — Verification
```bash
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -v
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -v -k "Cost"
cd worldenergydata && uv run pytest -v -k "cost_correlation"
cd digitalmodel && uv run python -c "from digitalmodel.field_development.benchmarks import cost_per_tree; print('import OK')"
cd digitalmodel && uv run mypy src/digitalmodel/field_development/benchmarks.py --ignore-missing-imports
```

## Acceptance Criteria
- [ ] All existing 27+ tests in test_benchmarks.py still pass
- [ ] All new cost tests pass (~15 tests across 4 classes)
- [ ] cost_per_tree returns dict keyed by DEPTH_BANDS with {mean, min, max}
- [ ] cost_per_km_flowline returns dict keyed by DEPTH_BANDS with {mean, min, max}
- [ ] cost_per_manifold returns dict keyed by DEPTH_BANDS with {mean, min, max}
- [ ] cost_benchmark_bands_with_costs returns nested dict[depth][concept] → {low, base, high}
- [ ] cross_validate_costs compares equipment-derived vs sanctioned costs
- [ ] Unit costs in physically reasonable ranges: cost/tree $10-200M, cost/km $5-50M
- [ ] subseaiq-scan-latest.json has equipment count fields for all 10 GoM fields
- [ ] No hardcoded absolute paths

## Cross-Review Requirements
- Codex or Gemini cross-review before merge
- Verify cost curves produce physically reasonable values
- Verify existing tests pass unchanged
- Verify no regressions in concept_probability_matrix or predict_concept_type
```

---

## 6. Morning Handoff

### What Was Done
- Read and verified the stage-1 dossier against live repo state
- Found 3 stale items: `benchmarks.py` grew 331 lines (#2053), `test_benchmarks.py` grew 346 lines, and `__init__.py` now exports benchmarks (was flagged as missing)
- Confirmed the core data gap: equipment count fields are still entirely absent from both `subseaiq-scan-latest.json` and `CostDataPoint` schema
- Produced this stage-2 execution pack with updated scope, operator commands, and implementation prompt

### What Needs Human Decision
1. **Equipment data source**: The issue's stated dependency on "SubseaIQ scraping with equipment count fields" is NOT MET. The operator must decide whether to (a) manually backfill 10 GoM fields, (b) wait for scraping pipeline, or (c) use synthetic data.
2. **Naming conflict**: The existing `concept_benchmark_bands()` function name in `benchmarks.py` overlaps with the proposed `cost_benchmark_bands()`. Suggest naming the cost variant `cost_benchmark_bands_with_costs()` or choosing a distinct name.

### Next Steps (In Order)
1. Resolve scoping decisions in Section 3.1
2. Run `gh issue edit 2055 --add-label "status:needs-refinement"` (or `status:plan-review` if decisions are clear)
3. Post scoping decisions as issue comment using Section 4.2 command
4. After user approval, apply `status:plan-approved` and dispatch implementation using the prompt in Section 5

### Key File Paths
| File | Why It Matters |
|---|---|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | Primary implementation target — extend with 6 cost functions |
| `digitalmodel/tests/field_development/test_benchmarks.py` | TDD target — 4 new test classes, ~15 tests |
| `worldenergydata/subseaiq/analytics/cost_correlation.py` | New file — band-level merge helpers |
| `data/field-development/subseaiq-scan-latest.json` | Data backfill target — add equipment counts to 10 GoM fields |
| `worldenergydata/src/worldenergydata/cost/data_collection/public_dataset.py` | Read-only reference — 71 sanctioned cost records |
| `worldenergydata/subseaiq/analytics/normalize.py` | Read-only reference — equipment field normalization |

---

## 7. Final Recommendation

**NEEDS REFINEMENT → then READY FOR PLAN-REVIEW.** The stage-1 dossier's core finding stands: equipment count data is absent from the JSON data file, blocking the issue's stated correlation goal. However, the implementation path is clear — a manual backfill of 10 GoM fields plus band-level aggregation makes this achievable in a single session. Apply `status:needs-refinement`, resolve the 4 scoping decisions in Section 3.1, then upgrade to `status:plan-review` for user approval before dispatching implementation.
