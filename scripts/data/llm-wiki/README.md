# llm-wiki scripts

Ingest, index, and search utilities for the local LLM wiki
(`data/llm-wiki/` or resolved via `resolve_wiki_path.py`).

## Scripts

- `ingest-orcina.py` — crawl Orcina webhelp (OrcaFlex / OrcaWave / OrcFxAPI)
  + papers, write product markdown and per-product `index.json`.
- `search-wiki.py` — build a combined `search-index.json` and run fast /
  deep TF-IDF search. Importable API: `search(query, deep=False, ...)`.
- `resolve_wiki_path.py` — portable resolver honouring
  `LLM_WIKI_DATA_DIR` -> `config/llm-wiki.yaml` -> `data/llm-wiki/` ->
  `knowledge/wikis/`. Ref: #2140.

## Tests

`tests/test_resolve_wiki_path.py` covers path resolution (#2140).
Fixture-backed ingest / search unit tests live in the same directory
per #2141.

## E2E smoke test

`tests/test_e2e_smoke.py` (added for #2480) is a nightly-cadence end-to-end
smoke test that exercises the full **raw-source -> wiki page -> combined
index -> search retrieval** contract against a minimal synthetic fixture.

**What it protects**

- Parser output shape (`ingest-orcina.py::html_to_markdown`).
- Product `index.json` structure consumed by `search-wiki.py`.
- `search-wiki.py --rebuild` regenerates the combined `search-index.json`.
- `search-wiki.py` retrieves a fixture page for a unique keyword
  (`ZZQQRRTEST1234`) in the top-3 results.
- MCP `wiki_search` retrieval once #2400 lands (capability-gated skip until
  then).
- Stage-break diagnostics: synthetic corruption at ingest / index stages
  fails loudly with a stage-named assertion message
  (`ingest stage broken: ...`, `index stage broken: ...`).

**Cadence**

Nightly CI only. Do not gate PRs on it — the test spawns `search-wiki.py`
as a subprocess and takes ~20s; per-PR coverage is handled by the #2141
unit tests.

**Regenerating the fixture**

If the ingest parser output format or the per-product `index.json` shape
changes, regenerate the golden expected markdown:

```
uv run python -c "
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location(
    'ingest_orcina', 'scripts/data/llm-wiki/ingest-orcina.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
src = pathlib.Path('scripts/data/llm-wiki/tests/fixtures/e2e/source.html').read_text()
title, md = m.html_to_markdown(src, 'file:///fixture/e2e/source.html')
pathlib.Path('scripts/data/llm-wiki/tests/fixtures/e2e/expected_topic.md').write_text(
    f'# {title}\n\n{md}\n')
"
```

Then rerun `uv run pytest scripts/data/llm-wiki/tests/test_e2e_smoke.py -v`
and commit the updated `expected_topic.md` alongside the parser change.
