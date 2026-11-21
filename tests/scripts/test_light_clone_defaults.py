"""New clones made by hub scripts are light by default.

A partial clone (``--filter=blob:none``) keeps full history but fetches file
contents only when a checkout or command needs them. ``ECOSYSTEM_FULL_CLONE=1``
restores a full clone for a caller that needs every object locally.

The checks run each script against fakes or a disposable local origin; nothing
reaches the network. Names are synthetic.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _bash() -> str | None:
    b = shutil.which("bash")
    if not b:
        return None
    if os.name == "nt" and "system32" in b.lower():
        return None  # the WSL launcher, not a POSIX bash for this tree
    return b


needs_bash = pytest.mark.skipif(_bash() is None, reason="no POSIX bash")


def _env(tmp_path: Path, full: bool) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                        "ECOSYSTEM_FULL_CLONE")}
    env["HOME"] = str(tmp_path / "home")
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    (tmp_path / "home").mkdir(exist_ok=True)
    if full:
        env["ECOSYSTEM_FULL_CLONE"] = "1"
    return env


def _git(*args: str, cwd: Path, env: dict[str, str]) -> str:
    return subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=t", *args],
                          cwd=cwd, env=env, check=True, capture_output=True, text=True).stdout.strip()


def _origin(tmp_path: Path, env: dict[str, str]) -> Path:
    seed = tmp_path / "seed"
    seed.mkdir()
    _git("init", "-q", "-b", "main", cwd=seed, env=env)
    (seed / "README.md").write_text("seed\n", encoding="utf-8")
    _git("add", "README.md", cwd=seed, env=env)
    _git("commit", "-qm", "seed", cwd=seed, env=env)
    bare = tmp_path / "origin.git"
    _git("clone", "-q", "--bare", str(seed), str(bare), cwd=tmp_path, env=env)
    _git("config", "uploadpack.allowFilter", "true", cwd=bare, env=env)
    return bare


def _recording_gh(tmp_path: Path, env: dict[str, str]) -> Path:
    """A gh stand-in: answers repo view, records repo clone arguments, then fails the clone."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir(exist_ok=True)
    record = tmp_path / "gh-clone-args.txt"
    gh = fake_bin / "gh"
    gh.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$1\" == repo && \"$2\" == view ]]; then echo PRIVATE; exit 0; fi\n"
        f"if [[ \"$1\" == repo && \"$2\" == clone ]]; then printf '%s\\n' \"$@\" > '{record.as_posix()}'; exit 1; fi\n"
        "exit 1\n",
        encoding="utf-8",
    )
    gh.chmod(0o755)
    env["PATH"] = f"{fake_bin.as_posix()}{os.pathsep}{env['PATH']}"
    return record


# --- scripts/repository_sync clone ------------------------------------------

def _sync_tree(tmp_path: Path, url: str) -> Path:
    tree = tmp_path / "ws"
    (tree / "scripts").mkdir(parents=True)
    (tree / "config").mkdir()
    for name in ("repository_sync", "repository_sync-auto"):
        shutil.copy2(ROOT / "scripts" / name, tree / "scripts" / name)
    (tree / "config" / "repos.conf").write_text(f"demo={url}\n", encoding="utf-8")
    return tree


@needs_bash
@pytest.mark.parametrize("full", [False, True])
def test_repository_sync_clone_is_partial_unless_opted_out(tmp_path, full):
    env = _env(tmp_path, full)
    url = _origin(tmp_path, env).as_uri()
    tree = _sync_tree(tmp_path, url)
    r = subprocess.run([_bash(), "scripts/repository_sync", "clone", "demo"],
                       cwd=tree, env=env, capture_output=True, text=True, timeout=120)
    assert (tree / "demo" / "README.md").is_file(), r.stdout + r.stderr
    flt = subprocess.run(["git", "-C", str(tree / "demo"), "config", "--get",
                          "remote.origin.partialclonefilter"],
                         env=env, capture_output=True, text=True).stdout.strip()
    assert flt == ("" if full else "blob:none")


# --- scripts/cron/commit-learning-artifacts.sh ------------------------------

@needs_bash
@pytest.mark.parametrize("full", [False, True])
def test_private_snapshot_clone_is_partial_unless_opted_out(tmp_path, full):
    repo = tmp_path / "repo"
    for rel in ("scripts/cron/commit-learning-artifacts.sh",
                "scripts/cron/lib/pii-safe-memory-snapshot.sh",
                "scripts/legal/public_redaction.py",
                "scripts/legal/check_identifiers.py",
                ".legal-identifier-gate.yaml"):
        dest = repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    env = _env(tmp_path, full)
    mem = tmp_path / "home" / ".claude" / "projects" / "-mnt-local-analysis-workspace-hub" / "memory"
    mem.mkdir(parents=True)
    (mem / "feedback_a.md").write_text("a lesson\n", encoding="utf-8")
    env["WORKSPACE_HUB_PYTHON"] = sys.executable
    env["PII_CODENAME_MAP"] = str(tmp_path / "no-map.yaml")
    env["CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE"] = str(tmp_path / "private-memory")
    _git("init", "-q", cwd=repo, env=env)
    _git("add", "-A", cwd=repo, env=env)
    _git("commit", "-qm", "seed", cwd=repo, env=env)
    record = _recording_gh(tmp_path, env)
    # A real run (dry-run skips the private clone); the fake gh fails the clone, so
    # the script stops before it writes or pushes anything.
    subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh"],
                   cwd=repo, env=env, capture_output=True, text=True, timeout=120)
    args = record.read_text(encoding="utf-8").split()
    assert args[:2] == ["repo", "clone"]
    assert ("--filter=blob:none" in args) is (not full)


# --- scripts/reports/team-summary-refresh.sh --------------------------------

@needs_bash
@pytest.mark.parametrize("full", [False, True])
def test_team_summary_clone_is_partial_unless_opted_out(tmp_path, full):
    env = _env(tmp_path, full)
    record = _recording_gh(tmp_path, env)
    subprocess.run([_bash(), str(ROOT / "scripts" / "reports" / "team-summary-refresh.sh"),
                    "democlient", "--dry-run"],
                   cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60)
    args = record.read_text(encoding="utf-8").split()
    assert args[:3] == ["repo", "clone", "vamseeachanta/llm-wiki-democlient"]
    assert "--depth" in args
    assert ("--filter=blob:none" in args) is (not full)
