from __future__ import annotations

import importlib.util
import json
import re
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


def existing_issue_card(number: int, title: str = "stale title", labels: list[str] | None = None) -> dict:
    repo = "vamseeachanta/workspace-hub"
    return {
        "idempotency_key": f"gh:{repo}#{number}",
        "title": title,
        "source": "github_issue",
        "source_url": f"https://github.com/{repo}/issues/{number}",
        "gh_state": "open",
        "gh_labels": labels or [],
        "initial_status": "triage",
        "priority": 0,
    }


def test_reconcile_moves_domain_labeled_issue_and_keeps_key_unique(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    key = "gh:vamseeachanta/workspace-hub#2802"
    repo_board = kanban / "boards/repo-workspace-hub.yaml"
    domain_board = kanban / "boards/repo-workspace-hub-ops.yaml"
    repo_data = read_yaml(repo_board)
    repo_data["cards"] = [
        {
            "idempotency_key": key,
            **existing_issue_card(2802),
        }
    ]
    write_yaml(repo_board, repo_data)

    result = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [
            issue(2802, "Auto-add every GitHub issue", labels=["domain:ops", "priority:high"])
        ],
        dry_run=False,
    )

    assert result.changed is True
    assert "repo-workspace-hub-ops.yaml" in result.diff
    repo_keys = [card["idempotency_key"] for card in read_yaml(repo_board)["cards"]]
    domain_cards = read_yaml(domain_board)["cards"]
    domain_keys = [card["idempotency_key"] for card in domain_cards]
    assert key not in repo_keys
    assert repo_keys + domain_keys == [key]
    assert [card["idempotency_key"] for card in domain_cards] == [key]
    assert domain_cards[0]["title"] == "Auto-add every GitHub issue"
    assert domain_cards[0]["gh_state"] == "open"
    assert domain_cards[0]["priority"] == 1
    assert domain_cards[0]["gh_labels"] == ["domain:ops", "priority:high"]


def test_reconcile_removes_missing_issue_with_allow_shrink_and_updates_closed_state(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    repo_board = kanban / "boards/repo-workspace-hub.yaml"
    repo_data = read_yaml(repo_board)
    repo_data["cards"] = [
        {
            **existing_issue_card(1, "deleted or transferred"),
        },
        {
            **existing_issue_card(2, "old title"),
        },
    ]
    write_yaml(repo_board, repo_data)

    result = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [issue(2, "closed issue", state="CLOSED")],
        dry_run=False,
        allow_shrink_repos={"vamseeachanta/workspace-hub"},
    )

    assert result.changed is True
    cards = read_yaml(repo_board)["cards"]
    assert [card["idempotency_key"] for card in cards] == ["gh:vamseeachanta/workspace-hub#2"]
    assert cards[0]["title"] == "closed issue"
    assert cards[0]["gh_state"] == "closed"


