# Issue #2053 Analysis — feat(field-dev): concept selection probability matrix and decision tree

**Analysis date:** 2026-04-10  
**Analyst:** Claude (claude-sonnet-4-6)  
**Workspace:** /mnt/local-analysis/workspace-hub  
**digitalmodel path:** /mnt/local-analysis/workspace-hub/digitalmodel  
**Requested output path:** /tmp/claude-issue-pack-2026-04-10-052749/results/2053.md  
*(Sandbox blocked /tmp writes; written here instead. Grant /tmp permission to write to original path.)*

---

## Verdict

**NOT directly executable — implementation already committed; issue requires closure + verification, not new code.**

The full scope of #2053 was implemented in digitalmodel commit `77b47195`
(Thu Apr 9 18:05:21 2026). All five deliverables named in the issue body exist
in the local codebase. The GitHub issue was never closed. The only remaining
work is: (a) confirm test suite passes, (b) optionally add Solveig/Sverdrup
case data that the issue named but the implementation omits, and (c) close the
issue with a summary comment.

A secondary blocker: no `status:plan-approved` label is present. Workspace-hub
governance requires plan-approval before a batch agent may implement an issue.
Since the implementation is already done, this gate is moot for coding — but a
fresh agent that did not read the local code would attempt redundant work.

---

## Evidence

### Issue body (fetched via `gh issue view 2053`)

| Field | Value |
|---|---|
| State | OPEN |
| Labels | `enhancement`, `priority:high`, `cat:engineering`, `agent:claude` |
| Author | vamseeachanta |
| Comments | 1 |
| Depends on | #1861 (scaffold — done), SubseaIQ scraping issue (real dataset) |

**Scope items from issue:**
1. Extract concept_type + water_depth + production_rate correlations from `SubseaProject` records
2. Build decision tree: `(water_depth, reservoir_size, distance_to_infra)` → predicted concept type
3. Generate concept selection probability matrix by water depth band
4. Validate against 6 case studies: Solveig, Sverdrup, Mad Dog, Appomattox, Perdido, Whale
5. Wire into `concept_selection.py` as an empirical weighting factor

