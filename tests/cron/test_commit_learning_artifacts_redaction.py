"""C20: commit-learning-artifacts.sh redacts host state before it enters the
public tree, and stops when the redactor cannot load.

The script used to ``cp`` the raw codex ``history.jsonl`` (and other host agent
state) into this PUBLIC repository. Each host copy now goes through
``scripts/legal/public_redaction.py copy``; a memory file whose name carries an
identifier is not copied at all; and the script refuses to snapshot anything
when the redactor cannot load. The run happens in a disposable repository with
a disposable HOME, and inherited Git bindings are cleared. Names are synthetic.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "cron" / "commit-learning-artifacts.sh"
SYNTH = "zorblaxcorp"

NEEDED = [
    "scripts/cron/commit-learning-artifacts.sh",
    "scripts/cron/lib/pii-safe-memory-snapshot.sh",
    "scripts/legal/public_redaction.py",
    "scripts/legal/check_identifiers.py",
    ".legal-identifier-gate.yaml",
]


def _bash() -> str | None:
    b = shutil.which("bash")
    if not b:
        return None
    if os.name == "nt" and "system32" in b.lower():
        return None  # the WSL launcher, not a POSIX bash for this tree
    return b


def test_no_raw_copy_of_host_state_into_the_public_tree():
    text = SCRIPT.read_text(encoding="utf-8")
    for host_file in ("history.jsonl", "session_index.jsonl", "state.json", "projects.json",
                      "MEMORY.md", "USER.md", "default.rules"):
        for line in text.splitlines():
            if host_file in line and line.strip().startswith("cp "):
                pytest.fail(f"raw cp of host file remains: {line.strip()}")
    assert "public_redaction.py" in text
    assert "self-check" in text


def _setup(tmp_path: Path, deny: Path | None):
    repo = tmp_path / "repo"
    for rel in NEEDED:
        dest = repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    home = tmp_path / "home"
    (home / ".codex").mkdir(parents=True)
    (home / ".codex" / "history.jsonl").write_text(
        '{"session_id":"s1","text":"work on the %s riser"}\n{"session_id":"s2","text":"clean"}\n' % SYNTH,
        encoding="utf-8",
    )
    mem = home / ".claude" / "projects" / "-mnt-local-analysis-workspace-hub" / "memory"
    mem.mkdir(parents=True)
    (mem / "feedback_a.md").write_text(f"lesson about {SYNTH}\n", encoding="utf-8")
    (mem / f"crossprovider_{SYNTH}_lifecycle_ab12.md").write_text("clean body\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                        "PII_CODENAME_MAP", "LEGAL_CLIENT_MAP", "WORKSPACE_HUB_DENY_LIST")}
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env["WORKSPACE_HUB_PYTHON"] = sys.executable
    env["PII_CODENAME_MAP"] = str(tmp_path / "no-map.yaml")
    if deny is not None:
        env["WORKSPACE_HUB_DENY_LIST"] = str(deny)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=env)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True, env=env)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True, env=env)
    subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "add", "-A"],
                   cwd=repo, check=True, env=env)
    subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-qm", "seed"],
                   cwd=repo, check=True, env=env)
    return repo, env


def _install_fake_gh_and_git(tmp_path: Path, env: dict[str, str]) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir(exist_ok=True)
    fake_gh = fake_bin / "gh"
    fake_gh.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$1\" == repo && \"$2\" == view ]]; then echo PRIVATE; exit 0; fi\n"
        "exit 1\n",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)
    real_git = shutil.which("git")
    assert real_git
    fake_git = fake_bin / "git"
    fake_git.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$1\" == -C && \"$3\" == pull && \"$4\" == --rebase ]]; then exit 0; fi\n"
        "if [[ \"$1\" == -C && \"$3\" == push ]]; then [[ -n \"${FAKE_GIT_PUSH_MARKER:-}\" ]] && touch \"$FAKE_GIT_PUSH_MARKER\"; exit 0; fi\n"
        "if [[ \"$1\" == push ]]; then [[ -n \"${FAKE_GIT_PUSH_MARKER:-}\" ]] && touch \"$FAKE_GIT_PUSH_MARKER\"; exit 0; fi\n"
        "exec " + real_git + " \"$@\"\n",
        encoding="utf-8",
    )
    fake_git.chmod(0o755)
    env["PATH"] = f"{fake_bin}:{env['PATH']}"


def _prepend_failing_rsync(tmp_path: Path, env: dict[str, str]) -> None:
    fake_bin = tmp_path / "failing-rsync-bin"
    fake_bin.mkdir(exist_ok=True)
    fake_rsync = fake_bin / "rsync"
    fake_rsync.write_text("#!/usr/bin/env bash\nexit 23\n", encoding="utf-8")
    fake_rsync.chmod(0o755)
    env["PATH"] = f"{fake_bin}:{env['PATH']}"


def _init_private_repo(path: Path, env: dict[str, str], repo_name: str = "local/private") -> None:
    path.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=path, check=True, env=env)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=path, check=True, env=env)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True, env=env)
    subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{repo_name}.git"],
                   cwd=path, check=True, env=env)
    (path / "README.md").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True, env=env)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=path, check=True, env=env)


@pytest.mark.skipif(_bash() is None, reason="no POSIX bash")
def test_run_redacts_host_copies_and_skips_name_bearing_files(tmp_path):
    deny = tmp_path / "deny.txt"
    deny.write_text(f"{SYNTH}\n", encoding="utf-8")
    repo, env = _setup(tmp_path, deny)
    private_repo = tmp_path / "private-memory"
    private_repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=private_repo, check=True, env=env)
    env["CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE"] = str(private_repo)
    r = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh", "--dry-run"],
                       cwd=repo, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    hist = repo / "config/agents/codex/state-snapshots/history.jsonl"
    assert hist.exists()
    assert SYNTH not in hist.read_text(encoding="utf-8").lower()
    assert '"clean"' in hist.read_text(encoding="utf-8")
    snaps = repo / "config/agents/claude/memory-snapshots"
    assert not snaps.exists()
    private_snaps = private_repo / "config/agents/claude/memory-snapshots"
    assert not private_snaps.exists()
    assert "Would update private Claude memory snapshots" in r.stdout
    assert SYNTH not in (r.stdout + r.stderr).lower()


@pytest.mark.skipif(_bash() is None, reason="no POSIX bash")
def test_run_rejects_wrong_private_snapshot_remote(tmp_path):
    repo, env = _setup(tmp_path, None)
    wrong_remote = tmp_path / "wrong.git"
    subprocess.run(["git", "init", "--bare", "-q", str(wrong_remote)], check=True, env=env)
    seed = tmp_path / "wrong-seed"
    subprocess.run(["git", "clone", "-q", str(wrong_remote), str(seed)], check=True, env=env)
    (seed / "README.md").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "add", "README.md"],
                   cwd=seed, check=True, env=env)
    subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-qm", "seed"],
                   cwd=seed, check=True, env=env)
    subprocess.run(["git", "push", "-q", "origin", "HEAD:main"], cwd=seed, check=True, env=env)
    private_repo = tmp_path / "private-memory"
    subprocess.run(["git", "clone", "-q", "--branch", "main", str(wrong_remote), str(private_repo)],
                   check=True, env=env)
    (seed / "pulled-before-verify.txt").write_text("must not be pulled\n", encoding="utf-8")
    subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "add",
                    "pulled-before-verify.txt"], cwd=seed, check=True, env=env)
    subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-qm",
                    "add marker"], cwd=seed, check=True, env=env)
    subprocess.run(["git", "push", "-q", "origin", "HEAD:main"], cwd=seed, check=True, env=env)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_gh = fake_bin / "gh"
    fake_gh.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$1\" == repo && \"$2\" == view ]]; then echo PRIVATE; exit 0; fi\n"
        "exit 1\n",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE"] = str(private_repo)
    r = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh"],
                       cwd=repo, env=env, capture_output=True, text=True)
    assert r.returncode != 0
    assert "unexpected origin" in r.stdout
    assert not (private_repo / "pulled-before-verify.txt").exists()
    assert not (repo / "config/agents/claude/memory-snapshots").exists()


@pytest.mark.skipif(_bash() is None, reason="no POSIX bash")
def test_run_rejects_private_snapshot_clone_inside_public_checkout_before_clone(tmp_path):
    repo, env = _setup(tmp_path, None)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_gh = fake_bin / "gh"
    fake_gh.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$1\" == repo && \"$2\" == view ]]; then echo PRIVATE; exit 0; fi\n"
        "if [[ \"$1\" == repo && \"$2\" == clone ]]; then mkdir -p \"$4\"; exit 0; fi\n"
        "exit 1\n",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    inside_public = repo / "private-memory"
    env["CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE"] = str(inside_public)
    r = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh"],
                       cwd=repo, env=env, capture_output=True, text=True)
    assert r.returncode != 0
    assert "outside the public checkout" in r.stdout
    assert not inside_public.exists()
    assert not (repo / "config/agents/claude/memory-snapshots").exists()


@pytest.mark.skipif(_bash() is None, reason="no POSIX bash")
def test_run_proceeds_on_a_host_without_the_private_list(tmp_path):
    """Owner decision S01: missing private config does not stop the job; the
    snapshot is written through the redactor's public rules."""
    repo, env = _setup(tmp_path, None)
    r = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh", "--dry-run"],
                       cwd=repo, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (repo / "config/agents/codex/state-snapshots/history.jsonl").exists()


