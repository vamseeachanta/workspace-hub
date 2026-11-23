# Priority / Closure Matrix — Stage-2 Execution Packs (2026-04-09)

Generated from 10 stage-2 execution packs produced overnight.
Source: `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/`

---

## 1. Scoring Model

Each issue is scored on 4 dimensions (1–5 scale). Lower Effort / Risk / Gating is better; higher Impact is better.

| Dimension | What It Measures | Scale |
|-----------|-----------------|-------|
| **Impact** | Downstream value: unblocks other work, fixes production bugs, delivers user-visible capability | 1 = nice-to-have cleanup → 5 = critical bug fix or high-value feature |
| **Effort** | Work remaining to close the issue, including code, tests, data backfill | 1 = ≤15 min / ≤20 LOC → 5 = multi-session / 500+ LOC |
| **Risk** | Probability of encountering problems: data gaps, contention, unknown unknowns | 1 = trivial, pattern-following → 5 = missing data, cross-issue conflicts |
| **Gating Friction** | Human decisions / approvals blocking progress before implementation can start | 1 = just needs label → 5 = multiple scoping decisions + external data dependency |

**Composite Priority Score** = (Impact × 2) − Effort − Risk − Gating

Higher score = act sooner. Range: −8 (hard, risky, blocked) to +7 (high-value, trivial, unblocked).

---

## 2. Ranked Table — All 10 Issues

| Rank | Issue | Title (short) | Impact | Effort | Risk | Gating | Score | Final Recommendation |
|------|-------|--------------|--------|--------|------|--------|-------|---------------------|
| **1** | #2056 | Governance Phase 2 — threshold bug fix | 4 | 1 | 1 | 2 | **+4** | FIX-AND-CLOSE |
| **2** | #2053 | Concept Selection — verify & close | 4 | 1 | 1 | 2 | **+4** | VERIFY-AND-CLOSE |
| **3** | #2057 | Governance Phase 3 — cleanup hygiene | 2 | 1 | 1 | 1 | **+1** | CLEANUP-AND-CLOSE |
| **4** | #2063 | Drilling Riser adapter | 3 | 2 | 1 | 2 | **+1** | READY FOR PLAN REVIEW |
| **5** | #2059 | Vessel Stability test cases | 3 | 2 | 2 | 2 | **0** | READY FOR PLAN REVIEW |
| **6** | #2054 | Decline Curve economics | 3 | 2 | 2 | 3 | **−1** | READY FOR PLAN REVIEW |
| **7** | #2060 | Timeline Benchmarks | 3 | 3 | 2 | 3 | **−2** | READY AFTER LABEL UPDATE |
| **8** | #2062 | Drilling Rig Fleet adapter | 3 | 3 | 2 | 3 | **−2** | REFINE ISSUE FIRST |
| **9** | #2058 | Architecture Patterns | 3 | 3 | 3 | 3 | **−3** | NEEDS FILE-SPLIT DECISION |
| **10** | #2055 | Subsea Cost Benchmarking | 4 | 4 | 4 | 5 | **−5** | NEEDS REFINEMENT |

---

## 3. Fastest-to-Close List

Issues ranked by minimal remaining work (Effort + Gating, ascending). These can be closed with quick focused sessions.

| Rank | Issue | Remaining Work | Est. Time |
|------|-------|---------------|-----------|
| 1 | **#2057** | Fix 5 broken links, create 4 smoke tests, update `docs/governance/SESSION-GOVERNANCE.md` | ~15 min |
| 2 | **#2056** | Change `threshold: 5000` → `200` in `scripts/workflow/governance-checkpoints.yaml:54`, update `docs/standards/REVIEW_GATE_BYPASS_POLICY.md`, add 1 integration test | ~15 min |
| 3 | **#2053** | Run test suite at `digitalmodel/tests/field_development/`, request cross-review, split production_rate_bopd to follow-up issue, close | ~20 min |
| 4 | **#2059** | Test-only: add BALDER fixture + CSV bulk test + parametrized 3-vessel stability class to `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | ~1 hr |
| 5 | **#2063** | Create `digitalmodel/src/digitalmodel/drilling_riser/adapter.py` (~80 lines) + integration tests following `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py:150` pattern | ~1 hr |

---

## 4. Best-to-Implement-Next List

Ranked by impact-to-effort ratio: highest value per unit of investment. These are the optimal use of morning engineering time.

