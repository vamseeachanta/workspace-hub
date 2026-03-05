from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_html_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "work-queue" / "generate-html-review.py"
    spec = importlib.util.spec_from_file_location("generate_html_review", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return _load_html_module()


@pytest.fixture()
def minimal_meta() -> dict:
    return {
        "id": "WRK-9999",
        "title": "test: verify canonical HTML template",
        "status": "working",
        "orchestrator": "claude",
        "computer": "ace-linux-1",
        "created_at": "2026-03-04T00:00:00Z",
        "commit": "abc1234def",
        "percent_complete": 42,
        "complexity": "simple",
        "route": "A",
    }


@pytest.fixture()
def minimal_sections() -> dict:
    return {
        "lede": "Minimal test artifact.",
        "exec_summary_html": "<ul><li>Outcome 1</li></ul>",
        "body_html": "<h2>Plan</h2><p>Step 1.</p>",
        "skill_manifest_html": "",
        "test_evidence_html": "",
        "reviewer_html": "",
    }


def test_collect_test_evidence_detects_missing_files(tmp_path: Path):
    mod = _load_html_module()
    evidence = mod.collect_test_evidence(str(tmp_path))

    assert evidence["example_pack_present"] is False
    assert evidence["variation_tests_present"] is False
    assert "No variation-test summary available" in evidence["variation_summary"]


def test_collect_test_evidence_extracts_variation_summary(tmp_path: Path):
    mod = _load_html_module()
    (tmp_path / "example-pack.md").write_text("# Example Pack\n", encoding="utf-8")
    (tmp_path / "variation-test-results.md").write_text(
        "# Variation Test Results\n\nPASS - all variations covered\n- detail\n",
        encoding="utf-8",
    )

    evidence = mod.collect_test_evidence(str(tmp_path))

    assert evidence["example_pack_present"] is True
    assert evidence["variation_tests_present"] is True
    assert evidence["variation_summary"] == "PASS - all variations covered"


def test_collect_test_evidence_reads_integrated_repo_test_counts(tmp_path: Path):
    mod = _load_html_module()
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "execute.yaml").write_text(
        """
integrated_repo_tests:
  - name: integration-smoke
    scope: integrated
    command: uv run --no-project pytest tests/unit/test_a.py
    result: pass
    artifact_ref: .claude/work-queue/assets/WRK-999/test-a.txt
  - name: repo-contract
    scope: repo
    command: uv run --no-project pytest tests/unit/test_b.py
    result: pass
    artifact_ref: .claude/work-queue/assets/WRK-999/test-b.txt
  - name: repo-regression
    scope: repo
    command: uv run --no-project pytest tests/unit/test_c.py
    result: pass
    artifact_ref: .claude/work-queue/assets/WRK-999/test-c.txt
""".strip()
        + "\n",
        encoding="utf-8",
    )

    evidence = mod.collect_test_evidence(str(tmp_path))

    assert evidence["integrated_repo_tests_count"] == 3
    assert evidence["integrated_repo_tests_valid_range"] is True
    assert evidence["integrated_repo_tests_all_pass"] is True


# ── Design system ─────────────────────────────────────────────────────────────

def test_css_contains_warm_parchment_bg(mod):
    assert "#f3efe6" in mod.CSS


def test_css_contains_teal_accent(mod):
    assert "#0f766e" in mod.CSS


def test_css_contains_badge_classes(mod):
    for cls in ("badge-pass", "badge-warn", "badge-fail", "badge-info"):
        assert cls in mod.CSS, f"Missing CSS class: {cls}"


def test_css_contains_print_media_query(mod):
    assert "@media print" in mod.CSS


def test_js_contains_collapsible_summary(mod):
    assert "buildSummary" in mod.JS


def test_js_contains_toc(mod):
    assert "toc" in mod.JS.lower()


def test_js_no_external_deps(mod):
    # JS must not reference external CDNs
    for cdn in ("cdn.jsdelivr", "unpkg.com", "cdnjs"):
        assert cdn not in mod.JS


# ── render_wrk_html structural ────────────────────────────────────────────────

