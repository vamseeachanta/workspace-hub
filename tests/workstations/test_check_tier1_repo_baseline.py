from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "workstations" / "check-tier1-repo-baseline.py"
REGISTRY_PATH = ROOT / "config" / "workstations" / "registry.yaml"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_tier1_repo_baseline", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def git_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / ".git").mkdir(exist_ok=True)


def git_link(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / ".git").write_text("gitdir: /tmp/example/.git\n", encoding="utf-8")


REQUIRED = ["workspace-hub", "digitalmodel", "assetutilities", "worldenergydata", "llm-wiki", "assethold"]
OPTIONAL = ["aceengineer-website", "aceengineer-strategy"]
NON_TIER1 = [
    "aceengineer-admin",
    "achantas-data",
    "achantas-media",
    "CAD-DEVELOPMENTS",
    "hobbies",
    "kaggle-rogii-2026",
    "llm-wiki-acma",
    "sabithaandkrishnaestates",
    "teamresumes",
]
HISTORICAL = ["acma-projects", "client_projects", "doris", "frontierdeepwater", "OGManufacturing", "rock-oil-field", "saipem", "sd-work", "seanation"]


def test_dev_primary_tier1_baseline_schema_v1_matches_2770_decision():
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    baseline = data["machines"]["dev-primary"]["tier1_baseline"]
    assert baseline["version"] == 1
    assert baseline["source_issues"] == {"tier1_decision": 2770, "relocation_reconciliation": 2766}
    assert baseline["required"] == REQUIRED
    assert baseline["optional"] == OPTIONAL


def test_all_classification_buckets_are_pairwise_disjoint_including_non_tier1_and_historical():
    checker = load_checker()
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    baseline = data["machines"]["dev-primary"]["tier1_baseline"]
    assert checker.classification_overlaps(baseline) == {}


def test_machine_repos_equals_required_optional_current_non_tier1():
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    machine = data["machines"]["dev-primary"]
    baseline = machine["tier1_baseline"]
    assert machine["repos"] == REQUIRED + OPTIONAL + NON_TIER1
    assert set(machine["repos"]).isdisjoint(baseline["historically_moved_not_currently_present"])


def test_data_access_profile_exact_required_set():
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    machine = data["machines"]["dev-primary"]
    repos = machine["telegram_hermes"]["data_access_profile"]["repos"]
    assert repos == REQUIRED
    assert "OGManufacturing" not in repos
    assert set(repos).isdisjoint(OPTIONAL + NON_TIER1 + HISTORICAL)


def test_historical_entries_have_provenance_schema_and_state_changed_warning(tmp_path: Path):
    checker = load_checker()
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    historical = data["machines"]["dev-primary"]["tier1_baseline"]["historically_moved_not_currently_present"]
    assert list(historical) == HISTORICAL
    for entry in historical.values():
        assert {"source_issue", "source_comment", "prior_claim", "latest_probe", "warning"} <= set(entry)
        assert entry["warning"] == "historical_state_changed_since_prior_comment"
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    messages = [item["message"] for item in report["warnings"]]
    assert any("historical state changed since prior comment" in msg for msg in messages)
    assert not any("missing_current" in msg for msg in messages)