| Rank | Issue | Why Now | Value Delivered |
|------|-------|---------|----------------|
| 1 | **#2056** | 1-line bug fix restores 200-call ceiling enforcement. `scripts/workflow/governance-checkpoints.yaml:54` threshold regression means governor never fires STOP at documented limit. Every session since `d4f46c770` has been running without the safety net. | Restores production safety governance |
| 2 | **#2053** | 4 of 5 scope items already implemented (commit `77b47195`). Verify `digitalmodel/tests/field_development/test_benchmarks.py` passes, split scope item 1, close. Highest-value code already written. | Unlocks concept selection analytics for downstream issues |
| 3 | **#2063** | All prerequisites met: 13 functions in `digitalmodel/src/digitalmodel/drilling_riser/`, 36 CSV records in `worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv`, adapter pattern proven at `ship_data.py:150`. Clean, bounded scope. | Connects real equipment data to riser calculations |
| 4 | **#2054** | Single-file change to `digitalmodel/src/digitalmodel/field_development/economics.py` (693 lines). Inline Arps math replaces hardcoded linear decline at lines 420-435 and 617-633. No new dependencies. | Proper decline curves for screening economics |
| 5 | **#2059** | Test-only work against existing infrastructure. `digitalmodel/src/digitalmodel/naval_architecture/floating_platform_stability.py` and fleet adapter already complete. Validates the entire stability pipeline end-to-end with real vessel data from `worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv`. | Pipeline validation + documentation of assumed vs measured params |

---

## 5. Needs-Refinement-First List

These issues have gating decisions that must be resolved before implementation can proceed.

| Issue | Blocking Decisions | Key Files Affected | Action |
|-------|-------------------|--------------------|--------|
| **#2055** | (1) Equipment data source: manual backfill vs wait for scraping pipeline. (2) Correlation architecture: band-level vs per-project. (3) CostDataPoint schema: extend or defer. (4) cost_correlation.py location. Data gap: `data/field-development/subseaiq-scan-latest.json` has zero equipment count fields (num_trees, num_manifolds, tieback_distance_km). | `digitalmodel/src/digitalmodel/field_development/benchmarks.py`, `worldenergydata/subseaiq/analytics/cost_correlation.py` (new), `data/field-development/subseaiq-scan-latest.json` | Resolve all 4 decisions → `status:needs-refinement` → `status:plan-review` |
| **#2058** | (1) File split required: `benchmarks.py` at 572 lines, adding 4 functions pushes to ~700. Must create `digitalmodel/src/digitalmodel/field_development/architecture_patterns.py`. (2) Contention with #2055 which has `wip:ace-linux-1` label and may touch `SubseaProject` dataclass concurrently. | `digitalmodel/src/digitalmodel/field_development/benchmarks.py`, `worldenergydata/subseaiq/analytics/normalize.py` | Approve file split → coordinate with #2055 → `status:plan-review` |
| **#2062** | (1) Issue title/body overstate scope: says "2,210 rigs" but realistic v1 is ~138 rigs with geometry (51 drillships + 87 semi-subs). Jack-ups have zero LOA/BEAM data. (2) No DRAFT_M column — requires draft estimation via L/D heuristics. | `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py`, `digitalmodel/src/digitalmodel/naval_architecture/hull_form.py`, `worldenergydata/data/modules/vessel_fleet/curated/drilling_rigs.csv` | Update title/body with v1 scope → `status:plan-review` |
| **#2060** | (1) `benchmarks.py` already at 572 lines — accept growth to ~700 or extract `timeline.py`? (2) SubseaIQ timeline field aliases are speculative (educated guesses). | `digitalmodel/src/digitalmodel/field_development/benchmarks.py`, `worldenergydata/subseaiq/analytics/normalize.py` | Decide on file growth policy → `status:plan-review` |

---

## 6. Final Recommended Morning Order

Optimized for: close quick wins first (momentum + governance fixes), then tackle highest-value bounded work, defer blocked items.

