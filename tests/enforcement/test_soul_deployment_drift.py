"""Regression criteria from issue 3833; all deployments are synthetic."""
import os
import shutil
import subprocess

import pytest
from test_soul_auto_load import ROOT, bash_executable, install

pytest_plugins = ("test_soul_auto_load",)


def tool(env, root, name, body):
    directory = root / "tools"
    directory.mkdir(exist_ok=True)
    path = directory / name
    path.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8")
    path.chmod(0o755)
    env["PATH"] = str(directory) + os.pathsep + env["PATH"]


@pytest.mark.parametrize("existing", ["copy", "link", "dangling", "absent"])
@pytest.mark.parametrize("failure", ["denied", "copy"])
@pytest.mark.parametrize("platform", ["Linux", "MINGW64"])
def test_failed_link_preserves_destination(installation, tmp_path, existing, failure, platform):
    """Independent oracle: failed replacement leaves original bytes/link unchanged."""
    repo, user, env = installation
    target = user / ".codex/AGENTS.md"
    if existing == "copy":
        target.write_bytes(b"Prior instructions\n")
    elif existing in {"link", "dangling"}:
        prior = user / "prior.md"
        if existing == "link":
            prior.write_bytes(b"Prior linked instructions\n")
        target.symlink_to(prior)
    before = os.readlink(target) if target.is_symlink() else (
        target.read_bytes() if target.exists() else None)
    tool(env, tmp_path, "uv", 'printf "LEGACY\\n"\n')
    tool(env, tmp_path, "uname", f'printf "{platform}\\n"\n')
    body = 'echo "synthetic link denial" >&2\nexit 1\n'
    if failure == "copy":
        body = 'cp "$2" "$3"\n'
    tool(env, tmp_path, "ln", body)
    result = install(installation)
    assert result.returncode == 1, result.stdout + result.stderr
    after = os.readlink(target) if target.is_symlink() else (
        target.read_bytes() if target.exists() else None)
    assert after == before
    assert not list(user.rglob("*.pre-install-backup.*"))
    assert not list(user.rglob(".soul-link.*"))
    assert (repo / "config/agents/codex/AGENTS.runtime.md").read_bytes() == b"Synthetic runtime fixture\n"


def test_successful_replacement_keeps_backup(installation, tmp_path):
    """Issue 3833: replacement is linked and prior instructions remain recoverable."""
    _, user, env = installation
    tool(env, tmp_path, "uv", 'printf "LEGACY\\n"\n')
    target = user / ".codex/AGENTS.md"
    target.write_bytes(b"Prior instructions\n")
    result = install(installation)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "~/.gemini/GEMINI.md not deployed" in result.stdout
    assert "~/.agy/SOUL.md not deployed" in result.stdout
    assert target.is_symlink()
    assert target.read_bytes() == b"Synthetic runtime fixture\n"
    backups = list(target.parent.glob("AGENTS.md.pre-install-backup.*"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == b"Prior instructions\n"


@pytest.mark.parametrize("transport,state", [("symlink", "CURRENT"), ("copy", "UNLINKED"),
                                            ("absent", "ABSENT"), ("stale", "STALE")])
def test_gate_counts_only_deployed_surfaces(tmp_path, transport, state):
    """Hand count: two excluded rows add zero drift; each bad deployed row adds one."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    user = tmp_path / "user"
    user.mkdir()
    env.update(HOME=str(user), FIXTURE_ROOT=str(tmp_path))
    (tmp_path / "origin-runtime").write_bytes(b"Authoritative fixture\n")
    (tmp_path / "claude-runtime").symlink_to(tmp_path / "origin-runtime")
    for name, relative in [("codex", "AGENTS.md"), ("hermes", "SOUL.md")]:
        directory = user / ("." + name)
        directory.mkdir()
        destination = directory / relative
        if transport in {"symlink", "stale"}:
            source = tmp_path / (name + "-runtime")
            source.write_bytes(b"Stale fixture\n" if transport == "stale" else b"Authoritative fixture\n")
            destination.symlink_to(source)
        elif transport == "copy":
            destination.write_bytes(b"Authoritative fixture\n")
    tool(env, tmp_path, "uv", 'printf "%s\\n" "$FIXTURE_ROOT/claude-runtime"\n')
    tool(env, tmp_path, "git", '''case "$*" in
  *--show-toplevel*) printf '%s\\n' "$FIXTURE_ROOT" ;;
  *rev-list*) echo 0 ;;
  *rev-parse*) echo synthetic ;;
  *show*) cat "$FIXTURE_ROOT/origin-runtime" ;;
esac
''')
    result = subprocess.run([bash_executable(), str(ROOT / "scripts/enforcement/check-soul-deployment-drift.sh"),
                             "--no-fetch"], cwd=tmp_path, env=env, text=True,
                            capture_output=True, timeout=30, check=False)
    assert result.returncode == (0 if transport == "symlink" else 1), result.stdout + result.stderr
    for provider in ("gemini", "agy"):
        row = next(line for line in result.stdout.splitlines() if line.startswith(provider + " "))
        assert "NOT-DEPLOYED" in row
    assert "0 drifted" in result.stdout if transport == "symlink" else "2 drifted" in result.stdout
    row = next(line for line in result.stdout.splitlines() if line.startswith("codex "))
    assert state in row


def test_self_test_is_isolated(tmp_path):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["HOME"] = str(tmp_path)
    result = subprocess.run([bash_executable(), str(ROOT / "scripts/enforcement/check-soul-deployment-drift.sh"),
                             "--self-test"], cwd=tmp_path, env=env, text=True,
                            capture_output=True, timeout=30, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "intentionally not deployed" in result.stdout
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("command", ["cp", "mv"])
def test_backup_or_publish_failure_keeps_original(installation, tmp_path, command):
    """A failed backup or rename preserves old bytes and permits the next provider."""
    _, user, env = installation
    tool(env, tmp_path, "uv", 'printf "LEGACY\\n"\n')
    target = user / ".hermes/SOUL.md"
    target.write_bytes(b"Prior instructions\n")
    env["REAL_TOOL"] = shutil.which(command)
    tool(env, tmp_path, command, '''case "$*" in
  *SOUL.md*) echo "synthetic replacement denial" >&2; exit 1 ;;
  *) exec "$REAL_TOOL" "$@" ;;
esac
''')
    result = install(installation)
    assert result.returncode == 1, result.stdout + result.stderr
    assert not target.is_symlink()
    assert target.read_bytes() == b"Prior instructions\n"
    assert (user / ".codex/AGENTS.md").is_symlink()
    assert not list(user.rglob(".soul-link.*"))
    backups = list(target.parent.glob("SOUL.md.pre-install-backup.*"))
    assert len(backups) == (1 if command == "mv" else 0)
    if backups:
        assert backups[0].read_bytes() == b"Prior instructions\n"
