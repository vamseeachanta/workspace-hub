"""Git 2.43 githooks: repository-local variables are exported by Git hooks.

Independent oracle: each script is two directory levels below its repository
root. Its root must equal that fixture root, never the scripts/testing folder.
The interrupted fixture has two HEAD leaves and zero index entries: review
must stop before argument processing or any provider invocation.
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


@pytest.mark.parametrize("script", ["review/cross-review.sh", "review/plan-review-fanout.sh",
                                    "enforcement/require-plan-review.sh",
                                    "enforcement/require-cross-review.sh",
                                    "enforcement/require-verify-artifacts.sh"])
def test_review_refuses_interrupted_worktree(repo, tmp_path, script):
    wt = tmp_path / "broken"
    git(repo, "worktree", "add", "--detach", "--no-checkout", str(wt))
    result = subprocess.run(["bash", str(ROOT / "scripts" / script)],
                            cwd=wt, capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert "empty index" in result.stderr


@pytest.mark.parametrize("script", ["run-all-tests.sh", "run-benchmarks.sh",
                                    "run-cross-repo-integration.sh", "refresh-fixtures.sh"])
@pytest.mark.parametrize("work_tree", [False, True])
def test_roots_in_real_linked_worktree(repo, tmp_path, script, work_tree):
    wt = tmp_path / "linked"
    git(repo, "worktree", "add", "--detach", str(wt))
    for name in (f"scripts/testing/{script}", "scripts/lib/tier1-repos.sh",
                 "config/tier1-python-repos.txt"):
        dest = wt / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    private = git(wt, "rev-parse", "--absolute-git-dir").decode().strip()
    env = dict(os.environ, GIT_DIR=private)
    if work_tree:
        env["GIT_WORK_TREE"] = "."
    result = subprocess.run(["bash", "-x", str(wt / "scripts/testing" / script),
                             "--invalid-fixture-option"], cwd=wt / "scripts/testing",
                            env=env, capture_output=True, text=True, check=False)
    assert f"+ REPO_ROOT={wt}\n" in result.stderr
    assert "scripts/testing/scripts/lib" not in result.stderr
