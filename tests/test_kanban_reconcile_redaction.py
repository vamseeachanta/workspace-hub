"""C20: the kanban reconciler redacts client identifiers before writing a board.

The boards are committed to this PUBLIC repository by CI every 20 minutes from
GitHub issue text. The reconciler applies the identifier gate's Redactor to
every board it writes and to the diff it prints, and fails closed when the
redactor cannot load. Names are synthetic.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("_tkr", HERE / "test_kanban_reconcile.py")
_tkr = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_tkr)

load_reconcile = _tkr.load_reconcile
seed_kanban = _tkr.seed_kanban
issue = _tkr.issue
existing_issue_card = _tkr.existing_issue_card
read_yaml = _tkr.read_yaml
write_yaml = _tkr.write_yaml

SYNTH = "zorblaxcorp"


@pytest.fixture(autouse=True)
def deny_list(tmp_path_factory, monkeypatch):
    p = tmp_path_factory.mktemp("deny") / "deny.txt"
    p.write_text(f"{SYNTH}\nre:(?i)quux\\s+marine\n", encoding="utf-8")
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(p))
    monkeypatch.delenv("LEGAL_CLIENT_MAP", raising=False)
    return p


def _all_text(kanban: Path) -> str:
    return "".join(p.read_text(encoding="utf-8") for p in (kanban / "boards").glob("*.yaml"))


def test_new_issue_title_is_redacted_on_the_board_and_in_the_diff(tmp_path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    result = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [issue(7, f"Riser study for {SYNTH.title()} on Quux Marine hull")],
        dry_run=False,
    )
    assert result.changed
    text = _all_text(kanban)
    assert SYNTH not in text.lower() and "quux" not in text.lower()
    assert "[redacted]" in text
    assert SYNTH not in result.diff.lower() and "quux" not in result.diff.lower()
    cards = read_yaml(kanban / "boards/repo-workspace-hub.yaml")["cards"]
    assert cards[0]["idempotency_key"] == "gh:vamseeachanta/workspace-hub#7"
    assert "hull" in cards[0]["title"]


def test_a_dirty_board_is_cleaned_even_when_the_issue_is_unchanged(tmp_path):
    """A name already on disk (an older run, or another field such as a body
    excerpt) is removed, and the removed text never reaches the printed diff."""
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    board = kanban / "boards/repo-workspace-hub.yaml"
    data = read_yaml(board)
    card = existing_issue_card(8, "clean title")
    card["body_excerpt"] = f"legacy excerpt naming {SYNTH}"
    data["cards"] = [card]
    write_yaml(board, data)

    result = reconcile.reconcile_kanban(
        kanban, issue_fetcher=lambda repo: [issue(8, "clean title")], dry_run=False
    )
    assert result.changed
    assert SYNTH not in board.read_text(encoding="utf-8").lower()
    assert SYNTH not in result.diff.lower()


def test_a_non_issue_card_is_redacted_too(tmp_path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    board = kanban / "boards/repo-workspace-hub.yaml"
    data = read_yaml(board)
    data["cards"] = [{"idempotency_key": "manual:1", "title": f"manual card {SYNTH}", "source": "manual"}]
    write_yaml(board, data)
    reconcile.reconcile_kanban(kanban, issue_fetcher=lambda repo: [], dry_run=False,
                               allow_empty_repos={"vamseeachanta/workspace-hub"})
    assert SYNTH not in board.read_text(encoding="utf-8").lower()


def test_second_run_is_a_no_op(tmp_path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    fetch = lambda repo: [issue(9, f"{SYNTH} mooring")]  # noqa: E731
    reconcile.reconcile_kanban(kanban, issue_fetcher=fetch, dry_run=False)
    first = _all_text(kanban)
    again = reconcile.reconcile_kanban(kanban, issue_fetcher=fetch, dry_run=False)
    assert again.changed is False
    assert _all_text(kanban) == first


def test_fails_closed_and_writes_nothing_when_the_redactor_cannot_load(tmp_path, monkeypatch):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    before = _all_text(kanban)
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(tmp_path / "missing.txt"))
    with pytest.raises(Exception) as exc:
        reconcile.reconcile_kanban(
            kanban, issue_fetcher=lambda repo: [issue(10, f"{SYNTH} title")], dry_run=False
        )
    assert "redact" in str(exc.value).lower()
    assert _all_text(kanban) == before


def test_main_exits_non_zero_when_the_redactor_cannot_load(tmp_path, monkeypatch, capsys):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(tmp_path / "missing.txt"))
    monkeypatch.setattr(reconcile, "fetch_repo_issues", lambda repo, page_size=100: [issue(11, SYNTH)])
    rc = reconcile.main(["--kanban-root", str(kanban)])
    assert rc != 0
    out = capsys.readouterr()
    assert SYNTH not in (out.out + out.err).lower()


def test_workflow_provides_the_private_lists_and_fails_closed_without_them():
    """CI has no private list unless the workflow materializes it. Without the
    deny list the redactor refuses to load; the workflow must say why and stop
    before reconciling rather than publish names the public hashes miss."""
    import yaml

    root = Path(__file__).resolve().parents[1]
    text = (root / ".github/workflows/kanban-reconcile.yml").read_text(encoding="utf-8")
    wf = yaml.load(text, Loader=yaml.BaseLoader)
    steps = wf["jobs"]["reconcile"]["steps"]
    names = [s.get("name", "") for s in steps]
    idx = next(i for i, n in enumerate(names) if "private" in n.lower() and "list" in n.lower())
    run_idx = len(steps) - 1
    assert idx < run_idx
    step = steps[idx]
    assert step["env"]["IDENTIFIER_DENY_LIST_SECRET"] == "${{ secrets.IDENTIFIER_DENY_LIST }}"
    assert step["env"]["LEGAL_CLIENT_MAP_SECRET"] == "${{ secrets.LEGAL_CLIENT_MAP }}"
    body = step["run"]
    assert "WORKSPACE_HUB_DENY_LIST=" in body and "GITHUB_ENV" in body
    assert "LEGAL_CLIENT_MAP=" in body
    assert "exit 1" in body
    # the secret values are written to files, never echoed
    assert "echo \"$IDENTIFIER_DENY_LIST_SECRET" not in body
