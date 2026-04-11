from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "codex-session-export.sh"
PY_RESOLVER = REPO_ROOT / "scripts" / "lib" / "python-resolver.sh"


def _write_fake_python3(tmp_path: Path) -> tuple[Path, Path]:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    py_log = tmp_path / "python3-args.txt"
    fake_py = fake_bin / "python3"
    fake_py.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\n' \"$@\" > \"${PY_LOG}\"\n"
        "exec /usr/bin/python3 \"$@\"\n",
        encoding="utf-8",
    )
    fake_py.chmod(fake_py.stat().st_mode | stat.S_IEXEC)
    return fake_bin, py_log


def test_codex_export_subprocess_exports_once_and_skips_on_rerun(tmp_path: Path) -> None:
    repo = tmp_path / "repo-under-test"
    (repo / "scripts" / "cron").mkdir(parents=True)
    (repo / "scripts" / "lib").mkdir(parents=True)
    shutil.copy2(SCRIPT, repo / "scripts" / "cron" / "codex-session-export.sh")
    shutil.copy2(PY_RESOLVER, repo / "scripts" / "lib" / "python-resolver.sh")

    home = tmp_path / "home"
    codex_dir = home / ".codex" / "sessions" / "2026" / "04" / "10"
    codex_dir.mkdir(parents=True)
    fake_bin, py_log = _write_fake_python3(tmp_path)

    session_file = codex_dir / "rollout-abc.jsonl"
    session_file.write_text(
        "\n".join(
            [
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
                            "name": "apply_diff",
                            "arguments": json.dumps({"file_path": "src/app.py"}),
                        },
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["HOME"] = str(home)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    env["PY_LOG"] = str(py_log)

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
    assert "Codex session export: 1 exported, 0 skipped" in first.stdout

    output_file = repo / "logs" / "orchestrator" / "codex" / "session_20260410.jsonl"
    assert output_file.exists()

    records = [json.loads(line) for line in output_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(records) == 3

    bash_record = next(r for r in records if r["codex_tool"] == "exec_command")
    assert bash_record["tool"] == "Bash"
    assert bash_record["cmd"] == "git status --short"
    assert bash_record["session_id"] == "sess-1"
    assert bash_record["model"] == "openai"

    read_record = next(r for r in records if r["codex_tool"] == "read_file")
    assert read_record["tool"] == "Read"
    assert read_record["file"] == "src/app.py"

    edit_record = next(r for r in records if r["codex_tool"] == "apply_diff")
    assert edit_record["tool"] == "Edit"
    assert edit_record["file"] == "src/app.py"

    state_file = repo / "logs" / "orchestrator" / "codex" / ".last-export-ts"
    assert state_file.exists()
    assert py_log.read_text(encoding="utf-8").splitlines()[0] == "-c"

    original_lines = output_file.read_text(encoding="utf-8").splitlines()

    second = subprocess.run(
        ["bash", str(script_path)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert second.returncode == 0, f"stdout: {second.stdout}\nstderr: {second.stderr}"
    assert "Codex session export: 0 exported, 1 skipped" in second.stdout
    assert output_file.read_text(encoding="utf-8").splitlines() == original_lines
