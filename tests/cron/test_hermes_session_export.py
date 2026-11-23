"""Checks for Hermes session export correction tracking (#1745)."""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "hermes-session-export.sh"


def test_hermes_export_mentions_corrections_log_output():
    text = SCRIPT.read_text()
    assert 'logs/orchestrator/hermes/corrections' in text or 'CORRECTIONS_DIR' in text


def test_hermes_export_tracks_repeated_file_edits_as_corrections():
    text = SCRIPT.read_text()
    assert 'correction_gap_seconds' in text
    assert 'type' in text and 'correction' in text


def test_hermes_export_reclassifies_session_search_and_skills_list() -> None:
    text = SCRIPT.read_text()
    assert "'skills_list': 'ToolSearch'" in text
    assert "'session_search': 'Grep'" in text
    assert "entry['search_query']" in text
    assert "entry['skill_category']" in text


def test_hermes_export_includes_session_id() -> None:
    text = SCRIPT.read_text()
    assert "session_id = session.get('session_id', '')" in text
    assert "'session_id': session_id" in text


def test_hermes_export_all_clears_previous_jsonl_outputs() -> None:
    text = SCRIPT.read_text()
    assert 'if [[ "$EXPORT_ALL" == "true" && "$DRY_RUN" == "false" ]]; then' in text
    assert 'rm -f "$OUTPUT_DIR"/session_*.jsonl "$CORRECTIONS_DIR"/session_*.jsonl "$STATE_FILE"' in text


def _write_fake_uv(tmp_path: Path) -> tuple[Path, Path]:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    uv_log = tmp_path / "uv-args.txt"
    fake_uv = fake_bin / "uv"
    fake_uv.write_text(
        "#!/usr/bin/env python3\n"
        "import os\n"
        "import subprocess\n"
        "import sys\n"
        "from pathlib import Path\n"
        "log_path = os.environ['UV_ARGS_FILE']\n"
        "Path(log_path).write_text('\\n'.join(sys.argv[1:]) + '\\n', encoding='utf-8')\n"
        "args = sys.argv[1:]\n"
        "assert args[:3] == ['run', '--no-project', 'python'], args\n"
        "proc = subprocess.run([sys.executable] + args[3:], stdin=sys.stdin.buffer)\n"
        "sys.exit(proc.returncode)\n",
        encoding="utf-8",
    )
    fake_uv.chmod(fake_uv.stat().st_mode | stat.S_IEXEC)
    return fake_bin, uv_log


