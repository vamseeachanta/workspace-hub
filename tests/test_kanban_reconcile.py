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


def gql_node(number: int, title: str, state: str = "OPEN", labels: list[str] | None = None,
             labels_has_next: bool = False) -> dict:
    """A single issue node in GraphQL response shape."""
    return {
        "number": number,
        "title": title,
        "state": state,
        "labels": {
            "pageInfo": {"hasNextPage": labels_has_next},
            "nodes": [{"name": name} for name in (labels or [])],
        },
    }


def gql_page(nodes: list[dict], has_next_page: bool, end_cursor: str | None) -> str:
    """A GraphQL response page as the JSON string `gh api graphql` emits on stdout."""
    return json.dumps(
        {
            "data": {
                "repository": {
                    "issues": {
                        "pageInfo": {
                            "hasNextPage": has_next_page,
                            "endCursor": end_cursor,
                        },
                        "nodes": nodes,
                    }
                }
            }
        }
    )


def test_fetch_repo_issues_unions_multiple_graphql_pages():
    reconcile = load_reconcile()
    calls = []

    pages = [
        gql_page([gql_node(1, "one"), gql_node(2, "two")], has_next_page=True, end_cursor="CUR1"),
        gql_page([gql_node(3, "three", state="CLOSED")], has_next_page=False, end_cursor=None),
    ]

    def runner(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout=pages[len(calls) - 1], stderr="")

    result = reconcile.fetch_repo_issues("vamseeachanta/workspace-hub", runner=runner)

    assert len(calls) == 2
    assert [r["number"] for r in result] == [1, 2, 3]
    # mapped to the card shape downstream expects
    assert result == [
        {"number": 1, "title": "one", "state": "OPEN", "labels": []},
        {"number": 2, "title": "two", "state": "OPEN", "labels": []},
        {"number": 3, "title": "three", "state": "CLOSED", "labels": []},
    ]


def test_fetch_repo_issues_raises_on_hasnextpage_without_cursor():
    # Guard against a cron hang: hasNextPage=true with a null endCursor would
    # otherwise re-fetch page 1 forever.
    reconcile = load_reconcile()

    def runner(cmd, **kwargs):
        return subprocess.CompletedProcess(
            cmd, 0,
            stdout=gql_page([gql_node(1, "one")], has_next_page=True, end_cursor=None),
            stderr="",
        )

    with pytest.raises(RuntimeError, match="endCursor"):
        reconcile.fetch_repo_issues("vamseeachanta/workspace-hub", runner=runner)


def test_fetch_repo_issues_raises_on_malformed_issue_pageinfo():
    # A 200 response with nodes but no issues.pageInfo is indistinguishable from
    # "last page" — must raise, not return a partial set.
    reconcile = load_reconcile()

    def runner(cmd, **kwargs):
        payload = {"data": {"repository": {"issues": {"nodes": []}}}}  # pageInfo missing
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")

    with pytest.raises(RuntimeError, match="pageInfo"):
        reconcile.fetch_repo_issues("vamseeachanta/workspace-hub", runner=runner)


def test_fetch_repo_issues_raises_on_non_advancing_cursor():
    # hasNextPage=true with a repeated endCursor would loop forever → must raise.
    reconcile = load_reconcile()

    def runner(cmd, **kwargs):
        payload = {"data": {"repository": {"issues": {
            "nodes": [],
            "pageInfo": {"hasNextPage": True, "endCursor": "SAME"},
        }}}}
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")

    with pytest.raises(RuntimeError, match="did not advance"):
        reconcile.fetch_repo_issues("vamseeachanta/workspace-hub", runner=runner)


def test_fetch_repo_issues_raises_on_malformed_label_pageinfo():
    # A node whose labels has nodes but no pageInfo could silently truncate labels
    # (board routing depends on them) → must raise.
    reconcile = load_reconcile()

    def runner(cmd, **kwargs):
        node = {"number": 1, "title": "x", "state": "OPEN",
                "labels": {"nodes": [{"name": "domain:foo"}]}}  # labels.pageInfo missing
        payload = {"data": {"repository": {"issues": {
            "nodes": [node],
            "pageInfo": {"hasNextPage": False, "endCursor": None},
        }}}}
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")

    with pytest.raises(RuntimeError, match="labels.pageInfo"):
        reconcile.fetch_repo_issues("vamseeachanta/workspace-hub", runner=runner)


def test_fetch_repo_issues_raises_mid_loop_without_partial():
    reconcile = load_reconcile()
    calls = []

    def runner(cmd, **kwargs):
        calls.append(cmd)
        if len(calls) == 1:
            return subprocess.CompletedProcess(
                cmd,
                0,
                stdout=gql_page([gql_node(1, "one")], has_next_page=True, end_cursor="CUR1"),
                stderr="",
            )
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="API rate limited")

    with pytest.raises(RuntimeError) as excinfo:
        reconcile.fetch_repo_issues("vamseeachanta/workspace-hub", runner=runner)

    # raised, not returned: no partial list escapes
    assert "vamseeachanta/workspace-hub" in str(excinfo.value)
    assert len(calls) == 2


def test_fetch_repo_issues_raises_when_labels_truncated():
    reconcile = load_reconcile()

    def runner(cmd, **kwargs):
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=gql_page(
                [gql_node(1, "many labels", labels=["domain:ops"], labels_has_next=True)],
                has_next_page=False,
                end_cursor=None,
            ),
            stderr="",
        )

    with pytest.raises(RuntimeError, match="label"):
        reconcile.fetch_repo_issues("vamseeachanta/workspace-hub", runner=runner)


