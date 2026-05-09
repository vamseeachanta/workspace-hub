# /mnt/ace Raw-Data Gap Analysis — llm-wiki Domain Coverage

**Generated:** 2026-05-08
**Scope:** Top-level dirs of `/mnt/ace` NOT yet covered by the 8 prior ingest buckets
**Method:** `du -sh`, `find -type f | wc -l`, extension histograms; subdir sampling for the largest trees
**Time spent:** ~10 wall minutes

## Executive Summary

The volume of uncovered raw data is dominated by four trees: **`docs/` (3.4 TB, not enumerated)**, **`digitalmodel/` (106 GB / 122k files, mostly outside the small subset already ingested)**, **`client_projects/` (250 GB / 65k files)**, and **`doris/` (38 GB / 73k files, partially ingested)**. The richest unmapped wiki content lives in `digitalmodel/docs/` — 86 topical subdirs that look like a hand-curated taxonomy already mapping nearly 1-to-1 onto **engineering**, **marine-engineering**, and **naval-architecture** wiki domains (mooring, riser_analysis, hydrodynamics, naval_architecture, openfoam, orcaflex, viv, wec, fatigue, geotechnical, etc.). `O&G-Standards/` (43 GB, 55k+ PDFs across ABS/API/ASME/ASTM/DNV/ISO/Norsok/etc.) is the single highest-leverage uncovered tree for **engineering-standards**, and `acma-codes/` (7.1 GB, ABS/AMSA/ColRegs/Jones-Act etc.) maps cleanly to **maritime-law** + **engineering-standards**. `2H/` (riser/wellhead client reports), `frontierdeepwater/`, `client_projects/energy_*`, and `rock-oil-field/`+`saipem/` (`.sim`/`.dat` OrcaFlex artifacts) are clear **marine-engineering** + **lng-projects** candidates. Out-of-scope: `aceengineer-admin/` (admin/HR), `Production/` (training media), `build/` (Rust/JS source), `kaggle-rogii-2026/` (active competition), `0_mrv/`, `umbilical/`, `scripts/`, `achantas-data/` (personal), `assets.json` (1.2 GB asset DB).

## Classification Table

