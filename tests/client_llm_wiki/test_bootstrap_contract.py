"""CLI, Git-layout, and live-private contract tests for issue #3449."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest
import yaml

from client_llm_wiki import bootstrap_contract
from client_llm_wiki.bootstrap_contract import (
    BootstrapContractError,
    derive_workspace_layout,
    execute_render,
    verify_private_repo,
    verify_unborn_clone,
)


REPO_SLUG = "example-org/llm-wiki-example-co"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _workspace(tmp_path: Path) -> Path:
    repo = tmp_path / "ecosystem" / "workspace-hub"
    template = repo / "templates" / "client-llm-wiki"
    (template / ".claude").mkdir(parents=True)
    (template / ".gitignore").write_text("private-output/\n", encoding="utf-8")
    (template / ".claude" / "CLAUDE.md").write_text("private\n", encoding="utf-8")
    (template / "README.md").write_text("# <CLIENT_SHORT_NAME>\n", encoding="utf-8")
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test Operator")
    _git(repo, "add", "templates/client-llm-wiki")
    _git(repo, "commit", "-m", "test: add template")
    return repo


def _entry(**overrides: object) -> dict[str, object]:
    entry: dict[str, object] = {
        "short_name": "example-co",
        "repo": REPO_SLUG,
        "visibility": "PRIVATE",
        "posture": "client-private",
        "status": "planned",
        "raw_roots": [],
        "raw_source_status": "not-mounted",
        "ingestion_enabled": False,
    }
    entry.update(overrides)
    return entry


def _registry_file(tmp_path: Path, entry: dict[str, object] | None = None) -> Path:
    path = tmp_path / "registry.yml"
    path.write_text(
        yaml.safe_dump(
            {"registry_version": "0.2", "wikis": [entry or _entry()]},
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def _legacy_registry(tmp_path: Path) -> Path:
    path = tmp_path / "legacy.yml"
    path.write_text(
        yaml.safe_dump(
            {
                "registry_version": 0.1,
                "wikis": [
                    {
                        "short_name": "example-co",
                        "repo": REPO_SLUG,
                        "visibility": "PRIVATE",
                        "posture": "client-private",
                        "status": "planned",
                        "raw_roots": ["/authorized/source/"],
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def _init_target(path: Path, origin: str | None = None) -> Path:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    if origin is not None:
        _git(path, "remote", "add", "origin", origin)
    return path


class RecordingRunner:
    def __init__(self, payload: object, returncode: int = 0):
        self.payload = payload
        self.returncode = returncode
        self.calls: list[list[str]] = []

    def __call__(self, args, **_kwargs):
        self.calls.append(list(args))
        stdout = self.payload if isinstance(self.payload, str) else json.dumps(self.payload)
        return subprocess.CompletedProcess(args, self.returncode, stdout, "lookup failed")


def _private_runner() -> RecordingRunner:
    return RecordingRunner({"visibility": "PRIVATE", "isArchived": False})


def test_main_and_linked_worktree_derive_same_sibling_target(tmp_path, monkeypatch):
    canonical = _workspace(tmp_path)
    linked = tmp_path / "linked-worktree"
    _git(canonical, "worktree", "add", "-b", "test-linked", str(linked), "HEAD")
    expected = canonical.parent / "llm-wiki-example-co"

    monkeypatch.chdir(tmp_path)
    main_layout = derive_workspace_layout(canonical, REPO_SLUG)
    monkeypatch.chdir(linked / "templates")
    linked_layout = derive_workspace_layout(linked, REPO_SLUG)

    assert main_layout.target == expected
    assert linked_layout.target == expected
    assert main_layout.canonical_checkout == canonical
    assert linked_layout.canonical_checkout == canonical


def test_layout_ignores_cwd_and_destination_environment(tmp_path, monkeypatch):
    workspace = _workspace(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLIENT_WIKI_DESTINATION", str(tmp_path / "attacker"))

    layout = derive_workspace_layout(workspace, REPO_SLUG)

    assert layout.target == workspace.parent / "llm-wiki-example-co"
    with pytest.raises(SystemExit):
        bootstrap_contract.main(
            ["classify", "--registry", "unused", "--destination", "/tmp/elsewhere"]
        )


@pytest.mark.parametrize(
    ("payload", "returncode"),
    [
        ({"visibility": "PUBLIC", "isArchived": False}, 0),
        ({"visibility": "PRIVATE", "isArchived": True}, 0),
        ({"visibility": "PRIVATE"}, 0),
        ("not-json", 0),
        ({"visibility": "PRIVATE", "isArchived": False}, 1),
    ],
)
def test_private_verification_fails_closed(payload, returncode):
    runner = RecordingRunner(payload, returncode)

    with pytest.raises(BootstrapContractError):
        verify_private_repo(REPO_SLUG, runner=runner)

    assert runner.calls == [
        ["gh", "repo", "view", REPO_SLUG, "--json", "visibility,isArchived"]
    ]


def test_private_verification_accepts_only_private_unarchived():
    runner = _private_runner()

    verify_private_repo(REPO_SLUG, runner=runner)

    assert len(runner.calls) == 1


@pytest.mark.parametrize(
    "origin",
    [
        "https://github.com/example-org/llm-wiki-example-co",
        "https://github.com/example-org/llm-wiki-example-co.git",
        "git@github.com:example-org/llm-wiki-example-co.git",
    ],
)
def test_matching_clean_unborn_clone_is_authorized(tmp_path, origin):
    clone = _init_target(tmp_path / "clone", origin)

    verify_unborn_clone(clone, REPO_SLUG)


@pytest.mark.parametrize("failure", ["missing-origin", "wrong-origin", "head", "dirty"])
def test_clone_git_preconditions_fail_closed(tmp_path, failure):
    origin = None if failure == "missing-origin" else f"https://github.com/{REPO_SLUG}.git"
    clone = _init_target(tmp_path / "clone", origin)
    if failure == "wrong-origin":
        _git(clone, "remote", "set-url", "origin", "https://example.invalid/lookalike")
    if failure in {"head", "dirty"}:
        (clone / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
    if failure == "head":
        _git(clone, "config", "user.email", "test@example.invalid")
        _git(clone, "config", "user.name", "Test Operator")
        _git(clone, "add", "unexpected.txt")
        _git(clone, "commit", "-m", "unexpected commit")

    with pytest.raises(BootstrapContractError):
        verify_unborn_clone(clone, REPO_SLUG)


def test_metadata_only_render_end_to_end(tmp_path):
    workspace = _workspace(tmp_path)
    registry = _registry_file(tmp_path)
    target = workspace.parent / "llm-wiki-example-co"
    _init_target(target, f"https://github.com/{REPO_SLUG}.git")
    git_identity = (target / ".git").stat().st_ino

    manifest = execute_render(
        registry,
        "example-co",
        template_worktree=workspace,
        runner=_private_runner(),
    )

    assert manifest.template_commit == _git(workspace, "rev-parse", "HEAD")
    assert (target / "README.md").read_text() == "# example-co\n"
    assert (target / ".git").stat().st_ino == git_identity
    unborn = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        text=True,
    )
    assert unborn.returncode != 0


@pytest.mark.parametrize("status", ["bootstrapped", "live", "retired"])
def test_nonplanned_entries_cannot_render_before_live_lookup(tmp_path, status):
    workspace = _workspace(tmp_path)
    registry = _registry_file(tmp_path, _entry(status=status))
    runner = _private_runner()

    with pytest.raises(BootstrapContractError, match="planned"):
        execute_render(
            registry,
            "example-co",
            template_worktree=workspace,
            runner=runner,
        )

    assert runner.calls == []


def test_legacy_registry_cannot_render_before_live_lookup(tmp_path):
    workspace = _workspace(tmp_path)
    runner = _private_runner()

    with pytest.raises(BootstrapContractError):
        execute_render(
            _legacy_registry(tmp_path),
            "example-co",
            template_worktree=workspace,
            runner=runner,
        )

    assert runner.calls == []


def test_source_registered_disabled_render_never_requires_raw_root(tmp_path):
    workspace = _workspace(tmp_path)
    missing_raw = tmp_path / "never-mounted" / "raw-source"
    registry = _registry_file(
        tmp_path,
        _entry(raw_roots=[str(missing_raw)], raw_source_status="mounted"),
    )
    target = workspace.parent / "llm-wiki-example-co"
    _init_target(target, f"git@github.com:{REPO_SLUG}.git")

    execute_render(
        registry,
        "example-co",
        template_worktree=workspace,
        runner=_private_runner(),
    )

    output = "\n".join(
        path.read_text(encoding="utf-8")
        for path in target.rglob("*")
        if path.is_file() and ".git" not in path.parts
    )
    assert str(missing_raw) not in output
    assert not missing_raw.exists()


def test_cli_validate_and_classify_emit_machine_readable_state(
    tmp_path, monkeypatch, capsys
):
    workspace = _workspace(tmp_path)
    registry = _registry_file(tmp_path)
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)

    assert bootstrap_contract.main(
        ["validate-registry", "--registry", str(registry)]
    ) == 0
    assert bootstrap_contract.main(
        ["classify", "--registry", str(registry), "--short-name", "example-co"]
    ) == 0

    payload = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert payload == {
        "mode": "metadata-only",
        "repo": REPO_SLUG,
        "short_name": "example-co",
        "target": str(workspace.parent / "llm-wiki-example-co"),
    }
