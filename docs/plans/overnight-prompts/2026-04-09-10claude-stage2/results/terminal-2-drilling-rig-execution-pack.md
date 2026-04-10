# Stage-2 Execution Pack: Drilling Rig Fleet Adapter — Issue #2062

| Field | Value |
|---|---|
| Issue | [#2062](https://github.com/vamseeachanta/workspace-hub/issues/2062) |
| Title | feat(naval-arch): drilling rig fleet adapter — 2,210 rigs into hull form validation |
| Labels | enhancement, cat:engineering, domain:code-promotion, agent:claude |
| State | OPEN |
| Dependencies | #1859 (vessel fleet adapter) DONE, #1319 (hull form parametric) DONE |
| Stage-1 dossier | `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md` |
| Refinement doc | `docs/plans/claude-followup-2026-04-09/results/issue-2055-2062-refinement-drafts.md` |
| Pack date | 2026-04-09 |

---

## 1. Fresh Status Check Since Stage-1 Dossier

**Check performed:** 2026-04-09 (same day as dossier)

### Files Verified Present and Unchanged

| File | Status | Lines | Key Functions |
|---|---|---|---|
| `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | Unchanged | 309 | `normalize_drilling_rig_record()` L233, `register_fleet_vessels()` L200, `estimate_vessel_hydrostatics()` L271, `_DEFAULT_CB=0.65` L267 |
| `digitalmodel/src/digitalmodel/naval_architecture/hull_form.py` | Unchanged | 128 | `block_coefficient()` L21, `prismatic_coefficient()` L38, `midship_coefficient()` L48, `waterplane_coefficient()` L59 |
| `digitalmodel/src/digitalmodel/naval_architecture/ship_dimensions.py` | Unchanged | 205 | `validate_vessel_entry()` L97, `merge_template_into_registry()` L142 |
| `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Unchanged | 49 | Exports 17 symbols including `normalize_drilling_rig_record` |
| `worldenergydata/data/modules/vessel_fleet/curated/drilling_rigs.csv` | Unchanged | 2,211 lines (2,210 data rows), 23 columns |
| `worldenergydata/src/worldenergydata/vessel_fleet/models/drilling_rig.py` | Unchanged | 131 | `DrillingRigEntry` dataclass L36 |
| `worldenergydata/src/worldenergydata/vessel_fleet/schemas/drilling_rig.py` | Unchanged | 172 | `DrillingRigSchema` L12, has HULL_FORM_TYPE/HULL_LIBRARY_REF fields |
| `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | Unchanged | 576 | 13 test classes, 49 test methods |
| `digitalmodel/tests/naval_architecture/test_hull_form.py` | Unchanged | 132 | 5 test classes, 13 test methods |

### Constants/Functions NOT Yet In Codebase (Confirmed Missing)

- `register_drilling_rigs()` — does not exist
- `_RIG_TYPE_HULL_FORM_MAP` — does not exist
- `_HULL_FORM_COEFFICIENTS` — does not exist
- `estimate_rig_hull_coefficients()` — does not exist
- `_estimate_draft()` — does not exist

### Git Activity

- Zero commits touching naval architecture files since dossier date
- No branches or PRs referencing #2062
- No other in-flight sessions working on this issue

### Staleness Verdict

**NOT STALE.** The stage-1 dossier accurately describes current repo state. All file paths, line numbers, function names, and data quality findings are confirmed current.

---

## 2. Minimal Plan-Review Packet

### Problem Statement

The vessel fleet adapter pattern (#1859) and hull form coefficient module (#1319) are complete, but no pipeline connects the 2,210-row drilling rig CSV to hull form validation. The CSV has critical data gaps: no DRAFT_M column, 100% empty DISPLACEMENT_TONNES, and only ~143 records with LOA+BEAM.

### v1 Scope

Register ~138 drilling rigs (51 drillships + 87 semi-subs with geometry) into the hull form validation pipeline using:
- Rig-type-to-hull-form mapping constants
- Hull-form-specific Cb/Cm/Cp default estimation
- Draft estimation from hull-type L/D heuristics (flagged `draft_estimated=True`)
- Batch registration function `register_drilling_rigs()`

### Files to Modify (6 files)

| # | File | Change |
|---|---|---|
| 1 | `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | Add `_RIG_TYPE_HULL_FORM_MAP`, `_estimate_draft()`, `register_drilling_rigs()` |
| 2 | `digitalmodel/src/digitalmodel/naval_architecture/hull_form.py` | Add `_HULL_FORM_COEFFICIENTS`, `estimate_rig_hull_coefficients()` |
| 3 | `digitalmodel/src/digitalmodel/naval_architecture/ship_dimensions.py` | Possibly relax draft validation or add rig-specific path |
| 4 | `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Export `register_drilling_rigs`, `estimate_rig_hull_coefficients` |
| 5 | `digitalmodel/tests/naval_architecture/test_hull_form.py` | Add `TestRigHullFormCoefficients` (5 tests) |
| 6 | `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | Add `TestRegisterDrillingRigs` (5 tests) |

### Acceptance Criteria

1. `estimate_rig_hull_coefficients("drillship")` returns Cb in [0.55, 0.70]
2. `estimate_rig_hull_coefficients("semi_submersible")` returns Cb in [0.40, 0.60]
3. `estimate_rig_hull_coefficients("jack_up")` returns Cb in [0.75, 0.90]
4. Cp = Cb / Cm identity holds for all rig types
5. `register_drilling_rigs(full_csv)` registers ~138, skips ~2,072
6. Estimated drafts flagged with `draft_estimated=True`
7. All 49 existing fleet adapter tests pass unchanged
8. All 13 existing hull form tests pass unchanged
9. 10 new tests added and passing

### Risk Summary

| Risk | Severity | Mitigation |
|---|---|---|
| Draft heuristics inaccurate for atypical vessels | Medium | Mark estimates with flag; downstream consumers check `draft_estimated` |
| Jack-ups zero geometry (1,009 skipped) | Low (v1) | Deferred to v2 CSV enrichment |
| Single DEFAULT_CB=0.65 used for non-rig vessels | Low | New rig-specific path is additive; does not modify existing default |
| ship_dimensions.py validation may reject estimated drafts | Medium | Test first; add rig-specific validation path only if needed |

---

## 3. Issue Refinement Recommendations

The issue title and body overstate implementable scope. The refinement doc at `docs/plans/claude-followup-2026-04-09/results/issue-2055-2062-refinement-drafts.md` provides a paste-ready replacement body. Key corrections:

### Title Change

**Current:** `feat(naval-arch): drilling rig fleet adapter — 2,210 rigs into hull form validation`
**Recommended:** `feat(naval-arch): drilling rig fleet adapter — drillship and semi-sub hull form validation (~138 rigs with geometry)`

### Body Additions

1. **Add explicit data limitations section** — DRAFT_M absent, DISPLACEMENT_TONNES empty, jack-ups have zero geometry
2. **Add draft estimation strategy** — Option A (L/D heuristics) with `draft_estimated=True` flag
3. **Add deferred items list** — jack-up registration, displacement validation, CSV enrichment
4. **Correct throughput expectation** — ~138 registerable rigs, not 2,210

### Label Additions

- Add `status:plan-review` after operator reviews this pack
- Add `status:plan-approved` after user approval to unblock implementation

---

## 4. Operator Command Pack

### 4a. Apply issue refinement (title + body update)

```bash
# Update issue title to reflect realistic v1 scope
gh issue edit 2062 --title "feat(naval-arch): drilling rig fleet adapter — drillship and semi-sub hull form validation (~138 rigs with geometry)"
```

```bash
# Update issue body with refined scope, data limitations, and acceptance criteria
gh issue edit 2062 --body "$(cat <<'EOF'
## Summary

Adapter to register drilling rigs from the vessel fleet CSV into the hull form validation pipeline. v1 targets drillships and semi-submersibles with LOA+BEAM data (~138 of 2,210 rigs).

## Problem

The vessel fleet adapter pattern (#1859) and hull form module (#1319) are complete, but no pipeline connects drilling rig CSV data to hull form coefficient estimation. The CSV lacks draft and displacement columns, so the adapter must estimate draft from hull-type heuristics.

## Data Limitations

- **NO DRAFT_M column** in `drilling_rigs.csv` (column does not exist in schema)
- **DISPLACEMENT_TONNES is 100% empty** across all 2,210 rows
- **Jack-ups (1,009 rigs) have zero LOA/BEAM data** — skipped in v1
- **Only ~143 records have any principal dimensions** (51 drillships, 87 semi-subs)
- All computed drafts are heuristic estimates flagged `draft_estimated=True`

## v1 Scope

### New constants in `ship_data.py`:
- `_RIG_TYPE_HULL_FORM_MAP`: drillship -> monohull, semi_submersible -> twin-hull, jack_up -> barge

### New functions in `hull_form.py`:
- `estimate_rig_hull_coefficients(rig_type: str) -> dict` — returns Cb, Cm, Cp, hull_form

### New functions in `ship_data.py`:
- `_estimate_draft(record, rig_type) -> Optional[float]` — L/D heuristics (drillship: LOA/15, semi-sub: BEAM*0.25, jack-up: LOA/8)
- `register_drilling_rigs(records, *, overwrite=False) -> tuple[int, int]` — normalize, estimate draft, map hull form, register

### Draft estimation strategy (Option A):
- Drillship: draft_ft = loa_ft / 15 (typical L/D ~14-16)
- Semi-submersible: draft_ft = beam_ft * 0.25 (pontoon draft relative to beam)
- Jack-up: draft_ft = loa_ft / 8 (barge hull, shallow draft)

## Deferred (v2 / follow-up issues)

- Jack-up registration (0 LOA/BEAM data; needs CSV enrichment)
- Platform rig and other types (sparse dimensions)
- Displacement-based Cb validation (no displacement data)
- DRAFT_M column addition to worldenergydata CSV
- Downstream consumer awareness for estimated drafts

## Acceptance Criteria

- [ ] `estimate_rig_hull_coefficients` returns Cb/Cm/Cp with Cp = Cb/Cm identity
- [ ] Drillship Cb in [0.55, 0.70]
- [ ] Semi-sub Cb in [0.40, 0.60]
- [ ] Jack-up Cb in [0.75, 0.90]
- [ ] `register_drilling_rigs` skips records without LOA+BEAM, returns (added, skipped)
- [ ] Smoke test: ~138 rigs registered from full CSV, ~2,072 skipped
- [ ] All existing fleet adapter tests pass unchanged
- [ ] 10 new tests (5 hull form coefficients + 5 rig registration)
- [ ] New functions exported from `__init__.py`

## Dependencies

- #1859 (vessel fleet adapter pattern) — DONE
- #1319 (hull form parametric design) — DONE
EOF
)"
```

### 4b. Apply labels for plan-review workflow

```bash
# Add plan-review label after reviewing this pack
gh issue edit 2062 --add-label "status:plan-review"
```

```bash
# After user approval, apply plan-approved to unblock implementation
gh issue edit 2062 --add-label "status:plan-approved"
```

### 4c. Post summary comment on issue

```bash
gh issue comment 2062 --body "$(cat <<'EOF'
## Stage-2 Execution Pack Complete

**Dossier:** `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md`
**Execution pack:** `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-2-drilling-rig-execution-pack.md`

### Fresh status (2026-04-09):
- All prerequisite files unchanged and present
- `register_drilling_rigs()` and hull form coefficient functions do not yet exist (confirmed missing)
- No in-flight branches or PRs

### Scope clarification:
- v1 targets ~138 rigs with geometry (51 drillships, 87 semi-subs), not all 2,210
- Draft estimation via L/D heuristics (no DRAFT_M column in CSV)
- 10 new tests, 6 files modified, purely additive changes

### Next steps:
1. Review and approve refined issue body
2. Apply `status:plan-review` then `status:plan-approved`
3. Implementation via TDD-first approach in stage-1 dossier
EOF
)"
```

---

## 5. Self-Contained Implementation Prompt for Claude

```
IMPLEMENTATION PROMPT — Issue #2062: Drilling Rig Fleet Adapter
================================================================

You are implementing the drilling rig fleet adapter for GitHub issue #2062.

PRE-FLIGHT: This issue MUST be labeled `status:plan-approved` before you begin.
If not, STOP and notify the user.

DOSSIER: docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md
EXECUTION PACK: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-2-drilling-rig-execution-pack.md

## Context

The vessel fleet adapter (#1859) provides normalize_fleet_record() and register_fleet_vessels().
The hull form module (#1319) provides block_coefficient(), prismatic_coefficient(), etc.
A drilling-rig-specific normalizer normalize_drilling_rig_record() already exists (ship_data.py L233).
The 2,210-row drilling_rigs.csv has NO DRAFT_M column and 100% empty DISPLACEMENT_TONNES.
Only ~143 records have LOA+BEAM (51 drillships, 87 semi-subs). Jack-ups have zero geometry.

## TDD-First Implementation (write failing tests BEFORE implementation)

### Step 1: Add tests to digitalmodel/tests/naval_architecture/test_hull_form.py

Add class TestRigHullFormCoefficients with 5 tests:
  1. test_drillship_cb_in_range — Cb in [0.55, 0.70]
  2. test_semi_submersible_cb_in_range — Cb in [0.40, 0.60]
  3. test_jack_up_cb_in_range — Cb in [0.75, 0.90]
  4. test_all_types_have_cm_and_cp — all 3 types return cm and cp, 0 < cp < 1
  5. test_cp_equals_cb_over_cm — Cp == Cb / Cm (approx)

Import: from digitalmodel.naval_architecture.hull_form import estimate_rig_hull_coefficients

### Step 2: Add tests to digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py

Add class TestRegisterDrillingRigs with 5 tests:
  1. test_register_drillship_with_loa_beam — added == 1
  2. test_register_semisub_with_loa_beam — added == 1
  3. test_skips_records_without_dimensions — added == 0, skipped == 1
  4. test_hull_form_mapped_after_registration — ship.hull_form == "monohull" for drillship
  5. test_hydrostatics_after_registration — Cb > 0.05 and < 0.95

Import: from digitalmodel.naval_architecture.ship_data import register_drilling_rigs
Use existing test fixtures in the file as reference for record format.

### Step 3: Run tests (expect 10 failures)

  uv run pytest digitalmodel/tests/naval_architecture/test_hull_form.py -v -k "Rig" --tb=short
  uv run pytest digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py -v -k "drilling" --tb=short

### Step 4: Implement in digitalmodel/src/digitalmodel/naval_architecture/hull_form.py

Add at module level:

  _HULL_FORM_COEFFICIENTS = {
      "drillship":        {"cb": 0.62, "cm": 0.97, "hull_form": "monohull"},
      "semi_submersible": {"cb": 0.50, "cm": 0.90, "hull_form": "twin-hull"},
      "jack_up":          {"cb": 0.82, "cm": 0.92, "hull_form": "barge"},
  }

Add function:

  def estimate_rig_hull_coefficients(rig_type: str) -> dict:
      """Return hull form coefficients for a drilling rig type."""
      if rig_type not in _HULL_FORM_COEFFICIENTS:
          raise ValueError(f"Unknown rig type: {rig_type}")
      entry = _HULL_FORM_COEFFICIENTS[rig_type]
      cb, cm = entry["cb"], entry["cm"]
      return {"cb": cb, "cm": cm, "cp": cb / cm, "hull_form": entry["hull_form"]}

### Step 5: Implement in digitalmodel/src/digitalmodel/naval_architecture/ship_data.py

Add at module level (after existing constants):

  _RIG_TYPE_HULL_FORM_MAP = {
      "drillship": "monohull",
      "semi_submersible": "twin-hull",
      "jack_up": "barge",
      "inland_barge": "barge",
      "submersible": "twin-hull",
  }

  _RIG_DRAFT_HEURISTICS = {
      "drillship": lambda loa, beam: loa / 15,
      "semi_submersible": lambda loa, beam: beam * 0.25,
      "jack_up": lambda loa, beam: loa / 8,
  }

Add functions:

  def _estimate_draft(record, rig_type):
      """Estimate draft from hull-type L/D heuristics. Returns draft_ft or None."""
      loa_ft = record.get("loa_ft")
      beam_ft = record.get("beam_ft")
      if rig_type in _RIG_DRAFT_HEURISTICS and loa_ft and beam_ft:
          return _RIG_DRAFT_HEURISTICS[rig_type](loa_ft, beam_ft)
      return None

  def register_drilling_rigs(records, *, overwrite=False):
      """Register drilling rigs into the ship registry. Returns (added, skipped)."""
      added = 0
      skipped = 0
      for raw in records:
          norm = normalize_drilling_rig_record(raw)
          if norm is None or not norm.get("loa_ft") or not norm.get("beam_ft"):
              skipped += 1
              continue
          rig_type = norm.get("rig_type", "")
          hull_form = _RIG_TYPE_HULL_FORM_MAP.get(rig_type)
          if hull_form:
              norm["hull_form"] = hull_form
          draft_ft = norm.get("draft_ft") or _estimate_draft(norm, rig_type)
          if draft_ft:
              norm["draft_ft"] = draft_ft
              norm["draft_estimated"] = not bool(raw.get("DRAFT_M"))
          else:
              skipped += 1
              continue
          # Attempt registration
          entry = {
              "hull_id": norm.get("name", "").upper().strip(),
              "name": norm.get("name"),
              "loa_ft": norm["loa_ft"],
              "beam_ft": norm["beam_ft"],
              "draft_ft": norm["draft_ft"],
              "draft_estimated": norm.get("draft_estimated", False),
              "hull_form": norm.get("hull_form"),
              "rig_type": rig_type,
              "vessel_category": "drilling",
          }
          if not entry["hull_id"] or not entry["name"]:
              skipped += 1
              continue
          try:
              merge_template_into_registry(entry, overwrite=overwrite)
              added += 1
          except Exception:
              skipped += 1
      return added, skipped

### Step 6: Update digitalmodel/src/digitalmodel/naval_architecture/__init__.py

Add to imports and __all__:
  - register_drilling_rigs (from ship_data)
  - estimate_rig_hull_coefficients (from hull_form)

### Step 7: Run all tests

  uv run pytest digitalmodel/tests/naval_architecture/ -v
  uv run pytest digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py -v -k "drilling"
  uv run pytest digitalmodel/tests/naval_architecture/test_hull_form.py -v -k "Rig"

### Step 8: Smoke test with full CSV

  uv run python -c "
  import csv
  from digitalmodel.naval_architecture.ship_data import register_drilling_rigs
  with open('worldenergydata/data/modules/vessel_fleet/curated/drilling_rigs.csv') as f:
      rows = list(csv.DictReader(f))
  print(f'Loaded {len(rows)} rigs')
  added, skipped = register_drilling_rigs(rows)
  print(f'Registered: {added}, Skipped: {skipped}')
  assert 100 < added < 200, f'Expected ~138, got {added}'
  assert 2000 < skipped < 2200, f'Expected ~2072, got {skipped}'
  print('Smoke test PASSED')
  "

### Step 9: Verify import paths

  uv run python -c "from digitalmodel.naval_architecture import register_drilling_rigs, estimate_rig_hull_coefficients; print('Imports OK')"

### Step 10: Post-implementation

  - Post summary comment on issue #2062
  - Request cross-review per project_cross_review_policy
  - Commit with message: feat(naval-arch): add drilling rig fleet adapter with hull form coefficients (#2062)
```

---

## 6. Morning Handoff

### What happened overnight

- Stage-1 dossier produced a comprehensive analysis of #2062 including data quality audit, 7-item implementation delta, TDD test code, and 3-phase execution plan.
- Refinement draft at `docs/plans/claude-followup-2026-04-09/results/issue-2055-2062-refinement-drafts.md` clarified that the "2,210 rigs" headline overstates scope — realistic v1 is ~138 rigs.
- Fresh repo check confirms all dossier findings are current. No stale data.

### What the operator needs to do

1. **Review this execution pack** (you're reading it now)
2. **Run the issue refinement commands** in section 4a to update issue title and body
3. **Apply `status:plan-review`** via section 4b command
4. **After your review, apply `status:plan-approved`** to unblock implementation
5. **Use the implementation prompt** in section 5 to dispatch to a Claude session
6. **Optional:** Post the summary comment from section 4c

### What to watch for during implementation

- The `normalize_drilling_rig_record()` function at `ship_data.py:233` already handles field mapping — the new `register_drilling_rigs()` must call it, not `normalize_fleet_record()`
- The `validate_vessel_entry()` function at `ship_dimensions.py:97` requires `draft_ft` — if this blocks registration, a rig-specific validation bypass may be needed
- Test the `merge_template_into_registry()` call at `ship_dimensions.py:142` to confirm it accepts the entry shape produced by `register_drilling_rigs()`

### Time estimate

Implementation scope: ~3 new functions, ~10 new tests, 4-6 file modifications. Well within a single Claude session.

---

## 7. Final Recommendation

**RECOMMEND: REFINE ISSUE, THEN APPROVE FOR IMPLEMENTATION.** The infrastructure is complete (#1859, #1319), the stage-1 dossier is not stale, the scope is realistic (~138 rigs), and the implementation is well-bounded. The only blocker is the plan-review workflow: update the issue body to reflect v1 scope limitations, apply `status:plan-review`, then `status:plan-approved` to unblock.
