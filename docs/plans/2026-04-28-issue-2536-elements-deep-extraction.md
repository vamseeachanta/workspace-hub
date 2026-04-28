# Plan — workspace-hub#2536 Elements Deep Extraction First Pass

## Status
Approved by user instruction in current Hermes session: "continue" after recommendation to execute #2536.

## Deliverable
A controlled first-pass deep extraction for high-value, small Elements-ingested corpora: suction pile sizing, riser toolbox, and QGIS.

## Scope
- Read `.planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv` and parent `/mnt/ace` source paths.
- Extract text/metadata from accessible high-priority PDFs/docs/spreadsheets without copying raw bulk data into git.
- Create source summaries and concept pages under `knowledge/wikis/marine-engineering/` and `knowledge/wikis/engineering/`.
- Preserve provenance links to `/mnt/ace` paths and #2535/#2536.
- Run focused wiki validation and llm-wiki tests.

## Boundaries
- No deletion or cleanup of `_from_elements/` or `/mnt/elements`; #2534 remains retention-gated.
- No raw bulk files copied into git/wiki raw folders.
- Do not process Woodfibre/Doris large corpora in this first pass except as future candidates.

## Validation
- Extracted artifact report exists under `.planning/intel/elements-deep-extraction/`.
- Wiki source/concept pages exist and link to source/catalog pages.
- `uv run pytest scripts/knowledge/tests/test_llm_wiki.py` passes.
- `llm_wiki.py status/lint` runs for touched domains.