def test_workspace_hub_root_git_is_not_reported_as_nested(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    assert not [b for b in report["blockers"] if "workspace-hub/.git" in b["message"]]


def test_direct_nested_git_directory_under_workspace_hub_is_blocker(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    git_dir(workspace / "nested-repo")
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    assert any("direct nested git repo" in b["message"] and "nested-repo" in b["message"] for b in report["blockers"])


def test_direct_nested_gitlink_under_workspace_hub_is_blocker(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    git_link(workspace / "nested-worktree")
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    assert any("direct nested git repo" in b["message"] and "nested-worktree" in b["message"] for b in report["blockers"])


def test_required_sibling_repos_present(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    assert not [b for b in report["blockers"] if "required repo missing" in b["message"]]


def test_missing_required_repo_blocks_readiness(tmp_path: Path):
    checker = load_checker()
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=tmp_path / "workspace-hub")
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    assert any("required repo missing" in b["message"] for b in report["blockers"])
    assert report["dispatchable"] is False


def test_optional_repo_absence_is_warning_only(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + NON_TIER1:
        git_dir(tmp_path / repo)
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    assert any("optional repo missing" in w["message"] for w in report["warnings"])
    assert not any("optional repo missing" in b["message"] for b in report["blockers"])


def test_current_non_tier1_absence_is_warning_only(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL:
        git_dir(tmp_path / repo)
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    assert any("current non-tier-1 repo missing" in w["message"] for w in report["warnings"])
    assert not any("current non-tier-1 repo missing" in b["message"] for b in report["blockers"])


def test_ogmanufacturing_current_runtime_removal_is_explicit_historical_anomaly():
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    machine = data["machines"]["dev-primary"]
    historical = machine["tier1_baseline"]["historically_moved_not_currently_present"]
    assert "OGManufacturing" in historical
    assert historical["OGManufacturing"]["runtime_access_change"] == "remove_from_data_access_profile"
    assert "OGManufacturing" not in machine["repos"]
    assert "OGManufacturing" not in machine["telegram_hermes"]["data_access_profile"]["repos"]


def test_agent_worktrees_is_allowed_only_as_non_git_infrastructure_dir(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    (tmp_path / "agent-worktrees").mkdir()
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    assert not any("agent-worktrees" in i["message"] for i in report["warnings"] + report["blockers"])
    git_link(tmp_path / "agent-worktrees")
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    assert any("agent-worktrees" in i["message"] for i in report["warnings"] + report["blockers"])


def test_unknown_top_level_sibling_git_repo_warns(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)
    git_dir(tmp_path / "surprise-repo")
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    assert any("unknown sibling git repo" in w["message"] and "surprise-repo" in w["message"] for w in report["warnings"])


def test_historical_repo_reappearing_gets_truthful_present_warning_not_unknown_absent(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)
    git_dir(tmp_path / "OGManufacturing")

    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    warnings = report["warnings"]

    assert any(w["code"] == "historical_repo_present" and w.get("repo") == "OGManufacturing" for w in warnings)
    assert not any(w["code"] == "unknown_sibling_git_repo" and w.get("repo") == "OGManufacturing" for w in warnings)
    assert not any("OGManufacturing" in w["message"] and "latest_probe=absent" in w["message"] for w in warnings)


def test_dirty_and_ahead_states_are_synthetic_warnings_not_blockers(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)
    git_state = {"digitalmodel": {"dirty": True, "ahead": 2, "behind": 0}}
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, git_state=git_state, now="2026-05-21T00:00:00Z")
    assert any("dirty" in w["message"] for w in report["warnings"])
    assert any("ahead" in w["message"] for w in report["warnings"])
    assert not any("digitalmodel" in b["message"] for b in report["blockers"])


def test_git_status_probe_failure_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)

    def fake_run(cmd, *args, **kwargs):
        if "status" in cmd:
            return subprocess.CompletedProcess(cmd, 128, stdout="", stderr="fatal: not a git repository")
        return subprocess.CompletedProcess(cmd, 0, stdout="origin/main\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")

    assert report["dispatchable"] is False
    assert any(b["code"] == "git_probe_failed" and b.get("repo") == "digitalmodel" for b in report["blockers"])


def test_required_repo_missing_upstream_fails_closed_and_non_required_upstream_gaps_warn(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)

    git_state = {
        "digitalmodel": {"dirty": False, "ahead": 0, "behind": 0, "upstream": None},
        "aceengineer-website": {"dirty": False, "ahead": 0, "behind": 0, "upstream": None},
        "aceengineer-admin": {"dirty": False, "ahead": 0, "behind": 0, "upstream": None},
    }
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, git_state=git_state, now="2026-05-21T00:00:00Z")

    assert report["dispatchable"] is False
    assert any(b["code"] == "git_upstream_missing" and b.get("repo") == "digitalmodel" for b in report["blockers"])
    assert any(w["code"] == "git_upstream_missing" and w.get("repo") == "aceengineer-website" for w in report["warnings"])
    assert any(w["code"] == "git_upstream_missing" and w.get("repo") == "aceengineer-admin" for w in report["warnings"])


def test_git_probes_disable_optional_locks(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)

    seen_git_calls = 0

    def fake_run(cmd, *args, **kwargs):
        nonlocal seen_git_calls
        if cmd[0] == "git":
            seen_git_calls += 1
            assert kwargs.get("env", {}).get("GIT_OPTIONAL_LOCKS") == "0"
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    assert seen_git_calls > 0


def test_cli_formats_json_markdown_html_and_exit_status(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    workspace.mkdir(parents=True)
    registry = tmp_path / "registry.yaml"
    registry.write_text(yaml.safe_dump(checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)), encoding="utf-8")

    json_result = subprocess.run(
        ["uv", "run", str(SCRIPT_PATH), "--registry", str(registry), "--machine", "dev-primary", "--repo-root", str(tmp_path), "--now", "2026-05-21T00:00:00Z", "--format", "json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert json_result.returncode == 1
    assert json.loads(json_result.stdout)["dispatchable"] is False

    markdown_result = subprocess.run(
        ["uv", "run", str(SCRIPT_PATH), "--registry", str(registry), "--machine", "dev-primary", "--repo-root", str(tmp_path), "--now", "2026-05-21T00:00:00Z", "--format", "markdown"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert markdown_result.returncode == 1
    assert "# ace-linux-1 tier-1 checkout normalization" in markdown_result.stdout
    assert "## Blockers" in markdown_result.stdout

    html_result = subprocess.run(
        ["uv", "run", str(SCRIPT_PATH), "--registry", str(registry), "--machine", "dev-primary", "--repo-root", str(tmp_path), "--now", "2026-05-21T00:00:00Z", "--format", "html"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert html_result.returncode == 1
    assert '<section id="summary" data-machine="ace-linux-1">' in html_result.stdout


def test_checker_is_readonly(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    checker = load_checker()
    forbidden_calls: list[str] = []

    def forbidden(name):
        def inner(*args, **kwargs):
            forbidden_calls.append(name)
            raise AssertionError(f"forbidden mutation called: {name}")
        return inner

    monkeypatch.setattr(subprocess, "Popen", forbidden("Popen"))
    monkeypatch.setattr(os, "rename", forbidden("os.rename"))
    monkeypatch.setattr(os, "remove", forbidden("os.remove"))
    monkeypatch.setattr(os, "unlink", forbidden("os.unlink"))
    monkeypatch.setattr(shutil, "move", forbidden("shutil.move"))
    monkeypatch.setattr(shutil, "rmtree", forbidden("shutil.rmtree"))
    monkeypatch.setattr(Path, "unlink", forbidden("Path.unlink"))
    monkeypatch.setattr(Path, "rename", forbidden("Path.rename"))
    monkeypatch.setattr(Path, "replace", forbidden("Path.replace"))

    def fake_run(cmd, *args, **kwargs):
        text = " ".join(str(part) for part in cmd)
        assert not any(op in text for op in [" clone", " fetch", " pull", " push", " mv", " rm", "delete", "sync"])
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    before = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*"))
    checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    after = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*"))
    assert before == after
    assert forbidden_calls == []


def test_html_report_sections_and_data_attributes(tmp_path: Path):
    checker = load_checker()
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)
    report = checker.check_machine(data, "dev-primary", repo_root=tmp_path, now="2026-05-21T00:00:00Z")
    html = checker.render_html(report)
    for section_id in [
        "summary",
        "required-tier1",
        "optional-tier1",
        "current-non-tier1-machine-access",
        "historical-reconciliation",
        "nested-git-check",
        "readiness-projection",
        "runbook-rollback-policy",
    ]:
        assert f'id="{section_id}"' in html
    assert 'data-machine="ace-linux-1"' in html
    assert "historical_state_changed_since_prior_comment" in html

    class StrictParser(HTMLParser):
        def error(self, message):  # pragma: no cover - HTMLParser no longer calls this in py3
            raise AssertionError(message)

    StrictParser().feed(html)


def test_committed_html_report_matches_deterministic_synthetic_generator_output(tmp_path: Path):
    checker = load_checker()
    artifact = ROOT / "docs" / "reports" / "ace-linux-1-tier1-checkout-normalization.html"
    html_text = artifact.read_text(encoding="utf-8")
    timestamp = "2026-05-21T09:46:50Z"
    workspace = tmp_path / "workspace-hub"
    git_dir(workspace)
    data = checker.minimal_registry_for_tests(repo_root=tmp_path, workspace_root=workspace)
    for repo in REQUIRED + OPTIONAL + NON_TIER1:
        git_dir(tmp_path / repo)
    report = checker.check_machine(
        data,
        "dev-primary",
        repo_root=tmp_path,
        git_state={repo: {"dirty": False, "ahead": 0, "behind": 0, "upstream": "origin/main"} for repo in REQUIRED + OPTIONAL + NON_TIER1},
        now=timestamp,
    )

    assert checker.render_html(report).strip() == html_text.strip()


def test_plan_index_row_is_upserted_once():
    readme = (ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    assert readme.count("#2766") == 1
    assert "2026-05-20-issue-2766-ace-linux-1-checkout-normalization.md" in readme
    assert "| [#2766](https://github.com/vamseeachanta/workspace-hub/issues/2766) | ace-linux-1-checkout-normalization |" in readme
    assert "| plan-approved | T2 |" in readme
