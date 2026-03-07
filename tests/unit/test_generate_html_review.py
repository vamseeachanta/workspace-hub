from __future__ import annotations

import importlib.util
import io
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


def test_css_uses_smaller_h1_scale(mod):
    assert "clamp(1.75rem,3.2vw,3rem)" in mod.CSS


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
    body_html = (
        "<h2>Cross-Review Summary</h2><p>Existing.</p>"
        "<h2>Test Summary</h2><p>Existing.</p>"
        "<h2>Gate-Pass Stage Status</h2><p>Existing.</p>"
    )
    sm, te, rv, gp = mod._suppress_duplicate_generated_sections(
        body_html,
        "<h2>Skill Manifest</h2><p>Generated.</p>",
        "<h2>Test Summary</h2><p>Generated.</p>",
        "<h2>Cross-Review Summary</h2><p>Generated.</p>",
        "<h2>Gate-Pass Stage Status</h2><p>Generated.</p>",
    )
    assert te == ""
    assert rv == ""
    assert gp == ""
    assert sm != ""


def test_render_gatepass_section_not_applicable(mod):
    html = mod.render_gatepass_section({
        "present": False,
        "stages": [],
        "summary": "Missing stage-evidence.yaml",
        "reason": "stage-evidence.yaml missing",
    })
    assert "Gate-Pass Stage Status" in html
    assert "FAIL" in html
    assert "Missing stage-evidence.yaml" in html


def test_render_gatepass_section_empty_rows_is_fail(mod):
    html = mod.render_gatepass_section({
        "present": True,
        "stages": [],
        "summary": "0 pass · 0 fail · 0 pending/warn · 0 n/a",
        "autonomy": "L1",
    })
    assert "Gate-Pass Stage Status" in html
    assert "No valid stage rows found" in html
    assert "FAIL" in html


def test_collect_stage_gatepass_reads_and_sorts(tmp_path: Path):
    mod = _load_html_module()
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "stage-evidence.yaml").write_text(
        """
autonomy_maturity_level: L3
stages:
  - order: 10
    stage: Work Execution
    status: done
    evidence: a.md
  - order: 2
    stage: Resource Intelligence
    status: blocked
    evidence: b.md
  - order: 18
    stage: Reclaim
    status: n/a
    evidence: c.md
""".strip()
        + "\n",
        encoding="utf-8",
    )
    gp = mod.collect_stage_gatepass(str(tmp_path))
    assert gp["present"] is True
    assert gp["autonomy"] == "L3"
    assert [s["order"] for s in gp["stages"]] == [2, 10, 18]
    assert gp["summary"] == "1 pass · 1 fail · 0 pending/warn · 1 n/a"


def test_collect_stage_gatepass_legacy_autonomy_and_bool_human_decision(tmp_path: Path):
    mod = _load_html_module()
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "stage-evidence.yaml").write_text(
        """
autonomy_maturity: L2
stages:
  - order: 5
    stage: User Review
    status: pending
    evidence: d.md
    human_decision_required: true
""".strip()
        + "\n",
        encoding="utf-8",
    )
    gp = mod.collect_stage_gatepass(str(tmp_path))
    assert gp["present"] is True
    assert gp["autonomy"] == "L2"
    assert gp["stages"][0]["human_decision_required"] == "yes"


def test_collect_stage_gatepass_missing_file(tmp_path: Path):
    mod = _load_html_module()
    gp = mod.collect_stage_gatepass(str(tmp_path))
    assert gp["present"] is False
    assert gp["summary"] == "Missing stage-evidence.yaml"


def test_collect_stage_gatepass_malformed_yaml(tmp_path: Path):
    mod = _load_html_module()
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "stage-evidence.yaml").write_text("key: [unclosed", encoding="utf-8")
    gp = mod.collect_stage_gatepass(str(tmp_path))
    assert gp["present"] is False


def test_collect_stage_gatepass_non_mapping_root(tmp_path: Path):
    mod = _load_html_module()
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "stage-evidence.yaml").write_text("- a\n- b\n", encoding="utf-8")
    gp = mod.collect_stage_gatepass(str(tmp_path))
    assert gp["present"] is False


def test_collect_stage_gatepass_non_list_stages(tmp_path: Path):
    mod = _load_html_module()
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "stage-evidence.yaml").write_text(
        "stages: not-a-list\n",
        encoding="utf-8",
    )
    gp = mod.collect_stage_gatepass(str(tmp_path))
    assert gp["present"] is False
    assert gp["reason"] == "stages must be a list"


