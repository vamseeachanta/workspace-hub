import os
import subprocess
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "skills" / "merge-submodule-skills.sh"


def write_skill(path: Path, body: str = "# Test skill\n") -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(body, encoding="utf-8")


def run_merge(workspace: Path, manifest: Path, report: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "WORKSPACE_HUB_ROOT": str(workspace),
            "WORKSPACE_HUB_SKILLS_ROOT": str(workspace / ".claude" / "skills"),
            "WORKSPACE_HUB_SKILL_REPO_MANIFEST": str(manifest),
        }
    )
    return subprocess.run(
        ["bash", str(SCRIPT), "--report-file", str(report)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_merge_discovers_nested_internal_skill_trees(tmp_path: Path) -> None:
    workspace = tmp_path / "hub"
    manifest = tmp_path / "repos.txt"
    report = tmp_path / "report.yaml"
    manifest.write_text("digitalmodel\n", encoding="utf-8")

    write_skill(workspace / "digitalmodel" / ".claude" / "skills" / "engineering" / "orcaflex-fatigue")

    result = run_merge(workspace, manifest, report)

    assert result.returncode == 0, result.stderr
    data = yaml.safe_load(report.read_text(encoding="utf-8"))
    actions = data["actions"]
    assert any(
        action["repo"] == "digitalmodel"
        and action["skill"] == "orcaflex-fatigue"
        and action["source_path"].endswith("engineering/orcaflex-fatigue")
        and action["action"] == "create"
        for action in actions
    )


def test_merge_reports_manifest_missing_repos_with_reasons(tmp_path: Path) -> None:
    workspace = tmp_path / "hub"
    manifest = tmp_path / "repos.txt"
    report = tmp_path / "report.yaml"
    manifest.write_text("digitalmodel\nworldenergydata\n", encoding="utf-8")
    write_skill(workspace / "digitalmodel" / ".claude" / "skills" / "orcaflex-analysis")

    result = run_merge(workspace, manifest, report)

    assert result.returncode == 0, result.stderr
    data = yaml.safe_load(report.read_text(encoding="utf-8"))
    assert {
        "repo": "worldenergydata",
        "path": str(workspace / "worldenergydata" / ".claude" / "skills"),
        "reason": "expected repo missing .claude/skills directory",
    } in data["skipped_repos"]


def test_merge_skips_dirty_repos_with_reason(tmp_path: Path) -> None:
    workspace = tmp_path / "hub"
    manifest = tmp_path / "repos.txt"
    report = tmp_path / "report.yaml"
    repo = workspace / "digitalmodel"
    manifest.write_text("digitalmodel\n", encoding="utf-8")
    write_skill(repo / ".claude" / "skills" / "orcaflex-analysis")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)

    result = run_merge(workspace, manifest, report)

    assert result.returncode == 0, result.stderr
    data = yaml.safe_load(report.read_text(encoding="utf-8"))
    assert data["summary"]["dirty_repos"] == 1
    assert data["skipped_repos"][0]["repo"] == "digitalmodel"
    assert data["skipped_repos"][0]["reason"] == "repo has uncommitted changes"
    assert data["actions"] == []


def test_merge_reports_skipped_template_dirs_with_reasons(tmp_path: Path) -> None:
    workspace = tmp_path / "hub"
    manifest = tmp_path / "repos.txt"
    report = tmp_path / "report.yaml"
    manifest.write_text("digitalmodel\n", encoding="utf-8")
    write_skill(workspace / "digitalmodel" / ".claude" / "skills" / "_internal" / "shared-helper")
    write_skill(workspace / "digitalmodel" / ".claude" / "skills" / "orcaflex-analysis")

    result = run_merge(workspace, manifest, report)

    assert result.returncode == 0, result.stderr
    data = yaml.safe_load(report.read_text(encoding="utf-8"))
    assert any(
        skipped["repo"] == "digitalmodel"
        and skipped["path"].endswith("_internal")
        and skipped["reason"] == "matched shared/template skip pattern: _internal"
        for skipped in data["skipped_skills"]
    )