def test_reconcile_fails_closed_when_active_repo_fetch_returns_empty(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    repo_board = kanban / "boards/repo-workspace-hub.yaml"
    repo_data = read_yaml(repo_board)
    repo_data["cards"] = [
        {
            "idempotency_key": "gh:vamseeachanta/workspace-hub#2802",
            "title": "must not be wiped by empty fetch",
            "source": "github_issue",
            "source_url": "https://github.com/vamseeachanta/workspace-hub/issues/2802",
            "gh_state": "open",
            "gh_labels": [],
            "initial_status": "triage",
            "priority": 0,
        }
    ]
    write_yaml(repo_board, repo_data)

    with pytest.raises(RuntimeError, match="empty issue list"):
        reconcile.reconcile_kanban(
            kanban,
            issue_fetcher=lambda repo: [],
            dry_run=True,
        )

    cards = read_yaml(repo_board)["cards"]
    assert [card["idempotency_key"] for card in cards] == [
        "gh:vamseeachanta/workspace-hub#2802"
    ]


def test_reconcile_fails_closed_when_active_repo_fetch_shrinks_existing_cards(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    repo_board = kanban / "boards/repo-workspace-hub.yaml"
    repo_data = read_yaml(repo_board)
    repo_data["cards"] = [
        existing_issue_card(1, "keep"),
        existing_issue_card(2, "missing from partial fetch"),
    ]
    write_yaml(repo_board, repo_data)

    with pytest.raises(RuntimeError, match="partial issue list"):
        reconcile.reconcile_kanban(
            kanban,
            issue_fetcher=lambda repo: [issue(1, "keep")],
            dry_run=False,
        )

    assert repo_board.read_text(encoding="utf-8") == yaml.safe_dump(repo_data, sort_keys=False)


def test_reconcile_allows_shrink_with_explicit_repo_override(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    repo_board = kanban / "boards/repo-workspace-hub.yaml"
    repo_data = read_yaml(repo_board)
    repo_data["cards"] = [
        existing_issue_card(1, "keep"),
        existing_issue_card(2, "legitimate deletion"),
    ]
    write_yaml(repo_board, repo_data)

    result = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [issue(1, "keep")],
        dry_run=False,
        allow_shrink_repos={"vamseeachanta/workspace-hub"},
    )

    assert result.changed is True
    assert [card["idempotency_key"] for card in read_yaml(repo_board)["cards"]] == [
        "gh:vamseeachanta/workspace-hub#1"
    ]


def test_board_files_returns_manifest_boards_only(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    entries = reconcile.load_manifest_entries(kanban)
    unmanifested = kanban / "boards/unmanifested-empty.yaml"
    write_yaml(unmanifested, {"board": {"slug": "unmanifested-empty"}, "cards": []})

    assert reconcile.board_files(kanban, entries) == [
        kanban / "boards/repo-workspace-hub-ops.yaml",
        kanban / "boards/repo-workspace-hub.yaml",
    ]


def test_unmanifested_board_with_card_aborts(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    write_yaml(
        kanban / "boards/unmanifested.yaml",
        {"board": {"slug": "unmanifested"}, "cards": [{"idempotency_key": "manual:1"}]},
    )

    with pytest.raises(RuntimeError, match="unmanifested board"):
        reconcile.reconcile_kanban(
            kanban,
            issue_fetcher=lambda repo: [],
            dry_run=True,
            allow_empty_repos={"vamseeachanta/workspace-hub"},
        )


def test_unmanifested_empty_board_warns_and_proceeds(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    write_yaml(kanban / "boards/unmanifested-empty.yaml", {"board": {"slug": "empty"}, "cards": []})

    result = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [],
        dry_run=True,
        allow_empty_repos={"vamseeachanta/workspace-hub"},
    )

    assert result.changed is False
    assert "unmanifested empty board" in capsys.readouterr().err


def test_dry_run_never_writes_even_when_write_files_true(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    repo_board = kanban / "boards/repo-workspace-hub.yaml"
    before = repo_board.read_bytes()

    result = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [issue(2802, "new card")],
        dry_run=True,
        write_files=True,
    )

    assert result.changed is True
    assert repo_board.read_bytes() == before


def test_reconcile_is_idempotent_on_second_run(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    repo_board = kanban / "boards/repo-workspace-hub.yaml"

    first = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [issue(2802, "stable title")],
        dry_run=False,
    )
    after_first = repo_board.read_bytes()
    second = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [issue(2802, "stable title")],
        dry_run=False,
    )

    assert first.changed is True
    assert second.changed is False
    assert repo_board.read_bytes() == after_first


def test_reconcile_preserves_board_comments_and_wrapped_scalars(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    repo_board = kanban / "boards/repo-workspace-hub.yaml"
    repo_board.write_text(
        """# board comment survives reconcile
board:
  slug: repo-workspace-hub
  tier: repo
  repo: vamseeachanta/workspace-hub
  workspace_path: /mnt/local-analysis/workspace-hub
  description: |
    Wrapped line one.
    Wrapped line two.
cards:
- idempotency_key: gh:vamseeachanta/workspace-hub#2802
  title: stale title
  source: github_issue
  source_url: https://github.com/vamseeachanta/workspace-hub/issues/2802
  gh_state: open
  gh_labels: []
  initial_status: triage
  priority: 0
""",
        encoding="utf-8",
    )

    reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [issue(2802, "fresh title")],
        dry_run=False,
    )

    text = repo_board.read_text(encoding="utf-8")
    assert "# board comment survives reconcile" in text
    assert "description: |\n    Wrapped line one.\n    Wrapped line two.\n" in text
    assert "title: fresh title" in text


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


def test_workflow_contract_keeps_phase_2_cron_deferred_and_push_retry_bounded():
    text = (ROOT / ".github/workflows/kanban-reconcile.yml").read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)

    assert workflow["concurrency"] == {
        "group": "kanban-reconcile",
        "cancel-in-progress": "false",
    }
    assert workflow["permissions"] == {"contents": "write", "issues": "read"}
    assert "# TODO(#2802 phase 2): re-enable the */20 schedule" in text
    assert '  # schedule:\n  #   - cron: "*/20 * * * *"' in text
    assert re.search(r"(?m)^  workflow_dispatch:", text)

    run = workflow["jobs"]["reconcile"]["steps"][-1]["run"]
    assert run.count('git commit -m "chore: reconcile kanban board"') == 1
    assert "for attempt in 1 2 3; do" in run
    assert "push_stderr=" in run
    assert "non-fast-forward" in run
    assert "fetch first" in run
    assert "git pull --rebase" not in run
