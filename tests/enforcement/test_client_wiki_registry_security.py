"""Adversarial snapshot, tool-failure, and raw-root checker tests."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "enforcement" / "check-client-wiki-registry.sh"
REPO_SLUG = "example-org/llm-wiki-example-client"
YQ = shutil.which("yq")


def _entry(**overrides: object) -> dict[str, object]:
    entry: dict[str, object] = {
        "short_name": "example-client",
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


def _write_registry(tmp_path: Path, entry: dict[str, object] | None = None) -> Path:
    path = tmp_path / "registry.yml"
    path.write_text(
        yaml.safe_dump(
            {"registry_version": "0.2", "wikis": [entry or _entry()]},
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def _write_executable(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)
    return path


def _fake_uv(tmp_path: Path) -> Path:
    return _write_executable(
        tmp_path / "fake-uv",
        f"""#!{sys.executable}
import os
import subprocess
import sys
args = sys.argv[1:]
expected = ["run", "--directory", {str(REPO_ROOT)!r}, "--frozen", "python"]
if args[:5] != expected:
    raise SystemExit(97)
if os.environ.get("SWAP_REGISTRY_SOURCE") and "validate-registry" in args:
    result = subprocess.run([sys.executable, *args[5:]])
    os.replace(os.environ["SWAP_REGISTRY_REPLACEMENT"], os.environ["SWAP_REGISTRY_SOURCE"])
    raise SystemExit(result.returncode)
os.execv(sys.executable, [sys.executable, *args[5:]])
""",
    )


def _failing_yq(tmp_path: Path, needle: str) -> Path:
    return _write_executable(
        tmp_path / "fake-yq",
        f"""#!{sys.executable}
import os
import sys
if {needle!r} in " ".join(sys.argv[1:]):
    print("injected late yq failure", file=sys.stderr)
    raise SystemExit(88)
os.execv({YQ!r}, [{YQ!r}, *sys.argv[1:]])
""",
    )


def _run_checker(
    tmp_path: Path,
    registry: Path,
    *,
    yq_bin: str | Path | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "REGISTRY_PATH": str(registry),
            "UV_BIN": str(_fake_uv(tmp_path)),
            "GH_BIN": str(tmp_path / "missing-gh"),
            "YQ_BIN": str(yq_bin or YQ or tmp_path / "missing-yq"),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    if extra_env:
        env.update(extra_env)
    return subprocess.run([str(CHECKER)], cwd=tmp_path, env=env, capture_output=True, text=True)


def test_late_yq_failure_is_dependency_exit_two_not_empty_success(tmp_path):
    registry = _write_registry(tmp_path)
    result = _run_checker(tmp_path, registry, yq_bin=_failing_yq(tmp_path, ".wikis | keys | .[]"))

    assert result.returncode == 2
    assert "yq" in result.stderr.lower()


def test_registry_replacement_after_validation_cannot_change_audit_snapshot(tmp_path):
    registry = _write_registry(tmp_path)
    replacement_dir = tmp_path / "replacement"
    replacement_dir.mkdir()
    replacement = _write_registry(replacement_dir, _entry(status="live"))

    result = _run_checker(
        tmp_path,
        registry,
        extra_env={
            "SWAP_REGISTRY_SOURCE": str(registry),
            "SWAP_REGISTRY_REPLACEMENT": str(replacement),
        },
    )

    assert result.returncode == 0


@pytest.mark.parametrize("kind", ["directory", "missing", "symlink"])
def test_raw_root_availability_uses_metadata_only(tmp_path, kind):
    parent = tmp_path / "raw-parent"
    parent.mkdir()
    root = parent / "raw root with spaces"
    if kind == "directory":
        root.mkdir()
        sentinel = root / "unreadable-sentinel"
        sentinel.write_text("never read\n", encoding="utf-8")
        before = (
            root.stat().st_ino,
            sentinel.stat().st_ino,
            hashlib.sha256(sentinel.read_bytes()).hexdigest(),
        )
        root.chmod(0)
    elif kind == "symlink":
        target = tmp_path / "real-raw"
        target.mkdir()
        root.symlink_to(target, target_is_directory=True)
    registry = _write_registry(
        tmp_path,
        _entry(raw_roots=[str(root)], raw_source_status="mounted"),
    )

    result = _run_checker(tmp_path, registry)

    if kind == "directory":
        root.chmod(0o700)
        after = (
            root.stat().st_ino,
            sentinel.stat().st_ino,
            hashlib.sha256(sentinel.read_bytes()).hexdigest(),
        )
        assert after == before
    assert result.returncode == (0 if kind == "directory" else 1)
    assert "never read" not in result.stdout + result.stderr


def test_public_wiki_raw_root_is_a_firewall_failure(tmp_path):
    registry = _write_registry(
        tmp_path,
        _entry(
            raw_roots=[str(REPO_ROOT.parent / "llm-wiki")],
            raw_source_status="mounted",
        ),
    )

    result = _run_checker(tmp_path, registry)

    assert result.returncode == 1
    assert "firewall" in result.stderr.lower()


def test_clone_audit_ignores_ambient_git_configuration(tmp_path):
    clone = tmp_path / "clone"
    subprocess.run(["git", "init", str(clone)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(clone), "remote", "add", "origin", f"https://github.com/{REPO_SLUG}.git"],
        check=True,
    )
    registry = _write_registry(tmp_path, _entry(local_working_clone=str(clone)))

    result = _run_checker(
        tmp_path,
        registry,
        extra_env={
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "remote.origin.url",
            "GIT_CONFIG_VALUE_0": "https://example.invalid/redirect",
        },
    )

    assert result.returncode == 0


def test_clone_audit_rejects_mismatched_effective_push_destination(tmp_path):
    clone = tmp_path / "clone"
    subprocess.run(["git", "init", str(clone)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(clone), "remote", "add", "origin", f"https://github.com/{REPO_SLUG}.git"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(clone), "config", "remote.origin.pushurl", "https://example.invalid/redirect"],
        check=True,
    )
    registry = _write_registry(tmp_path, _entry(local_working_clone=str(clone)))

    result = _run_checker(tmp_path, registry)

    assert result.returncode == 1
    assert "origin" in result.stderr.lower()
