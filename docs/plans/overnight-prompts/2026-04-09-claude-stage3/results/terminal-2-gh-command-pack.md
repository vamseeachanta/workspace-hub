# Unified `gh` Command Pack — Stage-2 Execution Packs (2026-04-09)

> **DRAFT ONLY** — Every command in this document is a draft template.
> Do NOT execute without human review. Do NOT pipe to `sh` or `bash`.

| Field | Value |
|---|---|
| Source packs | 10 stage-2 execution packs (terminals 1-10) |
| Issues covered | #2053, #2054, #2055, #2056, #2057, #2058, #2059, #2060, #2062, #2063 |
| Total commands | 48 |
| Generated | 2026-04-09 |

---

## 1. Safety Notes

1. **DRAFT ONLY** — Every `gh` command below is a draft for operator review. None have been executed.
2. **No GitHub mutations were made** during the generation of this pack.
3. **Review each command** before execution, especially `--body` payloads which may need tuning.
4. **Label ordering matters** — apply `status:plan-review` first. Only promote to `status:plan-approved` after human review of the corresponding execution pack.
5. **`gh issue edit --body`** overwrites the entire body. Verify you want a full replacement before running body-edit commands.
6. **Issue close commands** are gated — only run after implementation is verified.
7. **Follow-up issue creation** (#2053 spinoff) creates a new GitHub issue. Confirm the scope before running.
8. **#2055 has a special path** — it needs `status:needs-refinement` first (data dependency unmet), not direct `plan-review`.

---

## 2. Commands Grouped by Issue

### Issue #2053 — Concept Selection Probability Matrix

```bash
# DRAFT ONLY — #2053: Add plan-review label
gh issue edit 2053 --add-label "status:plan-review"
```

```bash
# DRAFT ONLY — #2053: Post plan summary comment
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

**Recommendation**: Run full test suite, then approve if green. Request Codex cross-review per `cat:engineering` policy.
EOF
)"
```

```bash
# DRAFT ONLY — #2053: After user approval, add plan-approved label
gh issue edit 2053 --add-label "status:plan-approved"
```

```bash
# DRAFT ONLY — #2053: Create follow-up issue for production_rate_bopd
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

### Issue #2054 — Production Decline Curve to Economics

```bash
# DRAFT ONLY — #2054: Add plan-review label
gh issue edit 2054 --add-label "status:plan-review"
```

```bash
# DRAFT ONLY — #2054: Post plan review comment
gh issue comment 2054 --body "$(cat <<'EOF'
## Plan Review Notes (Stage-2 Execution Pack)

**Plan location**: `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-9-decline-curve-execution-pack.md`

### Scope
- 1 file changed: `digitalmodel/src/digitalmodel/field_development/economics.py`
- 1 test file changed: `digitalmodel/tests/field_development/test_economics.py`
- Zero worldenergydata submodule changes
- Inline Arps math (3 one-liners), no new dependencies

### Design Decisions Needing Confirmation
1. `reservoir_size_mmbbl` treated as OOIP with default RF=0.15 — correct?
2. `b_factor` defaults to 0.5 for hyperbolic — acceptable?
3. Extract shared `_production_factors()` helper to eliminate duplication — approved?

### Acceptance Criteria
- [ ] `EconomicsInput` accepts `decline_type`, `decline_rate`, `b_factor`
- [ ] Exponential, hyperbolic, harmonic decline types work correctly
- [ ] No decline params = identical to pre-change linear behavior
- [ ] Production profile duplication eliminated
- [ ] All existing tests pass unchanged
EOF
)"
```

```bash
# DRAFT ONLY — #2054: After user approval, swap labels
gh issue edit 2054 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

---

### Issue #2055 — Subsea Cost Benchmarking

```bash
# DRAFT ONLY — #2055: Add needs-refinement label (data dependency unmet)
gh issue edit 2055 --add-label "status:needs-refinement"
```

```bash
# DRAFT ONLY — #2055: Post scoping decisions comment
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

```bash
# DRAFT ONLY — #2055: After resolving scoping decisions, upgrade to plan-review
gh issue edit 2055 --remove-label "status:needs-refinement" --add-label "status:plan-review"
```

```bash
# DRAFT ONLY — #2055: After user reviews plan, approve for implementation
gh issue edit 2055 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

---

### Issue #2056 — Session Governance Phase 2

