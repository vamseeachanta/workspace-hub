"""Contract checks for the public, non-executing disposition record.

Expected prerequisites come from issue 3695 and issue 2547, read on
2026-10-22. Fold decisions are proposals, not accepted issue outcomes.
No engineering calculation is performed.
"""

from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/wiki-stub-disposition.html"


class ReportParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.records = {}
        self.ids = set()
        self.links = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, "duplicate anchor"
            self.ids.add(attrs["id"])
        if tag == "article":
            self.records[attrs["id"]] = attrs
        if tag == "a":
            self.links.append(attrs["href"])
        if tag == "script":
            self.scripts.append(attrs)


@pytest.fixture
def report():
    parser = ReportParser()
    parser.feed(REPORT.read_text(encoding="utf-8"))
    return parser


@pytest.mark.parametrize("key", ["archive-dependent-stub", "unrostered-stub"])
def test_each_stub_has_a_conditional_fold_decision(report, key):
    """Issue 3695 asks for one disposition per stub; deletion is not enacted."""
    row = report.records[key]
    assert row["data-decision"] == "fold"
    assert row["data-status"] == "proposed"
    assert row["data-execution"] == "NOT_EVALUATED"


@pytest.mark.parametrize("anchor", [
    "summary", "revision-history", "basis", "archive-dependent-stub",
    "unrostered-stub", "worked-example", "acceptance", "limitations",
])
def test_required_evidence_and_handoff_sections_exist(report, anchor):
    assert anchor in report.ids


def test_sources_and_local_links_resolve(report):
    for link in report.links:
        if link.startswith("#"):
            assert link[1:] in report.ids
        elif "/issues/" not in link:
            assert (REPORT.parent / link).is_file(), link
    for issue in (3695, 2547, 3657):
        assert any(link.endswith(f"/issues/{issue}") for link in report.links)


def test_report_is_non_executing(report):
    """A public report must not initiate private reads or repository mutations."""
    assert report.scripts == []
    assert len(report.records) == 2  # Issue 3695 defines exactly two stubs.


def test_report_keeps_unknown_evidence_and_retention_explicit():
    text = REPORT.read_text(encoding="utf-8")
    for requirement in (
        "identity distinction", "source revision", "SHA-256", "readback",
        "private destination", "roster", "NOT_EVALUATED", "No repository",
        "not current inventory", "not closed",
    ):
        assert requirement in text
    assert text.index('id="summary"') < text.index('id="revision-history"')
    assert text.index('id="revision-history"') < text.index('id="basis"')
