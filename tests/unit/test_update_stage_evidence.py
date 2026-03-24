from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


def _script_path() -> Path:
    return Path(__file__).resolve().parents[2] / "scripts" / "work-queue" / "update-stage-evidence.py"


def _write_wrk_and_stage(tmp_path: Path) -> Path:
    stage_file = tmp_path / ".claude" / "work-queue" / "assets" / "WRK-999" / "evidence" / "stage-evidence.yaml"
    stage_file.parent.mkdir(parents=True, exist_ok=True)
    stage_file.write_text(
        """
wrk_id: WRK-999
generated_at: "2026-03-03T00:00:00Z"
reviewed_by: "agent"
stages:
  - order: 1
    stage: Capture
    status: done
    evidence: a
  - order: 2
    stage: Resource Intelligence
    status: pending
    evidence: b
  - order: 3
    stage: Triage
    status: pending
    evidence: c
  - order: 4
    stage: Plan Draft
    status: pending
    evidence: d
  - order: 5
    stage: User Review - Plan (Draft)
    status: pending
    evidence: e
  - order: 6
    stage: Cross-Review
    status: pending
    evidence: f
  - order: 7
    stage: User Review - Plan (Final)
    status: pending
    evidence: g
  - order: 8
    stage: Claim / Activation
    status: pending
    evidence: h
  - order: 9
    stage: Work-Queue Routing Skill
    status: pending
    evidence: i
  - order: 10
    stage: Work Execution
    status: pending
    evidence: j
  - order: 11
    stage: Artifact Generation
    status: pending
    evidence: k
  - order: 12
    stage: TDD / Eval
    status: pending
    evidence: l
  - order: 13
    stage: Agent Cross-Review
    status: pending
    evidence: m
  - order: 14
    stage: Verify Gate Evidence
    status: pending
    evidence: n
  - order: 15
    stage: Future Work Synthesis
    status: pending
    evidence: o
  - order: 16
    stage: Resource Intelligence Update
    status: pending
    evidence: p
  - order: 17
    stage: User Review - Implementation
    status: pending
    evidence: q
  - order: 18
    stage: Reclaim
    status: n/a
    evidence: r
  - order: 19
    stage: Close
    status: pending
    evidence: s
  - order: 20
    stage: Archive
    status: pending
    evidence: t
""".strip()
        + "\n",
        encoding="utf-8",
    )
    wrk_file = tmp_path / ".claude" / "work-queue" / "working" / "WRK-999.md"
    wrk_file.parent.mkdir(parents=True, exist_ok=True)
    wrk_file.write_text(
        f"""---
id: WRK-999
status: working
stage_evidence_ref: .claude/work-queue/assets/WRK-999/evidence/stage-evidence.yaml
---
""",
        encoding="utf-8",
    )
    return stage_file


def test_update_stage_evidence_apply(tmp_path: Path):
    pytest.importorskip("yaml")
    stage_file = _write_wrk_and_stage(tmp_path)
    env = os.environ.copy()
    env["WORKSPACE_ROOT"] = str(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(_script_path()),
            "WRK-999",
            "--order",
            "15",
            "--status",
            "done",
            "--evidence",
            "new-ref",
            "--reviewed-by",
            "codex",
        ],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    text = stage_file.read_text(encoding="utf-8")
    assert "[APPLY]" in result.stdout
    assert "order: 15" in text
    assert "status: done" in text
    assert "evidence: new-ref" in text
    assert "reviewed_by: codex" in text


def _write_repo_prefixed_wrk_and_stage(tmp_path: Path) -> Path:
    """Set up stage-evidence for a repo-prefixed WRK ID (GH-first format)."""
    wrk_id = "workspace-hub-1349"
    stage_file = tmp_path / ".claude" / "work-queue" / "assets" / wrk_id / "evidence" / "stage-evidence.yaml"
    stage_file.parent.mkdir(parents=True, exist_ok=True)
    stage_file.write_text(
        f"""wrk_id: {wrk_id}
generated_at: "2026-03-24T00:00:00Z"
reviewed_by: "agent"
stages:
  - order: 1
    stage: Capture
    status: done
    evidence: a
  - order: 2
    stage: Resource Intelligence
    status: pending
    evidence: b
  - order: 3
    stage: Triage
    status: pending
    evidence: c
  - order: 4
    stage: Plan Draft
    status: pending
    evidence: d
  - order: 5
    stage: User Review - Plan (Draft)
    status: pending
    evidence: e
  - order: 6
    stage: Cross-Review
    status: pending
    evidence: f
  - order: 7
    stage: User Review - Plan (Final)
    status: pending
    evidence: g
  - order: 8
    stage: Claim / Activation
    status: pending
    evidence: h
  - order: 9
    stage: Work-Queue Routing Skill
    status: pending
    evidence: i
  - order: 10
    stage: Work Execution
    status: pending
    evidence: j
  - order: 11
    stage: Artifact Generation
    status: pending
    evidence: k
  - order: 12
    stage: TDD / Eval
    status: pending
    evidence: l
  - order: 13
    stage: Agent Cross-Review
    status: pending
    evidence: m
  - order: 14
    stage: Verify Gate Evidence
    status: pending
    evidence: n
  - order: 15
    stage: Future Work Synthesis
    status: pending
    evidence: o
  - order: 16
    stage: Resource Intelligence Update
    status: pending
    evidence: p
  - order: 17
    stage: User Review - Implementation
    status: pending
    evidence: q
  - order: 18
    stage: Reclaim
    status: n/a
    evidence: r
  - order: 19
    stage: Close
    status: pending
    evidence: s
  - order: 20
    stage: Archive
    status: pending
    evidence: t
""",
        encoding="utf-8",
    )
    wrk_file = tmp_path / ".claude" / "work-queue" / "working" / f"{wrk_id}.md"
    wrk_file.parent.mkdir(parents=True, exist_ok=True)
    wrk_file.write_text(
        f"""---
id: {wrk_id}
status: working
stage_evidence_ref: .claude/work-queue/assets/{wrk_id}/evidence/stage-evidence.yaml
---
""",
        encoding="utf-8",
    )
    return stage_file


def test_update_stage_evidence_repo_prefixed_id(tmp_path: Path):
    """Repo-prefixed IDs (e.g. workspace-hub-1349) must not get WRK- prepended."""
    pytest.importorskip("yaml")
    stage_file = _write_repo_prefixed_wrk_and_stage(tmp_path)
    env = os.environ.copy()
    env["WORKSPACE_ROOT"] = str(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(_script_path()),
            "workspace-hub-1349",
            "--order",
            "2",
            "--status",
            "in_progress",
        ],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    text = stage_file.read_text(encoding="utf-8")
    assert "[APPLY]" in result.stdout
    assert "workspace-hub-1349" in result.stdout
    assert "WRK-workspace-hub" not in result.stdout
    assert "status: in_progress" in text


def test_update_stage_evidence_dry_run_no_change(tmp_path: Path):
    pytest.importorskip("yaml")
    stage_file = _write_wrk_and_stage(tmp_path)
    before = stage_file.read_text(encoding="utf-8")
    env = os.environ.copy()
    env["WORKSPACE_ROOT"] = str(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(_script_path()),
            "WRK-999",
            "--order",
            "16",
            "--status",
            "done",
            "--dry-run",
        ],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    after = stage_file.read_text(encoding="utf-8")
    assert "[DRY-RUN]" in result.stdout
    assert before == after