| Order | Issue | Action | Gate | Est. Session |
|-------|-------|--------|------|-------------|
| **1st** | #2056 | Fix `governance-checkpoints.yaml:54` threshold 5000→200, update bypass policy doc, add YAML integration test | Apply `status:plan-approved` retroactively | 15 min |
| **2nd** | #2053 | Run `uv run pytest digitalmodel/tests/field_development/ -v`, confirm green, split production_rate_bopd to follow-up, request cross-review, close | Apply `status:plan-review` then `status:plan-approved` | 20 min |
| **3rd** | #2057 | Fix 5 broken `session-start-routine` links in `.claude/skills/_internal/`, create 4 smoke tests, update `SESSION-GOVERNANCE.md`, reconcile duplicate session-corpus-audit | Apply `status:plan-approved` retroactively | 15 min |
| **4th** | #2063 | Full TDD implementation: `drilling_riser/adapter.py` + integration tests, following `ship_data.py:150` normalize/register pattern | `status:plan-review` → `status:plan-approved` | 1 hr |
| **5th** | #2059 | Test-only: BALDER fixture, CSV bulk registration test, parametrized 3-vessel stability test against `construction_vessels.csv` | `status:plan-review` → `status:plan-approved` | 1 hr |
| **6th** | #2054 | TDD: `DeclineType` enum, 3 EconomicsInput fields, extract `_production_factors()` helper, inline Arps math at `economics.py:420` and `:617` | `status:plan-review` → `status:plan-approved` (needs reservoir_size semantics decision) | 1.5 hr |
| **7th** | #2060 | Decide file growth policy, then TDD: 4 SubseaProject timeline fields, 3 new functions, normalizer aliases | File-size decision → `status:plan-approved` | 2 hr |
| **8th** | #2062 | Refine issue title/body to v1 scope (~138 rigs), then TDD: `register_drilling_rigs()`, hull form coefficients, draft estimation | Title/body update → `status:plan-approved` | 2 hr |
| **9th** | #2058 | Approve file split, coordinate with #2055, then TDD: `architecture_patterns.py` + 4 analytical functions + normalizer aliases | File split decision + #2055 coordination → `status:plan-approved` | 2 hr |
| **10th** | #2055 | Resolve 4 scoping decisions, manually backfill equipment counts for 10 GoM fields in `subseaiq-scan-latest.json`, then implement band-level cost correlation | 4 decisions + data backfill → `status:plan-approved` | 3+ hr |

### Morning Quick-Start Script (First 3 Issues)

```bash
# 1. Fix #2056 threshold bug — verify it exists first
grep 'threshold:' scripts/workflow/governance-checkpoints.yaml

# 2. Verify #2053 tests pass
cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short

# 3. Verify #2057 skill files exist
for skill in session-start-routine session-corpus-audit cross-review-policy comprehensive-learning-wrapper; do
  echo "--- $skill ---"
  head -5 .claude/skills/coordination/$skill/SKILL.md 2>/dev/null || echo "MISSING"
done
```

---

## Appendix: Concrete Repo References

| # | File Path | Relevance |
|---|-----------|-----------|
| 1 | `scripts/workflow/governance-checkpoints.yaml:54` | #2056 threshold bug: `5000` should be `200` |
| 2 | `digitalmodel/src/digitalmodel/field_development/benchmarks.py` (572 lines) | Shared by #2053, #2055, #2058, #2060 — file-size bottleneck |
| 3 | `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py:150` | #1859 adapter pattern — template for #2063, #2062 |
| 4 | `worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv` | #2063 data source — 36 records, imperial units |
| 5 | `worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv` | #2059 data source — 17 vessels (Sleipnir, Thialf, Balder) |
| 6 | `worldenergydata/data/modules/vessel_fleet/curated/drilling_rigs.csv` | #2062 data source — 2,210 rows, ~138 with geometry |
| 7 | `digitalmodel/src/digitalmodel/field_development/economics.py:420-435` | #2054 hardcoded linear decline (duplicated at `:617-633`) |
| 8 | `data/field-development/subseaiq-scan-latest.json` | #2055 blocker — 10 GoM fields, zero equipment count columns |
| 9 | `.claude/skills/coordination/session-start-routine/SKILL.md` | #2057 — 5 broken internal links point to wrong path |
| 10 | `docs/governance/SESSION-GOVERNANCE.md` (475 lines) | #2057 needs #2057 section; #2056 already documented |
| 11 | `digitalmodel/src/digitalmodel/field_development/concept_selection.py:468-525` | #2053 convenience wrapper already wired |
| 12 | `worldenergydata/subseaiq/analytics/normalize.py:31-54` | #2058, #2060 — alias dict needs extensions |
| 13 | `digitalmodel/src/digitalmodel/drilling_riser/__init__.py` | #2063 — currently 13 exports, needs 3 more |
| 14 | `.claude/hooks/session-governor-check.sh` | #2056 — PreToolUse hook, `FAST_PATH_CEILING=160` |
