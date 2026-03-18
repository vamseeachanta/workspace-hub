"""
Tests for WRK-1316: Stage transition hardening
  - run_hooks.py   — generic hook runner with gate/timeout/evidence
  - verify_checklist.py — checklist engine with blocker reporting

Run: uv run --no-project python -m pytest tests/work-queue/test_transition_hardening.py -v
"""

import json
import os
import stat
import sys
import textwrap

import pytest
import yaml

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "scripts", "work-queue"))


# ── helpers ──────────────────────────────────────────────────────────────────

def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def _make_script(path, exit_code=0, stderr=""):
    """Create an executable bash script that exits with the given code."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = ["#!/usr/bin/env bash"]
    if stderr:
        lines.append(f'echo "{stderr}" >&2')
    lines.append(f"exit {exit_code}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)


def _make_slow_script(path, sleep_seconds=5):
    """Create a script that sleeps (for timeout testing)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(f"#!/usr/bin/env bash\nsleep {sleep_seconds}\nexit 0\n")
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)


# ════════════════════════════════════════════════════════════════════════════
# RUN_HOOKS TESTS
# ════════════════════════════════════════════════════════════════════════════

class TestRunHooksNoHooks:
    """Empty or missing hook list → no blockers."""

    def test_empty_list_returns_no_blockers(self, tmp_path):
        from run_hooks import run_hooks
        blockers = run_hooks(
            hooks=[],
            wrk_id="WRK-TEST",
            repo_root=str(tmp_path),
            phase="pre_exit",
            stage=10,
        )
        assert blockers == []

    def test_none_hooks_returns_no_blockers(self, tmp_path):
        from run_hooks import run_hooks
        blockers = run_hooks(
            hooks=None,
            wrk_id="WRK-TEST",
            repo_root=str(tmp_path),
            phase="pre_exit",
            stage=10,
        )
        assert blockers == []


class TestRunHooksPassingHook:
    """Hook script exits 0 → no blockers."""

    def test_passing_hook_returns_no_blockers(self, tmp_path):
        from run_hooks import run_hooks
        script = tmp_path / "hooks" / "check-ok.sh"
        _make_script(str(script), exit_code=0)
        hooks = [{"script": str(script), "gate": "hard", "timeout_s": 10,
                  "description": "Always passes"}]
        blockers = run_hooks(
            hooks=hooks,
            wrk_id="WRK-TEST",
            repo_root=str(tmp_path),
            phase="pre_exit",
            stage=10,
        )
        assert blockers == []


class TestRunHooksFailingHard:
    """Hook exits non-zero with gate: hard → blocker returned."""

    def test_failing_hard_hook_blocks(self, tmp_path):
        from run_hooks import run_hooks
        script = tmp_path / "hooks" / "check-fail.sh"
        _make_script(str(script), exit_code=1, stderr="ACs not complete")
        hooks = [{"script": str(script), "gate": "hard", "timeout_s": 10,
                  "description": "Check ACs pass"}]
        blockers = run_hooks(
            hooks=hooks,
            wrk_id="WRK-TEST",
            repo_root=str(tmp_path),
            phase="pre_exit",
            stage=10,
        )
        assert len(blockers) == 1
        assert blockers[0]["description"] == "Check ACs pass"
        assert blockers[0]["returncode"] == 1


class TestRunHooksFailingSoft:
    """Hook exits non-zero with gate: soft → NO blocker (warn only)."""

    def test_failing_soft_hook_warns_only(self, tmp_path):
        from run_hooks import run_hooks
        script = tmp_path / "hooks" / "check-warn.sh"
        _make_script(str(script), exit_code=1, stderr="optional check failed")
        hooks = [{"script": str(script), "gate": "soft", "timeout_s": 10,
                  "description": "Optional lint"}]
        blockers = run_hooks(
            hooks=hooks,
            wrk_id="WRK-TEST",
            repo_root=str(tmp_path),
            phase="pre_exit",
            stage=10,
        )
        assert blockers == []


class TestRunHooksTimeout:
    """Hook exceeds timeout → treated as hard failure."""

    def test_hook_timeout_treated_as_failure(self, tmp_path):
        from run_hooks import run_hooks
        script = tmp_path / "hooks" / "slow.sh"
        _make_slow_script(str(script), sleep_seconds=10)
        hooks = [{"script": str(script), "gate": "hard", "timeout_s": 1,
                  "description": "Slow hook"}]
        blockers = run_hooks(
            hooks=hooks,
            wrk_id="WRK-TEST",
            repo_root=str(tmp_path),
            phase="pre_exit",
            stage=10,
        )
        assert len(blockers) == 1
        assert "timeout" in blockers[0].get("stderr", "").lower() or blockers[0]["returncode"] != 0


