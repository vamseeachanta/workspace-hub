"""Git 2.43 githooks post-commit contract: the commit cannot be undone here.

Independent oracle: a successful helper appends one literal line. A missing or
nonzero helper appends one failure event and the installed wrapper returns zero.
The tested hook file is copied only into a disposable repository's hooks folder.
The committed helper is authoritative; an edited helper must never be executed.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DISPATCH = ROOT / "scripts/hooks/post-commit-learning-dispatch.sh"
HELPER = "scripts/hooks/post-commit-learnings.sh"


def git(repo, *args, input=None, env=None):
    return subprocess.run(["git", "-C", str(repo), *args], input=input,
                          env=env, capture_output=True, check=True).stdout


def commit(repo):
    git(repo, "add", ".")
    tree = git(repo, "write-tree").decode().strip()
    env = dict(os.environ)
    for prefix in ("GIT_AUTHOR", "GIT_COMMITTER"):
        env[prefix + "_NAME"] = "Fixture"
        env[prefix + "_EMAIL"] = "fixture" + "@" + "example" + ".invalid"
    oid = git(repo, "commit-tree", tree, input=b"fixture\n", env=env).decode().strip()
    git(repo, "update-ref", "HEAD", oid)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
        monkeypatch.delenv(key, raising=False)
    root = tmp_path / "main"
    root.mkdir()
    git(root, "init", "-q")
    (root / "keep").mkdir()
    (root / "keep/readme.txt").write_text("fixture\n")
    (root / HELPER).parent.mkdir(parents=True)
    return root


def run_installed(root):
    common = Path(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip())
    hook = common / "hooks/post-commit"
    shutil.copyfile(DISPATCH, hook)
    hook.chmod(0o755)
    # git hook run invokes the exact installed event file, without a new commit.
    result = subprocess.run(["git", "hook", "run", "post-commit"], cwd=root,
                            capture_output=True, text=True, check=False)
    return result, common


@pytest.mark.parametrize("sparse", [False, True])
def test_installed_hook_uses_committed_helper(repo, tmp_path, sparse):
    (repo / HELPER).write_text("printf 'success\\n' >> learning-result.txt\n")
    commit(repo)
    active = repo
    if sparse:
        active = tmp_path / "linked"
        git(repo, "worktree", "add", "--detach", str(active))
        git(active, "sparse-checkout", "set", "--cone", "keep")
        assert not (active / HELPER).exists()
    else:
        (repo / HELPER).write_text("touch untrusted-was-executed\n")
    result, common = run_installed(active)
    assert result.returncode == 0, result.stderr
    assert (active / "learning-result.txt").read_text() == "success\n"
    assert not (active / "untrusted-was-executed").exists()
    assert not (common / "post-commit-learning-failures.log").exists()


@pytest.mark.parametrize("helper", [None, "exit 7\n"])
def test_missing_or_failed_helper_is_logged(repo, helper):
    if helper:
        (repo / HELPER).write_text(helper)
    commit(repo)
    result, common = run_installed(repo)
    assert result.returncode == 0
    log = (common / "post-commit-learning-failures.log").read_text()
    assert len(log.splitlines()) == 1
    assert "failure " in log
    assert "failures=1" in result.stderr
    assert "learning" in result.stderr


def test_pipeline_child_failure_propagates_to_wrapper(repo):
    shutil.copyfile(ROOT / HELPER, repo / HELPER)
    child = repo / "scripts/hooks/track-skill-patches.sh"
    child.write_text("exit 9\n")
    commit(repo)
    result, common = run_installed(repo)
    assert result.returncode == 0
    assert "failure " in (common / "post-commit-learning-failures.log").read_text()


def test_deleted_untracked_child_is_not_executed(repo):
    shutil.copyfile(ROOT / HELPER, repo / HELPER)
    commit(repo)
    child = repo / "scripts/hooks/track-skill-patches.sh"
    child.write_text("touch untracked-was-executed\n")
    result, _ = run_installed(repo)
    assert result.returncode == 0
    assert not (repo / "untracked-was-executed").exists()


def test_installer_emits_durable_payload_and_preserves_other_steps(repo):
    """Only learning bytes change; independent pre-push path repair is excluded."""
    (repo / HELPER).write_text("printf 'success\\n' >> learning-result.txt\n")
    commit(repo)
    hooks = repo / ".git/hooks"
    (hooks / "pre-commit").write_text("#!/usr/bin/env bash\nexit 0\n")
    (hooks / "pre-push").write_text(
        "#!/usr/bin/env bash\n# <<INSTALL_HOOKS_EXTENSION_POINT>>\nexit 0\n")
    legacy = 'bash "${REPO_ROOT}/scripts/hooks/post-commit-learnings.sh" || true'
    hook = hooks / "post-commit"
    hook.write_text("#!/usr/bin/env bash\nprintf 'other\\n' >> other-result.txt\n" +
                    legacy + "\nexit 0\n")
    for name in ("enforcement-env.sh", "require-review-on-push.sh"):
        dest = repo / "scripts/enforcement" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "scripts/enforcement" / name, dest)
    installer = ROOT / "scripts/enforcement/install-hooks.sh"
    result = subprocess.run(["bash", str(installer)], cwd=repo,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "learning_dispatch()" in hook.read_text()
    assert legacy not in hook.read_text()
    hook.chmod(0o755)
    # The real Git event invokes the installed payload in a sparse worktree.
    linked = repo.parent / "linked"
    git(repo, "worktree", "add", "--detach", str(linked))
    git(linked, "sparse-checkout", "set", "--cone", "keep")
    result = subprocess.run(["git", "hook", "run", "post-commit"], cwd=linked,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert (linked / "learning-result.txt").read_text() == "success\n"
    assert (linked / "other-result.txt").read_text() == "other\n"
    before = hook.read_bytes()
    result = subprocess.run(["bash", str(installer)], cwd=repo,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert hook.read_bytes() == before


def test_failure_events_accumulate(repo):
    (repo / HELPER).write_text("exit 7\n")
    commit(repo)
    run_installed(repo)
    result, common = run_installed(repo)
    assert result.returncode == 0
    assert "failures=2" in result.stderr
    assert len((common / "post-commit-learning-failures.log").read_text().splitlines()) == 2


def test_symlink_helper_is_not_executed(repo):
    helper = repo / HELPER
    helper.symlink_to("malicious.sh")
    (helper.parent / "malicious.sh").write_text("touch untrusted-was-executed\n")
    commit(repo)
    result, common = run_installed(repo)
    assert result.returncode == 0
    assert not (repo / "untrusted-was-executed").exists()
    assert (common / "post-commit-learning-failures.log").is_file()