def test_render_gatepass_section_escapes_html(mod):
    gp = {
        "present": True,
        "summary": "1 < 2 & risky",
        "autonomy": "L2<script>",
        "stages": [
            {
                "order": "<b>1</b>",
                "stage": "<Stage>",
                "status": "done",
                "gate": "PASS",
                "evidence": "path/<bad>.md",
                "owner": "user&agent",
                "blocker": "no",
                "comment": "x < y",
                "human_decision_required": "yes",
            }
        ],
    }
    html = mod.render_gatepass_section(gp)
    assert "<script>" not in html
    assert "&lt;b&gt;1&lt;/b&gt;" in html
    assert "&lt;Stage&gt;" in html
    assert "1 &lt; 2 &amp; risky" in html


def test_collect_prompt_start_context_reads_source_quote(mod, minimal_meta):
    body = '# Title\n\n## What\nDetails.\n\n*Source: "Original user request text."*\n'
    ctx = mod.collect_prompt_start_context(body, minimal_meta)
    assert ctx["present"] is True
    assert ctx["synthesized"] is False
    assert ctx["text"] == "Original user request text."


def test_collect_prompt_start_context_falls_back_to_title_and_what(mod, minimal_meta):
    body = "# Title\n\n## What\nPlan artifact summary.\n"
    ctx = mod.collect_prompt_start_context(body, minimal_meta)
    assert ctx["present"] is True
    assert ctx["synthesized"] is True
    assert "test: verify canonical HTML template" in ctx["text"]
    assert "Plan artifact summary." in ctx["text"]


def test_strip_duplicate_body_title_removes_matching_h1(mod):
    html = "<h1>test: verify canonical HTML template</h1><h2>What</h2><p>Body.</p>"
    stripped = mod._strip_duplicate_body_title(html, "test: verify canonical HTML template")
    assert stripped.startswith("<h2>What</h2>")
    assert stripped.count("<h1>") == 0


def test_strip_duplicate_body_title_keeps_non_matching_h1(mod):
    html = "<h1>Different heading</h1><h2>What</h2><p>Body.</p>"
    stripped = mod._strip_duplicate_body_title(html, "test: verify canonical HTML template")
    assert stripped == html


def test_collect_plan_quality_eval_reads_yaml(tmp_path: Path):
    mod = _load_html_module()
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "plan-quality-eval.yaml").write_text(
        """
decision_summary: Keep Claude sequencing, Codex validation checks, Gemini risk notes.
artifact_ref: .claude/work-queue/assets/WRK-9999/combined-plan.md
plans:
  - plan: Claude
    rating: strong
    completeness: 4/5
    test_eval_quality: 4/5
    execution_clarity: 5/5
    risk_coverage: 4/5
    standards_gate_alignment: 5/5
    decision: kept-core
    notes: Best sequencing.
""".strip()
        + "\n",
        encoding="utf-8",
    )
    plan_eval = mod.collect_plan_quality_eval(str(tmp_path))
    assert plan_eval["present"] is True
    assert plan_eval["decision_summary"].startswith("Keep Claude sequencing")
    assert plan_eval["plans"][0]["plan"] == "Claude"
    assert plan_eval["plans"][0]["rating"] == "strong"


def test_render_plan_quality_eval_section_renders_table(mod):
    html = mod.render_plan_quality_eval_section({
        "present": True,
        "decision_summary": "Use merged plan.",
        "artifact_ref": ".claude/work-queue/assets/WRK-1/combined-plan.md",
        "plans": [
            {
                "plan": "Claude",
                "rating": "strong",
                "decision": "kept-core",
                "notes": "Best sequencing.",
                "completeness": "4/5",
                "test_eval_quality": "4/5",
                "execution_clarity": "5/5",
                "risk_coverage": "4/5",
                "standards_gate_alignment": "5/5",
            }
        ],
    })
    assert "Plan Quality Eval Comparison" in html
    assert "Use merged plan." in html
    assert "kept-core" in html
    assert "Best sequencing." in html


def test_inject_generated_plan_sections_places_sections_in_plan_artifacts(mod):
    body_html = "<h1>Title</h1><h2>What</h2><p>Why now.</p><h2>Open Questions</h2><p>None.</p>"
    prompt_html = "<h2>Prompt Start Context</h2><div class='panel'><p>Original request.</p></div>"
    plan_eval_html = "<h2>Plan Quality Eval Comparison</h2><p>Comparison.</p>"
    result = mod._inject_generated_plan_sections(body_html, "plan-draft", prompt_html, plan_eval_html)

    assert result.index("Prompt Start Context") > result.index("</h1>")
    assert result.index("Plan Quality Eval Comparison") < result.index("Open Questions")


