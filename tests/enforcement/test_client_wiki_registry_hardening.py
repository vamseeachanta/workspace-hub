"""Clone and protected-root checker hardening tests for issue #3449."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
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


def _write_registry(
    tmp_path: Path,
    *,
    entries: list[dict[str, object]],
    relocated: bool | None = None,
) -> Path:
    document: dict[str, object] = {"registry_version": "0.2", "wikis": entries}
    if relocated is not None:
        document["relocated"] = relocated
    path = tmp_path / "registry.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def _fake_uv(tmp_path: Path) -> Path:
    script = tmp_path / "fake-uv"
    script.write_text(
        f"""#!{sys.executable}
import os
import sys

args = sys.argv[1:]
expected = ["run", "--directory", {str(REPO_ROOT)!r}, "--frozen", "python"]
if args[:5] != expected:
    raise SystemExit(97)
os.execv(sys.executable, [sys.executable, *args[5:]])
""",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def _run_checker(tmp_path: Path, registry: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "REGISTRY_PATH": str(registry),
            "UV_BIN": str(_fake_uv(tmp_path)),
            "GH_BIN": str(tmp_path / "missing-gh"),
            "YQ_BIN": str(YQ or tmp_path / "missing-yq"),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    return subprocess.run(
        [str(CHECKER)], cwd=tmp_path, env=env, capture_output=True, text=True
    )


def _make_clone(tmp_path: Path, origin: str) -> Path:
    clone = tmp_path / "clone"
    subprocess.run(["git", "init", str(clone)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(clone), "remote", "add", "origin", origin], check=True
    )
    return clone


@pytest.mark.parametrize(
    "origin",
    [f"https://github.com/{REPO_SLUG}.git", f"git@github.com:{REPO_SLUG}.git"],
)
def test_declared_clone_accepts_exact_origins(tmp_path, origin):
    clone = _make_clone(tmp_path, origin)
    registry = _write_registry(
        tmp_path, entries=[_entry(local_working_clone=str(clone))]
    )
    assert _run_checker(tmp_path, registry).returncode == 0


def test_declared_clone_accepts_independently_allowed_fetch_and_push_origins(tmp_path):
    clone = _make_clone(tmp_path, f"https://github.com/{REPO_SLUG}.git")
    subprocess.run(
        [
            "git",
            "-C",
            str(clone),
            "config",
            "remote.origin.pushurl",
            f"git@github.com:{REPO_SLUG}.git",
        ],
        check=True,
    )
    registry = _write_registry(
        tmp_path, entries=[_entry(local_working_clone=str(clone))]
    )
    assert _run_checker(tmp_path, registry).returncode == 0


@pytest.mark.parametrize("forbidden", ["include", "rewrite"])
def test_declared_clone_rejects_include_and_url_rewrite_config(tmp_path, forbidden):
    clone = _make_clone(tmp_path, f"https://github.com/{REPO_SLUG}.git")
    if forbidden == "include":
        command = ["git", "-C", str(clone), "config", "include.path", "/does/not/exist"]
    else:
        command = [
            "git",
            "-C",
            str(clone),
            "config",
            "url.https://example.invalid/.insteadOf",
            "https://github.com/",
        ]
    subprocess.run(command, check=True)
    registry = _write_registry(
        tmp_path, entries=[_entry(local_working_clone=str(clone))]
    )
    result = _run_checker(tmp_path, registry)
    assert result.returncode == 1
    assert "config" in result.stderr.lower()


@pytest.mark.parametrize("kind", ["missing", "nongit", "wrong-origin"])
def test_declared_clone_failures_are_detected_when_parent_exists(tmp_path, kind):
    clone = tmp_path / "clone"
    if kind == "nongit":
        clone.mkdir()
    elif kind == "wrong-origin":
        _make_clone(tmp_path, "https://example.invalid/lookalike")
    registry = _write_registry(
        tmp_path, entries=[_entry(local_working_clone=str(clone))]
    )
    result = _run_checker(tmp_path, registry)
    assert result.returncode == 1
    assert "clone" in result.stderr.lower()


def test_clone_under_absent_parent_warns_and_skips(tmp_path):
    clone = tmp_path / "absent-parent" / "clone"
    registry = _write_registry(
        tmp_path, entries=[_entry(local_working_clone=str(clone))]
    )
    result = _run_checker(tmp_path, registry)
    assert result.returncode == 0
    assert "WARN" in result.stderr


@pytest.mark.parametrize("protected_kind", ["canonical", "target"])
def test_protected_overlap_fails_before_raw_root_availability_skip(
    tmp_path, protected_kind
):
    common = subprocess.run(
        [
            "git",
            "-C",
            str(REPO_ROOT),
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    canonical = Path(common.stdout.strip()).parent
    protected = (
        canonical
        if protected_kind == "canonical"
        else canonical.parent / "llm-wiki-example-client"
    )
    registry = _write_registry(
        tmp_path,
        entries=[
            _entry(
                raw_roots=[str(protected / "absent" / "raw")],
                raw_source_status="mounted",
            )
        ],
    )
    result = _run_checker(tmp_path, registry)
    assert result.returncode == 1
    assert "overlaps protected" in result.stderr
    assert "skipping availability" not in result.stderr


def test_checker_is_tracked_executable_and_directly_invocable(tmp_path):
    index = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-s", "--", str(CHECKER)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert index.startswith("100755 ")
    assert CHECKER.stat().st_mode & stat.S_IXUSR
    registry = _write_registry(tmp_path, entries=[], relocated=True)
    assert _run_checker(tmp_path, registry).returncode == 0
