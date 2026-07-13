---
name: reference-vessel-fleet-data-locations
description: "Where drilling-rig/vessel particulars live in the repo ecosystem and how to fill gaps (spec PDFs, myshiptracking)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7619de1a-15ec-4e54-a4fc-1bece965f3e0
---

Vessel/rig particulars live in `worldenergydata/packages/worldenergydata-vessel_fleet/src/worldenergydata/vessel_fleet/`:
- `_data/curated/drilling_rigs.csv` — merged rig table (BSEE WAR + contractor fleet pages). Moonpool/draft columns exist but are largely UNPOPULATED; LOA/beam often hull-library estimates (`DIMENSION_CONFIDENCE=estimated`).
- `_data/raw/spec_details/*.parquet` — per-contractor scrape (Noble, Seadrill) with `DATA_SOURCE_URL` pointing at official rig-summary PDFs — the authoritative dimension source.
- Schema is ready for moonpool: `models/drilling_rig.py` (`moonpool_length_m/width_m/diameter_m`), `parsers/xls.py` parses "L x W" compounds.

**Noble fleet COMPLETE (31/31 rigs)** 2026-07-12: PR #989 (96K class, MERGED) + PR #990 (remaining 25 — P10000/Samsung-12000/Globetrotter drillships, DSS21/Victory/ExD/CS60E/Bingo semis, CJ70/CJ50 jackups). Parser `parsers/rig_summary.py` has TWO layout profiles (Noble "Rig Summary" colon-style + ex-Diamond "specification sheet" metric-in-parens); ingest `scripts/vessel_fleet/ingest_noble_spec_pdfs.py` (`--reparse` must use pdftotext -layout, the YAML SSOT extractor — pdfplumber gives false drift). PDFs + `extracted_specs.yaml` under `_data/raw/spec_pdfs/noble/`.

**Program epic wed #991** (owner direction 2026-07-12): spec DB for ALL leading contractors + all rig classes incl. onshore, → rig-selection insights. Children: #992 Transocean ✅ MERGED (PR #999, 27 rigs), #993 Valaris (**PR #1000** — 45 rigs incl. 31 jackups w/ LEG_LENGTH/CANTILEVER; fourth parser profile: column-aware sidebar matching), #994 Seadrill, #995 Borr/Shelf/ADES jackups (reuse Valaris jackup pattern), #996 Stena/Odfjell/client-d/COSL/Vantage, #997 onshore, #998 analytics. Spec URL patterns: Transocean `deepwater.com/documents/RigSpecs/<Rig%20Name>.pdf`; Valaris `valaris.com/files/doc_rigspecs/rigspecs2022/VALARIS-<slug>.pdf` (HTML pages 403 curl — use WebFetch/Chrome-UA; PDFs fetch fine). Generalized script: `ingest_contractor_spec_pdfs.py --contractor <name>`. wed #988 (myshiptracking) still open.

Hull identities (verified 2026-07-12): NOBLE VALIANT = ex MAERSK VALIANT (Samsung 96K, SHI 2013); **Noble Faye Kozack = ex PACIFIC KHAMSIN (IMO 9623324)**; **Noble Stanley Lafosse = ex PACIFIC SHARAV (IMO 9623336)** — NSL has a 115 ft × 41 ft moonpool vs 84 ft × 41 ft on the other five; never assume class-identical moonpools. Former names appear as separate curated rows (some with "(FKA …)" suffixes).

Related: [[project_subsea_intervention_database_epic]]