def test_fetch_repo_issues_maps_node_to_card_shape():
    reconcile = load_reconcile()

    def runner(cmd, **kwargs):
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=gql_page(
                [gql_node(2802, "Auto-add issue", state="OPEN",
                          labels=["domain:ops", "priority:high"])],
                has_next_page=False,
                end_cursor=None,
            ),
            stderr="",
        )

    result = reconcile.fetch_repo_issues("vamseeachanta/workspace-hub", runner=runner)

    assert result == [
        {
            "number": 2802,
            "title": "Auto-add issue",
            "state": "OPEN",
            "labels": [{"name": "domain:ops"}, {"name": "priority:high"}],
        }
    ]


def test_fetch_repo_issues_emits_graphql_command_with_pagination():
    reconcile = load_reconcile()
    calls = []

    pages = [
        gql_page([gql_node(1, "one")], has_next_page=True, end_cursor="CUR1"),
        gql_page([gql_node(2, "two")], has_next_page=False, end_cursor=None),
    ]

    def runner(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout=pages[len(calls) - 1], stderr="")

    reconcile.fetch_repo_issues("vamseeachanta/workspace-hub", runner=runner)

    page1, page2 = calls
    # graphql invocation, not `gh issue list`
    assert page1[:3] == ["gh", "api", "graphql"]
    assert "issue" not in page1
    # query carried via -f query=
    query_arg = next(a for a in page1 if a.startswith("query="))
    assert "pageInfo" in query_arg and "hasNextPage" in query_arg
    assert "first:100" in query_arg
    assert "labels(first:100)" in query_arg
    # owner/name passed as -F
    assert "owner=workspace-hub" not in page1  # owner is the org, not the repo name
    assert "owner=vamseeachanta" in page1
    assert "name=workspace-hub" in page1
    # page 1 carries no cursor; page 2 carries the endCursor from page 1
    assert not any(a.startswith("cursor=") for a in page1)
    assert "cursor=CUR1" in page2


def test_workflow_contract_keeps_phase_2_cron_active_and_push_retry_bounded():
    text = (ROOT / ".github/workflows/kanban-reconcile.yml").read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)

    assert workflow["concurrency"] == {
        "group": "kanban-reconcile",
        "cancel-in-progress": "false",
    }
    assert workflow["permissions"] == {"contents": "write", "issues": "read"}

    # Phase 2 (#2826): the */20 cron is now ACTIVE (uncommented), and the stale
    # "re-enable the */20 schedule" deferral TODO is gone.
    assert "# TODO(#2802 phase 2): re-enable the */20 schedule" not in text
    assert '  # schedule:\n  #   - cron: "*/20 * * * *"' not in text
    # `on:` is a YAML key; BaseLoader yields the literal string "on" unless it
    # parses as a bool, so look it up defensively.
    triggers = workflow.get("on", workflow.get(True))
    assert "schedule" in triggers
    assert {"cron": "*/20 * * * *"} in triggers["schedule"]
    # repository_dispatch lets sibling repos send low-latency nudges.
    assert "repository_dispatch" in triggers
    assert "workflow_dispatch" in triggers
    assert re.search(r"(?m)^  workflow_dispatch:", text)

    steps = workflow["jobs"]["reconcile"]["steps"]

    # The App-token-mint step is present, references the App secrets, and uses
    # actions/create-github-app-token so `gh api graphql` reads sibling repos.
    mint = next(
        s for s in steps if "create-github-app-token" in str(s.get("uses", ""))
    )
    assert "KANBAN_RECONCILE_APP_ID" in mint["with"]["app-id"]
    assert "KANBAN_RECONCILE_APP_KEY" in mint["with"]["private-key"]

    run_step = steps[-1]
    # Anti-loop split: the reconcile invocation gets the App token, but the
    # step-level GH_TOKEN/GITHUB_TOKEN (and therefore the push) stay the default
    # github.token so the board push does NOT carry the App token / retrigger CI.
    assert run_step["env"]["GH_TOKEN"] == "${{ github.token }}"
    assert run_step["env"]["GITHUB_TOKEN"] == "${{ github.token }}"
    assert run_step["env"]["APP_TOKEN"] == "${{ steps.app-token.outputs.token }}"

    run = run_step["run"]
    # Reconcile uses the App token; the push must NOT.
    assert 'GH_TOKEN="$APP_TOKEN"' in run
    assert "uv run python scripts/kanban/reconcile.py" in run
    assert 'APP_TOKEN' not in run.split("git push")[1]
    # Anti-loop hardening (Codex #2826.1): the App token must reach ONLY the reconcile
    # call, never git credentials. Assert no credential-injection sink exists that a
    # regression could use to wire the App token into the push (which would retrigger CI).
    for sink in ("git remote set-url", "http.extraheader", "gh auth setup-git", "git config credential"):
        assert sink not in run, f"anti-loop: unexpected git-credential mechanism '{sink}' in the run step"

    assert run.count('git commit -m "chore: reconcile kanban board"') == 1
    assert "for attempt in 1 2 3; do" in run
    assert "push_stderr=" in run
    assert "non-fast-forward" in run
    assert "fetch first" in run
    assert "git pull --rebase" not in run
