from __future__ import annotations

import importlib.util
import subprocess
import os
import stat
import sys
from types import SimpleNamespace

import pytest
from pathlib import Path

def load_repair():
    path = Path(__file__).resolve().parents[2] / "scripts" / "readiness" / "repair-sibling-sso-flow.py"
    spec = importlib.util.spec_from_file_location("sibling_sso_repair", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def fixture_registry(tmp_path, aliases=False):
    config = {"hostname": "ace-linux-1", "workspace_root": str(tmp_path / "workspace-hub"),
              "tier1_repo_root": str(tmp_path), "repos": ["digitalmodel"]}
    if aliases:
        config["hostname_aliases"] = ["vamsee-linux1"]
    return {"machines": {"dev-primary": config}}
def test_repair_apply_blocked_when_live_label_missing(monkeypatch):
    repair = load_repair()
    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout="status:plan-review\n", stderr="")
    monkeypatch.setattr(repair.subprocess, "run", fake_run)
    assert repair.require_user_approval(2775) is False
def test_repair_apply_fails_closed_on_gh_error(monkeypatch):
    repair = load_repair()
    def fake_run(*args, **kwargs):
        raise FileNotFoundError("gh")
    monkeypatch.setattr(repair.subprocess, "run", fake_run)
    assert repair.require_user_approval(2775) is False
def test_repair_refuses_when_fs_is_ntfs3(monkeypatch, tmp_path):
    repair = load_repair()
    monkeypatch.setattr(repair, "detect_fs_type", lambda _path: "ntfs3")
    result = repair.preflight_sibling_repo(tmp_path)
    assert result["status"] == "blocked"
    assert result["reason"] == "ntfs3_mount"
def test_detect_fs_type_returns_unknown_when_findmnt_missing(monkeypatch, tmp_path):
    repair = load_repair()
    def fake_run(*_args, **_kwargs):
        raise FileNotFoundError("findmnt")
    monkeypatch.setattr(repair, "run", fake_run)
    assert repair.detect_fs_type(tmp_path) == "unknown"
def test_repair_post_write_verifies_symbolic_link(tmp_path):
    repair = load_repair()
    target = tmp_path / "workspace-hub" / ".claude" / "skills"
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text("---\nname: central\n---\n")
    repo = tmp_path / "digitalmodel"
    provider = repo / ".codex"
    provider.mkdir(parents=True)
    link = provider / "skills"
    link.symlink_to("../../workspace-hub/.claude/skills")
    result = repair.verify_symlink(link, "../../workspace-hub/.claude/skills")
    assert result["status"] == "pass"
def test_repair_manifest_creates_missing_provider_skill_links(monkeypatch, tmp_path):
    repair = load_repair()
    hub = tmp_path / "workspace-hub"
    hub.mkdir()
    (hub / "AGENTS.md").write_text("# Workspace Hub\n")
    repo = tmp_path / "digitalmodel"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# digitalmodel\nContract: ../workspace-hub/AGENTS.md\n")
    registry = fixture_registry(tmp_path, aliases=True)
    monkeypatch.setattr(repair, "load_registry", lambda: registry)
    manifest = repair.build_manifest("dev-primary")
    actions = manifest["repos"][0]["actions"]
    assert {action["path"] for action in actions} == {
        str(repo / ".codex" / "skills"),
        str(repo / ".gemini" / "skills"),
    }
    assert repair.build_manifest("ace-linux-1")["machine"] == "dev-primary"
    assert repair.build_manifest("vamsee-linux1")["machine"] == "dev-primary"

def test_repair_manifest_blocks_non_hub_local_agents_contract(monkeypatch, tmp_path):
    repair = load_repair()
    repo = tmp_path / "digitalmodel"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# digitalmodel\nLocal-only divergent contract\n")
    registry = fixture_registry(tmp_path)
    monkeypatch.setattr(repair, "load_registry", lambda: registry)
    manifest = repair.build_manifest("dev-primary")
    actions = manifest["repos"][0]["actions"]
    assert {
        (action["kind"], action.get("reason"))
        for action in actions
    } >= {("blocked", "missing_workspace_hub_contract")}

