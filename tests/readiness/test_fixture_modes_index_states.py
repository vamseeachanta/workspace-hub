"""Native regular-file content and merge stages must preserve fixture readback.

Mode literals and stage zero follow Git 2.44.0 gitformat-index, Index entry:
https://git-scm.com/docs/gitformat-index/2.44.0
The index-info example defines removal with mode zero and stages 1, 2 and 3:
https://git-scm.com/docs/git-update-index/2.44.0#_using_index_info
Porcelain v1 XY uses X for index changes, Y for working-tree changes, and UU
for both-modified conflicts (git-status, Porcelain Format Version 1):
https://git-scm.com/docs/git-status/2.44.0#_porcelain_format_version_1
Expected records below are handwritten from those contracts; content identities
come from separately retained synthetic inputs, never from the mode checker.
"""

import os
import stat
import subprocess

import pytest
from fixture_modes import assert_file_modes, prepare_file_mode
from test_sibling_sso_native_preflight import git, native_repo

pytestmark = pytest.mark.skipif(
    os.name == "nt", reason="POSIX physical mode coverage requires a native filesystem"
)

# Independent physical/index mode pairs from the cited index-format contract.
MODES = [(False, 0o644, "100644"), (True, 0o755, "100755")]
ORIGINAL = "original synthetic content\n"
STAGED = "staged synthetic content\n"
WORKTREE = "working-tree synthetic content\n"
RELATIVE = "control.txt"


def git_input(repo, *args, content):
    """native_repo has already isolated inherited Git bindings/configuration."""
    return subprocess.run(
        ["git", *args], cwd=repo, input=content, text=True,
        capture_output=True, check=True,
    ).stdout


def blob_id(repo, content):
    return git_input(repo, "hash-object", "--stdin", content=content).strip()


def index_records(repo):
    return git(repo, "ls-files", "--stage", "-z", "--", RELATIVE)


def owned_status(repo):
    return git(
        repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", RELATIVE
    )


def check_preserving(repo, path, executable, error=None):
    """Check raw index bytes and physical bytes/mode around every invocation."""
    index = repo / git(repo, "rev-parse", "--git-path", "index").strip()
    before = path.read_bytes(), path.stat().st_mode, index.read_bytes()
    try:
        if error is None:
            assert_file_modes(repo, RELATIVE, executable=executable)
        else:
            with pytest.raises(AssertionError, match=error):
                assert_file_modes(repo, RELATIVE, executable=executable)
    finally:
        assert (path.read_bytes(), path.stat().st_mode, index.read_bytes()) == before


@pytest.fixture(params=MODES, ids=["nonexecutable", "executable"])
def clean_regular_file(tmp_path, monkeypatch, request):
    executable, physical, indexed = request.param
    _, repo = native_repo(monkeypatch, tmp_path)
    path = repo / RELATIVE
    path.write_text(ORIGINAL)
    prepare_file_mode(path, executable=executable)
    # Commit only inside the disposable repository; no implicit checker calls.
    git(repo, "add", "-A")
    git(repo, "commit", "-m", "synthetic fixture")

    assert stat.S_ISREG(path.stat().st_mode)
    assert stat.S_IMODE(path.stat().st_mode) == physical
    assert git(repo, "config", "--get", "core.filemode").strip() == "true"
    original = blob_id(repo, ORIGINAL)
    assert git(repo, "rev-parse", f"HEAD:{RELATIVE}").strip() == original
    assert git(repo, "hash-object", "--", RELATIVE).strip() == original
    assert index_records(repo) == f"{indexed} {original} 0\t{RELATIVE}\0"
    assert owned_status(repo) == ""
    check_preserving(repo, path, executable)
    return repo, path, executable, physical, indexed, original


def assert_content_state(fixture, worktree_content, status):
    repo, path, _executable, physical, indexed, original = fixture
    staged = blob_id(repo, STAGED)
    working = blob_id(repo, worktree_content)
    head = git(repo, "rev-parse", f"HEAD:{RELATIVE}").strip()
    index = git(repo, "rev-parse", f":0:{RELATIVE}").strip()
    worktree = git(repo, "hash-object", "--", RELATIVE).strip()
    assert (head, index, worktree) == (original, staged, working)
    assert index != head
    assert worktree != head
    assert (worktree == index) == (worktree_content == STAGED)
    assert stat.S_IMODE(path.stat().st_mode) == physical
    assert index_records(repo) == f"{indexed} {staged} 0\t{RELATIVE}\0"
    assert owned_status(repo) == f"{status} {RELATIVE}\0"


def test_staged_content_dirt_is_rejected(clean_regular_file):
    repo, path, executable, *_ = clean_regular_file
    path.write_text(STAGED)
    git(repo, "add", "--", RELATIVE)
    assert_content_state(clean_regular_file, STAGED, "M ")
    check_preserving(repo, path, executable, "owned path is dirty")


def test_staged_and_worktree_dirt_is_rejected(clean_regular_file):
    repo, path, executable, *_ = clean_regular_file
    path.write_text(STAGED)
    git(repo, "add", "--", RELATIVE)
    path.write_text(WORKTREE)
    assert_content_state(clean_regular_file, WORKTREE, "MM")
    check_preserving(repo, path, executable, "owned path is dirty")


def test_unmerged_index_stages_are_rejected(clean_regular_file):
    repo, path, executable, physical, indexed, original = clean_regular_file
    # Stage numbers and removal syntax follow the cited index-info example.
    stages = [("1", ORIGINAL), ("2", STAGED), ("3", WORKTREE)]
    blobs = [
        (stage, git_input(repo, "hash-object", "-w", "--stdin", content=content).strip())
        for stage, content in stages
    ]
    assert len({blob for _stage, blob in blobs}) == len(stages)
    assert blobs == [(stage, blob_id(repo, content)) for stage, content in stages]
    assert git(repo, "rev-parse", f"HEAD:{RELATIVE}").strip() == original
    records = "".join(f"{indexed} {blob} {stage}\t{RELATIVE}\n" for stage, blob in blobs)
    git_input(
        repo, "update-index", "--index-info",
        content=f"0 {original}\t{RELATIVE}\n" + records,
    )
    # Exact output excludes any stage-zero entry or additional stage record.
    assert index_records(repo) == records.replace("\n", "\0")
    assert stat.S_IMODE(path.stat().st_mode) == physical
    assert git(repo, "hash-object", "--", RELATIVE).strip() == original
    assert owned_status(repo) == f"UU {RELATIVE}\0"
    check_preserving(repo, path, executable, "expected one indexed regular fixture file")


def test_clean_stage_zero_control(clean_regular_file):
    repo, path, executable, _physical, indexed, original = clean_regular_file
    assert index_records(repo) == f"{indexed} {original} 0\t{RELATIVE}\0"
    assert owned_status(repo) == ""
    check_preserving(repo, path, executable)
