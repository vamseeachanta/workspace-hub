---
date: 2026-05-12
session: llm-wiki external-content ingests (3) — naval-architecture + marine-engineering
status: COMPLETE — 3 commits pushed to vamseeachanta/llm-wiki main, no follow-ups required
session_kind: external-content-ingest (LinkedIn × 2 + vendor product family × 1)
artifacts:
  - commit 94e0bd62 (naval-architecture) — Miah Froude number
  - commit f24c6a8f (marine-engineering) — Lloyd's tug working-end fender height
  - commit 33338317 (marine-engineering) — NOV motion compensation systems
  - 5 PDFs archived at /mnt/ace/llm-wiki-archive/marine-engineering/raw/papers/ (NOV_*, ~56 MB)
---

# llm-wiki external-content ingests — 2026-05-12

## TL;DR

Three external-content ingests landed on `vamseeachanta/llm-wiki` `main` in one session, pushed as fast-forward `b0a441c6..33338317`. Two were LinkedIn practitioner posts (Miah Froude number; Lloyd's Maritime Institute tug fender discussion); one was a vendor product-family page with five downloadable brochures (NOV motion compensation systems). The vendor variant established a new precedent in the workflow memory: binary PDFs archived off-repo at `/mnt/ace/llm-wiki-archive/<domain>/raw/papers/` with vendor-prefixed filenames; in-repo source page references brochures by canonical filename only (no `/mnt/ace` paths leak into the public CC-BY-4.0 repo).

## What landed (in `vamseeachanta/llm-wiki`)

### Commit 1 — `94e0bd62` — naval-architecture / Miah Froude
- NEW `wikis/naval-architecture/wiki/sources/miah-2026-froude-number.md` — trigger-source summary.
- NEW `wikis/naval-architecture/wiki/concepts/froude-number.md` — substantive synthesis adding what the post omitted: length / volumetric / depth Froude variants, the displacement / semi-displacement / planing regime spectrum, and the Froude/Reynolds model-scale dilemma. Anchored on Tupper 5e, PNA Vol II (Lewis 1988), Larsson & Raven 2010, Bertram 2012, Molland Turnock Hudson 2017, Savitsky 1964, Froude 1874, ITTC RP 7.5-02-02-01.
- MOD `index.md` (page_count 72→74, source_count 44→45) + `log.md`.

### Commit 2 — `f24c6a8f` — marine-engineering / Lloyd's tug fender
- NEW `wikis/marine-engineering/wiki/sources/lloyds-maritime-institute-2026-tug-fender-height-discussion.md` — discussion-prompt summary.
- NEW `wikis/marine-engineering/wiki/concepts/tug-working-end-fendering.md` — substantive synthesis (working-end definition by tug-propulsion type, freeboard-matching design driver across the assisted-vessel mix, hull-geometry effects, tug-stability cap, fender-face geometries). Anchored on Hensen 2003 *Tug Use in Port* 2e, PIANC MarCom WG 33 (2002), BS 6349-4:2014 (named only), OCIMF MEG4 2018 (named only).
- MOD `index.md` (concepts header 21→22, page_count 19210→19212, source_count 19167→19168) + `log.md`.

### Commit 3 — `33338317` — marine-engineering / NOV motion compensation
- NEW `wikis/marine-engineering/wiki/sources/nov-2026-motion-compensation-product-family.md` — vendor product-family inventory (CMC, Riser Tensioners, AHD, AHDD, Offshore Product Reference Guide).
- NEW `wikis/marine-engineering/wiki/concepts/motion-compensation-systems.md` — substantive synthesis (passive vs active heave compensation; drillstring / riser tensioner / crane families; AHC control architecture; standards landscape). Anchored on API Spec 8C, API Spec 16F, API RP 16Q, DNV-OS-E101, ABS Guide for the Classification of Drilling Systems, ISO 13628 series, Hatleskog & Dunnigan 2007 IEEE JOE, Bai & Bai 2018 *Subsea Engineering Handbook* 2e.
- MOD `index.md` (concepts header 22→23, page_count 19212→19214, source_count 19168→19169) + `log.md`.

## Off-repo binaries (private vendor mount)

At `/mnt/ace/llm-wiki-archive/marine-engineering/raw/papers/`:

| File | Size |
|---|---|
| NOV_Crown_Mounted_Compensation_2026.pdf | 1.0 MB |
| NOV_Riser_Tensioners_2026.pdf | 2.8 MB |
| NOV_Active_Heave_Drilling_Drawworks_AHD_2026.pdf | 2.0 MB |
| NOV_Active_Heave_Dual_Drilling_Drawworks_AHDD_2026.pdf | 0.5 MB |
| NOV_Offshore_Product_Reference_Guide_2026.pdf | 50 MB |

All downloaded from `assets.nov.com` (Bynder DAM URLs — those paths can rotate; the local archive is the durable artifact).

## Operational notes captured (folded into memory)

- The existing memory `project_llm_wiki_external_post_ingest_workflow.md` was renamed/widened to `llm-wiki external-content ingest workflow` and now covers the vendor-product-family variant explicitly, including the off-repo archival rule, the no-`/mnt/ace`-paths-in-repo rule, and the Bynder-DAM-URL caveat.
- The user authorization rhythm worked cleanly: scoping question (AskUserQuestion) before deep work, commit authorization (AskUserQuestion) before each commit batch, push authorization on explicit request. No surprises, no `--no-verify`, no destructive operations.

## What's next

Nothing pending. The three commits are live on `vamseeachanta/llm-wiki:main`. If new URLs surface for ingest, re-enter via the same 8-step workflow.
