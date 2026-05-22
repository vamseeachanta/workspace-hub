from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path


def load_repair():
    path = Path(__file__).resolve().parents[2] / "scripts" / "readiness" / "repair-sibling-sso-flow.py"
    spec = importlib.util.spec_from_file_location("sibling_sso_repair", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_repair_apply_blocked_when_live_label_missing(monkeypatch):
    repair = load_repair()

    def fake_run(*args, **kwargs):
        class Result:
            returncode = 0
            stdout = "status:plan-review\n"
            stderr = ""
        return Result()

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
    registry = {
        "machines": {
            "dev-primary": {
                "hostname": "ace-linux-1",
                "hostname_aliases": ["vamsee-linux1"],
                "workspace_root": str(tmp_path / "workspace-hub"),
                "tier1_repo_root": str(tmp_path),
                "repos": ["digitalmodel"],
            }
        }
    }
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
    registry = {
        "machines": {
            "dev-primary": {
                "hostname": "ace-linux-1",
                "workspace_root": str(tmp_path / "workspace-hub"),
                "tier1_repo_root": str(tmp_path),
                "repos": ["digitalmodel"],
            }
        }
    }
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
    registry = {
        "machines": {
            "dev-primary": {
                "hostname": "ace-linux-1",
                "workspace_root": str(tmp_path / "workspace-hub"),
                "tier1_repo_root": str(tmp_path),
                "repos": ["digitalmodel"],
            }
        }
    }
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
    registry = {
        "machines": {
            "dev-primary": {
                "hostname": "ace-linux-1",
                "workspace_root": str(tmp_path / "workspace-hub"),
                "tier1_repo_root": str(tmp_path),
                "repos": ["digitalmodel"],
            }
        }
    }
    monkeypatch.setattr(repair, "load_registry", lambda: registry)

    manifest = repair.build_manifest("dev-primary")

    actions = manifest["repos"][0]["actions"]
    assert any(
        action["kind"] == "rewrite_agents_pointer" and action["from"] == "../AGENTS.md"
        for action in actions
    )


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


def test_rewrite_agents_pointer_updates_contract_lines_only(tmp_path):
    repair = load_repair()
    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        "# Repo\n"
        "Contract: ../AGENTS.md | Source: src/repo/\n"
        "Notes: literal ../AGENTS.md in prose should remain unchanged.\n"
        "Legacy contract: ../AGENTS.md\n"
    )

    repair.rewrite_agents_pointer(agents, "../AGENTS.md", "../workspace-hub/AGENTS.md")

    assert agents.read_text() == (
        "# Repo\n"
        "Contract: ../workspace-hub/AGENTS.md | Source: src/repo/\n"
        "Notes: literal ../AGENTS.md in prose should remain unchanged.\n"
        "Legacy contract: ../workspace-hub/AGENTS.md\n"
    )
