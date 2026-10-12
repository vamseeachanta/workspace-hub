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


def _run_with_stub(
    tmp_path: Path,
    stub_body: str,
    issue: str = "3999",
    *extra_args: str,
) -> subprocess.CompletedProcess[str]:
    stub_dir = _write_gh_stub(tmp_path, stub_body)
    env = {
        **os.environ,
        "PATH": f"{stub_dir}{os.pathsep}{os.environ.get('PATH', '')}",
        "GITHUB_REPOSITORY": "example/project",
    }
    return subprocess.run(
        [_bash(), str(SCRIPT), "--strict", "--issue", issue, *extra_args],
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


def _recording_stub(label_json: str, timeline_json: str, log_path: Path) -> str:
    return textwrap.dedent(
        f"""\
        #!/usr/bin/env bash
        set -euo pipefail
        printf '%s\\n' "$*" >> {log_path}

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


def test_cross_repository_reference_uses_named_repository(tmp_path: Path):
    log_path = tmp_path / "gh.log"
    result = _run_with_stub(
        tmp_path,
        _recording_stub('{"labels":[{"name":"dispatch:ready"}]}', "[]", log_path),
        "other/project#3999",
    )
    assert result.returncode == 0
    log = log_path.read_text()
    assert "issue view 3999 --repo other/project --json labels" in log
    assert "api repos/other/project/issues/3999/timeline" not in log


def test_label_read_api_failure_fails_closed(tmp_path: Path):
    result = _run_with_stub(
        tmp_path,
        textwrap.dedent(
            """\
            #!/usr/bin/env bash
            set -euo pipefail
            if [[ "${1:-}" == "auth" && "${2:-}" == "status" ]]; then
              exit 0
            fi
            if [[ "${1:-}" == "issue" && "${2:-}" == "view" ]]; then
              echo "not found" >&2
              exit 1
            fi
            exit 1
            """
        ),
    )
    assert result.returncode == 1
    assert "could not read labels" in result.stdout
    assert "failing closed" in result.stdout


def test_timeline_api_failure_fails_closed(tmp_path: Path):
    result = _run_with_stub(
        tmp_path,
        textwrap.dedent(
            """\
            #!/usr/bin/env bash
            set -euo pipefail
            if [[ "${1:-}" == "auth" && "${2:-}" == "status" ]]; then
              exit 0
            fi
            if [[ "${1:-}" == "issue" && "${2:-}" == "view" ]]; then
              echo '{"labels":[{"name":"status:plan-approved"}]}'
              exit 0
            fi
            if [[ "${1:-}" == "api" ]]; then
              echo "api unavailable" >&2
              exit 1
            fi
            exit 1
            """
        ),
    )
    assert result.returncode == 1
    assert "could not read timeline" in result.stdout
    assert "failing closed" in result.stdout


def test_label_present_without_actor_fails_closed(tmp_path: Path):
    result = _run_with_stub(
        tmp_path,
        _stub(
            '{"labels":[{"name":"status:plan-approved"}]}',
            '[{"event":"labeled","label":{"name":"status:plan-approved"},"actor":null}]',
        ),
    )
    assert result.returncode == 1
    assert "no label-setter could be determined" in result.stdout


def test_no_issue_referenced_fails_when_required_in_strict_mode(tmp_path: Path):
    result = _run_with_stub(
        tmp_path,
        _stub('{"labels":[]}', "[]"),
        "",
        "--require-issue-reference",
        "--issues",
        "",
    )
    assert result.returncode == 1
    assert "no issue referenced" in result.stdout


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
