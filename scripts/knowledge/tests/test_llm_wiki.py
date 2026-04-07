"""Tests for llm_wiki.py CLI."""

import os
import shutil
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


# Point REPO_ROOT and WIKIS_DIR at temp dirs for testing
REPO_ROOT = Path(os.environ.get("LLM_WIKI_TEST_ROOT", tempfile.mkdtemp()))
WIKIS_DIR = REPO_ROOT / "knowledge" / "wikis"


@pytest.fixture(autouse=True)
def fresh_wikis():
    """Ensure WIKIS_DIR is clean for each test."""
    if WIKIS_DIR.exists():
        shutil.rmtree(WIKIS_DIR)
    WIKIS_DIR.mkdir(parents=True, exist_ok=True)
    yield
    # cleanup
    if WIKIS_DIR.exists():
        shutil.rmtree(WIKIS_DIR)


@pytest.fixture(autouse=True)
def patch_repos():
    """Patch module-level constants to use test paths."""
    import scripts.knowledge.llm_wiki as m
    with patch.object(m, "REPO_ROOT", REPO_ROOT):
        with patch.object(m, "WIKIS_DIR", WIKIS_DIR):
            yield


def run_cmd(*args):
    """Helper to run the CLI with given args."""
    from scripts.knowledge.llm_wiki import main
    sys.argv = ["llm-wiki"] + list(args)
    return main()


# ────────────────────────────
# Init tests
# ────────────────────────────


class TestInit:

    def test_init_creates_structure(self):
        assert run_cmd("init", "test-domain") == 0
        wiki_root = WIKIS_DIR / "test-domain"
        assert wiki_root.exists()
        assert wiki_root.is_dir()

    def test_init_creates_raw_dirs(self):
        run_cmd("init", "test-domain")
        wiki_root = WIKIS_DIR / "test-domain"
        assert (wiki_root / "raw" / "papers").exists()
        assert (wiki_root / "raw" / "standards").exists()
        assert (wiki_root / "raw" / "articles").exists()
        assert (wiki_root / "raw" / "assets").exists()

    def test_init_creates_wiki_dirs(self):
        run_cmd("init", "test-domain")
        wiki_root = WIKIS_DIR / "test-domain"
        assert (wiki_root / "wiki" / "entities").exists()
        assert (wiki_root / "wiki" / "concepts").exists()
        assert (wiki_root / "wiki" / "sources").exists()
        assert (wiki_root / "wiki" / "comparisons").exists()
        assert (wiki_root / "wiki" / "visualizations").exists()

    def test_init_creates_schema(self):
        run_cmd("init", "test-domain")
        schema = WIKIS_DIR / "test-domain" / "CLAUDE.md"
        assert schema.exists()
        content = schema.read_text()
        assert "Wiki Schema: test-domain" in content
        assert "Directory Structure" in content
        assert "Ingest Workflow" in content
        assert "Lint Workflow" in content

    def test_init_creates_index(self):
        run_cmd("init", "test-domain")
        index = WIKIS_DIR / "test-domain" / "wiki" / "index.md"
        assert index.exists()
        content = index.read_text()
        assert "Knowledge Index: test-domain" in content
        assert "page_count: 0" in content
        assert "source_count: 0" in content

    def test_init_creates_log(self):
        run_cmd("init", "test-domain")
        log = WIKIS_DIR / "test-domain" / "wiki" / "log.md"
        assert log.exists()
        content = log.read_text()
        assert "Wiki Log: test-domain" in content
        assert "Auto-generated" in content

    def test_init_creates_overview(self):
        run_cmd("init", "test-domain")
        overview = WIKIS_DIR / "test-domain" / "wiki" / "overview.md"
        assert overview.exists()
        content = overview.read_text()
        assert "Overview" in content
        assert "Auto-generated" in content

    def test_init_normalizes_domain_name(self):
        run_cmd("init", "Marine Engineering")
        assert (WIKIS_DIR / "marine-engineering").exists()
        assert not (WIKIS_DIR / "Marine Engineering").exists()

    def test_init_fails_if_exists(self):
        run_cmd("init", "test-domain")
        assert run_cmd("init", "test-domain") == 1

    def test_init_creates_gitkeep_markers(self):
        run_cmd("init", "test-domain")
        assert (WIKIS_DIR / "test-domain" / "raw" / ".gitkeep").exists()
        assert (WIKIS_DIR / "test-domain" / "wiki" / ".gitkeep").exists()


# ────────────────────────────
# Status tests
# ────────────────────────────


