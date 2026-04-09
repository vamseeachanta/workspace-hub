# Dossier: Concept Selection Probability Matrix & Decision Tree

## Issue Metadata

| Field | Value |
|-------|-------|
| Issue | #2053 |
| Title | feat(field-dev): concept selection probability matrix and decision tree from SubseaIQ benchmarks |
| Labels | `enhancement`, `priority:high`, `cat:engineering`, `agent:claude` |
| Status | OPEN (no `status:plan-review` or `status:plan-approved` label) |
| Depends on | #1861 (scaffold -- DONE, commits `aaf90c8e`, `526e2352`) |
| Depends on | SubseaIQ scraping issue (real dataset -- NOT YET AVAILABLE) |
| Target files | `benchmarks.py` (extend), `test_benchmarks.py` (extend) |
| Dossier date | 2026-04-09 |

---

## 1. Current-State Findings

### 1.1 Files and Modules Already Present

| File | Lines | Issue | Status |
|------|-------|-------|--------|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | 241 | #1861 | Complete scaffold |
| `digitalmodel/src/digitalmodel/field_development/concept_selection.py` | 393 | #1843 | Complete, hardcoded GoM weights |
| `digitalmodel/src/digitalmodel/field_development/subsea_bridge.py` | 530 | #1861 | Complete, 10-field GoM catalog |
| `digitalmodel/src/digitalmodel/field_development/capex_estimator.py` | -- | #1843 | Complete |
| `digitalmodel/src/digitalmodel/field_development/opex_estimator.py` | -- | #1843 | Complete |
| `digitalmodel/src/digitalmodel/field_development/economics.py` | -- | #1858 | Complete |
| `digitalmodel/src/digitalmodel/field_development/__init__.py` | 59 | -- | Exports concept_selection symbols, NOT benchmarks symbols |
| `data/field-development/subseaiq-scan-latest.json` | 113 | #1861 | 10 GoM fields (no Norwegian fields) |

### 1.2 Tests Already Present

| File | Tests | Issue |
|------|-------|-------|
| `digitalmodel/tests/field_development/test_benchmarks.py` | 27 (5 classes) | #1861 |
| `digitalmodel/tests/field_development/test_concept_selection.py` | 38+ (9 classes) | #1843 |
| `digitalmodel/tests/field_development/test_subsea_bridge.py` | 10+ | #1861 |

**Test classes in `test_benchmarks.py`:**
- `TestLoadProjects` (7 tests)
- `TestConceptBenchmarkBands` (7 tests)
- `TestSubseaArchitectureStats` (6 tests + 1 empty)
- `TestJunkValues` (3 tests)
- `TestNormalizeIntegration` (1 integration test)