def test_append_missing_key_sections_adds_plan_quality_eval_placeholder(mod):
    body_html = "<h2>Plan</h2><p>Step 1.</p>"
    result = mod._append_missing_key_sections(body_html, "plan-draft")
    assert "Plan Quality Eval Comparison" in result
    assert "Not applicable." in result


def test_render_wrk_html_does_not_emit_empty_gatepass_card(mod, minimal_meta, minimal_sections):
    sections = dict(minimal_sections)
    sections["gatepass_html"] = ""
    html = mod.render_wrk_html(minimal_meta, "plan-draft", sections)
    assert '<div class="card">\n    \n  </div>' not in html


def test_gatepass_section_appears_once_when_already_in_body(mod):
    body_html = "<h2>Gate-Pass Stage Status</h2><p>Existing.</p>"
    sm, te, rv, gp = mod._suppress_duplicate_generated_sections(
        body_html,
        "<h2>Skill Manifest</h2><p>Generated.</p>",
        "<h2>Test Summary</h2><p>Generated.</p>",
        "<h2>Cross-Review Summary</h2><p>Generated.</p>",
        "<h2>Gate-Pass Stage Status</h2><p>Generated.</p>",
    )
    with_missing = mod._append_missing_key_sections(
        body_html,
        "plan-draft",
        extra_html=[sm, te, rv, gp],
    )
    assert with_missing.count("Gate-Pass Stage Status") == 1


def test_render_wrk_html_includes_gatepass_once_when_only_generated(mod, minimal_meta):
    sections = {
        "lede": "lede",
        "exec_summary_html": "<p>summary</p>",
        "body_html": "<h2>What</h2><p>body</p>",
        "skill_manifest_html": "",
        "gatepass_html": "<h2>Gate-Pass Stage Status</h2><p>Generated.</p>",
        "test_evidence_html": "",
        "reviewer_html": "",
    }
    html = mod.render_wrk_html(minimal_meta, "plan-draft", sections)
    assert html.count("Gate-Pass Stage Status") == 1


def test_generate_review_renders_single_gatepass_heading(tmp_path: Path, monkeypatch):
    mod = _load_html_module()
    repo = tmp_path / "repo"
    queue = repo / ".claude" / "work-queue"
    working = queue / "working"
    assets = queue / "assets" / "WRK-1"
    evidence = assets / "evidence"
    working.mkdir(parents=True)
    evidence.mkdir(parents=True)
    (working / "WRK-1.md").write_text(
        """---
id: WRK-1
title: Sample
status: working
route: B
complexity: B
orchestrator: codex
computer: ace-linux-1
created_at: 2026-03-05
percent_complete: 50
---

## What
Build sample.
""",
        encoding="utf-8",
    )
    (evidence / "stage-evidence.yaml").write_text(
        """
autonomy_maturity_level: L2
stages:
  - order: 5
    stage: User Review - Plan (Draft)
    status: done
    evidence: evidence.md
""".strip()
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod.os, "popen", lambda *_a, **_k: io.StringIO(str(repo)))
    out = assets / "plan-draft-review.html"
    mod.generate_review("WRK-1", "plan-draft", str(out))
    html = out.read_text(encoding="utf-8")
    assert html.count("<h2>Gate-Pass Stage Status</h2>") == 1


# ── Phase 2: Changes Since Stage 5 (AC-21, AC-21b, WRK-1017) ─────────────────

def test_collect_changes_since_stage5_no_publish_yaml(tmp_path: Path):
    mod = _load_html_module()
    result = mod.collect_changes_since_stage5(str(tmp_path), str(tmp_path))
    assert result["present"] is False
    assert "not found" in result["reason"]


def test_collect_changes_since_stage5_no_plan_draft_event(tmp_path: Path):
    mod = _load_html_module()
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    publish = evidence_dir / "user-review-publish.yaml"
    publish.write_text(
        "events:\n  - stage: plan_final\n    commit: abc1234\n    pushed_to_origin: true\n",
        encoding="utf-8",
    )
    result = mod.collect_changes_since_stage5(str(tmp_path), str(tmp_path))
    assert result["present"] is False
    assert "plan_draft" in result["reason"]


