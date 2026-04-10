# Next-Wave Claude Execution Prompts — Stage 3, Terminal 5

Generated: 2026-04-09
Source: 10 stage-2 execution packs + stage-3 priority matrix
Pipeline: Stage 1 (dossiers) -> Stage 2 (execution packs) -> Stage 3 (synthesis) -> **Stage 4 (this file)**

---

## 1. Preconditions by Issue

Before dispatching any prompt, the operator must verify these preconditions are met.

| Issue | Precondition | Verification Command | Status Gate |
|-------|-------------|---------------------|-------------|
| #2056 | Threshold bug confirmed at `governance-checkpoints.yaml:54` | `grep 'threshold:' scripts/workflow/governance-checkpoints.yaml` | Apply `status:plan-approved` |
| #2053 | Core tests pass; production_rate_bopd split decision made | `cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py tests/field_development/test_concept_probability.py -v --tb=short` | Apply `status:plan-approved` |
| #2057 | 4 skill files exist; broken links confirmed | `for s in session-start-routine session-corpus-audit cross-review-policy comprehensive-learning-wrapper; do test -f .claude/skills/coordination/$s/SKILL.md && echo "OK: $s" \|\| echo "MISSING: $s"; done` | Apply `status:plan-approved` retroactively |
| #2063 | CSV data present; adapter pattern confirmed at `ship_data.py:150` | `wc -l worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv && head -3 digitalmodel/src/digitalmodel/drilling_riser/__init__.py` | Apply `status:plan-review` then `status:plan-approved` |
| #2059 | Construction vessels CSV present; stability module importable | `wc -l worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv && cd digitalmodel && uv run python -c "from digitalmodel.naval_architecture.floating_platform_stability import compute_gz_curve; print('OK')"` | Apply `status:plan-review` then `status:plan-approved` |
| #2054 | Economics module importable; lines 420-435 still have linear decline | `cd digitalmodel && uv run python -c "from digitalmodel.field_development.economics import EconomicsInput; print('OK')" && sed -n '420,435p' src/digitalmodel/field_development/economics.py` | Apply `status:plan-review` then `status:plan-approved` |
| #2060 | File-size policy decided (accept growth to ~700 OR extract `timeline.py`) | `wc -l digitalmodel/src/digitalmodel/field_development/benchmarks.py` | Operator decision required -> then `status:plan-approved` |
| #2062 | Issue body updated to reflect v1 scope (~138 rigs, not 2,210) | `gh issue view 2062 --repo vamseeachanta/workspace-hub --json title,body \| head -20` | Scope refinement -> then `status:plan-approved` |

---

## 2. Execution Prompts

### Prompt 1 of 7: Fix Governance Threshold Bug (#2056)

**Wave:** 1 (Quick Closes) | **Terminal:** Any | **Est. Time:** 15 min
**Parallel-safe with:** Prompts 2, 3

```
We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2056 — Session Governance Phase 2 (Runtime Hook Enforcement)
Status: Implementation ~90% complete. One threshold regression bug found in stage-2 review.

Context:
- Commit d4f46c770 introduced a regression: governance-checkpoints.yaml line 54 has
  threshold: 5000 but the documented and intended ceiling is 200 tool calls per session.
- The PreToolUse hook at .claude/hooks/session-governor-check.sh has a hardcoded
  FAST_PATH_CEILING=160 that provides partial coverage, but the governor-level 200-call
  ceiling is ineffective because the YAML says 5000.
- docs/standards/REVIEW_GATE_BYPASS_POLICY.md has stale default text that needs updating.

Tasks:
1. Fix scripts/workflow/governance-checkpoints.yaml line 54: change threshold from 5000 to 200.
2. Update docs/standards/REVIEW_GATE_BYPASS_POLICY.md to reflect the 200-call ceiling
   and reference the governor check hook.
3. Add an integration test in digitalmodel/tests/ or tests/ that reads the production
   governance-checkpoints.yaml and asserts the tool-call-ceiling threshold equals 200.
   Place the test at: tests/governance/test_checkpoints_yaml.py
4. Verify the fix: grep 'threshold:' scripts/workflow/governance-checkpoints.yaml
5. Run the new test: uv run pytest tests/governance/test_checkpoints_yaml.py -v
6. Post a gh issue comment on #2056 summarizing: bug found, fix applied, test added.
   Use: gh issue comment 2056 --repo vamseeachanta/workspace-hub --body "..."

Allowed write paths:
- scripts/workflow/governance-checkpoints.yaml
- docs/standards/REVIEW_GATE_BYPASS_POLICY.md
- tests/governance/test_checkpoints_yaml.py (NEW)
- tests/governance/__init__.py (NEW, if needed)

Negative write boundaries (DO NOT touch):
- .claude/hooks/session-governor-check.sh
- .claude/hooks/error-loop-tracker.sh
- .claude/settings.json
- Any file under digitalmodel/
- Any file under worldenergydata/

Cross-review: Not required (cat:ai-orchestration, single-line fix + test).

Verification:
  grep 'threshold: 200' scripts/workflow/governance-checkpoints.yaml
  uv run pytest tests/governance/test_checkpoints_yaml.py -v
  gh issue view 2056 --repo vamseeachanta/workspace-hub --json comments --jq '.comments[-1].body' | head -5
```

