"""Focused regressions for issue #1249 generator and CLAUDE admission."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATOR = REPO_ROOT / "scripts/operations/compliance/generate_agent_adapters.sh"
PROPAGATOR = REPO_ROOT / "scripts/automation/propagate-slash-commands.sh"
GATE = REPO_ROOT / "scripts/enforcement/check_no_new_claude_md.py"


def _find_bash() -> str | None:
    candidates = [
        shutil.which("bash"),
        "C:/Program Files/Git/usr/bin/bash.exe",
        str(Path.home() / "AppData/Local/Programs/Git/usr/bin/bash.exe"),
    ]
    return next((path for path in candidates if path and Path(path).is_file()), None)


BASH = _find_bash()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture_workspace(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "workspace-hub"
    script = root / "scripts/operations/compliance/generate_agent_adapters.sh"
    script.parent.mkdir(parents=True)
    shutil.copy2(GENERATOR, script)
    (root / "AGENTS.md").write_text("Contract-Version: 7\nshared\n")
    sibling = root / "repo-a"
    (sibling / ".git").mkdir(parents=True)
    return root, sibling


def _run_generator(
    root: Path, *arguments: str
) -> subprocess.CompletedProcess[str]:
    if not BASH:
        pytest.skip("bash unavailable")
    bash_path = Path(BASH)
    git_root = bash_path.parents[2]
    env = os.environ.copy()
    env["PATH"] = os.pathsep.join(
        [str(git_root / "usr/bin"), str(git_root / "mingw64/bin"), env.get("PATH", "")]
    )
    return subprocess.run(
        [
            BASH,
            "scripts/operations/compliance/generate_agent_adapters.sh",
            *(arguments or ("--repos", "repo-a")),
        ],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=False
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "fixture@example.invalid")
    _git(repo, "config", "user.name", "Fixture")
    return repo


def _write_baseline(repo: Path, baseline: Path) -> str:
    claude = repo / "CLAUDE.md"
    payload = {
        "schema_version": 1,
        "repositories": [
            {
                "path": str(repo.resolve()),
                "tracked_instruction_files": [
                    {
                        "path": "CLAUDE.md",
                        "classification": "active_instruction",
                        "working": {
                            "presence": "FILE",
                            "is_symlink": False,
                            "is_reparse": False,
                            "content_sha256": _sha256(claude),
                        },
                    }
                ],
            }
        ],
    }
    baseline.write_text(json.dumps(payload, sort_keys=True) + "\n")
    return _sha256(baseline)


def _run_gate(
    repo: Path,
    baseline: Path,
    digest: str,
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(GATE),
            "--repo-root",
            str(repo),
            "--baseline",
            str(baseline),
            "--baseline-sha256",
            digest,
        ],
        text=True,
        env=env,
        capture_output=True,
        check=False,
    )


def test_generator_preserves_existing_agents_and_claude(tmp_path: Path) -> None:
    root, sibling = _fixture_workspace(tmp_path)
    agents = sibling / "AGENTS.md"
    claude = sibling / "CLAUDE.md"
    agents.write_text("unique repository contract\n")
    claude.write_text("legacy baseline\n")
    before = {_sha256(agents), _sha256(claude)}

    result = _run_generator(root)

    assert result.returncode == 0, result.stderr
    assert {_sha256(agents), _sha256(claude)} == before
    assert "preserve: repo-a AGENTS.md already exists" in result.stdout
    assert "preserve: repo-a CLAUDE.md baseline unchanged" in result.stdout


def test_generator_creates_only_missing_agents_and_is_idempotent(tmp_path: Path) -> None:
    root, sibling = _fixture_workspace(tmp_path)

    first = _run_generator(root)
    agents = sibling / "AGENTS.md"
    assert first.returncode == 0, first.stderr
    assert agents.is_file()
    assert not (sibling / "CLAUDE.md").exists()
    first_bytes = agents.read_bytes()

    second = _run_generator(root)
    assert second.returncode == 0, second.stderr
    assert agents.read_bytes() == first_bytes
    assert not (sibling / "CLAUDE.md").exists()


def test_generator_rejects_repo_traversal(tmp_path: Path) -> None:
    root, _ = _fixture_workspace(tmp_path)
    outside = tmp_path / "outside"
    (outside / ".git").mkdir(parents=True)

    result = _run_generator(root, "--repos", "../outside")

    assert result.returncode != 0
    assert "unsafe repository name" in result.stderr
    assert not (outside / "AGENTS.md").exists()


def test_propagator_has_no_claude_creation_status_or_staging() -> None:
    source = PROPAGATOR.read_text(encoding="utf-8")
    assert "CLAUDE_MD_HOME" not in source
    assert "Creating CLAUDE.md" not in source
    assert "git status --porcelain .agent-os CLAUDE.md" not in source
    assert "git add .agent-os CLAUDE.md" not in source


def test_gate_reports_matching_baseline(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "CLAUDE.md").write_text("legacy\n")
    _git(repo, "add", "CLAUDE.md")
    _git(repo, "commit", "-qm", "fixture")
    baseline = tmp_path / "baseline.json"
    digest = _write_baseline(repo, baseline)

    result = _run_gate(repo, baseline, digest)

    assert result.returncode == 0, result.stderr
    assert "BASELINE CLAUDE.md" in result.stdout
    assert "PASS baseline=1 new=0 changed=0" in result.stdout


@pytest.mark.parametrize("change", ["new", "changed"])
def test_gate_rejects_new_or_changed_active_claude(tmp_path: Path, change: str) -> None:
    repo = _init_repo(tmp_path)
    (repo / "CLAUDE.md").write_text("legacy\n")
    _git(repo, "add", "CLAUDE.md")
    _git(repo, "commit", "-qm", "fixture")
    baseline = tmp_path / "baseline.json"
    digest = _write_baseline(repo, baseline)
    target = repo / ("nested/CLAUDE.md" if change == "new" else "CLAUDE.md")
    target.parent.mkdir(exist_ok=True)
    target.write_text("unexpected\n")

    result = _run_gate(repo, baseline, digest)

    assert result.returncode == 1
    assert f"{change.upper()}" in result.stdout


def test_gate_rejects_ignored_new_claude(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "CLAUDE.md").write_text("legacy\n")
    (repo / ".gitignore").write_text("ignored/\n")
    _git(repo, "add", "CLAUDE.md", ".gitignore")
    _git(repo, "commit", "-qm", "fixture")
    baseline = tmp_path / "baseline.json"
    digest = _write_baseline(repo, baseline)
    ignored = repo / "ignored/CLAUDE.md"
    ignored.parent.mkdir()
    ignored.write_text("unexpected\n")

    result = _run_gate(repo, baseline, digest)

    assert result.returncode == 1
    assert "NEW ignored/CLAUDE.md" in result.stdout


def test_gate_ignores_inherited_foreign_git_bindings(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "target")
    (repo / "CLAUDE.md").write_text("legacy\n")
    _git(repo, "add", "CLAUDE.md")
    _git(repo, "commit", "-qm", "fixture")
    baseline = tmp_path / "baseline.json"
    digest = _write_baseline(repo, baseline)
    new_file = repo / "nested/CLAUDE.md"
    new_file.parent.mkdir()
    new_file.write_text("unexpected\n")

    foreign = _init_repo(tmp_path / "foreign")
    env = os.environ.copy()
    env.update(
        {
            "GIT_DIR": str(foreign / ".git"),
            "GIT_WORK_TREE": str(foreign),
            "GIT_COMMON_DIR": str(foreign / ".git"),
        }
    )
    result = _run_gate(repo, baseline, digest, env=env)

    assert result.returncode == 1
    assert "NEW nested/CLAUDE.md" in result.stdout


def test_gate_excludes_only_named_non_active_classes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "CLAUDE.md").write_text("legacy\n")
    _git(repo, "add", "CLAUDE.md")
    _git(repo, "commit", "-qm", "fixture")
    baseline = tmp_path / "baseline.json"
    digest = _write_baseline(repo, baseline)
    for relative in (
        "archive/CLAUDE.md",
        "vendor/x/CLAUDE.md",
        "tests/fixtures/CLAUDE.md",
        ".agents/skills/creative/popular-web-designs/templates/CLAUDE.md",
        ".claude/skills/creative/popular-web-designs/templates/CLAUDE.md",
    ):
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n")

    result = _run_gate(repo, baseline, digest)

    assert result.returncode == 0, result.stderr
    assert "excluded=5" in result.stdout


def test_gate_fails_closed_on_digest_root_or_symlink_ambiguity(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "CLAUDE.md").write_text("legacy\n")
    _git(repo, "add", "CLAUDE.md")
    _git(repo, "commit", "-qm", "fixture")
    baseline = tmp_path / "baseline.json"
    digest = _write_baseline(repo, baseline)

    wrong_digest = _run_gate(repo, baseline, "0" * 64)
    assert wrong_digest.returncode == 2
    assert "baseline digest mismatch" in wrong_digest.stderr

    payload = json.loads(baseline.read_text())
    payload["repositories"][0]["path"] = str((tmp_path / "other").resolve())
    baseline.write_text(json.dumps(payload, sort_keys=True) + "\n")
    wrong_root = _run_gate(repo, baseline, _sha256(baseline))
    assert wrong_root.returncode == 2
    assert "repository root mismatch" in wrong_root.stderr


@pytest.mark.parametrize("unsafe_path", ["../CLAUDE.md", "C:relative/CLAUDE.md"])
def test_gate_rejects_unsafe_baseline_paths(tmp_path: Path, unsafe_path: str) -> None:
    repo = _init_repo(tmp_path)
    (repo / "CLAUDE.md").write_text("legacy\n")
    _git(repo, "add", "CLAUDE.md")
    _git(repo, "commit", "-qm", "fixture")
    baseline = tmp_path / "baseline.json"
    _write_baseline(repo, baseline)
    payload = json.loads(baseline.read_text())
    payload["repositories"][0]["tracked_instruction_files"][0]["path"] = unsafe_path
    baseline.write_text(json.dumps(payload, sort_keys=True) + "\n")

    result = _run_gate(repo, baseline, _sha256(baseline))

    assert result.returncode == 2
    assert "unsafe baseline path" in result.stderr



def test_gate_rejects_symlink_ambiguity(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    real = repo / "real.md"
    real.write_text("legacy\n")
    claude = repo / "CLAUDE.md"
    try:
        claude.symlink_to("real.md")
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    _git(repo, "add", "CLAUDE.md", "real.md")
    _git(repo, "commit", "-qm", "fixture")
    baseline = tmp_path / "baseline.json"
    digest = _write_baseline(repo, baseline)

    result = _run_gate(repo, baseline, digest)

    assert result.returncode == 2
    assert "symlink" in result.stderr


def test_gate_rejects_symlinked_parent_escape(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    external = outside / "CLAUDE.md"
    external.write_text("legacy\n")
    linked = repo / "linked"
    try:
        linked.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink unavailable: {exc}")
    baseline = tmp_path / "baseline.json"
    payload = {
        "schema_version": 1,
        "repositories": [
            {
                "path": str(repo.resolve()),
                "tracked_instruction_files": [
                    {
                        "path": "linked/CLAUDE.md",
                        "working": {"content_sha256": _sha256(external)},
                    }
                ],
            }
        ],
    }
    baseline.write_text(json.dumps(payload, sort_keys=True) + "\n")

    result = _run_gate(repo, baseline, _sha256(baseline))

    assert result.returncode == 2
    assert "linked ancestor" in result.stderr or "escapes repo root" in result.stderr
