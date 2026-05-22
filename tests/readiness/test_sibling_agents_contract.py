from __future__ import annotations

import importlib.util
import socket
from pathlib import Path


def load_checker():
    path = Path(__file__).resolve().parents[2] / "scripts" / "readiness" / "check-sibling-sso-flow.py"
    spec = importlib.util.spec_from_file_location("sibling_sso_checker", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_agents_pointer_to_missing_parent_fails(tmp_path):
    checker = load_checker()
    repo = tmp_path / "digitalmodel"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Digitalmodel\nContract: ../AGENTS.md | Source: src/digitalmodel/\n")

    result = checker.check_agents_contract(repo, tmp_path / "workspace-hub", tmp_path)

    assert result["status"] == "fail"
    assert result["kind"] == "stale_parent_contract"


def test_agents_pointer_to_existing_parent_contract_still_fails(tmp_path):
    checker = load_checker()
    (tmp_path / "AGENTS.md").write_text("# stale parent contract\n")
    repo = tmp_path / "digitalmodel"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Digitalmodel\nContract: ../AGENTS.md | Source: src/digitalmodel/\n")

    result = checker.check_agents_contract(repo, tmp_path / "workspace-hub", tmp_path)

    assert result["status"] == "fail"
    assert result["kind"] == "stale_parent_contract"


def test_present_repo_missing_agents_contract_fails(tmp_path):
    checker = load_checker()
    ws = tmp_path / "workspace-hub"
    ws.mkdir()
    (ws / "AGENTS.md").write_text("# Workspace Hub\n")
    repo = tmp_path / "digitalmodel"
    repo.mkdir()

    result = checker.check_harness_contracts(ws, tmp_path, ["digitalmodel"])

    assert result["status"] == "fail"
    assert result["repos"]["digitalmodel"]["kind"] == "missing_agents"


def test_non_hub_repo_with_arbitrary_local_agents_contract_fails(tmp_path):
    checker = load_checker()
    ws = tmp_path / "workspace-hub"
    ws.mkdir()
    (ws / "AGENTS.md").write_text("# Workspace Hub\n")
    repo = tmp_path / "digitalmodel"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Digitalmodel\nLocal-only divergent contract\n")

    result = checker.check_agents_contract(repo, ws, tmp_path)

    assert result["status"] == "fail"
    assert result["kind"] == "missing_workspace_hub_contract"


def test_agents_pointer_to_workspace_hub_passes(tmp_path):
    checker = load_checker()
    ws = tmp_path / "workspace-hub"
    ws.mkdir()
    (ws / "AGENTS.md").write_text("# Workspace Hub\n")
    repo = tmp_path / "digitalmodel"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Digitalmodel\nContract: ../workspace-hub/AGENTS.md | Source: src/digitalmodel/\n")

    result = checker.check_agents_contract(repo, ws, tmp_path)

    assert result["status"] == "pass"


def test_agents_contract_with_workspace_hub_and_stale_parent_pointer_fails(tmp_path):
    checker = load_checker()
    ws = tmp_path / "workspace-hub"
    ws.mkdir()
    (ws / "AGENTS.md").write_text("# Workspace Hub\n")
    repo = tmp_path / "digitalmodel"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "# Digitalmodel\n"
        "Contract: ../workspace-hub/AGENTS.md | Source: src/digitalmodel/\n"
        "Legacy contract: ../AGENTS.md\n"
    )

    result = checker.check_agents_contract(repo, ws, tmp_path)

    assert result["status"] == "fail"
    assert result["kind"] == "stale_parent_contract"


def test_arbitrary_workspace_hub_agents_mention_without_contract_fails(tmp_path):
    checker = load_checker()
    ws = tmp_path / "workspace-hub"
    ws.mkdir()
    (ws / "AGENTS.md").write_text("# Workspace Hub\n")
    repo = tmp_path / "digitalmodel"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "# Digitalmodel\n"
        "Notes: a useful file exists at /mnt/local-analysis/workspace-hub/AGENTS.md.\n"
    )

    result = checker.check_agents_contract(repo, ws, tmp_path)

    assert result["status"] == "fail"
    assert result["kind"] == "missing_workspace_hub_contract"


def test_build_report_checks_memory_from_registry_workspace_root(tmp_path, monkeypatch):
    checker = load_checker()
    canonical = tmp_path / "workspace-hub"
    worktree = tmp_path / "agent-worktree"
    canonical.mkdir()
    worktree.mkdir()

    calls = []

    monkeypatch.setattr(checker, "repo_root", lambda: worktree)
    monkeypatch.setattr(
        checker,
        "resolve_machine",
        lambda _registry_path, _machine_name=None: (
            "local-test",
            {
                "hostname": socket.gethostname().split(".")[0],
                "workspace_root": str(canonical),
                "tier1_repo_root": str(tmp_path),
                "repos": [],
            },
        ),
    )

    def fake_run_memory_check(root, machine=None, local_root=None):
        calls.append((root, local_root))
        return checker._section("pass", evidence_paths=[str(local_root)])

    monkeypatch.setattr(checker, "run_memory_check", fake_run_memory_check)
    monkeypatch.setattr(checker, "registry_status", lambda _registry_path, _harness_path: checker._section("pass"))

    report = checker.build_report("local-test")

    assert report["memory"]["status"] == "pass"
    assert calls == [(canonical, canonical)]


def test_remote_memory_check_unreachable_linux_host_fails_closed(monkeypatch, tmp_path):
    checker = load_checker()

    class Result:
        returncode = 255
        stdout = ""
        stderr = "ssh: connect to host ace-linux-2 port 22: Network is unreachable"

    monkeypatch.setattr(checker.socket, "gethostname", lambda: "ace-linux-1")
    monkeypatch.setattr(checker.subprocess, "run", lambda *args, **kwargs: Result())

    result = checker.run_memory_check(
        tmp_path / "workspace-hub",
        {"hostname": "ace-linux-2", "workspace_root": str(tmp_path / "workspace-hub")},
        tmp_path / "workspace-hub",
    )

    assert result["status"] == "fail"
    assert result["reason"] == "ssh_unreachable"