def test_collect_changes_since_stage5_unresolvable_commit(tmp_path: Path):
    mod = _load_html_module()
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    publish = evidence_dir / "user-review-publish.yaml"
    publish.write_text(
        "events:\n  - stage: plan_draft\n    commit: deadbeefdeadbeef00000000\n    pushed_to_origin: true\n",
        encoding="utf-8",
    )
    # Use tmp_path as workspace_root so git rev-parse fails (not a real git repo with that commit)
    result = mod.collect_changes_since_stage5(str(tmp_path), str(tmp_path))
    assert result["present"] is False


def test_collect_changes_since_stage5_with_fixture(tmp_path: Path, monkeypatch):
    """AC-21b: fixture-backed test with known delta content."""
    mod = _load_html_module()
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    publish = evidence_dir / "user-review-publish.yaml"
    publish.write_text(
        "events:\n  - stage: plan_draft\n    commit: abc1234abcd\n    pushed_to_origin: true\n",
        encoding="utf-8",
    )

    # Patch subprocess.run to simulate known git output
    import subprocess as _subprocess
    known_stat = (
        " scripts/work-queue/verify-gate-evidence.py | 85 ++++++++\n"
        " specs/templates/stage5-evidence-contract.yaml | 20 ++\n"
        " 2 files changed, 105 insertions(+)\n"
    )
    known_log = (
        "abc1235 feat(WRK-1017): Phase 1A canonical checker\n"
        "abc1236 feat(WRK-1017): add bootstrap script\n"
    )

    call_count = {"n": 0}

    def fake_run(cmd, **kwargs):
        call_count["n"] += 1
        result = _subprocess.CompletedProcess(cmd, 0)
        if "rev-parse" in cmd:
            result.stdout = "abc1234abcd\n"
            result.stderr = ""
            return result
        if "--stat" in cmd:
            result.stdout = known_stat
            result.stderr = ""
            return result
        if "--oneline" in cmd:
            result.stdout = known_log
            result.stderr = ""
            return result
        return result

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    result = mod.collect_changes_since_stage5(str(tmp_path), str(tmp_path))
    assert result["present"] is True
    assert result["baseline_commit"] == "abc1234abcd"
    assert result["commit_count"] == 2
    assert "verify-gate-evidence.py" in result["stat_text"]
    assert "stage5-evidence-contract.yaml" in result["stat_text"]
    assert any("Phase 1A canonical checker" in c for c in result["commits"])


def test_render_changes_since_stage5_absent(mod):
    html = mod.render_changes_since_stage5({"present": False, "reason": "no publish yaml"})
    assert "Changes Since Stage 5" in html
    assert "no publish yaml" in html


def test_render_changes_since_stage5_present(mod):
    delta = {
        "present": True,
        "baseline_commit": "abc1234",
        "stat_text": "scripts/foo.py | 5 ++\n1 file changed",
        "commits": ["abc1235 feat: add foo", "abc1236 fix: fix bar"],
        "commit_count": 2,
    }
    html = mod.render_changes_since_stage5(delta)
    assert "Changes Since Stage 5" in html
    assert "abc1234" in html
    assert "abc1235 feat: add foo" in html
    assert "abc1236 fix: fix bar" in html
    assert "scripts/foo.py" in html


def test_generate_review_plan_final_has_changes_since_stage5(tmp_path: Path, monkeypatch):
    """Integration: plan-final HTML must contain Changes Since Stage 5 section."""
    mod = _load_html_module()
    repo = tmp_path / "repo"
    queue = repo / ".claude" / "work-queue"
    working = queue / "working"
    assets = queue / "assets" / "WRK-2"
    evidence = assets / "evidence"
    working.mkdir(parents=True)
    evidence.mkdir(parents=True)
    (working / "WRK-2.md").write_text(
        "---\nid: WRK-2\ntitle: Phase 2 Test\nstatus: working\nroute: C\n"
        "complexity: complex\norchestrator: claude\ncomputer: ace-linux-1\n"
        "created_at: 2026-03-07\npercent_complete: 60\n---\n\n## What\nTest plan.\n",
        encoding="utf-8",
    )
    # No publish.yaml → section should render with absent message
    monkeypatch.setattr(mod.os, "popen", lambda *_a, **_k: io.StringIO(str(repo)))
    out = assets / "plan-final-review.html"
    mod.generate_review("WRK-2", "plan-final", str(out))
    html = out.read_text(encoding="utf-8")
    assert "Changes Since Stage 5" in html