def test_repair_manifest_blocks_arbitrary_workspace_hub_agents_mention(monkeypatch, tmp_path):
    repair = load_repair()
    repo = tmp_path / "digitalmodel"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "# digitalmodel\n"
        "Notes: a useful file exists at ../workspace-hub/AGENTS.md.\n"
    )
    registry = fixture_registry(tmp_path)
    monkeypatch.setattr(repair, "load_registry", lambda: registry)
    manifest = repair.build_manifest("dev-primary")
    actions = manifest["repos"][0]["actions"]
    assert {action.get("reason") for action in actions if action["kind"] == "blocked"} >= {
        "missing_workspace_hub_contract"
    }

def test_repair_manifest_rewrites_mixed_stale_parent_contract(monkeypatch, tmp_path):
    repair = load_repair()
    repo = tmp_path / "digitalmodel"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "# digitalmodel\n"
        "Contract: ../workspace-hub/AGENTS.md | Source: src/digitalmodel/\n"
        "Legacy contract: ../AGENTS.md\n"
    )
    registry = fixture_registry(tmp_path)
    monkeypatch.setattr(repair, "load_registry", lambda: registry)
    manifest = repair.build_manifest("dev-primary")
    actions = manifest["repos"][0]["actions"]
    assert any(
        action["kind"] == "rewrite_agents_pointer" and action["from"] == "../AGENTS.md"
        for action in actions
    )

def test_repair_manifest_rewrites_inherits_prose_parent_contract(monkeypatch, tmp_path):
    repair = load_repair()
    repo = tmp_path / "digitalmodel"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "# digitalmodel\n"
        "This repository inherits the canonical contract from:\n"
        "../AGENTS.md\n"
    )
    registry = fixture_registry(tmp_path)
    monkeypatch.setattr(repair, "load_registry", lambda: registry)
    manifest = repair.build_manifest("dev-primary")
    actions = manifest["repos"][0]["actions"]
    assert any(
        action["kind"] == "rewrite_agents_pointer" and action["from"] == "../AGENTS.md"
        for action in actions
    )

def test_repair_manifest_accepts_inherits_prose_workspace_hub_contract(monkeypatch, tmp_path):
    repair = load_repair()
    hub = tmp_path / "workspace-hub"
    hub.mkdir()
    (hub / "AGENTS.md").write_text("# workspace-hub\n")
    skill_root = hub / ".claude" / "skills"
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text("---\nname: central\n---\n")
    repo = tmp_path / "digitalmodel"
    repo.mkdir()
    (repo / ".codex").mkdir()
    (repo / ".gemini").mkdir()
    (repo / ".codex" / "skills").symlink_to("../../workspace-hub/.claude/skills")
    (repo / ".gemini" / "skills").symlink_to("../../workspace-hub/.claude/skills")
    (repo / "AGENTS.md").write_text(
        "# digitalmodel\n"
        "This repository inherits the canonical contract from:\n"
        "../workspace-hub/AGENTS.md\n"
    )
    registry = fixture_registry(tmp_path)
    monkeypatch.setattr(repair, "load_registry", lambda: registry)
    manifest = repair.build_manifest("dev-primary")
    assert manifest["repos"][0]["actions"] == []

def test_preflight_blocks_unexpected_owned_regular_file(monkeypatch, tmp_path):
    repair = load_repair()
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=tmp_path, check=True, stdout=subprocess.PIPE)
    monkeypatch.setattr(repair, "detect_fs_type", lambda _path: "ext4")
    owned = tmp_path / ".codex" / "skills"
    owned.parent.mkdir()
    owned.write_text("user data\n")
    result = repair.preflight_sibling_repo(tmp_path)
    assert result["status"] == "blocked"
    assert result["reason"] == "unsafe_owned_path"

