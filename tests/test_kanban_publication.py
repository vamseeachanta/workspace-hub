"""Publication-boundary tests using synthetic issue data only.

Expected results follow the data handling contract's publication boundary:
ignored and untracked local outputs are allowed; tracked, trackable or redirected
outputs are refused before fetching. No numerical calibration is involved.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def rc():
    spec = importlib.util.spec_from_file_location(
        "kanban_publication_reconcile", ROOT / "scripts/kanban/reconcile.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mirror(tmp_path, rc):
    root = tmp_path / "mirror"
    root.mkdir()
    rc.write_yaml(root / "manifest.yaml", {"manifest": {"boards": [{
        "slug": "repo-sample", "tier": "repo", "repo": "sample/repo",
        "file": "boards/repo-sample.yaml",
    }]}})
    return root


def live_issue(_repo, **_kwargs):
    # Hand calculation: one input issue produces one repository-board card.
    return [{"number": 1, "title": "Synthetic task", "state": "OPEN", "labels": []}]


def mock_checkout(mirror, monkeypatch, *, tracked=False, ignored=True, failure=None):
    """Emulate read-only Git answers; never create or change an index."""
    (mirror / ".git").mkdir()
    (mirror / ".git/HEAD").write_text("ref: refs/heads/test\n", encoding="utf-8")
    calls = []

    def run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        assert cmd[0] == "git"
        assert kwargs["cwd"] == mirror
        if failure:
            return subprocess.CompletedProcess(cmd, 128, "", failure)
        if "ls-files" in cmd:
            return subprocess.CompletedProcess(
                cmd, 0, "boards/repo-sample.yaml\0" if tracked else "", ""
            )
        assert "check-ignore" in cmd
        return subprocess.CompletedProcess(cmd, 0 if ignored else 1, "", "")

    monkeypatch.setattr(subprocess, "run", run)
    return calls


@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize("tracked,ignored", [(True, True), (False, False)])
def test_unsafe_git_destination_refused_before_fetch(
    rc, mirror, monkeypatch, dry_run, tracked, ignored
):
    calls = mock_checkout(mirror, monkeypatch, tracked=tracked, ignored=ignored)
    board = mirror / "boards/repo-sample.yaml"
    board.parent.mkdir()
    board.write_text("cards: []\n", encoding="utf-8")
    before = board.read_bytes()

    def forbidden_fetch(_repo):
        pytest.fail("issue content fetched before destination validation")

    with pytest.raises(RuntimeError, match="local-only"):
        rc.reconcile_kanban(mirror, issue_fetcher=forbidden_fetch, dry_run=dry_run)
    assert calls
    assert board.read_bytes() == before


def test_ignored_untracked_destination_can_be_rebuilt(rc, mirror, monkeypatch):
    calls = mock_checkout(mirror, monkeypatch)
    result = rc.reconcile_kanban(mirror, issue_fetcher=live_issue, dry_run=False)
    assert len(result.changed_files) == 1
    assert rc.load_yaml(result.changed_files[0])["cards"][0]["title"] == "Synthetic task"
    assert any("check-ignore" in cmd for cmd, _ in calls)


def test_git_inspection_failure_is_closed_without_echoing_stderr(rc, mirror, monkeypatch):
    mock_checkout(mirror, monkeypatch, failure="synthetic restricted diagnostic")
    with pytest.raises(RuntimeError, match="local-only") as exc:
        rc.reconcile_kanban(mirror, issue_fetcher=live_issue, dry_run=True)
    assert "synthetic restricted diagnostic" not in str(exc.value)


@pytest.mark.parametrize("binding", ["GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"])
def test_git_bindings_do_not_select_another_checkout(rc, mirror, monkeypatch, binding):
    monkeypatch.setenv(binding, str(mirror / "unrelated"))
    calls = mock_checkout(mirror, monkeypatch)
    rc.reconcile_kanban(mirror, issue_fetcher=live_issue, dry_run=True)
    assert calls
    assert all(binding not in kwargs["env"] for _, kwargs in calls)
    assert os.environ[binding] == str(mirror / "unrelated")


@pytest.mark.parametrize("destination", ["../outside.yaml", "manifest.yaml", "boards/../../outside.yaml"])
def test_manifest_cannot_redirect_generated_cards_outside_boards(rc, mirror, destination):
    doc = rc.load_yaml(mirror / "manifest.yaml")
    doc["manifest"]["boards"][0]["file"] = destination
    rc.write_yaml(mirror / "manifest.yaml", doc)

    def forbidden_fetch(_repo):
        pytest.fail("redirected destination reached issue fetch")

    with pytest.raises(RuntimeError, match="local-only"):
        rc.reconcile_kanban(mirror, issue_fetcher=forbidden_fetch, dry_run=False)
    assert not (mirror.parent / "outside.yaml").exists()


@pytest.mark.parametrize("symlink_kind", ["directory", "file", "internal"])
def test_symlink_destinations_are_refused(rc, mirror, tmp_path, symlink_kind):
    outside = tmp_path / "outside"
    outside.mkdir()
    boards = mirror / "boards"
    if symlink_kind == "directory":
        boards.symlink_to(outside, target_is_directory=True)
    else:
        boards.mkdir()
        target = boards / "other.yaml" if symlink_kind == "internal" else outside / "other.yaml"
        target.write_text("cards: []\n", encoding="utf-8")
        (boards / "repo-sample.yaml").symlink_to(target)

    def forbidden_fetch(_repo):
        pytest.fail("symlink destination reached issue fetch")

    with pytest.raises(RuntimeError, match="local-only"):
        rc.reconcile_kanban(mirror, issue_fetcher=forbidden_fetch, dry_run=False)


@pytest.mark.parametrize("dry_run", [False, True])
def test_cli_reports_count_without_card_content(rc, mirror, monkeypatch, capsys, dry_run):
    monkeypatch.setattr(rc, "fetch_repo_issues", live_issue)
    args = ["--kanban-root", str(mirror)] + (["--dry-run"] if dry_run else [])
    assert rc.main(args) == 0
    output = capsys.readouterr()
    assert "kanban reconcile: 1 board file(s) changed" in output.out
    assert "Synthetic task" not in output.out + output.err
    assert (mirror / "boards/repo-sample.yaml").exists() is not dry_run


def test_cli_content_diff_requires_explicit_request(rc, mirror, monkeypatch, capsys):
    monkeypatch.setattr(rc, "fetch_repo_issues", live_issue)
    assert rc.main(["--kanban-root", str(mirror), "--dry-run", "--show-diff"]) == 0
    assert "+    title: Synthetic task" in capsys.readouterr().out
    assert not (mirror / "boards/repo-sample.yaml").exists()


def test_all_generated_manifest_destinations_in_this_checkout_are_local(rc):
    """Enumerate all current entries, rather than a sample of historical paths."""
    root = ROOT / ".claude/memory/kanban"
    rc.validate_local_destinations(root, rc.load_manifest_entries(root))


def test_real_index_rejects_tracked_destination(rc):
    """Use a current authored file, without staging or changing any Git metadata."""
    root = ROOT / ".claude/memory/kanban"
    entry = rc.BoardEntry(
        "synthetic", "repo", "sample/repo", None, root / "boards/ecosystem.yaml"
    )
    with pytest.raises(RuntimeError, match="is tracked"):
        rc.validate_local_destinations(root, [entry])


def test_real_ignore_rules_reject_trackable_destination(rc):
    root = ROOT / "scripts/kanban"
    entry = rc.BoardEntry(
        "synthetic", "repo", "sample/repo", None, root / "boards/repo-sample.yaml"
    )
    with pytest.raises(RuntimeError, match="must be ignored"):
        rc.validate_local_destinations(root, [entry])


def test_domain_only_manifest_is_also_checked(rc, mirror, monkeypatch):
    doc = rc.load_yaml(mirror / "manifest.yaml")
    doc["manifest"]["boards"][0]["tier"] = "domain"
    rc.write_yaml(mirror / "manifest.yaml", doc)
    mock_checkout(mirror, monkeypatch, ignored=False)
    with pytest.raises(RuntimeError, match="must be ignored"):
        rc.reconcile_kanban(mirror, issue_fetcher=live_issue, repo_filter="sample/other")


def test_authored_board_without_repository_is_preserved(rc, mirror):
    doc = rc.load_yaml(mirror / "manifest.yaml")
    doc["manifest"]["boards"].append({
        "slug": "authored", "tier": "ecosystem", "file": "boards/authored.yaml",
    })
    rc.write_yaml(mirror / "manifest.yaml", doc)
    authored = mirror / "boards/authored.yaml"
    authored.parent.mkdir()
    authored.write_text("cards:\n  - title: Synthetic authored theme\n", encoding="utf-8")
    before = authored.read_bytes()
    rc.reconcile_kanban(mirror, issue_fetcher=live_issue, dry_run=False)
    assert authored.read_bytes() == before


def test_missing_git_executable_refuses_fetch(rc, mirror, monkeypatch):
    mock_checkout(mirror, monkeypatch)

    def unavailable(*_args, **_kwargs):
        raise FileNotFoundError("synthetic restricted diagnostic")

    monkeypatch.setattr(subprocess, "run", unavailable)
    with pytest.raises(RuntimeError, match="Git inspection unavailable"):
        rc.reconcile_kanban(mirror, issue_fetcher=live_issue, dry_run=False)


def test_symlinked_kanban_root_is_refused(rc, mirror, tmp_path):
    alias = tmp_path / "alias"
    alias.symlink_to(mirror, target_is_directory=True)

    def forbidden_fetch(_repo):
        pytest.fail("symlinked root reached issue fetch")

    with pytest.raises(RuntimeError, match="symlink destination"):
        rc.reconcile_kanban(alias, issue_fetcher=forbidden_fetch, dry_run=False)


def test_default_root_is_anchored_to_script_checkout(rc, monkeypatch):
    """Neither caller cwd nor inherited Git bindings select a different tree."""
    monkeypatch.setenv("GIT_WORK_TREE", "synthetic-other-checkout")

    def run(cmd, **kwargs):
        assert kwargs["cwd"] == ROOT
        assert "GIT_WORK_TREE" not in kwargs["env"]
        return subprocess.CompletedProcess(cmd, 0, str(ROOT) + "\n", "")

    monkeypatch.setattr(subprocess, "run", run)
    assert rc.repo_root() == ROOT
