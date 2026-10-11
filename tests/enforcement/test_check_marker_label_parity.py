from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/enforcement/check-marker-label-parity.sh"


def _bash() -> str:
    if sys.platform == "win32":
        native = Path(os.environ["ProgramFiles"]) / "Git/bin/bash.exe"
        assert native.is_file(), "Native Git Bash is required for Windows hook tests"
        return str(native)
    bash = shutil.which("bash")
    assert bash
    return bash


def _write_gh_stub(tmp_path: Path, body: str) -> Path:
    stub_dir = tmp_path / "bin"
    stub_dir.mkdir()
    gh = stub_dir / "gh"
    gh.write_text(body)
    gh.chmod(0o755)
    return stub_dir


def _run_with_stub(tmp_path: Path, stub_body: str, issue: str = "3999") -> subprocess.CompletedProcess[str]:
    stub_dir = _write_gh_stub(tmp_path, stub_body)
    env = {
        **os.environ,
        "PATH": f"{stub_dir}{os.pathsep}{os.environ.get('PATH', '')}",
        "GITHUB_REPOSITORY": "example/project",
    }
    return subprocess.run(
        [_bash(), str(SCRIPT), "--strict", "--issue", issue],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )


def _stub(label_json: str, timeline_json: str) -> str:
    return textwrap.dedent(
        f"""\
        #!/usr/bin/env bash
        set -euo pipefail

        if [[ "${{1:-}}" == "auth" && "${{2:-}}" == "status" ]]; then
          exit 0
        fi

        if [[ "${{1:-}}" == "issue" && "${{2:-}}" == "view" ]]; then
          cat <<'JSON'
        {label_json}
        JSON
          exit 0
        fi

        if [[ "${{1:-}}" == "api" ]]; then
          cat <<'JSON'
        {timeline_json}
        JSON
          exit 0
        fi

        echo "unexpected gh invocation: $*" >&2
        exit 1
        """
    )


def test_status_plan_approved_set_by_bot_fails(tmp_path: Path):
    result = _run_with_stub(
        tmp_path,
        _stub(
            '{"labels":[{"name":"status:plan-approved"}]}',
            '[{"event":"labeled","label":{"name":"status:plan-approved"},"actor":{"login":"queue-bot[bot]","type":"Bot"}}]',
        ),
    )
    assert result.returncode == 1
    assert "set by bot" in result.stdout


def test_status_plan_approved_set_by_user_passes(tmp_path: Path):
    result = _run_with_stub(
        tmp_path,
        _stub(
            '{"labels":[{"name":"status:plan-approved"}]}',
            '[{"event":"labeled","label":{"name":"status:plan-approved"},"actor":{"login":"reviewer","type":"User"}}]',
        ),
    )
    assert result.returncode == 0
    assert "set by reviewer" in result.stdout


def test_paginated_timeline_uses_latest_status_label_event(tmp_path: Path):
    result = _run_with_stub(
        tmp_path,
        _stub(
            '{"labels":[{"name":"status:plan-approved"}]}',
            """[
              [{"event":"labeled","label":{"name":"status:plan-approved"},"actor":{"login":"queue-bot[bot]","type":"Bot"}}],
              [{"event":"labeled","label":{"name":"status:plan-approved"},"actor":{"login":"reviewer","type":"User"}}]
            ]""",
        ),
    )
    assert result.returncode == 0
    assert "set by reviewer" in result.stdout


def test_issue_without_status_plan_approved_label_passes(tmp_path: Path):
    result = _run_with_stub(
        tmp_path,
        _stub('{"labels":[{"name":"dispatch:ready"}]}', "[]"),
    )
    assert result.returncode == 0
    assert "label absent" in result.stdout


def test_missing_gh_fails_in_strict_issue_mode(tmp_path: Path):
    env = {**os.environ, "PATH": ""}
    result = subprocess.run(
        [_bash(), str(SCRIPT), "--strict", "--issue", "3999"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "gh CLI not found" in result.stderr
