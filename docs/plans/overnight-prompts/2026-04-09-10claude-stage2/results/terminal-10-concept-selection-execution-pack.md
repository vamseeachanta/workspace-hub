# Execution Pack: Concept Selection Probability Matrix & Decision Tree

## 1. Issue Metadata

| Field | Value |
|-------|-------|
| Issue | #2053 |
| Title | feat(field-dev): concept selection probability matrix and decision tree from SubseaIQ benchmarks |
| Labels | `enhancement`, `priority:high`, `cat:engineering`, `agent:claude` |
| State | OPEN |
| Gate labels | **None** (missing `status:plan-review` and `status:plan-approved`) |
| Depends on | #1861 (scaffold -- DONE, commits `aaf90c8e`, `526e2352`) |
| Depends on | SubseaIQ Norwegian NCS scraping issue -- NOT YET AVAILABLE |
| Stage-1 dossier | `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-10-concept-selection-matrix.md` |
| Stage-2 date | 2026-04-09 |

---

## 2. Fresh Status Check Since Stage-1 Dossier

The stage-1 dossier (written 2026-04-09 ~overnight) declared all 5 scope items as "NOT STARTED". This is now **stale**. Commit `77b47195` (`feat(benchmarks): add validate_against_cases and dedicated probability tests (#2053)`, 2026-04-09 18:05) landed significant implementation work. Here is the corrected delta:

### 2.1 Scope Item Status (Updated)

| # | Scope Item | Dossier Claim | Actual Status | Evidence |
|---|-----------|---------------|---------------|----------|
| 1 | Extract concept_type + water_depth + production_rate correlations | NOT STARTED | **STILL NOT STARTED** | `SubseaProject` dataclass at `benchmarks.py:59-75` still lacks `production_rate_bopd` field. No correlation function exists. |
| 2 | Build decision tree: (water_depth, reservoir_size, distance_to_infra) -> concept type | NOT STARTED | **DONE** | `predict_concept_type()` at `benchmarks.py:282-426`. Returns `ConceptPrediction` dataclass (benchmarks.py:78-97). Rule-based, not ML. |
| 3 | Generate probability matrix by depth band | NOT STARTED | **DONE** | `concept_probability_matrix()` at `benchmarks.py:231-269`. Normalises `concept_benchmark_bands()` counts to 0.0-1.0 fractions. |
| 4 | Validate against 6 case studies | NOT STARTED | **PARTIALLY DONE** | `validate_against_cases()` at `benchmarks.py:433-528`. 15 GoM fields in `CASE_STUDY_RECORDS` fixture (test_benchmarks.py:671-704). **Missing**: Norwegian fields Solveig and Sverdrup (data dependency). |
| 5 | Wire into concept_selection.py as empirical weighting factor | NOT STARTED | **DONE** | `empirical_weights` parameter at `concept_selection.py:288`. Convenience wrapper `concept_selection_with_benchmarks()` at `concept_selection.py:468-525`. |

### 2.2 File Line Count Drift

| File | Dossier Claimed | Actual Now | Delta |
|------|----------------|------------|-------|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | 241 | 572 | +331 |
| `digitalmodel/src/digitalmodel/field_development/concept_selection.py` | 393 | 525 | +132 |
| `digitalmodel/tests/field_development/test_benchmarks.py` | 417 | 763 | +346 |
| `digitalmodel/src/digitalmodel/field_development/__init__.py` | 59 | 93 | +34 |
| `data/field-development/subseaiq-scan-latest.json` | 113 | 112 | -1 |

**New file not in dossier**: `digitalmodel/tests/field_development/test_concept_probability.py` (408 lines) -- dedicated probability test suite.

### 2.3 New Exports (Already Wired)

`__init__.py` already exports all #2053 symbols:
- `ConceptPrediction`, `concept_probability_matrix`, `predict_concept_type`, `validate_against_cases`
- `concept_selection_with_benchmarks`
- `DEPTH_BANDS`, `SubseaProject`, `load_projects`, `concept_benchmark_bands`

### 2.4 Test Coverage Added Since Dossier