```bash
# DRAFT ONLY — #2056: Add plan-review label
gh issue edit 2056 --add-label "status:plan-review"
```

```bash
# DRAFT ONLY — #2056: Post threshold regression finding comment
gh issue comment 2056 --body "$(cat <<'EOF'
## Stage-2 Execution Pack Finding: Threshold Regression

**Bug**: `governance-checkpoints.yaml:54` has `threshold: 5000` — should be `200`.
Introduced in `d4f46c770` (Phase 2c). The 200-call ceiling is not enforced by the
governor; only the hook's hardcoded fast-path at 160 provides partial coverage.

**Fix**: One-line change.
**Impact**: Tool-call ceiling effectively non-functional at the documented 200 limit.

Remaining scope: threshold fix + bypass policy doc update + optional cleanup.
Stage-1 dossier: 3 of 4 gaps already resolved by overnight implementation.
EOF
)"
```

```bash
# DRAFT ONLY — #2056: After operator approval
gh issue edit 2056 --add-label "status:plan-approved"
```

```bash
# DRAFT ONLY — #2056: Close after implementation verified
gh issue close 2056 --comment "Completed. All 4 gaps resolved: tool-call ceiling (200), error-loop-breaker (3x), strict review gate, threshold regression fixed."
```

---

### Issue #2057 — Session Governance Phase 3

```bash
# DRAFT ONLY — #2057: Update issue body with completion status
gh issue edit 2057 --body "$(cat <<'BODY'
## Context

#1839 identified several pieces of session infrastructure that were lost during the GSD migration or never built. Phase 1 delivered the checkpoint model. Phase 2 wires runtime enforcement. This issue covers rebuilding the lost skills.

## Deliverables — Status

### 1. session-start-routine skill — DONE
- **Restored**: `.claude/skills/coordination/session-start-routine/SKILL.md` (v1.0.0)
- **Commits**: e582d7e70, ef8e7826b

### 2. session-corpus-audit skill — DONE
- **Pre-existing**: `.claude/skills/workspace-hub/session-corpus-audit/SKILL.md` (434 lines, Hermes v1.0.0)
- **Slim version added**: `.claude/skills/coordination/session-corpus-audit/SKILL.md` (58 lines)

### 3. comprehensive-learning — DONE
- **Pre-existing**: `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md` (v2.5.0)
- **Wrapper added**: `.claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md` (143 lines)

### 4. cross-review-policy skill — DONE
- **Created**: `.claude/skills/coordination/cross-review-policy/SKILL.md` (v1.0.0)

## Remaining Cleanup
- [ ] Fix 5 broken `session-start-routine` links in `_internal/meta/` skills
- [ ] Create 4 smoke tests in `tests/skills/`
- [ ] Update `docs/governance/SESSION-GOVERNANCE.md` with #2057 section
- [ ] Reconcile duplicate session-corpus-audit files (coordination/ vs workspace-hub/)

## References
- Parent: #1839
- Governance doc: `docs/governance/SESSION-GOVERNANCE.md`
BODY
)"
```

```bash
# DRAFT ONLY — #2057: Add plan-review label
gh issue edit 2057 --add-label "status:plan-review"
```

```bash
# DRAFT ONLY — #2057: Post status comment
gh issue comment 2057 --body "$(cat <<'COMMENT'
## Stage-2 Status Report (2026-04-09)

**All 4 skill deliverables implemented** during overnight batch (terminal 6, commits e582d7e70..ef8e7826b).

Skills created at `.claude/skills/coordination/` path:
- `session-start-routine/SKILL.md` (44 lines)
- `session-corpus-audit/SKILL.md` (58 lines)
- `cross-review-policy/SKILL.md` (57 lines)
- `comprehensive-learning-wrapper/SKILL.md` (143 lines)

**Remaining cleanup** (plan-review pending):
1. Fix 5 broken internal links in `_internal/meta/` skills
2. Create 4 smoke tests
3. Update SESSION-GOVERNANCE.md
4. Reconcile duplicate session-corpus-audit (coordination/ 58 lines vs workspace-hub/ 434 lines)

Process note: implementation preceded plan-approval label. Apply `status:plan-approved` retroactively after reviewing this pack.
COMMENT
)"
```

```bash
# DRAFT ONLY — #2057: After operator approves cleanup plan
gh issue edit 2057 --add-label "status:plan-approved" --remove-label "status:plan-review"
```

