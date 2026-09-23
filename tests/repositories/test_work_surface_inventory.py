from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts" / "repositories" / "work_surface_inventory.py"
FIXTURES = Path(__file__).parent / "fixtures" / "work_surface_inventory"


def _load_module():
    spec = importlib.util.spec_from_file_location("work_surface_inventory", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _surface(tmp_path: Path) -> Path:
    alpha = tmp_path / "alpha"
    for path in (alpha / ".git", alpha / ".claude", alpha / ".codex", alpha / ".gemini"):
        path.mkdir(parents=True)
    for path in (alpha / "AGENTS.md", alpha / ".claude" / "CLAUDE.md", alpha / ".mcp.json"):
        path.write_text("ok", encoding="utf-8")
    (tmp_path / "private-client-name" / ".git").mkdir(parents=True)
    return tmp_path


def test_fixture_golden_summary(tmp_path):
    inventory = _load_module().build_inventory(
        FIXTURES / "mission-map.yaml", FIXTURES / "workstations.yaml",
        _surface(tmp_path), "macbook-portable")
    expected = json.loads((FIXTURES / "expected.json").read_text())
    assert inventory == expected


def test_rejects_duplicate_names_and_bad_enums(tmp_path):
    module = _load_module()
    bad = tmp_path / "bad.yaml"
    bad.write_text("repos:\n- {repo: a, profile: code, sensitivity: public, mcp_required: false}\n- {repo: a, profile: other, sensitivity: secret, mcp_required: false}\n")
    with pytest.raises(ValueError):
        module.load_declared_repositories(bad)


def test_unclassified_is_incomplete(tmp_path):
    module = _load_module()
    declared = {"a": {"repo": "a", "profile": "code", "sensitivity": "unclassified", "mcp_required": False}}
    result = module.join_inventory(declared, set(), {}, 0)
    assert result["repositories"][0]["contract"]["complete"] is False


def test_unknown_repositories_are_aggregate_only(tmp_path):
    inventory = _load_module().build_inventory(
        FIXTURES / "mission-map.yaml", FIXTURES / "workstations.yaml",
        _surface(tmp_path), "macbook-portable")
    rendered = json.dumps(inventory)
    assert inventory["summary"]["unexpected_count"] == 1
    assert "private-client-name" not in rendered
    assert "token" not in rendered


def test_external_symlink_is_not_followed(tmp_path):
    outside = tmp_path.parent / "outside-secret"
    (outside / ".git").mkdir(parents=True)
    (tmp_path / "linked").symlink_to(outside, target_is_directory=True)
    observed, unexpected = _load_module().observe_work_surface(tmp_path, {"linked"})
    assert observed["linked"]["observed_local"] is False
    assert unexpected == 0


def test_gitfile_worktrees_count_as_repositories(tmp_path):
    declared_worktree = tmp_path / "declared"
    declared_worktree.mkdir()
    (declared_worktree / ".git").write_text("gitdir: ../real.git/worktrees/declared\n")
    unknown_worktree = tmp_path / "unknown"
    unknown_worktree.mkdir()
    (unknown_worktree / ".git").write_text("gitdir: ../real.git/worktrees/unknown\n")
    observed, unexpected = _load_module().observe_work_surface(tmp_path, {"declared"})
    assert observed["declared"]["observed_local"] is True
    assert unexpected == 1


def test_same_adapter_contract_for_knowledge_profile(tmp_path):
    module = _load_module()
    repo = tmp_path / "notes"
    (repo / ".git").mkdir(parents=True)
    (repo / "AGENTS.md").write_text("ok")
    observed, _ = module.observe_work_surface(tmp_path, {"notes"})
    declared = {"notes": {"repo": "notes", "profile": "knowledge", "sensitivity": "public", "mcp_required": False}}
    item = module.join_inventory(declared, set(), observed, 0)["repositories"][0]
    assert item["contract"]["complete"] is False
    assert item["contract"]["codex_dir"] is False


def test_distinguishes_configured_missing_declared_missing_and_non_git(tmp_path):
    module = _load_module()
    (tmp_path / "plain").mkdir()
    declared = {
        name: {"repo": name, "profile": "knowledge", "sensitivity": "public", "mcp_required": False}
        for name in ("configured", "absent", "plain")
    }
    observed, unexpected = module.observe_work_surface(tmp_path, set(declared))
    inventory = module.join_inventory(declared, {"configured"}, observed, unexpected)
    states = {item["name"]: item["state"] for item in inventory["repositories"]}
    assert states == {"absent": "declared-missing", "configured": "configured-missing", "plain": "non-git"}
    assert inventory["summary"]["missing"] == 2
    assert inventory["summary"]["non_git"] == 1


def test_summary_reports_configured_and_present_counts(tmp_path):
    inventory = _load_module().build_inventory(
        FIXTURES / "mission-map.yaml", FIXTURES / "workstations.yaml",
        _surface(tmp_path), "macbook-portable")
    assert inventory["summary"]["configured"] == 1
    assert inventory["summary"]["present"] == 1
    assert inventory["summary"]["unknown"] == 1
    assert inventory["summary"]["adapter_coverage"] == {"complete": 1, "incomplete": 1}


def test_markdown_exposes_distinct_states(tmp_path):
    module = _load_module()
    (tmp_path / "plain").mkdir()
    declared = {
        name: {"repo": name, "profile": "knowledge", "sensitivity": "public", "mcp_required": False}
        for name in ("configured", "absent", "plain")
    }
    observed, unexpected = module.observe_work_surface(tmp_path, set(declared))
    markdown = module.render_markdown(module.join_inventory(declared, {"configured"}, observed, unexpected))
    assert "| State |" in markdown
    assert "configured-missing" in markdown
    assert "declared-missing" in markdown
    assert "non-git" in markdown


def test_check_mode_never_writes(tmp_path):
    module = _load_module()
    output = tmp_path / "missing.json"
    assert module.write_or_check(output, "{}\n", check=True) is False
    assert not output.exists()