@pytest.mark.parametrize("artifact_type,label", [
    ("plan-draft",     "Plan Draft Review"),
    ("plan-final",     "Plan Final Review"),
    ("implementation", "Implementation Review"),
    ("close",          "Close Review"),
])
def test_artifact_label_in_eyebrow(mod, minimal_meta, minimal_sections,
                                   artifact_type, label):
    html = mod.render_wrk_html(minimal_meta, artifact_type, minimal_sections)
    assert label in html


def test_h1_contains_title(mod, minimal_meta, minimal_sections):
    html = mod.render_wrk_html(minimal_meta, "plan-draft", minimal_sections)
    assert "test: verify canonical HTML template" in html


def test_lede_present(mod, minimal_meta, minimal_sections):
    html = mod.render_wrk_html(minimal_meta, "plan-draft", minimal_sections)
    assert "Minimal test artifact." in html


def test_meta_grid_present(mod, minimal_meta, minimal_sections):
    html = mod.render_wrk_html(minimal_meta, "plan-draft", minimal_sections)
    assert 'class="meta"' in html
    assert 'class="pill"' in html


def test_exec_summary_present(mod, minimal_meta, minimal_sections):
    html = mod.render_wrk_html(minimal_meta, "plan-draft", minimal_sections)
    assert 'class="exec-summary"' in html


def test_css_inlined_not_linked(mod, minimal_meta, minimal_sections):
    html = mod.render_wrk_html(minimal_meta, "plan-draft", minimal_sections)
    assert "<style>" in html
    assert 'rel="stylesheet"' not in html
    assert "orchestrator.css" not in html


def test_js_inlined(mod, minimal_meta, minimal_sections):
    html = mod.render_wrk_html(minimal_meta, "plan-draft", minimal_sections)
    assert "<script>" in html
    assert "data-collapsed" in html


# ── render_meta_grid ──────────────────────────────────────────────────────────

def test_meta_grid_all_pill_fields(mod, minimal_meta):
    html = mod.render_meta_grid(minimal_meta)
    for label in ("WRK ID", "Status", "Route", "Orchestrator",
                  "Computer", "Created", "Commit", "% Done"):
        assert label in html, f"Missing pill: {label}"


def test_meta_grid_commit_truncated(mod, minimal_meta):
    html = mod.render_meta_grid(minimal_meta)
    assert "abc1234" in html
    assert "abc1234def" not in html


# ── badge helpers ─────────────────────────────────────────────────────────────

def test_badge_pass(mod):
    b = mod.badge("PASS", "pass")
    assert 'badge-pass' in b and "PASS" in b


def test_status_badge_done_is_pass(mod):
    assert "badge-pass" in mod.status_badge("done")


def test_status_badge_pending_is_info(mod):
    assert "badge-info" in mod.status_badge("pending")


# ── render_reviewer_synthesis ─────────────────────────────────────────────────

def test_empty_reviewers_returns_not_applicable(mod):
    html = mod.render_reviewer_synthesis([])
    assert "Cross-Review Summary" in html
    assert "Not applicable." in html


def test_reviewers_table_includes_verdicts(mod):
    reviewers = [
        {"name": "Claude", "verdict": "APPROVE", "kind": "pass",
         "path": "assets/WRK-1/review-claude.md"},
        {"name": "Codex", "verdict": "NO_OUTPUT", "kind": "info",
         "path": "assets/WRK-1/review-codex.md"},
    ]
    html = mod.render_reviewer_synthesis(reviewers)
    assert "APPROVE" in html and "badge-pass" in html
    assert "NO_OUTPUT" in html and "badge-info" in html


def test_close_normalizes_future_work_to_next_work(mod):
    body = "## Future Work\n- item 1\n"
    normalized = mod._normalize_close_section_names(body, "close")
    assert "## Next Work" in normalized
    assert "## Future Work" not in normalized


def test_suppress_duplicate_generated_sections(mod):
    body_html = "<h2>Cross-Review Summary</h2><p>Existing.</p><h2>Test Summary</h2><p>Existing.</p>"
    sm, te, rv = mod._suppress_duplicate_generated_sections(
        body_html,
        "<h2>Skill Manifest</h2><p>Generated.</p>",
        "<h2>Test Summary</h2><p>Generated.</p>",
        "<h2>Cross-Review Summary</h2><p>Generated.</p>",
    )
    assert te == ""
    assert rv == ""
    assert sm != ""