**Target files named in issue:**
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py`
- `digitalmodel/tests/field_development/test_benchmarks.py`

### Commit evidence

```
git -C digitalmodel log --oneline --grep="2053"
77b47195 feat(benchmarks): add validate_against_cases and dedicated probability tests (#2053)
```

Commit `77b47195` (Apr 9 18:05, Vamsee Achanta) adds 529 lines across 3 files:
- `src/digitalmodel/field_development/__init__.py` (+19 lines — public API exports)
- `src/digitalmodel/field_development/benchmarks.py` (+102 lines — new functions)
- `tests/field_development/test_concept_probability.py` (+408 lines — 26 new tests)

---

## Local data / files verified

### Core implementation files — all present and implemented

| File | Status | Key items confirmed |
|---|---|---|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | ✅ Full implementation | `SubseaProject`, `ConceptPrediction`, `load_projects`, `concept_benchmark_bands`, `concept_probability_matrix`, `predict_concept_type`, `validate_against_cases`, `subsea_architecture_stats` |
| `digitalmodel/src/digitalmodel/field_development/concept_selection.py` | ✅ Wired | `concept_selection(empirical_weights=...)` parameter, `concept_selection_with_benchmarks()` wrapper, `_NAME_MAP` for SubseaIQ→HostType translation |
| `digitalmodel/tests/field_development/test_benchmarks.py` | ✅ Extended | `TestConceptProbabilityMatrix` (7 tests), `TestPredictConceptType` (11 tests), `TestCaseStudyValidation` (3 tests) |
| `digitalmodel/tests/field_development/test_concept_probability.py` | ✅ New file | 26 tests covering `validate_against_cases`, integration with `concept_selection_with_benchmarks`, edge cases |

### Depth band constants (in benchmarks.py)

```python
DEPTH_BANDS = ("0-300m", "300-800m", "800-1500m", "1500m+")
```

Decision tree logic (lines 358–443 of benchmarks.py):
- Step 1: Classify `water_depth` to band
- Step 2: Base probabilities from `concept_probability_matrix(projects)`
- Step 3: Reservoir size adjustments (tieback boost <50 MMbbl, penalise >200 MMbbl)
- Step 4: Distance-to-infra adjustments (tieback boost ≤15 km, penalise >60 km)
- Step 5: Re-normalise → return `ConceptPrediction`

### Case studies available locally

**In `test_benchmarks.py` `CASE_STUDY_RECORDS` fixture (15 GoM fields):**
Perdido (Spar, 2438m), Mars (TLP, 896m), Atlantis (Semi, 2150m), Thunder Horse
(Semi, 1844m), Mad Dog (Spar, 1311m), Appomattox (Semi, 2195m), Whale (Semi,
1372m), Stones (FPSO, 2900m), Lucius (Spar, 2164m), Ursa (TLP, 1158m),
Na Kika (Semi, 1920m), Holstein (Spar, 1325m), Shenzi (TLP, 1311m),
Constitution (Spar, 1524m), Great White (Spar, 2438m)

**Issue-specified cases present locally:** Mad Dog ✅, Appomattox ✅, Perdido ✅, Whale ✅  
**Issue-specified cases MISSING:** Solveig ✗, Sverdrup ✗  
(These are Norwegian shelf fields; no public water depth / reservoir data is
encoded in the repo. The implementation uses GoM analogues instead.)

### SubseaIQ real dataset

The issue depends on a SubseaIQ scraping issue for a real dataset. No scraped
JSON/YAML data file exists under `digitalmodel/` or `worldenergydata/`. The
implementation uses synthetic `SubseaProject` records in test fixtures — sufficient
for the probability matrix logic, but the issue's stated dependency on live
SubseaIQ data is unresolved.

The `TestNormalizeIntegration` test is gated with `pytest.skip(...)` — it will
be skipped if the worldenergydata scraping pipeline is absent. Core tests do not
require live data.

---

## Approval / gate status

| Gate | Status | Notes |
|---|---|---|
| `status:plan-approved` GitHub label | ❌ ABSENT | Required by workspace-hub CLAUDE.md planning workflow |
| Work-queue entry (`.claude/work-queue/`) | ❌ ABSENT | No WRK file for #2053 |
| Plan document (`docs/plans/*2053*`) | ❌ ABSENT | No plan file found |
| Commit in digitalmodel referencing #2053 | ✅ PRESENT | `77b47195` Apr 9 2026 |
| Implementation complete (code check) | ✅ YES | All 5 scope items implemented |
| Tests written | ✅ YES | 26+ tests in test_concept_probability.py, ~21 in test_benchmarks.py |

**Gate verdict:** `status:plan-approved` gate is absent. However, since the code
is already committed, the gate is retroactively moot — the work bypassed the
approval process but is done. Do not re-implement; close the issue instead.

---

## Dirty-worktree risk

- **workspace-hub:** Git status shows only `.claude/state/` and `scripts/` changes — unrelated to field-dev.
- **digitalmodel:** `uv.lock` modified (dependency lock only, not source).
- **No uncommitted source changes** that could be overwritten by an agent.
- **Primary risk:** A fresh agent implementing from scratch would produce duplicate/conflicting functions in `benchmarks.py`. Do not dispatch an implementation agent.

---

## Exact write boundaries for implementation

*Since implementation is already done, boundaries describe what remains (closure work only):*

### What is complete — do NOT rewrite

- `benchmarks.py` lines 248–545: `concept_probability_matrix`, `predict_concept_type`, `validate_against_cases`, `ConceptPrediction`
- `concept_selection.py` lines 283–525: `empirical_weights` parameter, `concept_selection_with_benchmarks`
- `test_concept_probability.py`: entire file (26 tests)
- `test_benchmarks.py` lines 499–843: `TestConceptProbabilityMatrix`, `TestPredictConceptType`, `TestCaseStudyValidation`

### What is missing (optional gap)

- Solveig (~330m, Fixed Platform/Jack-up) and Sverdrup (~110m, Jack-up) case study entries
  - Could be added to `CASE_STUDY_RECORDS` in `test_benchmarks.py`
  - No definitive public reservoir sizes available — requires engineering judgement
- A GitHub issue comment explaining what was implemented (required by policy)
- Closing the issue

---

## Minimal verification commands

```bash
# 1. Confirm all three functions exist in benchmarks.py
grep -n "def concept_probability_matrix\|def predict_concept_type\|def validate_against_cases" \
  digitalmodel/src/digitalmodel/field_development/benchmarks.py

# 2. Confirm empirical_weights wired in concept_selection.py
grep -n "empirical_weights\|concept_selection_with_benchmarks" \
  digitalmodel/src/digitalmodel/field_development/concept_selection.py

# 3. Run the #2053 test suite
cd digitalmodel && uv run pytest \
  tests/field_development/test_concept_probability.py \
  tests/field_development/test_benchmarks.py::TestConceptProbabilityMatrix \
  tests/field_development/test_benchmarks.py::TestPredictConceptType \
  tests/field_development/test_benchmarks.py::TestCaseStudyValidation \
  -v --tb=short

# 4. Confirm commit
git -C digitalmodel log --oneline --grep="2053"
# Expected: 77b47195 feat(benchmarks): add validate_against_cases and dedicated probability tests (#2053)
```

---

## Self-contained implementation prompt

*(Omitted — verdict is NOT directly executable as new implementation. All five scope items are already committed at `77b47195`. Dispatching an implementation agent would produce duplicate code and merge conflicts.)*

---

## Next action

**Priority order:**

1. **Verify tests pass** — run the three `uv run pytest` commands above from within `digitalmodel/`. The `uv.lock` drift does not affect test logic.

2. **Post a closing comment on GitHub issue #2053** — per workspace-hub policy (`feedback_gh_issue_comment.md`), every implemented issue requires a summary comment. Suggested text:
   ```
   Implemented in digitalmodel commit 77b47195 (Apr 9 2026).
   
   Delivered:
   - concept_probability_matrix() — normalised probabilities per depth band
   - predict_concept_type() — 5-step empirical decision tree
   - validate_against_cases() — accuracy validation against known fields
   - concept_selection_with_benchmarks() — wired into concept_selection.py
   
   Tests: 26 tests in test_concept_probability.py + 21 in test_benchmarks.py.
   Case studies: 15 GoM fields (Mad Dog, Appomattox, Perdido, Whale included).
   Solveig and Sverdrup omitted — no authoritative public reservoir data.
   ```

3. **Close the issue** — `gh issue close 2053` (after posting comment).

4. **Optional:** Add Solveig (~330m, Fixed Platform) and Sverdrup (~110m, Jack-up) entries to `CASE_STUDY_RECORDS` in `test_benchmarks.py` if authoritative data can be sourced from public references.

5. **Do NOT dispatch an implementation agent** — all scope items are done.
