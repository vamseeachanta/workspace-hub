from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "operations" / "relabel-agent-to-ai.sh"


def test_relabel_agent_to_ai_dry_run_maps_gemini_to_agy(tmp_path: Path) -> None:
    fake_gh = tmp_path / "gh"
    fake_gh.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$GH_CALL_LOG"
case "$*" in
  "repo list vamseeachanta --no-archived --limit 10000 --json nameWithOwner --jq .[].nameWithOwner")
    printf '%s\\n' 'vamseeachanta/workspace-hub'
    ;;
  "issue list --repo vamseeachanta/workspace-hub --state all --limit 10000 --json number,labels --jq .[] | @base64")
    printf '%s\\n' 'eyJudW1iZXIiOjEwMSwibGFiZWxzIjpbeyJuYW1lIjoiYWdlbnQ6Z2VtaW5pIn1dfQ=='
    ;;
  "pr list --repo vamseeachanta/workspace-hub --state all --limit 10000 --json number,labels --jq .[] | @base64")
    printf '%s\\n' 'eyJudW1iZXIiOjIwMiwibGFiZWxzIjpbeyJuYW1lIjoiYWdlbnQ6Y29kZXgifV19'
    ;;
  *)
    exit 99
    ;;
esac
""",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)
    call_log = tmp_path / "calls.log"
    env = os.environ | {
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "GH_CALL_LOG": str(call_log),
    }

    completed = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "DRY-RUN issue vamseeachanta/workspace-hub#101: add ai:agy remove agent:gemini" in completed.stdout
    assert "DRY-RUN pr vamseeachanta/workspace-hub#202: add ai:codex remove agent:codex" in completed.stdout
    assert "edit" not in call_log.read_text(encoding="utf-8")


def test_relabel_agent_to_ai_apply_edits_issues_and_prs(tmp_path: Path) -> None:
    fake_gh = tmp_path / "gh"
    fake_gh.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$GH_CALL_LOG"
case "$*" in
  "repo list vamseeachanta --no-archived --limit 10000 --json nameWithOwner --jq .[].nameWithOwner")
    printf '%s\\n' 'vamseeachanta/workspace-hub'
    ;;
  "issue list --repo vamseeachanta/workspace-hub --state all --limit 10000 --json number,labels --jq .[] | @base64")
    printf '%s\\n' 'eyJudW1iZXIiOjEwMSwibGFiZWxzIjpbeyJuYW1lIjoiYWdlbnQ6Y2xhdWRlIn1dfQ=='
    ;;
  "pr list --repo vamseeachanta/workspace-hub --state all --limit 10000 --json number,labels --jq .[] | @base64")
    printf '%s\\n' 'eyJudW1iZXIiOjIwMiwibGFiZWxzIjpbeyJuYW1lIjoiYWdlbnQ6Z2VtaW5pIn1dfQ=='
    ;;
  "label list --repo vamseeachanta/workspace-hub --limit 1000 --json name --jq .[].name")
    printf '%s\\n' 'ai:claude' 'ai:agy'
    ;;
  "issue edit 101 --repo vamseeachanta/workspace-hub --add-label ai:claude --remove-label agent:claude")
    ;;
  "pr edit 202 --repo vamseeachanta/workspace-hub --add-label ai:agy --remove-label agent:gemini")
    ;;
  *)
    exit 99
    ;;
esac
""",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)
    call_log = tmp_path / "calls.log"
    env = os.environ | {
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "GH_CALL_LOG": str(call_log),
    }

    completed = subprocess.run(
        ["bash", str(SCRIPT), "--apply"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    log = call_log.read_text(encoding="utf-8")
    assert "issue edit 101 --repo vamseeachanta/workspace-hub --add-label ai:claude --remove-label agent:claude" in log
    assert "pr edit 202 --repo vamseeachanta/workspace-hub --add-label ai:agy --remove-label agent:gemini" in log


def test_relabel_agent_to_ai_strips_crlf_from_python_output(tmp_path: Path) -> None:
    fake_gh = tmp_path / "gh"
    fake_gh.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$GH_CALL_LOG"
case "$*" in
  "repo list vamseeachanta --no-archived --limit 10000 --json nameWithOwner --jq .[].nameWithOwner")
    printf '%s\\n' 'vamseeachanta/workspace-hub'
    ;;
  "issue list --repo vamseeachanta/workspace-hub --state all --limit 10000 --json number,labels --jq .[] | @base64")
    printf '%s\\n' 'eyJudW1iZXIiOjEwMSwibGFiZWxzIjpbeyJuYW1lIjoiYWdlbnQ6Z2VtaW5pIn1dfQ=='
    ;;
  "pr list --repo vamseeachanta/workspace-hub --state all --limit 10000 --json number,labels --jq .[] | @base64")
    ;;
  *)
    exit 99
    ;;
