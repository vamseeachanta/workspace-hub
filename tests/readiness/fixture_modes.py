"""Mode contracts for disposable Git fixtures; never change Git portability policy.

Source: Git 2.44.0 gitformat-index, Index entry mode field:
https://git-scm.com/docs/gitformat-index/2.44.0
regular-file permissions are 644 or 755. Physical permission bits are checked
separately because changing the index cannot chmod a working-tree file.
"""
import os
import stat
import subprocess
from pathlib import Path

# Git's regular-file modes, per the index-format source above.
MODES = {False: (0o644, "100644"), True: (0o755, "100755")}


def git(repo: Path, *args: str) -> str:
    """Keep caller repository bindings and user Git configuration out of fixtures."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return subprocess.run(
        ["git", "-C", str(repo), *args], env=env, check=True,
        capture_output=True, text=True,
    ).stdout


def prepare_file_mode(path: Path, *, executable: bool) -> None:
    """Set physical permissions before the fixture stages and commits the file."""
    assert path.is_file() and not path.is_symlink(), "expected regular fixture file"
    path.chmod(MODES[executable][0])


def assert_file_modes(repo: Path, relative: str, *, executable: bool) -> None:
    """Require physical mode, index mode and clean owned-path status on POSIX."""
    assert os.name != "nt", "Windows mode checks provide limited native coverage"
    physical, indexed = MODES[executable]
    path = repo / relative
    assert path.is_file() and not path.is_symlink(), "expected regular fixture file"
    assert stat.S_IMODE(path.stat().st_mode) == physical, "physical mode mismatch"
    assert git(repo, "config", "--get", "core.filemode").strip() == "true", (
        "native fixture requires core.filemode=true"
    )
    entries = git(repo, "ls-files", "--stage", "-z", "--", relative).split("\0")
    entries = [entry for entry in entries if entry]
    assert len(entries) == 1, "expected one indexed regular fixture file"
    metadata, name = entries[0].split("\t", 1)
    mode, _, stage = metadata.split()
    assert mode == indexed and stage == "0" and name == relative, "index mode mismatch"
    assert not git(repo, "status", "--porcelain=v1", "--untracked-files=all", "--", relative), (
        "owned path is dirty"
    )
