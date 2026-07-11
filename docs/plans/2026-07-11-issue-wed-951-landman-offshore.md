# Plan for worldenergydata#951: Landman lens (offshore) — BSEE lease panel with grabbable placeholders

> **Status:** adversarial-reviewed (r1 Fable subagent MAJOR/2 + MINOR/1, COMPUTED @ wed 5ead2c6 → r2 this revision; both MAJORs folded: lease count 20 not 26, per-lease block was false precision)
> **Complexity:** T1–T2 — a derived `landman` block on the poster payload + a lease panel; data-honest placeholders link a filed ingest issue.
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/951 (parent epic #943, program #939)
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** r1 pending; summary → #951 evidence comment.

---

## Resource Intelligence Summary

### Sources consulted (LOCAL clone of origin/main @ `5ead2c6`; lease coverage computed)
- **Issue #951 + epic #943 + program #939.** Landman offshore = a per-field lease panel: lease ids, blocks, operator, status, working interest, effective/expiration dates.
- **`config/fields.yml`** — THE canonical lease registry (#755): 11 fields, `bsee.leases` (`^G\d{5}$`) + `bsee.area_blocks` + `bsee_block_note`. The 10 LT fields each have 1–6 leases; loader `worldenergydata.common.fields_registry.by_lease` resolves variants. This is the join spine.
- **`docs/modules/bsee/analysis/production/FDAS_V30/leases.xlsx` (20 rows) + `leases_v21_kc.csv` (26 rows)** — the only committed lease datasets. Columns: **`LEASE_NUM, Lease_Numeric, LEASE_NAME, DEV_NAME, WATER_DEPTH, DEV_SYSTEM`** (NO block, NO status, NO dates). **r1-computed coverage: the 10 LT poster-fields have exactly 20 leases, ALL 100% covered in both files** (leases.xlsx = the 20 LT leases; the CSV adds 6 buckskin). **Scope = 20 leases / 10 fields — NOT 26** (26 double-counts buckskin, which has `surfaces.lifecycle_poster:false` and is out of scope; r1 f1). Join MUST normalize case (`g25792`,`g19555` are lowercase in the V30 files; `by_lease` handles it). xlsx needs pandas (venv build only; Pages deploy unaffected).
- **`docs/knowledge-base/bsee/data-dictionaries/leasing/lease-fields.md`** — defines the RICH landman attributes: **Lease Status** (PRD/EXPD/SOP/UNIT/REL…), **Effective Date**, **Expiration Date**, **Lease Type**, area/block. **⚠️ These are DESCRIBED but the committed datasets DO NOT carry them** — `leases.xlsx` has only name/depth/dev-system; `bin/lease_data.py` loader has no status/date/lessee fields (grep empty). Working interest lives in `_facts.json.working_interest` (partner splits) but not per-lease.
- **`_facts.json`** — per-field `operator`, `working_interest` (partner list). The panel's operator/WI-partners come from here.
- **Shipped E3 pattern (#949)** — a derived block on the poster payload flows to BOTH the poster and `_explorer.json` (the shell panel); the #946 identity gate covers parity. No new sidecar file needed.

### Gaps identified (→ grabbable placeholders, per [[feedback_placeholder_links_to_filing_issue]])
The rich landman attributes — **lease status, effective/expiration dates, lease type, per-lease working interest, operator-of-record history** — are NOT in committed data. Per owner guidance (2026-07-11): render them as **visible placeholders linking a filed `cat:data` ingest issue**, not silent omission.

### Parallel-work check
No open lane touches the poster payload landman/lease surface. Re-verify at implementation start; fresh clone (never FUSE).

## Goal

Every LT field poster + Explorer field panel gains a **Lease & landman** card: the leases we can source (id · block · water depth · dev system · operator/partners from `fields.yml` + V30 + `_facts.json`), with the rich landman columns (status, dates, working interest) shown as **placeholders that link a filed BSEE lease-status ingest issue** — turning each gap into grabbable work.

## Non-goals
- NO lease-status/date/WI fabrication — those are placeholders until the ingest lands.
- NO lease-first funnel entry yet (that's a later E3 slice; this is the field-view panel per #950/#951 acceptance).
- NO buckskin (no poster). NO new sidecar file (rides `_explorer.json`).
- NO new ingest IN this wave — the ingest is FILED as the grabbable issue (T7), not executed here.

## Artifact Map

| Artifact | Kind | Path |
|---|---|---|
| Lease-panel builder | new tested module | `src/worldenergydata/field_development/landman.py` — `build_landman(field_facts, registry_field, lease_rows, ingest_issue)` |
| V30 lease crosswalk | edit (build-time) | `build_lifecycle_posters.py` loads `leases.xlsx`+`leases_v21_kc.csv` once (pandas, build-only) → per-lease name/depth/dev-system |
| Poster payload | edit | `facts_to_field` attaches `landman` (flows to `_explorer.json`) |
| Poster + shell panel | edit | `lifecycle_template.html`, `atlas_template.html` — Lease & landman table + placeholder links |
| Ingest issue | new `cat:data` issue | BSEE lease-status/dates/WI dataset (verified URL at filing) — the placeholders link here |
| Tests | new + edit | landman builder units; lease-resolves-through-registry gate; placeholder-present gate |

## Design decisions

**D1 — `build_landman(...)` from the canonical registry + V30 + facts. NO per-lease block (r1 f4).**
Per lease: `{lease_num, water_depth_ft, dev_system, lease_name}` (V30 join by CASE-NORMALIZED LEASE_NUM) — **no `block` per lease**, because `fields.yml` `leases` and `area_blocks` are unpaired parallel lists of different lengths (jack_st_malo 6 leases/3 blocks, cascade_chinook 2/4, kaskida 2/2, north_platte 2/4 — 4 of 10 fields would fabricate a lease→block pairing). Instead the panel shows **`area_blocks` as a field-level list once** (`blocks: [...]` + `bsee_block_note`), and the lease→block pairing is one of the placeholder attributes deferred to the ingest issue (the BSEE Lease/Block Admin table carries it). Field-level: `operator`, `working_interest` partners (from `_facts.json`, per-FIELD — real), `n_leases`, `blocks`. Plus `pending` = placeholder attributes (`status, effective_date, expiration_date, lease_type, per_lease_block, per_lease_working_interest, operator_of_record_history`) and `ingest_issue`. Pure function; unit-tested. Every lease MUST resolve through `fields_registry.by_lease` (fail-closed) — gate asserts it.

**D2 — Placeholders link the ingest issue (owner guidance).**
Panel header (field-level, real): operator · working-interest partners · **blocks list** (`area_blocks` + note). Lease table columns: **Lease · Water depth · Dev system · Status · Effective · Expiration · WI** — the last four render `— <a href="…issue/NNN">pending</a>` (public GitHub URL, allowed external link), NOT blank/omitted. One-liner above the table: "Lease status, dates, per-lease block & working interest pending the BSEE lease-data ingest (#NNN) — contributions welcome." Panel heading is `<h2>`/`<h3>` in the poster, never `<h1>` (nav-spine single-`<h1>` rule; r1 f6).

**D3 — Payload, not a new file (E3 pattern).** `field["landman"] = build_landman(...)`. Rides `const FIELD` + `_explorer.json`; identity gate covers it.

**D4 — Poster + shell panel.** Poster: a "Lease & landman" section (all fields have ≥1 lease → always rendered). Shell `renderField`: a "Lease & landman" cardlet with the same table (rich-only; global cards unaffected). Both use public-layout hrefs for the issue link (external, so no rebasing).

**D5 — The ingest issue = the round-up (T7).** File a `cat:data` issue: BSEE Lease & Lease-Owner data (data.bsee.gov Leasing/Ownership; URL verified at filing per the wed #855 rule + [[feedback_document_discovered_data_sources_as_issues]]). Body lists the exact attributes (from the data dictionary), the join path (LEASE_NUM → `fields.yml`), and the consumer (this panel). Also file a sibling `cat:data` issue for the **well-plugging P&A** gap deferred from #949 (lease→borehole join for LT fields) so that placeholder is grabbable too, and retro-link #949's note.

**D6 — Gates.**
(a) landman builder units (lease join, no per-lease block, placeholder list, WI partners);
(b) every `fields.yml` LT lease resolves through `by_lease` AND appears in the panel — assert **20 leases across 10 fields, 0 dropped**;
(c) `_explorer.json`: all 10 LT fields carry `landman` with ≥1 lease + `blocks` list; each `pending` attribute present;
(d) the ingest-issue href present on every placeholder (no blank landman cell); no per-lease `block` key emitted (false-precision guard);
(e) #946/#947/#948/#949 gates green (identity, no-NaN, wells, risk).

## Implementation steps

| # | Step | Files |
|---|---|---|
| T1 | File the two `cat:data` ingest issues (lease-status + well-P&A), verified URLs → capture their numbers | — |
| T2 | `landman.build_landman` + unit tests (RED-first) | new module + tests |
| T3 | V30 lease crosswalk load + attach `landman` in `facts_to_field`; regenerate posters + `_explorer.json` | generator + artifacts |
| T4 | Poster + shell Lease & landman panels + placeholder links; regenerate `field-atlas/index.html` | templates + artifacts |
| T5 | Gates (D6); full suite `-o addopts="" --noconftest` | tests |
| T6 | Lint mirror; PR `feat(explorer): …` ≤80ch; auto-merge; live verify (Jack/St Malo 6-lease table, placeholders link the issue, Big Foot 1 lease) | — |
| T7 | Retro-link #949 well-P&A note to its new ingest issue (small follow-up note/comment) | — |

## Acceptance mapping (issue #951 → plan)

| Criterion | Delivered by |
|---|---|
| Lease panel per field from BSEE registry keyed by `fields.yml` leases | D1/D4 (10 LT fields, **20 leases**) |
| Panel on posters + machine-readable for the shell | D3 (`_explorer.json`) |
| Honest nulls for attributes BSEE data doesn't carry | D2 — placeholders LINKING the ingest issue (owner-guided, not blank) |
| Registry round-trip test | D6(b) |

## Risks & mitigations
- **R1 looks like a stub** → the panel ships real lease/block/depth/dev-system/operator data (all 10 fields); only the rich attributes are placeholders, and each is grabbable via the linked issue (owner-endorsed pattern).
- **R2 V30 lease join misses** → r1 RAN it: 20/20 LT leases covered in both files (case-normalized); any future miss shows the lease from `fields.yml` with all-placeholder cells (never dropped).
- **R5 per-lease block false precision** (r1 f4) → blocks are field-level only; per-lease block is a placeholder → ingest issue. Gate (d) asserts no per-lease `block` key.
- **R3 external issue link** → GitHub issue URLs are allowed external hrefs (not in the internal link-graph gate); assert present, not resolved.
- **R4 poster/explorer churn** → gate-covered.

## Ops notes
Local clone (FUSE hangs), venv-min (+pandas for the xlsx read + economics path), heredoc python, `-o addopts="" --noconftest`, agent verifies / human merges. landman module in `src/` → flake8-covered. `all_regions_atlas.html` embeds date.today() — never commit its regeneration.
