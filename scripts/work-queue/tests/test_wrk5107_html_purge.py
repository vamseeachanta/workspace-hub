"""
Tests for WRK-5107: Purge HTML gates from verify-gate-evidence.py.

Covers:
- check_github_issue_gate(): valid URL, PR URL, comment URL, missing, malformed
- Integrated test gate: count=2 fail, count=3 pass, count=10 pass, duplicates
- Resource-intelligence gate: "done"/"COMPLETE" pass, unknown fail
- Future-work gate: string recs, mixed recs, malformed (null, number) fail
- Plan gate: spec_ref present pass, missing fallback
- Removed HTML functions no longer exist
"""
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module import via importlib (file has hyphens in name)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "work-queue"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "verify_gate_evidence",
    SCRIPTS_DIR / "verify-gate-evidence.py",
)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

check_github_issue_gate = _mod.check_github_issue_gate
check_execute_integrated_tests_gate = _mod.check_execute_integrated_tests_gate
check_resource_intelligence_gate = _mod.check_resource_intelligence_gate
check_future_work_gate = _mod.check_future_work_gate
get_field = _mod.get_field


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_assets(tmp_path: Path) -> Path:
    assets = tmp_path / "assets"
    (assets / "evidence").mkdir(parents=True)
    return assets


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# T1 — HTML functions removed
# ---------------------------------------------------------------------------

def test_T1_html_functions_removed():
    """Purged HTML functions must no longer exist on the module."""
    assert not hasattr(_mod, "check_browser_open_elapsed_time")
    assert not hasattr(_mod, "check_html_open_default_browser_gate")
    assert not hasattr(_mod, "check_user_review_publish_gate")
    assert not hasattr(_mod, "check_plan_publish_predates_approval")


# ---------------------------------------------------------------------------
# T2 — check_github_issue_gate: valid URL
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("url", [
    "https://github.com/user/repo/issues/123",
    "https://www.github.com/org/my-repo/issues/1",
    "https://github.com/a/b/issues/99999",
])
def test_T2_github_issue_gate_valid(tmp_path, url):
    assets = _make_assets(tmp_path)
    fm = f"---\ngithub_issue_ref: {url}\n---\n"
    ok, detail = check_github_issue_gate(fm)
    assert ok is True, detail


# ---------------------------------------------------------------------------
# T3 — check_github_issue_gate: PR URL rejected
# ---------------------------------------------------------------------------

def test_T3_github_issue_gate_pr_url(tmp_path):
    fm = "---\ngithub_issue_ref: https://github.com/user/repo/pull/42\n---\n"
    ok, detail = check_github_issue_gate(fm)
    assert ok is False
    assert "issue" in detail.lower() or "invalid" in detail.lower()


# ---------------------------------------------------------------------------
# T4 — check_github_issue_gate: comment URL rejected
# ---------------------------------------------------------------------------

def test_T4_github_issue_gate_comment_url(tmp_path):
    fm = "---\ngithub_issue_ref: https://github.com/user/repo/issues/1#issuecomment-123\n---\n"
    ok, detail = check_github_issue_gate(fm)
    assert ok is False


# ---------------------------------------------------------------------------
# T5 — check_github_issue_gate: missing field
# ---------------------------------------------------------------------------

def test_T5_github_issue_gate_missing():
    fm = "---\ntitle: something\n---\n"
    ok, detail = check_github_issue_gate(fm)
    assert ok is False
    assert "missing" in detail.lower() or "absent" in detail.lower()


# ---------------------------------------------------------------------------
# T6 — check_github_issue_gate: malformed URL
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("url", [
    "not-a-url",
    "http://github.com/user/repo/issues/1",
    "https://gitlab.com/user/repo/issues/1",
    "https://github.com/user/repo/issues/",
    "https://github.com/user/repo/issues/abc",
])
def test_T6_github_issue_gate_malformed(url):
    fm = f"---\ngithub_issue_ref: {url}\n---\n"
    ok, detail = check_github_issue_gate(fm)
    assert ok is False


# ---------------------------------------------------------------------------
# T7 — Integrated test gate: count < 3 fails
# ---------------------------------------------------------------------------

def test_T7_integrated_tests_too_few(tmp_path):
    assets = _make_assets(tmp_path)
    _write(assets / "evidence" / "execute.yaml", (
        "integrated_repo_tests:\n"
        "  - name: t1\n    scope: integrated\n    command: pytest\n"
        "    result: pass\n    artifact_ref: a.txt\n"
        "  - name: t2\n    scope: repo\n    command: pytest\n"
        "    result: pass\n    artifact_ref: b.txt\n"
    ))
    ok, detail = check_execute_integrated_tests_gate(assets)
    assert ok is False
    assert "3" in detail


# ---------------------------------------------------------------------------
# T8 — Integrated test gate: count = 3 passes
# ---------------------------------------------------------------------------

def test_T8_integrated_tests_exactly_three(tmp_path):
    assets = _make_assets(tmp_path)
    tests_yaml = ""
    for i in range(1, 4):
        tests_yaml += (
            f"  - name: t{i}\n    scope: integrated\n    command: pytest\n"
            f"    result: pass\n    artifact_ref: f{i}.txt\n"
        )
    _write(assets / "evidence" / "execute.yaml",
           f"integrated_repo_tests:\n{tests_yaml}")
    ok, detail = check_execute_integrated_tests_gate(assets)
    assert ok is True, detail


# ---------------------------------------------------------------------------
# T9 — Integrated test gate: count = 10 passes (no upper bound)
# ---------------------------------------------------------------------------

