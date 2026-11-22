"""Fixture-backed search contracts; ingestion and scoring remain unchanged.

Basis: ../search-wiki.py defines TITLE_W=3.0, SECTION_W=2.0, BODY_W=1.0.
Its search_fast uses indexed title/section counts; search_deep also counts the
whole markdown (including headings). Both use natural-log IDF and round scores
to three decimal places. Expected values below are hand calculations from the
literal corpus, never obtained from the search tokenizer or scoring helpers.

Corpus: alpha, beta, unrelated (same product), and paper: four documents.
The field-count oracle in test_fixture_term_counts lists (title, section, text)
occurrences independently. For unfiltered searches:
* lantern: df=1, IDF=ln(4); alpha fast=3*ln(4)=4.159,
  deep=(3+1)*ln(4)=5.545.
* quartz: df=3, IDF=ln(4/3); paper/alpha/beta fast weights are 9/6/3,
  giving 2.589/1.726/0.863; deep weights are 12/8/4,
  giving 3.452/2.301/1.151.
* saffron: df=2, IDF=ln(2); beta/alpha fast weights are 4/2,
  giving 2.773/1.386; deep weights are 6/3, giving 4.159/2.079.
* cobalt: absent from indexed fields; deep df=2, weights alpha/beta=3/1,
  giving 2.079/0.693.
Filtered deep quartz uses three readable documents and df=2:
alpha=8*ln(3/2)=3.244, beta=4*ln(3/2)=1.622. Fast IDF still uses all entries.
Limits zero, one and two are literal prefix lengths of these ordered matches.
The missing page adds one indexed entry (five total), but no readable markdown.
"""

import importlib.util
import json
import re
from pathlib import Path

import pytest


SCRIPT_DIR = Path(__file__).resolve().parent.parent
ALPHA = "orcaflex/topics/alpha.md"
BETA = "orcaflex/topics/beta.md"
UNRELATED = "orcaflex/topics/unrelated.md"
PAPER = "papers/note.md"
ALL_FILES = [ALPHA, BETA, UNRELATED, PAPER]

# Literal, synthetic inputs: product, filename, indexed title, sections, markdown.
DOCUMENTS = (
    ("orcaflex", "alpha.md", "Lantern Quartz Quartz", ["Saffron"],
     "# Lantern Quartz Quartz\n\n## Saffron\n\ncobalt cobalt cobalt.\n"),
    ("orcaflex", "beta.md", "Quartz Manual", ["Saffron Saffron"],
     "# Quartz Manual\n\n## Saffron Saffron\n\ncobalt.\n"),
    ("orcaflex", "unrelated.md", "Unrelated Guide", ["Background"],
     "# Unrelated Guide\n\n## Background\n\nPlain reference text.\n"),
    ("papers", "note.md", "Quartz Quartz Quartz Memo", ["Overview"],
     "# Quartz Quartz Quartz Memo\n\n## Overview\n\nNotes.\n"),
)


