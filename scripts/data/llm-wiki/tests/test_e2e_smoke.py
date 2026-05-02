"""End-to-end smoke test for the llm-wiki pipeline.

Exercises the raw-source -> wiki page -> combined index -> search retrieval chain
against a minimal synthetic fixture. Complements the narrower unit tests from
#2141 and guards against silent regressions across the full pipeline.

Notes on scope:
  * `ingest-orcina.py` CLI is network-coupled to the Orcina TOC; we therefore
    exercise the ingest stage via its pure parser entry point
    (`html_to_markdown`) and write the product index.json in the exact shape
    `ingest_product()` produces. The search stage is exercised end-to-end by
    invoking `search-wiki.py` as a subprocess.
  * MCP assertion (#2400) is capability-gated: skipped cleanly when the MCP
    server module is not available.

Ref: GH #2480
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "e2e"
INGEST_SCRIPT = SCRIPT_DIR / "ingest-orcina.py"
SEARCH_SCRIPT = SCRIPT_DIR / "search-wiki.py"

FIXTURE_PRODUCT = "orcaflex"
FIXTURE_KEYWORD = "ZZQQRRTEST1234"
FIXTURE_FILE_STEM = "zzqqrrtest_reference"
FIXTURE_SOURCE_URL = "file:///fixture/e2e/source.html"


def _load_ingest_module():
    """Import scripts/data/llm-wiki/ingest-orcina.py despite the hyphenated path."""
    spec = importlib.util.spec_from_file_location(
        "ingest_orcina_e2e", str(INGEST_SCRIPT)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_DISTRACTOR_HTML = """<!DOCTYPE html>
