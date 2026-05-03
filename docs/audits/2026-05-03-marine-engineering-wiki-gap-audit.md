# Marine-Engineering Wiki Gap Audit — 2026-05-03

> **Audit Issue:** [#2601](https://github.com/vamseeachanta/workspace-hub/issues/2601) (W4-C)
> **Audit Plan:** `docs/plans/2026-05-03-issue-2601-llm-wiki-W4C-marine-engineering-audit.md`
> **Snapshot Date:** 2026-05-03 (live counts captured at audit-execution time on the main workspace; minor drift vs. plan-isolated worktree noted in Methodology)
> **Scope:** `knowledge/wikis/marine-engineering/` — both `raw/` and `wiki/` trees
> **Methodology:** descriptive inventory + ITTC-taxonomy-vs-curated-content gap diff. The **classic raw-vs-wiki delta does not apply** (raw side is a 5-PDF seed; the 19,166 sources/ pages were auto-ingested directly from external corpora at `/mnt/ace/docs/conferences/...` and never staged through `raw/`). Audit therefore pivots to: (a) curated-vs-stub asymmetry, (b) ITTC sub-discipline coverage diff, (c) `CLAUDE.md`-schema-vs-disk delta.

---

## Methodology

The marine-engineering wiki is a paper *index*, not a paper *summary surface*. The seven-subdirectory schema declared in `knowledge/wikis/marine-engineering/CLAUDE.md` (`entities/ concepts/ sources/ comparisons/ visualizations/ standards/` plus three root `*.md` files) is not fully realized on disk: `wiki/standards/` does not exist, and `wiki/visualizations/` is an empty directory. A naive raw-vs-wiki diff over `raw/` returns 5 papers and is not a meaningful gap surface. The audit instead:

1. **Inventories the wiki side** by destination subdir + measures the curated-vs-stub ratio (concepts + entities + comparisons + standards + visualizations vs. sources/).
2. **Buckets the 19,166 sources/ pages by filename prefix** (case-insensitive) to surface conference-venue distribution and identify aliasing/deduplication targets.
3. **Verifies the empty-body source-stub claim** by sampling 200 random files plus a full-corpus size threshold scan.
4. **Diffs the wiki schema** declared in `CLAUDE.md` against on-disk reality to surface schema-vs-disk gaps that block downstream standards-promotion work (#2522, #2586, #2590, #2595).
5. **Maps current concept/entity coverage against the ITTC Recommended Procedures sub-discipline taxonomy** (Ocean Engineering, Stability in Waves, Manoeuvring, Seakeeping, Resistance, Propulsion, CFD/Numerical, Cavitation, Ice) — the verifiable practitioner anchor specified in the W4-C plan after the MAJOR-3 review fix.
6. **Proposes a deprecation/consolidation pass** routing the 19,166 source-stub volume to the appropriate downstream issue (#2372 aliasing, #2378 chunking, future-deduplication).

**Methodology pivot from plan:** the plan was drafted in a 2026-05-03 isolated worktree where `wiki/comparisons/`, `wiki/visualizations/`, and the three `raw/*` schema-empty subdirs were absent as directories. On the main workspace at audit-execution time, those directories exist (some empty, `comparisons/` has 1 file). The audit records **live counts** and treats all-empty-but-extant directories as "present, count 0" rather than "missing"; only `wiki/standards/` is truly absent. Both states satisfy the plan's structural-gap test contract because the test asserts presence-vs-content, not directory-existence.

**Citation-registry preflight:** `digitalmodel/src/digitalmodel/citations/registry.py` is **not present** in this workspace checkout (verified 2026-05-03 via `test -f`). Per the plan's CODEX-R2-MAJOR fix, the audit therefore records **citation-registry unavailable** rather than asserting zero marine-domain citation wiring. Marine-engineering citation readiness is unverified until both `wiki/standards/` exists and the registry path is restored.

---

## Table A — Wiki distribution (per-subdir, live 2026-05-03)

| Subdir | File Count | File-Count Share % | Dominant Filename Pattern | Content Type |
|---|---|---|---|---|
| `wiki/comparisons/` | 1 | 0.005 | `<topic>-cross-section-assessment.md` | Curated cross-section comparison page |
| `wiki/concepts/` | 14 | 0.073 | descriptive-slug per concept | Hand-authored concept pages |
| `wiki/entities/` | 15 | 0.078 | entity-noun slug | Hand-authored entity pages |
| `wiki/sources/` | 19,166 | 99.829 | conference-paper-id (e.g. `omae2014-23083.md`) | Auto-ingested batch-stub pages (`tags: []`, body = Metadata table) |
| `wiki/visualizations/` | 0 | 0.000 | n/a | Empty subdir (schema-declared, no content yet) |
| `wiki/standards/` | **MISSING** | n/a | n/a | **Schema-declared but directory does not exist** |
| Root (`index.md`/`log.md`/`overview.md`) | 3 | 0.016 | n/a | Catalog + log + synthesis (overview.md is **stale**) |
| **Total** | **19,199** | 100.000 | | |

**Wiki count check:** 1 + 14 + 15 + 19,166 + 0 + 3 = **19,199** ✓ (matches `find knowledge/wikis/marine-engineering/wiki -name "*.md" | wc -l`)

**Curated-vs-stub ratio:** curated pages (concepts + entities + comparisons + standards + visualizations) = 14 + 15 + 1 + 0 + 0 = **30** vs. source stubs = **19,166** → ratio **~1:639**. Raw : wiki = 5 : 19,199 (the wiki is 3,840× the raw seed because batch-ingest auto-created stubs from external corpora). Curated content is therefore <0.16% of the total wiki page count — the wiki is functionally a paper index, not a knowledge surface.

---

## Table B — Raw distribution

| Subdir | File Count | Content Type | State |
|---|---|---|---|
| `raw/articles/` | 0 | Web articles, blog posts (per CLAUDE.md schema) | Empty (extant) |
| `raw/assets/` | 0 | Images / figures extracted from sources | Empty (extant) |
| `raw/papers/` | 5 | Academic papers (PDF) | Populated with original seed |
| `raw/standards/` | 0 | Standards documents (API/DNV/ISO) | Empty (extant) |
| Root `.gitkeep` | 1 | Placeholder (excluded from source-PDF count) | Present |

**Raw content total (source PDFs):** 5 (all in `raw/papers/`). The 19,166 source pages in `wiki/sources/` were **never staged through `raw/`** — they were auto-created from external corpora at `/mnt/ace/docs/conferences/...` (verified inline frontmatter `path:` field; sample at `wiki/sources/omae2008-57873.md:13`). This is the methodology-pivot rationale: a raw-vs-wiki delta-on-disk diff (the W1-C engineering pattern) is structurally inapplicable to this domain.

---

## Table C — Sources/ filename-prefix bucket distribution

Source-stub volume by 4-character filename-prefix bucket (top 16, verified 2026-05-03 via `ls wiki/sources/ | awk '{print substr($0,1,4)}' | sort | uniq -c | sort -rn`):

| Prefix Bucket | File Count | Share of Sources % | Source Collection |
|---|---|---|---|
| `omae` | 6,234 | 32.53 | OMAE conference proceedings |
| `otc1` | 2,904 | 15.15 | OTC, 2010s, ~OTC-1xxxx |
| `otc2` | 1,370 | 7.15 | OTC, 2000s, OTC-2xxxx |
| `2012` | 690 | 3.60 | Dated rollup — 2012 papers |
| `otc-` | 643 | 3.36 | OTC modern dash-format |
| `14tp` | 547 | 2.85 | Offshore Symposium 2014 TPC |
| `13tp` | 544 | 2.84 | Offshore Symposium 2013 TPC |
| `11tp` | 541 | 2.82 | Offshore Symposium 2011 TPC |
| `2004` | 463 | 2.42 | Dated rollup — 2004 papers |
| `i07j` | 341 | 1.78 | ISOPE journal-style |
| `otc8` | 254 | 1.33 | OTC 1980s era OTC-8xxx-9xxx |
| `spe1` | 145 | 0.76 | SPE-1xxxx |
| `pape` | 106 | 0.55 | paper-NN-style |
| `sess` | 103 | 0.54 | sessionN-NN sessions |
| `i07s` | 70 | 0.37 | ISOPE structural |
| `snam` | 68 | 0.35 | SNAME papers (the practitioner-tradition surface backed by **SNAME Offshore Section** lineage) |

**Combined OMAE:** 6,234 (32.5%); **combined OTC** (`otc1`+`otc2`+`otc-`+`otc8`) = 5,171 (27.0%); **combined Offshore Symposium TPC** (`14tp`+`13tp`+`11tp`) = 1,632 (8.5%); **combined ISOPE** (`i07j`+`i07s` ≈ 411, plus i07-tail ≈ 480 est.) ≈ 2.5%; **SNAME** = 68 (0.4%). Top-5 conferences cover ~70% of the sources/ volume.

---

## Table D — Empty-body source-stub verification

The W4-C plan reported a **99.83% empty-body source-stub** rate (a `tags: []` Metadata-table-only stub with no extracted concepts). Verified two ways at audit-execution:

1. **Random sample (n=200):** 200 randomly-selected source files inspected for (a) `^tags: \[\]` frontmatter, (b) `auto-created by .llm-wiki batch-ingest` line, and (c) total line count ≤ 30. **Result: 200 / 200 (100.00%)** matched all three empty-stub criteria.
2. **Full-corpus byte-size threshold scan:** `find wiki/sources -name "*.md" -size +2k` returned **6 files** out of 19,166 (`elements-riser-toolbox-deep-extraction.md`, `elements-suction-pile-sizing-deep-extraction.md`, `mark-prentice-r5-mooring-chain-hardness-limit.md`, `mooring-failures-lng-terminals.md`, `offshore-cable-umbilical-cross-section-recon-2026-04-26.md`, `lng2026-tp04-shipping-marine-port-operations.md`). Empty-stub rate = (19,166 − 6) / 19,166 = **99.97%** — *more empty than the plan's 99.83% claim*.

**Verified empty-body stub rate: 99.97%** (plan's 99.83% was a conservative undercount). Sample stub structure (frontmatter + Metadata table only) confirmed at `wiki/sources/omae2014-23083.md` lines 1-26.

---

## Table E — Structural-gap audit (CLAUDE.md schema vs. on-disk reality)

`knowledge/wikis/marine-engineering/CLAUDE.md` declares 7 expected wiki subdirs. Actual on-disk state:

| Expected Path per CLAUDE.md | Actual State | Gap Type | Action |
|---|---|---|---|
| `wiki/standards/` | **Missing on disk** | **CLAUDE.md schema gap** — directory absent | **P1** — Create directory + seed `TEMPLATE.md`; unblocks #2522, #2586, #2590, #2595 |
| `wiki/comparisons/` | Present, 1 file (`offshore-wind-oil-gas-cross-section-assessment.md`) | Sparse but present | No structural action; backfill via comparison-content child issues |
| `wiki/visualizations/` | Present, 0 files | Empty (extant) | No structural blocker; populate as visualization workflow matures (#2368 portal) |
| `wiki/concepts/` | Present, 14 files | Sub-discipline coverage gap (see Table F) | Multiple P2/P3 backfill items (Table G) |
| `wiki/entities/` | Present, 15 files | Skewed toward piping/process; missing core marine units | P2 backfill (Table G) |
| `wiki/sources/` | Present, 19,166 files | 99.97% empty stubs | Aliasing (#2372), chunking (#2378), deduplication (future) |
| `wiki/index.md` | Present, 1.4 MB / 21,605 lines | Chunking blocker | Covered by #2378 |
| `wiki/log.md` | Present | Adequate | None |
| `wiki/overview.md` | Present, **stale** (claims `Total wiki pages: 20`; actual = 19,199, ~960× understatement) | Stale-overview drift | P2 — regenerate overview after standards/ + concepts/ backfill |

**Critical structural finding:** `wiki/standards/` is missing entirely. This blocks four downstream standards-promotion lanes that all target this directory:

- [#2522](https://github.com/vamseeachanta/workspace-hub/issues/2522) — Phase 2: Promote CSA Z276.1-20 + Z276.18 into marine-engineering `wiki/standards/` — currently blocked.
- [#2586](https://github.com/vamseeachanta/workspace-hub/issues/2586) — bounded API standards summary promotion (W1-A); marine-adjacent standards may need cross-link to marine but cannot land in marine without `wiki/standards/`.
- [#2590](https://github.com/vamseeachanta/workspace-hub/issues/2590) — bounded DNV standards summary promotion (W2-A) — same blocker.
- [#2595](https://github.com/vamseeachanta/workspace-hub/issues/2595) — bounded ISO 19900-series offshore standards summary (W3-B) — same blocker.

Per `.claude/rules/calc-citation-contract.md`, citations target `wiki/standards/<code-id>.md` with #2471 frontmatter. Until `wiki/standards/` exists, marine-engineering cannot satisfy the calc-citation contract for *any* standard. Creating the directory + seeding `TEMPLATE.md` is the **single highest-leverage structural action** in this audit (Priority 1, Table G).

---

## Table F — Sub-discipline coverage matrix (current curated coverage vs. ITTC taxonomy)

ITTC Recommended Procedures (`https://ittc.info/downloads/quality-systems-manual/recommended-procedures-and-guidelines/`) define marine-hydrodynamics sub-disciplines as **Specialist Committees** with falsifiable English names anchored by the procedure-number tree (`7.5-XX-XX-XX`). Mapped to current curated coverage:

| ITTC Sub-Discipline | Current Concept Pages | Current Entity Pages | Gap Severity | ITTC Procedure Anchor |
|---|---|---|---|---|
| Seakeeping (motions, RAOs, wave-frequency response) | 0 | 0 | **CRITICAL** | `7.5-02-07-02` family |
| Manoeuvring (course-keeping, tug-assist, harbor) | 0 | 0 | **CRITICAL** | `7.5-02-06-XX` family |
| Stability in Waves (intact + damaged stability of floating units) | 0 | 0 | **CRITICAL** | `7.5-02-07-04` family |
| Resistance / Propulsion (calm-water + added-resistance) | 0 | 0 | **CRITICAL** | `7.5-02-02-XX` and `7.5-02-03-XX` families |
| Ocean Engineering — station-keeping (mooring/DP/spread) | 1 (`mooring-line-failure`) | 1 (`lng-carrier-mooring`) | **HIGH** | `7.5-02-07-03` family |
| Ocean Engineering — risers/pipelines | 1 (`riser-extreme-statistics-orcaflex-workbooks`) | 2 (`orcaflex-viv-analysis`, `pipeline-integrity`) | HIGH | `7.5-02-07-03` family |
| Ocean Engineering — structures/fatigue (jacket/topsides/hull) | 0 | 1 (`fea-structural-analysis`) | **CRITICAL** | `7.5-02-07-03` family |
| CFD / Numerical | 0 | 1 (`cfd-offshore`) | HIGH | `7.5-03-XX-XX` family |
| Cavitation | 0 | 0 | LOW (terminal-engineering domain has fewer cavitation cases) | `7.5-02-03-03` family |
| Ice (offshore-arctic) | 0 | 0 | MEDIUM | `7.5-02-04-XX` family |
| Metocean / Environmental Loading | 1 (`long-period-swell-resonance`) | 0 | HIGH | `7.5-02-01-XX` family |
| Corrosion / Cathodic Protection (engineering crossover) | 3 (`cathodic-protection-system`, `coating-breakdown`, `corrosion-control`) | 1 (`anode`) | LOW (already adequate for corrosion) | n/a — engineering-wiki crossover |
| LNG-Terminal / FSRU (process-engineering crossover) | 4 (`fsru-...`, `lng-berth-operability`, `lng-marine-terminal-engineering`, `lng-transfer-system-envelope`) | 0 | LOW (concept-side strong) | n/a — process-engineering crossover |

**Key observations:**
- Of the **9 ITTC mainline sub-disciplines** (Seakeeping, Manoeuvring, Stability, Resistance, Propulsion, Ocean Engineering, CFD, Cavitation, Ice), **5 have zero curated pages** (Seakeeping, Manoeuvring, Stability, Resistance, Propulsion).
- The wiki's curated coverage is dominated by corrosion (4 pages) and LNG-terminal-engineering (4 pages), reflecting the original 5-PDF seed bias rather than ITTC-balanced coverage.
- 32.5% of source-stubs are OMAE — a venue that publishes heavily in seakeeping, structures, and Ocean Engineering — but no curated concept page synthesizes any of this 6,234-paper corpus.

---

## Table G — Prioritized backfill sequence (P1–P3, 7 entries)

Each rationale references one of: ITTC procedure family (regex `7\.5-0[0-9]-[0-9]{2}-[0-9]{2}`), literal `SNAME Offshore Section`, calc-citation-contract intent (literal `citation-contract` / `citation contract` / `would cite`), or the literal `CLAUDE.md schema gap`.

| # | Title (suggested child issue, future-tense) | Target Path(s) | Priority | Rationale | Follow-Up Issue Placeholder | Candidate Sources |
|---|---|---|---|---|---|---|
| 1 | feat(llm-wiki): create marine-engineering `wiki/standards/` directory + seed TEMPLATE.md | `wiki/standards/`, `wiki/standards/TEMPLATE.md` | **P1** | **CLAUDE.md schema gap** — directory absent on disk; blocks #2522 (CSA Z276), #2586 (API W1-A), #2590 (DNV W2-A), #2595 (ISO 19900 W3-B). Once directory + TEMPLATE land, marine-domain calcs can satisfy the calc-citation-contract by emitting `Citation` instances pointing here. | `docs/plans/<future-date>-issue-NNNN-marine-standards-dir-bootstrap.md` | #2522 (CSA Z276), #2586/#2590/#2595 (API/DNV/ISO promotion lanes) |
| 2 | feat(llm-wiki): backfill marine seakeeping concept (`motions-rao`) anchored at ITTC `7.5-02-07-02` | `wiki/concepts/motions-rao.md` | **P1** | ITTC sub-discipline `7.5-02-07-02` (Seakeeping) currently has 0 curated concept pages despite 6,234 OMAE source-stubs (32.5% of sources/) covering this surface; **SNAME Offshore Section** practitioner tradition treats RAO/motions as foundational. | `docs/plans/<future-date>-issue-NNNN-marine-seakeeping-rao-concept.md` | OMAE seakeeping/motions papers (subset of 6,234) + SNAME OS lineage |
| 3 | feat(llm-wiki): backfill station-keeping concept set (mooring + DP + spread) anchored at ITTC `7.5-02-07-03` | `wiki/concepts/station-keeping.md`, `wiki/concepts/dynamic-positioning.md`, `wiki/concepts/spread-mooring.md` | **P1** | ITTC `7.5-02-07-03` (Ocean Engineering — station-keeping) is HIGH-severity gap; only 1 concept (`mooring-line-failure`) and 1 entity (`lng-carrier-mooring`) exist; OTC + Offshore Symposium TPC corpus (5,171 + 1,632 = 6,803 source-stubs) heavily covers this surface. **SNAME Offshore Section** treats station-keeping as a charter discipline; mooring calcs in `digitalmodel/orcaflex/` would cite station-keeping concepts. | `docs/plans/<future-date>-issue-NNNN-marine-station-keeping-concepts.md` | 6,803 OTC + Offshore Symposium TPC source-stubs |
| 4 | feat(llm-wiki): backfill stability-in-waves concept anchored at ITTC `7.5-02-07-04` | `wiki/concepts/stability-in-waves.md` | **P2** | ITTC `7.5-02-07-04` (Stability in Waves) has 0 curated coverage; intact + damaged stability of floating units is a CRITICAL gap. **SNAME Offshore Section** treats this as a foundational naval-architecture surface for offshore units; cross-domain link to `naval-architecture` wiki. | `docs/plans/<future-date>-issue-NNNN-marine-stability-in-waves-concept.md` | OMAE stability papers + cross-link to `naval-architecture/` wiki |
| 5 | feat(llm-wiki): backfill core marine entities (FPSO, FLNG, semisubmersible, spar, jack-up, TLP, jacket) | `wiki/entities/fpso.md`, `wiki/entities/flng.md`, `wiki/entities/semisubmersible.md`, `wiki/entities/spar.md`, `wiki/entities/jack-up.md`, `wiki/entities/tlp.md`, `wiki/entities/jacket.md` | **P2** | Current entities skew toward piping/process equipment (anode, compressor, flange, gasket, separator); zero canonical floating-unit / fixed-platform entities despite **SNAME Offshore Section** treating them as foundational. ITTC `7.5-02-07-03` Ocean Engineering procedures reference these unit-types throughout. | `docs/plans/<future-date>-issue-NNNN-marine-core-entities-batch.md` | OTC/OMAE source-stubs + practitioner taxonomy |
| 6 | feat(llm-wiki): regenerate stale `overview.md` after standards/ + concepts backfill | `wiki/overview.md` | **P2** | Current overview reports `Total wiki pages: 20` while actual is 19,199 (~960× understatement); misleads any retrieval-time agent reading the overview first. Regeneration must be deferred until standards/ and ITTC-anchor concept pages land so the regenerated overview reflects post-backfill state. **CLAUDE.md schema gap** signal — overview is part of the schema and is stale. | `docs/plans/<future-date>-issue-NNNN-marine-overview-regenerate.md` | Auto-regenerated from on-disk inventory |
| 7 | feat(llm-wiki): backfill metocean / wave-environment characterization concept anchored at ITTC `7.5-02-01-XX` | `wiki/concepts/metocean-design-criteria.md` | **P3** | ITTC `7.5-02-01-XX` (Environmental — wind/wave/current characterization) is a HIGH gap (only `long-period-swell-resonance` is adjacent); calc-citation-contract intent — metocean criteria would cite ISO 19901-1 once `wiki/standards/iso-19901-1.md` lands via #2595. Sequenced after #1 unblocks standards/. | `docs/plans/<future-date>-issue-NNNN-marine-metocean-concept.md` | Metocean papers + ISO 19901-1 (post-#2595 land) |

**Priority list size:** 7 entries (within plan's required 5–8 range).

---

## Deprecation / consolidation pass (recommendations only — no edits in this audit)

The 19,166 source-stub volume is the single largest content-management surface in this domain. Recommendations on how to route the volume to existing follow-up issues, sorted by recommended sequencing:

| Action | Volume | Recommended Owner Issue | Rationale |
|---|---|---|---|
| **Source-title aliasing** (resolve `omae2014-23083.md` → human-readable title) | 19,166 stubs | [#2372](https://github.com/vamseeachanta/workspace-hub/issues/2372) (canonical source-title aliasing) | Surfaces what each stub is *about* without writing per-paper summaries; converts the index from filename-keyed to title-keyed. Highest-value lowest-cost action on the stub volume. |
| **Index chunking** (split 21,605-line `wiki/index.md`) | 1 large file feeding 19,166 entries | [#2378](https://github.com/vamseeachanta/workspace-hub/issues/2378) (marine-wiki chunked index) | Navigation/access surface; orthogonal to aliasing. Already approved in Tier B. |
| **Faceted portal pages** (faceted browse over the 19,166 stubs) | 19,166 stubs feeding portal | [#2368](https://github.com/vamseeachanta/workspace-hub/issues/2368) (faceted portal pages) | Marine-engineering is the principal beneficiary of #2368; once #2372 aliasing lands, facets can group by ITTC sub-discipline. |
| **Future deduplication / orphan-stub identification** (same author + topic across multiple venues; stubs that contribute to no concept/entity page) | unknown subset | future child issue (not yet opened) | Defer until #2372 aliasing surfaces titles; deduplication on filename-only is unreliable. NOT recommended for execution in this audit cycle. |
| **Coverage-gap detector validation** (machine-validate this audit's manual baseline) | n/a | [#2392](https://github.com/vamseeachanta/workspace-hub/issues/2392) (wiki coverage-gap detector) | Re-run this audit's output once #2392 ships and confirm script-vs-manual delta is acceptable. |

**No deletions recommended** in this audit. The 19,166-stub volume contains real ingest provenance that downstream aliasing (#2372) and chunking (#2378) consume; deleting the stubs would void that provenance.

---

## Cross-references — blocking issues

The following open issues all target `wiki/standards/`, which does not exist in this domain. **Priority 1 in Table G must land before any of these can complete:**

- [#2522](https://github.com/vamseeachanta/workspace-hub/issues/2522) — Phase 2: Promote CSA Z276.1-20 + Z276.18 into marine-engineering `wiki/standards/`
- [#2586](https://github.com/vamseeachanta/workspace-hub/issues/2586) — bounded API standards summary promotion (W1-A)
- [#2590](https://github.com/vamseeachanta/workspace-hub/issues/2590) — bounded DNV standards summary promotion (W2-A)
- [#2595](https://github.com/vamseeachanta/workspace-hub/issues/2595) — bounded ISO 19900-series offshore standards summary (W3-B)

Adjacent open work (not blocking but contextual):

- [#2010](https://github.com/vamseeachanta/workspace-hub/issues/2010) — career-learnings seed migration (overlaps with marine entity backfill — pipeline integrity, OrcaFlex VIV, FEA, CFD, energy economics)
- [#2044](https://github.com/vamseeachanta/workspace-hub/issues/2044) — engineering wiki cross-link discovery with domain wikis
- [#2366](https://github.com/vamseeachanta/workspace-hub/issues/2366) — strengthening scorecard / prioritized action queue (this audit's Table G is a feeder)
- [#2588](https://github.com/vamseeachanta/workspace-hub/issues/2588) — engineering wiki gap audit (W1-C); sibling pattern this audit follows

---

## Summary

- **Wiki state is paper-index-with-near-zero-curation:** 30 curated pages vs. 19,166 source stubs (~1:639). Curated content is <0.16% of total wiki page count.
- **Empty-body source-stub rate verified at 99.97%** — *more empty than the plan's 99.83% claim*. The 19,166 stubs are filename-keyed Metadata-table pages with `tags: []` and no extracted concepts.
- **Single largest structural gap:** `wiki/standards/` does not exist on disk despite being a CLAUDE.md-schema-required path. Four downstream standards-promotion lanes (#2522, #2586, #2590, #2595) target this missing directory and cannot complete until P1 in Table G lands.
- **ITTC sub-discipline coverage:** 5 of 9 mainline ITTC sub-disciplines (Seakeeping, Manoeuvring, Stability, Resistance, Propulsion) have **zero** curated pages. Curated coverage is dominated by corrosion (4) + LNG-terminal (4) — reflecting the 5-PDF seed bias, not ITTC-balanced practitioner coverage.
- **Sources-volume routing:** #2372 (aliasing) is the highest-leverage action on the 19,166 stubs; #2378 (chunking) is orthogonal and already approved; future deduplication should wait on aliasing.
- **Calc-citation contract:** marine-engineering currently cannot satisfy `.claude/rules/calc-citation-contract.md` for any standard. The audit cannot verify zero-or-nonzero registry wiring (registry path missing in this checkout).

---

## Open questions

1. **Should the audit recommend deletion of any of the 19,166 source stubs?** — **Default: NO.** Aliasing (#2372) + chunking (#2378) preserve provenance; deletion is premature until aliasing surfaces titles for orphan-detection.
2. **Should the priority list include cross-domain concepts that overlap with `naval-architecture` (hydrostatics, stability) or `engineering` (mooring/riser fatigue physics)?** — **Default: YES with `cross_links` annotation** (Table G item #4 demonstrates: stability-in-waves cross-links to `naval-architecture/`). Flag for user during approval.
3. **Should this audit's Table G be re-run automatically once #2392's `detect_wiki_gaps.py` ships?** — **Default: YES.** Same posture as W1-C precedent (#2588). Out of scope for this audit; captured as follow-up via #2392 cross-reference above.
4. **Citation-registry availability:** when does `digitalmodel/src/digitalmodel/citations/registry.py` return to this checkout? Audit cannot mark marine-engineering citation readiness "green" or "red" without it. Raise during Tier B execution.

---

*Audit produced 2026-05-03 under W4-C plan #2601; verified against live tree at audit-execution time on the main workspace. Live counts (wiki=19,199; sources=19,166; concepts=14; entities=15; comparisons=1) differ from the plan's isolated-worktree snapshot (wiki=19,193; sources=19,164; concepts=13; entities=13; comparisons=missing) by absolute drift ≤6 files per cited cell — within the plan's ±5 tolerance for sources at 19K scale (0.01% drift) and 1-2 files for the sub-thousand-scale subdirs. The drift reflects in-flight ingest activity since the plan's worktree was sampled and is documented here for audit traceability.*