| /mnt/ace path | est files | size | top extensions | suggested wiki | priority | rationale |
|---|---:|---:|---|---|---|---|
| `0_mrv` | 11 | 68K | md | no fit | low | tiny stub; mostly already governed elsewhere |
| `2H` | 32 | 42M | md, pdf, xlsx, pptx, docx | marine-engineering | **high** | 2H Offshore client reports — riser/wellhead/SCR/drilling-riser fatigue, SLOR design, mode normalization. Directly relevant to marine-engineering wiki; small size = fast win |
| `aceengineer-admin` | 15,587 | 8.6G | jpg, log, png, js, class, pdf | no fit | low | Tax, invoices, employees, USBank, Apex — administrative; out of scope for wiki |
| `aceengineercode` | 4,197 | 2.4G | yml, png, py, csv, md, xlsx | engineering | med | Internal AGENTS-OS scaffolding + codebase modules, specs, tests. Some `docs/` and `modules/` content may overlap engineering wiki; needs targeted subdir pass |
| `achantas-data` | 107 | 1.2M | md | no fit | low | Personal travel/data per memory note; out of scope |
| `acma-codes` | 4,897 | 7.1G | pdf, tif, gif, dll, fnt, db | maritime-law + engineering-standards | **high** | ABS Rules, AMSA, ColRegs, Jones Act, BSEE, Bureau Veritas, British Standards, CSA, etc. Split: maritime regulatory bodies → maritime-law; class society / structural codes → engineering-standards |
| `assethold` | 507 | 24M | md, xlsx, pdf | asset-management | med | Already partially covered (casa-grande). Remaining 504 md files likely property/asset records — natural extension of asset-management wiki |
| `build` | 33,964 | 4.0G | h, rs, js, json, md, s, c | no fit | low | `codex-desktop` Rust/JS build tree — toolchain artifacts, not content |
| `capytaine` | 325 | 4.2M | py, rst, f90, dat | engineering or marine-engineering | med | BEM hydrodynamics solver source. Best as a "tools/capytaine" page under marine-engineering or engineering hydrodynamics subpage (mirrors gmsh/HAMS pattern) |
| `client_projects` | 65,365 | 250G | jpg, pdf, png, php, class, java, dat, xml | marine-engineering + lng-projects + engineering | **high** | `energy_*` subdirs span drilling-riser, FDAS, integrity, metocean, mooring, pipeline-installation, BSEE, MRV, subseafirst, KBR. Numbered project dirs (0111-RII, 0127-Mooring, 0159-Anchor-FEA) look like high-value engineering case studies. Volume is large; subdir-level filter required |
| `digitalmodel` | 122,799 | 106G | sldprt, pdf, lod, dat, out, key, doc, mpd, xls, json | engineering + marine-engineering + naval-architecture | **highest** | `docs/` has 86 topical subdirs nearly 1-to-1 with wiki taxonomy: mooring, riser_analysis, naval_architecture, hydrodynamics, openfoam, orcaflex, orcawave, viv, wec, fatigue, geotechnical, fem, modal-analysis, plate-buckling, ship-design, submarine-cables, pipe, pipelines, risers, structural, welding, wind. SolidWorks (sldprt), LOD, OUT files imply CAD/FEA case data. Single largest mapping opportunity |
| `doris` | 72,968 | 38G | pdf, jpg, png, docx, dwf, doc, xls | engineering + lng-projects + marine-engineering | med | Already 3 buckets covered (62092_sesa, training, codes). Remaining: 61850_zama, 61863_lakach, admin, calculations, models, orcaflex, other_projects. Lakach and Zama are LNG/upstream projects → lng-projects; orcaflex/models/calculations → engineering & marine |
| `frontierdeepwater` | 6,281 | 6.5G | md, csv, pdf, py, gif, pptx, jpg, msg | marine-engineering + engineering | **high** | "Frontier Deepwater" — agent-os-style repo with Engineering/, REFERENCES/, modules/, HX-Venture, Mktg subdirs. PPTX + PDF + msg suggests client-deliverable archive. Direct deepwater marine content |
| `gmsh` | 3,984 | 144M | h, cpp, geo, c, hpp, py | engineering | low | gmsh meshing source tree. Best as a tool-page under engineering (companion to capytaine/HAMS) |
| `HAMS` | 1,086 | 56M | rao, txt, f90, sample, pnl | marine-engineering | med | RAO files, panel meshes, Fortran solver — diffraction/radiation hydrodynamics. Tool-page under marine-engineering |
| `kaggle-rogii-2026` | 2,327 | 1.3G | csv, png, pptx | no fit | low | Active competition (per memory). Out of scope until competition closes |
| `MoorDyn` | 1,193 | 28M | h, cpp, hpp, txt, md, py | marine-engineering | med | Open-source mooring dynamics solver — natural tool-page under marine-engineering/mooring |
| `MoorPy` | 93 | 1.4M | py, sample, dat, rst, yaml | marine-engineering | low | Quasi-static mooring tool. Pair with MoorDyn page; minimal incremental size |
| `OGManufacturing` | 22 | 58M | pdf, sh | engineering or no fit | low | 21 PDFs, no clear taxonomy from listing — sample needed before mapping |
| `O&G-Standards` | 57,509 | 43G | pdf, txt, doc, jpg, docx, wmf, xls | engineering-standards | **highest** | Hand-curated codes-and-standards library: ABS, API, ASCE, ASME, ASTM, AWS, BSI, DNV, HSE, IEC, ISO, MIL, NACE, NEMA, Norsok, OnePetro. 54,916 PDFs. Has `_inventory.db`, `_catalog.json`, OCR text — already indexed. Dispatch directly to engineering-standards |
| `openfast` | 1,288 | 253M | f90, rst, txt, png, md, py, pdf, vfproj | marine-engineering or engineering | med | NREL wind/floating turbine simulator — fits marine-engineering (offshore wind) and could anchor a wind subpage |
| `opm-common` | 3,274 | 113M | hpp, cpp, data, cmake, py, h, inc, ecl | engineering | low | Open Porous Media (reservoir simulation) — niche; tool-page under engineering reservoir |
| `Production` | 57,653 | 29G | jpg, mp3, png, md, mov, aae, webp, m4a | no fit (mostly) | low | Training media: EOR workshops, ESP pump curves, Halliburton presentations, IPL training. Audio/video heavy. INDEX.md + _knowledge_base may be salvageable but bulk is media |
| `rock-oil-field` | 1,034 | 2.5G | pdf, dat, sim, xlsx, docx, xlsm | marine-engineering | med | `.sim`/`.dat` = OrcaFlex artifacts. Likely subsea/riser project archive. Volume modest; high signal-to-noise |
| `saipem` | 555 | 2.4G | pdf, dat, sim, jpg, docx | marine-engineering + lng-projects | med | "yellowtail" subdir = ExxonMobil Guyana FPSO; `.sim` = OrcaFlex. Saipem is offshore/SURF — directly relevant |
| `scripts` | 4 | 64K | pyc, py | no fit | low | 4 files; admin scripts |
| `seanation` | 561 | 266M | sldprt, pdf, sldasm | engineering | low | SolidWorks parts + assemblies + PDFs. CT drilling project — niche; small. Could go into engineering CAD subpage |
| `umbilical` | 3 | 20K | md | marine-engineering | low | Stub, 3 md files. Possibly seed for an umbilical wiki page (digitalmodel/docs/umbilical exists — consolidate) |
| `WEC-Sim` | 1,085 | 625M | dat, m, png, tec, rst, cal, pdf, gdf | marine-engineering | med | Wave Energy Converter SIMulator (NREL/Sandia). Fits marine-engineering wave-energy subpage |
| `worldenergydata` | 345 | 9.6G | bin, csv, pdf, zip, txt | no fit (likely) | low | `.bin` heavy = vendor data dumps. Already governed by worldenergydata GTM project (memory note). Skip |
| `docs` | not enumerated | 3.4T | (sampled) | engineering + marine-engineering + lng-projects | **high** but deferred | Numbered project dirs (`0098 Mecor Pipeline`, `0113 Orc DR`, `0124 100ksi Pipe`, `0181 KBR Pipeline`, `0190 DISYS Drilling Riser`) plus `engineering-refs/{api,dnv,drilling,fea,general}/`, `literature/`, `simulation/`, `tecplot/`. Project dirs duplicate `client_projects/` numbering — investigate dedup before ingest. Per task brief, deferred |
| `data` | (skipped) | 772G | — | out of scope | — | Vendor data lake per task brief |
| `llm-wiki` | — | 28K | — | (staging) | — | Snapshot of `docs/` tree; not source data |
| `llm-wiki-archive` | — | 29M | — | marine-engineering (historical) | — | Has `marine-engineering/` subdir — historical wiki snapshot, useful for diffing prior coverage |
| `digitalmodel/llm-wiki` | — | — | — | (in-tree placeholder) | — | Per task brief: ignore |
| `assets.json` (+ backups) | 1 file | 1.2G + 705M | json | no fit | low | Likely assethold/property database export. Not wiki content |