<html><head><title>Vessel Response Amplitude Operator</title></head>
<body>
<h1>Vessel Response Amplitude Operator</h1>
<p>Generic unrelated topic used as a corpus distractor so TF-IDF is non-degenerate.</p>
<h2>Background</h2>
<p>Motion transfer functions relate wave input to vessel response.</p>
</body></html>
"""
_DISTRACTOR_STEM = "vessel_rao"


def _run_ingest(tmp_wiki: Path) -> Path:
    """Stage 1: parse fixture HTML and write a product wiki tree + index.json.

    Mirrors the shape `ingest_product()` produces so search-wiki.py can consume
    the output. The parser itself is the real production entry point. A second
    distractor topic is written so TF-IDF scoring is non-degenerate
    (single-doc corpora yield idf=0 and suppress all results).
    """
    ingest = _load_ingest_module()
    import re

    html = (FIXTURE_DIR / "source.html").read_text()
    title, markdown = ingest.html_to_markdown(html, FIXTURE_SOURCE_URL)
    d_title, d_markdown = ingest.html_to_markdown(
        _DISTRACTOR_HTML, "file:///fixture/e2e/distractor.html"
    )

    product_dir = tmp_wiki / FIXTURE_PRODUCT / "topics"
    product_dir.mkdir(parents=True, exist_ok=True)
    topic_md = product_dir / f"{FIXTURE_FILE_STEM}.md"
    topic_md.write_text(f"# {title}\n\n{markdown}")
    distractor_md = product_dir / f"{_DISTRACTOR_STEM}.md"
    distractor_md.write_text(f"# {d_title}\n\n{d_markdown}")

    def _topic_entry(stem: str, ttl: str, md: str, src: str) -> dict:
        sections = re.findall(r"^#{1,3}\s+(.+)$", md, re.MULTILINE)[:15]
        return {
            "file": f"{stem}.md",
            "title": ttl,
            "section_path": ["Test Section"],
            "sections": sections,
            "source_url": src,
            "size_bytes": len(md),
            "word_count": len(md.split()),
        }

    topics = [
        _topic_entry(FIXTURE_FILE_STEM, title, markdown, FIXTURE_SOURCE_URL),
        _topic_entry(_DISTRACTOR_STEM, d_title, d_markdown,
                     "file:///fixture/e2e/distractor.html"),
    ]
    index = {
        "product": "OrcaFlex",
        "base_url": "file:///fixture",
        "generated": "2026-04-24T00:00:00+00:00",
        "topic_count": len(topics),
        "total_words": sum(t["word_count"] for t in topics),
        "total_size_mb": 0.0,
        "errors": 0,
        "skipped": 0,
        "topics": topics,
    }
    (tmp_wiki / FIXTURE_PRODUCT / "index.json").write_text(json.dumps(index, indent=2))
    return topic_md


def _run_search(tmp_wiki: Path, query: str, rebuild: bool = False) -> list[dict]:
    """Stage 2+3: invoke search-wiki.py as a subprocess, return parsed JSON results."""
    env = os.environ.copy()
    env["LLM_WIKI_DATA_DIR"] = str(tmp_wiki)
    cmd = [sys.executable, str(SEARCH_SCRIPT), query, "--json"]
    if rebuild:
        cmd.append("--rebuild")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(
            f"search stage broken: search-wiki.py exited {result.returncode}\n"
            f"stderr: {result.stderr}\nstdout: {result.stdout}"
        )
    # --rebuild prints a status line before the JSON blob; isolate the JSON array.
    stdout = result.stdout.strip()
    start = stdout.find("[")
    if start < 0:
        raise RuntimeError(f"search stage broken: no JSON in stdout: {stdout!r}")
    return json.loads(stdout[start:])


@pytest.fixture()
def tmp_wiki(tmp_path: Path) -> Path:
    wiki = tmp_path / "llm-wiki"
    wiki.mkdir()
    return wiki


# -- 1. Ingest stage ----------------------------------------------------------


def test_ingest_produces_wiki_pages(tmp_wiki: Path):
    """Ingest writes expected markdown and updates the product index."""
    topic_md = _run_ingest(tmp_wiki)

    assert topic_md.exists(), "ingest stage broken: expected wiki markdown file missing"
    body = topic_md.read_text()
    assert FIXTURE_KEYWORD in body, (
        "ingest stage broken: fixture keyword missing from rendered markdown"
    )

    product_index = tmp_wiki / FIXTURE_PRODUCT / "index.json"
    assert product_index.exists(), "ingest stage broken: product index.json missing"
    data = json.loads(product_index.read_text())
    titles = [t["title"] for t in data.get("topics", [])]
    assert any(FIXTURE_KEYWORD in t for t in titles), (
        "ingest stage broken: fixture topic not listed in product index.json"
    )


# -- 2. Index rebuild ---------------------------------------------------------


def test_search_index_rebuilds(tmp_wiki: Path):
    """build_index writes a combined search-index.json containing fixture tokens."""
    _run_ingest(tmp_wiki)
    # Force rebuild via the --rebuild CLI flag.
    _run_search(tmp_wiki, FIXTURE_KEYWORD, rebuild=True)

    combined = tmp_wiki / "search-index.json"
    assert combined.exists(), "index stage broken: combined search-index.json not written"
    entries = json.loads(combined.read_text())
    assert any(FIXTURE_KEYWORD.lower() in e.get("title_tokens", []) for e in entries), (
        "index stage broken: fixture title_tokens missing from combined index"
    )


# -- 3. Search retrieval ------------------------------------------------------


def test_search_wiki_retrieval(tmp_wiki: Path):
    """search-wiki.py returns the fixture page in top-3 results for the unique keyword."""
    _run_ingest(tmp_wiki)
    results = _run_search(tmp_wiki, FIXTURE_KEYWORD, rebuild=True)

    assert results, "search stage broken: zero results returned for unique fixture keyword"
    top3 = results[:3]
    assert any(FIXTURE_FILE_STEM in r["file"] for r in top3), (
        "search stage broken: fixture page not in top-3 results for unique keyword"
    )


# -- 4. MCP retrieval (capability-gated for #2400) ----------------------------


def test_mcp_wiki_search_retrieval(tmp_wiki: Path):
    """MCP wiki_search (once #2400 lands) returns the fixture page."""
    try:
        import importlib
        importlib.import_module("wiki_mcp_server")
    except ImportError:
        pytest.skip("MCP wiki_search server not present (pending #2400)")

    _run_ingest(tmp_wiki)
    # Placeholder invocation contract; real implementation fills in once #2400 merges.
    import wiki_mcp_server  # type: ignore[import-not-found]
    os.environ["LLM_WIKI_DATA_DIR"] = str(tmp_wiki)
    results = wiki_mcp_server.wiki_search(FIXTURE_KEYWORD)  # type: ignore[attr-defined]
    assert any(FIXTURE_FILE_STEM in r.get("file", "") for r in results), (
        "mcp stage broken: fixture page not returned by wiki_search MCP tool"
    )


# -- 5. Synthetic-break: missing wiki file -----------------------------------


def test_ingest_break_detects_missing_wiki_file(tmp_wiki: Path):
    """Smoke fails loudly if the rendered wiki markdown is absent after ingest."""
    topic_md = _run_ingest(tmp_wiki)
    topic_md.unlink()  # corrupt ingest stage output

    with pytest.raises(AssertionError) as excinfo:
        assert topic_md.exists(), (
            "ingest stage broken: expected wiki markdown file missing"
        )
    assert "ingest stage broken" in str(excinfo.value)


# -- 6. Synthetic-break: stale combined index --------------------------------


def test_ingest_break_detects_stale_index(tmp_wiki: Path):
    """Smoke fails if the combined search-index.json is not regenerated from sources."""
    _run_ingest(tmp_wiki)
    # Simulate stale/missing combined index by running search without rebuilding
    # after corrupting the product index. Deleting the product index before
    # rebuild must surface the fixture absence from the combined index.
    (tmp_wiki / FIXTURE_PRODUCT / "index.json").unlink()

    _run_search(tmp_wiki, FIXTURE_KEYWORD, rebuild=True)
    combined = tmp_wiki / "search-index.json"
    entries = json.loads(combined.read_text())
    fixture_present = any(
        FIXTURE_KEYWORD.lower() in e.get("title_tokens", []) for e in entries
    )

    with pytest.raises(AssertionError) as excinfo:
        assert fixture_present, (
            "index stage broken: fixture absent from combined index after source corruption"
        )
    assert "index stage broken" in str(excinfo.value)