def test_owned_path_restore_preserves_unrelated_dirty_file(tmp_path):
    repair = load_repair()
    owned = tmp_path / ".codex" / "skills"
    owned.parent.mkdir()
    owned.symlink_to("../../.claude/skills")
    unrelated = tmp_path / "notes.txt"
    unrelated.write_text("dirty\n")
    backups = repair.capture_owned_paths([owned])
    owned.unlink()
    owned.symlink_to("../../workspace-hub/.claude/skills")
    repair.restore_owned_paths(backups)
    assert unrelated.read_text() == "dirty\n"
    assert owned.is_symlink()
    assert owned.readlink().as_posix() == "../../.claude/skills"

def test_preflight_blocks_repo_behind_upstream(monkeypatch, tmp_path):
    repair = load_repair()
    monkeypatch.setattr(repair, "detect_fs_type", lambda _path: "ext4")
    (tmp_path / ".git").mkdir()
    def fake_git_output(_repo, args):
        class Result:
            returncode = 0
            stdout = ""
            stderr = ""
        result = Result()
        if args == ["status", "--porcelain"]:
            result.stdout = ""
        elif args == ["symbolic-ref", "--short", "HEAD"]:
            result.stdout = "main\n"
        elif args == ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]:
            result.stdout = "origin/main\n"
        elif args == ["rev-list", "--left-right", "--count", "@{u}...HEAD"]:
            result.stdout = "2\t0\n"
        return result
    monkeypatch.setattr(repair, "git_output", fake_git_output)
    result = repair.preflight_sibling_repo(tmp_path)
    assert result["status"] == "blocked"
    assert result["reason"] == "behind_upstream"

def test_classify_agents_contract_blocks_arbitrary_stale_parent_reference(tmp_path):
    repair = load_repair()
    agents = tmp_path / "AGENTS.md"
    agents.write_text("# Repo\nNotes: literal ../AGENTS.md in prose should not be auto-rewritten.\n")
    result = repair.classify_agents_contract(tmp_path, tmp_path.parent)
    assert result["status"] == "blocked"
    assert result["reason"] == "arbitrary_stale_parent_reference"

@pytest.mark.parametrize("before,after", [
    ("Contract: ../AGENTS.md | Source: src/repo/\nLegacy contract: ../AGENTS.md\n",
     "Contract: ../workspace-hub/AGENTS.md | Source: src/repo/\nLegacy contract: ../workspace-hub/AGENTS.md\n"),
    ("This repository inherits the canonical contract from:\n../AGENTS.md\n",
     "This repository inherits the canonical contract from:\n../workspace-hub/AGENTS.md\n")])
def test_rewrite_agents_pointer_updates_only_contract_lines(tmp_path, before, after):
    repair = load_repair()
    agents = tmp_path / "AGENTS.md"
    notes = "Notes: literal ../AGENTS.md in prose should remain unchanged.\n"
    agents.write_text("# Repo\n" + before + notes)
    repair.rewrite_agents_pointer(agents, "../AGENTS.md", "../workspace-hub/AGENTS.md")
    assert agents.read_text() == "# Repo\n" + after + notes

