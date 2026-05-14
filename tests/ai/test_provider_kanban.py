"""Tests for scripts/ai/provider-kanban.py (#2665)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "provider-kanban.py"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "ai" / "provider_kanban"

spec = importlib.util.spec_from_file_location("provider_kanban", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["provider_kanban"] = module
spec.loader.exec_module(module)

# Pre-load continuous-planning-pipeline ONCE from the real repo path so tests that
# monkeypatch provider-kanban's WORKSPACE_HUB don't poison the loader.
CPP_PATH = REPO_ROOT / "scripts" / "ai" / "continuous-planning-pipeline.py"
_cpp_spec = importlib.util.spec_from_file_location("_cpp_for_tests", CPP_PATH)
cpp_module = importlib.util.module_from_spec(_cpp_spec)
assert _cpp_spec.loader is not None
sys.modules["_cpp_for_tests"] = cpp_module
_cpp_spec.loader.exec_module(cpp_module)


def _write_plan(root: Path, number: int, *, status: str = "plan-review", with_risks: bool = True, with_tdd: bool = True) -> Path:
    path = root / "docs" / "plans" / f"2026-05-12-issue-{number}-sample.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [
        f"# Plan for #{number}: sample work",
        "",
        f"> **Status:** {status}",
        "",
        "## Deliverable",
        "",
        "A sample deliverable used to verify hover-card extraction from durable plan data.",
        "",
    ]
    if with_risks:
        body.extend([
            "## Risks and Open Questions",
            "",
            "- **Risk:** mocked dependency could leak into real CLI invocation",
            "- **Risk:** atomic promotion ordering against parallel git activity",
            "",
        ])
    if with_tdd:
        body.extend([
            "## TDD Test List",
            "",
            "| Test name | What it verifies | Expected input | Expected output |",
            "|---|---|---|---|",
            "| `test_one` | first | foo | bar |",
            "| `test_two` | second | foo | bar |",
            "",
        ])
    body.append("## Acceptance Criteria\n- [ ] sample\n")
    path.write_text("\n".join(body), encoding="utf-8")
    return path


def _write_reviews(root: Path, number: int, verdicts: dict[str, str], sha: str | None = None) -> None:
    base = root / "scripts" / "review" / "results"
    base.mkdir(parents=True, exist_ok=True)
    for provider, verdict in verdicts.items():
        path = base / f"2026-05-12-plan-{number}-{provider}.md"
        prefix = f"Plan-SHA256: {sha}\n" if sha else ""
        if verdict == "EMPTY":
            path.write_text("", encoding="utf-8")
        else:
            path.write_text(f"{prefix}Verdict: {verdict}\nbody\n", encoding="utf-8")


def _marker(root: Path, number: int, *, body: str | None = None) -> Path:
    path = root / ".planning" / "plan-approved" / f"{number}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    default = (
        f"# Marker\nApproved by: user\nApproval source: test\nIssue: #{number}\n"
        f"Plan: docs/plans/2026-05-12-issue-{number}-sample.md\n"
    )
    path.write_text(body or default, encoding="utf-8")
    return path


def _issue(number, labels=None, *, state="OPEN", title="sample") -> dict:
    return {
        "number": number,
        "title": title,
        "url": f"https://example.test/issues/{number}",
        "state": state,
        "labels": [{"name": lbl} for lbl in (labels or [])],
        "body": "",
        "comments": [],
    }


def _scorecard():
    return json.loads((FIXTURE_DIR / "scorecard.json").read_text(encoding="utf-8"))


def _workstations():
    return json.loads((FIXTURE_DIR / "workstations.json").read_text(encoding="utf-8"))


def _work_queue_with_full_candidates(numbers: list[int]) -> dict:
    return {
        "generated_at": "2026-05-12T12:00:00Z",
        "provider_queues": {
            "codex": {
                "provider": "codex",
                "top_issues": [{"number": n, "routing_reason": "fix"} for n in numbers[:8]],
                "full_candidates": [{"number": n, "routing_reason": "fix"} for n in numbers],
            },
            "claude": {"provider": "claude", "top_issues": [], "full_candidates": []},
            "gemini": {"provider": "gemini", "top_issues": [], "full_candidates": []},
        },
    }


def _patch_root(monkeypatch, root: Path):
    monkeypatch.setattr(module, "WORKSPACE_HUB", root)


# ────────────────────────────────────────────────────────────────────────────
# Plan-named tests
# ────────────────────────────────────────────────────────────────────────────


def test_kanban_groups_issues_by_lane_provider_and_machine(tmp_path, monkeypatch):
    _patch_root(monkeypatch, tmp_path)
    plan_path = _write_plan(tmp_path, 8001)
    # Load continuous-planning-pipeline against this tmp tree by patching its WORKSPACE_HUB too.
    cpp = cpp_module
    monkeypatch.setattr(cpp_module, "WORKSPACE_HUB", tmp_path)

    # Issue with all gates clean → execution_ready lane
    sha = cpp.sha256_file(plan_path)
    _write_reviews(tmp_path, 8001, {"claude": "MINOR", "codex": "MINOR", "gemini": "MINOR"}, sha=sha)
    _marker(tmp_path, 8001)

    kanban = module.build_kanban(
        work_queue=_work_queue_with_full_candidates([8001]),
        scorecard=_scorecard(),
        utilization={},
        workstations=_workstations(),
        issues=[_issue(8001, ["status:plan-approved"])],
        root=tmp_path,
        pipeline_module=cpp,
    )

    assert "execution_ready" in kanban["lanes"]
    assert any(c["number"] == 8001 for c in kanban["lanes"]["execution_ready"])
    card = kanban["cards"][0]
    assert card["provider_route"] == "codex"
    assert card["machine_route"] == "ace-linux-1", "should pick the first reachable+authed+fresh ace-linux-1"
    assert card["machine_ready"] is True


def test_kanban_uses_full_issue_candidate_set_not_top_issues_truncation(tmp_path, monkeypatch):
    """If full_candidates is missing the generator must fail closed (#2665)."""
    _patch_root(monkeypatch, tmp_path)

    # Synthetic queue with NO full_candidates
    bad_queue = {
        "generated_at": "2026-05-12T12:00:00Z",
        "provider_queues": {
            "codex": {"provider": "codex", "top_issues": []},  # missing full_candidates
        },
    }
    with pytest.raises(module.KanbanError, match="full_candidates"):
        module.build_kanban(
            work_queue=bad_queue, scorecard=_scorecard(), utilization={},
            workstations=_workstations(), issues=[_issue(1, [])],
            root=tmp_path,
        )

    # And when full_candidates DOES exist with 12 codex issues, all 12 appear in cards.
    cpp = cpp_module
    monkeypatch.setattr(cpp_module, "WORKSPACE_HUB", tmp_path)
    numbers = list(range(8100, 8112))  # 12 issues
    issues = [_issue(n, ["status:plan-review"]) for n in numbers]
    kanban = module.build_kanban(
        work_queue=_work_queue_with_full_candidates(numbers),
        scorecard=_scorecard(), utilization={}, workstations=_workstations(),
        issues=issues, root=tmp_path, pipeline_module=cpp,
    )
    seen_numbers = {c["number"] for c in kanban["cards"]}
    assert seen_numbers == set(numbers), "all 12 candidates must surface in Kanban cards"


def test_hover_summary_includes_plan_risk_tests_and_route(tmp_path, monkeypatch):
    _patch_root(monkeypatch, tmp_path)
    cpp = cpp_module
    monkeypatch.setattr(cpp_module, "WORKSPACE_HUB", tmp_path)
    plan_path = _write_plan(tmp_path, 8201, with_risks=True, with_tdd=True)
    sha = cpp.sha256_file(plan_path)
    _write_reviews(tmp_path, 8201, {"claude": "MINOR", "codex": "MINOR", "gemini": "MINOR"}, sha=sha)

    kanban = module.build_kanban(
        work_queue=_work_queue_with_full_candidates([8201]),
        scorecard=_scorecard(), utilization={}, workstations=_workstations(),
        issues=[_issue(8201, ["status:plan-review", "priority:high"])],
        root=tmp_path, pipeline_module=cpp,
    )

    hover = kanban["cards"][0]["hover"]
    assert "sample deliverable" in hover["plan_summary"].lower()
    assert "atomic promotion" in hover["risks"] or "mocked dependency" in hover["risks"]
    assert "TDD tests" in hover["tests"]
    assert hover["provider_route"] == "codex"
    assert hover["machine_route"] == "ace-linux-1"
    assert "priority:high" in hover["labels"]


def test_approve_button_disabled_when_reviews_missing_or_major(tmp_path, monkeypatch):
    _patch_root(monkeypatch, tmp_path)
    cpp = cpp_module
    monkeypatch.setattr(cpp_module, "WORKSPACE_HUB", tmp_path)
    plan_path = _write_plan(tmp_path, 8301)
    sha = cpp.sha256_file(plan_path)
    # Two providers MINOR, one MAJOR → not clean
    _write_reviews(tmp_path, 8301, {"claude": "MAJOR", "codex": "MINOR", "gemini": "MINOR"}, sha=sha)

    kanban = module.build_kanban(
        work_queue=_work_queue_with_full_candidates([8301]),
        scorecard=_scorecard(), utilization={}, workstations=_workstations(),
        issues=[_issue(8301, ["status:plan-review"])],
        root=tmp_path, served_localhost=True,
        user_intent_metadata={"user_action_token": "tok-abc"},
        pipeline_module=cpp,
    )
    card = kanban["cards"][0]
    assert card["approval_ready"] is False
    assert any("major_review" in b for b in card["approval_blockers"])


def test_approve_button_enabled_only_for_open_plan_review_issue_with_plan_and_clean_reviews(tmp_path, monkeypatch):
    _patch_root(monkeypatch, tmp_path)
    cpp = cpp_module
    monkeypatch.setattr(cpp_module, "WORKSPACE_HUB", tmp_path)
    plan_path = _write_plan(tmp_path, 8401)
    sha = cpp.sha256_file(plan_path)
    _write_reviews(tmp_path, 8401, {"claude": "MINOR", "codex": "APPROVE", "gemini": "MINOR"}, sha=sha)
    # NOTE: do NOT create a marker — plan-review status needs absent marker.

    # Without served_localhost the button must be disabled.
    kanban_static = module.build_kanban(
        work_queue=_work_queue_with_full_candidates([8401]),
        scorecard=_scorecard(), utilization={}, workstations=_workstations(),
        issues=[_issue(8401, ["status:plan-review"])],
        root=tmp_path, served_localhost=False, pipeline_module=cpp,
    )
    assert kanban_static["cards"][0]["approval_ready"] is False
    assert any("static dashboard" in b for b in kanban_static["cards"][0]["approval_blockers"])

    # With served_localhost AND user_action_token, all gates pass → enabled.
    kanban_live = module.build_kanban(
        work_queue=_work_queue_with_full_candidates([8401]),
        scorecard=_scorecard(), utilization={}, workstations=_workstations(),
        issues=[_issue(8401, ["status:plan-review"])],
        root=tmp_path, served_localhost=True,
        user_intent_metadata={"user_action_token": "tok-xyz"},
        pipeline_module=cpp,
    )
    assert kanban_live["cards"][0]["approval_ready"] is True
    assert kanban_live["cards"][0]["approval_blockers"] == []


def test_render_static_html_contains_no_secrets_and_no_external_mutation_by_default(tmp_path, monkeypatch):
    _patch_root(monkeypatch, tmp_path)
    cpp = cpp_module
    monkeypatch.setattr(cpp_module, "WORKSPACE_HUB", tmp_path)
    plan_path = _write_plan(tmp_path, 8501)
    sha = cpp.sha256_file(plan_path)
    _write_reviews(tmp_path, 8501, {"claude": "MINOR", "codex": "MINOR", "gemini": "MINOR"}, sha=sha)

    kanban = module.build_kanban(
        work_queue=_work_queue_with_full_candidates([8501]),
        scorecard=_scorecard(), utilization={}, workstations=_workstations(),
        issues=[_issue(8501, ["status:plan-review"])],
        root=tmp_path, served_localhost=False, pipeline_module=cpp,
    )
    html = module.render_html(kanban)

    # No external fetch / no JS that mutates remote state
    assert "<script" not in html.lower(), "static HTML must not include script tags"
    assert "fetch(" not in html, "static HTML must not include fetch() calls"
    assert "xhr" not in html.lower()

    # No tokens / API keys / env secrets
    for taboo in ("ghp_", "sk-", "AKIA", "GITHUB_TOKEN", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        assert taboo not in html, f"static HTML must not contain {taboo}"

    # Buttons are visibly disabled in static mode
    assert 'disabled' in html, "static HTML must render disabled approval buttons"

    # CLI fallback commands are present
    assert "approve-provider-plan.py" in html
    assert "--mode dry-run" in html
    assert "--mode real" in html


def test_kanban_renders_markdown_with_lane_headers(tmp_path, monkeypatch):
    _patch_root(monkeypatch, tmp_path)
    cpp = cpp_module
    monkeypatch.setattr(cpp_module, "WORKSPACE_HUB", tmp_path)
    _write_plan(tmp_path, 8601)

    kanban = module.build_kanban(
        work_queue=_work_queue_with_full_candidates([8601]),
        scorecard=_scorecard(), utilization={}, workstations=_workstations(),
        issues=[_issue(8601, [])],
        root=tmp_path, pipeline_module=cpp,
    )
    md = module.render_markdown(kanban)
    for lane in ("plan_review", "execution_ready", "running_leased", "qa_closeout", "planning_feedstock", "blocked"):
        assert f"Lane: {lane}" in md
    assert "approve-provider-plan.py" in md
