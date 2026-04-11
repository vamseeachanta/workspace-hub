from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "gemini-session-export.sh"
NIGHTLY = REPO_ROOT / "scripts" / "cron" / "comprehensive-learning-nightly.sh"
README = REPO_ROOT / "logs" / "orchestrator" / "README.md"


def test_gemini_export_script_exists_and_targets_session_jsonl() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    assert "logs/orchestrator/gemini" in text
    assert "session_" in text and ".jsonl" in text
    assert "projectHash" in text
    assert "tool_call_id" in text
    assert "exported_tool_call_ids" in text


def test_gemini_export_scans_project_name_and_project_hash_directories() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    assert 'gemini_tmp / repo_name / "chats"' in text
    assert 'gemini_tmp / repo_hash / "chats"' in text
    assert 'hashlib.sha256(str(workspace_hub).encode("utf-8")).hexdigest()' in text


def test_gemini_export_reclassifies_help_and_investigation_tools() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    assert '"codebase_investigator": "ToolSearch"' in text
    assert '"cli_help": "ToolSearch"' in text
    assert '"search_file_content": "Grep"' in text


def test_nightly_workflow_invokes_gemini_export() -> None:
    text = NIGHTLY.read_text(encoding="utf-8")

    assert "Gemini session export" in text
    assert "bash scripts/cron/gemini-session-export.sh" in text


def test_orchestrator_readme_mentions_gemini_session_jsonl_requirement() -> None:
    text = README.read_text(encoding="utf-8")

    assert "logs/orchestrator/gemini/session_*.jsonl" in text


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


def test_gemini_export_subprocess_exports_one_record_and_dedupes_on_rerun(tmp_path: Path) -> None:
    repo = tmp_path / "repo-under-test"
    (repo / "scripts" / "cron").mkdir(parents=True)
    shutil.copy2(SCRIPT, repo / "scripts" / "cron" / "gemini-session-export.sh")

    home = tmp_path / "home"
    fake_bin, uv_log = _write_fake_uv(tmp_path)

    repo_hash = hashlib.sha256(str(repo.resolve()).encode("utf-8")).hexdigest()
    chats_dir = home / ".gemini" / "tmp" / repo.name / "chats"
    chats_dir.mkdir(parents=True)

    session_file = chats_dir / "session-abc.json"
    session_file.write_text(
        json.dumps(
            {
                "projectHash": repo_hash,
                "sessionId": "sess-1",
                "kind": "interactive",
                "summary": "Export smoke test",
                "startTime": "2026-04-10T14:00:00Z",
                "lastUpdated": "2026-04-10T14:05:00Z",
                "messages": [
                    {
                        "id": "msg-1",
                        "type": "gemini",
                        "model": "gemini-2.5-pro",
                        "timestamp": "2026-04-10T14:01:00Z",
                        "toolCalls": [
                            {
                                "id": "tool-1",
                                "name": "run_shell_command",
                                "status": "success",
                                "timestamp": "2026-04-10T14:02:00Z",
                                "args": {"command": "git status --short"},
                                "result": [{"functionResponse": {"response": {}}}],
                            }
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

    script_path = repo / "scripts" / "cron" / "gemini-session-export.sh"

    first = subprocess.run(
        ["bash", str(script_path)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert first.returncode == 0, f"stdout: {first.stdout}\nstderr: {first.stderr}"
    assert "Gemini session export: 1 records exported from 1 matching sessions, 0 skipped" in first.stdout

    output_file = repo / "logs" / "orchestrator" / "gemini" / "session_20260410.jsonl"
    assert output_file.exists()

    lines = output_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    record = json.loads(lines[0])
    assert record["tool"] == "Bash"
    assert record["gemini_tool"] == "run_shell_command"
    assert record["cmd"] == "git status --short"
    assert record["session_id"] == "sess-1"
    assert record["project_hash"] == repo_hash
    assert record["tool_call_id"] == "tool-1"

    state_file = repo / "logs" / "orchestrator" / "gemini" / ".export-state.json"
    assert state_file.exists()

    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert state["sessions"]["sess-1"]["exported_tool_call_ids"] == ["tool-1"]

    uv_args = uv_log.read_text(encoding="utf-8").splitlines()
    assert uv_args[:4] == ["run", "--no-project", "python", "-"]

    second = subprocess.run(
        ["bash", str(script_path)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert second.returncode == 0, f"stdout: {second.stdout}\nstderr: {second.stderr}"
    assert "Gemini session export: 0 records exported from 1 matching sessions, 0 skipped" in second.stdout
    assert output_file.read_text(encoding="utf-8").splitlines() == lines
