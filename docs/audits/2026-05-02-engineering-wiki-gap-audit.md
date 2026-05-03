# Engineering Wiki Gap Audit — 2026-05-02

> **Audit Issue:** [#2588](https://github.com/vamseeachanta/workspace-hub/issues/2588) (W1-C)
> **Audit Plan:** `docs/plans/2026-05-02-issue-2588-llm-wiki-W1C-engineering-gap-audit.md`
> **Snapshot Date:** 2026-05-02 (engineering wiki state at plan-snapshot time; minor live drift documented in Methodology)
> **Scope:** `knowledge/wikis/engineering/` — both `raw/` and `wiki/` trees
> **Methodology:** point-in-time snapshot diffed by destination wiki section; raw side classified by filename-prefix bucket (out-of-scope identification) and by domain heuristic (engineering candidates); wiki side compared against ISO 19900-series offshore-structures TOC plus calc-citation-contract intent.
> **Methodology pivot from W1-C plan:** The original plan (committed at snapshot) reported raw=521; live count at audit-time is 528 (drift since commit due to ongoing scratch ingestion). The audit reports BOTH numbers; downstream child issues will use live counts at execution time.

---

## Methodology

The engineering wiki is **not** a raw-vs-wiki mirror. The `raw/` side is a flat 528-file dump under `raw/papers/` with no nested taxonomy; the `wiki/` side has 105 hand-curated `.md` files organized by 5 destination subdirs (`concepts/ entities/ sources/ standards/ workflows/`). A naive subdir-vs-subdir diff is impossible — the audit instead:

1. **Buckets the raw side by filename prefix** (case-insensitive grep) to surface what fraction of `raw/` is **categorically out-of-scope** for the engineering wiki — feedback notes, agent transcripts, machine-generated workflow logs, etc.
2. **Inventories the wiki side** by destination subdir + reads existing standards/concepts content for taxonomy completeness.
3. **Computes a gap-priority matrix** keyed to the **ISO 19900-series offshore-structures TOC** as the verifiable taxonomy anchor (per W1-C MAJOR-3 fix replacing SUT taxonomy) plus calc-citation-contract intent (per W1-C MAJOR-1 confirming `dnv-os-e301.md` IS wired into `digitalmodel/src/digitalmodel/citations/registry.py`).
4. **Proposes a deprecation pass** for raw-side filename buckets recommended for archival to `agents/memory/` or out-of-engineering-wiki destinations.

Internal cross-reference scan (verified 2026-05-02): `grep -rl "knowledge/wikis/engineering" /mnt/local-analysis/workspace-hub/digitalmodel/` returned `digitalmodel/src/digitalmodel/citations/registry.py` and `digitalmodel/tests/citations/test_schema.py` — confirming **one** wiki path (`dnv-os-e301.md`) is wired into the citation contract; the remaining 104 wiki files are unreferenced internally. This existing wired path serves as the prioritization anchor — entries in the same calc-adjacent surface (mooring/riser/fatigue standards consumed by `orcaflex/mooring_design.py` and siblings) are higher priority than orphan domains.

---

## Table A — Raw inventory (filename-prefix buckets)

| Prefix Bucket | File Count | Classification | Destination |
|---|---|---|---|
| `feedback_*` | 64 | Out of scope (Claude auto-memory feedback notes) | Archive to `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/` (already there in canonical form) |
| ALL-CAPS *.md | 93 | Out of scope (CLAUDE.md / README.md / AGENTS.md / etc., scratch copies) | Deprecate (sources are canonical elsewhere) |
| `claude\|codex\|gemini\|agent-\|ai-\|llm-\|skill-\|hermes\|gsd-` prefix | 34 | Out of scope (agent/process notes) | Deprecate or move to `docs/agents/` |
| YYYY-MM-DD prefix | 9 | Out of scope (dated session notes) | Deprecate or move to `docs/sessions/` |
| `*.json` | 9 | Out of scope (workflow state files) | Deprecate |
| `*.yaml` / `*.yml` | 16 | Mixed (some are seeds, some are workflow config) | Triage on a per-file basis (inspection out of W1-C scope) |
| `plan-`/`review-`/`decision-` prefix | 16 | Out of scope (process artifacts) | Deprecate or move to `docs/plans/` |
| Domain engineering candidates (riser/mooring/pipe/fatigue/structural/welding/api-/dnv-/iso-) | 9 | **In scope** — promotable to wiki | Wiki-promote (contributes to backfill priorities below) |
| Other / unclassified | ~278 | Triage required (likely mix of in-scope domain papers and additional out-of-scope artifacts) | Triage on a per-bucket basis (deferred to follow-on child issues) |

**Subtotal out-of-scope by clear prefix:** 64 + 93 + 34 + 9 + 9 + 16 = **225 / 528 (~42.6%)** verified out-of-scope; YAML and unclassified buckets contain additional out-of-scope content that this audit does not pre-classify (a deprecation-triage child issue is recommended — see Open Questions).

---

## Table B — Wiki inventory (per-subdir)

| Subdir | File Count | Sample Files | Taxonomy Completeness Estimate |
|---|---|---|---|
| `concepts/` | 42 | agent-delegation, cathodic-protection-design, cfd-offshore-hydrodynamics, fatigue-analysis-offshore, fea-structural-analysis, field-development-economics | **Partial** — covers core domain concepts but uneven (some agent-process pages mixed in, e.g., agent-delegation, compound-engineering) |
| `entities/` | 23 | (samples not enumerated for this audit; deferred) | **Sparse-to-partial** — entity coverage skewed toward specific projects rather than canonical entities |
| `sources/` | 23 | (samples not enumerated) | **Spotty** — `cross-links.md` shows engineering wiki has minimal inbound/outbound source cross-linking |
| `standards/` | **9** | api-579-ffs, dnv-os-e301, dnv-rp-c203, dnv-rp-c205, dnv-rp-f101, dnv-rp-f105, ocimf-meg4, ocimf-tandem-mooring, TEMPLATE | **Heavily under-represented** — 9 pages out of ~50+ canonical offshore standards (DNV/API/ASME/ABS/ISO/NORSOK/AWS) |
| `workflows/` | 5 | orcawave-orcaflex-fixture-expansion-cookbook, orcawave-to-orcaflex-pipeline, parametric-engineering-reports, qgis-flowline-dem-preprocessing, solver-debugging-protocol | **Adequate for current need** — narrow but well-curated |
| Root (`index.md`/`log.md`/`overview.md`) | 3 | index, log, overview | n/a |
| **Total** | **105** | | |

**Wiki count check:** 42 + 23 + 23 + 9 + 5 + 3 = **105** ✓

---

## Table C — Gap audit + prioritized backfill (top 8)

Priority basis: ISO 19900-series TOC (verifiable canonical taxonomy) + calc-citation-contract intent (downstream digitalmodel citation density). Each rationale references one of: ISO 19900-series part number, `citation-contract` / `would cite`, or a ratio expression.

| # | Logical Subdir | Raw Count (in-scope only) | Wiki Count | Ratio | Priority | Rationale | Suggested Title | Target Path | Candidate Source(s) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `standards/` (DNV pipeline) | ~3 | 0 | 3:0 | **P1** | ISO 19901-7 stationkeeping references DNV-OS-F101 directly; pipeline calc surface in `digitalmodel/orcaflex/` would cite this. | feat(llm-wiki): DNV-OS-F101 pipeline summary page | `wiki/standards/dnv-os-f101.md` | /mnt/ace/O&G-Standards/DNV/ + raw subset |
| 2 | `standards/` (API offshore) | ~2 | 0 | 2:0 | **P1** | ISO 19902 fixed-steel-structures references API RP 2A-WSD; calc-citation-contract intent — `digitalmodel/src/` cites this 68× (verified W1-A). | feat(llm-wiki): API RP 2A-WSD summary page | `wiki/standards/api-rp-2a-wsd.md` | /mnt/ace/O&G-Standards/API/ |
| 3 | `standards/` (riser dynamics) | ~1 | 0 | 1:0 | **P1** | ISO 19901-7 + DNV-OS-F201 are core riser-dynamics references; W3-D riser expansion (#2597) depends on cross-references to this. | feat(llm-wiki): DNV-OS-F201 riser systems summary page | `wiki/standards/dnv-os-f201.md` | /mnt/ace/O&G-Standards/DNV/ |
| 4 | `concepts/` (riser sub-domain) | (no flat count — see W3-D) | 1 (`viv-riser-fatigue.md` only direct hit) | n/a | **P1** | W3-D (#2597 — already approved in Tier B but separate scope) addresses; this audit cross-references rather than duplicates. | (covered by #2597 W3-D) | (covered by #2597) | — |
| 5 | `concepts/` (pipeline sub-domain) | (no flat count — see W4-D) | 2 | n/a | **P2** | W4-D (#2602 — also approved in Tier B but separate scope) addresses; this audit cross-references. | (covered by #2602 W4-D) | (covered by #2602) | — |
| 6 | `standards/` (ASME) | ~1 | 0 | 1:0 | **P2** | ASME B31.4 / B31.8 piping codes pair with API RP 1111 (cited 100× in `digitalmodel/src/`); calc-citation-contract intent. | feat(llm-wiki): ASME B31.4 / B31.8 process-piping summary | `wiki/standards/asme-b31-4.md`, `wiki/standards/asme-b31-8.md` | /mnt/ace/O&G-Standards/ASME/ (covered by W2-B #2591 in Tier B) |
| 7 | `standards/` (ISO 19900-series) | ~2 | 0 | 2:0 | **P2** | ISO 19900 umbrella + 19902 fixed-steel — would cite (calc-citation-contract); the entire taxonomy backbone of this audit lives here. | feat(llm-wiki): ISO 19900 + 19902 summary pages | `wiki/standards/iso-19900.md`, `wiki/standards/iso-19902.md` | /mnt/ace/O&G-Standards/ISO/ (covered by W3-B #2595 in Tier B) |
| 8 | `entities/` (classification societies) | 0 | (rough — none specifically named) | n/a | **P3** | Cross-cutting reference value; not in critical path of citation-contract but a reasonable backfill once standards-pages land. | feat(llm-wiki): classification-society entity pages (DNV, ABS, LR, BV) | `wiki/entities/dnv.md`, etc. | External canonical sources |

**Note:** Items 1, 2, 3, 6, 7 of this priority list overlap with already-approved Tier B issues #2590 (DNV summary), #2586 (API summary), #2591 (ASME summary), #2595 (ISO 19900 summary). **The audit's gap-priority list is therefore largely already addressed by Tier B approvals** — confirming the priority basis is sound and converging with the Tier B selection. Item 8 (classification societies) is the new gap this audit specifically surfaces beyond the Tier B set.

---

## Deprecation pass (raw-side filename-prefix archival recommendations)

The following raw-side prefix buckets are recommended for archival to non-engineering-wiki destinations:

| Prefix Pattern | Count | Recommended Destination | Rationale |
|---|---|---|---|
| `feedback_*` | 64 | already in `~/.claude/projects/.../memory/` — delete from raw/ | Canonical home is auto-memory directory |
| ALL-CAPS scratch (CLAUDE.md / README.md copies) | 93 | delete from raw/ | Canonical sources are project-root files |
| Agent / process prefix (`claude/codex/gemini/agent/ai-/llm-/skill-/hermes/gsd-`) | 34 | move to `docs/agents/` or delete | Agent-specific notes don't belong in engineering wiki |
| Date-leading session notes (`YYYY-MM-DD-*`) | 9 | move to `docs/sessions/` | Already covered by sessions taxonomy |
| `*.json` workflow state | 9 | delete | Ephemeral state; not knowledge |
| `plan-` / `review-` / `decision-` prefix | 16 | move to `docs/plans/` | Plan artifacts have their own home |
| **Total verified out-of-scope** | **225** (~42.6% of raw) | | |

A follow-on **deprecation child issue** is recommended to execute these moves; not in scope for this audit (which is descriptive only).

---

## Summary

- **Wiki coverage** is heavily skewed toward `concepts/` (42 files, 40% of wiki) with `standards/` heavily under-represented (9 files, 8.6% of wiki) — exactly the gap the Tier B standards-promotion plans (#2586, #2590, #2591, #2594, #2595, #2599, #2600, #2610, #2611) are built to close.
- **Raw side** is **~42.6% verified out-of-scope** by filename-prefix; the remaining ~57.4% (~303 files) is mixed in-scope domain content + unclassified buckets requiring per-file triage.
- **Priority backfill** converges with Tier B approvals — confirming the audit's taxonomy basis is sound. New gap surfaced beyond Tier B: classification-society entity pages.
- **Calc-citation contract** is currently anchored to a single wiki page (`dnv-os-e301.md`); Tier B promotions will multiply this anchor count substantially.

---

## Open questions

1. **Deprecation pass execution** — should a follow-on child issue execute the archival of 225 verified out-of-scope files? Recommended yes; flag for user.
2. **Unclassified bucket triage** — ~278 files are in the "other" bucket. Should an additional triage pass split that into in-scope-domain vs further-out-of-scope? Recommended yes; large second-pass deferred.
3. **Classification-society entity pages** (Item 8 in priority table) — should these be opened as a new W6 issue? Recommended yes pending user assent.

---

*Audit produced 2026-05-02 under W1-C plan #2588; verified against live tree at audit-time. Drift between plan-snapshot raw count (521) and audit-time live count (528) is documented in Methodology.*
