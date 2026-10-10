"""Tests for the client team-summary generator (workspace-hub#3967)."""

from __future__ import annotations

import copy
import json
import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from team_summary import build  # noqa: E402

FIXTURE = REPO_ROOT / "tools" / "team_summary" / "example" / "summary.yml"


@pytest.fixture()
def data() -> dict:
    return build.load(FIXTURE)


def test_example_fixture_is_valid(data):
    assert build.validate(data) == []


def test_more_than_three_priorities_is_rejected(data):
    bad = copy.deepcopy(data)
    bad["priorities"] = bad["priorities"] * 2
    assert any("priorities" in e for e in build.validate(bad))


def test_item_without_source_is_rejected(data):
    bad = copy.deepcopy(data)
    del bad["issues"][0]["source"]
    assert any("source" in e for e in build.validate(bad))


def test_unknown_issue_status_is_rejected(data):
    bad = copy.deepcopy(data)
    bad["issues"][0]["status"] = "maybe"
    assert any("status" in e for e in build.validate(bad))


def test_review_requires_doc_and_known_ask(data):
    missing_doc = build.load(FIXTURE)
    del missing_doc["priorities"][1]["review"]["doc"]
    assert any("review" in e and "doc" in e for e in build.validate(missing_doc))

    bad_ask = build.load(FIXTURE)
    bad_ask["issues"][1]["review"]["ask"] = "signature"
    assert any("review.ask" in e for e in build.validate(bad_ask))


def test_html_is_deterministic(data):
    assert build.render_html(data) == build.render_html(copy.deepcopy(data))


def test_html_has_fixed_sections_in_order(data):
    html = build.render_html(data)
    order = [build.SECTION_TITLES[k] for k in build.SECTION_ORDER]
    positions = [html.index(title) for title in order if title in html]
    assert positions == sorted(positions)
    assert build.SECTION_TITLES["learn_or_solve"] in html
    assert build.SECTION_TITLES["sources"] in html


def test_review_links_render_with_link_base(data):
    html = build.render_html(data)
    assert "Approval needed:" in html
    assert (
        '<a href="https://example.invalid/wiki/reports/screening-note/README.md">'
        "README.md</a>"
    ) in html
    assert (
        '<a href="https://example.invalid/wiki/docs/reviews/team-summary/rev-4-review.html">'
        "rev-4.html</a>"
    ) in html
    assert build.HTML_REVIEW_INSTRUCTION in html
    assert "Send the saved comments JSON to the project inbox." in html


def test_review_paths_render_as_plain_text_without_link_base(data):
    plain = copy.deepcopy(data)
    del plain["review"]["link_base"]
    html = build.render_html(plain)
    assert '<a href="https://example.invalid' not in html
    assert "reports/screening-note/README.md" in html
    assert "docs/reviews/team-summary/rev-4-review.html" in html


def test_review_section_is_omitted_without_review_items(data):
    plain = copy.deepcopy(data)
    for section in ("priorities", "issues", "blockers", "deliverables"):
        for item in plain.get(section) or []:
            item.pop("review", None)
    for items in (plain.get("areas") or {}).values():
        for item in items:
            item.pop("review", None)
    assert "Documents awaiting your input" not in build.render_html(plain)


def test_review_section_deduplicates_by_doc_and_ask(data):
    dup = copy.deepcopy(data)
    dup["issues"][0]["review"] = dict(dup["priorities"][1]["review"])
    html = build.render_html(dup)
    assert html.count("<td>Approval needed</td>") == 1


def test_every_source_is_listed(data):
    html = build.render_html(data)
    for source in build.collect_sources(data):
        assert build.escape(source) in html


def test_empty_area_is_omitted(data):
    trimmed = copy.deepcopy(data)
    trimmed["areas"] = {"technical": data["areas"]["technical"]}
    html = build.render_html(trimmed)
    assert build.AREA_TITLES["technical"] in html
    assert build.AREA_TITLES["marketing"] not in html


def test_text_is_escaped(data):
    risky = copy.deepcopy(data)
    risky["learn_or_solve"] = "<script>alert(1)</script>"
    html = build.render_html(risky)
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


@pytest.mark.skipif(build.find_browser() is None, reason="no headless Chrome/Edge on this host")
def test_pdf_renders(tmp_path, data):
    out = tmp_path / "team-summary.pdf"
    build.build(FIXTURE, out)
    assert out.read_bytes()[:5] == b"%PDF-"
    assert out.stat().st_size > 5_000


def test_due_may_be_tbd_but_not_free_text(data):
    ok = copy.deepcopy(data)
    ok["priorities"][0]["due"] = "TBD"
    assert build.validate(ok) == []
    bad = copy.deepcopy(data)
    bad["priorities"][0]["due"] = "soon"
    assert any("due" in e for e in build.validate(bad))


def test_missing_sources_lists_only_absent_wiki_paths(tmp_path, data):
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "README.md").write_text("x")
    (tmp_path / "reports" / "screening-note").mkdir()
    (tmp_path / "reports" / "screening-note" / "README.md").write_text("x")
    (tmp_path / "reports" / "screening-note" / "rev-4.html").write_text("<html></html>")
    withurl = copy.deepcopy(data)
    withurl["deliverables"][0]["source"] = "https://example.com/doc"
    missing = build.missing_sources(withurl, tmp_path)
    assert "reports/README.md" not in missing
    assert "https://example.com/doc" not in missing
    assert "projects/example/requests.md" in missing


def test_missing_sources_includes_absent_review_doc(tmp_path, data):
    for path in build.collect_sources(data):
        if "://" not in path:
            target = tmp_path / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("x")
    missing = build.missing_sources(data, tmp_path)
    assert "reports/screening-note/rev-4.html" in missing


def test_make_review_copies_creates_once_and_preserves_comments(tmp_path, data):
    source = tmp_path / "reports" / "screening-note" / "rev-4.html"
    source.parent.mkdir(parents=True)
    source.write_text("<html><body><p>Review me.</p></body></html>", encoding="utf-8")
    comments = tmp_path / "docs" / "reviews" / "team-summary" / "rev-4-review.json"
    comments.parent.mkdir(parents=True)
    comments.write_text(json.dumps({"comments": [{"comment": "keep"}]}), encoding="utf-8")

    made = build.make_review_copies(data, tmp_path)
    review_copy = tmp_path / "docs" / "reviews" / "team-summary" / "rev-4-review.html"
    assert made == [review_copy]
    first = review_copy.read_text(encoding="utf-8")
    assert "Review comments" in first
    assert json.loads(comments.read_text(encoding="utf-8"))["comments"][0]["comment"] == "keep"

    build.make_review_copies(data, tmp_path)
    assert review_copy.read_text(encoding="utf-8") == first


def test_make_review_copies_is_noop_without_html_review_docs(tmp_path, data):
    md_only = copy.deepcopy(data)
    md_only["review"].pop("copies_dir")
    md_only["issues"][1].pop("review")
    assert build.make_review_copies(md_only, tmp_path) == []
