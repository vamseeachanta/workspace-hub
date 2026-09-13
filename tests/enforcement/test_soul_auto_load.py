"""Installer wiring in disposable roots; no live provider-loading assertion."""
from pathlib import Path
import os
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]
SUPPORTED = {".claude/CLAUDE.md": "claude/SOUL.runtime.md",
             ".codex/AGENTS.md": "codex/AGENTS.runtime.md",
             ".hermes/SOUL.md": "hermes/SOUL.runtime.md"}


def bash_executable():
    candidates = [shutil.which("bash")]
    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidates.insert(0, str(Path(local) / "Programs/Git/usr/bin/bash.exe"))
    found = next((p for p in candidates if p and Path(p).is_file()), None)
    assert found, "Bash capability unavailable; installer coverage is not established"
    return found


@pytest.fixture
def installation(tmp_path):
    repo, user_root = tmp_path / "repo", tmp_path / "user"
    for relative in ["scripts/agents/install-soul-runtime.sh", "scripts/setup/lib/detect-os.sh"]:
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    for runtime in SUPPORTED.values():
        target = repo / "config/agents" / runtime
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("Synthetic runtime fixture\n", encoding="utf-8")
    for provider in [".claude", ".codex", ".hermes", ".gemini", ".agy"]:
        (user_root / provider).mkdir(parents=True)
    # Only the installer child receives this fixture HOME.
    env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATH")
           if key in os.environ}
    env.update(HOME=user_root.as_posix(), MSYS="winsymlinks:nativestrict")
    env["PATH"] = str(Path(bash_executable()).parent) + os.pathsep + env.get("PATH", "")
    return repo, user_root, env


def install(installation, cwd=None):
    repo, user_root, env = installation
    assert user_root.resolve().parent == repo.resolve().parent
    assert user_root.is_dir() and not user_root.is_symlink()
    return subprocess.run([bash_executable(), str(repo / "scripts/agents/install-soul-runtime.sh")],
                          cwd=cwd or user_root, env=env, capture_output=True,
                          text=True, encoding="utf-8", timeout=30)


def assert_supported_links(repo, user_root):
    for relative, runtime in SUPPORTED.items():
        link = user_root / relative
        assert link.is_symlink(), "Real symlink capability required; copies do not pass"
        assert link.resolve() == (repo / "config/agents" / runtime).resolve()
        assert link.read_text(encoding="utf-8") == "Synthetic runtime fixture\n"


def test_fixture_installer_creates_only_supported_real_links(installation):
    repo, user_root, _ = installation
    result = install(installation)
    assert result.returncode == 0, result.stdout + result.stderr
    assert_supported_links(repo, user_root)
    for relative in [".codex/SOUL.md", ".gemini/SOUL.md", ".gemini/GEMINI.md", ".agy/SOUL.md"]:
        assert not (user_root / relative).exists()
    assert not (repo / "CLAUDE.md").exists()


def test_fixture_installer_repeat_is_idempotent(installation):
    repo, user_root, _ = installation
    assert install(installation).returncode == 0
    before = {p: (os.readlink(user_root / p), (user_root / p).lstat().st_mtime_ns)
              for p in SUPPORTED}
    result = install(installation)
    assert result.returncode == 0, result.stdout + result.stderr
    assert_supported_links(repo, user_root)
    assert before == {p: (os.readlink(user_root / p), (user_root / p).lstat().st_mtime_ns)
                      for p in SUPPORTED}
    assert not list(user_root.rglob("*.pre-install-backup.*"))


def test_fixture_installer_preserves_regular_file_backup(installation):
    repo, user_root, _ = installation
    original = user_root / ".claude/CLAUDE.md"
    original.write_bytes(b"Original fixture instructions\n")
    result = install(installation)
    assert result.returncode == 0, result.stdout + result.stderr
    assert_supported_links(repo, user_root)
    backups = list(original.parent.glob("CLAUDE.md.pre-install-backup.*"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == b"Original fixture instructions\n"


def test_fixture_installer_self_locates_from_unrelated_directory(installation, tmp_path):
    repo, user_root, _ = installation
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    (foreign / "sentinel").write_bytes(b"Caller must remain untouched")
    before = {p.name: p.read_bytes() for p in foreign.iterdir()}
    result = install(installation, cwd=foreign)
    assert result.returncode == 0, result.stdout + result.stderr
    assert_supported_links(repo, user_root)
    assert before == {p.name: p.read_bytes() for p in foreign.iterdir()}


def test_fixture_installer_does_not_provision_absent_provider_directory(installation):
    _, user_root, _ = installation
    (user_root / ".claude").rmdir()
    result = install(installation)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (user_root / ".claude").exists()
    assert (user_root / ".codex/AGENTS.md").is_symlink()


def tree_bytes(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


@pytest.fixture
def generation(tmp_path):
    repo, caller = tmp_path / "source", tmp_path / "caller"
    inputs = ["config/agents/SHARED_SOUL.md", "scripts/agents/build-soul-runtime.sh",
              "scripts/agents/soul-runtime-lib.sh", "scripts/enforcement/check-soul-runtime-drift.sh",
              "scripts/agents/tests/test_build_soul_runtime_codex.sh", ".claude/rules/coding-style.md",
              ".claude/rules/patterns.md", "GEMINI.md"]
    inputs += ["config/agents/" + provider + "/" + ("SOUL.md" if provider == "hermes" else "SOUL.delta.md")
               for provider in ["hermes", "claude", "codex", "gemini", "agy"]]
    for relative in inputs:
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    caller.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["PATH"] = str(Path(bash_executable()).parent) + os.pathsep + env.get("PATH", "")
    for target in [repo, caller]:
        subprocess.run(["git", "-c", "init.templateDir=", "init", "-q", str(target)], env=env, check=True)
    subprocess.run([bash_executable(), "scripts/agents/build-soul-runtime.sh"], cwd=repo, env=env,
                   capture_output=True, check=True, timeout=60)
    return repo, caller, env


@pytest.mark.parametrize("script", ["scripts/agents/tests/test_build_soul_runtime_codex.sh",
                                  "scripts/enforcement/check-soul-runtime-drift.sh"])
def test_generation_tools_ignore_foreign_git_bindings(generation, script):
    repo, caller, env = generation
    before = tree_bytes(caller)
    source_before = tree_bytes(repo)
    env.update(GIT_DIR=(caller / ".git").as_posix(), GIT_WORK_TREE=caller.as_posix(),
               GIT_COMMON_DIR=(caller / ".git").as_posix())
    result = subprocess.run([bash_executable(), (repo / script).as_posix()], cwd=caller, env=env,
                            capture_output=True, encoding="utf-8", timeout=150)
    assert tree_bytes(caller) == before, "Foreign Git files or metadata changed"
    assert tree_bytes(repo) == source_before, "Source fixture changed"
    assert result.returncode == 0, result.stdout + result.stderr
