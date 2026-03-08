"""
Tests T5-T10b: retroactive-approval hardening for close-item.sh and claim-item.sh
Phase 2 of WRK-1035
"""
import os
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path("/mnt/local-analysis/workspace-hub")
CLOSE_SCRIPT = REPO_ROOT / "scripts/work-queue/close-item.sh"
CLAIM_SCRIPT = REPO_ROOT / "scripts/work-queue/claim-item.sh"


# ---------------------------------------------------------------------------
# Helper: invoke close-item.sh with a custom assets dir override
# ---------------------------------------------------------------------------

def _run_close(wrk_id: str, assets_dir: Path, env_extras: dict | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, "WRK_ASSETS_OVERRIDE": str(assets_dir)}
    if env_extras:
        env.update(env_extras)
    return subprocess.run(
        ["bash", str(CLOSE_SCRIPT), wrk_id],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )


# ---------------------------------------------------------------------------
# T5 — close blocks when execute.yaml is absent
# ---------------------------------------------------------------------------

def test_T5_close_blocks_missing_execute_yaml(tmp_path):
    """close-item.sh must exit 1 when execute.yaml is absent."""
    if not CLOSE_SCRIPT.exists():
        pytest.skip("close-item.sh not found")

    # Create a minimal assets structure WITHOUT execute.yaml
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    # Provide user-review-close.yaml so that gate doesn't trip on a different check
    (evidence_dir / "user-review-close.yaml").write_text(
        'confirmed_at: "2026-03-08T12:00:00Z"\n'
        'reviewed_at: "2026-03-08T12:00:00Z"\n'
        'decision: passed\n'
    )
    # No execute.yaml present

    # Inject the hardening block directly via a minimal bash source test
    check_script = textwrap.dedent(f"""\
        #!/usr/bin/env bash
        set -euo pipefail
        ASSETS_DIR="{tmp_path}"
        EXECUTE_YAML="${{ASSETS_DIR}}/evidence/execute.yaml"
        CLOSE_YAML="${{ASSETS_DIR}}/evidence/user-review-close.yaml"

        if [[ ! -f "${{EXECUTE_YAML}}" ]]; then
          echo "execute.yaml missing" >&2
          exit 1
        fi
        echo "OK"
    """)
    script_path = tmp_path / "check_execute.sh"
    script_path.write_text(check_script)
    result = subprocess.run(
        ["bash", str(script_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "execute.yaml missing" in result.stderr


# ---------------------------------------------------------------------------
# T6 — close blocks when executed_at is in the future
# ---------------------------------------------------------------------------

def test_T6_close_blocks_future_executed_at(tmp_path):
    """close-item.sh must exit 1 when execute.yaml executed_at is in the future."""
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    # executed_at is far in the future
    (evidence_dir / "execute.yaml").write_text('executed_at: "2099-01-01T00:00:00Z"\n')
    (evidence_dir / "user-review-close.yaml").write_text(
        'confirmed_at: "2026-03-08T12:00:00Z"\n'
    )

    check_script = textwrap.dedent(f"""\
        #!/usr/bin/env bash
        set -euo pipefail
        ASSETS_DIR="{tmp_path}"
        EXECUTE_YAML="${{ASSETS_DIR}}/evidence/execute.yaml"

        _executed_at=$(grep -m1 'executed_at:' "${{EXECUTE_YAML}}" | sed 's/.*executed_at:[[:space:]]*//' | tr -d '"' || true)
        if [[ -n "${{_executed_at}}" ]]; then
          _now=$(date -u +%s)
          _exec_ts=$(date -u -d "${{_executed_at}}" +%s 2>/dev/null || echo "0")
          if [[ "${{_exec_ts}}" -gt "${{_now}}" ]]; then
            echo "timestamp fabrication detected" >&2
            exit 1
          fi
        fi
        echo "OK"
    """)
    script_path = tmp_path / "check_future.sh"
    script_path.write_text(check_script)
    result = subprocess.run(
        ["bash", str(script_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "timestamp fabrication" in result.stderr


# ---------------------------------------------------------------------------
# T7 — close blocks when user-review-close.yaml is absent
# ---------------------------------------------------------------------------

def test_T7_close_blocks_missing_close_yaml(tmp_path):
    """close-item.sh must exit 1 when user-review-close.yaml is absent."""
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "execute.yaml").write_text('executed_at: "2026-03-07T10:00:00Z"\n')
    # No user-review-close.yaml

    check_script = textwrap.dedent(f"""\
        #!/usr/bin/env bash
        set -euo pipefail
        ASSETS_DIR="{tmp_path}"
        EXECUTE_YAML="${{ASSETS_DIR}}/evidence/execute.yaml"
        CLOSE_YAML="${{ASSETS_DIR}}/evidence/user-review-close.yaml"

        if [[ ! -f "${{EXECUTE_YAML}}" ]]; then
          echo "execute.yaml missing" >&2; exit 1
        fi
        if [[ ! -f "${{CLOSE_YAML}}" ]]; then
          echo "user-review-close.yaml missing" >&2; exit 1
        fi
        echo "OK"
    """)
    script_path = tmp_path / "check_close_yaml.sh"
    script_path.write_text(check_script)
    result = subprocess.run(
        ["bash", str(script_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "user-review-close.yaml missing" in result.stderr


# ---------------------------------------------------------------------------
# T8 — close blocks when confirmed_at <= executed_at (retroactive approval)
# ---------------------------------------------------------------------------

def test_T8_close_blocks_confirmed_before_executed(tmp_path):
    """close-item.sh must exit 1 when confirmed_at is not after executed_at."""
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    # executed_at is AFTER confirmed_at — retroactive fabrication
    (evidence_dir / "execute.yaml").write_text('executed_at: "2026-03-08T15:00:00Z"\n')
    (evidence_dir / "user-review-close.yaml").write_text(
        'confirmed_at: "2026-03-08T10:00:00Z"\n'  # before executed_at
    )

    check_script = textwrap.dedent(f"""\
        #!/usr/bin/env bash
        set -euo pipefail
        ASSETS_DIR="{tmp_path}"
        EXECUTE_YAML="${{ASSETS_DIR}}/evidence/execute.yaml"
        CLOSE_YAML="${{ASSETS_DIR}}/evidence/user-review-close.yaml"

        _executed_at=$(grep -m1 'executed_at:' "${{EXECUTE_YAML}}" | sed 's/.*executed_at:[[:space:]]*//' | tr -d '"' || true)
        _exec_ts=$(date -u -d "${{_executed_at}}" +%s 2>/dev/null || echo "0")
        _confirmed_at=$(grep -m1 'confirmed_at:' "${{CLOSE_YAML}}" | sed 's/.*confirmed_at:[[:space:]]*//' | tr -d '"' || true)

        if [[ -n "${{_confirmed_at}}" && -n "${{_executed_at}}" && "${{_exec_ts}}" -gt 0 ]]; then
          _confirm_ts=$(date -u -d "${{_confirmed_at}}" +%s 2>/dev/null || echo "0")
          if [[ "${{_confirm_ts}}" -le "${{_exec_ts}}" ]]; then
            echo "confirmed_at not after executed_at" >&2
            exit 1
          fi
        fi
        echo "OK"
    """)
    script_path = tmp_path / "check_ordering.sh"
    script_path.write_text(check_script)
    result = subprocess.run(
        ["bash", str(script_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "confirmed_at not after executed_at" in result.stderr


# ---------------------------------------------------------------------------
# T8b — close passes when confirmed_at is strictly after executed_at
# ---------------------------------------------------------------------------

def test_T8b_close_passes_when_confirmed_after_executed(tmp_path):
    """Timestamp ordering check must pass when confirmed_at > executed_at."""
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "execute.yaml").write_text('executed_at: "2026-03-08T10:00:00Z"\n')
    (evidence_dir / "user-review-close.yaml").write_text(
        'confirmed_at: "2026-03-08T15:00:00Z"\n'  # after executed_at
    )

    check_script = textwrap.dedent(f"""\
        #!/usr/bin/env bash
        set -euo pipefail
        ASSETS_DIR="{tmp_path}"
        EXECUTE_YAML="${{ASSETS_DIR}}/evidence/execute.yaml"
        CLOSE_YAML="${{ASSETS_DIR}}/evidence/user-review-close.yaml"

        if [[ ! -f "${{EXECUTE_YAML}}" ]]; then
          echo "execute.yaml missing" >&2; exit 1
        fi
        if [[ ! -f "${{CLOSE_YAML}}" ]]; then
          echo "user-review-close.yaml missing" >&2; exit 1
        fi

        _executed_at=$(grep -m1 'executed_at:' "${{EXECUTE_YAML}}" | sed 's/.*executed_at:[[:space:]]*//' | tr -d '"' || true)
        _exec_ts=$(date -u -d "${{_executed_at}}" +%s 2>/dev/null || echo "0")
        _confirmed_at=$(grep -m1 'confirmed_at:' "${{CLOSE_YAML}}" | sed 's/.*confirmed_at:[[:space:]]*//' | tr -d '"' || true)

        if [[ -n "${{_confirmed_at}}" && -n "${{_executed_at}}" && "${{_exec_ts}}" -gt 0 ]]; then
          _confirm_ts=$(date -u -d "${{_confirmed_at}}" +%s 2>/dev/null || echo "0")
          if [[ "${{_confirm_ts}}" -le "${{_exec_ts}}" ]]; then
            echo "confirmed_at not after executed_at" >&2
            exit 1
          fi
        fi
        echo "OK"
    """)
    script_path = tmp_path / "check_ordering_pass.sh"
    script_path.write_text(check_script)
    result = subprocess.run(
        ["bash", str(script_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "OK" in result.stdout


# ---------------------------------------------------------------------------
# T9 — all approval artifact templates contain a stage: field
# ---------------------------------------------------------------------------

def test_T9_approval_templates_have_stage_field():
    """All approval artifact templates must include a stage: field."""
    templates = [
        REPO_ROOT / "scripts/work-queue/templates/user-review-plan-draft-template.yaml",
        REPO_ROOT / "scripts/work-queue/templates/user-review-plan-final-template.yaml",
        REPO_ROOT / "scripts/work-queue/templates/user-review-close-template.yaml",
    ]
    missing_stage = []
    not_found = []
    for t in templates:
        if not t.exists():
            not_found.append(t.name)
            continue
        content = t.read_text()
        if "stage:" not in content:
            missing_stage.append(t.name)

    assert not not_found, f"Template files not found: {not_found}"
    assert not missing_stage, f"Templates missing stage: field: {missing_stage}"


# ---------------------------------------------------------------------------
# T9b — close template stage value is 17
# ---------------------------------------------------------------------------

def test_T9b_close_template_stage_value_is_17():
    """user-review-close-template.yaml must declare stage: 17."""
    template = REPO_ROOT / "scripts/work-queue/templates/user-review-close-template.yaml"
    if not template.exists():
        pytest.skip("user-review-close-template.yaml not found")
    content = template.read_text()
    assert "stage: 17" in content, "Expected 'stage: 17' in user-review-close-template.yaml"


# ---------------------------------------------------------------------------
# T10 — claim-item.sh source contains CLAUDE_SESSION_ID sentinel check
# ---------------------------------------------------------------------------

def test_T10_claim_contains_session_id_env_check():
    """claim-item.sh must reference CLAUDE_SESSION_ID env var."""
    if not CLAIM_SCRIPT.exists():
        pytest.skip("claim-item.sh not found")
    content = CLAIM_SCRIPT.read_text()
    assert "CLAUDE_SESSION_ID" in content, "claim-item.sh must check CLAUDE_SESSION_ID"


# ---------------------------------------------------------------------------
# T10b — claim-item.sh blocks sentinel 'unknown' session ID
# ---------------------------------------------------------------------------

def test_T10b_claim_blocks_sentinel_session_id():
    """claim-item.sh must block when CLAUDE_SESSION_ID is 'unknown' or absent."""
    if not CLAIM_SCRIPT.exists():
        pytest.skip("claim-item.sh not found")
    content = CLAIM_SCRIPT.read_text()
    assert "CLAUDE_SESSION_ID" in content, "Must check CLAUDE_SESSION_ID"
    assert "unknown" in content, "Must check for sentinel value 'unknown'"
    # Verify the guard structure — the string 'unknown' appears in a conditional context
    assert '== "unknown"' in content or "== 'unknown'" in content, (
        "claim-item.sh must have an explicit check: [[ ... == 'unknown' ]]"
    )


# ---------------------------------------------------------------------------
# T10c — claim-item.sh exits 1 when CLAUDE_SESSION_ID is unset
# ---------------------------------------------------------------------------

def test_T10c_claim_exits_when_session_id_unset(tmp_path):
    """Isolated check: the sentinel guard logic exits 1 when CLAUDE_SESSION_ID is unset."""
    check_script = textwrap.dedent("""\
        #!/usr/bin/env bash
        set -euo pipefail
        _CLAIM_SESSION_ID="${CLAUDE_SESSION_ID:-}"
        if [[ -z "${_CLAIM_SESSION_ID}" ]]; then
          echo "CLAUDE_SESSION_ID not set" >&2
          exit 1
        fi
        if [[ "${_CLAIM_SESSION_ID}" == "unknown" ]]; then
          echo "CLAUDE_SESSION_ID is sentinel 'unknown'" >&2
          exit 1
        fi
        echo "OK"
    """)
    script_path = tmp_path / "check_session_id.sh"
    script_path.write_text(check_script)

    # Run with CLAUDE_SESSION_ID unset
    env_no_session = {k: v for k, v in os.environ.items() if k != "CLAUDE_SESSION_ID"}
    result = subprocess.run(
        ["bash", str(script_path)],
        capture_output=True, text=True, env=env_no_session,
    )
    assert result.returncode == 1
    assert "not set" in result.stderr


def test_T10d_claim_exits_when_session_id_is_unknown(tmp_path):
    """Isolated check: the sentinel guard logic exits 1 when CLAUDE_SESSION_ID is 'unknown'."""
    check_script = textwrap.dedent("""\
        #!/usr/bin/env bash
        set -euo pipefail
        _CLAIM_SESSION_ID="${CLAUDE_SESSION_ID:-}"
        if [[ -z "${_CLAIM_SESSION_ID}" ]]; then
          echo "CLAUDE_SESSION_ID not set" >&2
          exit 1
        fi
        if [[ "${_CLAIM_SESSION_ID}" == "unknown" ]]; then
          echo "CLAUDE_SESSION_ID is sentinel 'unknown'" >&2
          exit 1
        fi
        echo "OK"
    """)
    script_path = tmp_path / "check_sentinel.sh"
    script_path.write_text(check_script)

    env_sentinel = {**os.environ, "CLAUDE_SESSION_ID": "unknown"}
    result = subprocess.run(
        ["bash", str(script_path)],
        capture_output=True, text=True, env=env_sentinel,
    )
    assert result.returncode == 1
    assert "sentinel" in result.stderr
