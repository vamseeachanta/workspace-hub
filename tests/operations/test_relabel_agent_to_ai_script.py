from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "operations" / "relabel-agent-to-ai.sh"
REPO = "vamseeachanta/workspace-hub"


def _item(number: int, labels: list[str]) -> str:
    payload = {"number": number, "labels": [{"name": label} for label in labels]}
    return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")


def _case(pattern: str, body: str) -> str:
    return f'  "{pattern}")\n{body}\n    ;;\n'


def _fake_gh(tmp_path: Path, cases: list[tuple[str, str]]) -> None:
    script = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        'printf "%s\\n" "$*" >> "$GH_CALL_LOG"',
        'case "$*" in',
    ]
    script.extend(_case(pattern, body) for pattern, body in cases)
    script.append("  *)\n    exit 99\n    ;;\nesac\n")
    fake_gh = tmp_path / "gh"
    fake_gh.write_text("\n".join(script), encoding="utf-8")
    fake_gh.chmod(0o755)


def _run(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ | {
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "GH_CALL_LOG": str(tmp_path / "calls.log"),
    }
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _calls(tmp_path: Path) -> str:
    return (tmp_path / "calls.log").read_text(encoding="utf-8")


def _common_cases(*, labels: str = "", open_issues: str = "", open_prs: str = "") -> list[tuple[str, str]]:
    return [
        (
            "repo list vamseeachanta --no-archived --limit 10000 --json nameWithOwner --jq .[].nameWithOwner",
            f"    printf '%s\\n' '{REPO}'",
        ),
        (
            f"label list --repo {REPO} --limit 1000 --json name --jq .[].name",
            labels or "    :",
        ),
        (
            f"issue list --repo {REPO} --state open --limit 10000 --json number,labels --jq .[] | @base64",
            open_issues or "    :",
        ),
        (
            f"pr list --repo {REPO} --state open --limit 10000 --json number,labels --jq .[] | @base64",
            open_prs or "    :",
        ),
    ]


def test_apply_open_codex_without_lane_adds_lane_codex(tmp_path: Path) -> None:
    _fake_gh(
        tmp_path,
        [
            *_common_cases(
                labels="    printf '%s\\n' 'lane:codex'",
                open_issues=f"    printf '%s\\n' '{_item(101, ['agent:codex'])}'",
            ),
            (f"issue edit 101 --repo {REPO} --add-label lane:codex --remove-label agent:codex", "    :"),
        ],
    )

    completed = _run(tmp_path, "--apply")

    assert completed.returncode == 0, completed.stderr
    assert f"APPLY issue {REPO}#101: add lane:codex remove agent:codex" in completed.stdout
    assert f"issue edit 101 --repo {REPO} --add-label lane:codex --remove-label agent:codex" in _calls(tmp_path)
    assert "--state closed" not in _calls(tmp_path)
    assert "ai:" not in completed.stdout


def test_apply_open_existing_lane_wins_and_only_agent_label_is_removed(tmp_path: Path) -> None:
    _fake_gh(
        tmp_path,
        [
            *_common_cases(
                labels="    printf '%s\\n' 'lane:codex' 'lane:claude'",
                open_issues=f"    printf '%s\\n' '{_item(101, ['agent:codex', 'lane:claude'])}'",
            ),
            (f"issue edit 101 --repo {REPO} --remove-label agent:codex", "    :"),
        ],
    )

    completed = _run(tmp_path, "--apply")

    assert completed.returncode == 0, completed.stderr
    assert f"CONFLICT issue {REPO}#101: existing lane label lane:claude wins; remove agent:codex" in completed.stdout
    log = _calls(tmp_path)
    assert f"issue edit 101 --repo {REPO} --remove-label agent:codex" in log
    assert "--add-label" not in log


def test_apply_open_agy_removes_agent_label_and_reports_unmapped(tmp_path: Path) -> None:
    _fake_gh(
        tmp_path,
        [
            *_common_cases(open_issues=f"    printf '%s\\n' '{_item(101, ['agent:agy'])}'"),
            (f"issue edit 101 --repo {REPO} --remove-label agent:agy", "    :"),
        ],
    )

    completed = _run(tmp_path, "--apply")

    assert completed.returncode == 0, completed.stderr
    assert f"UNMAPPED issue {REPO}#101: remove agent:agy; no lane added for open item" in completed.stdout
    assert f"issue edit 101 --repo {REPO} --remove-label agent:agy" in _calls(tmp_path)
    assert "lane:" not in completed.stdout
    assert "ai:" not in completed.stdout


def test_include_closed_maps_closed_gemini_to_ai_agy(tmp_path: Path) -> None:
    _fake_gh(
        tmp_path,
        [
            *_common_cases(labels="    printf '%s\\n' 'ai:agy'"),
            (
                f"issue list --repo {REPO} --state closed --limit 10000 --json number,labels --jq .[] | @base64",
                f"    printf '%s\\n' '{_item(303, ['agent:gemini'])}'",
            ),
            (f"pr list --repo {REPO} --state closed --limit 10000 --json number,labels --jq .[] | @base64", "    :"),
            (f"issue edit 303 --repo {REPO} --add-label ai:agy --remove-label agent:gemini", "    :"),
        ],
    )

    completed = _run(tmp_path, "--apply", "--include-closed")

    assert completed.returncode == 0, completed.stderr
    assert f"APPLY issue {REPO}#303: add ai:agy remove agent:gemini" in completed.stdout
    assert f"issue edit 303 --repo {REPO} --add-label ai:agy --remove-label agent:gemini" in _calls(tmp_path)
    assert "lane:" not in completed.stdout


def test_default_run_never_touches_closed_items(tmp_path: Path) -> None:
    _fake_gh(tmp_path, _common_cases())

    completed = _run(tmp_path, "--apply")

    assert completed.returncode == 0, completed.stderr
    assert "--state closed" not in _calls(tmp_path)
    assert "edit" not in _calls(tmp_path)


def test_open_only_flag_is_explicit_default(tmp_path: Path) -> None:
    _fake_gh(tmp_path, _common_cases())

    completed = _run(tmp_path, "--open-only")

    assert completed.returncode == 0, completed.stderr
    assert "--state open" in _calls(tmp_path)
    assert "--state closed" not in _calls(tmp_path)


def test_dry_run_reports_missing_open_lane_label(tmp_path: Path) -> None:
    _fake_gh(
        tmp_path,
        _common_cases(
            labels="    printf '%s\\n' 'lane:claude'",
            open_issues=f"    printf '%s\\n' '{_item(101, ['agent:codex'])}'",
        ),
    )

    completed = _run(tmp_path)

    assert completed.returncode != 0
    assert f"SKIP issue {REPO}#101: target label lane:codex missing in repo" in completed.stdout
    assert "Summary: repos OK=0 skipped=1 failed=0" in completed.stdout
    assert "issue edit" not in _calls(tmp_path)


def test_include_closed_reports_missing_ai_target_and_continues(tmp_path: Path) -> None:
    repo_b = "vamseeachanta/repo-b"
    _fake_gh(
        tmp_path,
        [
            (
                "repo list vamseeachanta --no-archived --limit 10000 --json nameWithOwner --jq .[].nameWithOwner",
                f"    printf '%s\\n' '{REPO}' '{repo_b}'",
            ),
            (f"label list --repo {REPO} --limit 1000 --json name --jq .[].name", "    :"),
            (f"issue list --repo {REPO} --state open --limit 10000 --json number,labels --jq .[] | @base64", "    :"),
            (f"pr list --repo {REPO} --state open --limit 10000 --json number,labels --jq .[] | @base64", "    :"),
            (
                f"issue list --repo {REPO} --state closed --limit 10000 --json number,labels --jq .[] | @base64",
                f"    printf '%s\\n' '{_item(101, ['agent:gemini'])}'",
            ),
            (f"pr list --repo {REPO} --state closed --limit 10000 --json number,labels --jq .[] | @base64", "    :"),
            (f"label list --repo {repo_b} --limit 1000 --json name --jq .[].name", "    printf '%s\\n' 'lane:claude'"),
            (
                f"issue list --repo {repo_b} --state open --limit 10000 --json number,labels --jq .[] | @base64",
                f"    printf '%s\\n' '{_item(201, ['agent:claude'])}'",
            ),
            (f"pr list --repo {repo_b} --state open --limit 10000 --json number,labels --jq .[] | @base64", "    :"),
            (f"issue list --repo {repo_b} --state closed --limit 10000 --json number,labels --jq .[] | @base64", "    :"),
            (f"pr list --repo {repo_b} --state closed --limit 10000 --json number,labels --jq .[] | @base64", "    :"),
            (f"issue edit 201 --repo {repo_b} --add-label lane:claude --remove-label agent:claude", "    :"),
        ],
    )

    completed = _run(tmp_path, "--apply", "--include-closed")

    assert completed.returncode != 0
    assert f"SKIP issue {REPO}#101: target label ai:agy missing in repo" in completed.stdout
    assert f"APPLY issue {repo_b}#201: add lane:claude remove agent:claude" in completed.stdout
    assert "Summary: repos OK=1 skipped=1 failed=0" in completed.stdout


def test_strips_crlf_from_python_output(tmp_path: Path) -> None:
    _fake_gh(
        tmp_path,
        [
            *_common_cases(
                labels="    printf '%s\\n' 'lane:codex'",
                open_issues=f"    printf '%s\\n' '{_item(101, ['agent:codex'])}'",
            ),
        ],
    )
    fake_python = tmp_path / "python3"
    fake_python.write_text(
        """#!/usr/bin/env bash
script=$(cat)
if grep -q 'item\\["number"\\]' <<<"$script"; then
  printf '101\\r\\n'
elif grep -q 'startswith("lane:")' <<<"$script"; then
  :
else
  printf 'agent:codex\\r\\n'
fi
""",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)

    completed = _run(tmp_path)

    assert completed.returncode == 0, completed.stderr
    assert f"DRY-RUN issue {REPO}#101: add lane:codex remove agent:codex" in completed.stdout


def test_exits_before_gh_when_python_missing(tmp_path: Path) -> None:
    _fake_gh(tmp_path, [])
    minimal_path = tmp_path / "bin"
    minimal_path.mkdir()
    bash_path = shutil.which("bash")
    assert bash_path is not None
    (minimal_path / "bash").symlink_to(bash_path)
    for tool in ("cat", "chmod", "env", "printf", "test", "true"):
        tool_path = shutil.which(tool)
        if tool_path is not None:
            (minimal_path / tool).symlink_to(tool_path)

    env = {
        "PATH": f"{tmp_path}:{minimal_path}",
        "GH_CALL_LOG": str(tmp_path / "calls.log"),
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

    assert completed.returncode == 2
    assert "python3 or python is required" in completed.stderr
    assert not (tmp_path / "calls.log").exists()