def test_apply_manifest_applies_repairable_symlinks_despite_blocked_agents(monkeypatch, tmp_path):
    repair = load_repair()
    hub = tmp_path / "workspace-hub"
    skill_root = hub / ".claude" / "skills"
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text("---\nname: central\n---\n")
    repo = tmp_path / "digitalmodel"
    (repo / ".codex").mkdir(parents=True)
    (repo / ".gemini").mkdir(parents=True)
    codex_link = repo / ".codex" / "skills"
    gemini_link = repo / ".gemini" / "skills"
    codex_link.symlink_to("../../.claude/skills")
    gemini_link.symlink_to("../../.claude/skills")
    (repo / "AGENTS.md").write_text("# digitalmodel\nLocal-only divergent contract\n")
    manifest = {
        "repos": [
            {
                "repo": "digitalmodel",
                "path": str(repo),
                "actions": [
                    {"kind": "rewrite_symlink", "path": str(codex_link), "target": "../../workspace-hub/.claude/skills"},
                    {"kind": "rewrite_symlink", "path": str(gemini_link), "target": "../../workspace-hub/.claude/skills"},
                    {"kind": "blocked", "path": str(repo / "AGENTS.md"), "reason": "missing_workspace_hub_contract"},
                ],
            }
        ]
    }
    monkeypatch.setattr(repair, "require_user_approval", lambda _issue: True)
    monkeypatch.setattr(repair, "preflight_sibling_repo", lambda _repo: {"status": "pass"})
    assert repair.apply_manifest(manifest) == 3
    assert codex_link.readlink().as_posix() == "../../workspace-hub/.claude/skills"
    assert gemini_link.readlink().as_posix() == "../../workspace-hub/.claude/skills"

def native_fixture(monkeypatch, tmp_path):
    repair = load_repair()
    repo = tmp_path / "project"
    repo.mkdir()
    monkeypatch.setattr(repair, "load_registry", lambda: {"machines": {"fixture": {
        "workspace_root": str(tmp_path / "workspace-hub"),
        "tier1_repo_root": str(tmp_path), "repos": ["project"]}}})
    monkeypatch.setattr(repair, "classify_agents_contract", lambda *_: {"status": "ok"})
    return repair, repo

@pytest.mark.parametrize("adapter", ["absent", "file", "link", "directory"])
def test_native_manifest_preserves_adapters_and_selects_gemini(monkeypatch, tmp_path, adapter):
    repair, repo = native_fixture(monkeypatch, tmp_path)
    (repo / ".agents/skills").mkdir(parents=True)
    legacy = repo / ".codex/skills"
    legacy.parent.mkdir()
    if adapter == "file":
        legacy.write_bytes(b"flattened legacy pointer\n")
    elif adapter == "link":
        legacy.symlink_to("missing-target", target_is_directory=True)
    elif adapter == "directory":
        legacy.mkdir()
        (legacy / "sentinel").write_bytes(b"preserved")
    before = repair.capture_owned_paths([legacy]) if adapter != "directory" else None
    record = repair.build_manifest("fixture")["repos"][0]
    assert record["codex_admission"] == "native_preserved"
    assert record["actions"] == [{"kind": "rewrite_symlink",
        "path": str(repo / ".gemini/skills"), "target": "../../workspace-hub/.claude/skills"}]
    if adapter == "directory":
        assert (legacy / "sentinel").read_bytes() == b"preserved"
    else:
        assert repair.capture_owned_paths([legacy]) == before

def test_native_manifest_reports_blocked_component(monkeypatch, tmp_path):
    repair, repo = native_fixture(monkeypatch, tmp_path)
    (repo / ".agents").write_bytes(b"not a directory")
    record = repair.build_manifest("fixture")["repos"][0]
    assert record["codex_admission"] == "blocked"
    assert {a.get("reason") for a in record["actions"]} >= {"native_skill_root_unresolved"}
    assert any(a["path"] == str(repo / ".gemini/skills") and a["kind"] == "rewrite_symlink"
               for a in record["actions"])

def test_stale_codex_batch_refused_before_capture(monkeypatch, tmp_path):
    repair, repo = native_fixture(monkeypatch, tmp_path)
    actions = repair.build_manifest("fixture")["repos"][0]["actions"]
    (repo / ".agents/skills").mkdir(parents=True)
    monkeypatch.setattr(repair, "capture_owned_paths", lambda *_: pytest.fail("captured stale batch"))
    assert repair._apply_repairable_actions("project", actions, repo) == 4
    assert not (repo / ".codex").exists() and not (repo / ".gemini").exists()