---

### Prompt 2 of 7: Verify and Close Concept Selection (#2053)

**Wave:** 1 (Quick Closes) | **Terminal:** Any | **Est. Time:** 20 min
**Parallel-safe with:** Prompts 1, 3

```
We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2053 — Concept Selection Probability Matrix & Decision Tree
Status: 4 of 5 scope items implemented in commit 77b47195. Scope item 1
(production_rate_bopd correlations) was NOT started and should be split to a follow-up.

Context:
- benchmarks.py (572 lines) contains predict_concept_type() at line 282-426 and
  concept_probability_matrix() at line 231-269. Both are implemented and tested.
- concept_selection.py (525 lines) has the integration wrapper
  concept_selection_with_benchmarks() at line 468-525.
- Test files: test_benchmarks.py (763 lines) and test_concept_probability.py (408 lines, NEW).
- Norwegian NCS fields (Solveig, Sverdrup) are data-blocked — 2 of 6 case studies.

Tasks:
1. Run the full field_development test suite:
   cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short
2. If any Norwegian case study tests fail due to missing NCS data, add pytest.skip markers
   with reason="NCS data dependency not yet available" — do NOT delete the tests.
3. Create a follow-up issue draft (do NOT create it on GitHub) capturing scope item 1:
   Title: "Add production_rate_bopd correlation to concept selection benchmarks"
   Write the draft to: docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/2053-followup-draft.md
4. Post a gh issue comment on #2053 summarizing: 4/5 scope items done, tests passing,
   scope item 1 split to follow-up, Norwegian cases deferred with skip markers.
   Use: gh issue comment 2053 --repo vamseeachanta/workspace-hub --body "..."
5. Do NOT close the issue — the operator will close after reviewing the comment.

Allowed write paths:
- digitalmodel/tests/field_development/test_benchmarks.py (pytest.skip markers only)
- digitalmodel/tests/field_development/test_concept_probability.py (pytest.skip markers only)
- docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/2053-followup-draft.md (NEW)

Negative write boundaries (DO NOT touch):
- digitalmodel/src/digitalmodel/field_development/benchmarks.py
- digitalmodel/src/digitalmodel/field_development/concept_selection.py
- Any file outside digitalmodel/tests/ and docs/plans/
- worldenergydata/

Cross-review: Request Codex cross-review per cat:engineering policy. Add a comment
noting: "Cross-review requested per engineering gate — concept selection analytics".

Verification:
  cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short 2>&1 | tail -20
  test -f docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/2053-followup-draft.md && echo "Follow-up draft exists"
  gh issue view 2053 --repo vamseeachanta/workspace-hub --json comments --jq '.comments | length'
```

---

### Prompt 3 of 7: Governance Phase 3 Cleanup (#2057)

**Wave:** 1 (Quick Closes) | **Terminal:** Any | **Est. Time:** 15 min
**Parallel-safe with:** Prompts 1, 2

