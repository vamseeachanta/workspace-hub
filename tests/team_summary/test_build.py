"""Tests for the client team-summary generator (workspace-hub#3967)."""

from __future__ import annotations

import copy
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


def test_html_is_deterministic(data):
    assert build.render_html(data) == build.render_html(copy.deepcopy(data))


def test_html_has_fixed_sections_in_order(data):
    html = build.render_html(data)
    order = [build.SECTION_TITLES[k] for k in build.SECTION_ORDER]
    positions = [html.index(title) for title in order if title in html]
    assert positions == sorted(positions)
    assert build.SECTION_TITLES["learn_or_solve"] in html
    assert build.SECTION_TITLES["sources"] in html


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
