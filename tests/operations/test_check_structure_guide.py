"""Exercise the file structure guide CLI against isolated Git repositories."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml


CHECKER = Path(__file__).resolve().parents[2] / "scripts/operations/check-structure-guide.py"


def execute(directory, *args, check=False, bindings=None):
    environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    environment.update(bindings or {})
    return subprocess.run(
        args, cwd=directory, env=environment, text=True, encoding="utf-8",
        capture_output=True, check=check,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


@pytest.fixture
def repo(tmp_path):
    directory = tmp_path / "fixture repo"
    directory.mkdir()
    execute(directory, "git", "init", "-q", check=True)
    (directory / "docs").mkdir()
    return directory


def guide(repo, entries, filename="docs/structure.yaml"):
    document = {
        "version": 1, "depth": 2, "ignore": [".git", "cache"],
        "entries": [{"path": "docs/", "purpose": "Project documentation"}, *entries],
    }
    path = repo / filename
    path.write_text(yaml.safe_dump(document), encoding="utf-8")
    return path


def invoke(repo, *args, bindings=None):
    return execute(repo.parent, sys.executable, CHECKER, repo, *args, bindings=bindings)


def findings(result):
    assert result.returncode == 1, (result.stdout, result.stderr)
    records = json.loads(result.stdout)["findings"]
    return {(item["kind"], item["path"].rstrip("/")) for item in records}


def test_discovers_tracked_untracked_and_empty_directories(repo):
    (repo / ".gitignore").write_text("build/\nindexed/\n", encoding="utf-8")
    for directory in ("build/output", "indexed/child", "src/new/inherited", "src/cache", "empty"):
        (repo / directory).mkdir(parents=True)
    (repo / "indexed/child/input.txt").touch()
    execute(repo, "git", "add", "-f", "indexed/child/input.txt", check=True)
    (repo / "src/new/file.txt").touch()
    guide(repo, [{"path": "src/", "purpose": "Source"}])
    assert findings(invoke(repo, "--json")) == {
        ("undocumented", "indexed"), ("undocumented", "indexed/child"),
        ("undocumented", "src/new"), ("undocumented", "empty"),
    }


def test_stale_entries_and_blank_or_absent_purposes(repo):
    (repo / "src").mkdir()
    (repo / "examples").mkdir()
    guide(repo, [
        {"path": "removed/", "purpose": "Previous inputs"},
        {"path": "src/", "purpose": "   "}, {"path": "examples/"},
    ])
    expected = {
        ("stale entry", "removed"), ("missing purpose", "src"),
        ("missing purpose", "examples"),
    }
    assert findings(invoke(repo, "--json")) == expected
    result = invoke(repo)
    assert result.returncode == 1
    for kind, path in expected:
        assert kind in result.stdout and path in result.stdout


def test_indexed_directory_removed_from_disk_is_stale(repo):
    folder = repo / "removed"
    folder.mkdir()
    source = folder / "input.txt"
    source.touch()
    execute(repo, "git", "add", "removed/input.txt", check=True)
    source.unlink()
    folder.rmdir()
    guide(repo, [{"path": "removed/", "purpose": "Inputs"}])
    assert findings(invoke(repo, "--json")) == {("stale entry", "removed")}


def test_inherited_git_bindings_do_not_override_target(repo):
    caller = repo.parent / "caller"
    caller.mkdir()
    execute(caller, "git", "init", "-q", check=True)
    (caller / "private").mkdir()
    (caller / "private/input.txt").touch()
    execute(caller, "git", "add", "private/input.txt", check=True)
    index = caller / ".git/index"
    before = index.read_bytes()
    guide(repo, [])
    result = invoke(repo, "--json", bindings={
        "GIT_DIR": str(caller / ".git"), "GIT_WORK_TREE": str(caller),
        "GIT_COMMON_DIR": str(caller / ".git"), "GIT_INDEX_FILE": str(index),
    })
    assert result.returncode == 0, (result.stdout, result.stderr)
    assert json.loads(result.stdout)["findings"] == []
    assert index.read_bytes() == before
    assert (caller / "private/input.txt").read_bytes() == b""


@pytest.mark.parametrize("content", [None, "entries: [", "[]"])
def test_unreadable_guide(repo, content):
    if content is not None:
        (repo / "docs/structure.yaml").write_text(content, encoding="utf-8")
    result = invoke(repo, "--json")
    assert result.returncode == 1, result.stderr
    assert {item["kind"] for item in json.loads(result.stdout)["findings"]} == {"unreadable guide"}


def test_alternate_guide_renders_complete_table(repo):
    (repo / "src").mkdir()
    path = guide(repo, [{
        "path": "src/", "purpose": "Library | tools", "owner": "engineering",
        "rules": ["Review changes", "Run checks"],
    }], filename="custom.yaml")
    result = invoke(repo, "--guide", path, "--render", "--json")
    assert result.returncode == 0, (result.stdout, result.stderr)
    assert json.loads(result.stdout)["findings"] == []
    markdown = (repo / "docs/STRUCTURE.md").read_text(encoding="utf-8")
    header = next(line for line in markdown.splitlines() if line.startswith("|"))
    assert [cell.strip().lower() for cell in header.strip("|").split("|")] == [
        "path", "purpose", "owner", "rules",
    ]
    for value in ("docs/", "Project documentation", "src/", "Library", "tools",
                  "engineering", "Review changes", "Run checks"):
        assert value in markdown