---

### Issue #2058 — Subsea Architecture Patterns

```bash
# DRAFT ONLY — #2058: Add plan-review label
gh issue edit 2058 --add-label "status:plan-review"
```

```bash
# DRAFT ONLY — #2058: Add priority label (optional)
gh issue edit 2058 --add-label "priority:medium"
```

```bash
# DRAFT ONLY — #2058: Post plan-review comment
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

```bash
# DRAFT ONLY — #2058: After human review, approve
gh issue edit 2058 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

---

### Issue #2059 — Real Vessel Stability Test Cases

```bash
# DRAFT ONLY — #2059: Post plan summary comment
gh issue comment 2059 --body "$(cat <<'EOF'
## Stage-2 Plan Review Packet

**Status**: Infrastructure complete (fleet adapter + stability engine). Remaining work is **test-only** (~80-120 lines).

**5 Open Gaps**:
1. BALDER_RECORD fixture missing from test file
2. No parametrized 3-vessel stability pipeline test (Sleipnir, Thialf, Balder)
3. No CSV-based bulk registration test (17 vessels)
4. No GZ curve physical reasonableness assertions
5. No assumed-vs-measured parameter documentation in tests

**Files to change**:
- `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` (extend)
- `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` (optional: semi-sub Cb/Cw defaults)

**Recommendation**: READY FOR PLAN REVIEW — label as `status:plan-review`, then `status:plan-approved` to unblock implementation.

_Execution pack: `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-4-vessel-stability-execution-pack.md`_
EOF
)"
```

```bash
# DRAFT ONLY — #2059: Add plan-review label
gh issue edit 2059 --add-label "status:plan-review"
```

```bash
# DRAFT ONLY — #2059: After human approval, swap labels
gh issue edit 2059 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

---

### Issue #2060 — Project Timeline Benchmarks

```bash
# DRAFT ONLY — #2060: Add plan-review label
gh issue edit 2060 --add-label "status:plan-review"
```

```bash
# DRAFT ONLY — #2060: Post plan-review comment
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

### Decision needed
benchmarks.py is 572 lines. Adding timeline code pushes to ~700. Accept growth or extract `timeline.py`?

### Recommendation
Ready after `status:plan-approved`. Pure addition, no contention with other terminals.
EOF
)"
```

```bash
# DRAFT ONLY — #2060: After review, approve
gh issue edit 2060 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

---

### Issue #2062 — Drilling Rig Fleet Adapter

```bash
# DRAFT ONLY — #2062: Update title to reflect realistic v1 scope
gh issue edit 2062 --title "feat(naval-arch): drilling rig fleet adapter — drillship and semi-sub hull form validation (~138 rigs with geometry)"
```

```bash
# DRAFT ONLY — #2062: Update issue body with refined scope
gh issue edit 2062 --body "$(cat <<'EOF'
## Summary

Adapter to register drilling rigs from the vessel fleet CSV into the hull form validation pipeline. v1 targets drillships and semi-submersibles with LOA+BEAM data (~138 of 2,210 rigs).

## Problem

The vessel fleet adapter pattern (#1859) and hull form module (#1319) are complete, but no pipeline connects drilling rig CSV data to hull form coefficient estimation. The CSV lacks draft and displacement columns, so the adapter must estimate draft from hull-type heuristics.

## Data Limitations

- **NO DRAFT_M column** in `drilling_rigs.csv`
- **DISPLACEMENT_TONNES is 100% empty** across all 2,210 rows
- **Jack-ups (1,009 rigs) have zero LOA/BEAM data** — skipped in v1
- **Only ~143 records have any principal dimensions** (51 drillships, 87 semi-subs)
- All computed drafts are heuristic estimates flagged `draft_estimated=True`

## v1 Scope

- `_RIG_TYPE_HULL_FORM_MAP`: drillship -> monohull, semi_submersible -> twin-hull, jack_up -> barge
- `estimate_rig_hull_coefficients(rig_type)` — returns Cb, Cm, Cp, hull_form
- `_estimate_draft(record, rig_type)` — L/D heuristics
- `register_drilling_rigs(records)` — normalize, estimate draft, map hull form, register

## Acceptance Criteria

- [ ] `estimate_rig_hull_coefficients` returns Cb/Cm/Cp with Cp = Cb/Cm identity
- [ ] Drillship Cb in [0.55, 0.70], Semi-sub Cb in [0.40, 0.60], Jack-up Cb in [0.75, 0.90]
- [ ] `register_drilling_rigs` skips records without LOA+BEAM, returns (added, skipped)
- [ ] Smoke test: ~138 rigs registered from full CSV, ~2,072 skipped
- [ ] All existing fleet adapter tests pass unchanged
- [ ] 10 new tests added and passing

## Dependencies

- #1859 (vessel fleet adapter pattern) — DONE
- #1319 (hull form parametric design) — DONE
EOF
)"
```