class TestStatus:

    def test_status_fails_if_not_found(self):
        assert run_cmd("status", "--wiki", "nonexistent") == 1

    def test_status_on_empty_wiki(self, capsys):
        run_cmd("init", "test-domain")
        assert run_cmd("status", "--wiki", "test-domain") == 0
        captured = capsys.readouterr()
        assert "Wiki Status: test-domain" in captured.out
        assert "0" in captured.out

    def test_status_reports_source_count(self, capsys):
        run_cmd("init", "test-domain")
        # Create a raw source file
        src = WIKIS_DIR / "test-domain" / "raw" / "papers" / "test.pdf"
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text("dummy")
        assert run_cmd("status", "--wiki", "test-domain") == 0
        captured = capsys.readouterr()
        assert "1" in captured.out  # at least 1 source

    def test_status_reports_page_count(self, capsys):
        run_cmd("init", "test-domain")
        # Create an entity page
        entity = WIKIS_DIR / "test-domain" / "wiki" / "entities" / "test-entity.md"
        entity.parent.mkdir(parents=True, exist_ok=True)
        entity.write_text("# Test Entity\nThis is a test entity.")
        assert run_cmd("status", "--wiki", "test-domain") == 0
        captured = capsys.readouterr()
        assert "entities" in captured.out


# ────────────────────────────
# Ingest tests
# ────────────────────────────


class TestIngest:

    def test_ingest_fails_if_wiki_not_found(self):
        # Create a dummy source
        src = REPO_ROOT / "test_source.pdf"
        src.write_text("dummy")
        assert run_cmd("ingest", str(src), "--wiki", "nonexistent") == 1

    def test_ingest_fails_if_source_not_found(self):
        run_cmd("init", "test-domain")
        assert run_cmd("ingest", "/nonexistent/file.pdf", "--wiki", "test-domain") == 1

    def test_ingest_copies_source(self):
        run_cmd("init", "test-domain")
        src = REPO_ROOT / "test_source.pdf"
        src.write_text("dummy source content")
        assert run_cmd("ingest", str(src), "--wiki", "test-domain") == 0
        target = WIKIS_DIR / "test-domain" / "raw" / "papers" / "test_source.pdf"
        assert target.exists()
        assert target.read_text() == "dummy source content"

    def test_ingest_provides_llm_instructions(self, capsys):
        run_cmd("init", "test-domain")
        src = REPO_ROOT / "test_api_doc.pdf"
        src.write_text("dummy")
        run_cmd("ingest", str(src), "--wiki", "test-domain")
        captured = capsys.readouterr()
        assert "Ingest Request" in captured.out
        assert "Instructions for the LLM" in captured.out
        assert "test_api_doc.pdf" in captured.out

    def test_ingest_skips_existing(self):
        run_cmd("init", "test-domain")
        src = REPO_ROOT / "dup_source.pdf"
        src.write_text("dummy")
        assert run_cmd("ingest", str(src), "--wiki", "test-domain") == 0
        # Second ingest without --force should fail
        assert run_cmd("ingest", str(src), "--wiki", "test-domain") == 1

    def test_ingest_force_overwrites(self):
        run_cmd("init", "test-domain")
        src = REPO_ROOT / "dup_source.pdf"
        src.write_text("original")
        run_cmd("ingest", str(src), "--wiki", "test-domain")
        src.write_text("updated")
        assert run_cmd("ingest", str(src), "--wiki", "test-domain", "--force") == 0
        target = WIKIS_DIR / "test-domain" / "raw" / "papers" / "dup_source.pdf"
        assert target.read_text() == "updated"


# ────────────────────────────
# Query tests
# ────────────────────────────


class TestQuery:

    def test_query_fails_if_wiki_not_found(self):
        assert run_cmd("query", "what is viv", "--wiki", "nonexistent") == 1

    def test_query_empty_wiki_returns_no_results(self, capsys):
        run_cmd("init", "test-domain")
        assert run_cmd("query", "what is viv", "--wiki", "test-domain") == 0
        captured = capsys.readouterr()
        assert "Found 0 matching pages" in captured.out

    def test_query_finds_matching_page(self, capsys):
        run_cmd("init", "test-domain")
        # Create a concept page
        page = WIKIS_DIR / "test-domain" / "wiki" / "concepts" / "viv.md"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("# Vortex-Induced Vibration\n\n"
                        "VIV occurs when fluid flows past a bluff body, "
                        "creating alternating vortices that cause oscillating forces.\n")
        assert run_cmd("query", "vortex induced vibration", "--wiki", "test-domain") == 0
        captured = capsys.readouterr()
        assert "Found 1 matching pages" in captured.out
        assert "viv.md" in captured.out

    def test_query_ranks_by_relevance(self, capsys):
        run_cmd("init", "test-domain")
        # Two pages with different keyword match counts
        p1 = WIKIS_DIR / "test-domain" / "wiki" / "concepts" / "viv.md"
        p1.parent.mkdir(parents=True, exist_ok=True)
        p1.write_text("# VIV\n\nVortex induced vibration causes fatigue in risers. "
                      "VIV analysis requires understanding of vortex shedding.\n")
        p2 = WIKIS_DIR / "test-domain" / "wiki" / "entities" / "riser.md"
        p2.write_text("# Riser\n\nA riser connects the wellhead to the platform.\n")
        capsys.readouterr()  # clear
        assert run_cmd("query", "vortex induced vibration fatigue", "--wiki", "test-domain") == 0
        captured = capsys.readouterr()
        assert "viv.md" in captured.out
        assert "riser.md" not in captured.out  # riser doesn't match the query keywords