@pytest.mark.skipif(_bash() is None, reason="no POSIX bash")
def test_run_fails_closed_when_a_named_private_list_is_missing(tmp_path):
    repo, env = _setup(tmp_path, tmp_path / "missing-deny.txt")
    r = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh", "--dry-run"],
                       cwd=repo, env=env, capture_output=True, text=True)
    assert r.returncode != 0
    assert not (repo / "config/agents/codex/state-snapshots/history.jsonl").exists()
    assert not (repo / "config/agents/claude/memory-snapshots").exists()


@pytest.mark.skipif(_bash() is None, reason="no POSIX bash")
def test_private_snapshot_second_run_with_fewer_local_files_deletes_nothing(tmp_path):
    repo, env = _setup(tmp_path, None)
    subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
                   cwd=repo, check=True, env=env)
    _install_fake_gh_and_git(tmp_path, env)
    private_repo = tmp_path / "private-memory"
    _init_private_repo(private_repo, env)
    env["CLAUDE_MEMORY_SNAPSHOT_REPO"] = "local/private"
    env["CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE"] = str(private_repo)
    env["CLAUDE_MEMORY_SNAPSHOT_HOST"] = "ace-linux-1"

    mem = Path(env["HOME"]) / ".claude/projects/-mnt-local-analysis-workspace-hub/memory"
    (mem / "keep.md").write_text("keep\n", encoding="utf-8")
    (mem / "drop-locally.md").write_text("do not delete private copy\n", encoding="utf-8")
    first = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh"],
                           cwd=repo, env=env, capture_output=True, text=True)
    assert first.returncode == 0, first.stdout + first.stderr

    (mem / "drop-locally.md").unlink()
    second = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh"],
                            cwd=repo, env=env, capture_output=True, text=True)
    assert second.returncode == 0, second.stdout + second.stderr

    host_root = private_repo / "hosts/ace-linux-1/config/agents/claude/memory-snapshots"
    assert (host_root / "keep.md").exists()
    assert (host_root / "drop-locally.md").exists()


