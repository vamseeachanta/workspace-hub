# Dossier: Issue #2060 — Project Timeline Benchmarks from SubseaIQ Milestone Data

| Field | Value |
|-------|-------|
| Issue | [#2060](https://github.com/vamseeachanta/workspace-hub/issues/2060) |
| Title | feat(field-dev): project timeline benchmarks from SubseaIQ milestone data |
| Labels | enhancement, cat:engineering, agent:claude |
| Depends on | #1861 (scaffold — done, commit `aaf90c8e`) |
| Date | 2026-04-09 |

---

## 1. Current-State Findings

### 1.1 Files/Modules Already Present

| File | Lines | Status |
|------|-------|--------|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | 240 | Scaffold complete — static attributes only |
| `digitalmodel/tests/field_development/test_benchmarks.py` | 417 | Tests for existing scaffold; 27 tests across 5 classes |
| `worldenergydata/subseaiq/analytics/normalize.py` | 130 | Field alias normalization — 10 canonical fields mapped |
| `digitalmodel/src/digitalmodel/field_development/__init__.py` | 58 | Module exports — benchmarks NOT re-exported yet |

### 1.2 Existing `SubseaProject` Dataclass (benchmarks.py:53-69)

```python
@dataclass
class SubseaProject:
    name: str                                   # required
    operator: Optional[str] = None
    water_depth_m: Optional[float] = None
    concept_type: Optional[str] = None
    tieback_distance_km: Optional[float] = None
    num_wells: Optional[int] = None
    num_trees: Optional[int] = None
    num_manifolds: Optional[int] = None
    fluid_type: Optional[str] = None
    region: Optional[str] = None
```

**Zero timeline fields exist.** No `year_concept`, `year_feed`, `year_fid`, `year_first_oil`, or any date/duration fields.

### 1.3 Existing Public Functions (benchmarks.py)

| Function | Line | Purpose |
|----------|------|---------|
| `load_projects(records)` | 76 | Parse raw dicts into `SubseaProject` list |
| `concept_benchmark_bands(projects)` | 121 | Concept type counts by water-depth band |
| `subsea_architecture_stats(projects)` | 156 | Tieback/trees/manifolds descriptive stats |

### 1.4 Existing Internal Helpers (benchmarks.py)

| Helper | Line | Purpose |
|--------|------|---------|
| `_classify_depth(depth_m)` | 203 | Classify depth into DEPTH_BANDS |
| `_describe(values)` | 211 | min/max/mean/count (NO percentiles) |
| `_opt_float(val)` | 223 | Safe float conversion |
| `_opt_int(val)` | 233 | Safe int conversion |

### 1.5 Existing Normalizer Aliases (normalize.py:31-54)

10 canonical fields mapped: `name`, `operator`, `water_depth_m`, `concept_type`, `tieback_distance_km`, `num_wells`, `num_trees`, `num_manifolds`, `fluid_type`, `region`.

**Zero timeline aliases exist.**

### 1.6 Tests Already Present (test_benchmarks.py)

| Class | Tests | Lines |
|-------|-------|-------|
| `TestLoadProjects` | 8 | 142-179 |
| `TestConceptBenchmarkBands` | 8 | 186-251 |
| `TestSubseaArchitectureStats` | 7 | 258-310 |
| `TestJunkValues` | 3 | 317-353 |
| `TestNormalizeIntegration` | 1 | 359-416 |

**Total: 27 existing tests. Zero timeline tests.**

### 1.7 Latest Relevant Commits

| Hash | Message |
|------|---------|
| `aaf90c8e` | Scaffold commit for #1861 — benchmarks.py + normalize.py + tests |
| `d8a6fd841` | `data: scrape SubseaIQ public field development data (#1860)` |
| No commits found touching these files since scaffold. |

### 1.8 Related Codebase Context

- `capex_estimator.py` and `opex_estimator.py` both use P50 terminology for base-case estimates but not percentile functions.
- `economics.py` has `field_life_years: int` — the only existing temporal parameter in the module.
- `subsea_bridge.py` has `GoMField.year` (production start year) — a single integer, not a full timeline.
- No Python-level percentile/quantile utilities exist in the field_development module.

---

## 2. Remaining Implementation Delta

### 2.1 Exact Missing Behaviors

| # | Behavior | Issue Checklist Item |
|---|----------|---------------------|
| B1 | Four new `Optional[int]` fields on `SubseaProject`: `year_concept`, `year_feed`, `year_fid`, `year_first_oil` | "Add timeline fields to SubseaProject" |
| B2 | `load_projects()` must parse these four fields from input dicts | Implicit from B1 |
| B3 | New function: compute inter-phase durations (concept→FEED, FEED→FID, FID→first_oil, concept→first_oil) | "Compute Concept→FEED→FID→First Oil duration statistics" |
| B4 | New function: duration statistics grouped by `concept_type` and a complexity proxy | "Duration statistics by concept type and project complexity" |
| B5 | New function: P10/P50/P90 percentile distributions for each duration interval | "Project schedule probability distributions" |
| B6 | Four new entries in `_FIELD_ALIASES` dict in normalize.py for timeline fields | "Extend normalizer with timeline field aliases" |
| B7 | Type conversion for timeline fields in `normalize_project()` (int via `_safe_int`) | Implicit from B6 |

### 2.2 Exact File Paths That Must Change

| File | Change Type |
|------|-------------|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | Extend dataclass, extend `load_projects`, add 3 new public functions, extend `_describe` or add `_percentiles` helper |
| `digitalmodel/tests/field_development/test_benchmarks.py` | Add timeline fields to fixtures, add 4+ new test classes |
| `worldenergydata/subseaiq/analytics/normalize.py` | Add 4 entries to `_FIELD_ALIASES`, add int conversion for timeline fields in `normalize_project` |

### 2.3 Design Decisions Required

| Decision | Recommended Approach | Rationale |
|----------|---------------------|-----------|
| Percentile computation | Use `sorted()` + index math, no numpy dependency | Module has zero numpy usage; keep dependency-free |
| Complexity proxy | Use `concept_type` + water-depth band as a 2D key | Matches existing `_classify_depth()` pattern |
| Year vs date | Use `Optional[int]` (year), not `datetime` | Issue specifies `year_concept`, `year_feed` etc. — integer years match SubseaIQ granularity |
| Duration type | Integer years (e.g. `year_fid - year_concept`) | Consistent with year-level input resolution |

---

## 3. TDD-First Execution Plan

### Phase 1: Failing Tests First

#### 1a. Extend test fixtures (test_benchmarks.py)

Add timeline fields to `FIXTURE_RECORDS`:

```python
# Add to each fixture record:
# Alpha:   year_concept=2005, year_feed=2007, year_fid=2009, year_first_oil=2013
# Bravo:   year_concept=2008, year_feed=2010, year_fid=2012, year_first_oil=2016
# Charlie: year_concept=2010, year_feed=2012, year_fid=2014, year_first_oil=2019
# Delta:   year_concept=2012, year_feed=2015, year_fid=2017, year_first_oil=2022
# Echo:    year_concept=2015, year_feed=None, year_fid=2019, year_first_oil=None  (sparse)
# Foxtrot: year_concept=2006, year_feed=2009, year_fid=2012, year_first_oil=2017
# Golf:    year_concept=2018, year_feed=2019, year_fid=2020, year_first_oil=2022
# Hotel:   year_concept=2014, year_feed=2016, year_fid=None, year_first_oil=None  (sparse)
```

#### 1b. Add test class `TestLoadProjectsTimeline` (~6 tests)

```
test_timeline_fields_loaded           — year_concept/year_feed/year_fid/year_first_oil populated
test_timeline_none_when_missing       — sparse records default to None
test_timeline_string_years_parsed     — "2015" → 2015
test_timeline_junk_years_become_none  — "TBD" → None
test_timeline_partial_preserved       — Echo has concept+fid but no feed/first_oil
test_timeline_not_required            — records with no timeline fields still load fine
```

#### 1c. Add test class `TestTimelineDurations` (~8 tests)

```
test_returns_dict_with_phase_keys     — keys: concept_to_feed, feed_to_fid, fid_to_first_oil, concept_to_first_oil
test_concept_to_feed_stats            — Alpha: 2yr, Bravo: 2yr, etc. → verify min/max/mean
test_feed_to_fid_stats                — verify computed durations
test_fid_to_first_oil_stats           — verify computed durations
test_concept_to_first_oil_total       — end-to-end duration
test_skips_projects_with_missing_years — Echo (no year_feed) excluded from concept_to_feed
test_empty_input_returns_zero_counts  — empty list → count=0
test_negative_durations_excluded      — if year_fid < year_concept, skip (data error)
```

#### 1d. Add test class `TestDurationsByConceptType` (~5 tests)

```
test_returns_dict_keyed_by_concept_type  — "TLP", "FPSO", etc.
test_tlp_durations                       — Bravo + Charlie grouped
test_single_concept_type                 — FPSO has only Foxtrot
test_skips_projects_without_timeline     — graceful exclusion
test_empty_input                         — empty list → empty dict
```

#### 1e. Add test class `TestScheduleDistributions` (~6 tests)

```
test_returns_p10_p50_p90_keys         — each phase duration has percentile keys
test_p50_matches_median               — median of durations
test_p10_less_than_p50                 — ordering: P10 ≤ P50 ≤ P90
test_single_project_p10_equals_p90    — degenerate case
test_skips_projects_with_missing_data — sparse data excluded
test_empty_input                      — empty → zeros or empty
```

#### 1f. Add test class `TestNormalizeTimelineIntegration` (~3 tests)

```
test_raw_timeline_keys_normalized     — "Concept Year" → year_concept
test_timeline_pipeline_end_to_end     — raw SubseaIQ keys → normalize → load → durations
test_mixed_timeline_and_static        — both static and timeline fields survive pipeline
```

### Phase 2: Implementation Steps

#### Step 2a. Extend `SubseaProject` dataclass (benchmarks.py:60-69)

Add after `region`:
```python
year_concept: Optional[int] = None
year_feed: Optional[int] = None
year_fid: Optional[int] = None
year_first_oil: Optional[int] = None
```

#### Step 2b. Extend `load_projects()` (benchmarks.py:100-113)

Add four `_opt_int()` calls for the new fields.

#### Step 2c. Add `_percentiles()` helper (benchmarks.py, new)

```python
def _percentiles(values: list[float], quantiles: tuple[float, ...] = (0.1, 0.5, 0.9)) -> dict[str, float]:
    """Compute percentiles from a sorted list without numpy."""
```

Pure-Python implementation using linear interpolation on sorted values.

#### Step 2d. Add `timeline_duration_stats()` public function (benchmarks.py, new)

```python
def timeline_duration_stats(projects: list[SubseaProject]) -> dict[str, dict[str, float]]:
    """Compute Concept→FEED→FID→First Oil duration statistics."""
```

Returns dict with keys: `concept_to_feed`, `feed_to_fid`, `fid_to_first_oil`, `concept_to_first_oil`. Each value is `_describe(durations)` output.

#### Step 2e. Add `duration_stats_by_concept_type()` public function (benchmarks.py, new)

```python
def duration_stats_by_concept_type(projects: list[SubseaProject]) -> dict[str, dict[str, dict[str, float]]]:
    """Duration statistics grouped by concept type."""
```

Outer key: concept_type. Inner structure matches `timeline_duration_stats` output.

#### Step 2f. Add `schedule_distributions()` public function (benchmarks.py, new)

```python
def schedule_distributions(projects: list[SubseaProject]) -> dict[str, dict[str, float]]:
    """P10/P50/P90 schedule duration distributions per phase transition."""
```

Returns dict keyed by phase transition, each containing `p10`, `p50`, `p90` values.

#### Step 2g. Extend normalizer (normalize.py:31-54)

Add to `_FIELD_ALIASES`:
```python
"year_concept": [
    "year_concept", "Concept Year", "concept_year", "Year Concept",
    "year_of_concept", "conceptYear",
],
"year_feed": [
    "year_feed", "FEED Year", "feed_year", "Year FEED",
    "year_of_feed", "feedYear",
],
"year_fid": [
    "year_fid", "FID Year", "fid_year", "Year FID",
    "year_of_fid", "fidYear", "Sanction Year", "sanction_year",
],
"year_first_oil": [
    "year_first_oil", "First Oil Year", "first_oil_year", "Year First Oil",
    "year_of_first_oil", "firstOilYear", "First Production Year",
    "first_production_year",
],
```

#### Step 2h. Extend `normalize_project()` type conversion (normalize.py:86-90)

Add timeline fields to the `_safe_int` conversion block:
```python
elif val is not None and canonical in (
    "num_wells", "num_trees", "num_manifolds",
    "year_concept", "year_feed", "year_fid", "year_first_oil",
):
    val = _safe_int(val)
```

### Phase 3: Verification Commands

```bash
# 1. Run all benchmark tests
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -v --tb=short

# 2. Run only new timeline tests
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -k "Timeline or Duration or Schedule or NormalizeTimeline" -v

# 3. Run normalize integration test
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py::TestNormalizeTimelineIntegration -v

# 4. Type check
cd digitalmodel && uv run python -c "from digitalmodel.field_development.benchmarks import SubseaProject; p = SubseaProject(name='test', year_concept=2020, year_fid=2024); print(p)"

# 5. Full field_development test suite (regression)
cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short

# 6. Quick smoke test for P10/P50/P90
cd digitalmodel && uv run python -c "
from digitalmodel.field_development.benchmarks import load_projects, schedule_distributions
recs = [
    {'name': 'A', 'year_concept': 2005, 'year_first_oil': 2013},
    {'name': 'B', 'year_concept': 2008, 'year_first_oil': 2016},
    {'name': 'C', 'year_concept': 2010, 'year_first_oil': 2019},
]
projects = load_projects(recs)
dist = schedule_distributions(projects)
print(dist)
assert 'concept_to_first_oil' in dist
assert dist['concept_to_first_oil']['p10'] <= dist['concept_to_first_oil']['p90']
print('PASS')
"

# 7. Verify normalizer handles timeline aliases
cd worldenergydata && uv run python -c "
from subseaiq.analytics.normalize import normalize_project
raw = {'Project Name': 'Test', 'Concept Year': 2010, 'FID Year': 2015, 'First Oil Year': 2020}
out = normalize_project(raw)
assert out['year_concept'] == 2010
assert out['year_fid'] == 2015
assert out['year_first_oil'] == 2020
print('PASS')
"
```

---

## 4. Risk/Blocker Analysis

### 4.1 Plan-Gate Blockers

| Blocker | Severity | Mitigation |
|---------|----------|------------|
| Issue #2060 lacks `status:plan-approved` label | **BLOCKING** | User must review this dossier and apply `status:plan-approved` before implementation |
| No `status:plan-review` label yet | Medium | Apply `status:plan-review` label to #2060 after posting this dossier |

### 4.2 Data/Source Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| SubseaIQ scraping with milestone date fields | **Unknown** | Issue body says "Depends on: SubseaIQ scraping with milestone date fields". Implementation can proceed with synthetic test data, but real value depends on scraped data having `Concept Year`, `FID Year`, `First Oil Year` fields |
| Actual SubseaIQ field names for timeline data | **Unknown** | The alias list in Step 2g is educated guesses. Real SubseaIQ scrape output should be inspected to confirm exact raw key names |
| `worldenergydata/subseaiq/` has no data files | Confirmed | Only `analytics/normalize.py` exists. No CSV/JSON data files with actual project milestone dates |

### 4.3 Merge/Contention Concerns

| Concern | Risk Level | Notes |
|---------|------------|-------|
| `benchmarks.py` modification by other terminals | **Low** | No other terminal in this 10-terminal batch targets benchmarks.py |
| `normalize.py` modification | **Low** | Only terminal-3 touches this file |
| `test_benchmarks.py` fixture modification | **Low** | Additive changes (new fields to existing fixtures, new test classes) |
| `__init__.py` re-export | **None** | Benchmarks module is not yet re-exported from `__init__.py` — no contention |

### 4.4 Technical Risks

| Risk | Mitigation |
|------|------------|
| Pure-Python percentile accuracy | Use linear interpolation matching `numpy.percentile(method='linear')`; add edge-case tests (1 element, 2 elements) |
| Negative computed durations (data errors) | Filter out negative durations with explicit skip + optional warning |
| All timeline fields None in real data | Graceful handling already pattern-established: functions return count=0 dicts |

---

## 5. Ready-to-Execute Prompt

```
You are implementing GitHub issue #2060: "feat(field-dev): project timeline benchmarks from SubseaIQ milestone data".

## Context
- Repo: workspace-hub (working directory: /mnt/local-analysis/workspace-hub)
- This extends the SubseaIQ benchmark bridge (issue #1861, scaffold complete).
- The benchmark bridge currently handles static project attributes. This adds temporal/schedule analysis.
- Use TDD: write failing tests first, then implement.
- Use `uv run` for all Python commands.

## Files to Modify
1. `digitalmodel/src/digitalmodel/field_development/benchmarks.py`
2. `digitalmodel/tests/field_development/test_benchmarks.py`
3. `worldenergydata/subseaiq/analytics/normalize.py`

## Implementation Checklist

### Step 1: Extend test fixtures (test_benchmarks.py)
- Add timeline fields (year_concept, year_feed, year_fid, year_first_oil) to FIXTURE_RECORDS
- Include at least 2 sparse records (some timeline fields = None)
- Keep all existing fixture data unchanged

### Step 2: Write failing test classes
- TestLoadProjectsTimeline: 6 tests for field loading, parsing, None defaults
- TestTimelineDurations: 8 tests for inter-phase duration computation
- TestDurationsByConceptType: 5 tests for concept-type grouping
- TestScheduleDistributions: 6 tests for P10/P50/P90 percentiles
- TestNormalizeTimelineIntegration: 3 tests for normalize → load pipeline

### Step 3: Run tests to confirm they fail
```bash
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -k "Timeline or Duration or Schedule or NormalizeTimeline" -v
```

### Step 4: Implement in benchmarks.py
- Add 4 Optional[int] fields to SubseaProject: year_concept, year_feed, year_fid, year_first_oil
- Extend load_projects() with _opt_int() calls for new fields
- Add _percentiles(values, quantiles) helper — pure Python, no numpy
- Add timeline_duration_stats(projects) → dict of phase transition statistics
- Add duration_stats_by_concept_type(projects) → stats grouped by concept_type
- Add schedule_distributions(projects) → P10/P50/P90 per phase transition

### Step 5: Implement in normalize.py
- Add 4 entries to _FIELD_ALIASES for year_concept, year_feed, year_fid, year_first_oil
- Add timeline fields to _safe_int conversion in normalize_project()

### Step 6: Run full test suite
```bash
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -v --tb=short
cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short
```

## Acceptance Criteria
- [ ] All 27 existing tests still pass (regression)
- [ ] All new timeline tests pass (~28 new tests)
- [ ] P10 ≤ P50 ≤ P90 invariant holds for all distributions
- [ ] Sparse data (missing timeline fields) handled gracefully — no crashes
- [ ] Junk values ("TBD", "N/A", "") in timeline fields → None
- [ ] Negative computed durations (year_fid < year_concept) excluded from stats
- [ ] normalize_project handles SubseaIQ timeline field aliases
- [ ] No new dependencies added (pure Python percentiles)
- [ ] benchmarks.py stays under 500 lines
- [ ] File header ABOUTME comments updated

## Cross-Review Requirements
- After implementation, run: `uv run pytest tests/field_development/ -v --tb=short`
- Verify no new imports beyond stdlib (dataclasses, typing)
- Verify _percentiles matches numpy.percentile behavior for small samples
- Verify normalize.py aliases cover likely SubseaIQ scrape column names
```

---

## 6. Final Recommendation

**READY AFTER LABEL UPDATE**

Issue #2060 is well-scoped, has zero existing implementation overlap, and builds cleanly on top of the #1861 scaffold. All three target files are identified and verified. The implementation is purely additive — no existing code needs modification beyond extending the dataclass and load function.

**Pre-implementation actions required:**
1. Apply `status:plan-review` label to #2060
2. Post this dossier (or link to it) as a comment on #2060
3. After user review, apply `status:plan-approved` label
4. Confirm SubseaIQ scrape data field names for timeline aliases (or accept educated guesses and refine later)

**Estimated scope:** ~150 new lines in benchmarks.py, ~150 new test lines, ~30 new normalizer lines. Medium complexity, self-contained, no cross-module dependencies.