class TestRunHooksWrkSubstitution:
    """WRK-NNN token in script path replaced with actual WRK ID."""

    def test_wrk_nnn_token_substituted(self, tmp_path):
        from run_hooks import run_hooks
        script = tmp_path / "hooks" / "check-WRK-0042.sh"
        _make_script(str(script), exit_code=0)
        hooks = [{"script": str(tmp_path / "hooks" / "check-WRK-NNN.sh"),
                  "gate": "hard", "timeout_s": 10,
                  "description": "WRK-specific check"}]
        blockers = run_hooks(
            hooks=hooks,
            wrk_id="WRK-0042",
            repo_root=str(tmp_path),
            phase="pre_exit",
            stage=10,
        )
        assert blockers == []


class TestRunHooksEvidence:
    """Hook execution writes evidence YAML to assets dir."""

    def test_hook_evidence_written(self, tmp_path):
        from run_hooks import run_hooks
        assets = tmp_path / "assets" / "WRK-TEST" / "evidence"
        assets.mkdir(parents=True)
        script = tmp_path / "hooks" / "check.sh"
        _make_script(str(script), exit_code=0)
        hooks = [{"script": str(script), "gate": "hard", "timeout_s": 10,
                  "description": "Evidence test"}]
        blockers = run_hooks(
            hooks=hooks,
            wrk_id="WRK-TEST",
            repo_root=str(tmp_path),
            phase="pre_exit",
            stage=10,
            assets_dir=str(tmp_path / "assets" / "WRK-TEST"),
        )
        evidence_file = assets / "hooks-pre_exit-10.yaml"
        assert evidence_file.exists(), "Hook evidence file not written"
        data = yaml.safe_load(evidence_file.read_text())
        assert data["phase"] == "pre_exit"
        assert data["stage"] == 10
        assert len(data["hooks"]) == 1
        assert data["hooks"][0]["passed"] is True


class TestRunHooksDryRun:
    """--dry-run mode: log what would run without executing."""

    def test_dry_run_does_not_execute(self, tmp_path):
        from run_hooks import run_hooks
        script = tmp_path / "hooks" / "dangerous.sh"
        _make_script(str(script), exit_code=1, stderr="should not run")
        hooks = [{"script": str(script), "gate": "hard", "timeout_s": 10,
                  "description": "Dangerous hook"}]
        blockers = run_hooks(
            hooks=hooks,
            wrk_id="WRK-TEST",
            repo_root=str(tmp_path),
            phase="pre_exit",
            stage=10,
            dry_run=True,
        )
        assert blockers == []


# ════════════════════════════════════════════════════════════════════════════
# VERIFY_CHECKLIST TESTS
# ════════════════════════════════════════════════════════════════════════════

class TestChecklistNoChecklist:
    """Stage with no checklist defined → passes (backward compat)."""

    def test_no_checklist_defined_passes(self, tmp_path):
        from verify_checklist import verify_checklist
        stage_yaml = tmp_path / "stage-10.yaml"
        _write(str(stage_yaml), "order: 10\nname: Work Execution\n")
        result = verify_checklist(
            stage_yaml_path=str(stage_yaml),
            wrk_id="WRK-TEST",
            stage=10,
            evidence_dir=str(tmp_path / "evidence"),
        )
        assert result["passed"] is True
        assert result["blockers"] == []


class TestChecklistAllComplete:
    """All checklist items complete → passes."""

    def test_all_items_complete_passes(self, tmp_path):
        from verify_checklist import verify_checklist
        stage_yaml = tmp_path / "stage-10.yaml"
        _write(str(stage_yaml), textwrap.dedent("""\
            order: 10
            name: Work Execution
            checklist:
              - id: CL-10-1
                text: "Tests written before implementation"
                requires_human: false
              - id: CL-10-2
                text: "No regressions"
                requires_human: false
        """))
        evidence_dir = tmp_path / "evidence"
        _write(str(evidence_dir / "checklist-10.yaml"), textwrap.dedent("""\
            stage: 10
            items:
              - id: CL-10-1
                completed: true
                completed_at: "2026-03-18T00:00:00Z"
                completed_by: agent
              - id: CL-10-2
                completed: true
                completed_at: "2026-03-18T00:01:00Z"
                completed_by: agent
        """))
        result = verify_checklist(
            stage_yaml_path=str(stage_yaml),
            wrk_id="WRK-TEST",
            stage=10,
            evidence_dir=str(evidence_dir),
        )
        assert result["passed"] is True
        assert result["blockers"] == []


