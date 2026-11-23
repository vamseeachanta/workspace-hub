# Plan for worldenergydata#848: Phase-norm layer — field vs play vs country on every life-cycle stage

> **Status:** plan-approved — owner approval 2026-07-06 (in-session): **play-norms-only v1**, country = ROADMAP badges via wed#681. Marker: `.planning/plan-approved/wed-848.md`. (History: r1 Claude MAJOR + r2 Codex MAJOR → r3 inline patch → approved.)
> **Complexity:** T2 — justified post-descope: one data family (FDAS V30 xlsx + benchmark CSV), one new src module, one builder, one template block; country baselines explicitly deferred (below), so no new ingest surface. Upgrade to T3 only if country baselines are pulled back into scope.
> **Date:** 2026-07-06 (r3 revision same day)
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/848 (repo: **worldenergydata**, NOT workspace-hub — attestation in r2 resolved the number against workspace-hub; all issue/path evidence below is wed-repo-qualified)
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-06-plan-wed848-claude.md (MAJOR, 10 findings) | ...-codex.md (MAJOR, 14 findings) | finding→patch map in §Adversarial Review Summary

---

## Resource Intelligence Summary

### Existing repo code (all paths verified against worldenergydata `origin/main` via `git cat-file -e` / `git show`, 2026-07-06)
- `reports/lower_tertiary/lt_well_benchmark_lower_tertiary_2010_latest.csv` — 56 wells × **19 cols** (r1 F9 correction) incl. `api12, field, drilling_days, completion_days, first_oil, cum_oil_mmbbl, uptime_pct, interventions, decline_annual_pct`. **Covers only 7/10 canonical fields — kaskida, north_platte, tiber have NO rows** (r1 F4): pre-FID fields with no producing wells. Field-side chips for those 3 render the honest "no well-level data (pre-production)" state.
- `docs/modules/bsee/analysis/production/FDAS_V30/drilling_and_completion_days.xlsx` — **217 data rows** after dropping the blank + TOTALS trailer rows (LEASE_NAME-notna rule, `scripts/lower_tertiary/build_drilling_insights.py:70-74`). **DRILLING_DAYS is calendar TD−spud for 166/184 populated rows and the benchmark generator computes `(td−spud).days+1`** (r1 F3) → there is NO native-rig-day basis anywhere in this family. v2 basis = `calendar_days` everywhere; the 18 xlsx rows whose DRILLING_DAYS ≠ TD−spud are kept but flagged in the build log (`adjusted_rows` count in provenance).
- `data/modules/bsee/current/wells/well_data.csv` — 57,281 rows, BUT **only ~100 rows carry both WELL_SPUD_DATE and TOTAL_DEPTH_DATE** (r1 F1, matches the #777 WATER_DEPTH sparsity precedent) and the benchmark's `6081240…` API range is essentially absent (r1 F2: api join hits 1/56). **Consequence: this file CANNOT provide country D&C baselines nor field/play Abandon populations. v2 uses it ONLY for the all-GoM PA/TA context share** (single population-level number, vintage caveat stated on-page).
- **Working join** (r1 F2): benchmark `api12` ↔ V30 xlsx `API_WELL_NUMBER` matches **55/56 after normalization** (xlsx stores float-formatted strings — strip `.0`, zero-pad to 12). Field membership inside the xlsx additionally via LEASE_NAME → canonical id mapping (same source `build_drilling_insights.py` uses), with the Cascade/Chinook and Jack/St Malo name-split mapping enumerated in config (r1 F4).
- `reports/lower_tertiary/lifecycle/_facts.json` — list of 10 field dicts (ids big_foot…tiber); `config/fields.yml` — #755 crosswalk (no BOTM codes; not needed in v2).
- `reports/lower_tertiary/lifecycle/lifecycle_template.html` — **8-phase stage-gate spine with activity cards rendered only for current±1 phase** (r1 F6) → per-stage-card chips are NOT viable. v2 UI = a dedicated always-rendered **"Performance vs norm" strip** (5 chips: Drill/Complete/Produce/Workover/Abandon) below the gates spine.
- Precedents: `src/worldenergydata/field_development/host_text_classifier.py` (src/ = flake8-gated home, PR wed#800), `worldenergydata.decommissioning.facility_liability` (tested module pattern, wed#793).

### Standards
Not applicable — statistical aggregation of public BSEE data; no standards-derived constants (calc-citation rule's "Do NOT apply" clause). Provenance requirements are still carried in the `_norms.json` schema (r2 F13).

### LLM Wiki pages consulted
No relevant wiki pages (public federal data, in-repo). Ecosystem-data hook consulted: drilling-well domain home is worldenergydata; the domain-database vehicle is wed#681 (OPEN, "D11 — Establish the drilling-well database") — referenced as the country-baseline ROADMAP dependency below.

### Documents consulted
- worldenergydata#848 (this plan's contract) + epic #754 (both-altitudes contract, issuecomment-4881675172) + #774/#775 (insight bar + filter rules) + **#846 (OPEN: full-raw WAR D&C extraction overshoots World Oil — why raw WAR is NOT used for baselines)** + #851 (KC ingest in flight; populations will grow — build must be re-runnable) + **#681 (OPEN: drilling-well database — the designated future source for country/GoM-wide D&C baselines)**.
- `docs/plans/README.md` — no prior #848 plan; wed CI prior art #2433/#2452.
- Skill: `.claude/skills/workspace-hub-learned/wed-field-hub-drilldown-pages/SKILL.md` (grammar + CI gotchas; created alongside this plan).
- Drive-file index (`search.py "drilling completion days benchmark norm" --caller plan-resource-intel`): 20 rows, none relevant beyond in-repo sources.

### Gaps identified (built from scratch)
- `src/worldenergydata/field_development/phase_norms.py`, `config/phase_norms.yml`, `scripts/lower_tertiary/build_phase_norms.py`, `_norms.json` contract, norms strip template block, stage distribution pages, tests.

### Evidence (embedded verification)
- Issue states (repo-qualified): wed#848 OPEN (this plan), wed#754 OPEN epic, wed#846 OPEN, wed#681 OPEN, wed#851 OPEN PR.
- Column/row probes and join-coverage counts: recorded above and independently reproduced by the r1 reviewer (see review artifact "What I verified" section — 100/57,281 date density; 1/56 vs 55/56 join outcomes; 166/184 calendar equality; 7/10 field coverage; 217 data rows).
- **Reproduction proofs: N/A — new-feature plan; no alleged failure.** The r1 adversarial reproduction of every data claim is the load-bearing evidence.
- Parallel-work check (2026-07-06): open wed PRs #845/#851/#852/#853 + 20 worktrees — none touches the lifecycle family → **single-lane**, dedicated worktree off fresh origin/main.

## Artifact Map
| Artifact | Kind | Path |
|---|---|---|
| Norm engine | new module | `src/worldenergydata/field_development/phase_norms.py` |
| Config | new YAML | `config/phase_norms.yml` (min_n, censor rules, field-name mappings, aggregation table) |
| Builder | new script | `scripts/lower_tertiary/build_phase_norms.py` |
| Data contract | generated | `reports/lower_tertiary/lifecycle/_norms.json` |
| Stage pages | generated ×5 | `reports/lower_tertiary/lifecycle/norms/{drill,complete,produce,workover,abandon}.html` |
| Norms strip | edit | `reports/lower_tertiary/lifecycle/lifecycle_template.html` + `scripts/lower_tertiary/build_lifecycle_posters.py` |
| Publish wiring | edit | `scripts/build_pages.py` (+ `config/repo_structure.yml` allowlist rows if required) |
| Tests | new | `tests/unit/field_development/test_phase_norms.py` |

## Deliverable (v2, descoped honestly)
Every LT life-cycle poster gains an always-rendered **"Performance vs norm" strip**: five chips (Drill/Complete/Produce/Workover/Abandon), each showing the field value, Δ vs the **leave-one-field-out play baseline**, and an n-badge on BOTH sides (`Drill 46.5 d (n=24) · −12% vs LT (n=32)`), linking to `norms/<stage>.html#<field_id>` distribution pages (population strip-plot, field highlighted, thesis + a number). Chips degrade honestly: pre-production fields (kaskida/north_platte/tiber) → "no well-level data"; thin baselines → "insufficient (n=X)"; **country column = explicit ROADMAP badge for D&C/Produce/Workover** ("GoM-wide population pending wed#681"), EXCEPT one honest country context stat on the Abandon page (all-GoM PA/TA share from `BOREHOLE_STAT_CD`, labelled with the vintage-mix caveat). `_norms.json` is the machine contract for #849/#756.

**What v1 explicitly does NOT deliver** (r1 F1/F2, r2 F5): computed country baselines for Drill/Complete/Produce/Workover. Their chips say so on-page; wed#681 is the tracked dependency. No number is fabricated to fill the gap.

### Methodological rules (correctness-critical, r3-hardened)
1. **Single basis:** all D&C durations are `calendar_days` (TD−spud family) — the "native rig-days" premise was false (r1 F3). Every MetricValue carries `basis`; deltas computed only within one basis (kept as a structural guard for future bases).
2. **Leave-one-field-out play baselines** (r1 F5, r2 F7): a field is never part of its own baseline (Jack/St Malo alone is 43% of the play population). Baseline n after exclusion is stored and displayed; below `min_n` (default 8) → `insufficient`.
3. **Honest degradation everywhere:** field-side metrics ALSO carry n and degrade (r1 F7) — a 3-well field median renders with `(n=3)` and a `low-n` flag, and below `field_min_n` (default 3) renders "insufficient wells".
4. **Population semantics stated per metric** (r1 F8, r2 F6): benchmark CSV = producing wells (survivor population); xlsx = development wellbores. Each stage page states its population definition; Drill/Complete use the xlsx wellbore population for BOTH field and baseline (semantic comparability — same source, same event definitions), Produce/Workover use the benchmark producing-well population for both sides. No cross-population deltas.
5. **Censoring rules for durations** (r2 F5): drop rows missing spud or TD, non-positive durations, durations > `max_days` (config, default 1,000); sidetrack/bypass wellbores kept (matches the published drilling-insights population); all exclusion counts logged to provenance.
6. **api12 normalization + join-coverage gate** (r1 F2, r2 F10): normalize float-string APIs (strip `.0`, zero-pad 12); build FAILS if benchmark↔xlsx match < 90% (current 55/56 = 98%).
7. **Golden-number reconciliation** (r1 F10): build asserts the recomputed play-wide Drill median equals the published drilling-insights figure (46.5 d) within rounding; any drift fails the build with the filter-waterfall diff.

### Stage-metric matrix (v2) — aggregation policy explicit (r2 F8)
| Stage | Field metric (aggregation) | Play baseline (leave-one-out) | Country |
|---|---|---|---|
| Drill | median well drill_days; median days/1000 ft TVD | xlsx wellbore population | ROADMAP (wed#681) |
| Complete | median well completion_days | xlsx wellbore population | ROADMAP (wed#681) |
| Produce | median uptime_pct; median decline_annual_pct; median cum_oil/well | benchmark producing wells | ROADMAP |
| Workover | interventions per well = total÷wells (mean; count data) | benchmark producing wells | ROADMAP |
| Abandon | field-side: UNAVAILABLE v1 (no per-field abandonment population — join dead, r1 F2) | play-side: UNAVAILABLE v1 | all-GoM PA/TA share (context stat + vintage caveat) |

## Pseudocode (core module)
```python
@dataclass(frozen=True)
class MetricValue: value: float; n: int; basis: str; population: str; aggregation: str
@dataclass(frozen=True)
class Comparator:  # play or country side
    status: str  # ok | insufficient | unavailable | roadmap
    metric: MetricValue | None; method: str | None  # e.g. leave_one_field_out
    reason: str | None
@dataclass(frozen=True)
class NormEntry: field_id, stage, metric_id, unit, field: MetricValue|None,
                 field_status, play: Comparator, country: Comparator,
                 delta_play_pct|None, delta_country_pct|None

def normalize_api(s) -> str            # strip .0 float suffix, zero-pad 12
def load_lt_population(xlsx) -> frame  # LEASE_NAME-notna drop; censor rules; adjusted_rows count
def map_lease_to_field(cfg) -> dict    # LEASE_NAME→canonical id incl. cascade_chinook/jack_st_malo splits
def compute(cfg) -> (entries, provenance)   # leave-one-out baselines; deltas same-basis+same-population only
def write_norms_json(entries, provenance, out)
```
`_norms.json` top level (r2 F9): `{schema_version, generated, config_hash, builder, sources: [{path, sha256, rows_total, rows_used, excluded: {missing_dates, nonpositive, over_max, totals_trailer, unmatched_api}}], join_coverage, entries: [...]}` — every entry self-describes unit/basis/aggregation/population/n per side.

## Files to Change
1–8 unchanged from the Artifact Map. Template edit = new norms-strip block (always rendered; NOT inside the current±1 activity-card logic). Publication: the lifecycle family is published via the lifecycle copy block (no underscore→hyphen rename applies there — r1 F9 corrected); `norms/` sub-dir rides the same copy; verified by the link test below.

## TDD Test List (write first, confirm red)
1. `test_lt_loader_drops_blank_and_totals_rows_and_censors` — fixture with trailer + bad-date + negative + >max rows → exact exclusion counts in provenance.
2. `test_normalize_api_float_suffix_and_padding` — `"608124006001.0"`→`"608124006001"`; short forms zero-padded (r2 F10).
3. `test_join_coverage_gate_fails_below_threshold` — coverage 0.8 fixture → build error naming unmatched APIs.
4. `test_leave_one_field_out_baseline_excludes_self` — field with 43% share: baseline recomputed without it; n reflects exclusion (r1 F5).
5. `test_field_side_low_n_flag_and_insufficient` — n=3 → `low-n`; n=2 with field_min_n=3 → `insufficient` (r1 F7).
6. `test_unavailable_and_roadmap_never_carry_numbers` — country D&C entries have `status='roadmap'`, metric None; Abandon field-side `unavailable` (r2 F5-adjacent honesty).
7. `test_delta_requires_same_basis_and_population` — mismatched basis or population → delta None + structural error (r1 F3, rule 4).
8. `test_norms_json_schema_complete_and_deterministic` — 10 ids × 5 stages, ordering stable across runs, schema fields present, round-trip (r2 F9/F10).
9. `test_golden_reconciliation_against_drilling_insights` — recomputed play Drill median == 46.5 d fixture contract (r1 F10).
10. `test_lease_name_field_split_mapping` — Cascade+Chinook lease names → `cascade_chinook`; Jack + St. Malo → `jack_st_malo` (r1 F4).
11. `test_generated_poster_contains_norms_strip_links` — rendered poster HTML contains `norms/drill.html#<id>` for a rich field AND the "no well-level data" state for kaskida (r2 F10/F12).
12. `test_abandon_context_share_from_status_codes` — fixture BOREHOLE_STAT_CD → correct share + caveat string present.

## Acceptance Criteria (v2)
- [ ] Tested module computes field metrics + leave-one-out play baselines from xlsx/benchmark with explicit censoring; join-coverage and golden-reconciliation gates pass in the build
- [ ] Norms strip on all 10 posters: 7 fields with live chips + n-badges both sides; 3 pre-production fields with the honest no-data state; country cells = ROADMAP badges (wed#681 linked), never numbers
- [ ] 5 stage pages with population definition stated, field highlighted, thesis + a number; Abandon page carries the all-GoM context share with vintage caveat
- [ ] `_norms.json` carries full provenance (sources, hashes, row counts, exclusions, join coverage, per-side n/basis/population/aggregation)
- [ ] All 12 TDD tests pass; post-publish link check over the public tree resolves every chip/anchor href (automated, not manual — r2 F10)
- [ ] Chip renders legibly in the poster's narrow column incl. the degraded states (visual check in PR screenshots — r2 F12)

## Risks (v2)
1. Residual semantic drift between benchmark `drilling_days` and xlsx `DRILLING_DAYS` for the 18 adjusted rows → both sides drawn from the SAME xlsx for D&C (rule 4); benchmark days used only for well-page display, not baselines.
2. Template merge race with future lanes → single-lane worktree; post-merge grep of the norms-strip markup on origin/main (#767-loss lesson).
3. #851 KC ingest shifts populations → deterministic re-runnable build; provenance row counts make drift visible.
4. CI: mirror all three linters (black 25.9.0 / isort 6.0.1 / flake8 7.3.0 on `src/ tests/`; re-verify pins against `.github/workflows/ci.yml` at implementation time); PR title subject ≤80 chars; `./.venv/bin/python -m pytest`.
5. Country-baseline expectation management: the issue text says "compare to the country average" — v1 ships the slot + ROADMAP badge, not the number; wed#681 tracked. If the owner wants country numbers in v1, scope re-opens to a data-ingest lane (T3) — flagged for the approval decision.

## Adversarial Review Summary
- **r1 (Claude subagent, repo-verified): MAJOR, 10 findings** — artifact `...-plan-wed848-claude.md`.
- **r2 (Codex dispatch): MAJOR, 14 findings** — artifact `...-plan-wed848-codex.md`. r2 F1/F2 were attestation-tooling artifacts (attested against workspace-hub instead of worldenergydata); resolved by repo-qualifying all evidence (header + Evidence section), not by dismissal.
- **r3 (this revision, inline per `feedback_r3_inline_loop_break_pattern`):** finding→patch map — country-baseline infeasibility → descoped to ROADMAP badges + wed#681 (r1 F1); dead well_data join → benchmark↔xlsx join with normalization + coverage gate (r1 F2, r2 F3/F4/F10); false rig-day basis → single calendar basis + adjusted-row logging (r1 F3, r2 F6); 7/10 coverage → honest field-side states (r1 F4); self-inclusion → leave-one-out + tests (r1 F5, r2 F7); template current±1 → always-rendered norms strip (r1 F6); field-side n honesty (r1 F7); population semantics per metric (r1 F8, r2 F6); factual corrections 19 cols/217 rows/no-rename (r1 F9); golden reconciliation + join/link tests (r1 F10, r2 F10); schema provenance depth (r2 F9/F13); aggregation policy table (r2 F8); censoring rules (r2 F5); chip legibility AC (r2 F12); T2 justification (r2 F14); public-path answer: lifecycle copy block preserves names, automated link check (r2 F11 + question 2).
- Not approval-self-labeled: awaiting user decision, including the explicit Risk-5 scope question (country numbers now vs wed#681 later).