**Test result at scaffold completion:** 27 passed in 2.68s (per #1861 implementation comment).

### 1.3 Latest Relevant Commits

| Hash | Date | Message |
|------|------|---------|
| `526e2352` | 2026-04-09 | `fix(field-dev): harden benchmark bridge against scraped junk values (#1861)` |
| `aaf90c8e` | 2026-04-09 | `feat(field-dev): add SubseaIQ benchmark bridge scaffold (#1861)` |
| `689fadfd` | 2026-04-08 | `fix(field-dev): address code review findings for economics facade (#1858)` |
| `d5e1bd19` | 2026-04-04 | `feat(field_development): add concept selection framework (#1843)` |

### 1.4 Key Data Structures (Current State)

**`SubseaProject` dataclass** (`benchmarks.py:54-69`):
```python
@dataclass
class SubseaProject:
    name: str
    operator: Optional[str] = None
    water_depth_m: Optional[float] = None
    concept_type: Optional[str] = None
    tieback_distance_km: Optional[float] = None
    num_wells: Optional[int] = None
    num_trees: Optional[int] = None
    num_manifolds: Optional[int] = None
    fluid_type: Optional[str] = None
    region: Optional[str] = None
    # MISSING: production_rate / capacity_bopd (needed for #2053 scope item 1)
```

**`GoMField` dataclass** (`subsea_bridge.py:35-60`):
```python
@dataclass
class GoMField:
    name: str
    operator: str
    water_depth_m: float
    host: str          # e.g. 'Spar', 'TLP', 'Semi-submersible'
    year: int
    capacity_bopd: int  # HAS production capacity
```

**`concept_selection()` scoring weights** (`concept_selection.py:248-253`):
```python
# Weights: depth (40%), reservoir (30%), distance (20%), fluid (10%)
0.40 * depth_s + 0.30 * reservoir_s + 0.20 * distance_s + 0.10 * fluid_s
```
These are hardcoded. Issue #2053 scope item 5 says: "wire into existing concept_selection.py as an empirical weighting factor".

**Depth band constants** (`benchmarks.py:34-46`):
```python
DEPTH_BANDS = ("0-300m", "300-800m", "800-1500m", "1500m+")
_DEPTH_THRESHOLDS = ((0.0, 300.0), (300.0, 800.0), (800.0, 1500.0), (1500.0, inf))
```

---

## 2. Remaining Implementation Delta

### 2.1 Exact Missing Behaviors

| # | Scope item | Status | What's missing |
|---|-----------|--------|----------------|
| 1 | Extract concept_type + water_depth + production_rate correlations | NOT STARTED | `SubseaProject` lacks `production_rate`/`capacity_bopd` field. No correlation extraction function exists. |
| 2 | Build decision tree: (water_depth, reservoir_size, distance_to_infra) -> concept type | NOT STARTED | No `concept_decision_tree()` function. Need simple rule-based tree (not ML — dataset too small). |
| 3 | Generate probability matrix by depth band | NOT STARTED | `concept_benchmark_bands()` returns raw counts but no percentage conversion. Need `concept_probability_matrix()`. |
| 4 | Validate against 6 case studies | NOT STARTED | Only 4 of 6 fields (Mad Dog, Appomattox, Perdido, Whale) are in GoM dataset. Solveig and Sverdrup are Norwegian NCS fields not in current data. |
| 5 | Wire into concept_selection.py as empirical weighting factor | NOT STARTED | `concept_selection()` uses hardcoded weights. Need an `empirical_weight` parameter or a `blend_empirical_scores()` integration. |

### 2.2 Exact File Paths That Should Change

**Primary changes (in benchmarks.py):**
1. `digitalmodel/src/digitalmodel/field_development/benchmarks.py` — add:
   - `production_rate_bopd` field to `SubseaProject` dataclass (line ~69)
   - `concept_probability_matrix(projects) -> dict[str, dict[str, float]]` — converts band counts to percentages
   - `concept_decision_tree(water_depth, reservoir_size_mmbbl, distance_to_infra_km, projects) -> str` — rule-based concept prediction
   - `_extract_correlations(projects) -> dict` — concept_type + water_depth + production_rate correlation helper

2. `digitalmodel/tests/field_development/test_benchmarks.py` — add:
   - `TestConceptProbabilityMatrix` class (~8-10 tests)
   - `TestConceptDecisionTree` class (~8-10 tests)
   - `TestCaseStudyValidation` class (6 tests, one per case study)
   - Fixture data with `production_rate_bopd` values

**Secondary changes (concept_selection integration):**
3. `digitalmodel/src/digitalmodel/field_development/concept_selection.py` — modify:
   - `concept_selection()` to accept optional `empirical_weights: dict[str, float]` parameter
   - New internal `_apply_empirical_bias()` helper
   - Blend empirical probability with existing composite score

4. `digitalmodel/tests/field_development/test_concept_selection.py` — add:
   - Tests for empirical weighting factor integration

5. `digitalmodel/src/digitalmodel/field_development/__init__.py` — add exports:
   - `concept_probability_matrix`, `concept_decision_tree` from benchmarks

**Data changes:**
6. `data/field-development/subseaiq-scan-latest.json` — may need expansion with:
   - Norwegian fields (Solveig, Sverdrup) or separate NCS dataset
   - Additional field metadata for validation targets

---

## 3. TDD-First Execution Plan

### Phase 1: Failing Tests First

#### Step 1.1 — Add `production_rate_bopd` to SubseaProject
```python
# test_benchmarks.py — new test in TestLoadProjects
def test_production_rate_field_loaded(self, projects):
    """SubseaProject should support production_rate_bopd."""
    bravo = [p for p in projects if p.name == "Bravo"][0]
    assert hasattr(bravo, "production_rate_bopd")
```
Update `FIXTURE_RECORDS` to include `"production_rate_bopd"` values.

#### Step 1.2 — Probability Matrix Tests
```python
class TestConceptProbabilityMatrix:
    def test_returns_dict_with_depth_bands(self, projects):
        matrix = concept_probability_matrix(projects)
        for band in DEPTH_BANDS:
            assert band in matrix

    def test_probabilities_sum_to_one(self, projects):
        matrix = concept_probability_matrix(projects)
        for band, probs in matrix.items():
            if probs:  # skip empty bands
                assert abs(sum(probs.values()) - 1.0) < 1e-6

    def test_deepwater_band_percentages(self, projects):
        """Charlie (900m, TLP) and Delta (1200m, Semi) -> 50% each."""
        matrix = concept_probability_matrix(projects)
        deep = matrix["800-1500m"]
        assert deep["TLP"] == pytest.approx(0.5)
        assert deep["Semi"] == pytest.approx(0.5)

    def test_empty_band_returns_empty_dict(self):
        matrix = concept_probability_matrix([])
        assert all(v == {} for v in matrix.values())

    def test_single_project_band_is_100_percent(self):
        projects = load_projects([
            {"name": "Solo", "water_depth_m": 200, "concept_type": "Fixed"}
        ])
        matrix = concept_probability_matrix(projects)
        assert matrix["0-300m"]["Fixed"] == pytest.approx(1.0)

    def test_missing_fields_excluded(self, sparse_projects):
        matrix = concept_probability_matrix(sparse_projects)
        total_concepts = sum(len(v) for v in matrix.values())
        assert total_concepts == 1  # only Sparse-D classifiable

    def test_example_from_issue(self):
        """Issue says 'at 800-1500m: 45% Semi, 30% TLP, ...' style output."""
        # Build a dataset that produces known percentages
        records = [
            {"name": f"S{i}", "water_depth_m": 1000, "concept_type": "Semi"}
            for i in range(9)
        ] + [
            {"name": f"T{i}", "water_depth_m": 1000, "concept_type": "TLP"}
            for i in range(6)
        ] + [
            {"name": f"P{i}", "water_depth_m": 1000, "concept_type": "Spar"}
            for i in range(3)
        ] + [
            {"name": f"B{i}", "water_depth_m": 1000, "concept_type": "Tieback"}
            for i in range(2)
        ]
        projects = load_projects(records)
        matrix = concept_probability_matrix(projects)
        deep = matrix["800-1500m"]
        assert deep["Semi"] == pytest.approx(0.45)
        assert deep["TLP"] == pytest.approx(0.30)
        assert deep["Spar"] == pytest.approx(0.15)
        assert deep["Tieback"] == pytest.approx(0.10)
```

#### Step 1.3 — Decision Tree Tests
```python
class TestConceptDecisionTree:
    def test_returns_string_concept_type(self, projects):
        result = concept_decision_tree(
            water_depth=900, reservoir_size_mmbbl=100,
            distance_to_infra_km=50, projects=projects,
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_shallow_water_predicts_fixed_or_tieback(self, projects):
        result = concept_decision_tree(
            water_depth=200, reservoir_size_mmbbl=30,
            distance_to_infra_km=5, projects=projects,
        )
        assert result in ("Fixed Platform", "Subsea Tieback")

    def test_deep_water_large_reservoir_standalone(self, projects):
        result = concept_decision_tree(
            water_depth=1800, reservoir_size_mmbbl=300,
            distance_to_infra_km=80, projects=projects,
        )
        assert result in ("Spar", "Semi", "FPSO")

    def test_close_infra_small_reservoir_tieback(self, projects):
        result = concept_decision_tree(
            water_depth=500, reservoir_size_mmbbl=20,
            distance_to_infra_km=5, projects=projects,
        )
        assert "Tieback" in result

    def test_raises_on_invalid_depth(self, projects):
        with pytest.raises(ValueError):
            concept_decision_tree(
                water_depth=-100, reservoir_size_mmbbl=100,
                distance_to_infra_km=50, projects=projects,
            )

    def test_none_distance_excludes_tieback(self, projects):
        result = concept_decision_tree(
            water_depth=1200, reservoir_size_mmbbl=200,
            distance_to_infra_km=None, projects=projects,
        )
        assert "Tieback" not in result

    def test_ultra_deep_favours_spar_or_fpso(self, projects):
        result = concept_decision_tree(
            water_depth=2500, reservoir_size_mmbbl=200,
            distance_to_infra_km=100, projects=projects,
        )
        assert result in ("Spar", "FPSO", "Semi")

    def test_decision_informed_by_project_data(self):
        """Tree should reflect empirical data, not just hard rules."""
        heavy_semi = load_projects([
            {"name": f"S{i}", "water_depth_m": 1200, "concept_type": "Semi"}
            for i in range(10)
        ])
        result = concept_decision_tree(
            water_depth=1200, reservoir_size_mmbbl=150,
            distance_to_infra_km=40, projects=heavy_semi,
        )
        assert result == "Semi"
```

#### Step 1.4 — Case Study Validation Tests
```python
class TestCaseStudyValidation:
    """Validate predictions against 6 real-world case studies."""

    @pytest.fixture
    def case_studies(self):
        """Known case studies from issue scope."""
        return {
            "Mad Dog":      {"depth": 1480, "actual": "Semi"},
            "Appomattox":   {"depth": 2250, "actual": "Semi"},
            "Perdido":      {"depth": 2438, "actual": "Spar"},
            "Whale":        {"depth": 2100, "actual": "Spar"},
            # Norwegian fields — require expanded dataset:
            # "Solveig":    {"depth": 350,  "actual": "Subsea Tieback"},
            # "Sverdrup":   {"depth": 110,  "actual": "Fixed Platform"},
        }

    def test_mad_dog_prediction(self, projects, case_studies):
        cs = case_studies["Mad Dog"]
        result = concept_decision_tree(
            water_depth=cs["depth"], reservoir_size_mmbbl=200,
            distance_to_infra_km=50, projects=projects,
        )
        assert result == cs["actual"] or cs["actual"] in result

    def test_appomattox_prediction(self, projects, case_studies):
        cs = case_studies["Appomattox"]
        result = concept_decision_tree(
            water_depth=cs["depth"], reservoir_size_mmbbl=200,
            distance_to_infra_km=60, projects=projects,
        )
        assert result == cs["actual"] or cs["actual"] in result

    def test_perdido_prediction(self, projects, case_studies):
        cs = case_studies["Perdido"]
        result = concept_decision_tree(
            water_depth=cs["depth"], reservoir_size_mmbbl=100,
            distance_to_infra_km=80, projects=projects,
        )
        assert result == cs["actual"] or cs["actual"] in result

    def test_whale_prediction(self, projects, case_studies):
        cs = case_studies["Whale"]
        result = concept_decision_tree(
            water_depth=cs["depth"], reservoir_size_mmbbl=80,
            distance_to_infra_km=60, projects=projects,
        )
        assert result == cs["actual"] or cs["actual"] in result
```

### Phase 2: Implementation Steps

1. **Add `production_rate_bopd` to `SubseaProject`** — new optional field, update `load_projects()` to parse it, update `_opt_float` usage
2. **Implement `concept_probability_matrix()`** — reuse `concept_benchmark_bands()` output, convert counts to fractions per band
3. **Implement `concept_decision_tree()`** — rule-based tree combining depth-band empirical probabilities with reservoir/distance thresholds. NOT an ML decision tree (dataset too small for sklearn). Structure:
   - Classify depth band
   - Look up empirical probabilities from `concept_probability_matrix()`
   - Apply reservoir size filter (small -> tieback bias, large -> standalone bias)
   - Apply distance filter (close -> tieback boost, far -> standalone boost)
   - Return most probable concept type after all filters
4. **Wire into `concept_selection.py`** — add optional `empirical_weights` parameter to `concept_selection()`, blend with existing composite score using configurable alpha (e.g. 0.3 empirical + 0.7 analytical)
5. **Export new symbols** from `__init__.py`
6. **Add Solveig/Sverdrup stubs** — mark as `pytest.skip("Norwegian dataset not yet available")` until SubseaIQ scraping dependency is fulfilled

### Phase 3: Verification Commands

```bash
# 1. Run all benchmark tests (existing + new)
cd digitalmodel && uv run python -m pytest tests/field_development/test_benchmarks.py -v

# 2. Run concept selection tests (check integration doesn't break)
cd digitalmodel && uv run python -m pytest tests/field_development/test_concept_selection.py -v

# 3. Run full field_development test suite
cd digitalmodel && uv run python -m pytest tests/field_development/ -v

# 4. Type checking (if mypy configured)
cd digitalmodel && uv run python -m mypy src/digitalmodel/field_development/benchmarks.py --ignore-missing-imports

# 5. Verify probability matrix output shape
cd digitalmodel && uv run python -c "
from digitalmodel.field_development.benchmarks import load_projects, concept_probability_matrix
projects = load_projects([
    {'name': 'A', 'water_depth_m': 1000, 'concept_type': 'TLP'},
    {'name': 'B', 'water_depth_m': 1100, 'concept_type': 'Semi'},
    {'name': 'C', 'water_depth_m': 1050, 'concept_type': 'TLP'},
])
matrix = concept_probability_matrix(projects)
print(matrix)
# Expected: {'800-1500m': {'TLP': 0.667, 'Semi': 0.333}, ...}
"

# 6. Verify decision tree against known GoM field
cd digitalmodel && uv run python -c "
from digitalmodel.field_development.benchmarks import load_projects, concept_decision_tree
# Use fixture data for prediction
projects = load_projects([
    {'name': 'P', 'water_depth_m': 2438, 'concept_type': 'Spar'},
    {'name': 'A', 'water_depth_m': 2250, 'concept_type': 'Semi'},
    {'name': 'M', 'water_depth_m': 1480, 'concept_type': 'Semi'},
    {'name': 'T', 'water_depth_m': 1844, 'concept_type': 'Semi'},
    {'name': 'R', 'water_depth_m': 896, 'concept_type': 'TLP'},
])
# Perdido-like query -> should predict Spar
result = concept_decision_tree(
    water_depth=2400, reservoir_size_mmbbl=100,
    distance_to_infra_km=80, projects=projects,
)
print(f'Predicted: {result}')
assert result in ('Spar', 'FPSO', 'Semi'), f'Unexpected: {result}'
"

# 7. Verify empirical weights integration in concept_selection
cd digitalmodel && uv run python -c "
from digitalmodel.field_development.concept_selection import concept_selection
# Should still work without empirical_weights (backward compatible)
result = concept_selection(
    water_depth=2438, reservoir_size_mmbbl=100,
    distance_to_infra_km=80, fluid_type='oil',
)
print(f'Without empirical: {result.selected_host.value}')
"
```

---

## 4. Risk/Blocker Analysis

### 4.1 Plan-Gate Blockers

| Blocker | Severity | Resolution |
|---------|----------|------------|
| Issue #2053 has no `status:plan-approved` label | **BLOCKING** | User must review plan and add `status:plan-approved` before implementation |
| `cat:engineering` label triggers Hard-Stop Policy | **BLOCKING** | Full gate sequence required: plan -> user review -> implement -> cross-review |
| No `status:plan-review` label yet | **MINOR** | Add label when posting plan to issue as comment |

### 4.2 Data/Source Dependencies

| Dependency | Status | Impact |
|-----------|--------|--------|
| #1861 scaffold (benchmarks.py) | DONE | No blocker |
| SubseaIQ scraping issue (real dataset) | NOT DONE | Validation against Solveig/Sverdrup impossible until Norwegian NCS data is scraped. Current dataset is only 10 GoM fields. |
| `SubseaProject` lacks `production_rate_bopd` | Gap in dataclass | Scope item 1 (correlations) cannot be fully implemented without adding this field |
| `GoMField` has `capacity_bopd` but `SubseaProject` doesn't | Design mismatch | Bridge between the two data models needs to be established |

### 4.3 Likely Merge/Contention Concerns

| Concern | Files | Mitigation |
|---------|-------|------------|
| Concurrent edits to `benchmarks.py` | `benchmarks.py` | Only one issue (#2053) targets this file currently |
| `concept_selection.py` signature change | `concept_selection.py` | New parameter must be optional with default=None for backward compatibility |
| `__init__.py` export additions | `__init__.py` | Append-only change, low conflict risk |
| Test fixture expansion | `test_benchmarks.py` | Add new fixtures alongside existing ones, don't modify `FIXTURE_RECORDS` |

### 4.4 Technical Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| 10-field dataset too small for meaningful probability matrix | HIGH | Document as limitation; design API to accept larger datasets when available |
| Decision tree overfits to GoM-only data | HIGH | Make tree data-driven so it improves with more data; add `region` filter |
| Norwegian fields (Solveig, Sverdrup) have different depth/concept patterns than GoM | MEDIUM | Use `pytest.skip` for Norwegian validation until data available |
| Empirical weighting destabilises existing concept_selection tests | LOW | Use alpha blend with default alpha=0.0 (no change) |

---

## 5. Ready-to-Execute Prompt

```
You are implementing GitHub issue #2053: feat(field-dev): concept selection probability matrix and decision tree from SubseaIQ benchmarks.

## Pre-requisites
- Issue must have `status:plan-approved` label before starting
- Read: benchmarks.py (241 lines), concept_selection.py (393 lines), subsea_bridge.py (530 lines)
- Read: test_benchmarks.py (417 lines), test_concept_selection.py
- Read: data/field-development/subseaiq-scan-latest.json (10 GoM fields)

## TDD Implementation Order

### Step 1: Add production_rate_bopd to SubseaProject
- File: digitalmodel/src/digitalmodel/field_development/benchmarks.py
- Add `production_rate_bopd: Optional[float] = None` to SubseaProject dataclass (after line 69)
- Update load_projects() to parse `production_rate_bopd` using _opt_float()
- Test first: add test_production_rate_field_loaded to TestLoadProjects
- Update FIXTURE_RECORDS with production_rate_bopd values

### Step 2: Implement concept_probability_matrix()
- File: digitalmodel/src/digitalmodel/field_development/benchmarks.py
- Signature: `concept_probability_matrix(projects: list[SubseaProject]) -> dict[str, dict[str, float]]`
- Reuse concept_benchmark_bands() output, divide each count by band total
- Return: {"800-1500m": {"Semi": 0.5, "TLP": 0.5}, ...}
- Tests first: TestConceptProbabilityMatrix class (7-8 tests)
  - probabilities sum to 1.0 per band
  - empty bands return empty dict
  - known fixture produces expected percentages
  - matches issue example format

### Step 3: Implement concept_decision_tree()
- File: digitalmodel/src/digitalmodel/field_development/benchmarks.py
- Signature: `concept_decision_tree(water_depth: float, reservoir_size_mmbbl: float, distance_to_infra_km: Optional[float], projects: list[SubseaProject]) -> str`
- Rule-based (NOT sklearn) — dataset too small for ML
- Algorithm:
  1. Classify water_depth into band using _classify_depth()
  2. Get empirical probabilities from concept_probability_matrix()
  3. Apply reservoir bias: small (<50 MMbbl) boosts tieback probability
  4. Apply distance bias: close (<15 km) boosts tieback, far (>30 km) boosts standalone
  5. Return concept type with highest adjusted probability
- Raise ValueError for water_depth <= 0 or reservoir_size_mmbbl <= 0
- Tests first: TestConceptDecisionTree class (8 tests)

### Step 4: Validate against case studies
- Tests: TestCaseStudyValidation class
- 4 GoM fields testable now: Mad Dog, Appomattox, Perdido, Whale
- 2 Norwegian fields: Solveig, Sverdrup -> pytest.skip("Norwegian dataset not available")
- Each test creates a realistic query and asserts prediction matches actual host type

### Step 5: Wire into concept_selection.py
- Add optional parameter: `empirical_weights: Optional[dict[str, float]] = None`
- If provided, blend: `final = (1 - alpha) * composite + alpha * empirical_probability`
- Default alpha = 0.3 (configurable)
- Backward compatible: if empirical_weights is None, existing behavior unchanged
- Tests: add 3-4 tests to test_concept_selection.py for empirical integration

### Step 6: Export new symbols
- Add to __init__.py: concept_probability_matrix, concept_decision_tree
- Add benchmarks import block in __init__.py

## Acceptance Criteria
- [ ] All existing 27 benchmark tests still pass
- [ ] All existing 38+ concept_selection tests still pass
- [ ] New TestConceptProbabilityMatrix: 7+ tests pass
- [ ] New TestConceptDecisionTree: 8+ tests pass
- [ ] 4 of 6 case study validations pass (2 skipped for Norwegian data)
- [ ] concept_selection() backward-compatible (no param = same behavior)
- [ ] Probabilities sum to 1.0 per depth band (within float tolerance)
- [ ] Decision tree returns valid concept type strings
- [ ] No hardcoded concept lists — all derived from project data

## Cross-Review Requirements (Hard-Stop Policy)
- After implementation: request Codex cross-review
- Codex must APPROVE before merge
- Focus areas for review:
  1. Probability calculations (floating-point edge cases)
  2. Decision tree logic (edge cases at band boundaries)
  3. Backward compatibility of concept_selection.py changes
  4. Test fixture data correctness

## Verification Commands
cd digitalmodel && uv run python -m pytest tests/field_development/test_benchmarks.py -v
cd digitalmodel && uv run python -m pytest tests/field_development/test_concept_selection.py -v
cd digitalmodel && uv run python -m pytest tests/field_development/ -v --tb=short
```

---

## 6. Architecture Notes

### Probability Matrix Design

The `concept_probability_matrix()` function is a thin wrapper over `concept_benchmark_bands()`:

```
concept_benchmark_bands() returns:     concept_probability_matrix() returns:
{"800-1500m": {"TLP": 2, "Semi": 1}}  {"800-1500m": {"TLP": 0.667, "Semi": 0.333}}
```

This keeps the existing function untouched and adds a normalized view.

### Decision Tree Design

NOT a machine learning decision tree. With only 10 GoM fields, statistical learning would overfit. Instead, a rule-based tree that:
1. Uses empirical band probabilities as prior
2. Adjusts based on reservoir size and distance heuristics
3. Is fully deterministic and explainable
4. Improves automatically as more projects are added to the dataset

### Empirical Integration Design

The existing `concept_selection()` uses a 4-factor weighted composite (depth 40%, reservoir 30%, distance 20%, fluid 10%). The empirical weighting from `concept_probability_matrix()` becomes a 5th factor that can be blended via:

```python
empirical_score = probability_for_this_host_in_this_depth_band * 100
final = (1 - alpha) * analytical_composite + alpha * empirical_score
```

Where alpha defaults to 0.0 (no change) and can be set to 0.3 for moderate empirical influence.

---

## 7. Final Recommendation

### **READY AFTER LABEL UPDATE**

**Rationale:**
- The scaffold (#1861) is complete and tested (27 passing tests)
- The target files (`benchmarks.py`, `concept_selection.py`) are well-structured and ready for extension
- The implementation delta is clearly defined with 5 concrete steps
- The TDD test plan covers all scope items
- 4 of 6 case study validations are immediately possible with existing data

**Required before implementation:**
1. Add `status:plan-review` label to issue #2053
2. User reviews this plan and approves
3. Add `status:plan-approved` label
4. Then implementation can proceed following the TDD execution plan above

**Open question for issue refinement:**
- Solveig and Sverdrup validation requires Norwegian NCS data not in current SubseaIQ dataset. Should the SubseaIQ scraping issue be completed first, or should these 2 validations be deferred to a follow-up issue?

---

*Dossier generated 2026-04-09 by overnight planning terminal 10.*
*Repo paths verified: benchmarks.py (241 lines), concept_selection.py (393 lines), test_benchmarks.py (417 lines).*
