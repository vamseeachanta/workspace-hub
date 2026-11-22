"""Execute the synthetic contract in the weekly-review query pack."""

import hashlib
from pathlib import Path

import pytest


DOC = Path("docs/document-intelligence/weekly-review-query-pack.md")
KEY = "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


@pytest.fixture
def example(tmp_path):
    repo = Path(__file__).resolve().parents[3]
    text = (repo / DOC).read_text(encoding="utf-8")
    blocks = text.split("```python\n")
    assert len(blocks) == 2, "The pack must contain exactly one executable example"
    code, closing, _ = blocks[1].partition("```")
    assert closing
    namespace = {"fixture_root": tmp_path, "lookup_script": repo / "scripts/knowledge/doc-key-lookup.py"}
    exec(compile(code, str(DOC), "exec"), namespace)
    return namespace


def test_documented_query_pack_executes(example):
    # Independent identities are specified in the document's answer contract.
    assert hashlib.sha256(b"abc").hexdigest() == KEY.removeprefix("sha256:")
    answer = example["answer"]
    assert answer["status"] == "answered"
    assert answer["lookup"]["query"] == KEY
    assert answer["lookup"]["lookup_type"] == "key"
    assert answer["lookup"]["index_records"] == [{
        "content_hash": KEY,
        "path": "synthetic/sources/alpha.txt",
        "source": "synthetic-alpha",
        "domain": "engineering",
        "status": "indexed",
    }]
    assert answer["lookup"]["wiki_pages"] == [{
        "domain": "engineering",
        "page": str(Path("knowledge/wikis/engineering/wiki/sources/alpha.md")),
        "title": "Synthetic alpha",
    }]
    assert answer["lookup"]["standards_ledger"] == []


def test_unanswered_query_is_explicit(example):
    answer = example["query_pack"]("absent-synthetic-key")
    assert answer["status"] == "unanswered"
    assert answer["lookup"] == {
        "query": "absent-synthetic-key", "lookup_type": "key",
        "index_records": [], "standards_ledger": [], "wiki_pages": [],
    }


def test_broken_source_mapping_is_detected(example):
    # Retain the matching wiki: nonempty output must not imply an answered query.
    index = example["fixture_root"] / "data/document-index/index.jsonl"
    index.write_text(index.read_text(encoding="utf-8").replace(KEY, "unrelated-key"), encoding="utf-8")
    answer = example["query_pack"](KEY)
    assert answer["status"] == "source-mapping-gap"
    assert answer["lookup"]["index_records"] == []
    assert answer["lookup"]["wiki_pages"] == [{
        "domain": "engineering",
        "page": str(Path("knowledge/wikis/engineering/wiki/sources/alpha.md")),
        "title": "Synthetic alpha",
    }]
