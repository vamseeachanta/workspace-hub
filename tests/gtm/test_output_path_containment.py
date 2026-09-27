"""A private output directory may not reach into the public repository (C19b Codex r1).

``check_private_dir`` and the weekly wrapper used to resolve the path and then test
containment, so a symlink or junction located under the public repository that
points outside passed. Both the lexical absolute path and the resolved path are
now compared with both spellings of the repository root (case-insensitively on
Windows), a path component that is a link under the repository is refused, and a
'..' component is refused outright.

Every path here is a temporary directory; nothing touches the real repository.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.lib import private_overlay

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "scripts" / "lib" / "private_path_guard.sh"


def _link(link: Path, target: Path) -> None:
    """Directory junction on Windows (no privilege needed), symlink elsewhere."""
    if os.name == "nt":
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


@pytest.fixture
def layout(tmp_path):
    repo = tmp_path / "PublicRepo"
    (repo / "inner").mkdir(parents=True)
    outside = tmp_path / "outside"
    (outside / "gtm").mkdir(parents=True)
    _link(repo / "link", outside)            # under the repo, points outside
    _link(tmp_path / "alias", repo / "inner")  # outside the repo, points inside
    _link(tmp_path / "rootalias", repo)        # a second spelling of the repo root
    return {"tmp": tmp_path, "repo": repo, "outside": outside}


def _refused(value, root, tmp: Path) -> str:
    with pytest.raises(private_overlay.PrivateOverlayError) as exc:
        private_overlay.check_private_dir(value, "'outputs.job_market_dir'", root)
    msg = str(exc.value)
    assert str(tmp) not in msg and "outputs.job_market_dir" in msg
    return msg


# --------------------------------------------------------------------------
# Python helper
# --------------------------------------------------------------------------
def test_directory_reached_through_a_link_under_the_repo_is_refused(layout):
    _refused(layout["repo"] / "link" / "gtm", layout["repo"], layout["tmp"])


def test_link_under_the_repo_itself_is_refused(layout):
    _refused(layout["repo"] / "link", layout["repo"], layout["tmp"])


def test_link_outside_the_repo_resolving_inside_is_refused(layout):
    _refused(layout["tmp"] / "alias", layout["repo"], layout["tmp"])


def test_repo_root_given_through_a_link_still_contains(layout):
    _refused(layout["repo"] / "inner", layout["tmp"] / "rootalias", layout["tmp"])
    _refused(layout["tmp"] / "rootalias" / "inner", layout["repo"], layout["tmp"])


def test_dotdot_component_is_refused(layout):
    value = str(layout["repo"] / "link") + os.sep + ".." + os.sep + "outside" + os.sep + "gtm"
    _refused(value, layout["repo"], layout["tmp"])


def test_real_directory_outside_the_repo_is_accepted(layout):
    out = private_overlay.check_private_dir(layout["outside"] / "gtm", "k", layout["repo"])
    assert out == (layout["outside"] / "gtm").resolve()


@pytest.mark.skipif(os.name != "nt", reason="case-insensitive comparison is Windows-only")
def test_containment_ignores_case_on_windows(layout):
    upper_root = str(layout["repo"]).upper()
    _refused(layout["repo"] / "inner", upper_root, layout["tmp"])
    assert private_overlay.is_within(str(layout["repo"] / "inner").lower(), upper_root)


def test_is_within_is_component_wise():
    base = os.path.abspath(os.sep + "synthetic-root")
    assert private_overlay.is_within(base, base)
    assert private_overlay.is_within(os.path.join(base, "a"), base)
    assert not private_overlay.is_within(base + "-sibling", base)


# --------------------------------------------------------------------------
# shell guard used by weekly-scan-refresh.sh
# --------------------------------------------------------------------------
def _find_bash():
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    for candidate in (Path(program_files) / "Git" / "bin" / "bash.exe",):
        if candidate.is_file():
            return str(candidate)
    found = shutil.which("bash")
    if found and "system32" not in found.lower():
        return found
    return None


def _guard(directory, repo) -> int:
    bash = _find_bash()
    if bash is None:
        pytest.skip("git-bash not found")
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")}
    as_posix = lambda p: str(p).replace("\\", "/")  # noqa: E731
    proc = subprocess.run(
        [bash, "-c", 'source "$0" && private_path_outside_repo "$1" "$2"',
         as_posix(GUARD), as_posix(directory), as_posix(repo)],
        capture_output=True, text=True, env=env, timeout=60,
    )
    assert str(directory) not in proc.stdout + proc.stderr
    return proc.returncode


def test_shell_guard_refuses_a_link_under_the_repo(layout):
    assert _guard(layout["repo"] / "link" / "gtm", layout["repo"]) != 0
    assert _guard(layout["repo"] / "link", layout["repo"]) != 0


def test_shell_guard_refuses_inside_and_aliases(layout):
    assert _guard(layout["repo"] / "inner", layout["repo"]) != 0
    assert _guard(layout["tmp"] / "alias", layout["repo"]) != 0
    assert _guard(layout["repo"] / "inner", layout["tmp"] / "rootalias") != 0


def test_shell_guard_refuses_dotdot_and_relative(layout):
    assert _guard(str(layout["repo"] / "link") + "/../outside/gtm", layout["repo"]) != 0
    assert _guard("relative/dir", layout["repo"]) != 0


@pytest.mark.skipif(os.name != "nt", reason="case-insensitive comparison is Windows-only")
def test_shell_guard_ignores_case_on_windows(layout):
    assert _guard(str(layout["repo"] / "inner").upper(), layout["repo"]) != 0


def test_shell_guard_accepts_a_real_outside_directory(layout):
    assert _guard(layout["outside"] / "gtm", layout["repo"]) == 0


def test_weekly_wrapper_uses_the_guard_for_both_checks():
    text = (REPO_ROOT / "scripts" / "gtm" / "weekly-scan-refresh.sh").read_text(encoding="utf-8")
    assert "private_path_guard.sh" in text
    assert text.count("private_path_outside_repo") >= 2
    assert 'case "$OUT_REAL/" in' not in text