```bash
# DRAFT ONLY — #2062: Add plan-review label
gh issue edit 2062 --add-label "status:plan-review"
```

```bash
# DRAFT ONLY — #2062: Post summary comment
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
3. Implementation via TDD-first approach
EOF
)"
```

```bash
# DRAFT ONLY — #2062: After user approval
gh issue edit 2062 --add-label "status:plan-approved"
```

---

### Issue #2063 — Wire Drilling Riser Components

```bash
# DRAFT ONLY — #2063: Post summary comment
gh issue comment 2063 --body "$(cat <<'EOF'
## Stage-2 Execution Pack Complete

**Dossier**: `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md`
**Execution pack**: `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-1-drilling-riser-execution-pack.md`

### Fresh Status (2026-04-09)
- All dossier claims verified against repo — 2 minor corrections (export count: 13 not 12; tension calc: 422.58 not 421.98 kN)
- `adapter.py` gap confirmed — no adapter connects worldenergydata CSV to calculation module
- #1859 dependency DONE, adapter pattern established in `ship_data.py`
- CSV data (36 records), loader, schemas all present and validated

### Scope
- 2 new files: `adapter.py` + `test_adapter_integration.py`
- 2 modified files: `__init__.py` (3 new exports) + `conftest.py` (CSV fixture)
- TDD-first, cross-review required per workspace-hub policy

### Next Step
Apply `status:plan-review` label, review the execution pack, then `status:plan-approved` to unblock implementation.
EOF
)"
```

```bash
# DRAFT ONLY — #2063: Add plan-review label
gh issue edit 2063 --add-label "status:plan-review"
```

```bash
# DRAFT ONLY — #2063: After human approval, swap labels
gh issue edit 2063 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

---

## 3. Commands Grouped by Action Type

### 3A. Comment Commands (10 issues)

All `gh issue comment` commands — post plan summaries and findings.

```bash
# DRAFT ONLY — Batch: Post comments on all 10 issues

# #2053
gh issue comment 2053 --body "$(cat <<'EOF'
## Plan Review Summary (Stage-2 Execution Pack)
**Status**: 4 of 5 scope items implemented (commit 77b47195). Remaining: production_rate_bopd (recommend split to follow-up) + Norwegian NCS case studies (blocked on data). Run full test suite, then approve if green.
EOF
)"

# #2054
gh issue comment 2054 --body "$(cat <<'EOF'
## Plan Review Notes (Stage-2 Execution Pack)
**Scope**: 1 file + 1 test file. Inline Arps math, no new deps. Decisions needed: reservoir_size_mmbbl semantics, b_factor default, _production_factors() extraction.
Pack: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-9-decline-curve-execution-pack.md
EOF
)"

# #2055
gh issue comment 2055 --body "$(cat <<'EOF'
## Stage-2 Scoping Decisions (2026-04-09)
Equipment data source: manual backfill for 10 GoM fields. Architecture: band-level aggregation (MVP). CostDataPoint schema: no changes. cost_correlation.py: worldenergydata/subseaiq/analytics/.
Pack: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-8-subsea-cost-execution-pack.md
EOF
)"

# #2056
gh issue comment 2056 --body "$(cat <<'EOF'
## Stage-2 Finding: Threshold Regression
**Bug**: governance-checkpoints.yaml:54 has threshold: 5000 — should be 200. Introduced in d4f46c770 (Phase 2c). Fix: one-line change. 3 of 4 original gaps already resolved by overnight implementation.
EOF
)"

# #2057
gh issue comment 2057 --body "$(cat <<'EOF'
## Stage-2 Status Report (2026-04-09)
All 4 skill deliverables implemented (commits e582d7e70..ef8e7826b). Remaining cleanup: 5 broken links, 4 smoke tests, SESSION-GOVERNANCE.md update, duplicate reconciliation.
EOF
)"

