"""Independent Git fixture oracles, per Git 2.43 ls-files and sparse-checkout.

Two target scripts have one line each: clean content gives zero findings;
a literal computed forbidden prefix gives one finding. The expected coverage
is two enumerated and two scanned, even when one tracked path is omitted.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from test_worktree_index_preflight import clean_env as fixture_clean_env
from test_worktree_index_preflight import git
from test_worktree_index_preflight import repo as fixture_repo

repo_fixture = pytest.fixture(name="repo")(fixture_repo.__wrapped__)
clean_env_fixture = pytest.fixture(name="clean_env")(fixture_clean_env.__wrapped__)

ROOT = Path(__file__).resolve().parents[2]


def install_scanner(root):
    for name in ("scripts/enforcement/check-no-abs-paths.sh",
                 "scripts/lib/worktree-index.sh"):
        dest = root / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)


def scan(root, *args, env=None, cwd=None):
    # Script belongs to this disposable repository, not the real checkout.
    return subprocess.run(["bash", str(root / "scripts/enforcement/check-no-abs-paths.sh"),
                           "--no-baseline", *args], cwd=cwd or root, env=env,
                          capture_output=True, text=True, check=False)


def commit_index(repo):
    tree = git(repo, "write-tree").decode().strip()
    env = dict(os.environ)
    for prefix in ("GIT_AUTHOR", "GIT_COMMITTER"):
        env[prefix + "_NAME"] = "Fixture"
        env[prefix + "_EMAIL"] = "fixture" + "@" + "example" + ".invalid"
    commit = subprocess.run(["git", "-C", str(repo), "commit-tree", tree],
                            input=b"scripts\n", env=env, capture_output=True,
                            check=True).stdout.decode().strip()
    git(repo, "update-ref", "HEAD", commit)


@pytest.fixture
def target(repo):
    for path in ("keep/clean.py", "omit/clean.py"):
        (repo / path).write_text("print('clean')\n")
    git(repo, "add", ".")
    commit_index(repo)
    install_scanner(repo)
    return repo


def bad_line():
    return "value = '" + "/" + "mnt" + "/forbidden'\n"


def test_full_coverage(target):
    result = scan(target)
    assert result.returncode == 0, result.stderr
    assert "enumerated=2 scanned=2" in result.stderr


def test_sparse_omission_reads_index(target, tmp_path):
    wt = tmp_path / "sparse"
    git(target, "worktree", "add", "--detach", str(wt))
    git(wt, "sparse-checkout", "set", "--cone", "keep")
    install_scanner(wt)
    assert not (wt / "omit/clean.py").exists()
    result = scan(wt)
    assert result.returncode == 0, result.stderr
    assert "enumerated=2 scanned=2" in result.stderr
    assert "object-fallback=1" in result.stderr


def test_staged_and_head_authority(target):
    path = target / "keep/clean.py"
    path.write_text(bad_line())
    git(target, "add", "keep/clean.py")
    path.write_text("print('clean')\n")
    staged = scan(target, "--staged")
    assert staged.returncode == 1
    assert "keep/clean.py:1:" in staged.stdout
    assert scan(target, "--head").returncode == 0
    assert scan(target).returncode == 0


def test_missing_materialized_file_is_error(target):
    (target / "keep/clean.py").unlink()
    result = scan(target)
    assert result.returncode == 2
    assert "missing materialized target" in result.stderr
    assert scan(target, "--staged").returncode == 0


@pytest.mark.parametrize("name", ["with space.py", "with\nnewline.py", "trailing\n.py"])
def test_unusual_filename(target, name):
    (target / name).write_text(bad_line())
    git(target, "add", name)
    result = scan(target, "--staged")
    assert result.returncode == 1
    assert name + ":1:" in result.stdout
    assert "enumerated=3 scanned=3" in result.stderr


def test_unmerged_index_is_refused(target):
    oid = git(target, "rev-parse", "HEAD:keep/clean.py").strip()
    git(target, "update-index", "--force-remove", "keep/clean.py")
    git(target, "update-index", "--index-info", input=(
        b"100644 " + oid + b" 1\tkeep/clean.py\n" +
        b"100644 " + oid + b" 2\tkeep/clean.py\n"))
    result = scan(target, "--staged")
    assert result.returncode == 2
    assert "unmerged" in result.stderr


@pytest.mark.parametrize("marker", ["committed", "untracked", "absent"])
def test_retired_marker_gate_remains_sparse_independent(repo, tmp_path, marker):
    """Retirement is authoritative: no marker grants or revokes task authority."""
    if marker != "absent":
        (repo / ".planning").mkdir()
        (repo / ".planning/marker.md").write_text("fixture\n")
        if marker == "committed":
            git(repo, "add", ".planning/marker.md")
            commit_index(repo)
    wt = tmp_path / "retired"
    git(repo, "worktree", "add", "--detach", str(wt))
    git(wt, "sparse-checkout", "set", "--cone", "keep")
    if marker != "absent":
        (wt / ".planning").mkdir(exist_ok=True)
        (wt / ".planning/marker.md").write_text("fixture\n")
    tracked = git(wt, "ls-files", ".planning/marker.md")
    assert bool(tracked) is (marker == "committed")
    for args in (["--strict"], ["--strict", "--require-issue", "3523"]):
        result = subprocess.run(["bash", str(ROOT / "scripts/enforcement/require-plan-approval.sh"),
                                 *args], cwd=wt, capture_output=True, text=True, check=False)
        assert result.returncode == 0
        assert "RETIRED" in result.stdout
        assert not (wt / ".planning/STATE.md").exists()


def snapshot(*roots):
    """Compare exact fixture bytes, including indexes, refs and object files."""
    return {path: path.read_bytes() for root in roots
            for path in root.rglob("*") if path.is_file()}


def index_git(root, index, *args):
    return subprocess.run(["git", "-C", str(root), *args],
                          env=dict(os.environ, GIT_INDEX_FILE=str(index)),
                          capture_output=True, check=True).stdout


@pytest.mark.parametrize("linked", [False, True])
@pytest.mark.parametrize("location", ["absolute", "relative", "subdirectory", "hook-bindings"])
@pytest.mark.parametrize("alternate_bad", [False, True])
def test_staged_effective_index(target, tmp_path, linked, location, alternate_bad):
    root = target
    if linked:
        root = tmp_path / "linked"
        git(target, "worktree", "add", "--detach", str(root))
        install_scanner(root)
    index = root / "selected.index"
    index_git(root, index, "read-tree", "HEAD")
    if alternate_bad:
        # This target exists only in the alternate index; enumeration matters too.
        path = root / "keep/selected.py"
        path.write_text(bad_line())
        index_git(root, index, "add", "keep/selected.py")
    else:
        path = root / "keep/clean.py"
        path.write_text(bad_line())
        git(root, "add", "keep/clean.py")
    path.write_text("print('clean')\n")
    cwd = root / "keep" if location == "subdirectory" else root
    selected = str(index) if location == "absolute" else os.path.relpath(index, cwd)
    env = dict(os.environ, GIT_INDEX_FILE=selected)
    if location == "hook-bindings":
        env.update(GIT_DIR=os.path.relpath(git(root, "rev-parse", "--absolute-git-dir")
                                         .decode().strip(), cwd), GIT_WORK_TREE=".")
    before = snapshot(target, root)
    result = scan(root, "--staged", env=env, cwd=cwd)
    assert result.returncode == (1 if alternate_bad else 0), result.stderr
    assert ("keep/selected.py:1:" in result.stdout) is alternate_bad
    count = 3 if alternate_bad else 2
    assert f"enumerated={count} scanned={count}" in result.stderr
    assert scan(root, "--head", env=env).returncode == 0
    assert scan(root, env=env).returncode == 0
    assert snapshot(target, root) == before


@pytest.mark.parametrize("state", ["missing", "corrupt", "empty", "unmerged"])
def test_staged_invalid_effective_index_is_refused(target, state):
    index = target / "selected.index"
    if state == "corrupt":
        index.write_bytes(b"invalid index fixture\n")
    elif state != "missing":
        index_git(target, index, "read-tree", "--empty" if state == "empty" else "HEAD")
        if state == "unmerged":
            oid = git(target, "rev-parse", "HEAD:keep/clean.py").strip()
            index_git(target, index, "update-index", "--force-remove", "keep/clean.py")
            subprocess.run(["git", "-C", str(target), "update-index", "--index-info"],
                           env=dict(os.environ, GIT_INDEX_FILE=str(index)),
                           input=b"100644 " + oid + b" 1\tkeep/clean.py\n",
                           capture_output=True, check=True)
    before = snapshot(target)
    result = scan(target, "--staged", env=dict(os.environ, GIT_INDEX_FILE=str(index)))
    assert result.returncode == (1 if state == "empty" else 2), result.stderr
    if state == "unmerged":
        assert "unmerged" in result.stderr
    assert snapshot(target) == before


@pytest.mark.parametrize("binding", ["cwd", "git-dir", "common-dir", "linked-worktree"])
def test_staged_foreign_index_is_not_selected(target, tmp_path, binding):
    other = tmp_path / "other"
    if binding == "linked-worktree":
        git(target, "worktree", "add", "--detach", str(other))
    else:
        git(target, "init", "-q", str(other))
    index = other / "selected.index"
    index_git(other, index, "read-tree", "--empty")
    (target / "keep/clean.py").write_text(bad_line())
    git(target, "add", "keep/clean.py")
    (target / "keep/clean.py").write_text("print('clean')\n")
    env = dict(os.environ, GIT_INDEX_FILE=str(index))
    cwd = other
    if binding == "git-dir":
        cwd = target
        env.update(GIT_DIR=str(other / ".git"), GIT_WORK_TREE=str(other))
    if binding == "common-dir":
        cwd = target
        env.update(GIT_COMMON_DIR=str(other / ".git"))
    before = snapshot(target, other)
    result = scan(target, "--staged", env=env, cwd=cwd)
    assert result.returncode == 1, result.stderr
    assert "keep/clean.py:1:" in result.stdout
    assert snapshot(target, other) == before
