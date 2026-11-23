import sqlite3
from pathlib import Path

import pytest

from adapters.base import AdapterError, tokenize
from adapters.jsonl import JsonlAdapter
from adapters.sqlite_fts import SqliteFtsAdapter
from adapters.tsv import TsvAdapter
from adapters.yaml_catalog import YamlCatalogAdapter
from registry import load_registry


def _index(registry_path, index_id):
    return load_registry(registry_path).get(index_id)


def test_sqlite_fts_adapter_bm25_rank(fixture_registry):
    adapter = SqliteFtsAdapter(_index(fixture_registry, "fixture_sqlite"))

    rows = adapter.search(tokenize("mooring"), limit=5)

    assert len(rows) >= 2
    assert rows[0].rank_basis == "fts_bm25"
    assert rows[0].raw_path.endswith("mooring-fatigue.pdf")


def test_sqlite_fts_multi_token_or_semantics(fixture_registry):
    adapter = SqliteFtsAdapter(_index(fixture_registry, "fixture_sqlite"))

    paths = [row.raw_path for row in adapter.search(tokenize("mooring fatigue"), limit=10)]

    assert any(path.endswith("mooring-only.pdf") for path in paths)
    assert any(path.endswith("fatigue-only.pdf") for path in paths)


def test_sqlite_fts_query_token_quoting(fixture_registry):
    adapter = SqliteFtsAdapter(_index(fixture_registry, "fixture_sqlite"))

    rows = adapter.search(tokenize('mooring" OR x near('), limit=5)

    assert rows


def test_sqlite_fts_readonly(fixture_registry):
    index = _index(fixture_registry, "fixture_sqlite")
    adapter = SqliteFtsAdapter(index)

    adapter.search(tokenize("mooring"), limit=1)

    with pytest.raises(sqlite3.OperationalError):
        sqlite3.connect(f"file:{index.path}?mode=ro", uri=True).execute(
            "CREATE TABLE should_fail(x)"
        )


def test_jsonl_adapter_streaming_topk(fixture_registry):
    adapter = JsonlAdapter(_index(fixture_registry, "fixture_jsonl"))

    rows = adapter.search(tokenize("riser"), limit=3)

    assert len(rows) == 3
    assert rows[0].raw_path.endswith("riser-design.pdf")
    assert all(row.rank_basis == "token_match" for row in rows)


def test_jsonl_adapter_skips_malformed_line(fixture_registry):
    adapter = JsonlAdapter(_index(fixture_registry, "fixture_jsonl"))

    rows = adapter.search(tokenize("malformed-survivor"), limit=5)

    assert len(rows) == 1
    assert rows[0].meta["malformed_lines"] == 1


def test_tsv_adapter_columns(fixture_registry):
    adapter = TsvAdapter(_index(fixture_registry, "fixture_tsv"))

    rows = adapter.search(tokenize("readable mooring"), limit=5)

    assert rows[0].raw_path.endswith("cad-mooring.dwg")
    assert rows[0].meta["format"] == "dwg"
    assert rows[0].meta["readability"] == "high"
    assert rows[0].meta["mtime"] == "2026-01-01"


def test_tsv_adapter_rejects_bad_header(fixture_registry, tmp_path):
    bad = tmp_path / "bad.tsv"
    bad.write_text("name_description\tformat\nmooring\tdwg\n")
    index = _index(fixture_registry, "fixture_tsv")
    index.path = bad

    with pytest.raises(AdapterError, match="missing required column"):
        TsvAdapter(index).search(tokenize("mooring"), limit=5)


def test_yaml_catalog_adapter(fixture_registry):
    adapter = YamlCatalogAdapter(_index(fixture_registry, "fixture_yaml"))

    rows = adapter.search(tokenize("installation guide"), limit=5)

    assert rows[0].raw_path == "/legacy/dde/literature/install-guide.pdf"
    assert rows[0].meta["title"] == "Installation Guide"
