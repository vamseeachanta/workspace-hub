"""Instruction lookup regressions; fixtures do not qualify a live owner or lock."""
import os
from pathlib import Path
import re
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]


def git(cwd, *args):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.check_output(["git", "-C", str(cwd), *args], env=env, text=True)


def test_authority_route_resolves_inside_hub():
    line = next(line for line in (ROOT / "AGENTS.md").read_text().splitlines()
                if line.startswith("- Authority routing:"))
    targets = re.findall(r"[\w./-]+\.md", line)
    assert len(targets) >= 2
    for target in targets:
        path = (ROOT / target).resolve()
        assert path.is_relative_to(ROOT.resolve()) and path.is_file(), target


@pytest.mark.parametrize("owner_present", [True, False])
def test_coordination_lookup_from_linked_worktree(tmp_path, monkeypatch, owner_present):
    line = next(line for line in (ROOT / "AGENTS.md").read_text().splitlines()
                if line.startswith("- Classify execution"))
    assert "git worktree list --porcelain" in line and "first record" in line
    assert "inherited Git bindings cleared" in line
    assert "bare primary unsupported" in line and "missing owner reported" in line
    targets = re.findall(r"\.\./llm-wiki/[\w./-]+", line)
    assert len(targets) == 2
    primary = tmp_path / "workspace" / "hub with spaces"
    primary.mkdir(parents=True)
    git(primary, "-c", "init.templateDir=", "init", "-q")
    git(primary, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "-c", f"core.hooksPath={tmp_path / 'no-hooks'}",
        "commit", "--allow-empty", "-qm", "Synthetic fixture")
    linked = tmp_path / "isolated" / "hub"
    linked.parent.mkdir()
    git(primary, "worktree", "add", "--detach", str(linked), "HEAD")
    if owner_present:
        for relative in targets:
            path = primary / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Synthetic owner fixture\n")
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    git(foreign, "-c", "init.templateDir=", "init", "-q")
    monkeypatch.setenv("GIT_DIR", str(foreign / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(foreign))
    monkeypatch.setenv("GIT_COMMON_DIR", str(foreign / ".git"))
    contaminated = subprocess.check_output(
        ["git", "-C", str(linked), "worktree", "list", "--porcelain"], text=True)
    assert Path(contaminated.splitlines()[0].removeprefix("worktree ")).resolve() == foreign
    first = git(linked, "worktree", "list", "--porcelain").split("\n\n")[0]
    assert "\nbare" not in first
    actual = Path(first.splitlines()[0].removeprefix("worktree ")).resolve()
    assert actual == primary.resolve()
    assert all((actual / target).is_file() == owner_present for target in targets)
    assert all(not (linked / target).exists() for target in targets)
