"""
T1-T12: Stage Auto-Loop tests for WRK-1046.

Tests exit_stage.py checkpoint writing, STAGE_GATE signal output,
human_gate detection from contracts, and start_stage.py resume block.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
STAGES_DIR = REPO_ROOT / "scripts" / "work-queue" / "stages"
EXIT_STAGE = REPO_ROOT / "scripts" / "work-queue" / "exit_stage.py"
START_STAGE = REPO_ROOT / "scripts" / "work-queue" / "start_stage.py"
GEN_HTML = REPO_ROOT / "scripts" / "work-queue" / "generate-html-review.py"


# ── shared setup helpers ───────────────────────────────────────────────────────

def _setup_tmp(tmp: Path) -> None:
    """Copy real stage contracts + generate-html-review.py into tmp_path."""
    (tmp / "scripts" / "work-queue").mkdir(parents=True, exist_ok=True)
    if not (tmp / "scripts" / "work-queue" / "stages").exists():
        shutil.copytree(STAGES_DIR, tmp / "scripts" / "work-queue" / "stages")
    shutil.copy(GEN_HTML, tmp / "scripts" / "work-queue" / "generate-html-review.py")


def _patch_stage_contract(tmp: Path, stage: int, human_gate: bool = False,
                           entry_reads: list[str] | None = None,
                           chained: list[int] | None = None) -> None:
    """Overwrite stage contract with minimal version (empty exit_artifacts)."""
    stages_dir = tmp / "scripts" / "work-queue" / "stages"
    # Remove existing
    for f in stages_dir.glob(f"stage-{stage:02d}-*.yaml"):
        f.unlink()
    lines = [
        f"order: {stage}",
        f"name: Test Stage {stage}",
        f"invocation: {'chained_agent' if chained else 'task_agent'}",
        f"human_gate: {'true' if human_gate else 'false'}",
    ]
    if chained:
        lines.append(f"chained_stages: {chained!r}".replace("'", ""))
    if entry_reads:
        lines.append("entry_reads:")
        for er in entry_reads:
            lines.append(f"  - {er}")
    lines.append("exit_artifacts: []")
    (stages_dir / f"stage-{stage:02d}-test.yaml").write_text("\n".join(lines) + "\n")


def _make_assets(tmp: Path, wrk_id: str) -> Path:
    """Create assets dir for WRK."""
    assets = tmp / ".claude" / "work-queue" / "assets" / wrk_id
    (assets / "evidence").mkdir(parents=True)
    return assets


def _run_exit(tmp: Path, wrk_id: str, stage: int,
              extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, "WORKSPACE_HUB": str(tmp)}
    cmd = ["uv", "run", "--no-project", "python", str(EXIT_STAGE), wrk_id, str(stage)]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=tmp, env=env)


def _read_checkpoint(tmp: Path, wrk_id: str) -> dict:
    """Parse checkpoint.yaml into a dict (handles scalar values and list fields)."""
    cp_path = tmp / ".claude" / "work-queue" / "assets" / wrk_id / "checkpoint.yaml"
    if not cp_path.exists():
        return {}
    out: dict = {}
    current_key: str | None = None
    list_items: list[str] = []
    for line in cp_path.read_text().splitlines():
        if line.startswith("  - "):  # list item
            if current_key:
                list_items.append(line.strip()[2:])
            continue
        if current_key and list_items:
            out[current_key] = list_items
            list_items = []
            current_key = None
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            key = k.strip()
            val = v.strip().strip('"').strip("'")
            if val:
                out[key] = val
            else:
                current_key = key
    if current_key and list_items:
        out[current_key] = list_items
    return out


# ── T1: checkpoint written with current_stage=N+1 ────────────────────────────

def test_t1_checkpoint_written_after_stage_exit(tmp_path):
    """T1: exit_stage.py writes checkpoint with current_stage=N+1."""
    wrk_id = "WRK-9901"
    _setup_tmp(tmp_path)
    _make_assets(tmp_path, wrk_id)
    _patch_stage_contract(tmp_path, 3)  # exit stage 3, minimal contract

    result = _run_exit(tmp_path, wrk_id, 3)
    assert result.returncode == 0, result.stderr

    cp = _read_checkpoint(tmp_path, wrk_id)
    assert cp.get("current_stage") == "4", f"expected current_stage=4, got {cp}"
    assert "checkpointed_at" in cp or "updated_at" in cp, f"timestamp missing: {cp}"
    assert cp.get("completed_stage") == "3", f"completed_stage missing: {cp}"


# ── T2: entry_reads from N+1 contract ────────────────────────────────────────

def test_t2_entry_reads_from_next_contract(tmp_path):
    """T2: entry_reads in checkpoint comes from stage N+1 contract."""
    wrk_id = "WRK-9902"
    _setup_tmp(tmp_path)
    _make_assets(tmp_path, wrk_id)
    _patch_stage_contract(tmp_path, 3)
    # Stage 4 contract (next) has entry_reads in real stages dir — not patched

    result = _run_exit(tmp_path, wrk_id, 3)
    assert result.returncode == 0, result.stderr

    cp = _read_checkpoint(tmp_path, wrk_id)
    er = cp.get("entry_reads")
    assert er, f"entry_reads missing or empty in checkpoint: {cp}"


# ── T3: --context-summary arg written ─────────────────────────────────────────

def test_t3_context_summary_from_arg(tmp_path):
    """T3: --context-summary arg lands in checkpoint."""
    wrk_id = "WRK-9903"
    _setup_tmp(tmp_path)
    _make_assets(tmp_path, wrk_id)
    _patch_stage_contract(tmp_path, 3)

    summary = "Triage done. Route=B, priority=high."
    result = _run_exit(tmp_path, wrk_id, 3, ["--context-summary", summary])
    assert result.returncode == 0, result.stderr

    cp = _read_checkpoint(tmp_path, wrk_id)
    assert cp.get("context_summary") == summary, f"got: {cp.get('context_summary')}"


# ── T4: auto-generated context_summary ────────────────────────────────────────

def test_t4_auto_context_summary(tmp_path):
    """T4: when --context-summary absent, auto-generates from stage info."""
    wrk_id = "WRK-9904"
    _setup_tmp(tmp_path)
    _make_assets(tmp_path, wrk_id)
    _patch_stage_contract(tmp_path, 3)

    result = _run_exit(tmp_path, wrk_id, 3)
    assert result.returncode == 0, result.stderr

    cp = _read_checkpoint(tmp_path, wrk_id)
    assert cp.get("context_summary"), "context_summary should be auto-generated"


# ── T5: stage_complete log event or signal ────────────────────────────────────

def test_t5_stage_complete_signal(tmp_path):
    """T5: stage_complete action appears in exit_stage.py stdout."""
    wrk_id = "WRK-9905"
    _setup_tmp(tmp_path)
    _make_assets(tmp_path, wrk_id)
    _patch_stage_contract(tmp_path, 3)

    result = _run_exit(tmp_path, wrk_id, 3)
    assert result.returncode == 0, result.stderr
    combined = result.stdout + result.stderr
    assert "stage_complete" in combined.lower() or "STAGE_GATE" in combined, \
        f"no stage_complete signal:\n{combined}"


# ── T6: STAGE_GATE spawn_subagent for non-gate stage ─────────────────────────

def test_t6_stage_gate_spawn_subagent(tmp_path):
    """T6: STAGE_GATE action=spawn_subagent for non-gate next stage."""
    wrk_id = "WRK-9906"
    _setup_tmp(tmp_path)
    _make_assets(tmp_path, wrk_id)
    _patch_stage_contract(tmp_path, 3)  # stage 3 exit; stage 4 next (human_gate=false)

    result = _run_exit(tmp_path, wrk_id, 3)
    assert result.returncode == 0, result.stderr
    assert "STAGE_GATE" in result.stdout, f"no STAGE_GATE:\n{result.stdout}"
    assert "spawn_subagent" in result.stdout, \
        f"expected spawn_subagent (stage 4 not a human gate):\n{result.stdout}"


# ── T7: STAGE_GATE await_user_approval for stage 5 ───────────────────────────

def test_t7_stage_gate_await_approval_stage5(tmp_path):
    """T7: STAGE_GATE action=await_user_approval when next stage has human_gate=true."""
    wrk_id = "WRK-9907"
    _setup_tmp(tmp_path)
    _make_assets(tmp_path, wrk_id)
    _patch_stage_contract(tmp_path, 4)  # exit stage 4; next = stage 5 (human_gate=true)

    result = _run_exit(tmp_path, wrk_id, 4)
    assert result.returncode == 0, result.stderr
    assert "await_user_approval" in result.stdout, \
        f"stage 5 is human_gate=true; expected await_user_approval:\n{result.stdout}"


# ── T8: await_user_approval for stages 7 and 17 ──────────────────────────────

@pytest.mark.parametrize("completed_stage,extra_setup", [
    (6, "cross_review"),   # exit 6 → next is 7 (human_gate=true); needs cross-review files
    (16, "none"),          # exit 16 → next is 17 (human_gate=true)
])
def test_t8_stage_gate_await_approval_7_17(tmp_path, completed_stage, extra_setup):
    """T8: stages 7 and 17 are human_gate=true → await_user_approval."""
    wrk_id = f"WRK-99{completed_stage:02d}"
    _setup_tmp(tmp_path)
    assets = _make_assets(tmp_path, wrk_id)
    _patch_stage_contract(tmp_path, completed_stage)

    if extra_setup == "cross_review":
        # Stage 6 D-item gate requires ≥3 cross-review files in evidence/ + WRK with route
        for name in ["cross-review-claude.md", "cross-review-codex.md",
                     "cross-review-gemini.md"]:
            (assets / "evidence" / name).write_text("## Verdict\nAPPROVE\n")
        wrk_md = (tmp_path / ".claude" / "work-queue" / "working" /
                  f"{wrk_id}.md")
        wrk_md.parent.mkdir(parents=True, exist_ok=True)
        wrk_md.write_text(f"---\nid: {wrk_id}\nroute: B\nstatus: working\n---\n")

    result = _run_exit(tmp_path, wrk_id, completed_stage)
    assert result.returncode == 0, result.stderr
    assert "await_user_approval" in result.stdout, \
        f"stage {completed_stage+1} should be human_gate=true:\n{result.stdout}"


# ── T9: human_gate read from contract YAML not hardcoded ─────────────────────

def test_t9_human_gate_from_contract(tmp_path):
    """T9: human_gate driven by stage contract YAML, not hardcoded list."""
    wrk_id = "WRK-9909"
    _setup_tmp(tmp_path)
    _make_assets(tmp_path, wrk_id)
    # Create a custom stage that overrides human_gate to true for an unusual stage
    _patch_stage_contract(tmp_path, 10)  # exit stage 10; override next (11) to human_gate=true
    _patch_stage_contract(tmp_path, 11, human_gate=True)

    result = _run_exit(tmp_path, wrk_id, 10)
    assert result.returncode == 0, result.stderr
    # Stage 11 is now human_gate=true via contract, not because of hardcoded list
    assert "await_user_approval" in result.stdout, \
        f"contract-driven human_gate=true not respected:\n{result.stdout}"


# ── T10: start_stage.py resume block fires with current_stage ─────────────────

def test_t10_start_stage_resume_block(tmp_path):
    """T10: start_stage.py shows resume block when checkpoint current_stage matches."""
    wrk_id = "WRK-9910"
    _setup_tmp(tmp_path)
    assets = _make_assets(tmp_path, wrk_id)
    cp = assets / "checkpoint.yaml"
    cp.write_text(
        "wrk_id: WRK-9910\n"
        "current_stage: 5\n"
        "stage_name: User Review Plan Draft\n"
        "completed_stage: 4\n"
        "next_action: Execute stage 5 gate review\n"
        "context_summary: Plan drafted and artifacts ready.\n"
        "entry_reads:\n"
        "  - .claude/work-queue/assets/WRK-9910/checkpoint.yaml\n"
        "  - specs/wrk/WRK-9910/plan.md\n"
        "checkpointed_at: 2026-03-08T19:00:00Z\n"
        "human_gate: true\n"
    )

    env = {**os.environ, "WORKSPACE_HUB": str(tmp_path)}
    result = subprocess.run(
        ["uv", "run", "--no-project", "python", str(START_STAGE), wrk_id, "5"],
        capture_output=True, text=True, cwd=tmp_path, env=env,
    )
    assert result.returncode == 0, result.stderr
    combined = result.stdout
    assert "checkpoint.yaml" in combined or "entry_reads" in combined.lower(), \
        f"resume block missing entry_reads:\n{combined}"


# ── T11: chained_stages in checkpoint for chained_agent contract ──────────────

def test_t11_chained_stages_in_checkpoint(tmp_path):
    """T11: chained_agent stage writes chained_stages from N+1 contract to checkpoint."""
    wrk_id = "WRK-9911"
    _setup_tmp(tmp_path)
    _make_assets(tmp_path, wrk_id)
    _patch_stage_contract(tmp_path, 7)  # exit stage 7; next = 8 which has chained_stages
    # Stage 8 real contract has chained_stages: [8, 9]

    result = _run_exit(tmp_path, wrk_id, 7)
    assert result.returncode == 0, result.stderr

    cp = _read_checkpoint(tmp_path, wrk_id)
    # chained_stages should appear in checkpoint if next stage contract has it
    assert "chained_stages" in cp or "chained_stages" in (result.stdout + result.stderr), \
        f"chained_stages not captured: cp={cp}"


# ── T12: stage 20 terminal — no STAGE_GATE ────────────────────────────────────

def test_t12_stage20_terminal_no_stage_gate(tmp_path):
    """T12: stage 20 exit writes current_stage=complete, no STAGE_GATE printed."""
    wrk_id = "WRK-9912"
    _setup_tmp(tmp_path)
    _make_assets(tmp_path, wrk_id)
    _patch_stage_contract(tmp_path, 20)

    result = _run_exit(tmp_path, wrk_id, 20)
    assert result.returncode == 0, result.stderr
    assert "STAGE_GATE" not in result.stdout, \
        f"stage 20 should not emit STAGE_GATE:\n{result.stdout}"

    cp = _read_checkpoint(tmp_path, wrk_id)
    assert cp.get("current_stage") == "complete", \
        f"expected current_stage=complete: {cp}"
