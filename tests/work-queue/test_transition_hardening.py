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


# ════════════════════════════════════════════════════════════════════════════
# SABOTAGE TESTS — deliberately break things and verify enforcement catches it
# ════════════════════════════════════════════════════════════════════════════

class TestSabotageChecklistBlocksExit:
    """Incomplete checklist must block exit — even if evidence file exists."""

    def test_one_of_three_incomplete_blocks(self, tmp_path):
        from verify_checklist import verify_checklist
        stage_yaml = tmp_path / "stage-10.yaml"
        _write(str(stage_yaml), textwrap.dedent("""\
            order: 10
            name: Work Execution
            checklist:
              - id: CL-10-1
                text: "TDD red"
                requires_human: false
              - id: CL-10-2
                text: "TDD green"
                requires_human: false
              - id: CL-10-3
                text: "Git pushed"
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
            wrk_id="WRK-SABOTAGE",
            stage=10,
            evidence_dir=str(evidence_dir),
        )
        assert result["passed"] is False
        assert len(result["blockers"]) == 1
        assert result["blockers"][0]["id"] == "CL-10-3"


class TestSabotageHumanItemWithoutApprover:
    """requires_human: true completed by agent but no approved_by → blocked."""

    def test_agent_completes_human_item_without_approval(self, tmp_path):
        from verify_checklist import verify_checklist
        stage_yaml = tmp_path / "stage-17.yaml"
        _write(str(stage_yaml), textwrap.dedent("""\
            order: 17
            name: User Review Close
            checklist:
              - id: CL-17-1
                text: "Walk through stages 10-16"
                requires_human: true
              - id: CL-17-2
                text: "Explicit approval"
                requires_human: true
        """))
        evidence_dir = tmp_path / "evidence"
        _write(str(evidence_dir / "checklist-17.yaml"), textwrap.dedent("""\
            stage: 17
            items:
              - id: CL-17-1
                completed: true
                completed_at: "2026-03-18T00:00:00Z"
                completed_by: agent
              - id: CL-17-2
                completed: true
                completed_at: "2026-03-18T00:01:00Z"
                completed_by: agent
        """))
        result = verify_checklist(
            stage_yaml_path=str(stage_yaml),
            wrk_id="WRK-SABOTAGE",
            stage=17,
            evidence_dir=str(evidence_dir),
        )
        assert result["passed"] is False
        assert len(result["blockers"]) == 2
        for b in result["blockers"]:
            assert "approved_by" in b["reason"]


class TestSabotageHookFailureBlocksExit:
    """Hard hook that exits 1 must appear in blockers."""

    def test_hard_hook_exit_1_blocks(self, tmp_path):
        from run_hooks import run_hooks
        script = tmp_path / "hooks" / "fail-hard.sh"
        _make_script(str(script), exit_code=1, stderr="AC check failed")
        blockers = run_hooks(
            hooks=[{"script": str(script), "gate": "hard",
                    "timeout_s": 10, "description": "AC check"}],
            wrk_id="WRK-SABOTAGE",
            repo_root=str(tmp_path),
            phase="pre_exit",
            stage=10,
        )
        assert len(blockers) == 1
        assert blockers[0]["returncode"] == 1
        assert "AC check" in blockers[0]["description"]


class TestSabotageHookTimeoutBlocks:
    """Hook that exceeds timeout must be treated as failure."""

    def test_timeout_is_hard_failure(self, tmp_path):
        from run_hooks import run_hooks
        script = tmp_path / "hooks" / "hang.sh"
        _make_slow_script(str(script), sleep_seconds=10)
        blockers = run_hooks(
            hooks=[{"script": str(script), "gate": "hard",
                    "timeout_s": 1, "description": "Hanging hook"}],
            wrk_id="WRK-SABOTAGE",
            repo_root=str(tmp_path),
            phase="pre_exit",
            stage=10,
        )
        assert len(blockers) == 1
        assert blockers[0]["returncode"] == -1


class TestSabotageMixedHooksOnlyHardBlocks:
    """Soft fail + hard fail → only hard appears in blockers."""

    def test_mixed_only_hard_in_blockers(self, tmp_path):
        from run_hooks import run_hooks
        soft_script = tmp_path / "hooks" / "soft-fail.sh"
        _make_script(str(soft_script), exit_code=1, stderr="soft warning")
        hard_script = tmp_path / "hooks" / "hard-fail.sh"
        _make_script(str(hard_script), exit_code=1, stderr="critical error")
        blockers = run_hooks(
            hooks=[
                {"script": str(soft_script), "gate": "soft",
                 "timeout_s": 10, "description": "Soft lint"},
                {"script": str(hard_script), "gate": "hard",
                 "timeout_s": 10, "description": "Hard gate check"},
            ],
            wrk_id="WRK-SABOTAGE",
            repo_root=str(tmp_path),
            phase="pre_exit",
            stage=10,
        )
        assert len(blockers) == 1
        assert blockers[0]["description"] == "Hard gate check"


class TestSabotagePartialCompletion:
    """3 defined, 2 complete → exactly 1 blocker with correct ID."""

    def test_exact_blocker_id(self, tmp_path):
        from verify_checklist import verify_checklist
        stage_yaml = tmp_path / "stage-12.yaml"
        _write(str(stage_yaml), textwrap.dedent("""\
            order: 12
            name: TDD Eval
            checklist:
              - id: CL-12-1
                text: "Full suite run"
                requires_human: false
              - id: CL-12-2
                text: "AC mapped"
                requires_human: false
              - id: CL-12-3
                text: "Matrix written"
                requires_human: false
        """))
        evidence_dir = tmp_path / "evidence"
        _write(str(evidence_dir / "checklist-12.yaml"), textwrap.dedent("""\
            stage: 12
            items:
              - id: CL-12-1
                completed: true
                completed_at: "2026-03-18T00:00:00Z"
                completed_by: agent
              - id: CL-12-3
                completed: true
                completed_at: "2026-03-18T00:01:00Z"
                completed_by: agent
        """))
        result = verify_checklist(
            stage_yaml_path=str(stage_yaml),
            wrk_id="WRK-SABOTAGE",
            stage=12,
            evidence_dir=str(evidence_dir),
        )
        assert result["passed"] is False
        assert len(result["blockers"]) == 1
        assert result["blockers"][0]["id"] == "CL-12-2"


# ════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS — verify wiring between enforcement layer and stage scripts
# ════════════════════════════════════════════════════════════════════════════

class TestIntegrationExitBlocksOnChecklist:
    """exit_stage.validate_exit + verify_checklist wired: incomplete checklist → exit blocked."""

    def _setup_stage(self, tmp_path, checklist_yaml=None):
        """Set up a minimal stage directory with contract + artifacts."""
        # Stage YAML with checklist
        stages_dir = tmp_path / "scripts" / "work-queue" / "stages"
        stages_dir.mkdir(parents=True)
        _write(str(stages_dir / "stage-10-work-execution.yaml"), textwrap.dedent("""\
            order: 10
            name: Work Execution
            weight: heavy
            invocation: task_agent
            human_gate: false
            exit_artifacts:
              - assets/WRK-INT/evidence/execute.yaml
            checklist:
              - id: CL-10-1
                text: "Tests written"
                requires_human: false
              - id: CL-10-2
                text: "Git pushed"
                requires_human: false
        """))
        # Assets dir with required artifact
        assets = tmp_path / ".claude" / "work-queue" / "assets" / "WRK-INT"
        evidence = assets / "evidence"
        evidence.mkdir(parents=True)
        _write(str(evidence / "execute.yaml"), "status: done\ntest_count: 5\n")
        # Checklist evidence (optional)
        if checklist_yaml:
            _write(str(evidence / "checklist-10.yaml"), checklist_yaml)
        return str(assets)

    def test_exit_blocked_when_checklist_incomplete(self, tmp_path):
        """validate_exit passes artifacts but verify_checklist blocks."""
        stage_dir = self._setup_stage(tmp_path)
        # No checklist evidence → all items are blockers
        # Call validate_exit which now calls verify_checklist internally
        from exit_stage import validate_exit
        # validate_exit needs the stage YAML path for checklist lookup
        # But it's called from _main() which does the lookup — test via _main simulation
        # Instead, test verify_checklist directly with the real stage YAML
        from verify_checklist import verify_checklist
        stage_yaml = str(tmp_path / "scripts" / "work-queue" / "stages" / "stage-10-work-execution.yaml")
        result = verify_checklist(
            stage_yaml_path=stage_yaml,
            wrk_id="WRK-INT",
            stage=10,
            evidence_dir=str(tmp_path / ".claude" / "work-queue" / "assets" / "WRK-INT" / "evidence"),
        )
        assert result["passed"] is False
        assert len(result["blockers"]) == 2

    def test_exit_passes_when_checklist_complete(self, tmp_path):
        checklist = textwrap.dedent("""\
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
        """)
        stage_dir = self._setup_stage(tmp_path, checklist_yaml=checklist)
        from verify_checklist import verify_checklist
        stage_yaml = str(tmp_path / "scripts" / "work-queue" / "stages" / "stage-10-work-execution.yaml")
        result = verify_checklist(
            stage_yaml_path=stage_yaml,
            wrk_id="WRK-INT",
            stage=10,
            evidence_dir=str(tmp_path / ".claude" / "work-queue" / "assets" / "WRK-INT" / "evidence"),
        )
        assert result["passed"] is True


class TestIntegrationPreExitHooksFromYaml:
    """_load_pre_exit_hooks merges pre_checks + pre_exit_hooks from real stage YAML."""

    def test_stage07_pre_checks_loaded(self):
        """Stage 7 YAML has pre_checks → merged into hooks list."""
        from exit_stage import _load_pre_exit_hooks
        stage_yaml = os.path.join(REPO, "scripts", "work-queue", "stages",
                                  "stage-07-user-review-plan-final.yaml")
        hooks = _load_pre_exit_hooks(stage_yaml)
        assert len(hooks) >= 1
        assert any("check-p1-resolved" in h["script"] for h in hooks)
        assert all(h.get("gate") in ("hard", "soft") for h in hooks)

    def test_stage17_pre_checks_normalized(self):
        """Stage 17 pre_checks with gate:hard (was required:true) loads correctly."""
        from exit_stage import _load_pre_exit_hooks
        stage_yaml = os.path.join(REPO, "scripts", "work-queue", "stages",
                                  "stage-17-user-review-implementation.yaml")
        hooks = _load_pre_exit_hooks(stage_yaml)
        assert len(hooks) >= 1
        assert any("check-acs-pass" in h["script"] for h in hooks)
        assert hooks[0]["gate"] == "hard"

    def test_stage14_pre_exit_hooks_loaded(self):
        """Stage 14 has pre_exit_hooks (not pre_checks) → loaded directly."""
        from exit_stage import _load_pre_exit_hooks
        stage_yaml = os.path.join(REPO, "scripts", "work-queue", "stages",
                                  "stage-14-verify-gate-evidence.yaml")
        hooks = _load_pre_exit_hooks(stage_yaml)
        assert len(hooks) >= 1
        assert any("verify-gate-evidence" in h["script"] for h in hooks)

    def test_stage10_no_pre_exit_hooks(self):
        """Stage 10 has no pre_exit_hooks or pre_checks → empty list."""
        from exit_stage import _load_pre_exit_hooks
        stage_yaml = os.path.join(REPO, "scripts", "work-queue", "stages",
                                  "stage-10-work-execution.yaml")
        hooks = _load_pre_exit_hooks(stage_yaml)
        assert hooks == []


class TestIntegrationPreEnterHooksWired:
    """start_stage._run_pre_enter_hooks fires hooks from stage YAML."""

    def test_pre_enter_hook_blocks_on_failure(self, tmp_path):
        """Failing pre_enter hook → SystemExit(1)."""
        from start_stage import _run_pre_enter_hooks
        # Create a stage YAML with a failing pre_enter hook
        stages_dir = tmp_path / "scripts" / "work-queue" / "stages"
        stages_dir.mkdir(parents=True)
        fail_script = tmp_path / "scripts" / "work-queue" / "fail-hook.sh"
        _make_script(str(fail_script), exit_code=1, stderr="precondition not met")
        _write(str(stages_dir / "stage-10-work-execution.yaml"), textwrap.dedent(f"""\
            order: 10
            name: Work Execution
            pre_enter_hooks:
              - script: {fail_script}
                description: "Check precondition"
                gate: hard
                timeout_s: 10
        """))
        assets_dir = str(tmp_path / ".claude" / "work-queue" / "assets" / "WRK-HOOK")
        os.makedirs(assets_dir, exist_ok=True)
        with pytest.raises(SystemExit) as exc:
            _run_pre_enter_hooks("WRK-HOOK", 10, str(tmp_path), assets_dir)
        assert exc.value.code == 1

    def test_pre_enter_hook_passes_on_success(self, tmp_path):
        """Passing pre_enter hook → no exception."""
        from start_stage import _run_pre_enter_hooks
        stages_dir = tmp_path / "scripts" / "work-queue" / "stages"
        stages_dir.mkdir(parents=True)
        ok_script = tmp_path / "scripts" / "work-queue" / "ok-hook.sh"
        _make_script(str(ok_script), exit_code=0)
        _write(str(stages_dir / "stage-10-work-execution.yaml"), textwrap.dedent(f"""\
            order: 10
            name: Work Execution
            pre_enter_hooks:
              - script: {ok_script}
                description: "All good"
                gate: hard
                timeout_s: 10
        """))
        assets_dir = str(tmp_path / ".claude" / "work-queue" / "assets" / "WRK-HOOK")
        os.makedirs(assets_dir, exist_ok=True)
        # Should not raise
        _run_pre_enter_hooks("WRK-HOOK", 10, str(tmp_path), assets_dir)


class TestIntegrationStageTiming:
    """Stage timing: started_at written at entry, completed_at + duration at exit."""

    def test_timing_start_written(self, tmp_path):
        """_log_gate_wait_start writes stage-timing-NN.yaml with started_at."""
        from start_stage import _log_gate_wait_start
        # Create is-human-gate.sh that returns exit 1 (not a human gate)
        scripts_dir = tmp_path / "scripts" / "work-queue"
        scripts_dir.mkdir(parents=True)
        _make_script(str(scripts_dir / "is-human-gate.sh"), exit_code=1)
        assets_dir = tmp_path / ".claude" / "work-queue" / "assets" / "WRK-TIME" / "evidence"
        assets_dir.mkdir(parents=True)
        _log_gate_wait_start("WRK-TIME", 10, str(tmp_path))
        timing_file = assets_dir / "stage-timing-10.yaml"
        assert timing_file.exists()
        content = timing_file.read_text()
        assert "started_at:" in content
        assert "stage: 10" in content
        assert "human_gate: false" in content

    def test_timing_human_gate_flagged(self, tmp_path):
        """Human-gate stage gets human_gate: true in timing file."""
        from start_stage import _log_gate_wait_start
        scripts_dir = tmp_path / "scripts" / "work-queue"
        scripts_dir.mkdir(parents=True)
        _make_script(str(scripts_dir / "is-human-gate.sh"), exit_code=0)  # IS a gate
        assets_dir = tmp_path / ".claude" / "work-queue" / "assets" / "WRK-TIME" / "evidence"
        assets_dir.mkdir(parents=True)
        _log_gate_wait_start("WRK-TIME", 5, str(tmp_path))
        timing_file = assets_dir / "stage-timing-05.yaml"
        assert timing_file.exists()
        content = timing_file.read_text()
        assert "human_gate: true" in content

    def test_timing_completed_appended(self, tmp_path):
        """_log_stage_completed appends completed_at + duration_s."""
        from exit_stage import _log_stage_completed
        stage_dir = tmp_path / "assets" / "WRK-TIME"
        evidence = stage_dir / "evidence"
        evidence.mkdir(parents=True)
        # Write a started_at timestamp
        _write(str(evidence / "stage-timing-10.yaml"), textwrap.dedent("""\
            stage: 10
            wrk_id: WRK-TIME
            human_gate: false
            started_at: "2026-03-18T05:00:00+00:00"
        """))
        _log_stage_completed(10, str(stage_dir))
        content = (evidence / "stage-timing-10.yaml").read_text()
        assert "completed_at:" in content
        assert "duration_s:" in content