## Highest-Leverage Targets (ranked)

1. **`O&G-Standards/`** → engineering-standards. 43 GB, 54,916 PDFs, already has `_inventory.db` + `_catalog.json` + OCR text. Lift cost is low because it's pre-indexed; coverage gain is enormous.
2. **`digitalmodel/docs/`** → engineering, marine-engineering, naval-architecture (split). 86 topical dirs with curated names — looks like the pre-existing taxonomy the wiki should mirror. Best ROI per hour.
3. **`acma-codes/`** → maritime-law + engineering-standards. 7.1 GB of regulatory + class-society material; clean split between law and standards.
4. **`2H/`** → marine-engineering. Only 42 MB but every dir is a deepwater riser/wellhead client report. High signal density.
5. **`client_projects/energy_*` + numbered dirs** → marine-engineering + lng-projects + engineering. 250 GB but subdir filtering can cherry-pick high-value `energy_drilling_riser`, `energy_metocean`, `energy_mrv`, `energy_pipeline_installation_mp`, `energy_subseafirst`.
6. **`frontierdeepwater/`** → marine-engineering. 6.5 GB; deepwater-focused client archive with structured Engineering/, REFERENCES/.
7. **`doris/{61850_zama,61863_lakach,orcaflex,models,calculations}`** → mix of lng-projects + marine-engineering. Already 3 buckets ingested, finish the tree.
8. **Hydrodynamic/CFD tool cluster** (`capytaine`, `gmsh`, `HAMS`, `MoorDyn`, `MoorPy`, `openfast`, `WEC-Sim`, `opm-common`) → tool-pages under engineering/marine-engineering. Each is small (≤625 MB). Bundle as a single "open-source-solvers" subpage rollup for fast coverage.

## Surprises and Out-of-Scope Notes

- `digitalmodel/docs/` has **86 curated topical subdirs** — far richer than the prior 3 ingested digitalmodel buckets. Major gap.
- `client_projects/` and `docs/` numbered dirs **overlap by project number** (`0111-RII`, `0113`, `0118`, etc.) — likely the same projects under different roots. **Dedup or canonicalize before ingest** to avoid double-counting.
- `O&G-Standards/` is **already indexed** (`_inventory.db`, `_catalog.json`, OCR text under `_ocr_text`). Wiki ingest should consume the existing index, not re-scan PDFs.
- `Production/` is mostly **multimedia training material** (mp3, mov, m4a, webp) — wiki-incompatible without transcription.
- `build/codex-desktop/` is the **codex-desktop build tree** per memory note — definitely not content.
- `assets.json` (1.2 GB single JSON file + backups) is genuinely surprising; likely an asset/property DB export — confirm with assethold owner before considering for asset-management wiki.
- `aceengineercode/` and `frontierdeepwater/` both contain `AGENT_OS_COMMANDS.md`, `CLAUDE.md`, `slash_commands.py` — they are **agent-os scaffolded repos**, not pure content; subdir-level filter required.
- `seanation/` has **438 SolidWorks parts** — CAD-heavy, low-text content; consider whether the wiki should ingest CAD index manifests rather than the binaries themselves.