def test_hermes_export_subprocess_exports_records_and_correction_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo-under-test"
    (repo / "scripts" / "cron").mkdir(parents=True)
    shutil.copy2(SCRIPT, repo / "scripts" / "cron" / "hermes-session-export.sh")

    home = tmp_path / "home"
    sessions_dir = home / ".hermes" / "sessions"
    sessions_dir.mkdir(parents=True)
    fake_bin, uv_log = _write_fake_uv(tmp_path)

    session_file = sessions_dir / "session_20260410_140000_abc.json"
    session_file.write_text(
        json.dumps(
            {
                "session_start": "2026-04-10T14:00:00Z",
                "model": "hermes-3",
                "session_id": "sess-1",
                "messages": [
                    {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "function": {
                                    "name": "terminal",
                                    "arguments": json.dumps({"command": "git status --short"}),
                                }
                            },
                            {
                                "function": {
                                    "name": "patch",
                                    "arguments": json.dumps({"path": "src/app.py"}),
                                }
                            },
                            {
                                "function": {
                                    "name": "patch",
                                    "arguments": json.dumps({"path": "src/app.py"}),
                                }
                            },
                            {
                                "function": {
                                    "name": "session_search",
                                    "arguments": json.dumps({"query": "bug", "role_filter": "assistant", "limit": 5}),
                                }
                            },
                            {
                                "function": {
                                    "name": "skills_list",
                                    "arguments": json.dumps({"category": "testing"}),
                                }
                            },
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["HOME"] = str(home)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    env["UV_ARGS_FILE"] = str(uv_log)

    script_path = repo / "scripts" / "cron" / "hermes-session-export.sh"
    result = subprocess.run(
        ["bash", str(script_path)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Hermes session export: 1 exported, 0 skipped" in result.stdout

    output_file = repo / "logs" / "orchestrator" / "hermes" / "session_20260410.jsonl"
    corrections_file = repo / "logs" / "orchestrator" / "hermes" / "corrections" / "session_20260410.jsonl"
    assert output_file.exists()
    assert corrections_file.exists()

    records = [json.loads(line) for line in output_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(records) == 5

    terminal_record = next(r for r in records if r["hermes_tool"] == "terminal")
    assert terminal_record["tool"] == "Bash"
    assert terminal_record["cmd"] == "git status --short"
    assert terminal_record["session_id"] == "sess-1"

    session_search_record = next(r for r in records if r["hermes_tool"] == "session_search")
    assert session_search_record["tool"] == "Grep"
    assert session_search_record["file"] == "__session_history__"
    assert session_search_record["search_query"] == "bug"
    assert session_search_record["role_filter"] == "assistant"
    assert session_search_record["limit"] == 5

    skills_list_record = next(r for r in records if r["hermes_tool"] == "skills_list")
    assert skills_list_record["tool"] == "ToolSearch"
    assert skills_list_record["file"] == "testing"
    assert skills_list_record["skill_category"] == "testing"

    correction_records = [json.loads(line) for line in corrections_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(correction_records) == 1
    correction = correction_records[0]
    assert correction["type"] == "correction"
    assert correction["file"] == "src/app.py"
    assert correction["basename"] == "app.py"
    assert correction["tool"] == "Edit"
    assert correction["file_extension"] == "py"
    assert correction["chain_files"] == ["src/app.py"]

    uv_args = uv_log.read_text(encoding="utf-8").splitlines()
    assert uv_args[:4] == ["run", "--no-project", "python", "-"]


def _isolated_exporter(tmp_path: Path) -> tuple[Path, Path, dict[str, str], Path]:
    repo = tmp_path / "repo-under-test"
    script_dir = repo / "scripts" / "cron"
    script_dir.mkdir(parents=True)
    shutil.copy2(SCRIPT, script_dir / SCRIPT.name)
    home = tmp_path / "user-config"
    inputs = home / ".hermes" / "sessions"
    inputs.mkdir(parents=True)
    fake_bin, uv_log = _write_fake_uv(tmp_path)
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    env["HOME"] = str(home)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    env["UV_ARGS_FILE"] = str(uv_log)
    return repo, inputs, env, uv_log


def _run_isolated_exporter(repo: Path, env: dict[str, str], dry_run: bool = False):
    args = ["bash", "-euo", "pipefail", str(repo / "scripts" / "cron" / SCRIPT.name)]
    if dry_run:
        args.append("--dry-run")
    return subprocess.run(args, cwd=repo, env=env, capture_output=True, text=True, check=False)


# Counts below are hand calculated from each synthetic input set: one unsupported
# file yields zero exports and one skip; adding one valid file yields one export.
# The date and terminal mapping use the existing subprocess fixture above.
@pytest.mark.parametrize("dry_run", [False, True], ids=["export", "dry-run"])
def test_undated_filename_is_skipped(tmp_path: Path, dry_run: bool) -> None:
    repo, inputs, env, uv_log = _isolated_exporter(tmp_path)
    (inputs / "session_000_undated.json").write_text("{}", encoding="utf-8")

    result = _run_isolated_exporter(repo, env, dry_run)

    assert result.returncode == 0, result.stderr
    assert "Hermes session export: 0 exported, 1 skipped" in result.stdout
    output = repo / "logs" / "orchestrator" / "hermes"
    assert not list(output.rglob("*.jsonl"))
    assert not (output / ".last-export-ts").exists()
    assert not uv_log.exists()


@pytest.mark.parametrize("dry_run", [False, True], ids=["export", "dry-run"])
def test_mixed_filenames_export_valid_session(tmp_path: Path, dry_run: bool) -> None:
    repo, inputs, env, uv_log = _isolated_exporter(tmp_path)
    # This sorts before the dated input, so continuing the loop is required.
    (inputs / "session_000_undated.json").write_text("{}", encoding="utf-8")
    (inputs / "session_20260410_140000_abc.json").write_text(
        json.dumps({
            "messages": [{
                "role": "assistant",
                "tool_calls": [{
                    "function": {
                        "name": "terminal",
                        "arguments": json.dumps({"command": "true"}),
                    },
                }],
            }],
        }),
        encoding="utf-8",
    )
    output = repo / "logs" / "orchestrator" / "hermes"
    output.mkdir(parents=True)
    state = output / ".last-export-ts"
    # Zero is an epoch sentinel earlier than these newly created fixture files.
    state.write_text("0\n", encoding="utf-8")

    result = _run_isolated_exporter(repo, env, dry_run)

    assert result.returncode == 0, result.stderr
    assert "Hermes session export: 1 exported, 1 skipped" in result.stdout
    if dry_run:
        assert "[dry-run] Would export" in result.stdout
        assert not list(output.rglob("*.jsonl"))
        assert state.read_text(encoding="utf-8") == "0\n"
        assert not uv_log.exists()
    else:
        records = [
            json.loads(line)
            for line in (output / "session_20260410.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        # Exactly one terminal call was supplied; no correction or other output.
        assert len(records) == 1
        assert records[0]["tool"] == "Bash"
        assert records[0]["hermes_tool"] == "terminal"
        assert records[0]["cmd"] == "true"
        assert records[0]["ts"] == ""
        assert list(output.rglob("*.jsonl")) == [output / "session_20260410.jsonl"]
        assert state.read_text(encoding="utf-8").strip().isdigit()
        assert state.read_text(encoding="utf-8") != "0\n"
        assert uv_log.read_text(encoding="utf-8").splitlines()[:4] == [
            "run", "--no-project", "python", "-"
        ]


# Characterize existing conversion semantics: invalid JSON exits successfully,
# while non-iterable messages raise an error. The shell suppresses both errors,
# but only successful conversion advances the export count and timestamp.
@pytest.mark.parametrize(
    ("payload", "exported"),
    [("{", 1), ('{"messages": null}', 0)],
    ids=["invalid-json", "invalid-messages"],
)
def test_malformed_dated_input_preserves_existing_behavior(
    tmp_path: Path, payload: str, exported: int
) -> None:
    repo, inputs, env, uv_log = _isolated_exporter(tmp_path)
    (inputs / "session_20260410_140000_abc.json").write_text(payload, encoding="utf-8")
    output = repo / "logs" / "orchestrator" / "hermes"
    output.mkdir(parents=True)
    state = output / ".last-export-ts"
    state.write_text("0\n", encoding="utf-8")

    result = _run_isolated_exporter(repo, env)

    assert result.returncode == 0, result.stderr
    assert f"Hermes session export: {exported} exported, 0 skipped" in result.stdout
    assert not list(output.rglob("*.jsonl"))
    assert uv_log.exists()
    if exported:
        assert state.read_text(encoding="utf-8").strip().isdigit()
        assert state.read_text(encoding="utf-8") != "0\n"
    else:
        assert state.read_text(encoding="utf-8") == "0\n"