```
We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2057 — Session Governance Phase 3 (Skill Restoration)
Status: All 4 deliverable skill files are already implemented and committed. Only cleanup
hygiene remains: broken internal links, missing smoke tests, and a duplicate skill file.

Context:
- 4 skill files exist at .claude/skills/coordination/:
  session-start-routine/SKILL.md (44 lines)
  session-corpus-audit/SKILL.md (58 lines)
  comprehensive-learning-wrapper/SKILL.md (143 lines)
  cross-review-policy/SKILL.md (57 lines)
- 5 broken links in .claude/skills/_internal/meta/ reference an old
  "session-start-routine" path that was reorganized.
- A duplicate session-corpus-audit exists at
  .claude/skills/workspace-hub/session-corpus-audit/SKILL.md (434 lines) — the
  coordination/ version (58 lines) is canonical.
- docs/governance/SESSION-GOVERNANCE.md (475 lines) needs a #2057 section.

Tasks:
1. Find and fix all broken session-start-routine links in .claude/skills/_internal/meta/:
   grep -rn "session-start-routine" .claude/skills/_internal/
   Update paths to point to .claude/skills/coordination/session-start-routine/SKILL.md
2. Reconcile the duplicate session-corpus-audit:
   - Read both versions (coordination/ 58 lines vs workspace-hub/ 434 lines)
   - If workspace-hub/ version has unique content, merge valuable sections into
     the coordination/ version. Otherwise, delete the workspace-hub/ version.
   - Leave a one-line comment in the canonical file noting the merge.
3. Add a #2057 section to docs/governance/SESSION-GOVERNANCE.md documenting Phase 3
   deliverables (4 skills, their purpose, restoration status).
4. Create 4 smoke test files that verify each skill file is valid YAML-frontmatter + markdown:
   Place at: tests/governance/test_phase3_skill_smoke.py
   Each test: read file, assert frontmatter parses, assert non-empty body.
5. Run smoke tests: uv run pytest tests/governance/test_phase3_skill_smoke.py -v
6. Post a gh issue comment on #2057 summarizing cleanup work done.

Allowed write paths:
- .claude/skills/_internal/meta/**/*.md (link fixes only)
- .claude/skills/coordination/session-corpus-audit/SKILL.md (merge content)
- .claude/skills/workspace-hub/session-corpus-audit/ (DELETE if redundant)
- docs/governance/SESSION-GOVERNANCE.md (append section)
- tests/governance/test_phase3_skill_smoke.py (NEW)
- tests/governance/__init__.py (NEW, if needed)

Negative write boundaries (DO NOT touch):
- .claude/skills/coordination/session-start-routine/SKILL.md (content is correct)
- .claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md
- .claude/skills/coordination/cross-review-policy/SKILL.md
- .claude/settings.json
- .claude/hooks/
- Any file under digitalmodel/ or worldenergydata/

Cross-review: Not required (cleanup-only, no production code).

Verification:
  grep -rn "session-start-routine" .claude/skills/_internal/ | grep -v "coordination/" && echo "BROKEN LINKS REMAIN" || echo "All links fixed"
  uv run pytest tests/governance/test_phase3_skill_smoke.py -v
  grep -c "2057" docs/governance/SESSION-GOVERNANCE.md
```

---

### Prompt 4 of 7: Drilling Riser Adapter Implementation (#2063)

**Wave:** 2 (Implementation) | **Terminal:** Any | **Est. Time:** 1 hr
**Parallel-safe with:** Prompts 5, 6
**Depends on:** Wave 1 complete (labels applied)