class TestChecklistIncomplete:
    """Missing checklist item → blocker returned."""

    def test_incomplete_item_blocks(self, tmp_path):
        from verify_checklist import verify_checklist
        stage_yaml = tmp_path / "stage-10.yaml"
        _write(str(stage_yaml), textwrap.dedent("""\
            order: 10
            name: Work Execution
            checklist:
              - id: CL-10-1
                text: "Tests written"
                requires_human: false
              - id: CL-10-2
                text: "No regressions"
                requires_human: false
        """))
        evidence_dir = tmp_path / "evidence"
        _write(str(evidence_dir / "checklist-10.yaml"), textwrap.dedent("""\
            stage: 10
            items:
              - id: CL-10-1
                completed: true
                completed_at: "2026-03-18T00:00:00Z"
                completed_by: agent
        """))
        result = verify_checklist(
            stage_yaml_path=str(stage_yaml),
            wrk_id="WRK-TEST",
            stage=10,
            evidence_dir=str(evidence_dir),
        )
        assert result["passed"] is False
        assert len(result["blockers"]) == 1
        assert result["blockers"][0]["id"] == "CL-10-2"


class TestChecklistHumanRequired:
    """requires_human: true item needs approved_by field."""

    def test_human_required_without_approval_blocks(self, tmp_path):
        from verify_checklist import verify_checklist
        stage_yaml = tmp_path / "stage-05.yaml"
        _write(str(stage_yaml), textwrap.dedent("""\
            order: 5
            name: User Review Plan Draft
            checklist:
              - id: CL-05-1
                text: "Plan reviewed section-by-section"
                requires_human: true
        """))
        evidence_dir = tmp_path / "evidence"
        _write(str(evidence_dir / "checklist-05.yaml"), textwrap.dedent("""\
            stage: 5
            items:
              - id: CL-05-1
                completed: true
                completed_at: "2026-03-18T00:00:00Z"
                completed_by: agent
        """))
        result = verify_checklist(
            stage_yaml_path=str(stage_yaml),
            wrk_id="WRK-TEST",
            stage=5,
            evidence_dir=str(evidence_dir),
        )
        assert result["passed"] is False
        assert "approved_by" in result["blockers"][0]["reason"]

    def test_human_required_with_approval_passes(self, tmp_path):
        from verify_checklist import verify_checklist
        stage_yaml = tmp_path / "stage-05.yaml"
        _write(str(stage_yaml), textwrap.dedent("""\
            order: 5
            name: User Review Plan Draft
            checklist:
              - id: CL-05-1
                text: "Plan reviewed"
                requires_human: true
        """))
        evidence_dir = tmp_path / "evidence"
        _write(str(evidence_dir / "checklist-05.yaml"), textwrap.dedent("""\
            stage: 5
            items:
              - id: CL-05-1
                completed: true
                completed_at: "2026-03-18T00:00:00Z"
                completed_by: agent
                approved_by: vamsee
                approved_at: "2026-03-18T00:05:00Z"
        """))
        result = verify_checklist(
            stage_yaml_path=str(stage_yaml),
            wrk_id="WRK-TEST",
            stage=5,
            evidence_dir=str(evidence_dir),
        )
        assert result["passed"] is True


class TestChecklistNoEvidenceFile:
    """Checklist defined but no evidence file → all items are blockers."""

    def test_missing_evidence_blocks_all(self, tmp_path):
        from verify_checklist import verify_checklist
        stage_yaml = tmp_path / "stage-10.yaml"
        _write(str(stage_yaml), textwrap.dedent("""\
            order: 10
            name: Work Execution
            checklist:
              - id: CL-10-1
                text: "Tests written"
                requires_human: false
              - id: CL-10-2
                text: "No regressions"
                requires_human: false
        """))
        result = verify_checklist(
            stage_yaml_path=str(stage_yaml),
            wrk_id="WRK-TEST",
            stage=10,
            evidence_dir=str(tmp_path / "evidence"),
        )
        assert result["passed"] is False
        assert len(result["blockers"]) == 2