| Test Class | File | Tests | Scope Item |
|-----------|------|-------|------------|
| `TestConceptProbabilityMatrix` | `test_benchmarks.py:471-539` | 9 | #3 (matrix) |
| `TestPredictConceptType` | `test_benchmarks.py:546-663` | 12 | #2 (decision tree) |
| `TestCaseStudyValidation` | `test_benchmarks.py:707-763` | 5 | #4 (case studies) |
| `TestEmpiricalWeights` | `test_concept_selection.py:434+` | 5+ | #5 (integration) |
| `TestConceptSelectionWithBenchmarks` | `test_concept_selection.py:522+` | 4+ | #5 (convenience wrapper) |
| Dedicated probability suite | `test_concept_probability.py` | ~408 lines | #3 (extended) |

---

## 3. Minimal Plan-Review Packet

### 3.1 What's Done (4 of 5 scope items)

Scope items 2, 3, 4 (partial), and 5 are implemented and tested. The core engineering is complete:

- **Probability matrix**: `concept_probability_matrix()` converts band counts to normalised fractions. Sums to 1.0 per band. Empty bands return `{}`.
- **Decision tree**: `predict_concept_type()` is a rule-based predictor (not ML). Uses empirical probabilities as prior, adjusts for reservoir size (small <50 MMbbl boosts tieback, large >200 MMbbl penalises) and distance-to-infra (<15 km boosts tieback, >60 km penalises).
- **Case validation**: `validate_against_cases()` runs predictions against a case study list and returns accuracy metrics. 15 GoM fields in test fixtures. 4 of the 6 issue-specified cases (Mad Dog, Appomattox, Perdido, Whale) are covered via `CASE_STUDY_RECORDS`.
- **Integration**: `concept_selection()` accepts optional `empirical_weights` dict. Alpha blend at 0.3 empirical, 0.7 analytical. Backward compatible (None = no change). `concept_selection_with_benchmarks()` is a convenience wrapper that does the full pipeline.

### 3.2 What's NOT Done (1 of 5 scope items + 1 data gap)

| Gap | Priority | Effort | Blocker? |
|-----|----------|--------|----------|
| **Scope item 1**: `production_rate_bopd` field + correlation extraction | Medium | ~1 hour | Not a blocker for items 2-5 |
| **Norwegian NCS data**: Solveig + Sverdrup case studies | Low | External dependency | Blocks 2 of 6 case study validations |

### 3.3 Risk Assessment (Updated)

| Risk | Status | Notes |
|------|--------|-------|
| 10-field dataset too small | MITIGATED | Test fixtures now use 15 GoM fields + 28 synthetic records |
| Decision tree overfits to GoM | ACKNOWLEDGED | Code is data-driven; accuracy improves with more data |
| Empirical weighting breaks existing tests | MITIGATED | `empirical_weights=None` is default; dedicated tests exist |
| No cross-review | STILL OPEN | Required by `cat:engineering` Hard-Stop Policy |
| Tests not verified running | OPEN | Implementation landed but test suite status unconfirmed |

---

## 4. Issue Refinement Recommendations

### 4.1 Suggested Label Updates

```
# Add plan-review label (gates implementation review)
gh issue edit 2053 --add-label "status:plan-review"
```

### 4.2 Suggested Scope Adjustments

1. **Split scope item 1** into a follow-up issue. The `production_rate_bopd` field and correlation extraction is independent of the probability matrix and decision tree. Items 2-5 are functional without it.

2. **Defer Norwegian validation** to a follow-up issue or mark as blocked on SubseaIQ NCS scraping. Document the 2 skipped case studies explicitly in the issue body.

3. **Add acceptance criteria to issue body** reflecting what's already implemented:
   - `concept_probability_matrix()` returns normalised probabilities per depth band
   - `predict_concept_type()` returns `ConceptPrediction` with rationale
   - `validate_against_cases()` validates against GoM case studies
   - `concept_selection_with_benchmarks()` integrates with existing concept selection
   - All existing tests pass (27 benchmark + 38 concept_selection)

### 4.3 Suggested Issue Body Checkbox Updates

```markdown
## Scope
- [ ] Extract concept_type + water_depth + production_rate correlations (DEFERRED: needs `production_rate_bopd` field)
- [x] Build decision tree: given (water_depth, reservoir_size, distance_to_infra) -> predicted concept type
- [x] Generate concept selection probability matrix by water depth band
- [~] Validate against 6 case studies (4/6 GoM done; 2 Norwegian blocked on NCS data)
- [x] Wire into existing `concept_selection.py` as an empirical weighting factor
```

