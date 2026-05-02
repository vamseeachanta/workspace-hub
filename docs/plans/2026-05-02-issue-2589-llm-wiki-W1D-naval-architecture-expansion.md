# Plan for #2589: feat(llm-wiki): naval-architecture wiki topical expansion — 10 core concept pages (W1-D)

> **Status:** plan-review (revised after r1 review)
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2589
> **Review artifacts:** scripts/review/results/2026-05-02-plan-2589-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

Wiki target tree: `knowledge/wikis/naval-architecture/wiki/` — 62 markdown files on disk; `index.md` frontmatter `page_count` reads 61 because the index regenerator excludes `index.md` itself from its own catalogue total. This plan will bump `page_count` 61 → 71 (+10 new pages) while the on-disk file count moves 62 → 72. Directory schema mandated by `knowledge/wikis/naval-architecture/CLAUDE.md` (concepts/, entities/, sources/, standards/, comparisons/, visualizations/, plus index/log/overview).

- Found: 6 baseline concept pages from the 2026-04-07 init —
  - `concepts/hydrostatics.md` (Cb, Cwp, Cm, Cp, TPC, Bonjean, hydrostatic curves)
  - `concepts/resistance-propulsion.md` (Rf/Rr, ITTC 1957, Holtrop, propeller open-water)
  - `concepts/seakeeping.md` (six DOF, RAOs, JONSWAP/PM/ITT spectra, operability)
  - `concepts/stability.md` (GM, GZ, intact + damage, IMO IS Code)
  - `concepts/ship-design.md` (5-phase design spiral, parametric, Holtrop-Mennen)
  - `concepts/ship-structures.md`
- Found: 9 issue-#2564 / #2567 maneuvering concept pages added 2026-04-30 → 2026-05-01 (`maneuvering-coordinate-conventions.md`, `rudder-force-modeling.md`, `yaw-moment-rudder-sweep.md`, `maneuvering-validation-metrics.md`, `environmental-yaw-moment-coefficients.md`, `steering-gear-design-checks.md`, `rudder-stock-design-checks.md`).
- Found: 43 source-summary pages under `sources/` — including PNA Vol I/II/III scans, Tupper, Bertram (Practical Ship Hydrodynamics), Biran (Ship Hydrostatics & Stability), Lewis (Marine Hydrodynamics), USNA EN400 course notes, Journée (Offshore Hydromechanics), Rawson & Tupper (Basic Ship Theory).
- Found: 1 standards page — `standards/steering-gear-rudder-stock-rule-crosswalk.md`.
- Found: 0 entity pages (`entities/` empty per `index.md` line 73 "No entity pages yet").
- Gap: classification-society entities; canonical IMO conventions; ITTC procedures; resistance components (frictional/wave/form) breakouts; propulsor-specific pages; lines plan / hull-form geometry; weights & loads; structural-design first-principles; wave theory; CFD; intact-stability codes; damage-stability subdivision.

### Standards

