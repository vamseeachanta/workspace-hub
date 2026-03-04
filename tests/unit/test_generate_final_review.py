from __future__ import annotations

import importlib.util
import sys
from unittest.mock import patch
from pathlib import Path


def _load_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "work-queue" / "generate-final-review.py"
    spec = importlib.util.spec_from_file_location("generate_final_review", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_split_frontmatter_parses_header():
    mod = _load_module()
    text = "---\nid: WRK-1\nstatus: working\n---\n\n# Title\nBody\n"
    fm, body = mod._split_frontmatter(text)
    assert fm["id"] == "WRK-1"
    assert fm["status"] == "working"
    assert body.startswith("# Title")


def test_extract_first_section_returns_first_match():
    mod = _load_module()
    body = "## Context\nA\n\n## Why\nB\n"
    assert mod._extract_first_section(body, ["What", "Context"]) == "A"


def test_sanitize_rendered_html_strips_scripts_and_inline_handlers():
    mod = _load_module()
    dirty = '<p onclick=evil()>X</p><script>alert(1)</script><svg onload=evil()></svg><a href="javascript:bad()">y</a>'
    clean = mod._sanitize_rendered_html(dirty)
    assert "<script" not in clean.lower()
    assert "onclick=" not in clean.lower()
    assert "<svg" not in clean.lower()
    assert "javascript:" not in clean.lower()


def test_validate_wrk_id_rejects_path_traversal():
    mod = _load_module()
    try:
        mod._validate_wrk_id("../../etc/passwd")
    except ValueError:
        return
    raise AssertionError("Expected ValueError for invalid WRK id")


def test_safe_workspace_ref_blocks_escape(tmp_path: Path):
    mod = _load_module()
    outside = mod._safe_workspace_ref(tmp_path, "../../etc/passwd")
    assert outside is None


def test_safe_workspace_ref_accepts_in_workspace(tmp_path: Path):
    mod = _load_module()
    good = mod._safe_workspace_ref(tmp_path, "a/b/c.txt")
    assert good is not None
    assert str(good).startswith(str(tmp_path.resolve()))


def test_sanitize_rendered_html_fails_closed_when_bleach_missing():
    mod = _load_module()
    with patch.dict(sys.modules, {"bleach": None}):
        clean = mod._sanitize_rendered_html("<p>ok</p>")
    assert "sanitizer dependency missing" in clean.lower()


def test_collect_sections_uses_asset_fallback_on_escaped_plan_ref(tmp_path: Path):
    mod = _load_module()
    assets_dir = tmp_path / "assets"
    evidence_dir = assets_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "plan-html-review-draft.md").write_text("draft-fallback", encoding="utf-8")
    (assets_dir / "plan-html-review-final.md").write_text("final-fallback", encoding="utf-8")
    fm = {
        "plan_html_review_draft_ref": "../../outside-draft.md",
        "plan_html_review_final_ref": "../../outside-final.md",
    }
    sections = mod._collect_sections(
        body="## What\nx\n",
        fm=fm,
        workspace_root=tmp_path,
        assets_dir=assets_dir,
        evidence_dir=evidence_dir,
    )
    assert sections["draft_review"] == "draft-fallback"
    assert sections["final_review"] == "final-fallback"
