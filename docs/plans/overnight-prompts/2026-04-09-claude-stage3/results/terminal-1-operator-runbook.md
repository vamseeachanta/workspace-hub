# Morning Operator Runbook -- 2026-04-09 Overnight Batch Results

**Generated**: 2026-04-09 (Stage-3 synthesis of 10 Stage-2 execution packs)
**Operator**: Vamsee Achanta
**Batch**: `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/`

---

## 1. Executive Summary

The overnight batch processed 10 issues across two domains: **subsea/naval engineering** (7 issues) and **AI governance** (3 issues). Two governance issues (#2057, #2056) received significant implementation overnight and are near-complete -- one has a **threshold regression bug** requiring an urgent 1-line fix. Issue #2053 (concept selection) was also largely implemented overnight (4 of 5 scope items). The remaining 7 issues produced validated execution packs with self-contained implementation prompts ready for dispatch after `status:plan-approved` labeling.

**Key findings:**
- **1 bug discovered**: `governance-checkpoints.yaml:54` has `threshold: 5000` (should be `200`) -- tool-call ceiling is effectively unenforced
- **1 data blocker**: #2055 subsea cost benchmarking is blocked on missing equipment count fields in `subseaiq-scan-latest.json`
- **1 file contention risk**: `benchmarks.py` (572 lines) is touched by #2060, #2058, and #2055 -- schedule sequentially
- **3 issues closable today** with minimal effort (#2057, #2056, #2053)
- **All 10 issues** lack the `status:plan-approved` gate label

---

## 2. 10-Issue Table

| # | Issue | Title (short) | Recommendation | Fastest Next Action | Blocker |
|---|-------|---------------|----------------|---------------------|---------|
| 1 | #2063 | Drilling riser adapter | Approve and dispatch | `gh issue edit 2063 --add-label "status:plan-review"` | `status:plan-approved` label |
| 2 | #2062 | Drilling rig fleet adapter (~138 rigs) | Refine issue scope, then approve | Update title/body to reflect v1 scope (~138 rigs, not 2,210) | Issue overstates scope; needs refinement |
| 3 | #2060 | Timeline benchmarks | Decide on file size, then approve | Decide: accept benchmarks.py growth to ~700 lines or extract `timeline.py` | `benchmarks.py` at 572 lines; decision needed |
| 4 | #2059 | Vessel stability tests | Approve and dispatch (test-only) | `gh issue edit 2059 --add-label "status:plan-review"` | `status:plan-approved` label |
| 5 | #2058 | Subsea architecture patterns | Approve file-split strategy | Confirm `architecture_patterns.py` split; check #2055 WIP status | File split decision + #2055 contention |
| 6 | #2057 | Governance Phase 3 (skills) | Cleanup and close (95% done) | Run verification commands from pack section 5a | Retroactive approval needed; 5 broken links |
| 7 | #2056 | Governance Phase 2 (hooks) | **FIX BUG**, then close (90% done) | Fix `threshold: 5000` -> `200` in `governance-checkpoints.yaml:54` | Threshold regression bug |
| 8 | #2055 | Subsea cost benchmarking | Needs refinement (data gap) | Decide: manual backfill, wait for scraping, or use synthetic data | Equipment count data missing from JSON |
| 9 | #2054 | Decline curve economics | Approve and dispatch | Clarify `reservoir_size_mmbbl` semantics (OOIP vs EUR) | `status:plan-approved` + 1 design decision |
| 10 | #2053 | Concept selection matrix | Verify tests, split remainder, close | `cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short` | Test verification + cross-review gate |

---

## 3. Morning Sequence (First 10 Actions, Strict Order)

**Rationale**: Bug fix first, then close near-done items to clear the board, then approve new work in dependency order.

| Step | Action | Issue | Time Est. | Command / Details |
|------|--------|-------|-----------|-------------------|
| 1 | **Fix threshold bug** | #2056 | 2 min | Edit `scripts/workflow/governance-checkpoints.yaml` line 54: change `threshold: 5000` to `threshold: 200` |
| 2 | Verify threshold fix | #2056 | 1 min | `grep 'threshold:' scripts/workflow/governance-checkpoints.yaml` |
| 3 | Run governance tests | #2056 | 2 min | `uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v --tb=short` |
| 4 | Verify #2053 tests | #2053 | 3 min | `cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short` |
| 5 | Verify #2057 skills exist | #2057 | 1 min | `for s in session-start-routine session-corpus-audit cross-review-policy comprehensive-learning-wrapper; do head -5 .claude/skills/coordination/$s/SKILL.md; done` |
| 6 | Label 3 quick wins for review | #2056, #2057, #2053 | 1 min | `gh issue edit 2056 --add-label "status:plan-approved"` (repeat for 2057, 2053) |
| 7 | Post threshold bug comment | #2056 | 1 min | Use operator command from terminal-7 execution pack section 5.2 |
| 8 | Label 3 ready issues for review | #2063, #2059, #2054 | 1 min | `gh issue edit 2063 --add-label "status:plan-review"` (repeat for 2059, 2054) |
| 9 | Decide benchmarks.py strategy | #2060, #2058 | 5 min | Choose: (a) accept 700-line growth, or (b) extract `timeline.py` and `architecture_patterns.py` |
| 10 | Triage #2055 data gap | #2055 | 5 min | Decide equipment count data source: manual backfill vs wait for scraping pipeline |

---

## 4. High-Risk Items vs Quick Wins

### HIGH-RISK ITEMS

| Issue | Risk | Severity | Mitigation |
|-------|------|----------|------------|
| #2056 | **Threshold bug**: tool-call ceiling at 5000 instead of 200 -- governor STOP never fires at documented limit | **CRITICAL** | One-line fix: `governance-checkpoints.yaml:54` `threshold: 5000` -> `200` |
| #2055 | **Data blocker**: equipment count fields (num_trees, num_manifolds, tieback_distance_km) absent from `subseaiq-scan-latest.json` | **HIGH** | Manual backfill for 10 GoM fields, or defer issue |
| #2058 | **File contention**: `benchmarks.py` touched by #2060, #2058, #2055 -- concurrent implementation causes merge conflicts | **MEDIUM** | Execute #2060 before #2058; defer #2055 until both land |
| #2062 | **Scope overstatement**: issue says "2,210 rigs" but only ~138 have geometry data | **MEDIUM** | Update title/body before approval to set realistic expectations |
| #2059 | **Monohull coefficients for semi-subs**: `_DEFAULT_CB=0.65` used for all vessel types | **LOW** | Tests document assumed vs measured; optional Cb/Cw override in scope |

### QUICK WINS (closable today)

| Issue | Current State | Remaining Work | Est. Effort |
|-------|--------------|----------------|-------------|
| #2057 | All 4 skills implemented overnight | Fix 5 broken links, 4 smoke tests, governance doc update | 15-20 min Claude session |
| #2056 | 3 of 4 gaps resolved overnight | 1-line threshold fix + doc update + 1 integration test | 10-15 min Claude session |
| #2053 | 4 of 5 scope items implemented | Verify tests green, split `production_rate_bopd` to follow-up, cross-review | 15 min verification + review dispatch |
| #2063 | Execution pack complete, all prereqs met | Full TDD implementation (~190 lines) | 1 focused Claude session |
| #2059 | Execution pack complete, infra done | Test-only work (~80-120 new lines) | 1 short Claude session |

---

## 5. File Paths to Consult Per Issue

### #2063 -- Drilling Riser Adapter
| File | Role |
|------|------|
| `digitalmodel/src/digitalmodel/drilling_riser/__init__.py` | 13 exports; add 3 adapter exports |
| `digitalmodel/src/digitalmodel/drilling_riser/adapter.py` | **CREATE**: normalize + register + string weight |
| `digitalmodel/tests/drilling_riser/test_adapter_integration.py` | **CREATE**: 6+ integration tests |
| `digitalmodel/tests/drilling_riser/conftest.py` | Empty -- add CSV fixture |
| `worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv` | 36 curated records (read-only) |
| `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | Pattern reference: `normalize_fleet_record()` at L150 |

### #2062 -- Drilling Rig Fleet Adapter
| File | Role |
|------|------|
| `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | Add `register_drilling_rigs()`, `_estimate_draft()`, `_RIG_TYPE_HULL_FORM_MAP` |
| `digitalmodel/src/digitalmodel/naval_architecture/hull_form.py` | Add `estimate_rig_hull_coefficients()`, `_HULL_FORM_COEFFICIENTS` |
| `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Export 2 new functions |
| `digitalmodel/tests/naval_architecture/test_hull_form.py` | Add 5 tests |
| `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | Add 5 tests |
| `worldenergydata/data/modules/vessel_fleet/curated/drilling_rigs.csv` | 2,210 rows; ~138 with geometry |

### #2060 -- Timeline Benchmarks
| File | Role |
|------|------|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | Extend `SubseaProject` + `load_projects()` + add 3 public functions (572 -> ~700 lines) |
| `digitalmodel/tests/field_development/test_benchmarks.py` | Add 5 test classes (~28 tests) |
| `worldenergydata/subseaiq/analytics/normalize.py` | Add 4 field aliases + int coercion |
| `digitalmodel/src/digitalmodel/field_development/__init__.py` | Re-export 3 new timeline functions |

### #2059 -- Vessel Stability Tests
| File | Role |
|------|------|
| `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | Add BALDER fixture, CSV bulk test, 3-vessel parametrized stability class |
| `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | Optional: semi-sub Cb/Cw defaults at L267-268 |
| `worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv` | 17 vessels (Sleipnir, Thialf, Balder) |

### #2058 -- Subsea Architecture Patterns
| File | Role |
|------|------|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | Add 3 dataclass fields + `load_projects()` update only |
| `digitalmodel/src/digitalmodel/field_development/architecture_patterns.py` | **CREATE**: 4 analytical functions (~120 lines) |
| `digitalmodel/tests/field_development/test_architecture_patterns.py` | **CREATE**: ~15-20 tests |
| `worldenergydata/subseaiq/analytics/normalize.py` | Add 3 alias groups |

### #2057 -- Governance Phase 3 (Cleanup)
| File | Role |
|------|------|
| `.claude/skills/coordination/session-start-routine/SKILL.md` | Deliverable #1 (44 lines, done) |
| `.claude/skills/coordination/session-corpus-audit/SKILL.md` | Deliverable #2 slim version (58 lines, done) |
| `.claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md` | Deliverable #3 wrapper (143 lines, done) |
| `.claude/skills/coordination/cross-review-policy/SKILL.md` | Deliverable #4 (57 lines, done) |
| `docs/governance/SESSION-GOVERNANCE.md` | Needs #2057 section addition (475 lines) |
| `.claude/skills/_internal/meta/` | 5 broken `session-start-routine` links to fix |

### #2056 -- Governance Phase 2 (Bug Fix)
| File | Role |
|------|------|
| `scripts/workflow/governance-checkpoints.yaml` | **BUG**: line 54 `threshold: 5000` must be `200` |
| `.claude/hooks/session-governor-check.sh` | PreToolUse hook (99 lines, working) |
| `.claude/hooks/error-loop-tracker.sh` | PostToolUse hook (130 lines, working) |
| `scripts/enforcement/require-review-on-push.sh` | Strict default confirmed at L255 |
| `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` | Stale text: still says warning-based default |
| `tests/work-queue/test_session_governor.py` | 55 tests (add 1 production YAML test) |

### #2055 -- Subsea Cost Benchmarking
| File | Role |
|------|------|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | Add `cost_usd_mm` field + 5 cost functions |
| `data/field-development/subseaiq-scan-latest.json` | **DATA GAP**: needs equipment count backfill |
| `worldenergydata/subseaiq/analytics/cost_correlation.py` | **CREATE**: band-level merge helpers |
| `worldenergydata/src/worldenergydata/cost/data_collection/public_dataset.py` | 71 sanctioned cost records (read-only) |

### #2054 -- Decline Curve Economics
| File | Role |
|------|------|
| `digitalmodel/src/digitalmodel/field_development/economics.py` | Add `DeclineType` enum, 3 fields, extract `_production_factors()` helper (693 lines) |
| `digitalmodel/tests/field_development/test_economics.py` | Add 4 test classes (~18 tests, 590 lines) |

### #2053 -- Concept Selection Matrix
| File | Role |
|------|------|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | All new functions present (572 lines) |
| `digitalmodel/src/digitalmodel/field_development/concept_selection.py` | `concept_selection_with_benchmarks()` at L468 (525 lines) |
| `digitalmodel/tests/field_development/test_benchmarks.py` | New test classes at L471, L546, L707 (763 lines) |
| `digitalmodel/tests/field_development/test_concept_probability.py` | Dedicated test suite (408 lines) |

---

## 6. Final Recommendation Block

### Immediate Priority (do first, today)

1. **Fix #2056 threshold bug** -- the tool-call ceiling is unenforced. One-line change in `governance-checkpoints.yaml:54`. This is a production configuration defect.

2. **Verify and close #2053** -- run the test suite; if green, split `production_rate_bopd` to follow-up and request cross-review. Core value already delivered.

3. **Dispatch #2057 cleanup** -- paste the section 6 prompt from the terminal-6 execution pack into a Claude session. All skills exist; just link fixes + smoke tests.

### Batch Dispatch Order (after clearing the above)

Schedule these **sequentially** to avoid `benchmarks.py` contention:

| Wave | Issues | Reasoning |
|------|--------|-----------|
| Wave 1 | #2063 (riser adapter), #2059 (vessel stability), #2054 (decline curve) | Independent files. No contention. Can run in parallel terminals. |
| Wave 2 | #2060 (timeline benchmarks) | Touches `benchmarks.py`. Must land before Wave 3. |
| Wave 3 | #2058 (architecture patterns) | Touches `benchmarks.py` (fields only) + creates `architecture_patterns.py`. Depends on Wave 2. |
| Wave 4 | #2062 (drilling rig fleet) | Requires title/body refinement first. Independent of benchmarks.py. |
| Deferred | #2055 (subsea cost) | Blocked on equipment data. Resolve data gap before planning implementation. |

### Label Sequence (copy-paste ready)

```bash
# Step 1: Retroactive approval for completed work
gh issue edit 2057 --add-label "status:plan-approved"
gh issue edit 2056 --add-label "status:plan-approved"

# Step 2: Plan-review for ready issues
gh issue edit 2063 --add-label "status:plan-review"
gh issue edit 2059 --add-label "status:plan-review"
gh issue edit 2054 --add-label "status:plan-review"
gh issue edit 2053 --add-label "status:plan-review"

# Step 3: After reviewing each, promote to plan-approved
gh issue edit 2063 --remove-label "status:plan-review" --add-label "status:plan-approved"
gh issue edit 2059 --remove-label "status:plan-review" --add-label "status:plan-approved"
gh issue edit 2054 --remove-label "status:plan-review" --add-label "status:plan-approved"
gh issue edit 2053 --remove-label "status:plan-review" --add-label "status:plan-approved"

# Step 4: Issues needing decisions first
gh issue edit 2060 --add-label "status:plan-review"
gh issue edit 2058 --add-label "status:plan-review"
gh issue edit 2062 --add-label "status:plan-review"

# Step 5: Blocked issue
gh issue edit 2055 --add-label "status:needs-refinement"
```

### Verification Commands (confirm current state before acting)

```bash
# 1. Confirm threshold bug
grep 'threshold:' scripts/workflow/governance-checkpoints.yaml

# 2. Confirm #2057 skills present
ls -la .claude/skills/coordination/*/SKILL.md

# 3. Confirm #2053 test suite passes
cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short

# 4. Confirm benchmarks.py current size (contention planning)
wc -l digitalmodel/src/digitalmodel/field_development/benchmarks.py

# 5. Confirm equipment data gap
python3 -c "import json; d=json.load(open('data/field-development/subseaiq-scan-latest.json')); print(list(d['gom_fields'][0].keys()))"
```

### All Execution Pack Paths

| Terminal | Execution Pack |
|----------|----------------|
| 1 | `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-1-drilling-riser-execution-pack.md` |
| 2 | `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-2-drilling-rig-execution-pack.md` |
| 3 | `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-3-timeline-benchmarks-execution-pack.md` |
| 4 | `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-4-vessel-stability-execution-pack.md` |
| 5 | `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-5-architecture-patterns-execution-pack.md` |
| 6 | `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-6-governance-phase3-execution-pack.md` |
| 7 | `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-7-governance-phase2-execution-pack.md` |
| 8 | `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-8-subsea-cost-execution-pack.md` |
| 9 | `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-9-decline-curve-execution-pack.md` |
| 10 | `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-10-concept-selection-execution-pack.md` |