# #2058
gh issue comment 2058 --body "$(cat <<'EOF'
## Stage-2 Plan Review — Ready for Approval
All 6 features unimplemented (verified). benchmarks.py at 572 lines — new functions must go in architecture_patterns.py. Coordinate with #2055 (wip:ace-linux-1).
Pack: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-5-architecture-patterns-execution-pack.md
EOF
)"

# #2059
gh issue comment 2059 --body "$(cat <<'EOF'
## Stage-2 Plan Review Packet
Infrastructure complete. Remaining work is test-only (~80-120 lines). 5 open gaps: BALDER fixture, parametrized stability test, CSV bulk test, GZ reasonableness, assumed-vs-measured docs.
Pack: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-4-vessel-stability-execution-pack.md
EOF
)"

# #2060
gh issue comment 2060 --body "$(cat <<'EOF'
## Plan Review — Stage-2 Execution Pack
Scope: 4 timeline fields + 3 new functions + 28 tests. 4 files. Decision needed: accept benchmarks.py growth to ~700 or extract timeline.py?
Pack: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-3-timeline-benchmarks-execution-pack.md
EOF
)"

# #2062
gh issue comment 2062 --body "$(cat <<'EOF'
## Stage-2 Execution Pack Complete
v1 targets ~138 rigs (51 drillships, 87 semi-subs). Draft estimation via L/D heuristics. 10 new tests, 6 files modified.
Pack: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-2-drilling-rig-execution-pack.md
EOF
)"

# #2063
gh issue comment 2063 --body "$(cat <<'EOF'
## Stage-2 Execution Pack Complete
Dossier verified, 2 minor corrections. adapter.py gap confirmed. Scope: 2 new files + 2 modified files. TDD-first.
Pack: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-1-drilling-riser-execution-pack.md
EOF
)"
```

### 3B. Label Commands — `status:plan-review` (Wave 1)

Apply to all issues except #2055 (which gets `needs-refinement` first).

```bash
# DRAFT ONLY — Wave 1: Apply plan-review labels to 9 issues
gh issue edit 2053 --add-label "status:plan-review"
gh issue edit 2054 --add-label "status:plan-review"
gh issue edit 2056 --add-label "status:plan-review"
gh issue edit 2057 --add-label "status:plan-review"
gh issue edit 2058 --add-label "status:plan-review"
gh issue edit 2059 --add-label "status:plan-review"
gh issue edit 2060 --add-label "status:plan-review"
gh issue edit 2062 --add-label "status:plan-review"
gh issue edit 2063 --add-label "status:plan-review"

# Special: #2055 gets needs-refinement first
gh issue edit 2055 --add-label "status:needs-refinement"
```

### 3C. Label Commands — `status:plan-approved` (Wave 2, after human review)

```bash
# DRAFT ONLY — Wave 2: Promote to plan-approved AFTER human reviews each pack
gh issue edit 2053 --add-label "status:plan-approved"
gh issue edit 2054 --remove-label "status:plan-review" --add-label "status:plan-approved"
gh issue edit 2056 --add-label "status:plan-approved"
gh issue edit 2057 --add-label "status:plan-approved" --remove-label "status:plan-review"
gh issue edit 2058 --remove-label "status:plan-review" --add-label "status:plan-approved"
gh issue edit 2059 --remove-label "status:plan-review" --add-label "status:plan-approved"
gh issue edit 2060 --remove-label "status:plan-review" --add-label "status:plan-approved"
gh issue edit 2062 --add-label "status:plan-approved"
gh issue edit 2063 --remove-label "status:plan-review" --add-label "status:plan-approved"

# Special: #2055 goes needs-refinement → plan-review → plan-approved (3-step)
gh issue edit 2055 --remove-label "status:needs-refinement" --add-label "status:plan-review"
gh issue edit 2055 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

### 3D. Issue Body Edit Commands (2 issues)