esac
""",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)
    fake_python = tmp_path / "python"
    fake_python.write_text(
        """#!/usr/bin/env bash
script=$(cat)
if grep -q 'item\\["number"\\]' <<<"$script"; then
  printf '101\\r\\n'
else
  printf 'agent:gemini\\r\\n'
fi
""",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)
    call_log = tmp_path / "calls.log"
    env = os.environ | {
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "GH_CALL_LOG": str(call_log),
    }

    completed = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "DRY-RUN issue vamseeachanta/workspace-hub#101: add ai:agy remove agent:gemini" in completed.stdout
    assert "ai:gemini" not in completed.stdout


def test_relabel_agent_to_ai_skips_unknown_agent_labels(tmp_path: Path) -> None:
    fake_gh = tmp_path / "gh"
    fake_gh.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$GH_CALL_LOG"
case "$*" in
  "repo list vamseeachanta --no-archived --limit 10000 --json nameWithOwner --jq .[].nameWithOwner")
    printf '%s\\n' 'vamseeachanta/workspace-hub'
    ;;
  "issue list --repo vamseeachanta/workspace-hub --state all --limit 10000 --json number,labels --jq .[] | @base64")
    printf '%s\\n' 'eyJudW1iZXIiOjEwMSwibGFiZWxzIjpbeyJuYW1lIjoiYWdlbnQ6YW55In0seyJuYW1lIjoiYWdlbnQ6b3RoZXIifV19'
    ;;
  "pr list --repo vamseeachanta/workspace-hub --state all --limit 10000 --json number,labels --jq .[] | @base64")
    ;;
  *)
    exit 99
    ;;
esac
""",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)
    call_log = tmp_path / "calls.log"
    env = os.environ | {
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "GH_CALL_LOG": str(call_log),
    }

    completed = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "SKIP issue vamseeachanta/workspace-hub#101: unsupported legacy label agent:any" in completed.stdout
    assert "SKIP issue vamseeachanta/workspace-hub#101: unsupported legacy label agent:other" in completed.stdout
    assert "add ai:any" not in completed.stdout
    assert "add ai:other" not in completed.stdout
    assert "edit" not in call_log.read_text(encoding="utf-8")


def test_relabel_agent_to_ai_apply_skips_missing_target_labels(tmp_path: Path) -> None:
    fake_gh = tmp_path / "gh"
    fake_gh.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$GH_CALL_LOG"
case "$*" in
  "repo list vamseeachanta --no-archived --limit 10000 --json nameWithOwner --jq .[].nameWithOwner")
    printf '%s\\n' 'vamseeachanta/workspace-hub'
    ;;
  "label list --repo vamseeachanta/workspace-hub --limit 1000 --json name --jq .[].name")
    printf '%s\\n' 'ai:claude'
    ;;
  "issue list --repo vamseeachanta/workspace-hub --state all --limit 10000 --json number,labels --jq .[] | @base64")
    printf '%s\\n' 'eyJudW1iZXIiOjEwMSwibGFiZWxzIjpbeyJuYW1lIjoiYWdlbnQ6Y29kZXgifV19'
    ;;
  "pr list --repo vamseeachanta/workspace-hub --state all --limit 10000 --json number,labels --jq .[] | @base64")
    ;;
  *)
    exit 99
    ;;
esac
""",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)
    call_log = tmp_path / "calls.log"
    env = os.environ | {
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "GH_CALL_LOG": str(call_log),
    }

    completed = subprocess.run(
        ["bash", str(SCRIPT), "--apply"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "SKIP issue vamseeachanta/workspace-hub#101: target label ai:codex missing in repo" in completed.stdout
    log = call_log.read_text(encoding="utf-8")
    assert "label list --repo vamseeachanta/workspace-hub" in log
    assert "issue edit" not in log
