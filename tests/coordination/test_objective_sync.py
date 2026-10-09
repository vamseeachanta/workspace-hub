from __future__ import annotations

from pathlib import Path

import yaml

from scripts.coordination.sync_objective_template import planned_targets, sync_templates

REPO_ROOT = Path(__file__).resolve().parents[2]


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
        (tmp_path / repo / ".git").mkdir(parents=True)

    actions = sync_templates(manifest_path, tmp_path, dry_run=True)

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

    actions = sync_templates(manifest_path, tmp_path, dry_run=False)

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
    (tmp_path / "repo-a" / ".git").mkdir(parents=True)

    actions = sync_templates(manifest_path, tmp_path, dry_run=False)
    copied = tmp_path / "repo-a" / ".github" / "ISSUE_TEMPLATE" / "objective.yml"

    assert actions[0].startswith("copied ")
    assert copied.read_text(encoding="utf-8") == (
        REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "objective.yml"
    ).read_text(encoding="utf-8")