---

## 5. Operator Command Pack

### 5.1 Verify Tests Pass (Pre-Requisite)

```bash
# Run all benchmark tests (existing + new #2053 tests)
git -C /mnt/local-analysis/workspace-hub/digitalmodel stash list && \
  uv run --directory /mnt/local-analysis/workspace-hub/digitalmodel \
    python -m pytest tests/field_development/test_benchmarks.py -v --tb=short

# Run dedicated probability test suite
uv run --directory /mnt/local-analysis/workspace-hub/digitalmodel \
  python -m pytest tests/field_development/test_concept_probability.py -v --tb=short

# Run concept selection tests (empirical_weights + convenience wrapper)
uv run --directory /mnt/local-analysis/workspace-hub/digitalmodel \
  python -m pytest tests/field_development/test_concept_selection.py -v --tb=short -k "empirical or benchmark"

# Run full field_development suite for regression
uv run --directory /mnt/local-analysis/workspace-hub/digitalmodel \
  python -m pytest tests/field_development/ -v --tb=short
```

### 5.2 Gate Label Commands

```bash
# Step 1: Add plan-review label (post this execution pack as comment)
gh issue edit 2053 --add-label "status:plan-review"

# Step 2: Post plan summary as issue comment
gh issue comment 2053 --body "$(cat <<'EOF'
## Plan Review Summary (Stage-2 Execution Pack)

**Status**: 4 of 5 scope items implemented and tested (commit `77b47195`).

### Done:
- `concept_probability_matrix()` — normalised probabilities per depth band
- `predict_concept_type()` — rule-based decision tree with `ConceptPrediction` return
- `validate_against_cases()` — GoM case study validation (15 fields)
- `concept_selection_with_benchmarks()` — empirical weighting integration

### Remaining:
- Scope item 1 (`production_rate_bopd` correlations) — recommend split to follow-up
- Norwegian NCS case studies (Solveig, Sverdrup) — blocked on data dependency

### Test coverage:
- 9 probability matrix tests, 12 decision tree tests, 5 case study tests
- 5+ empirical weights tests, 4+ convenience wrapper tests
- 408-line dedicated probability test file

### Key files:
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py` (572 lines)
- `digitalmodel/src/digitalmodel/field_development/concept_selection.py` (525 lines)
- `digitalmodel/tests/field_development/test_benchmarks.py` (763 lines)

**Recommendation**: Run full test suite, then approve if green. Request Codex cross-review per `cat:engineering` policy.
EOF
)"

# Step 3: After user approval, add plan-approved label
gh issue edit 2053 --add-label "status:plan-approved"

# Step 4: After implementation finalization, request cross-review
# (Only after tests confirmed green and production_rate_bopd decision made)
```

### 5.3 Optional: Create Follow-Up Issue for production_rate_bopd

```bash
gh issue create \
  --title "feat(field-dev): add production_rate_bopd to SubseaProject and extract correlations" \
  --label "enhancement,cat:engineering,agent:claude" \
  --body "$(cat <<'EOF'
## Context
Follow-up to #2053 scope item 1. The `SubseaProject` dataclass in `benchmarks.py` currently lacks a `production_rate_bopd` field. The `GoMField` dataclass in `subsea_bridge.py` has `capacity_bopd` but there's no bridge between the two data models.

## Scope
- [ ] Add `production_rate_bopd: Optional[float]` to `SubseaProject` dataclass
- [ ] Update `load_projects()` to parse `production_rate_bopd` via `_opt_float()`
- [ ] Implement `_extract_correlations(projects) -> dict` for concept_type + water_depth + production_rate
- [ ] Bridge `GoMField.capacity_bopd` to `SubseaProject.production_rate_bopd` in subsea_bridge

## Target Files
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py` (extend SubseaProject)
- `digitalmodel/tests/field_development/test_benchmarks.py` (extend TestLoadProjects)

## Depends On
- #2053 (probability matrix — done)
- #1861 (scaffold — done)
EOF
)"
```

---

## 6. Self-Contained Future Implementation Prompt