@pytest.mark.skipif(_bash() is None, reason="no POSIX bash")
def test_private_snapshot_rsync_failure_does_not_commit_or_push(tmp_path):
    repo, env = _setup(tmp_path, None)
    subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
                   cwd=repo, check=True, env=env)
    _install_fake_gh_and_git(tmp_path, env)
    _prepend_failing_rsync(tmp_path, env)
    private_repo = tmp_path / "private-memory"
    _init_private_repo(private_repo, env)
    env["CLAUDE_MEMORY_SNAPSHOT_REPO"] = "local/private"
    env["CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE"] = str(private_repo)
    env["CLAUDE_MEMORY_SNAPSHOT_HOST"] = "ace-linux-1"
    push_marker = tmp_path / "push-called"
    env["FAKE_GIT_PUSH_MARKER"] = str(push_marker)

    before_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=private_repo, env=env, text=True).strip()
    mem = Path(env["HOME"]) / ".claude/projects/-mnt-local-analysis-workspace-hub/memory"
    (mem / "new.md").write_text("new\n", encoding="utf-8")

    r = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh"],
                       cwd=repo, env=env, capture_output=True, text=True)
    after_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=private_repo, env=env, text=True).strip()

    assert r.returncode != 0
    assert before_head == after_head
    assert not push_marker.exists()
    assert not (private_repo / "hosts/ace-linux-1/config/agents/claude/memory-snapshots/new.md").exists()


