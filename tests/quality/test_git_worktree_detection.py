"""Repository detection against Git-created layouts, with no fixture commits.

Oracle: Git reference, rev-parse --is-inside-work-tree/--show-prefix and
gitrepository-layout, accessed 2026-10-22 (https://git-scm.com/docs).
Hand derivation: a root has valid working-tree metadata and an empty prefix;
bare repositories lack a working tree; child folders have a nonempty prefix;
ordinary directories and malformed markers have no valid metadata. Resolver
expected paths follow the documented explicit-base, nested, sibling order.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.lib.tier1_repos import resolve_tier1_repo_path

ROOT = Path(__file__).resolve().parents[2]
SHELL = ROOT / "scripts/lib/tier1-repos.sh"
INDEX = ROOT / "scripts/search/build_content_index.py"


def clean_git_env() -> dict[str, str]:
    env = os.environ.copy()
    names = subprocess.check_output(["git", "rev-parse", "--local-env-vars"], text=True)
    for name in names.splitlines():
        env.pop(name, None)
    env.pop("TIER1_REPOS_BASE", None)
    return env


def git(*args: str | Path) -> None:
    subprocess.run(
        ["git", *map(str, args)], env=clean_git_env(), check=True, capture_output=True
    )


@pytest.fixture
def layouts(tmp_path: Path) -> dict[str, Path]:
    clone = tmp_path / "primary checkout"
    linked = tmp_path / "linked checkout"
    separate = tmp_path / "separate checkout"
    bare = tmp_path / "bare"
    git("init", "-q", clone)
    git("-C", clone, "worktree", "add", "--orphan", "-b", "linked-fixture", linked)
    git("init", "-q", "--separate-git-dir", tmp_path / "metadata", separate)
    git("init", "-q", "--bare", bare)
    nested = clone / "nested"
    nested.mkdir()
    ordinary = tmp_path / "ordinary"
    ordinary.mkdir()
    malformed = tmp_path / "malformed"
    malformed.mkdir()
    (malformed / ".git").write_text("not a gitfile\n")
    empty = tmp_path / "empty metadata"
    (empty / ".git").mkdir(parents=True)
    dangling = tmp_path / "dangling"
    dangling.mkdir()
    (dangling / ".git").symlink_to(tmp_path / "absent metadata")
    return {
        "clone": clone, "linked": linked, "separate": separate, "bare": bare,
        "nested": nested, "ordinary": ordinary, "malformed": malformed,
        "empty": empty, "dangling": dangling, "missing": tmp_path / "missing",
    }


def detect(implementation: str, path: Path) -> bool:
    if implementation == "python":
        from scripts.lib.git_worktree import is_git_worktree_root

        return is_git_worktree_root(path)
    if implementation == "shell":
        result = subprocess.run(
            ["bash", "-c", 'source "$1"; is_git_worktree_root "$2"', "probe", str(SHELL), str(path)],
            capture_output=True, check=False,
        )
        return result.returncode == 0
    spec = importlib.util.spec_from_file_location("content_index_probe", INDEX)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.is_repo_root(path)


@pytest.mark.parametrize("implementation", ["python", "shell", "index"])
@pytest.mark.parametrize("kind", [
    "clone", "linked", "separate", "bare", "nested", "ordinary", "malformed",
    "empty", "dangling", "missing",
])
def test_root_detection(implementation: str, kind: str, layouts: dict[str, Path]) -> None:
    assert detect(implementation, layouts[kind]) is (kind in {"clone", "linked", "separate"})


@pytest.mark.parametrize("implementation", ["python", "shell", "index"])
def test_inherited_git_bindings_are_isolated(
    implementation: str, layouts: dict[str, Path], monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GIT_DIR", str(layouts["bare"]))
    monkeypatch.setenv("GIT_WORK_TREE", str(layouts["ordinary"]))
    monkeypatch.setenv("GIT_COMMON_DIR", str(layouts["bare"]))
    monkeypatch.setenv("GIT_INDEX_FILE", str(layouts["missing"]))
    monkeypatch.setenv("GIT_OBJECT_DIRECTORY", str(layouts["missing"]))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.bare")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "true")
    before = os.environ.copy()
    assert detect(implementation, layouts["linked"])
    assert not detect(implementation, layouts["malformed"])
    assert not detect(implementation, layouts["nested"])
    assert os.environ == before
    assert not layouts["missing"].exists()


@pytest.mark.parametrize("implementation", ["python", "shell", "index"])
def test_probe_preserves_metadata(implementation: str, layouts: dict[str, Path]) -> None:
    """A read-only probe must preserve every fixture metadata byte and path."""
    metadata = layouts["clone"] / ".git"

    def snapshot():
        return {
            str(path.relative_to(metadata)): path.read_bytes()
            for path in metadata.rglob("*") if path.is_file()
        }

    before = snapshot()
    gitfile = (layouts["linked"] / ".git").read_bytes()
    assert detect(implementation, layouts["linked"])
    assert snapshot() == before
    assert (layouts["linked"] / ".git").read_bytes() == gitfile


@pytest.mark.parametrize("implementation", ["python", "shell"])
@pytest.mark.parametrize("kind", ["clone", "linked", "separate", "malformed", "empty", "dangling", "bare"])
def test_resolver_with_git_metadata(
    implementation: str, kind: str, layouts: dict[str, Path], tmp_path: Path,
) -> None:
    target = layouts[kind]
    # Invalid metadata must not be disguised by the source-export fallback.
    if kind in {"malformed", "empty", "dangling"}:
        (target / "pyproject.toml").write_text("[project]\nname = 'fixture'\n")
    hub = tmp_path / "hub"
    hub.mkdir()
    expected = kind in {"clone", "linked", "separate"}
    if implementation == "python":
        if expected:
            assert resolve_tier1_repo_path(target.name, repo_root=hub) == target
        else:
            with pytest.raises(FileNotFoundError):
                resolve_tier1_repo_path(target.name, repo_root=hub)
    else:
        env = clean_git_env()
        env["REPO_ROOT"] = str(hub)
        result = subprocess.run(
            ["bash", "-c", 'source "$1"; resolve_tier1_repo_path "$2"', "probe", str(SHELL), target.name],
            env=env, text=True, capture_output=True, check=False,
        )
        assert (result.returncode == 0) is expected
        assert result.stdout == (str(target) if expected else "")


def test_python_probe_fails_closed_without_git(layouts: dict[str, Path], monkeypatch) -> None:
    from scripts.lib.git_worktree import is_git_worktree_root

    def unavailable(*args, **kwargs):
        raise FileNotFoundError("git unavailable")

    monkeypatch.setattr(subprocess, "run", unavailable)
    assert not is_git_worktree_root(layouts["linked"])


def test_content_index_direct_invocation(layouts: dict[str, Path], tmp_path: Path) -> None:
    """Only the linked root is inside this scan; no counts from the implementation."""
    (layouts["linked"] / "README.md").write_text("# Fixture\n")
    output_json = tmp_path / "index.json"
    output_md = tmp_path / "index.md"
    result = subprocess.run(
        [sys.executable, str(INDEX), "--root", str(layouts["linked"]),
         "--output-json", str(output_json), "--output-md", str(output_md)],
        cwd=tmp_path, env=clean_git_env(), text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(output_json.read_text()) == {
        str(layouts["linked"]): {
            "disciplines": [], "project_files": [], "key_docs": ["README.md"],
        }
    }
    assert output_md.read_text().startswith("<!-- tier1-raw-inventory-banner:")


@pytest.mark.parametrize("override", [False, True])
def test_tier1_list_direct_invocation(tmp_path: Path, override: bool) -> None:
    env = clean_git_env()
    env.pop("PYTHONPATH", None)
    env.pop("REPO_ROOT", None)
    env.pop("TIER1_REPOS_FILE", None)
    if override:
        source = tmp_path / "repos.txt"
        source.write_text("# Fixture\nexample-repo\n")
        env["TIER1_REPOS_FILE"] = str(source)
    else:
        source = ROOT / "config/tier1-python-repos.txt"
    expected = [line.split("#")[0].strip() for line in source.read_text().splitlines()]
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/lib/tier1_repos.py")],
        cwd=tmp_path, env=env, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [line for line in expected if line]
