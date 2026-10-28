"""Independent literal inputs for the promotion frontmatter example.

Field meanings and baseline fields: durable-vs-transient-knowledge-boundary.md,
section 10.1. Titles, dates, artifact references, source identifiers and hex keys
below are synthetic fixture inputs, not claims about existing pages or artifacts.
The keys illustrate the baseline form; they are not verified content digests.
Traversal depth follows this file's tests/knowledge location. Subprocess success
uses the conventional zero exit status; the timeout is a test harness budget.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples/knowledge/promotion_frontmatter.py"
POLICY = ROOT / "docs/document-intelligence/durable-vs-transient-knowledge-boundary.md"

# These literals precede the implementation and are the independent example basis.
EXPECTED = (
    {
        "title": "Synthetic issue finding",
        "doc_key": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "sources": ["synthetic-source:reference-alpha"],
        "promoted_from": "issue:123",
        "last_updated": "2026-01-12",
    },
    {
        "title": "Synthetic handoff finding",
        "doc_key": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "sources": ["synthetic-source:reference-beta"],
        "promoted_from": "docs/handoffs/synthetic-handoff.md",
        "last_updated": "2026-02-16",
    },
    {
        "title": "Synthetic recurring finding",
        "doc_key": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        "sources": ["synthetic-source:reference-gamma"],
        "promoted_from": "reports/recurring/synthetic-review-2026-03-09.md",
        "last_updated": "2026-03-10",
    },
)


@pytest.fixture(scope="module")
def emitted(tmp_path_factory):
    """Execute outside the checkout with no repository imports or user site."""
    workdir = tmp_path_factory.mktemp("outside-checkout")
    assert not workdir.is_relative_to(ROOT)
    result = subprocess.run(
        [sys.executable, "-I", str(EXAMPLE)],
        cwd=workdir,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    assert result.stderr == ""
    return tuple(yaml.safe_load_all(result.stdout))


@pytest.mark.parametrize("expected", EXPECTED, ids=("issue", "handoff", "recurring-report"))
def test_emission_matches_literal_inputs_and_roundtrips(emitted, expected):
    actual, = (mapping for mapping in emitted if mapping["title"] == expected["title"])
    assert actual == expected
    assert yaml.safe_load(yaml.safe_dump(actual)) == expected


def test_emits_exactly_the_declared_examples(emitted):
    assert emitted == EXPECTED


@pytest.mark.parametrize("expected", EXPECTED, ids=("issue", "handoff", "recurring-report"))
def test_source_identity_lineage_and_update_date_are_distinct(emitted, expected):
    actual, = (mapping for mapping in emitted if mapping["title"] == expected["title"])
    assert actual["sources"] == expected["sources"]
    assert actual["promoted_from"] == expected["promoted_from"]
    assert actual["promoted_from"] not in actual["sources"]
    assert actual["last_updated"] == expected["last_updated"]
    assert isinstance(actual["last_updated"], str)
    assert date.fromisoformat(actual["last_updated"]).isoformat() == expected["last_updated"]
    assert "status" not in actual


def test_help_describes_scope_without_emitting_mappings(tmp_path):
    assert not tmp_path.is_relative_to(ROOT)
    result = subprocess.run(
        [sys.executable, "-I", str(EXAMPLE), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    help_text = " ".join(result.stdout.split())
    for explanation in (
        "section 10.1",
        "does not impose a wiki schema",
        "cannot establish that promotion or source qualification occurred",
        "processing-status enum",
        "different unresolved recommendation",
        "sources",
        "promoted_from",
        "last_updated",
    ):
        assert explanation in help_text
    assert result.stderr == ""
    assert "---" not in result.stdout


def test_example_matches_current_section_and_is_linked():
    section = POLICY.read_text(encoding="utf-8").split(
        "### 10.1 Templates and conventions", maxsplit=1
    )[1].split("### 10.2", maxsplit=1)[0]
    rows = {
        cells[0]: cells[1:]
        for line in section.splitlines()
        if line.startswith("| `")
        for cells in [[cell.strip() for cell in line.strip("|").split("|")]]
    }
    assert rows["`promoted_from`"][0].startswith("string (")
    assert "issue reference, handoff path, run-output reference" in rows["`promoted_from`"][0]
    assert rows["`sources`"][0] == "list of source identifiers"
    assert "non-identity" in rows["`sources`"][1]
    assert "`title`, `last_updated`, `doc_key`" in section
    assert "final binding lives in each wiki's `CLAUDE.md`" in section
    assert "(../../examples/knowledge/promotion_frontmatter.py)" in section