```
We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2063 — Wire Drilling Riser Components into Analysis
Status: Not started. All prerequisites met. This is a green-field adapter following
the proven pattern at digitalmodel/src/digitalmodel/naval_architecture/ship_data.py:150.

Context:
- digitalmodel/src/digitalmodel/drilling_riser/ has 13 existing exports (functions for
  riser analysis, stress calculations, etc.)
- worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv has
  36 records with columns: component_name, od_in, id_in, weight_lb_per_ft, grade, etc.
- The adapter pattern to follow is ship_data.py:150 — normalize_vessel_record() and
  register_vessel_fleet(). Apply the same pattern for riser components.
- Depends on #1859 (vessel fleet adapter, DONE).

Tasks:
1. Read the existing adapter pattern:
   Read digitalmodel/src/digitalmodel/naval_architecture/ship_data.py lines 140-200
2. Read the CSV to understand column schema:
   head -5 worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv
3. Create digitalmodel/src/digitalmodel/drilling_riser/adapter.py (~80 lines):
   - normalize_riser_component_record(row: dict) -> dict
     Convert imperial units (od_in, weight_lb_per_ft) to SI (od_m, weight_n_per_m).
   - register_riser_components(csv_path: Path) -> list[dict]
     Load CSV, normalize each row, return list of component dicts.
   - compute_riser_string_weight_kn(components: list[dict], lengths_m: list[float]) -> float
     Sum component weights over given lengths, return total in kN.
4. Update digitalmodel/src/digitalmodel/drilling_riser/__init__.py:
   Add 3 new exports: normalize_riser_component_record, register_riser_components,
   compute_riser_string_weight_kn
5. Create digitalmodel/tests/drilling_riser/test_adapter_integration.py (~90 lines):
   - test_normalize_single_record: known input -> known SI output
   - test_register_loads_csv: register from CSV, assert len == 36
   - test_register_column_schema: assert required keys in each normalized record
   - test_string_weight_basic: 3 components x 100m each -> expected kN
   - test_string_weight_empty: empty list -> 0.0
   - test_normalize_missing_field: row missing 'od_in' -> raises KeyError or returns None
6. Update digitalmodel/tests/drilling_riser/conftest.py:
   Add a fixture that loads the CSV and returns raw rows.
7. Run tests:
   cd digitalmodel && uv run pytest tests/drilling_riser/ -v --tb=short
8. Post gh issue comment on #2063 summarizing implementation.

Allowed write paths:
- digitalmodel/src/digitalmodel/drilling_riser/adapter.py (NEW)
- digitalmodel/src/digitalmodel/drilling_riser/__init__.py (add 3 exports)
- digitalmodel/tests/drilling_riser/test_adapter_integration.py (NEW)
- digitalmodel/tests/drilling_riser/conftest.py (add fixture)

Negative write boundaries (DO NOT touch):
- digitalmodel/src/digitalmodel/drilling_riser/riser_analysis.py
- digitalmodel/src/digitalmodel/drilling_riser/stress.py
- digitalmodel/src/digitalmodel/naval_architecture/ (entire directory)
- worldenergydata/ (read-only for CSV)
- scripts/, .claude/, docs/

Cross-review: Request Codex cross-review per cat:engineering policy. The adapter
introduces unit conversion logic (imperial -> SI) that must be verified for correctness.

Verification:
  cd digitalmodel && uv run pytest tests/drilling_riser/test_adapter_integration.py -v
  uv run python -c "from digitalmodel.drilling_riser import normalize_riser_component_record, register_riser_components, compute_riser_string_weight_kn; print('All 3 exports OK')"
  wc -l src/digitalmodel/drilling_riser/adapter.py  # expect ~80
```

---

### Prompt 5 of 7: Vessel Stability Test Cases (#2059)

**Wave:** 2 (Implementation) | **Terminal:** Any | **Est. Time:** 1 hr
**Parallel-safe with:** Prompts 4, 6
**Depends on:** Wave 1 complete (labels applied)

