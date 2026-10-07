from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest


def load_repair():
    path = Path(__file__).resolve().parents[2] / "scripts/readiness/repair-sibling-sso-flow.py"
    spec = importlib.util.spec_from_file_location("sibling_sso_native_preflight", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout


def commit_all(repo: Path, message: str = "fixture") -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-m", message)


def native_repo(monkeypatch, tmp_path: Path):
    repair = load_repair()
    skill_root = tmp_path / "workspace-hub/.claude/skills"
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text("---\nname: central\n---\n")
    (tmp_path / "workspace-hub/AGENTS.md").write_text("# workspace-hub\n")
    repo = tmp_path / "project"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test User")
    git(repo, "config", "core.autocrlf", "false")
    (repo / ".agents/skills").mkdir(parents=True)
    (repo / "AGENTS.md").write_text(
        "# project\nContract: ../workspace-hub/AGENTS.md\n"
    )
    monkeypatch.setattr(
        repair,
        "load_registry",
        lambda: {
            "machines": {
                "fixture": {
                    "workspace_root": str(tmp_path / "workspace-hub"),
                    "tier1_repo_root": str(tmp_path),
                    "repos": ["project"],
                }
            }
        },
    )
    monkeypatch.setattr(repair, "detect_fs_type", lambda _path: "ext4")
    monkeypatch.setattr(repair, "require_user_approval", lambda _issue: True)
    monkeypatch.setattr(repair, "verify_symlink", lambda *_args: {"status": "pass"})
    return repair, repo


def correct_gemini_link(repo: Path) -> Path:
    link = repo / ".gemini/skills"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to("../../workspace-hub/.claude/skills", target_is_directory=True)
    return link


def build_and_apply(repair, repo: Path) -> tuple[int, dict]:
    manifest = repair.build_manifest("fixture")
    assert manifest["repos"][0]["path"] == str(repo)
    return repair.apply_manifest(manifest), manifest


def scoped_status(repo: Path, *paths: str) -> str:
    return git(
        repo, "status", "--porcelain=v1", "--untracked-files=all", "--", *paths
    )


@pytest.mark.parametrize("dirty_codex", [False, True])
def test_native_dirty_codex_directory_is_preserved_while_gemini_repairs(
    monkeypatch, tmp_path, dirty_codex
):
    repair, repo = native_repo(monkeypatch, tmp_path)
    sentinel = repo / ".codex/skills/sentinel"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_bytes(b"before\n")
    commit_all(repo)
    if dirty_codex:
        sentinel.write_bytes(b"dirty preserved\n")
    before_status = scoped_status(repo, ".codex/skills")

    result, manifest = build_and_apply(repair, repo)

    assert manifest["repos"][0]["codex_admission"] == "native_preserved"
    assert result == 0
    assert sentinel.read_bytes() == (b"dirty preserved\n" if dirty_codex else b"before\n")
    assert scoped_status(repo, ".codex/skills") == before_status
    assert (repo / ".gemini/skills").readlink().as_posix() == "../../workspace-hub/.claude/skills"


def test_native_dirty_codex_file_is_preserved_while_agents_repairs(
    monkeypatch, tmp_path
):
    repair, repo = native_repo(monkeypatch, tmp_path)
    codex = repo / ".codex/skills"
    codex.parent.mkdir(parents=True)
    codex.write_bytes(b"before\n")
    correct_gemini_link(repo)
    (repo / "AGENTS.md").write_text("# project\nContract: ../AGENTS.md\n")
    commit_all(repo)
    codex.write_bytes(b"dirty preserved\n")
    before_status = scoped_status(repo, ".codex/skills")

    result, _manifest = build_and_apply(repair, repo)

    assert result == 0
    assert codex.read_bytes() == b"dirty preserved\n"
    assert scoped_status(repo, ".codex/skills") == before_status
    assert "Contract: ../workspace-hub/AGENTS.md" in (repo / "AGENTS.md").read_text()


def test_native_unselected_codex_substring_dirt_is_preserved(
    monkeypatch, tmp_path
):
    repair, repo = native_repo(monkeypatch, tmp_path)
    legacy = repo / ".codex/skills-legacy/sentinel"
    nested = repo / "sub/.codex/skills/sentinel"
    for path in (legacy, nested):
        path.parent.mkdir(parents=True)
        path.write_bytes(b"before\n")
    commit_all(repo)
    for path in (legacy, nested):
        path.write_bytes(b"dirty preserved\n")
    before_status = scoped_status(repo, ".codex/skills-legacy", "sub/.codex/skills")

    result, _manifest = build_and_apply(repair, repo)

    assert result == 0
    assert legacy.read_bytes() == b"dirty preserved\n"
    assert nested.read_bytes() == b"dirty preserved\n"
    assert scoped_status(repo, ".codex/skills-legacy", "sub/.codex/skills") == before_status
    assert (repo / ".gemini/skills").readlink().as_posix() == "../../workspace-hub/.claude/skills"


def test_native_dirty_selected_gemini_still_blocks(monkeypatch, tmp_path, capsys):
    repair, repo = native_repo(monkeypatch, tmp_path)
    gemini = repo / ".gemini/skills"
    gemini.parent.mkdir(parents=True)
    gemini.write_bytes(b"tracked placeholder\n")
    commit_all(repo)
    gemini.unlink()

    result, _manifest = build_and_apply(repair, repo)

    assert result == 3
    assert '"reason": "dirty_touched_paths"' in capsys.readouterr().err
    assert not gemini.exists()


def test_native_dirty_selected_agents_still_blocks(monkeypatch, tmp_path, capsys):
    repair, repo = native_repo(monkeypatch, tmp_path)
    correct_gemini_link(repo)
    commit_all(repo)
    agents = repo / "AGENTS.md"
    agents.write_text("# project\nContract: ../AGENTS.md\n")

    result, _manifest = build_and_apply(repair, repo)

    assert result == 3
    assert '"reason": "dirty_touched_paths"' in capsys.readouterr().err
    assert "Contract: ../AGENTS.md" in agents.read_text()


def test_absent_native_unsafe_selected_codex_blocks_batch(monkeypatch, tmp_path, capsys):
    repair, repo = native_repo(monkeypatch, tmp_path)
    (repo / ".agents/skills").rmdir()
    (repo / ".agents").rmdir()
    codex = repo / ".codex/skills"
    codex.parent.mkdir()
    codex.write_bytes(b"unsafe selected destination\n")
    commit_all(repo)

    result, manifest = build_and_apply(repair, repo)

    assert manifest["repos"][0]["codex_admission"] == "absent"
    assert result == 3
    assert '"reason": "unsafe_owned_path"' in capsys.readouterr().err
    assert codex.read_bytes() == b"unsafe selected destination\n"
    assert not (repo / ".gemini/skills").exists()


@pytest.mark.parametrize("new_state", ["absent", "blocked"])
def test_apply_time_native_drift_blocks_on_preserved_codex_path(
    monkeypatch, tmp_path, capsys, new_state
):
    repair, repo = native_repo(monkeypatch, tmp_path)
    codex = repo / ".codex/skills"
    codex.mkdir(parents=True)
    (codex / "sentinel").write_bytes(b"preserved\n")
    commit_all(repo)
    manifest = repair.build_manifest("fixture")
    assert manifest["repos"][0]["codex_admission"] == "native_preserved"
    if new_state == "absent":
        (repo / ".agents/skills").rmdir()
        (repo / ".agents").rmdir()
    else:
        (repo / ".agents/skills").rmdir()
        (repo / ".agents").rmdir()
        (repo / ".agents").write_bytes(b"blocked native component\n")

    assert repair.apply_manifest(manifest) == 3
    diagnostic = capsys.readouterr().err
    assert '"reason": "unsafe_owned_path"' in diagnostic
    assert '"kind": "unsafe_owned_path"' in diagnostic
    assert (codex / "sentinel").read_bytes() == b"preserved\n"
    assert not (repo / ".gemini/skills").exists()
