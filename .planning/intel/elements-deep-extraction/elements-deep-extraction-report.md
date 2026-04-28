# Elements deep extraction #2536 — first-pass report

Generated: 2026-04-28

## Scope executed

First-pass deep extraction was limited to the high-value/small Elements corpora agreed for `workspace-hub#2536`:

| Corpus | Raw path | Result |
|---|---|---|
| Suction pile sizing | `/mnt/ace/digitalmodel/references/suction-pile-sizing` | PDF text extracted; two workbooks inspected; source + concept pages created |
| Riser toolbox | `/mnt/ace/digitalmodel/references/riser-toolbox` | Two smaller OrcaFlex statistics workbooks inspected; source + concept pages created |
| QGIS | `/mnt/ace/digitalmodel/tools/qgis` | Projection, DEM grid stats, DXF entity count extracted; source + workflow pages created |

## Raw-data policy

No raw bulk files were copied into git/wiki raw folders. Wiki pages link to `/mnt/ace` source paths and include extracted metadata/method summaries only.

## Extraction artifacts

- `extracted-text/suction-pile-sizing-program.txt` — 251 lines from PDF via `pdftotext -layout`.
- `workbook-summary.json` and `workbooks/*.json` — workbook structures, labels, formula samples.
- `gis/dem-stats.json` — DEM header and value statistics.
- `gis/dxf-entity-summary.json` — DXF entity summary.
- `gis/qgis-files.json` — compact QGIS corpus inventory.

## Wiki pages created

| Domain | Page |
|---|---|
| marine-engineering | `wiki/sources/elements-suction-pile-sizing-deep-extraction.md` |
| marine-engineering | `wiki/concepts/suction-pile-preliminary-sizing-api-py-tz.md` |
| marine-engineering | `wiki/sources/elements-riser-toolbox-deep-extraction.md` |
| marine-engineering | `wiki/concepts/riser-extreme-statistics-orcaflex-workbooks.md` |
| engineering | `wiki/sources/elements-qgis-flowline-dem-deep-extraction.md` |
| engineering | `wiki/workflows/qgis-flowline-dem-preprocessing.md` |

## Validation

| Check | Result |
|---|---|
| `uv run scripts/knowledge/llm_wiki.py status --wiki marine-engineering` | PASS; status report written |
| `uv run scripts/knowledge/llm_wiki.py lint --wiki marine-engineering` | PASS exit code; warnings are pre-existing large-corpus frontmatter/orphan warnings |
| `uv run scripts/knowledge/llm_wiki.py status --wiki engineering` | PASS; status report written |
| `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` | PASS exit code; new QGIS source orphan resolved by index link; remaining warnings are pre-existing source frontmatter warnings |
| `uv run pytest scripts/knowledge/tests/test_llm_wiki.py` | PASS — 41 tests passed |

Validation logs are under `.planning/intel/elements-deep-extraction/validation/`.

## Deferred

- Large Riser Toolbox workbooks were not fully expanded into wiki text.
- Woodfibre/Doris large corpora remain metadata-only from `#2535` until separately scoped.
- No source/staging cleanup was performed; `workspace-hub#2534` remains retention-gated.
