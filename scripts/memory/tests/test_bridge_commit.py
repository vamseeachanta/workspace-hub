"""TDD tests for the private memory bridge commit helper."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
LIB = REPO_ROOT / "scripts" / "memory" / "bridge-commit.sh"
BRIDGE = REPO_ROOT / "scripts" / "memory" / "bridge-hermes-claude.sh"
SCHEDULE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"

HOST_SLUG = "ace-linux-1"
HOST_MEMORY = f"hosts/{HOST_SLUG}/memory/agents.md"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert result.returncode == 0, f"git {args} failed: {result.stderr}"
    return result.stdout.strip()


def _seed_private_repo(tmp_path: Path) -> Path:
    work = tmp_path / "private"
    work.mkdir()
    _git(work, "init", "-q")
    _git(work, "checkout", "-q", "-b", "main")
    _git(work, "config", "user.email", "t@example.invalid")
    _git(work, "config", "user.name", "test")
    _git(work, "config", "commit.gpgsign", "false")
    host_file = work / HOST_MEMORY
    host_file.parent.mkdir(parents=True, exist_ok=True)
    host_file.write_text("seed\n", encoding="utf-8")
    _git(work, "add", "-A")
    _git(work, "commit", "-qm", "init")
    bare = tmp_path / "origin.git"
    _git(work, "init", "-q", "--bare", str(bare))
    _git(bare, "symbolic-ref", "HEAD", "refs/heads/main")
    _git(work, "remote", "add", "origin", str(bare))
    _git(work, "push", "-q", "-u", "origin", "main")
    return work


def _run(repo: Path, host_slug: str = HOST_SLUG) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "-c", f'source "{LIB}"; bridge_private_commit_and_push "{repo}" "{host_slug}" "2026-10-09"'],
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def private_repo(tmp_path: Path) -> Path:
    return _seed_private_repo(tmp_path)


def test_private_commit_lands_only_host_folder(private_repo: Path):
    (private_repo / HOST_MEMORY).write_text("updated\n", encoding="utf-8")
    unrelated = private_repo / "unrelated.txt"
    unrelated.write_text("dirty\n", encoding="utf-8")

    result = _run(private_repo)

    assert result.returncode == 0, result.stderr
    committed = _git(private_repo, "show", "--name-only", "--format=", "HEAD")
    assert HOST_MEMORY in committed
    assert "unrelated.txt" not in committed
    assert unrelated.read_text(encoding="utf-8") == "dirty\n"


def test_private_commit_fails_closed_without_host_folder(private_repo: Path):
    result = _run(private_repo, "ace-linux-2")

    assert result.returncode != 0
    assert "hosts/ace-linux-2" in result.stderr


def test_bridge_does_not_add_public_memory_paths_to_commit():
    text = LIB.read_text(encoding="utf-8")
    assert ".claude/memory" not in text
    assert "config/agents/codex/MEMORY.runtime.md" not in text
    assert "config/agents/gemini/MEMORY.runtime.md" not in text


def _task_command(task_id: str) -> str:
    data = yaml.safe_load(SCHEDULE.read_text(encoding="utf-8"))
    for task in _iter_tasks(data):
        if task.get("id") == task_id:
            return task["command"]
    raise AssertionError(f"task {task_id} not found")


def _iter_tasks(node):
    if isinstance(node, dict):
        if "id" in node and "command" in node:
            yield node
        for value in node.values():
            yield from _iter_tasks(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_tasks(value)


def test_schedule_bridge_commit_flag_position():
    command = _task_command("hermes-claude-bridge")
    assert "--commit" in command
    assert command.index("--commit") < command.index(">>")


def test_bridge_requires_private_repo_before_writes():
    text = BRIDGE.read_text(encoding="utf-8")
    validation = text.index("require_private_memory_repo")
    first_mkdir = text.index("mkdir -p")
    assert validation < first_mkdir
    assert "MEMORY_PRIVATE_REPO_DIR" in text
    assert "MEMORY_PRIVATE_REPO_SLUG" not in text
    assert "gh repo view" in text
    assert "visibility" in text
    assert "hosts/${HOST_SLUG}/memory" in text
    assert "config/agents/codex/MEMORY.runtime.md" not in text
    assert "config/agents/gemini/MEMORY.runtime.md" not in text


def test_bridge_fails_closed_when_private_repo_unreachable(tmp_path: Path):
    env = {
        **os_environ_minimal(tmp_path),
        "MEMORY_PRIVATE_REPO_DIR": str(tmp_path / "missing-private"),
        "MEMORY_BRIDGE_HOST_SLUG": HOST_SLUG,
    }

    result = subprocess.run(["bash", str(BRIDGE)], capture_output=True, text=True, env=env)

    assert result.returncode != 0
    assert "private memory repo is required" in result.stderr
    assert not (tmp_path / "missing-private").exists()


def test_bridge_writes_private_per_host_folder(tmp_path: Path):
    private = tmp_path / "private"
    private.mkdir()
    _git(private, "init", "-q")
    _git(private, "checkout", "-q", "-b", "main")
    home = tmp_path / "home"
    hermes = home / ".hermes" / "memories"
    hermes.mkdir(parents=True)
    (hermes / "MEMORY.md").write_text("role-local fact\n", encoding="utf-8")
    repo_slug = str(REPO_ROOT.resolve()).replace("/", "-")
    auto_mem = home / ".claude" / "projects" / repo_slug / "memory"
    auto_mem.mkdir(parents=True)
    auto_mem.joinpath("MEMORY.md").write_text(
        "- [Strict up-to-date ruleset](feedback_strict_uptodate_ruleset_no_admin_bypass.md) — reviewed redacted entry\n"
        "- [Verify generated state](feedback_verify_generated_state_against_origin_not_working_copy.md) — reviewed redacted entry\n",
        encoding="utf-8",
    )

    env = {
        **os_environ_minimal(home),
        "MEMORY_PRIVATE_REPO_DIR": str(private),
        "MEMORY_PRIVATE_ALLOW_LOCAL_TEST": "1",
        "MEMORY_BRIDGE_HOST_SLUG": "ace-linux-2",
    }

    result = subprocess.run(["bash", str(BRIDGE)], capture_output=True, text=True, env=env)

    assert result.returncode == 0, result.stderr
    assert (private / "hosts" / "ace-linux-2" / "memory" / "agents.md").exists()
    assert (private / "hosts" / "ace-linux-2" / "memory" / "context.md").exists()
    assert (private / "hosts" / "ace-linux-2" / "readback" / "codex.md").exists()
    assert (private / "hosts" / "ace-linux-2" / "readback" / "gemini.md").exists()
    assert not (private / ".claude" / "memory").exists()


def os_environ_minimal(home: Path) -> dict[str, str]:
    import os

    env = os.environ.copy()
    env["HOME"] = str(home)
    env["BRIDGE_REPO_ROOT"] = str(REPO_ROOT)
    env["UV_CACHE_DIR"] = "/tmp/uv-cache-x02"
    return env