```
We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2059 — Real Vessel Stability Test Cases (Sleipnir, Thialf, Balder)
Status: Not started. All infrastructure is complete — this is test-only work.

Context:
- The stability pipeline is fully implemented:
  digitalmodel/src/digitalmodel/naval_architecture/floating_platform_stability.py
  digitalmodel/src/digitalmodel/naval_architecture/ship_data.py (register + normalize)
- worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv has 17
  vessels including Sleipnir (14000t crane vessel), Thialf (semi-sub crane), and Balder
  (FPSO/production semi-sub).
- Sleipnir and Balder lack measured displacement — must use parametric estimates with
  draft_estimated=True flag.
- Monohull form coefficients (Cb=0.65, Cw=0.72) are used for semi-subs. Tests should
  bound expected accuracy with tolerances, not assert exact GZ values.

Tasks:
1. Read existing test file to understand patterns:
   Read digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py
2. Read the CSV to understand vessel data available:
   head -20 worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv
3. Add BALDER_RECORD fixture dict to test file (matching CSV columns).
4. Create test class TestCSVBulkRegistration:
   - test_register_17_vessels: register all 17 from CSV, assert count
   - test_all_have_required_keys: each registered vessel has loa_m, beam_m, hull_type
5. Create test class TestThreeVesselStabilityPipeline (parametrized over Sleipnir,
   Thialf, Balder):
   - test_register_and_compute_gz: register vessel -> compute GZ curve -> assert
     GZ_max > 0 and righting_lever reasonable (0.5 to 5.0 m range for large vessels)
   - test_metacentric_height_positive: GM > 0 for all three vessels
   - test_draft_estimation_flagged: for Sleipnir and Balder, assert
     draft_estimated=True in the registered record
6. Add docstrings noting which parameters are assumed vs measured:
   "Sleipnir: LOA, BEAM from CSV; displacement estimated via Cb=0.65 heuristic"
7. Run tests:
   cd digitalmodel && uv run pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short
8. Post gh issue comment on #2059 summarizing test coverage added.

Allowed write paths:
- digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py (extend)
- digitalmodel/tests/naval_architecture/conftest.py (if fixture needed)

Negative write boundaries (DO NOT touch):
- digitalmodel/src/ (entire source tree — this is test-only work)
- worldenergydata/ (read-only for CSV)
- scripts/, .claude/, docs/

Cross-review: Request Codex cross-review per cat:engineering policy. Stability
calculations with parametric estimates need independent verification of tolerance ranges.

Verification:
  cd digitalmodel && uv run pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short 2>&1 | tail -20
  grep -c "def test_" tests/naval_architecture/test_vessel_fleet_adapter.py  # expect increase of 5-7
```

---

### Prompt 6 of 7: Decline Curve Economics Implementation (#2054)

**Wave:** 2 (Implementation) | **Terminal:** Any | **Est. Time:** 1.5 hr
**Parallel-safe with:** Prompts 4, 5
**Depends on:** Wave 1 complete (labels applied)

```
We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2054 — Production Decline Curve to Economics Cashflow Model
Status: Not started. Single-file change to economics.py (693 lines).

Context:
- digitalmodel/src/digitalmodel/field_development/economics.py has hardcoded linear
  decline at lines 420-435 (_build_annual_cashflows) and lines 617-633
  (build_economics_schedule). Both blocks duplicate ~15 lines of production factor logic.
- The execution pack recommends: add DeclineType enum, add 3 optional fields to
  EconomicsInput, extract _production_factors() helper, wire inline Arps formulas.
- Use INLINE Arps formulas (not importing ArpsDeclineCurve) to avoid scipy/pandas dependency.
- Arps formulas:
  exponential: q(t) = q_i * exp(-D * t)
  hyperbolic:  q(t) = q_i / (1 + b * D * t)^(1/b)
  harmonic:    q(t) = q_i / (1 + D * t)
- Backward-compatible: no decline params = current linear model behavior.
- Default b_factor=0.5 for hyperbolic; default recovery_factor=0.15.

Tasks:
1. Read the current economics.py to understand the existing decline logic:
   Read digitalmodel/src/digitalmodel/field_development/economics.py lines 1-50 (imports/classes)
   Read digitalmodel/src/digitalmodel/field_development/economics.py lines 410-445
   Read digitalmodel/src/digitalmodel/field_development/economics.py lines 610-640
2. Add DeclineType enum (exponential, hyperbolic, harmonic, linear) near top of file.
3. Add 3 optional fields to EconomicsInput dataclass:
   decline_type: DeclineType = DeclineType.LINEAR
   decline_rate: float = 0.0  # annual decline rate D
   b_factor: float = 0.5  # Arps b-factor for hyperbolic
4. Add __post_init__ validation:
   - If decline_type is hyperbolic, b_factor must be in (0, 1)
   - If decline_type is not linear, decline_rate must be > 0
5. Extract _production_factors(economics_input, years) -> list[float] helper:
   Returns annual production factor for each year based on decline_type.
   Linear: current behavior (plateau then ramp-down).
   Exponential/Hyperbolic/Harmonic: Arps formula normalized to year 1 = 1.0.
6. Wire _production_factors() into _build_annual_cashflows (replace lines ~420-435)
   and build_economics_schedule (replace lines ~617-633).
7. Create tests in digitalmodel/tests/field_development/test_economics.py:
   - TestDeclineType: enum members exist, default is LINEAR
   - TestProductionFactors: each decline type produces expected shape
     (exponential decays faster than hyperbolic at same D)
   - TestEconomicsInputValidation: invalid b_factor raises, zero decline_rate raises
   - TestBackwardCompatibility: existing tests still pass with no decline params
   Run: cd digitalmodel && uv run pytest tests/field_development/test_economics.py -v --tb=short
8. Post gh issue comment on #2054 summarizing implementation.

Allowed write paths:
- digitalmodel/src/digitalmodel/field_development/economics.py
- digitalmodel/tests/field_development/test_economics.py

Negative write boundaries (DO NOT touch):
- digitalmodel/src/digitalmodel/field_development/benchmarks.py
- digitalmodel/src/digitalmodel/field_development/concept_selection.py
- worldenergydata/
- scripts/, .claude/, docs/

Cross-review: Request Codex cross-review per cat:engineering policy. Arps formula
implementation must be verified for physical correctness (decline curves should be
monotonically decreasing, production factors in [0, 1]).

Verification:
  cd digitalmodel && uv run pytest tests/field_development/test_economics.py -v --tb=short 2>&1 | tail -20
  uv run python -c "from digitalmodel.field_development.economics import DeclineType, EconomicsInput; print(list(DeclineType)); print('OK')"
  # Backward compat: existing test suite must still pass
  cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short 2>&1 | grep -E "(PASSED|FAILED|ERROR)" | tail -10
```

