# Plan for worldenergydata#949: Underwriting-lens pilot — per-field HPHT + decommissioning risk badges

> **Status:** adversarial-reviewed (r1 Fable subagent MAJOR/1 + MINOR/1, COMPUTED evidence @ wed 6630ad7 → r2 this revision; the review corrected a false "no per-field P&A exists" premise — pilot is now TWO signals, not one)
> **Complexity:** T1–T2 — two derived risk blocks on the poster payload + header/panel chips; no new ingest, no new sidecar file.
> **Date:** 2026-07-11 (r2 same day)
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/949 (parent epic #943, program #939)
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** r1 findings summarized in the #949 evidence comment (subagent RAN the name-match + exceedance recompute); local-only by convention.

---

## Resource Intelligence Summary

### Sources consulted (LOCAL clone of origin/main @ `6630ad7`; r1 re-computed every claim)
- **Issue #949 + epic #943 + program #939.** Proposed three per-field signals: P&A exposure, under-pressure severity, HPHT-vs-equipment. Grounding (r1-verified) resolves each to its honest per-field availability below.
- **HPHT — directly per-field** in `_facts.json.reservoir` (`pressure_psi, equip_rating_psi, hpht_class, temp_f`). Exceedance `round((p−e)/e*100)` computes for **5 fields** (r1-confirmed, none missed): anchor 25,000/20,000 **+25%** (flagship), shenandoah 22,000/20,000 +10%, kaskida 20,000/20,000 0%, tiber 20,000/20,000 0%, julia 13,500/15,000 −10%. `hpht_class` present for **9 fields** (all but big_foot). 4 class-only (north_platte rating-only; cascade_chinook & jack_st_malo pressure-only; stones class-only) → **9 non-null risk, big_foot None**.
- **⚠️ julia pressure is a SUBSEA-SYSTEM figure, not reservoir pore pressure (r1 f4).** `_facts.json` julia `source_note`: "subsea pressures ~13,500 psi (15,000-psi-rated trees + first permanent HIPPS)"; `_pressure.json` carries an explicit `pressure_caveat`. So julia's 13,500-vs-15,000 is system-vs-tree-rating, semantically ≠ anchor's reservoir-vs-equipment. `_facts.json` has no basis flag → the classifier would wrongly treat julia like anchor unless fixed.
- **Under-pressure — NOT the LT population (r1-verified, HONEST drop).** `_pressure.json`: `offshore.regime = "Over-pressured (HPHT)"` `field_count:10` = the LT fields; `onshore.regime = "Under-pressured / near-vacuum"` = US Mid-Continent gas (30,100 wells). An under-pressure badge on LT posters would be wrong data → link `/pressure-atlas/`; the onshore under-pressure signal belongs to the onshore lens (#951).
- **P&A / decommissioning — PARTIALLY per-field (r1 f1 CORRECTED my draft).** Two distinct things:
  - **Well-plugging P&A: genuinely unavailable per LT field** — `well_data.csv` has NO lease column and its `BOTM_FLD_NAME_CD` covers only 23 shelf codes (all `ST*`/`EW873`/`WILD`); zero LT-field boreholes attributable. Correct to exclude.
  - **Facility decommissioning: 3 LT fields DO have a sourced per-facility figure** in `reports/decommissioning/regional_liability.csv` (name-matched): **Big Foot TLP $43.23M** (Mini-TLP, depth-modeled — genuine), **Jack/St. Malo FPU $80.0M** and **Stones FPSO $80.0M** (both the CSV header's "FPSO base low-confidence" flat placeholder). My draft's "no per-field P&A number exists" was **false**; r2 surfaces these as a decommissioning chip with honest confidence flags.
- **`build_lifecycle_posters.py::facts_to_field`** (~L280–315) — payload already carries `reservoir`/`treeLabel`; `main()` (L432–434) attaches `norms`+`performance` before embedding `const FIELD` and writing `_explorer.json`. r1-verified `test_explorer_identity_with_posters` asserts FULL dict equality (not a frozen key set), so new `risk` keys flow to both sides and no test breaks.
- **Templates** — `lifecycle_template.html` and `atlas_template.html` each have exactly one `<h1>` (nav-spine fail-closed; `test_atlas_shell_pins`); a span chip adds none. `FIELD_JSON_RE` tolerates the new keys. Publish hrefs: `decommissioning/pa-liability-wave.html` (hyphen), `pressure-atlas/`; both resolve from the poster (`lifecycle/`) and shell (`field-atlas/`) bases (one level deep) — r1-confirmed.
- **Classifier home** — `src/worldenergydata/field_development/` (beside `host_text_classifier`, the `treeLabel` classifier this pilot mirrors); flake8-covered, importable via the existing sys.path insert.
- Drive-file search: not applicable.

### Gaps identified
No derived HPHT/decommissioning risk view; julia system-pressure basis not flagged in `_facts.json`; no per-field decommissioning chip despite available data (my draft's premise error).

### Parallel-work check
No open lane touches poster risk/reservoir or the atlas header. Re-verify at implementation start; fresh clone (never FUSE).

## Goal

Every LT field carries the underwriting signals its data actually supports: an **HPHT badge** (reservoir pressure vs equipment rating, 9 fields) and, where a sourced figure exists, a **facility-decommissioning badge** (3 fields, confidence-flagged), each linking its front-door page. Honesty-gated throughout; the two non-applicable framings (well-P&A per field, under-pressure on LT) are handled by explicit links + documented exclusions, never fake numbers.

## Non-goals (honest scoping)
- **NO under-pressure badge on LT** (wrong population; onshore lens #951 owns it) — reservoir chip links `/pressure-atlas/`.
- **NO per-field well-plugging P&A count** (not attributable: no lease column, 0 LT boreholes) — documented exclusion; the facility-decommissioning chip is the honest per-field decommissioning signal instead.
- NO new ingest, NO new sidecar file, NO shell redesign.

## Artifact Map

| Artifact | Kind | Path |
|---|---|---|
| HPHT classifier | new tested module | `src/worldenergydata/field_development/hpht_risk.py` — `classify_hpht(reservoir)` |
| Decommissioning join | new tested module | `src/worldenergydata/field_development/decommission_risk.py` — `classify_decommissioning(facility_name, rows)` |
| julia basis flag | data edit | `_facts.json` julia.reservoir gains `pressure_basis: "subsea_system"` (curated from source_note) |
| Poster payload | edit | `facts_to_field` attaches `risk` = `{hpht, decommissioning}` (flows to `_explorer.json`) |
| Poster header + panel | edit | `lifecycle_template.html`, `atlas_template.html` — HPHT + decommissioning chips + lens links |
| Facility crosswalk | edit | `_facts.json` (or overlay) per-field `decommissioning_facility` name for the 3 matches |
| Tests | new + edit | classifier units (HPHT 5+ cases, julia system-basis, decommission 3 + confidence); payload/parity/null gates |

## Design decisions (r2)

**D1 — `classify_hpht(reservoir)`; system-pressure basis respected (r1 f4).**
`None` when no `pressure_psi` and no `hpht_class`. Else `{class, pressure_psi, equip_rating_psi, exceedance_pct, severity, basis, label}`. **Exceedance is computed ONLY when `pressure_basis` is reservoir (default); `pressure_basis=="subsea_system"` (julia) → severity `class-only`** with a label naming the system basis ("HPHT · subsea system 13.5k / 15k-psi trees"), never a reservoir-vs-equipment "−10%". `severity ∈ {over-rating(>0), at-rating(0), within(<0), class-only}`. Pure, unit-tested: anchor +25 over-rating, shenandoah +10, kaskida 0 at-rating, tiber 0, julia class-only(system), stones class-only, big_foot None.

**D2 — `classify_decommissioning(facility_name, regional_rows)` (r1 f1).**
Name-matches `regional_liability.csv`; returns `{cost_musd, host_type, confidence, basis}` where `confidence="low"` when `host_type` contains FPSO/FPU (the CSV header's "FPSO base low-confidence"), else `"modeled"`; `basis="facility removal (not well P&A)"`. Big Foot → $43.23M modeled; Jack/St Malo & Stones → $80.0M low. `None` for the other 7. A per-field `decommissioning_facility` name lives in `_facts.json`/overlay (curated crosswalk: big_foot→"Big Foot TLP", jack_st_malo→"Jack/St. Malo FPU", stones→"Stones FPSO").

**D3 — Payload, not a new file.** `field["risk"] = {"hpht": classify_hpht(...), "decommissioning": classify_decommissioning(...)}`. Rides `const FIELD` + `_explorer.json`; the #946 identity gate covers parity. E3's "_risk.json" intent met by `_explorer.json`.

**D4 — Poster header + shell panel chips.** HPHT chip beside the tree badge (over-rating=red, at-rating=amber, within/class-only=slate) → `../pressure-atlas/`. Decommissioning chip (modeled=solid, low=dashed/"~") → `../decommissioning/pa-liability-wave.html`. Null → no chip. Shell `renderField` renders both from `f.risk` (from the fetched `_explorer.json` payload, NOT the roster — r1-confirmed the panel reads the explorer field object) + an honest "well-plugging P&A not attributed per field" one-liner.

**D5 — Provenance.** Chips show the reservoir `source_note` / the CSV confidence basis; #805 em-dash nulls respected.

**D6 — Gates.**
(a) HPHT units (5 exceedance exact + julia system-basis class-only + stones class-only + big_foot None);
(b) decommission units (3 matches, Big Foot modeled vs 2 low-confidence, 7 None);
(c) `_explorer.json`: exactly 9 fields `risk.hpht` non-null, exactly 3 `risk.decommissioning` non-null, severities/confidence recomputed-parity;
(d) no chip HTML where the corresponding risk is null (poster scan);
(e) #946/#947/#948 gates green (identity, no-NaN, wells);
(f) pressure-atlas + P&A-wave hrefs resolve.

## Implementation steps

| # | Step | Files |
|---|---|---|
| T1 | `hpht_risk` + `decommission_risk` modules + unit tests (RED-first) | new modules + tests |
| T2 | julia `pressure_basis` + per-field `decommissioning_facility` crosswalk in `_facts.json` | data |
| T3 | Attach `risk` in `facts_to_field`; regenerate posters + `_explorer.json` | generator + artifacts |
| T4 | Poster header chips + shell panel chips + lens links; regenerate `field-atlas/index.html` | templates + artifacts |
| T5 | Gates (D6); full suite `-o addopts="" --noconftest` | tests |
| T6 | Lint mirror; PR `feat(explorer): …` ≤80ch; auto-merge; live verify (Anchor red +25%, Julia system-basis not "−10% within", Big Foot no HPHT chip + no decom chip? — Big Foot HAS $43M decom chip; Stones low-confidence dashed) | — |
| T7 | Re-scope comment on #949 (under-pressure→#951; well-P&A excluded w/ rationale; facility-decommissioning surfaced for 3 fields) | — |

## Acceptance mapping (issue #949 → plan)

| Issue criterion | Delivered by |
|---|---|
| Field header risk badges where data supports them | D4: HPHT (9) + decommissioning (3); under-pressure honestly excluded (wrong population) |
| Each badge links its screen page | HPHT→pressure-atlas; decommissioning→P&A wave |
| Honest nulls: no badge where no data | D1/D2 None + D6(d); julia system-basis not over-claimed |
| Machine-readable risk surface | D3 — `_explorer.json` |

## Risks & mitigations
- **R1 re-scope drops legitimate work** → r1 CAUGHT this; r2 restores the facility-decommissioning signal (3 fields) and only excludes the genuinely-unavailable well-P&A count (documented).
- **R2 julia over-claim** → `pressure_basis` flag + class-only severity (r1 f4).
- **R3 confidence laundering** → Big Foot modeled vs the 2 FPSO-base low-confidence explicitly flagged (dashed chip + "~").
- **R4 exceedance math** → unit tests pin all 5.
- **R5 poster/explorer churn** → gate-covered.

## Ops notes
Local clone (FUSE hangs), venv-min (+pandas for the economics import path, per #948), heredoc python, `-o addopts="" --noconftest`, agent verifies / human merges. Both classifiers in `src/` → flake8-covered.