@pytest.fixture()
def search_module(tmp_path, monkeypatch):
    """Resolve only the temporary wiki before executing the hyphenated module.

    Combines the importlib pattern in test_e2e_smoke.py with the script-path
    import seam in test_resolve_wiki_path.py; monkeypatch restores both seams.
    """
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    monkeypatch.setenv("LLM_WIKI_DATA_DIR", str(wiki))
    monkeypatch.syspath_prepend(str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location(
        "search_wiki_modes", SCRIPT_DIR / "search-wiki.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.WIKI_DIR == wiki
    assert module.INDEX_PATH == wiki / "search-index.json"
    return module


@pytest.fixture()
def wiki(search_module):
    """Write all product metadata, markdown and generated indexes in tmp_path."""
    indexes = {}
    for product, filename, title, sections, markdown in DOCUMENTS:
        directory = search_module.WIKI_DIR / product
        if product != "papers":
            directory /= "topics"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / filename).write_text(markdown, encoding="utf-8")
        indexes.setdefault(product, []).append(
            {"file": filename, "title": title, "sections": sections}
        )
    for product, entries in indexes.items():
        key = "papers" if product == "papers" else "topics"
        (search_module.WIKI_DIR / product / "index.json").write_text(
            json.dumps({key: entries}), encoding="utf-8"
        )
    return search_module


def _files(results):
    return [result["file"] for result in results]


def test_fixture_term_counts():
    """Independent word counts establish the literal score basis above."""
    expected = {
        "alpha.md": {"lantern": (1, 0, 1), "quartz": (2, 0, 2),
                     "saffron": (0, 1, 1), "cobalt": (0, 0, 3)},
        "beta.md": {"lantern": (0, 0, 0), "quartz": (1, 0, 1),
                    "saffron": (0, 2, 2), "cobalt": (0, 0, 1)},
        "unrelated.md": {"lantern": (0, 0, 0), "quartz": (0, 0, 0),
                         "saffron": (0, 0, 0), "cobalt": (0, 0, 0)},
        "note.md": {"lantern": (0, 0, 0), "quartz": (3, 0, 3),
                    "saffron": (0, 0, 0), "cobalt": (0, 0, 0)},
    }
    for _, filename, title, sections, markdown in DOCUMENTS:
        fields = (title, " ".join(sections), markdown)
        for term, counts in expected[filename].items():
            actual = tuple(
                re.findall(r"\b[a-z]+\b", field.lower()).count(term)
                for field in fields
            )
            assert actual == counts, (filename, term)


@pytest.mark.parametrize("deep, score", [(False, 4.159), (True, 5.545)])
def test_title_only_term(wiki, deep, score):
    results = wiki.search("lantern", deep=deep)
    assert _files(results) == [ALPHA]
    assert [result["score"] for result in results] == [score]
    assert [result["matched"] for result in results] == [["lantern"]]


@pytest.mark.parametrize(
    "deep, scores", [(False, [2.773, 1.386]), (True, [4.159, 2.079])]
)
def test_section_only_term(wiki, deep, scores):
    results = wiki.search("saffron", deep=deep)
    assert _files(results) == [BETA, ALPHA]
    assert [result["score"] for result in results] == scores
    assert [result["matched"] for result in results] == [["saffron"], ["saffron"]]


def test_body_only_term_requires_deep_search(wiki):
    assert wiki.search("cobalt") == []
    results = wiki.search("cobalt", deep=True)
    assert _files(results) == [ALPHA, BETA]
    assert [result["score"] for result in results] == [2.079, 0.693]
    assert [result["matched"] for result in results] == [["cobalt"], ["cobalt"]]


@pytest.mark.parametrize(
    "deep, scores, filtered_scores",
    [(False, [2.589, 1.726, 0.863], [1.726, 0.863]),
     (True, [3.452, 2.301, 1.151], [3.244, 1.622])],
)
def test_product_filter_and_limit(wiki, deep, scores, filtered_scores):
    results = wiki.search("quartz", deep=deep)
    assert _files(results) == [PAPER, ALPHA, BETA]
    assert [result["score"] for result in results] == scores
    filtered = wiki.search("quartz", deep=deep, product="orcaflex")
    assert _files(filtered) == [ALPHA, BETA]
    assert [result["product"] for result in filtered] == ["orcaflex", "orcaflex"]
    assert [result["score"] for result in filtered] == filtered_scores
    assert _files(wiki.search("quartz", deep=deep, limit=1)) == [PAPER]
    assert _files(wiki.search(
        "quartz", deep=deep, product="orcaflex", limit=1
    )) == [ALPHA]
    assert _files(wiki.search(
        "quartz", deep=deep, product="orcaflex", limit=2
    )) == [ALPHA, BETA]
    assert wiki.search("quartz", deep=deep, limit=0) == []
    assert wiki.search("quartz", deep=deep, product="orcawave") == []


@pytest.mark.parametrize("deep", [False, True])
@pytest.mark.parametrize("query", ["", " \t\n", "! ?"])
def test_empty_query(wiki, deep, query):
    """Empty, whitespace and punctuation inputs have no searchable terms."""
    assert wiki.search(query, deep=deep) == []


def test_missing_markdown(wiki):
    """An indexed but never written page remains fast-searchable, not deep."""
    index_path = wiki.WIKI_DIR / "orcaflex" / "index.json"
    index = json.loads(index_path.read_text())
    index["topics"].append(
        {"file": "missing.md", "title": "Missing Beacon", "sections": []}
    )
    index_path.write_text(json.dumps(index), encoding="utf-8")
    assert not (wiki.WIKI_DIR / "orcaflex" / "topics" / "missing.md").exists()
    wiki.build_index(force=True)
    assert _files(wiki.search("beacon")) == ["orcaflex/topics/missing.md"]
    assert wiki.search("beacon", deep=True) == []
    assert _files(wiki.search("lantern", deep=True)) == [ALPHA]


def test_missing_product_indexes(search_module):
    """An empty temporary wiki has no metadata, markdown or combined index."""
    assert list(search_module.WIKI_DIR.iterdir()) == []
    assert search_module.build_index(force=True) == []
    assert json.loads(search_module.INDEX_PATH.read_text()) == []
    assert search_module.search("lantern") == []
    assert search_module.search("lantern", deep=True) == []


def test_forced_index_creation_and_cache_reuse(wiki, monkeypatch):
    assert not wiki.INDEX_PATH.exists()
    assert _files(wiki.build_index(force=True)) == ALL_FILES
    assert _files(json.loads(wiki.INDEX_PATH.read_text())) == ALL_FILES
    # A forced build must ignore even a fresh but empty cache.
    wiki.INDEX_PATH.write_text("[]", encoding="utf-8")
    assert _files(wiki.build_index(force=True)) == ALL_FILES
    cached_bytes = wiki.INDEX_PATH.read_bytes()
    cached_mtime = wiki.INDEX_PATH.stat().st_mtime_ns

    def reject_source_reload(product):
        pytest.fail(f"Fresh cache unexpectedly reloaded product {product}")

    monkeypatch.setattr(wiki, "_load_topics", reject_source_reload)
    assert _files(wiki.build_index()) == ALL_FILES
    assert _files(wiki.search("lantern")) == [ALPHA]
    assert _files(wiki.search("lantern", deep=True)) == [ALPHA]
    assert wiki.INDEX_PATH.read_bytes() == cached_bytes
    assert wiki.INDEX_PATH.stat().st_mtime_ns == cached_mtime
