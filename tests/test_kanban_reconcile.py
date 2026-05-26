from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/kanban/reconcile.py"


def load_reconcile():
    spec = importlib.util.spec_from_file_location("kanban_reconcile", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def seed_kanban(root: Path) -> Path:
    kanban = root / ".claude/memory/kanban"
    write_yaml(
        kanban / "manifest.yaml",
        {
            "manifest": {
                "boards": [
                    {
                        "slug": "repo-workspace-hub",
                        "tier": "repo",
                        "repo": "vamseeachanta/workspace-hub",
                        "file": "boards/repo-workspace-hub.yaml",
                        "children": ["repo-workspace-hub-ops"],
                    },
                    {
                        "slug": "repo-workspace-hub-ops",
                        "tier": "domain",
                        "repo": "vamseeachanta/workspace-hub",
                        "domain": "ops",
                        "parent_slug": "repo-workspace-hub",
                        "file": "boards/repo-workspace-hub-ops.yaml",
                    },
                ]
            }
        },
    )
    write_yaml(
        kanban / "domains.yaml",
        {
            "repos": {
                "vamseeachanta/workspace-hub": {
                    "board": "repo-workspace-hub",
                    "domains": [{"name": "ops", "status": "existing"}],
                }
            }
        },
    )
    write_yaml(
        kanban / "boards/repo-workspace-hub.yaml",
        {
            "board": {
                "slug": "repo-workspace-hub",
                "tier": "repo",
                "repo": "vamseeachanta/workspace-hub",
                "workspace_path": "/mnt/local-analysis/workspace-hub",
            },
            "cards": [],
        },
    )
    write_yaml(
        kanban / "boards/repo-workspace-hub-ops.yaml",
        {
            "board": {
                "slug": "repo-workspace-hub-ops",
                "tier": "domain",
                "repo": "vamseeachanta/workspace-hub",
                "domain": "ops",
                "parent_slug": "repo-workspace-hub",
                "workspace_path": "/mnt/local-analysis/workspace-hub",
            },
            "cards": [],
        },
    )
    return kanban


def issue(number: int, title: str, state: str = "OPEN", labels: list[str] | None = None) -> dict:
    return {
        "number": number,
        "title": title,
        "state": state,
        "labels": [{"name": name} for name in (labels or [])],
    }


def test_dry_run_moves_domain_labeled_issue_and_keeps_key_unique(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    key = "gh:vamseeachanta/workspace-hub#2802"
    repo_board = kanban / "boards/repo-workspace-hub.yaml"
    domain_board = kanban / "boards/repo-workspace-hub-ops.yaml"
    repo_data = read_yaml(repo_board)
    repo_data["cards"] = [
        {
            "idempotency_key": key,
            "title": "stale title",
            "source": "github_issue",
            "source_url": "https://github.com/vamseeachanta/workspace-hub/issues/2802",
            "gh_state": "open",
            "gh_labels": [],
            "initial_status": "triage",
            "priority": 0,
        }
    ]
    write_yaml(repo_board, repo_data)

    result = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [
            issue(2802, "Auto-add every GitHub issue", labels=["domain:ops", "priority:high"])
        ],
        dry_run=True,
    )

    assert result.changed is True
    assert "repo-workspace-hub-ops.yaml" in result.diff
    assert key not in [card["idempotency_key"] for card in read_yaml(repo_board)["cards"]]
    domain_cards = read_yaml(domain_board)["cards"]
    assert [card["idempotency_key"] for card in domain_cards] == [key]
    assert domain_cards[0]["title"] == "Auto-add every GitHub issue"
    assert domain_cards[0]["gh_state"] == "open"
    assert domain_cards[0]["priority"] == 1
    assert domain_cards[0]["gh_labels"] == ["domain:ops", "priority:high"]


def test_reconcile_removes_missing_issue_and_updates_closed_state(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    repo_board = kanban / "boards/repo-workspace-hub.yaml"
    repo_data = read_yaml(repo_board)
    repo_data["cards"] = [
        {
            "idempotency_key": "gh:vamseeachanta/workspace-hub#1",
            "title": "deleted or transferred",
            "source": "github_issue",
            "source_url": "https://github.com/vamseeachanta/workspace-hub/issues/1",
            "gh_state": "open",
            "gh_labels": [],
            "initial_status": "triage",
            "priority": 0,
        },
        {
            "idempotency_key": "gh:vamseeachanta/workspace-hub#2",
            "title": "old title",
            "source": "github_issue",
            "source_url": "https://github.com/vamseeachanta/workspace-hub/issues/2",
            "gh_state": "open",
            "gh_labels": [],
            "initial_status": "triage",
            "priority": 0,
        },
    ]
    write_yaml(repo_board, repo_data)

    result = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [issue(2, "closed issue", state="CLOSED")],
        dry_run=True,
    )

    assert result.changed is True
    cards = read_yaml(repo_board)["cards"]
    assert [card["idempotency_key"] for card in cards] == ["gh:vamseeachanta/workspace-hub#2"]
    assert cards[0]["title"] == "closed issue"
    assert cards[0]["gh_state"] == "closed"


def test_fetch_repo_issues_aborts_when_gh_limit_is_reached():
    reconcile = load_reconcile()
    calls = []

    def runner(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=json.dumps([issue(1, "one"), issue(2, "two")]),
            stderr="",
        )

    with pytest.raises(RuntimeError, match="truncated"):
        reconcile.fetch_repo_issues("vamseeachanta/workspace-hub", limit=2, runner=runner)

    assert calls == [
        [
            "gh",
            "issue",
            "list",
            "--repo",
            "vamseeachanta/workspace-hub",
            "--state",
            "all",
            "--limit",
            "2",
            "--json",
            "number,title,state,labels",
        ]
    ]