def test_changed_native_state_rolls_back_earlier_gemini(monkeypatch, tmp_path):
    repair, repo = native_fixture(monkeypatch, tmp_path)
    gemini = repo / ".gemini/skills"
    gemini.parent.mkdir()
    gemini.symlink_to("original-target", target_is_directory=True)
    actions = [{"kind": "rewrite_symlink", "path": str(repo / provider / "skills"),
                "target": "changed-target"} for provider in (".gemini", ".codex")]
    states = iter(["absent", "native"])
    def changed_root(_):
        state = next(states)
        if state == "native":
            (repo / ".codex/skills").mkdir(parents=True)
            (repo / ".codex/skills/sentinel").write_bytes(b"concurrent preserved")
        return state
    monkeypatch.setattr(repair, "classify_native_root", changed_root)
    monkeypatch.setattr(repair, "verify_symlink", lambda *_: {"status": "pass"})
    assert repair._apply_repairable_actions("project", actions, repo) == 4
    assert os.readlink(gemini) == "original-target"
    assert (repo / ".codex/skills/sentinel").read_bytes() == b"concurrent preserved"

@pytest.mark.parametrize("relative", ["../foreign/.codex/skills", ".codex/other", ".agents/skills"])
def test_action_outside_owned_locations_is_refused(monkeypatch, tmp_path, relative):
    repair, repo = native_fixture(monkeypatch, tmp_path)
    action = {"kind": "rewrite_symlink", "path": str(repo / relative), "target": "unused"}
    monkeypatch.setattr(repair, "capture_owned_paths", lambda *_: pytest.fail("captured invalid path"))
    assert repair._apply_repairable_actions("project", [action], repo) == 4

def load_native_probe():
    path = Path(__file__).resolve().parents[2] / "scripts/skills/native_skill_root.py"
    spec = importlib.util.spec_from_file_location("native_probe_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

@pytest.mark.parametrize("entry,kind,expected", [
    (".agents", "absent", "absent"), (".agents/skills", "absent", "absent"),
    (".agents/skills", "directory", "native"), (".agents", "file", "blocked"),
    (".agents/skills", "file", "blocked"), (".agents", "link", "blocked"),
    (".agents/skills", "link", "blocked")])
def test_native_probe_real_components(tmp_path, entry, kind, expected):
    probe = load_native_probe()
    path = tmp_path / entry
    path.parent.mkdir(parents=True, exist_ok=True)
    if kind == "directory":
        path.mkdir()
    elif kind == "file":
        path.write_bytes(b"sentinel")
    elif kind == "link":
        path.symlink_to("missing-target", target_is_directory=True)
    assert probe.classify_native_root(tmp_path) == expected
    result = subprocess.run([sys.executable, probe.__file__, str(tmp_path)], capture_output=True, text=True)
    assert (result.stdout.strip(), result.returncode) == (expected, 2 if expected == "blocked" else 0)

@pytest.mark.parametrize("platform,attributes,expected", [
    ("nt", 16, "native"), ("nt", 16 | 1024, "blocked"),
    ("nt", None, "blocked"), ("unknown", 16, "blocked")])
def test_native_probe_simulated_platform_metadata(monkeypatch, tmp_path, platform, attributes, expected):
    probe = load_native_probe()
    metadata = SimpleNamespace(st_mode=stat.S_IFDIR | 0o755)
    if attributes is not None:
        metadata.st_file_attributes = attributes
    monkeypatch.setattr(probe, "os", SimpleNamespace(name=platform, lstat=lambda _: metadata))
    assert probe.classify_native_root(tmp_path) == expected

def test_native_probe_permission_error_is_not_absence(monkeypatch, tmp_path):
    probe = load_native_probe()
    def denied(_):
        raise PermissionError("fixture access denied")
    monkeypatch.setattr(probe, "os", SimpleNamespace(name="posix", lstat=denied))
    assert probe.classify_native_root(tmp_path) == "blocked"
