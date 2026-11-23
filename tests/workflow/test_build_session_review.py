"""Tests for the #3306 lean reference-layer session-review renderer."""
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
    "headline": "One-line headline.",
    "refs": [
        {"type": "issue", "num": 3306, "label": "lean session review"},
        {"type": "pr", "num": 3299},
        {"type": "plan", "path": "docs/plans/2026-06-28-issue-3306-lean-session-review.md"},
        {"type": "decision", "label": "publish-mode=sanitized-public", "num": 3298},
        {"type": "handoff", "label": "session record", "path": "docs/session-handoffs/x.md"},
        {"type": "report", "label": "sessions index", "path": "docs/reports/sessions/index.html"},
    ],
}


def test_refs_resolve_to_canonical_homes():
    html = bsr.render_session_html(PAYLOAD)
    assert f"{bsr.REPO}/issues/3306" in html          # issue
    assert f"{bsr.REPO}/pull/3299" in html            # PR
    assert f"{bsr.REPO}/blob/main/docs/plans/2026-06-28-issue-3306-lean-session-review.md" in html  # plan path
    assert f"{bsr.REPO}/issues/3298" in html          # decision → issue thread
    assert f"{bsr.REPO}/blob/main/docs/session-handoffs/x.md" in html  # handoff record


def test_page_is_lean_no_restated_prose_blocks():
    html = bsr.render_session_html(PAYLOAD)
    # the lean page has no KPI tiles, no data tables, no bulleted prose sections
    assert 'class="kpi"' not in html
    assert "<table" not in html
    assert "<ul>" not in html
    assert 'class="refs"' in html  # grouped link index instead


def test_grouped_headings_present():
    html = bsr.render_session_html(PAYLOAD)
    for heading in ("Issues", "PRs", "Plans", "Decisions", "Record", "Reports"):
        assert f">{heading}</span>" in html


def test_self_contained():
    html = bsr.render_session_html(PAYLOAD)
    assert "<link" not in html and "<script" not in html and "src=" not in html
    assert "<style>" in html


def test_missing_path_ref_is_flagged_not_silent(tmp_path):
    payload = {**PAYLOAD, "refs": [{"type": "plan", "path": "docs/plans/nope.md"}]}
    html = bsr.render_session_html(payload, repo_root=tmp_path)  # file absent → flagged
    assert "⚠" in html
    # and a present file is NOT flagged
    (tmp_path / "docs" / "plans").mkdir(parents=True)
    (tmp_path / "docs" / "plans" / "yes.md").write_text("x")
    html2 = bsr.render_session_html(
        {**PAYLOAD, "refs": [{"type": "plan", "path": "docs/plans/yes.md"}]}, repo_root=tmp_path)
    assert "⚠" not in html2


def test_v1_payload_shim_renders_lean():
    # an old v1 payload (issues[]/prs[], no refs) still renders as lean links
    v1 = {"slug": "old", "date": "2026-06-01", "title": "Old",
          "issues": [{"num": 100, "note": "thing"}], "prs": [{"num": 200, "what": "fix"}]}
    html = bsr.render_session_html(v1)
    assert f"{bsr.REPO}/issues/100" in html
    assert f"{bsr.REPO}/pull/200" in html
    assert "<table" not in html  # not the old table render


def test_unknown_ref_type_not_dropped():
    html = bsr.render_session_html(
        {**PAYLOAD, "refs": [{"type": "weird", "label": "keepme", "href": "https://x"}]})
    assert "keepme" in html and "Other" in html


def test_build_writes_page_manifest_and_index(tmp_path):
    entry = bsr.build(PAYLOAD, tmp_path, PATTERNS, public=True)
    assert (tmp_path / "2026-06-28-demo.html").exists()
    assert entry["file"] == "2026-06-28-demo.html"
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest[0]["slug"] == "demo"
    assert "Session Reviews" in (tmp_path / "index.html").read_text()


def test_public_build_redacts_client_name(tmp_path):
    dirty = {**PAYLOAD, "slug": "leaky",
             "refs": [{"type": "issue", "num": 1, "label": "work on Synthco Field"}]}
    bsr.build(dirty, tmp_path, PATTERNS, public=True)
    page = (tmp_path / "2026-06-28-leaky.html").read_text()
    assert "Synthco Field" not in page
    sani.assert_clean(page, PATTERNS)


def test_committed_session_pages_pass_sanitization():
    repo_root = Path(__file__).resolve().parents[2]
    pats = sani.load_deny_patterns(repo_root / ".legal-deny-list.yaml")
    sessions = repo_root / "docs" / "reports" / "sessions"
    pages = [p for p in sessions.glob("*.html") if p.name != "index.html"] if sessions.exists() else []
    for page in pages:
        sani.assert_clean(page.read_text(encoding="utf-8"), pats)