Standards-page production for naval-architecture is still bootstrapping. Per `.claude/rules/calc-citation-contract.md`, every standards-derived constant or formula in calc modules must cite a wiki standards page with `code_id`/`publisher`/`revision` frontmatter. Naval-arch wiki currently exposes 1 standards page (steering-gear/rudder-stock crosswalk per #2567). **No standards page promotion is in this plan's scope** — concept pages will reference standards bodies (IMO, ITTC, IACS, SNAME) by name + URL, leaving downstream codification to follow-up issues consistent with the #2471 sanctioned routing principle and #2566/#2568 in-flight precedent.

| Standard | Status | Source |
|---|---|---|
| IMO 2008 IS Code (Intact Stability) | referenced (no codified standards page) | https://www.imo.org/en/OurWork/Safety/Pages/Default.aspx (Maritime Safety landing; review-finding m3 noted HTTP 500 on the previous deeper URL — link-resolution will be re-verified at implementation) |
| IMO MSC.137(76) (Manoeuvring) | referenced — already in `sources/imo-msc-circ-1053-...` | sources page exists; codified standards page out of scope here |
| ITTC 1957 friction line / Recommended Procedures (specific procedure numbers to be verified at implementation — review m8 downgraded confidence) | referenced (URL-cited) | https://ittc.info/ |
| IACS UR S series (longitudinal strength) | referenced (URL-cited) | https://iacs.org.uk/ |
| SNAME PNA second revision | already in `sources/principles-of-naval-architecture-*` | textbook scans on /mnt/ace allowed for citation only — no extraction (#2482) |

### LLM Wiki pages consulted

- `knowledge/wikis/naval-architecture/wiki/index.md` — 61 pages, 43 sources, last regenerated 2026-05-01; entities table empty.
- `knowledge/wikis/naval-architecture/CLAUDE.md` — frontmatter schema (title, tags, added, last_updated mandatory; sources/cross_links recommended).
- `knowledge/wikis/naval-architecture/wiki/concepts/hydrostatics.md` (lines 1–30) — confirms current style: section headings, bulleted definitions, no extracted text, ~1 page typical.
- `knowledge/wikis/naval-architecture/wiki/concepts/seakeeping.md` (lines 1–30) — same style; six-DOF + spectra reference.
- `knowledge/wikis/naval-architecture/wiki/concepts/stability.md` (lines 1–30) — Key Concepts + Key References section established.
- `knowledge/wikis/naval-architecture/wiki/concepts/resistance-propulsion.md` (lines 1–35) — current page is broad (single page covers BOTH resistance components AND propulsor types) — strong false-gap risk for a "propulsors" or "ship-resistance-components" subdivision; mitigated by scoping new pages to topics not already named.
- Sibling: `knowledge/wikis/marine-engineering/wiki/` and `knowledge/wikis/maritime-law/wiki/` — referenced via cross-links from `ship-design.md`; not in scope.

### Documents consulted

- `docs/plans/_template-issue-plan.md` — followed structure verbatim; retrieval contract requires ≥3 distinct sources with embedded evidence.
- `.claude/rules/calc-citation-contract.md` — concept pages do not emit `Citation` instances (citations are calc-module artifacts); standards-page promotion deferred to follow-ups.
- `.claude/rules/coding-style.md` — single-site edits only; verify each new file added to `index.md` does not delete an adjacent line.
- Memory `feedback_plan_past_tense_artifact_claims.md` — this plan uses **future tense throughout** for all proposed pages.
- Memory `project_wiki_standards_path_decision.md` — `wiki/standards/<code-id>.md` reserved for codified standards; this plan stays in `wiki/concepts/`.
- #2566 — OPEN, "test(naval-arch): full CI and package validation for yaw and rudder-stock sweep workflows" — operational gate on #2564/#2565, no wiki content overlap.
- #2568 — OPEN, "feat(naval-arch): preliminary turning-circle and tactical-diameter estimator input workflow" — RESERVES turning-circle, tactical-diameter, advance, transfer, Nomoto-style maneuvering-input-workflow concepts.
- #2540 — OPEN, "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — wave epic; this plan is W1-D under that wave (naval-architecture domain).
- /mnt/ace inventory: `acma-codes/IMO/{Passenger Ships, Cargo Ships, Ship Security}`, `acma-codes/ABS Rules/{International Naval Ships, Naval Vessels, Propulsion, Wind Assisted Propulsion, Ice Class, Conditions of Classification}`, `acma-codes/DNV Rules/{2018 DNVGL Ship Rules, DNVGL-Class_2017-07}`, `O&G-Standards/SNAME/ship-plans`, `digitalmodel/docs/ship-design`, `digitalmodel/docs/naval_architecture`, `doris/codes/BV Ship and Offshore Rules` — confirms classification-society raw material is locally citable. Plan does not extract from these PDFs (per #2482 deny-list); concept pages will cite them by reference.
- WebSearch — Tupper "Introduction to Naval Architecture" 5e chapter list: Introduction, Definition & regulation, Ship-form calculations, Flotation, Stability, Launching/docking/grounding, Resistance, Propulsion, Ship environments, Seakeeping, Vibration/noise/shock, Manoeuvring, Structures, Ship design, Ship types (https://shop.elsevier.com/books/introduction-to-naval-architecture/tupper/978-0-08-098237-3).
- WebSearch — SNAME PNA Second Revision: Vol I Stability & Strength (chapters: hull-form description, intact stability, damage stability, hull structural design); Vol II Resistance, Propulsion, Vibration; Vol III Motions in Waves, Controllability (https://sname.org/principles-naval-architecture).
- WebSearch — ITTC Recommended Procedures index at https://ittc.info/ (specific procedure numbers e.g. `7.5-02-*`, `7.5-03-*`, `7.5-02-07-021` are NOT independently verified from the landing page — review m8 marked these as to-be-verified-at-implementation; pages will cite the homepage URL only until the procedure-number prefixes are confirmed against the ITTC downloads index).

### Gaps identified

Coverage matrix vs. canonical Tupper-5e + PNA-3-volume curriculum (after excluding #2566/#2568 reservations):

| Canonical topic | Current wiki status | #2566/#2568 reserved? | Action |
|---|---|---|---|
| Hull-form geometry / lines plan | gap | no | **NEW** `concepts/hull-form-geometry.md` |
| Hydrostatics (coefficients, Bonjean) | covered | no | leave |
| Intact stability (GZ, GM) | partial — under `stability.md` | no | **NEW** `concepts/intact-stability-criteria.md` (IMO 2008 IS Code expansion) |
| Damage stability + subdivision | gap (mention only) | no | **NEW** `concepts/damage-stability.md` |
| Resistance components (frictional/wave/form) | partial — under `resistance-propulsion.md` | no | **NEW** `concepts/ship-resistance-components.md` |
| Propulsors (FPP, CPP, podded, waterjet, azimuth) | partial — same page | no | **NEW** `concepts/marine-propulsors.md` |
| Propeller theory (open-water, KT/KQ, J) | partial | no | **NEW** `concepts/propeller-theory.md` |
| Seakeeping basics | covered | no | leave |
| Wave theory & spectra (PM, JONSWAP) | partial — bullets only | no | **NEW** `concepts/wave-theory-and-spectra.md` |
| Ship maneuvering basics | covered (#2564 pack) | rate of turn, yaw, rudder | leave |
| Turning circle / tactical diameter | not yet built | **YES — #2568 reserves** | **EXCLUDE** |
| Rudder force / stock design | covered (#2567) | yaw, rudder-stock, steering | leave |
| Structural design (longitudinal strength) | shallow (`ship-structures.md`) | no | **NEW** `concepts/ship-structural-strength.md` (IACS UR S) |
| Weights & loading | gap | no | **NEW** `concepts/ship-weights-and-loading.md` |
| Classification societies (IACS members) | gap (entities/ empty) | no | **NEW** `entities/classification-societies.md` |
| IMO regulatory framework | gap (referenced only) | no | **NEW** `entities/imo-regulatory-framework.md` |
| Vibration / noise / shock | gap | no | not in this batch — defer |
| Ship types | gap | no | not in this batch — defer |
| CFD for naval-arch | gap | no | not in this batch — defer (sibling marine-engineering wiki) |

**Top-10 selected for this expansion** (foundational + cross-linkable, citable canonical reference, raw source on /mnt/ace or stable URL):

1. `concepts/hull-form-geometry.md`
2. `concepts/intact-stability-criteria.md`
3. `concepts/damage-stability.md`
4. `concepts/ship-resistance-components.md`
5. `concepts/marine-propulsors.md`
6. `concepts/propeller-theory.md`
7. `concepts/wave-theory-and-spectra.md`
8. `concepts/ship-structural-strength.md`
9. `concepts/ship-weights-and-loading.md`
10. `entities/classification-societies.md`

(11th candidate `entities/imo-regulatory-framework.md` deferred to W2 to keep batch at exactly 10 + index update; surfaces as Open Question below.)

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):

- `#2566` — OPEN — "test(naval-arch): full CI and package validation for yaw and rudder-stock sweep workflows" — body confirms CI/package scope, NOT wiki content.
- `#2568` — OPEN — "feat(naval-arch): preliminary turning-circle and tactical-diameter estimator input workflow" — body reserves turning-circle, tactical-diameter, advance, transfer, Nomoto, MMG, sea-trial validation language.
- `#2540` — OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — parent wave epic.

**File existence** (`find … | sort` 2026-05-02):

- EXISTS: `knowledge/wikis/naval-architecture/wiki/index.md` (61 pages catalogued)
- EXISTS: `knowledge/wikis/naval-architecture/wiki/concepts/{hydrostatics,resistance-propulsion,seakeeping,ship-design,ship-structures,stability,maneuvering-coordinate-conventions,maneuvering-validation-metrics,environmental-yaw-moment-coefficients,rudder-force-modeling,rudder-stock-design-checks,steering-gear-design-checks,yaw-moment-rudder-sweep}.md` (13 concept pages)
- EXISTS: `knowledge/wikis/naval-architecture/wiki/sources/` (43 source pages)
- MISSING (this plan creates): `concepts/hull-form-geometry.md`, `concepts/intact-stability-criteria.md`, `concepts/damage-stability.md`, `concepts/ship-resistance-components.md`, `concepts/marine-propulsors.md`, `concepts/propeller-theory.md`, `concepts/wave-theory-and-spectra.md`, `concepts/ship-structural-strength.md`, `concepts/ship-weights-and-loading.md`, `entities/classification-societies.md`
- MISSING (this plan creates): `tests/knowledge/test_naval_architecture_expansion.py`

**Line excerpts** (from `concepts/hydrostatics.md` lines 1–8 — frontmatter contract this plan must reproduce):

```
---
title: "Ship Hydrostatics"
tags: ["hydrostatics", "coefficients", "displacement", "bonjean", "stability"]
sources:
  - naval-architecture-resources
added: 2026-04-07
last_updated: 2026-04-07
---
```

**Gap proofs** (`ls knowledge/wikis/naval-architecture/wiki/entities/ 2>&1`):

- "(empty)" — confirms `entities/` directory has zero pages despite being declared in `CLAUDE.md` schema; `index.md` line 73 reads "No entity pages yet" — confirms.

**#2568 reservation proof** (excerpt from `gh issue view 2568 --json body`):

> "Output tables/charts for advance, tactical diameter, turning diameter, and turn-rate response if supported by the chosen preliminary model."

This plan's selected topics avoid every reserved noun-phrase: no page on turning-circle, tactical-diameter, advance, transfer, Nomoto, or turning-rate-response.

<!-- Source count: 9 distinct sources cited above —
  (1) issue body for #2589 / parent-wave context,
  (2) wiki index,
  (3) wiki CLAUDE.md schema,
  (4) #2566, (5) #2568, (6) #2540,
  (7) /mnt/ace acma-codes inventory,
  (8) WebSearch Tupper,
  (9) WebSearch PNA + ITTC.
  Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2589-llm-wiki-W1D-naval-architecture-expansion.md` |
| Tests | `tests/knowledge/test_naval_architecture_expansion.py` |
| Implementation (10 wiki pages) | `knowledge/wikis/naval-architecture/wiki/concepts/*.md` (9) + `entities/classification-societies.md` (1) |
| Index update | `knowledge/wikis/naval-architecture/wiki/index.md` |
| Log update | `knowledge/wikis/naval-architecture/wiki/log.md` |
| Plan review — Claude | `scripts/review/results/2026-05-02-plan-2589-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-02-plan-2589-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-2589-gemini.md` |

---

## Deliverable

Ten new concept/entity pages will exist under `knowledge/wikis/naval-architecture/wiki/`, each carrying `CLAUDE.md`-compliant frontmatter, ≥1 standards-body cross-reference (IMO/ITTC/IACS/SNAME), ≥2 `see_also` cross-links, and zero overlap with #2566 or #2568 deliverables — with `index.md` updated to surface every new page in its catalogue table.

---

## Pseudocode

```
# Per-page authoring contract (applies to all 10 new pages):
function author_concept_page(slug, scope_summary):
    write frontmatter:
        title: human-readable
        tags: [domain-tag, sub-topic-tag, standards-tag]
        added: 2026-05-02
        last_updated: 2026-05-02
        sources: [naval-architecture-resources]
        see_also: [≥2 sibling-page paths]
    section "Scope" — 1 paragraph stating what the page IS and what it is NOT (boundary page pattern from #2567)
    section "Key Concepts" — 5–10 bulleted definitions, each ≤1 line
    section "Standards / References" — ≥1 bullet NAMING IMO|ITTC|IACS|SNAME with stable URL or source-page link, but MUST NOT enumerate specific thresholds, formulas, or code clauses (those belong on `wiki/standards/<code-id>.md` per #2471 routing)
    section "Cross-References" — markdown links to ≥2 see_also targets
    forbid: extracted text from PDFs (#2482 deny-list)
    forbid: any reference to turning-circle, tactical-diameter, advance, transfer, Nomoto (#2568 reservation)
    enforce: word count ≤ 400 per page (concept summary, not chapter copy)

function update_index(index_path, new_pages):
    insert each new concept page into "Concepts" table (alphabetical by title)
    insert classification-societies into "Entities" table (replacing "No entity pages yet" line)
    bump page_count from 61 → 71 in frontmatter
    leave source_count untouched (no new sources)

function append_log(log_path):
    append "[2026-05-02] expand | naval-arch W1-D — 10 core concept pages"
        - Pages added: <list>
        - Notes: covers Tupper-5e + PNA core curriculum gaps; excludes #2566/#2568 reservations.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/naval-architecture/wiki/concepts/hull-form-geometry.md` | Lines plan, sectional-area curve, hull-form coefficients (boundary against `hydrostatics.md`) |
| Create | `knowledge/wikis/naval-architecture/wiki/concepts/intact-stability-criteria.md` | Names the IMO IS Code criteria categories (general, weather, severe-wind/rolling) without restating thresholds; cross-links to a future `wiki/standards/imo-is-code.md` page for specific values |
| Create | `knowledge/wikis/naval-architecture/wiki/concepts/damage-stability.md` | SOLAS Chapter II-1 subdivision, probabilistic damage stability, attained subdivision index |
| Create | `knowledge/wikis/naval-architecture/wiki/concepts/ship-resistance-components.md` | Frictional/wave-making/form/appendage/air decomposition; Froude scaling; ITTC 1957 |
| Create | `knowledge/wikis/naval-architecture/wiki/concepts/marine-propulsors.md` | FPP/CPP/podded/waterjet/azimuth/contra-rotating overview |
| Create | `knowledge/wikis/naval-architecture/wiki/concepts/propeller-theory.md` | Momentum + blade-element theories, KT/KQ/J open-water, hull-propeller coefficients |
| Create | `knowledge/wikis/naval-architecture/wiki/concepts/wave-theory-and-spectra.md` | Linear wave theory, Pierson-Moskowitz, JONSWAP, ITTC, ISSC spectrum families |
| Create | `knowledge/wikis/naval-architecture/wiki/concepts/ship-structural-strength.md` | Longitudinal strength + hull-girder bending concepts; NAMES IACS UR S without restating section-modulus formulas; cross-links to a future `wiki/standards/iacs-ur-s.md` page for specific clauses |
| Create | `knowledge/wikis/naval-architecture/wiki/concepts/ship-weights-and-loading.md` | Lightship + deadweight breakdown, hydrostatic loading, longitudinal weight distribution |
| Create | `knowledge/wikis/naval-architecture/wiki/entities/classification-societies.md` | IACS members (ABS, DNV, LR, BV, CCS, KR, NK, RINA, RS, IRS, PRS, CRS) — first entity page |
| Modify | `knowledge/wikis/naval-architecture/wiki/concepts/resistance-propulsion.md` | Reduce to index/router page; move detailed bullets to ship-resistance-components.md / propeller-theory.md / marine-propulsors.md (per review M1) |
| Modify | `knowledge/wikis/naval-architecture/wiki/concepts/stability.md` | Reduce intact-stability and damage-stability bullets to one-line pointers to new pages (per review M2) |
| Modify | `knowledge/wikis/naval-architecture/wiki/index.md` | Add 9 concept rows + 1 entity row; bump `page_count` 61 → 71 |
| Modify | `knowledge/wikis/naval-architecture/wiki/log.md` | Append expansion log entry |
| Modify | `knowledge/seeds/naval-architecture-resources.yaml` | Source-of-truth seed file driving `index.md` regeneration; add the 10 new pages here so tooling re-emits the index correctly (per review m7) |
| Create | `tests/knowledge/test_naval_architecture_expansion.py` | TDD frontmatter / cross-link / standards-citation / index-resolves / no-redundant-content / see-also-resolves checks |
| Update | `docs/plans/README.md` | Add this plan to plan index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_all_ten_pages_exist` | Each of the 10 new files is on disk | path list | all 10 `Path.exists()` is True |
| `test_frontmatter_required_fields` | Every new page has `title`, `tags`, `added`, `last_updated` per `CLAUDE.md` schema | parse YAML frontmatter | all 4 keys present, non-empty |
| `test_frontmatter_see_also_min_two` | Each page lists ≥2 entries in `see_also` | parse YAML | `len(see_also) >= 2` |
| `test_at_least_one_standards_reference` | Page body cites ≥1 of IMO / ITTC / IACS / SNAME | regex search of body text | match found per page |
| `test_no_reservation_overlap_in_new_pages_and_no_expansion_in_existing` | Body contains zero #2568 reserved phrases in the 10 NEW pages, AND no expansion of existing occurrences in `concepts/maneuvering-validation-metrics.md` (line-count of reserved-phrase matches must equal pre-edit baseline) | regex `r'\b(turning circle\|tactical diameter\|Nomoto)\b'` (case-insensitive) over new pages + delta check on existing maneuvering-validation-metrics.md | zero matches in new pages; zero net new matches in existing page (per review M3) |
| `test_word_count_under_400` | Concept summary discipline (no chapter copy per #2482) | count words | each page < 400 words |
| `test_index_links_resolve` | Every relative link in `index.md` Concepts + Entities tables resolves | walk markdown links | 100% resolve |
| `test_see_also_paths_resolve` | Every `see_also` entry in each new page's frontmatter points to a real file on disk (relevance check, not just structural shell — per review m4) | parse YAML, `Path.exists()` per entry | 100% resolve |
| `test_index_page_count_bumped` | `index.md` frontmatter `page_count` updated to ≥71 | parse YAML | `page_count >= 71` |
| `test_log_entry_appended` | `log.md` contains a 2026-05-02 expand entry | grep | match present |
| `test_no_pdf_extraction_markers` | New pages contain no copy-paste markers (e.g. very long single paragraphs > 80 words, or "Page N of M" stamps) | heuristic | no flagged paragraphs |
| `test_no_redundant_content_between_old_and_new_pages` | After modification, `concepts/resistance-propulsion.md` MUST NOT contain the five resistance-component bullets (frictional/wave-making/form/appendage/air) AND MUST NOT contain the five propulsor-type bullets (FPP/CPP/podded/waterjet/azimuth) AND MUST NOT contain the propeller open-water bullets — those bullets live only on the new pages (per review M1) | regex match for the bullet phrases against `resistance-propulsion.md` | zero matches; the page is reduced to an index/router |

---

## Acceptance Criteria

- [ ] All 10 new wiki pages will exist with valid frontmatter (`title`, `tags`, `added=2026-05-02`, `last_updated=2026-05-02`).
- [ ] Each new page will NAME ≥1 standards body (IMO / ITTC / IACS / SNAME) with stable URL or sibling source-page link, but MUST NOT enumerate specific thresholds, formulas, or code clauses — those belong on `wiki/standards/<code-id>.md` per #2471 routing.
- [ ] `concepts/stability.md` will be updated to defer detailed intact-stability and damage-stability criteria to the new pages (one-line pointers, per review M2).
- [ ] `concepts/resistance-propulsion.md` will be reduced to an index/router page; the five resistance-component bullets, the five propulsor-type bullets, and the propeller-open-water bullets will exist only on the new pages (per review M1).
- [ ] Each new page will list ≥2 `see_also` cross-links.
- [ ] No new page will reference any noun-phrase reserved by #2568 (turning circle, tactical diameter, advance, transfer, Nomoto).
- [ ] No new page will duplicate scope of `concepts/yaw-moment-rudder-sweep.md`, `concepts/rudder-force-modeling.md`, `concepts/rudder-stock-design-checks.md`, or `concepts/steering-gear-design-checks.md` (the #2564/#2567 deliverables).
- [ ] `index.md` Concepts table will list 9 new rows (alphabetical); Entities table will list 1 new row replacing the empty placeholder.
- [ ] `index.md` frontmatter `page_count` will read ≥71.
- [ ] `log.md` will carry a `[2026-05-02] expand | naval-arch W1-D` entry.
- [ ] `tests/knowledge/test_naval_architecture_expansion.py` will pass: `uv run pytest tests/knowledge/test_naval_architecture_expansion.py -v`.
- [ ] No regression in existing knowledge tests: `uv run pytest tests/knowledge/ -v`.
- [ ] Each new page will be ≤400 words (concept-summary discipline per #2482 deny-list).
- [ ] Review artifacts will be posted under `scripts/review/results/2026-05-02-plan-2589-{claude,codex,gemini}.md`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | MAJOR → revised | 4 MAJOR (resistance-propulsion duplication; stability.md overlap; reserved-phrase test scope; standards-cross-ref boundary) + 8 MINOR — all addressed inline |
| Codex | UNAVAILABLE | codex-cli 0.124.0 stdin-hang regression (#2479); fanout dispatch hung; killed at 2026-05-02T12:21Z |
| Gemini | UNAVAILABLE | gemini CLI cwd=/tmp sandbox cannot resolve repo paths; err logged to scripts/review/results/.failed-fanout-2026-05-02/ |

**Overall result:** PASS-after-revision (4 MAJOR + 8 MINOR fixes applied 2026-05-02)

**Revisions made based on review:**
- M1 — `concepts/resistance-propulsion.md` will be reduced to an index/router; the five resistance-component bullets, the five propulsor-type bullets, and the propeller-open-water bullets will be moved into the three new pages. Added Files-to-Change row + new TDD test `test_no_redundant_content_between_old_and_new_pages`.
- M2 — `concepts/stability.md` will be amended to point at the new `intact-stability-criteria.md` and `damage-stability.md`. Added Files-to-Change row + Acceptance Criterion.
- M3 — Reserved-phrase test renamed `test_no_reservation_overlap_in_new_pages_and_no_expansion_in_existing` and scope revised to "no NEW occurrences in the 10 new pages plus no expansion of existing occurrences in `concepts/maneuvering-validation-metrics.md`" (option b in the review).
- M4 — Acceptance Criterion + Pseudocode `Standards / References` clause clarified: pages NAME standards bodies but MUST NOT enumerate specific thresholds/formulas/clauses. Page-scope language for `intact-stability-criteria.md` and `ship-structural-strength.md` constrained accordingly with cross-link forward-references to `wiki/standards/imo-is-code.md` and `wiki/standards/iacs-ur-s.md`.
- m1 — Source-summary count corrected 36 → 43 (lines ~25, ~120).
- m2 — 61-vs-62 reconciled inline: `index.md` `page_count` excludes `index.md` itself; on-disk count goes 62 → 72 while `page_count` goes 61 → 71.
- m3 — IMO Intact-Stability URL replaced with the canonical Maritime Safety landing `https://www.imo.org/en/OurWork/Safety/Pages/Default.aspx`; link-resolution will be re-verified at implementation.
- m4 — Added TDD test `test_see_also_paths_resolve` to convert structural shell into a real relevance check.
- m5 — Word-count cap committed at 400 (default); Open Question removed.
- m6 — Aggregated `entities/classification-societies.md` committed as a permanent design call independent of batch size; circular-reasoning Open Question removed.
- m7 — `knowledge/seeds/naval-architecture-resources.yaml` declared the source of truth driving `index.md` regeneration; added Files-to-Change row.
- m8 — ITTC procedure-number citation downgraded to "to be verified at implementation" with confidence-downgrade note; pages will cite ITTC homepage URL until specific numbers are confirmed.

**Provenance:** Single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`. Round-1 MAJOR; round-2 verdict pending user re-review.

---

## Risks and Open Questions

- **Risk: terminology drift (US vs. EU vocab).** Tupper uses "manoeuvring", PNA uses "maneuvering"; "lines plan" vs. "lines drawing"; "longitudinal strength" vs. "hull girder strength"; "scantlings" (UK class-rules) vs. "structural design" (US PNA). Will adopt PNA/SNAME spelling as primary with EU spelling parenthetical on first occurrence per page.
- **Risk: over-reliance on Western canonical sources.** Tupper, PNA, ITTC, IACS dominate the citable set. Chinese (CCS rules), Russian (RS), and Japanese (NK) class society perspectives will appear only via the IACS-membership entity page.
- **Risk: false-gap from terminology mismatch.** `concepts/resistance-propulsion.md` already mentions propulsor types; the new `marine-propulsors.md` and `ship-resistance-components.md` will explicitly cross-link to the existing page and state the boundary in the Scope section (boundary-page pattern from #2567 deliverables).
- **Risk: silent overlap with #2568.** Any future-tense mention of "rate of turn", "rudder angle", "course-keeping" inside `intact-stability-criteria.md` (weather criterion) could brush #2568 surface area. Tests will hard-fail on the reserved-phrase regex.
- **Risk: scope creep into vibration / ship-types / CFD.** Three additional Tupper chapters remain unaddressed; this plan deliberately defers them to a W2 follow-up (preserves the 10-page bound).
- **Risk: index-edit collision (resolved per review m7).** `index.md` is regenerated by `llm-wiki` tooling; the seed file `knowledge/seeds/naval-architecture-resources.yaml` IS the source of truth this plan edits. The plan writes the 10 new pages into the seed, then writes `index.md` (so the catalogue is consistent the moment the change lands), and `log.md` carries the audit entry.

- **Decision (review m6): classification-society rules.** This plan commits to a single aggregated `entities/classification-societies.md` page as a **permanent design call independent of batch size**. The aggregation is correct because the entity-page is a directory of IACS members with cross-links to per-society standards pages (when those promote later via calc-citation needs); per-society fan-out is reserved for the standards-page tier per #2471 routing. This is no longer an Open Question.
- **Decision (review m5): word-count cap.** 400 words per new page is the committed default. Existing baseline pages average ~150–250 words; 400 leaves headroom for the new pages without crossing into textbook-chapter density per #2482. Removable in implementation if a specific page legitimately needs more — but only with a noted exception in the page itself. This is no longer an Open Question.
- **Open: should `entities/imo-regulatory-framework.md` ship in this batch (making it 11 pages) or in W2?** Current plan defers to W2.

---

## Complexity: T2

**T2** — 10 new wiki pages + 2 modified registry files + 1 new test module. Multi-file, TDD required, but no new code logic / no calc-citation emission / no calc-module touch. Risk is concentrated in cross-link discipline and #2568 reservation hygiene, both addressable with regex tests. Not T3 because there is no new module / no calc / no migration / no schema change.