```bash
# DRAFT ONLY — #2057: Full body replacement with completion status
gh issue edit 2057 --body "$(cat <<'BODY'
## Context
#1839 Phase 3: rebuild lost session infrastructure skills.

## Deliverables — All DONE
1. session-start-routine — `.claude/skills/coordination/session-start-routine/SKILL.md`
2. session-corpus-audit — slim at coordination/ + original at workspace-hub/
3. comprehensive-learning — wrapper at coordination/comprehensive-learning-wrapper/
4. cross-review-policy — `.claude/skills/coordination/cross-review-policy/SKILL.md`

## Remaining Cleanup
- [ ] Fix 5 broken links in _internal/meta/ skills
- [ ] Create 4 smoke tests
- [ ] Update SESSION-GOVERNANCE.md
- [ ] Reconcile duplicate session-corpus-audit
BODY
)"

# DRAFT ONLY — #2062: Full body replacement with refined scope
gh issue edit 2062 --title "feat(naval-arch): drilling rig fleet adapter — drillship and semi-sub hull form validation (~138 rigs with geometry)"
gh issue edit 2062 --body "$(cat <<'EOF'
## Summary
Adapter to register drilling rigs from the vessel fleet CSV into the hull form validation pipeline. v1 targets drillships and semi-submersibles with LOA+BEAM data (~138 of 2,210 rigs).

## Data Limitations
- NO DRAFT_M column, DISPLACEMENT_TONNES 100% empty
- Jack-ups (1,009 rigs) have zero LOA/BEAM — skipped in v1
- All drafts are heuristic estimates flagged draft_estimated=True

## Acceptance Criteria
- [ ] estimate_rig_hull_coefficients returns Cb/Cm/Cp with Cp = Cb/Cm
- [ ] register_drilling_rigs: ~138 registered, ~2,072 skipped
- [ ] All existing tests pass unchanged, 10 new tests

## Dependencies
- #1859 (DONE), #1319 (DONE)
EOF
)"
```

### 3E. Issue Title Edit Commands (1 issue)

```bash
# DRAFT ONLY — #2062: Update title to reflect realistic v1 scope
gh issue edit 2062 --title "feat(naval-arch): drilling rig fleet adapter — drillship and semi-sub hull form validation (~138 rigs with geometry)"
```

### 3F. Additional Label Commands (1 issue)

```bash
# DRAFT ONLY — #2058: Add priority label
gh issue edit 2058 --add-label "priority:medium"
```

### 3G. Issue Close Commands (1 issue, post-implementation only)

```bash
# DRAFT ONLY — #2056: Close ONLY after threshold fix verified
gh issue close 2056 --comment "Completed. All 4 gaps resolved: tool-call ceiling (200), error-loop-breaker (3x), strict review gate, threshold regression fixed."
```

### 3H. Follow-Up Issue Creation (1 issue)

```bash
# DRAFT ONLY — Create follow-up for #2053 scope item 1
gh issue create \
  --title "feat(field-dev): add production_rate_bopd to SubseaProject and extract correlations" \
  --label "enhancement,cat:engineering,agent:claude" \
  --body "$(cat <<'EOF'
Follow-up to #2053 scope item 1. Add production_rate_bopd field to SubseaProject, update load_projects(), extract correlations.
Depends on: #2053 (done), #1861 (done)
EOF
)"
```

---

## 4. Batch Order Recommendation

Execute in this sequence to respect the label gate workflow:

| Wave | Action | Issues | Prerequisite |
|------|--------|--------|-------------|
| **W0** | Read all 10 execution packs | All | None |
| **W1** | Post plan-summary comments | #2053-#2063 (all 10) | W0 complete |
| **W2** | Apply `status:plan-review` labels | #2053, #2054, #2056-#2060, #2062, #2063 (9 issues) | W1 complete |
| **W2b** | Apply `status:needs-refinement` to #2055 | #2055 | W1 complete |
| **W3** | Edit issue bodies/titles | #2057 (body), #2062 (title+body) | W1 complete |
| **W4** | Add optional labels | #2058 (priority:medium) | Any time |
| **GATE** | **Human reviews each execution pack** | All | W1-W3 complete |
| **W5** | Apply `status:plan-approved` | Per-issue as reviewed | GATE passed per issue |
| **W6** | Dispatch implementation prompts | Per-issue | W5 per issue |
| **W7** | Close fully-complete issues | #2056 (after fix), #2057 (after cleanup) | Implementation verified |
| **W8** | Create follow-up issues | #2053 spinoff | Any time after W5 |

### Quick-Start Sequence (minimum viable)

If the operator wants to move fast, the absolute minimum sequence is:

1. Run all W1 comment commands (10 comments, can be done in parallel)
2. Run all W2 label commands (10 labels)
3. Review packs, then run W5 for approved issues
4. Dispatch implementation

