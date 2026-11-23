from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from scripts.coordination.sync_objective_template import planned_targets, sync_templates
from scripts.coordination.sync_objective_template import main as sync_main

REPO_ROOT = Path(__file__).resolve().parents[2]


def _init_repo(path: Path, branch: str = "main") -> None:
    path.mkdir(parents=True)
    subprocess.run(
        ["git", "init", "-b", branch], cwd=path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.invalid"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    (path / "README.md").write_text("fixture\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "README.md"], cwd=path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "fixture"],
        cwd=path,
        check=True,
        capture_output=True,
    )


def test_objective_sync_manifest_targets_canonical_repos() -> None:
    manifest = yaml.safe_load(
        (REPO_ROOT / "config" / "objective-intake-sync.yml").read_text(encoding="utf-8")
    )

    assert manifest["source"] == ".github/ISSUE_TEMPLATE/objective.yml"
    assert manifest["sync_mode"] == "active-via-helper"
    assert {
        "workspace-hub",
        "digitalmodel",
        "assetutilities",
        "worldenergydata",
        "raw-to-knowledge-playbook",
        "aceengineer-agents",
    } <= set(manifest["canonical_repos"])


def test_objective_sync_dry_run_lists_copy_actions(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.yml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "source": ".github/ISSUE_TEMPLATE/objective.yml",
                "destination": ".github/ISSUE_TEMPLATE/objective.yml",
                "canonical_repos": ["repo-a", "repo-b"],
            }
        ),
        encoding="utf-8",
    )
    for repo in ("repo-a", "repo-b"):
        _init_repo(tmp_path / repo)

    actions = sync_templates(manifest_path, tmp_path)

    assert len(actions) == 2
    assert actions[0].startswith("would-copy ")
    assert "repo-a/.github/ISSUE_TEMPLATE/objective.yml" in actions[0]


def test_objective_sync_refuses_missing_repositories(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.yml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "source": ".github/ISSUE_TEMPLATE/objective.yml",
                "destination": ".github/ISSUE_TEMPLATE/objective.yml",
                "canonical_repos": ["missing-repo"],
            }
        ),
        encoding="utf-8",
    )

    actions = sync_templates(manifest_path, tmp_path, apply=True)

    assert actions == [f"missing-repo {tmp_path / 'missing-repo'}"]
    assert not (tmp_path / "missing-repo").exists()


def test_objective_sync_copies_to_existing_git_repo(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.yml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "source": ".github/ISSUE_TEMPLATE/objective.yml",
                "destination": ".github/ISSUE_TEMPLATE/objective.yml",
                "canonical_repos": ["repo-a"],
            }
        ),
        encoding="utf-8",
    )
    _init_repo(tmp_path / "repo-a")

    actions = sync_templates(manifest_path, tmp_path, apply=True)
    copied = tmp_path / "repo-a" / ".github" / "ISSUE_TEMPLATE" / "objective.yml"

    assert actions[0].startswith("copied ")
    assert copied.read_text(encoding="utf-8") == (
        REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "objective.yml"
    ).read_text(encoding="utf-8")


def test_objective_sync_default_is_dry_run(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.yml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "source": ".github/ISSUE_TEMPLATE/objective.yml",
                "destination": ".github/ISSUE_TEMPLATE/objective.yml",
                "canonical_repos": ["repo-a"],
            }
        ),
        encoding="utf-8",
    )
    _init_repo(tmp_path / "repo-a")

    actions = sync_templates(manifest_path, tmp_path)
    copied = tmp_path / "repo-a" / ".github" / "ISSUE_TEMPLATE" / "objective.yml"

    assert actions[0].startswith("would-copy ")
    assert not copied.exists()


def test_objective_sync_cli_accepts_explicit_dry_run(tmp_path: Path, capsys) -> None:
    manifest_path = tmp_path / "manifest.yml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "source": ".github/ISSUE_TEMPLATE/objective.yml",
                "destination": ".github/ISSUE_TEMPLATE/objective.yml",
                "canonical_repos": ["repo-a"],
            }
        ),
        encoding="utf-8",
    )
    _init_repo(tmp_path / "repo-a")

    assert sync_main(
        [
            "--manifest",
            str(manifest_path),
            "--workspace-root",
            str(tmp_path),
            "--dry-run",
        ]
    ) == 0

    assert "would-copy " in capsys.readouterr().out


def test_objective_sync_apply_skips_dirty_repo(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.yml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "source": ".github/ISSUE_TEMPLATE/objective.yml",
                "destination": ".github/ISSUE_TEMPLATE/objective.yml",
                "canonical_repos": ["repo-a"],
            }
        ),
        encoding="utf-8",
    )
    repo = tmp_path / "repo-a"
    _init_repo(repo)
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    actions = sync_templates(manifest_path, tmp_path, apply=True)

    assert actions == [f"skip-dirty {repo}"]


def test_objective_sync_apply_skips_non_default_branch(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.yml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "source": ".github/ISSUE_TEMPLATE/objective.yml",
                "destination": ".github/ISSUE_TEMPLATE/objective.yml",
                "canonical_repos": ["repo-a"],
            }
        ),
        encoding="utf-8",
    )
    repo = tmp_path / "repo-a"
    _init_repo(repo)
    subprocess.run(
        ["git", "checkout", "-b", "feature/test"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    actions = sync_templates(manifest_path, tmp_path, apply=True)

    assert actions == [f"skip-non-default-branch {repo} feature/test default=main"]