```
You are completing the remaining work on GitHub issue #2053: feat(field-dev): concept selection probability matrix and decision tree from SubseaIQ benchmarks.

## Current State (as of 2026-04-09)

4 of 5 scope items are DONE. Commit 77b47195 added the core implementation. Key functions exist and are tested:
- concept_probability_matrix() at benchmarks.py:231-269
- predict_concept_type() at benchmarks.py:282-426
- validate_against_cases() at benchmarks.py:433-528
- concept_selection_with_benchmarks() at concept_selection.py:468-525
- empirical_weights parameter at concept_selection.py:288

## What Remains

### Priority 1: Verify test suite
Run all tests and fix any failures:
```
uv run --directory digitalmodel python -m pytest tests/field_development/ -v --tb=short
```

### Priority 2: Decide on production_rate_bopd
Scope item 1 asks for concept_type + water_depth + production_rate correlations. The SubseaProject dataclass at benchmarks.py:59-75 lacks production_rate_bopd. Two options:
- Option A: Add the field now (~30 min). Add `production_rate_bopd: Optional[float] = None` at line 75, update load_projects, add _extract_correlations().
- Option B: Split to a follow-up issue (see operator command pack).

### Priority 3: Norwegian case studies
Solveig and Sverdrup validation requires NCS data not in `data/field-development/subseaiq-scan-latest.json`. Options:
- Add pytest.skip markers for these 2 cases
- Or add hardcoded Norwegian reference data alongside GoM CASE_STUDY_RECORDS

### Priority 4: Cross-review gate
Per cat:engineering Hard-Stop Policy, request Codex cross-review before merge. Focus areas:
1. Float precision in probability calculations (concept_probability_matrix)
2. Decision tree boundary conditions (predict_concept_type depth band edges)
3. Backward compatibility of empirical_weights parameter in concept_selection
4. CASE_STUDY_RECORDS data accuracy (water depths, concept types)

### Priority 5: Close the issue
```
gh issue edit 2053 --add-label "status:done"
gh issue comment 2053 --body "Implemented in 77b47195. Scope item 1 (production_rate_bopd) split to follow-up issue."
```

## Key Files
- digitalmodel/src/digitalmodel/field_development/benchmarks.py (572 lines)
- digitalmodel/src/digitalmodel/field_development/concept_selection.py (525 lines)
- digitalmodel/tests/field_development/test_benchmarks.py (763 lines)
- digitalmodel/tests/field_development/test_concept_probability.py (408 lines)
- digitalmodel/tests/field_development/test_concept_selection.py (empirical tests at line 434+)
- digitalmodel/src/digitalmodel/field_development/__init__.py (93 lines, exports wired)
- data/field-development/subseaiq-scan-latest.json (112 lines, 10 GoM fields)

## Do NOT
- Modify existing passing tests without justification
- Change the ConceptPrediction dataclass interface
- Remove the backward-compatible default (empirical_weights=None)
- Self-approve: this requires user review and status:plan-approved label
```

---

## 7. Morning Handoff

**For the operator reviewing this at session start:**

1. **The big surprise**: The stage-1 dossier was already stale when this pack was written. Commit `77b47195` implemented 4 of 5 scope items. The overnight planner and the overnight implementer overlapped.

2. **Immediate action**: Run the test suite (commands in section 5.1). If green, the issue is ~90% done.

3. **Decision needed**: Should scope item 1 (`production_rate_bopd` correlations) be completed in-issue or split to a follow-up? The recommendation is to split -- it's independent and the core value (probability matrix + decision tree + integration) is already delivered.

4. **Gate compliance**: The `cat:engineering` label requires cross-review. After test verification, post the plan-review comment (section 5.2), get user approval, then request Codex cross-review.

5. **Key repo paths to inspect**:
   - `digitalmodel/src/digitalmodel/field_development/benchmarks.py` -- all new functions
   - `digitalmodel/tests/field_development/test_benchmarks.py` -- all new test classes
   - `digitalmodel/src/digitalmodel/field_development/concept_selection.py:468-525` -- integration wrapper

---

## 8. Final Recommendation

**NEARLY COMPLETE -- VERIFY AND CLOSE**: 4 of 5 scope items implemented with comprehensive tests. Run `uv run --directory digitalmodel python -m pytest tests/field_development/ -v` to confirm green, split scope item 1 to follow-up, post plan-review comment, and request Codex cross-review per `cat:engineering` gate policy. Issue can proceed to `status:plan-review` immediately.