---

### Prompt 7 of 7: Timeline Benchmarks from SubseaIQ (#2060)

**Wave:** 3 (After Decisions) | **Terminal:** Any | **Est. Time:** 2 hr
**NOT parallel-safe with:** Prompt 6 (if #2060 touches benchmarks.py concurrently)
**Depends on:** Operator decides file-size policy (accept ~700 lines OR extract timeline.py)

```
We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2060 — Project Timeline Benchmarks from SubseaIQ
Status: Not started. Depends on file-size policy decision for benchmarks.py (currently 572 lines).

Context:
- digitalmodel/src/digitalmodel/field_development/benchmarks.py is 572 lines after
  #2053 landed. Adding ~130 lines for timeline functions pushes it to ~700.
- OPERATOR DECISION REQUIRED before running this prompt:
  Option A: Accept growth to ~700 lines (add timeline functions to benchmarks.py)
  Option B: Extract to digitalmodel/src/digitalmodel/field_development/timeline.py
  (The operator should replace OPTION_CHOSEN below with A or B before dispatching.)
- SubseaProject dataclass needs 4 new optional fields: year_concept, year_feed,
  year_fid, year_first_oil (all Optional[int]).
- load_projects() needs to parse these via existing _opt_int() helper.
- worldenergydata/subseaiq/analytics/normalize.py:31-54 needs 4 new alias entries
  in _FIELD_ALIASES for timeline field names.
- Timeline field names are educated guesses — may need refinement after first real scrape.

Tasks:
1. Read current state:
   Read digitalmodel/src/digitalmodel/field_development/benchmarks.py lines 1-30
   Read worldenergydata/subseaiq/analytics/normalize.py lines 25-60
2. Extend SubseaProject dataclass with 4 optional fields:
   year_concept: Optional[int] = None
   year_feed: Optional[int] = None
   year_fid: Optional[int] = None
   year_first_oil: Optional[int] = None
3. Update load_projects() to parse 4 fields via _opt_int().
4. Add 4 alias groups to _FIELD_ALIASES in normalize.py:
   "year_concept": ["concept_year", "concept_approval", "concept_date"],
   "year_feed": ["feed_year", "feed_complete", "feed_date"],
   "year_fid": ["fid_year", "final_investment_decision", "fid_date"],
   "year_first_oil": ["first_oil_year", "first_production", "startup_year"]
5. IF OPTION_CHOSEN == A: Add 3 functions to benchmarks.py:
   - timeline_duration_stats(projects) -> dict of inter-phase duration stats
   - duration_stats_by_concept_type(projects) -> dict grouped by concept_type
   - schedule_distributions(projects) -> P10/P50/P90 percentile distributions
   IF OPTION_CHOSEN == B: Create timeline.py with the same 3 functions.
6. Add exports to digitalmodel/src/digitalmodel/field_development/__init__.py.
7. Create ~28 tests across 5 test classes in:
   digitalmodel/tests/field_development/test_timeline_benchmarks.py (NEW)
   - TestSubseaProjectTimeline: 4 field tests
   - TestLoadProjectsTimeline: parse with/without fields
   - TestTimelineDurations: inter-phase math (concept->FEED, FEED->FID, FID->first oil)
   - TestDurationsByConceptType: grouping correctness
   - TestScheduleDistributions: P10/P50/P90 output shape
8. Run: cd digitalmodel && uv run pytest tests/field_development/test_timeline_benchmarks.py -v
9. Post gh issue comment on #2060 summarizing implementation and noting timeline
   field aliases are speculative pending first SubseaIQ scrape.

Allowed write paths (Option A):
- digitalmodel/src/digitalmodel/field_development/benchmarks.py
- digitalmodel/src/digitalmodel/field_development/__init__.py
- digitalmodel/tests/field_development/test_timeline_benchmarks.py (NEW)
- worldenergydata/subseaiq/analytics/normalize.py

Allowed write paths (Option B — if file split chosen):
- digitalmodel/src/digitalmodel/field_development/timeline.py (NEW)
- digitalmodel/src/digitalmodel/field_development/__init__.py
- digitalmodel/tests/field_development/test_timeline_benchmarks.py (NEW)
- worldenergydata/subseaiq/analytics/normalize.py
- digitalmodel/src/digitalmodel/field_development/benchmarks.py (SubseaProject fields ONLY)

Negative write boundaries (DO NOT touch):
- digitalmodel/src/digitalmodel/field_development/economics.py
- digitalmodel/src/digitalmodel/field_development/concept_selection.py
- digitalmodel/src/digitalmodel/naval_architecture/
- digitalmodel/src/digitalmodel/drilling_riser/
- scripts/, .claude/, docs/ (except gh issue comment)

Cross-review: Request Codex cross-review per cat:engineering policy. Timeline
alias guesses and percentile logic need verification.

Verification:
  cd digitalmodel && uv run pytest tests/field_development/test_timeline_benchmarks.py -v
  uv run python -c "from digitalmodel.field_development import timeline_duration_stats, duration_stats_by_concept_type, schedule_distributions; print('All 3 exports OK')"
  wc -l src/digitalmodel/field_development/benchmarks.py  # confirm within policy
```

---

## 3. Cross-Review Requirements Summary

| Prompt | Issue | Cross-Review Required? | Reviewer | Gate |
|--------|-------|----------------------|----------|------|
| 1 | #2056 | No | — | cat:ai-orchestration, trivial fix |
| 2 | #2053 | **Yes** | Codex | cat:engineering, analytics code |
| 3 | #2057 | No | — | Cleanup only, no production code |
| 4 | #2063 | **Yes** | Codex | cat:engineering, unit conversion logic |
| 5 | #2059 | **Yes** | Codex | cat:engineering, parametric estimates |
| 6 | #2054 | **Yes** | Codex | cat:engineering, Arps formula correctness |
| 7 | #2060 | **Yes** | Codex | cat:engineering, percentile + alias logic |

Cross-review protocol: After each implementation prompt completes, the operator should
dispatch a Codex review session targeting the changed files. The review prompt template:

```
Review the following files for correctness, edge cases, and adherence to the existing
codebase patterns. Focus on: unit conversion accuracy, formula correctness, backward
compatibility, and test coverage gaps.

Files: [list changed files from the prompt's allowed write paths]
Issue: vamseeachanta/workspace-hub#XXXX
```

---

## 4. Verification Commands — Full Suite

Run these after all prompts in a wave complete to confirm no regressions:

```bash
# Wave 1 verification (after Prompts 1-3)
grep 'threshold: 200' scripts/workflow/governance-checkpoints.yaml
uv run pytest tests/governance/ -v --tb=short
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py tests/field_development/test_concept_probability.py -v --tb=short
grep -rn "session-start-routine" .claude/skills/_internal/ | grep -v "coordination/" | wc -l  # expect 0

# Wave 2 verification (after Prompts 4-6)
cd digitalmodel && uv run pytest tests/drilling_riser/ -v --tb=short
cd digitalmodel && uv run pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short
cd digitalmodel && uv run pytest tests/field_development/test_economics.py -v --tb=short
# Full regression:
cd digitalmodel && uv run pytest tests/ -v --tb=short 2>&1 | tail -5

# Wave 3 verification (after Prompt 7)
cd digitalmodel && uv run pytest tests/field_development/test_timeline_benchmarks.py -v --tb=short
cd digitalmodel && uv run pytest tests/ -v --tb=short 2>&1 | tail -5
```

---

## 5. Final Batching Recommendation

### Dispatch Plan

```
WAVE 1 — Quick Closes (3 terminals, parallel)
  Terminal A: Prompt 1 (#2056 threshold fix)      ~15 min
  Terminal B: Prompt 2 (#2053 verify & close)      ~20 min
  Terminal C: Prompt 3 (#2057 cleanup)             ~15 min
  ── barrier: wait for all 3 to complete ──
  ── operator: review comments, apply labels ──

WAVE 2 — Implementation (3 terminals, parallel)
  Terminal D: Prompt 4 (#2063 drilling riser)       ~1 hr
  Terminal E: Prompt 5 (#2059 vessel stability)     ~1 hr
  Terminal F: Prompt 6 (#2054 decline curve)        ~1.5 hr
  ── barrier: wait for all 3 to complete ──
  ── operator: dispatch Codex cross-reviews ──
  ── operator: run Wave 2 verification suite ──

WAVE 3 — After Decisions (1 terminal, sequential)
  Precondition: operator decides file-size policy for benchmarks.py
  Terminal G: Prompt 7 (#2060 timeline benchmarks)  ~2 hr
  ── operator: dispatch Codex cross-review ──
  ── operator: run Wave 3 verification suite ──
```

### Issues Deferred to Future Waves

| Issue | Reason | Unblock Action |
|-------|--------|---------------|
| #2062 | Scope overstatement (2,210 -> ~138 rigs); issue body needs v1 refinement | Operator updates issue title/body, then re-queue |
| #2058 | File split decision required + contention with #2055 (wip:ace-linux-1) | Resolve #2055 first, approve file split, then re-queue |
| #2055 | Critical data blocker: SubseaIQ has zero equipment count fields | Operator decides data source (manual/pipeline/synthetic), backfills 10 GoM fields |

### Estimated Total Execution Time

| Wave | Terminals | Wall-Clock Time | Cumulative |
|------|-----------|----------------|------------|
| Wave 1 | 3 parallel | ~20 min | 20 min |
| Operator review | — | ~10 min | 30 min |
| Wave 2 | 3 parallel | ~1.5 hr | 2 hr |
| Cross-review | 3 Codex sessions | ~30 min | 2.5 hr |
| Wave 3 | 1 sequential | ~2 hr | 4.5 hr |

**Total: ~4.5 hours wall-clock across 7 terminals (3+3+1), closing 7 of 10 issues.**

---

## Appendix: Issue-to-Prompt Traceability

| Issue | Stage-2 Terminal | This Wave Prompt | Wave | Action |
|-------|-----------------|-----------------|------|--------|
| #2056 | T7 | Prompt 1 | 1 | FIX-AND-CLOSE |
| #2053 | T10 | Prompt 2 | 1 | VERIFY-AND-CLOSE |
| #2057 | T6 | Prompt 3 | 1 | CLEANUP-AND-CLOSE |
| #2063 | T1 | Prompt 4 | 2 | IMPLEMENT |
| #2059 | T4 | Prompt 5 | 2 | IMPLEMENT (test-only) |
| #2054 | T9 | Prompt 6 | 2 | IMPLEMENT |
| #2060 | T3 | Prompt 7 | 3 | IMPLEMENT (after decision) |
| #2062 | T2 | Deferred | — | Needs scope refinement |
| #2058 | T5 | Deferred | — | Needs file split + #2055 resolution |
| #2055 | T8 | Deferred | — | Needs data source decision |