@pytest.mark.skipif(_bash() is None, reason="no POSIX bash")
def test_private_snapshot_invalid_host_does_not_commit_or_push(tmp_path):
    repo, env = _setup(tmp_path, None)
    subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
                   cwd=repo, check=True, env=env)
    _install_fake_gh_and_git(tmp_path, env)
    private_repo = tmp_path / "private-memory"
    _init_private_repo(private_repo, env)
    env["CLAUDE_MEMORY_SNAPSHOT_REPO"] = "local/private"
    env["CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE"] = str(private_repo)
    env["CLAUDE_MEMORY_SNAPSHOT_HOST"] = "!"
    push_marker = tmp_path / "push-called"
    env["FAKE_GIT_PUSH_MARKER"] = str(push_marker)

    before_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=private_repo, env=env, text=True).strip()
    mem = Path(env["HOME"]) / ".claude/projects/-mnt-local-analysis-workspace-hub/memory"
    (mem / "new.md").write_text("new\n", encoding="utf-8")

    r = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh"],
                       cwd=repo, env=env, capture_output=True, text=True)
    after_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=private_repo, env=env, text=True).strip()

    assert r.returncode != 0
    assert before_head == after_head
    assert not push_marker.exists()
    hosts_root = private_repo / "hosts"
    assert not hosts_root.exists() or not any(hosts_root.glob("*"))


@pytest.mark.skipif(_bash() is None, reason="no POSIX bash")
def test_private_snapshot_invalid_public_ref_does_not_commit_or_push(tmp_path):
    repo, env = _setup(tmp_path, None)
    _install_fake_gh_and_git(tmp_path, env)
    private_repo = tmp_path / "private-memory"
    _init_private_repo(private_repo, env)
    env["CLAUDE_MEMORY_SNAPSHOT_REPO"] = "local/private"
    env["CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE"] = str(private_repo)
    env["CLAUDE_MEMORY_SNAPSHOT_HOST"] = "ace-linux-1"
    env["CLAUDE_MEMORY_SNAPSHOT_PUBLIC_REF"] = "refs/heads/does-not-exist"
    push_marker = tmp_path / "push-called"
    env["FAKE_GIT_PUSH_MARKER"] = str(push_marker)

    before_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=private_repo, env=env, text=True).strip()
    mem = Path(env["HOME"]) / ".claude/projects/-mnt-local-analysis-workspace-hub/memory"
    (mem / "new.md").write_text("new\n", encoding="utf-8")

    r = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh"],
                       cwd=repo, env=env, capture_output=True, text=True)
    after_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=private_repo, env=env, text=True).strip()

    assert r.returncode != 0
    assert before_head == after_head
    assert not push_marker.exists()


@pytest.mark.skipif(_bash() is None, reason="no POSIX bash")
def test_private_snapshot_two_hosts_write_separate_subfolders(tmp_path):
    repo, env = _setup(tmp_path, None)
    subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
                   cwd=repo, check=True, env=env)
    _install_fake_gh_and_git(tmp_path, env)
    private_repo = tmp_path / "private-memory"
    _init_private_repo(private_repo, env)
    env["CLAUDE_MEMORY_SNAPSHOT_REPO"] = "local/private"
    env["CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE"] = str(private_repo)
    mem = Path(env["HOME"]) / ".claude/projects/-mnt-local-analysis-workspace-hub/memory"

    env["CLAUDE_MEMORY_SNAPSHOT_HOST"] = "ace-linux-1"
    (mem / "linux.md").write_text("linux role\n", encoding="utf-8")
    first = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh"],
                           cwd=repo, env=env, capture_output=True, text=True)
    assert first.returncode == 0, first.stdout + first.stderr

    env["CLAUDE_MEMORY_SNAPSHOT_HOST"] = "ace-linux-2"
    (mem / "linux.md").unlink()
    (mem / "linux2.md").write_text("linux role 2\n", encoding="utf-8")
    second = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh"],
                            cwd=repo, env=env, capture_output=True, text=True)
    assert second.returncode == 0, second.stdout + second.stderr

    root = private_repo / "hosts"
    assert (root / "ace-linux-1/config/agents/claude/memory-snapshots/linux.md").exists()
    assert (root / "ace-linux-2/config/agents/claude/memory-snapshots/linux2.md").exists()
