"""Tests for the #3298 session-review renderer + index + manifest."""
import json
import sys
from pathlib import Path

SCRIPTS_WORKFLOW = Path(__file__).resolve().parents[2] / "scripts" / "workflow"
sys.path.insert(0, str(SCRIPTS_WORKFLOW))

import build_session_review as bsr  # noqa: E402
import session_review_sanitize as sani  # noqa: E402

PATTERNS = [("Synthco Field", False)]

PAYLOAD = {
    "slug": "demo",
    "date": "2026-06-28",
    "title": "Demo session",
    "lane": "claude",
    "summary": "Did stuff.",
    "kpis": [{"n": 3, "l": "PRs merged"}],
    "prs": [{"num": 3273, "what": "thing", "status": "merged"}],
    "issues": [{"num": 3298, "state": "filed", "note": "feature"}],
    "decisions": ["chose option 1"],
    "artifacts": ["a file"],
    "next_steps": ["do the next thing"],
}


def test_session_html_has_sections_and_links():
    html = bsr.render_session_html(PAYLOAD)
    assert "Demo session" in html
    assert f"{bsr.REPO}/pull/3273" in html      # PR linked
    assert f"{bsr.REPO}/issues/3298" in html    # issue linked
    for label in ("At a glance", "Pull requests", "Issues", "Decisions",
                  "Artifacts", "Next steps"):
        assert label in html


def test_session_html_is_self_contained():
    html = bsr.render_session_html(PAYLOAD)
    # no external stylesheet or script references — fully inline
    assert "<link" not in html
    assert "<script" not in html
    assert "src=" not in html
    assert "<style>" in html


def test_build_writes_page_manifest_and_index(tmp_path):
    entry = bsr.build(PAYLOAD, tmp_path, PATTERNS, public=True)
    page = tmp_path / "2026-06-28-demo.html"
    assert page.exists()
    assert entry["file"] == "2026-06-28-demo.html"
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest[0]["slug"] == "demo"
    assert (tmp_path / "index.html").exists()
    assert "Session Reviews" in (tmp_path / "index.html").read_text()


def test_manifest_newest_first_and_replace_by_slug(tmp_path):
    bsr.build({**PAYLOAD, "slug": "older", "date": "2026-06-01"}, tmp_path, PATTERNS)
    bsr.build({**PAYLOAD, "slug": "newer", "date": "2026-06-28"}, tmp_path, PATTERNS)
    bsr.build({**PAYLOAD, "slug": "newer", "date": "2026-06-28", "title": "Newer v2"},
              tmp_path, PATTERNS)  # replace, not duplicate
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert [e["slug"] for e in manifest] == ["newer", "older"]  # newest first
    assert sum(e["slug"] == "newer" for e in manifest) == 1     # replaced
    assert manifest[0]["title"] == "Newer v2"


def test_index_links_to_each_session_file(tmp_path):
    bsr.build({**PAYLOAD, "slug": "s1", "date": "2026-06-28"}, tmp_path, PATTERNS)
    idx = (tmp_path / "index.html").read_text()
    assert 'href="2026-06-28-s1.html"' in idx  # relative sibling link (works published)


def test_public_build_redacts_client_name(tmp_path):
    dirty = {**PAYLOAD, "slug": "leaky", "summary": "Worked on Synthco Field today"}
    bsr.build(dirty, tmp_path, PATTERNS, public=True)
    page = (tmp_path / "2026-06-28-leaky.html").read_text()
    assert "Synthco Field" not in page
    sani.assert_clean(page, PATTERNS)  # gate passes on the written page


def test_committed_session_pages_pass_sanitization():
    """Every committed session page must be public-safe against the real deny-list."""
    repo_root = Path(__file__).resolve().parents[2]
    pats = sani.load_deny_patterns(repo_root / ".legal-deny-list.yaml")
    sessions = repo_root / "docs" / "reports" / "sessions"
    pages = [p for p in sessions.glob("*.html") if p.name != "index.html"] if sessions.exists() else []
    for page in pages:
        sani.assert_clean(page.read_text(encoding="utf-8"), pats)