def test_T9_integrated_tests_ten_passes(tmp_path):
    assets = _make_assets(tmp_path)
    tests_yaml = ""
    for i in range(1, 11):
        tests_yaml += (
            f"  - name: t{i}\n    scope: integrated\n    command: pytest\n"
            f"    result: pass\n    artifact_ref: f{i}.txt\n"
        )
    _write(assets / "evidence" / "execute.yaml",
           f"integrated_repo_tests:\n{tests_yaml}")
    ok, detail = check_execute_integrated_tests_gate(assets)
    assert ok is True, detail


# ---------------------------------------------------------------------------
# T10 — Integrated test gate: duplicates collapsed
# ---------------------------------------------------------------------------

def test_T10_integrated_tests_duplicates_collapsed(tmp_path):
    """3 entries but only 2 unique names → count=2 → FAIL."""
    assets = _make_assets(tmp_path)
    tests_yaml = ""
    for i in [1, 2, 1]:  # name t1 appears twice
        tests_yaml += (
            f"  - name: t{i}\n    scope: integrated\n    command: pytest\n"
            f"    result: pass\n    artifact_ref: f{i}.txt\n"
        )
    _write(assets / "evidence" / "execute.yaml",
           f"integrated_repo_tests:\n{tests_yaml}")
    ok, detail = check_execute_integrated_tests_gate(assets)
    assert ok is False
    assert "unique" in detail.lower() or "2" in detail


# ---------------------------------------------------------------------------
# T11 — Resource-intelligence: "done" passes
# ---------------------------------------------------------------------------

def test_T11_resource_intelligence_done(tmp_path):
    assets = _make_assets(tmp_path)
    _write(assets / "evidence" / "resource-intelligence.yaml", (
        "completion_status: done\n"
        "top_p1_gaps: []\n"
        "skills:\n  core_used: [a, b, c]\n"
    ))
    ok, detail = check_resource_intelligence_gate(assets)
    assert ok is True, detail


# ---------------------------------------------------------------------------
# T12 — Resource-intelligence: "COMPLETE" passes (case-insensitive)
# ---------------------------------------------------------------------------

def test_T12_resource_intelligence_complete_upper(tmp_path):
    assets = _make_assets(tmp_path)
    _write(assets / "evidence" / "resource-intelligence.yaml", (
        "completion_status: COMPLETE\n"
        "top_p1_gaps: []\n"
        "skills:\n  core_used: [a, b, c]\n"
    ))
    ok, detail = check_resource_intelligence_gate(assets)
    assert ok is True, detail


# ---------------------------------------------------------------------------
# T13 — Resource-intelligence: unknown status fails
# ---------------------------------------------------------------------------

def test_T13_resource_intelligence_unknown_fails(tmp_path):
    assets = _make_assets(tmp_path)
    _write(assets / "evidence" / "resource-intelligence.yaml", (
        "completion_status: banana\n"
        "top_p1_gaps: []\n"
        "skills:\n  core_used: [a, b, c]\n"
    ))
    ok, detail = check_resource_intelligence_gate(assets)
    assert ok is False


# ---------------------------------------------------------------------------
# T14 — Future-work: string recommendations pass
# ---------------------------------------------------------------------------

def test_T14_future_work_string_recs(tmp_path):
    assets = _make_assets(tmp_path)
    _write(assets / "evidence" / "future-work.yaml", (
        "recommendations:\n"
        "  - disposition: existing-updated\n    status: done\n"
        "    captured: true\n"
    ))
    ok, detail = check_future_work_gate(assets)
    assert ok is True, detail


# ---------------------------------------------------------------------------
# T15 — Future-work: mixed recs (strings + dicts) pass
# ---------------------------------------------------------------------------

def test_T15_future_work_mixed_recs(tmp_path):
    """Both dict and string entries should be accepted."""
    assets = _make_assets(tmp_path)
    _write(assets / "evidence" / "future-work.yaml", (
        "recommendations:\n"
        "  - disposition: spun-off-new\n    status: done\n"
        "    captured: true\n"
        "  - disposition: existing-updated\n    status: done\n"
        "    captured: true\n"
    ))
    ok, detail = check_future_work_gate(assets)
    assert ok is True, detail


# ---------------------------------------------------------------------------
# T16 — Future-work: null entry fails
# ---------------------------------------------------------------------------

def test_T16_future_work_null_entry(tmp_path):
    assets = _make_assets(tmp_path)
    _write(assets / "evidence" / "future-work.yaml", (
        "recommendations:\n"
        "  - null\n"
    ))
    ok, detail = check_future_work_gate(assets)
    assert ok is False


# ---------------------------------------------------------------------------
# T17 — Future-work: number entry fails
# ---------------------------------------------------------------------------

def test_T17_future_work_number_entry(tmp_path):
    assets = _make_assets(tmp_path)
    _write(assets / "evidence" / "future-work.yaml", (
        "recommendations:\n"
        "  - 42\n"
    ))
    ok, detail = check_future_work_gate(assets)
    assert ok is False


# ---------------------------------------------------------------------------
# T18 — Plan gate: spec_ref present
# ---------------------------------------------------------------------------

def test_T18_plan_spec_ref_used():
    """get_field on spec_ref should return a value from frontmatter."""
    fm = "spec_ref: .claude/work-queue/assets/WRK-999/plan.md\n"
    val = get_field(fm, "spec_ref")
    assert val is not None
    assert "plan.md" in val