---

## 5. Copy/Paste Blocks — Exact Commands Only

### Block A: All plan-review labels (one-shot)

```bash
# DRAFT ONLY — Apply plan-review to 9 issues + needs-refinement to 1
gh issue edit 2053 --add-label "status:plan-review"
gh issue edit 2054 --add-label "status:plan-review"
gh issue edit 2055 --add-label "status:needs-refinement"
gh issue edit 2056 --add-label "status:plan-review"
gh issue edit 2057 --add-label "status:plan-review"
gh issue edit 2058 --add-label "status:plan-review"
gh issue edit 2059 --add-label "status:plan-review"
gh issue edit 2060 --add-label "status:plan-review"
gh issue edit 2062 --add-label "status:plan-review"
gh issue edit 2063 --add-label "status:plan-review"
```

### Block B: All plan-approved labels (after review)

```bash
# DRAFT ONLY — Promote all to plan-approved (run individually as each is reviewed)
gh issue edit 2053 --add-label "status:plan-approved"
gh issue edit 2054 --remove-label "status:plan-review" --add-label "status:plan-approved"
gh issue edit 2055 --remove-label "status:needs-refinement" --add-label "status:plan-approved"
gh issue edit 2056 --add-label "status:plan-approved"
gh issue edit 2057 --add-label "status:plan-approved" --remove-label "status:plan-review"
gh issue edit 2058 --remove-label "status:plan-review" --add-label "status:plan-approved"
gh issue edit 2059 --remove-label "status:plan-review" --add-label "status:plan-approved"
gh issue edit 2060 --remove-label "status:plan-review" --add-label "status:plan-approved"
gh issue edit 2062 --add-label "status:plan-approved"
gh issue edit 2063 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

---

## 6. Final Operator Checklist

- [ ] Read all 10 execution packs in `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/`
- [ ] Review each `gh` command body payload before executing
- [ ] Confirm `status:plan-review` label exists in the repo (create if missing)
- [ ] Confirm `status:plan-approved` label exists in the repo (create if missing)
- [ ] Confirm `status:needs-refinement` label exists (for #2055)
- [ ] Run Wave 1 comments (Section 3A)
- [ ] Run Wave 2 plan-review labels (Section 3B / Block A)
- [ ] Run body/title edits for #2057 and #2062 (Section 3D/3E)
- [ ] **HUMAN REVIEW GATE** — read each execution pack and decide approve/reject per issue
- [ ] Run Wave 5 plan-approved labels selectively (Block B — only for approved issues)
- [ ] For #2055: resolve 4 scoping decisions before promoting past needs-refinement
- [ ] For #2056: verify threshold fix before closing
- [ ] For #2057: verify cleanup (broken links, smoke tests) before closing
- [ ] For #2053: decide whether to create follow-up issue for production_rate_bopd
- [ ] **Do NOT execute `gh issue close` until implementation is verified**
- [ ] **Do NOT execute `gh issue create` until follow-up scope is confirmed**

---

## Appendix: Issue Summary Table

| Issue | Title (short) | Pack | Readiness | Special Notes |
|---|---|---|---|---|
| #2053 | Concept selection probability matrix | terminal-10 | 90% done, verify tests | Follow-up issue for production_rate_bopd |
| #2054 | Production decline curve economics | terminal-9 | Ready for plan-review | Decisions: OOIP semantics, b_factor default |
| #2055 | Subsea cost benchmarking | terminal-8 | Needs refinement | Data dependency unmet (equipment counts) |
| #2056 | Session governance Phase 2 | terminal-7 | 90% done, threshold bug | One-line fix: 5000 -> 200 |
| #2057 | Session governance Phase 3 | terminal-6 | 95% done, cleanup only | All 4 skills built; broken links remain |
| #2058 | Subsea architecture patterns | terminal-5 | Ready for plan-review | Must split to architecture_patterns.py |
| #2059 | Real vessel stability tests | terminal-4 | Ready for plan-review | Test-only, ~80-120 lines |
| #2060 | Project timeline benchmarks | terminal-3 | Ready for plan-review | Decision: accept 700-line benchmarks.py? |
| #2062 | Drilling rig fleet adapter | terminal-2 | Ready for plan-review | Title/body need refinement first |
| #2063 | Wire drilling riser components | terminal-1 | Ready for plan-review | Small scope, well-bounded |
