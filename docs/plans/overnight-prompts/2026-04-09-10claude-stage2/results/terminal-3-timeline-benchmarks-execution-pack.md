# Execution Pack: Issue #2060 — Project Timeline Benchmarks from SubseaIQ Milestone Data

| Field | Value |
|-------|-------|
| Issue | [#2060](https://github.com/vamseeachanta/workspace-hub/issues/2060) |
| Title | feat(field-dev): project timeline benchmarks from SubseaIQ milestone data |
| Labels | enhancement, cat:engineering, agent:claude |
| Depends on | #1861 (scaffold — done, commit `aaf90c8e`), #2053 (probability matrix — done) |
| Stage-1 dossier | `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md` |
| Stage-2 date | 2026-04-09 |

---

## 1. Fresh Status Check (since stage-1 dossier)

### 1.1 File-Level Delta

| File | Dossier size | Current size | Change since dossier |
|------|-------------|-------------|---------------------|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | 240 lines | **572 lines** | +332: #2053 added `ConceptPrediction`, `concept_probability_matrix`, `predict_concept_type`, `validate_against_cases` |
| `digitalmodel/tests/field_development/test_benchmarks.py` | 417 lines | **763 lines** | +346: 3 new test classes for #2053 features |
| `worldenergydata/subseaiq/analytics/normalize.py` | 130 lines | **129 lines** | Unchanged |
| `digitalmodel/src/digitalmodel/field_development/__init__.py` | "not re-exported" | **93 lines, fully re-exported** | Dossier was stale — benchmarks now fully wired into `__init__.py` with 8 exports |

### 1.2 Current Public API Surface (benchmarks.py)

| Function/Class | Line | Added by |
|----------------|------|----------|
| `SubseaProject` | 60 | #1861 |
| `ConceptPrediction` | 79 | #2053 |
| `load_projects()` | 104 | #1861 |
| `concept_benchmark_bands()` | 149 | #1861 |
| `subsea_architecture_stats()` | 184 | #1861 |
| `concept_probability_matrix()` | 231 | #2053 |
| `predict_concept_type()` | 282 | #2053 |
| `validate_against_cases()` | 433 | #2053 |

### 1.3 Corrected Line References

| Item | Dossier ref | Actual ref |
|------|-------------|------------|
| `SubseaProject` fields | lines 53-69 | **lines 59-75** |
| `load_projects()` parsing | lines 76-113 | **lines 104-142** |
| `_classify_depth()` | line 203 | **line 535** |
| `_describe()` | line 211 | **line 543** |
| `_opt_float()` | line 223 | **line 555** |
| `_opt_int()` | line 233 | **line 565** |
| `_FIELD_ALIASES` in normalize.py | lines 31-54 | **lines 31-54** (unchanged) |
| `_safe_int` conversion block | lines 86-90 | **line 88** |

### 1.4 Dossier Staleness Summary

| Claim | Status |
|-------|--------|
| "Zero timeline fields exist" | **Still true** — confirmed via grep |
| "benchmarks NOT re-exported from `__init__.py`" | **STALE** — now fully re-exported (8 symbols) |
| "benchmarks.py stays under 500 lines" acceptance criterion | **Already violated** — file is 572 lines |
| "No other terminal targets benchmarks.py" | **Still true** — no contention in this batch |
| File line counts | **All stale** — corrected above |
| Normalizer state | **Accurate** — 10 canonical fields, zero timeline aliases |

### 1.5 Label State

| Label | Present? |
|-------|----------|
| `status:plan-review` | **No** |
| `status:plan-approved` | **No** |
| `enhancement` | Yes |
| `cat:engineering` | Yes |
| `agent:claude` | Yes |

---

## 2. Minimal Plan-Review Packet

### 2.1 Scope Confirmation

Seven behaviors to implement (unchanged from dossier):

| # | Behavior | Complexity |
|---|----------|-----------|
| B1 | 4 new `Optional[int]` fields on `SubseaProject` (year_concept, year_feed, year_fid, year_first_oil) | Low |
| B2 | `load_projects()` parses 4 timeline fields via `_opt_int()` | Low |
| B3 | `timeline_duration_stats()` — inter-phase durations with descriptive stats | Medium |
| B4 | `duration_stats_by_concept_type()` — stats grouped by concept_type | Medium |
| B5 | `schedule_distributions()` — P10/P50/P90 percentile distributions | Medium |
| B6 | 4 new entries in `_FIELD_ALIASES` for timeline fields | Low |
| B7 | Type conversion for timeline fields in `normalize_project()` | Low |

### 2.2 Files That Must Change

| # | File | Change type | Est. delta |
|---|------|------------|-----------|
| F1 | `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | Extend dataclass, extend `load_projects`, add `_percentiles` helper, add 3 new public functions | +120-150 lines |
| F2 | `digitalmodel/tests/field_development/test_benchmarks.py` | Extend fixtures, add 5 new test classes (~28 tests) | +150-180 lines |
| F3 | `worldenergydata/subseaiq/analytics/normalize.py` | Add 4 entries to `_FIELD_ALIASES`, extend `_safe_int` conversion | +25-35 lines |
| F4 | `digitalmodel/src/digitalmodel/field_development/__init__.py` | Add 3 new function imports + `__all__` entries | +6-8 lines |

### 2.3 Design Decisions (pre-resolved)

| Decision | Resolution | Rationale |
|----------|-----------|-----------|
| Percentile computation | Pure-Python `sorted()` + index math | Module has zero numpy usage; keep dependency-free |
| Complexity proxy | `concept_type` + water-depth band (2D key) | Matches existing `_classify_depth()` pattern |
| Year type | `Optional[int]` | SubseaIQ granularity is year-level |
| Duration type | Integer years | Consistent with year-level inputs |
| File size concern | Accept growth to ~720 lines OR extract `timeline.py` | See refinement rec #3 below |

### 2.4 Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| benchmarks.py exceeds 500-line guideline | **Medium** | Already at 572; timeline adds ~130 more. Accept for now or extract to `timeline.py` (operator decides) |
| SubseaIQ field names for timeline data unknown | **Low** | Alias list is educated guesses — refine after first real scrape |
| Pure-Python percentile edge cases | **Low** | Add explicit tests for 1-element, 2-element, and identical-value cases |
| Negative durations from bad data | **Low** | Filter out with explicit skip; pattern already used in existing code |

---

## 3. Issue Refinement Recommendations

### Rec 1: Update issue checklist to include `__init__.py`

The issue body lists 3 target files. A 4th file (`__init__.py`) must also be updated to wire new timeline functions into the public API.

### Rec 2: Remove "benchmarks.py stays under 500 lines" criterion

The file crossed 500 lines when #2053 landed. Either:
- **(a)** Accept the growth (recommended for this issue — extraction is a separate refactor)
- **(b)** Extract timeline functions to `digitalmodel/src/digitalmodel/field_development/timeline.py` as part of this issue

### Rec 3: Add `__init__.py` re-export checklist item

Add to issue body:
```
- [ ] Re-export timeline_duration_stats, duration_stats_by_concept_type, schedule_distributions from __init__.py
```

### Rec 4: Clarify SubseaIQ scrape field names

The alias list in the dossier is educated guesses. When real SubseaIQ scrape data with milestone dates becomes available, validate the column names and update `_FIELD_ALIASES` accordingly. Consider adding an issue comment noting which aliases are confirmed vs speculative.

---

## 4. Operator Command Pack

### 4.1 Apply `status:plan-review` label

```bash
gh issue edit 2060 --add-label "status:plan-review"
```

### 4.2 Post plan-review comment on issue

```bash
gh issue comment 2060 --body "$(cat <<'EOF'
## Plan Review — Stage-2 Execution Pack

**Dossier**: `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md`
**Execution pack**: `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-3-timeline-benchmarks-execution-pack.md`

### Scope
- 4 timeline fields on `SubseaProject` + load/parse
- 3 new public functions: `timeline_duration_stats`, `duration_stats_by_concept_type`, `schedule_distributions`
- 4 normalizer alias entries + int conversion
- ~28 new tests across 5 test classes
- `__init__.py` re-export update

### Files (4)
1. `digitalmodel/src/digitalmodel/field_development/benchmarks.py` (+130 lines)
2. `digitalmodel/tests/field_development/test_benchmarks.py` (+160 lines)
3. `worldenergydata/subseaiq/analytics/normalize.py` (+30 lines)
4. `digitalmodel/src/digitalmodel/field_development/__init__.py` (+7 lines)

### Freshness note
Stage-1 dossier line numbers are stale (benchmarks.py grew 240→572 from #2053). Execution pack has corrected references.

### Decision needed
benchmarks.py is 572 lines. Adding timeline code pushes to ~700. Accept growth or extract `timeline.py`?

### Recommendation
Ready after `status:plan-approved`. Pure addition, no contention with other terminals.
EOF
)"
```

### 4.3 Approve and begin (after review)

```bash
gh issue edit 2060 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

### 4.4 Pre-implementation verification commands

```bash
# Verify target files exist and check sizes
wc -l digitalmodel/src/digitalmodel/field_development/benchmarks.py \
     digitalmodel/tests/field_development/test_benchmarks.py \
     worldenergydata/subseaiq/analytics/normalize.py \
     digitalmodel/src/digitalmodel/field_development/__init__.py

# Confirm zero timeline code exists yet
grep -rn "year_concept\|year_feed\|year_fid\|year_first_oil\|timeline_duration" \
  digitalmodel/src/digitalmodel/field_development/ \
  worldenergydata/subseaiq/analytics/

# Run existing tests to confirm green baseline
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -v --tb=short
```

---

## 5. Self-Contained Implementation Prompt for Claude

```
You are implementing GitHub issue #2060: "feat(field-dev): project timeline benchmarks from SubseaIQ milestone data".

## Context
- Repo: workspace-hub (working directory: /mnt/local-analysis/workspace-hub)
- This extends the SubseaIQ benchmark bridge (issue #1861 scaffold, #2053 probability matrix — both done).
- benchmarks.py is 572 lines with 8 public functions. You are adding 3 new public functions + extending the dataclass.
- Use TDD: write failing tests first, then implement.
- Use `uv run` for all Python commands.
- The stage-1 dossier at `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md` has full design details. Reference it for fixture data, test specs, and function signatures. NOTE: Line numbers in the dossier are stale — use the corrected references below.

## Corrected Line References (as of 2026-04-09)
- SubseaProject dataclass: benchmarks.py lines 59-75
- load_projects(): benchmarks.py lines 104-142
- _describe(): benchmarks.py line 543
- _opt_int(): benchmarks.py line 565
- _FIELD_ALIASES: normalize.py lines 31-54
- _safe_int conversion: normalize.py line 88

## Files to Modify (4 files)
1. `digitalmodel/src/digitalmodel/field_development/benchmarks.py` — extend dataclass, extend load_projects, add _percentiles helper, add 3 public functions
2. `digitalmodel/tests/field_development/test_benchmarks.py` — extend fixtures, add 5 test classes (~28 tests)
3. `worldenergydata/subseaiq/analytics/normalize.py` — add 4 entries to _FIELD_ALIASES, extend _safe_int block
4. `digitalmodel/src/digitalmodel/field_development/__init__.py` — add imports for timeline_duration_stats, duration_stats_by_concept_type, schedule_distributions to both imports and __all__

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

### Step 3: Confirm tests fail
```bash
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -k "Timeline or Duration or Schedule or NormalizeTimeline" -v
```

### Step 4: Implement in benchmarks.py
- Add 4 Optional[int] fields to SubseaProject after line 75: year_concept, year_feed, year_fid, year_first_oil
- Extend load_projects() at line 128-140: add 4 _opt_int() calls for new fields
- Add _percentiles(values, quantiles) helper after _describe() — pure Python, no numpy
- Add timeline_duration_stats(projects) public function
- Add duration_stats_by_concept_type(projects) public function
- Add schedule_distributions(projects) public function

### Step 5: Implement in normalize.py
- Add 4 entries to _FIELD_ALIASES (after line 54) for year_concept, year_feed, year_fid, year_first_oil
- Add timeline field names to _safe_int conversion tuple at line 88

### Step 6: Update __init__.py
- Add timeline_duration_stats, duration_stats_by_concept_type, schedule_distributions to imports from .benchmarks (after line 44)
- Add same 3 names to __all__ list (after line 70)

### Step 7: Run full test suite
```bash
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -v --tb=short
cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short
```

## Acceptance Criteria
- [ ] All 27+ existing tests still pass (regression)
- [ ] All ~28 new timeline tests pass
- [ ] P10 <= P50 <= P90 invariant holds for all distributions
- [ ] Sparse data (missing timeline fields) handled gracefully — no crashes
- [ ] Junk values ("TBD", "N/A", "") in timeline fields → None
- [ ] Negative computed durations (year_fid < year_concept) excluded from stats
- [ ] normalize_project handles SubseaIQ timeline field aliases
- [ ] No new dependencies added (pure Python percentiles)
- [ ] New functions re-exported from __init__.py
- [ ] File header ABOUTME comments updated to mention #2060

## Cross-Review Requirements
- After implementation, run: `cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short`
- Verify no new imports beyond stdlib (dataclasses, typing)
- Verify _percentiles matches numpy.percentile behavior for small samples
- Verify normalize.py aliases cover likely SubseaIQ scrape column names
```

---

## 6. Morning Handoff

**For the operator (Vamsee):**

1. This execution pack corrects several stale details from the stage-1 dossier (line numbers, file sizes, `__init__.py` re-export status).
2. The core implementation delta is unchanged — zero timeline code exists, all 7 behaviors are still needed.
3. **Decision needed**: benchmarks.py is already 572 lines (over the 500-line guideline). Adding timeline code pushes to ~700. Accept the growth now and extract later, or split `timeline.py` as part of this issue?
4. No `status:plan-review` or `status:plan-approved` labels exist. Run the operator commands in Section 4 to advance the issue through the gate.
5. No contention risk — no other terminal in this batch touches these files.
6. Estimated scope: ~330 new lines across 4 files. Medium complexity, self-contained, no cross-module dependencies.

---

## 7. Final Recommendation

**READY AFTER LABEL UPDATE** — Issue #2060 is well-scoped, has zero existing implementation overlap, and builds cleanly on the #1861/#2053 foundation. Run `gh issue edit 2060 --add-label "status:plan-review"` to begin the gate sequence, then `--add-label "status:plan-approved"` after review. The implementation prompt in Section 5 is self-contained and can be dispatched to any Claude terminal.
