from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "codex-session-export.sh"


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


def test_codex_export_subprocess_exports_once_and_dedupes_mutated_session_on_rerun(tmp_path: Path) -> None:
    repo = tmp_path / "repo-under-test"
    (repo / "scripts" / "cron").mkdir(parents=True)
    shutil.copy2(SCRIPT, repo / "scripts" / "cron" / "codex-session-export.sh")

    home = tmp_path / "home"
    codex_dir = home / ".codex" / "sessions" / "2026" / "04" / "10"
    codex_dir.mkdir(parents=True)
    fake_bin, uv_log = _write_fake_uv(tmp_path)

    session_file = codex_dir / "rollout-abc.jsonl"
    base_lines = [
        json.dumps(
            {
                "timestamp": "2026-04-10T14:00:00Z",
                "type": "session_meta",
                "payload": {"id": "sess-1", "cwd": "/tmp/project", "model_provider": "openai"},
            }
        ),
        json.dumps(
            {
                "timestamp": "2026-04-10T14:01:00Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "id": "call-1",
                    "name": "exec_command",
                    "arguments": json.dumps({"command": "git status --short"}),
                },
            }
        ),
        json.dumps(
            {
                "timestamp": "2026-04-10T14:02:00Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "id": "call-2",
                    "name": "read_file",
                    "arguments": json.dumps({"path": "src/app.py"}),
                },
            }
        ),
        json.dumps(
            {
                "timestamp": "2026-04-10T14:03:00Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "id": "call-3",
                    "name": "apply_diff",
                    "arguments": json.dumps({"file_path": "src/app.py"}),
                },
            }
        ),
    ]
    session_file.write_text("\n".join(base_lines) + "\n", encoding="utf-8")

    env = os.environ.copy()
    env["HOME"] = str(home)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    env["UV_ARGS_FILE"] = str(uv_log)

    script_path = repo / "scripts" / "cron" / "codex-session-export.sh"

    first = subprocess.run(
        ["bash", str(script_path)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert first.returncode == 0, f"stdout: {first.stdout}\nstderr: {first.stderr}"
    assert "Codex session export: 3 records exported from 1 matching sessions, 0 skipped" in first.stdout

    output_file = repo / "logs" / "orchestrator" / "codex" / "session_20260410.jsonl"
    assert output_file.exists()

    records = [json.loads(line) for line in output_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(records) == 3

    bash_record = next(r for r in records if r["codex_tool"] == "exec_command")
    assert bash_record["tool"] == "Bash"
    assert bash_record["cmd"] == "git status --short"
    assert bash_record["session_id"] == "sess-1"
    assert bash_record["model"] == "openai"
    assert bash_record["tool_call_id"] == "call-1"
    assert bash_record["native_session_file"].endswith("rollout-abc.jsonl")

    read_record = next(r for r in records if r["codex_tool"] == "read_file")
    assert read_record["tool"] == "Read"
    assert read_record["file"] == "src/app.py"

    edit_record = next(r for r in records if r["codex_tool"] == "apply_diff")
    assert edit_record["tool"] == "Edit"
    assert edit_record["file"] == "src/app.py"

    state_file = repo / "logs" / "orchestrator" / "codex" / ".export-state.json"
    assert state_file.exists()
    state = json.loads(state_file.read_text(encoding="utf-8"))
    session_state = state["sessions"][str(session_file)]
    assert session_state["exported_tool_call_ids"] == ["call-1", "call-2", "call-3"]

    uv_args = uv_log.read_text(encoding="utf-8").splitlines()
    assert uv_args[:4] == ["run", "--no-project", "python", "-"]

    original_lines = output_file.read_text(encoding="utf-8").splitlines()

    session_file.write_text(
        "\n".join(
            base_lines
            + [
                json.dumps(
                    {
                        "timestamp": "2026-04-10T14:04:00Z",
                        "type": "response_item",
                        "payload": {
                            "type": "function_call",
                            "id": "call-4",
                            "name": "search_files",
                            "arguments": json.dumps({"pattern": "TODO", "path": "src"}),
                        },
                    }
                )
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    second = subprocess.run(
        ["bash", str(script_path)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert second.returncode == 0, f"stdout: {second.stdout}\nstderr: {second.stderr}"
    assert "Codex session export: 1 records exported from 1 matching sessions, 0 skipped" in second.stdout

    updated_records = [json.loads(line) for line in output_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(updated_records) == 4
    assert output_file.read_text(encoding="utf-8").splitlines()[:3] == original_lines

    grep_record = next(r for r in updated_records if r["codex_tool"] == "search_files")
    assert grep_record["tool"] == "Grep"
    assert grep_record["query"] == "TODO"
    assert grep_record["search_root"] == "src"
    assert grep_record["tool_call_id"] == "call-4"