# ────────────────────────────
# Lint tests
# ────────────────────────────


class TestLint:

    def test_lint_fails_if_wiki_not_found(self):
        assert run_cmd("lint", "--wiki", "nonexistent") == 1

    def test_lint_passes_empty_wiki(self, capsys):
        run_cmd("init", "test-domain")
        assert run_cmd("lint", "--wiki", "test-domain") == 0
        captured = capsys.readouterr()
        assert "Wiki Lint: test-domain" in captured.out
        # Fresh wiki has index.md and log.md — may have low-density warning but no criticals
        assert "CRITICAL" not in captured.out

    def test_lint_detects_empty_pages(self, capsys):
        run_cmd("init", "test-domain")
        # Create placeholder-only page
        page = WIKIS_DIR / "test-domain" / "wiki" / "entities" / "placeholder-entity.md"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("# Placeholder Entity\n\n> Auto-generated by llm-wiki init\n")
        assert run_cmd("lint", "--wiki", "test-domain") == 1
        captured = capsys.readouterr()
        assert "EMPTY" in captured.out or "empty" in captured.out

    def test_lint_detects_orphan_pages(self, capsys):
        run_cmd("init", "test-domain")
        capsys.readouterr()  # clear init output
        # Create page with no inbound links (index.md doesn't link to it)
        page = WIKIS_DIR / "test-domain" / "wiki" / "entities" / "orphan-entity.md"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("# Orphan Entity\n\nThis page has no links pointing to it from anywhere.\n"
                        "It mentions [another thing](../concepts/concept.md).\n")
        assert run_cmd("lint", "--wiki", "test-domain") == 1
        captured = capsys.readouterr()
        assert "orphan" in captured.out.lower()
        assert "orphan-entity.md" in captured.out

    def test_lint_passes_well_linked_wiki(self, capsys):
        run_cmd("init", "test-domain")
        # Create a page that IS linked from index.md
        index = WIKIS_DIR / "test-domain" / "wiki" / "index.md"
        page = WIKIS_DIR / "test-domain" / "wiki" / "entities" / "test-entity.md"
        page.parent.mkdir(parents=True, exist_ok=True)

        page_text = "# Test Entity\n\nThis is a well-defined entity with content.\n"
        page.write_text(page_text)
        # Update index to link to the page
        idx_text = index.read_text()
        idx_text += "\n## Entities\n\n| Page | Summary |\n|------|--------|\n"
        idx_text += f"| [Test Entity](entities/test-entity.md) | A test entity |\n"
        index.write_text(idx_text)

        result = run_cmd("lint", "--wiki", "test-domain")
        # Should pass (no orphan, not empty since it has content, index exists)
        captured = capsys.readouterr()
        assert "Wiki Lint: test-domain" in captured.out

    def test_lint_detects_low_link_density(self, capsys):
        run_cmd("init", "test-domain")
        # Create multiple pages with no cross-references
        for i in range(5):
            page = WIKIS_DIR / "test-domain" / "wiki" / "concepts" / f"concept{i}.md"
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(f"""# Concept {i}

> Created by llm-wiki init

This is a concept page with real content about topic {i}.
It discusses various engineering principles and methodologies.
No cross-references anywhere in this page.
""")
        assert run_cmd("lint", "--wiki", "test-domain") == 1
        captured = capsys.readouterr()
        assert "cross" in captured.out.lower() or "density" in captured.out.lower()


# ────────────────────────────
# get_wiki_snapshot tests
# ────────────────────────────


class TestWikiSnapshot:

    def test_snapshot_empty_wiki(self):
        run_cmd("init", "test-domain")
        from scripts.knowledge.llm_wiki import get_wiki_snapshot
        result = get_wiki_snapshot(WIKIS_DIR / "test-domain")
        # Fresh wiki should only report index.md — no entity/concept/source pages yet
        assert "index.md" in result
        assert "entities" not in result

    def test_snapshot_with_pages(self):
        run_cmd("init", "test-domain")
        page = WIKIS_DIR / "test-domain" / "wiki" / "entities" / "calm-buoy.md"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("# CALM Buoy\n")
        from scripts.knowledge.llm_wiki import get_wiki_snapshot
        result = get_wiki_snapshot(WIKIS_DIR / "test-domain")
        assert "calm-buoy" in result
