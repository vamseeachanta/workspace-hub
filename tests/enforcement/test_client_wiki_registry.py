"""Hermetic subprocess tests for the client-wiki registry checker."""
from __future__ import annotations

import json
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
    entries: list[dict[str, object]] | None = None,
    version: object = "0.2",
    relocated: bool | None = None,
) -> Path:
    document: dict[str, object] = {
        "registry_version": version,
        "wikis": entries if entries is not None else [_entry()],
    }
    if relocated is not None:
        document["relocated"] = relocated
    path = tmp_path / "registry.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def _write_executable(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)
    return path


def _fake_uv(tmp_path: Path, *, fail: bool = False) -> Path:
    script = tmp_path / "fake-uv"
    return _write_executable(
        script,
        f"""#!{sys.executable}
import os
import sys

args = sys.argv[1:]
expected = ["run", "--directory", {str(REPO_ROOT)!r}, "--frozen", "python"]
if args[:5] != expected:
    print("unexpected uv arguments: " + repr(args), file=sys.stderr)
    raise SystemExit(97)
if {fail!r}:
    raise SystemExit(86)
os.execv(sys.executable, [sys.executable, *args[5:]])
""",
    )


def _fake_gh(tmp_path: Path) -> tuple[Path, Path, Path]:
    script = tmp_path / "fake-gh"
    log = tmp_path / "gh.calls"
    payload = tmp_path / "gh.json"
    _write_executable(
        script,
        f"""#!{sys.executable}
import os
import sys

args = sys.argv[1:]
with open(os.environ["FAKE_GH_LOG"], "ab") as stream:
    stream.write(b"\\0".join(arg.encode() for arg in args) + b"\\0")
expected = ["repo", "view", {REPO_SLUG!r}, "--json", "visibility,isArchived"]
if args != expected:
    print("unexpected gh arguments", file=sys.stderr)
    raise SystemExit(97)
with open(os.environ["FAKE_GH_PAYLOAD"], encoding="utf-8") as stream:
    sys.stdout.write(stream.read())
raise SystemExit(int(os.environ.get("FAKE_GH_RC", "0")))
""",
    )
    return script, log, payload


def _run_checker(
    tmp_path: Path,
    registry: Path,
    *,
    uv_bin: str | Path | None = None,
    gh_bin: str | Path | None = None,
    yq_bin: str | Path | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "REGISTRY_PATH": str(registry),
            "UV_BIN": str(uv_bin or _fake_uv(tmp_path)),
            "GH_BIN": str(gh_bin or tmp_path / "missing-gh"),
            "YQ_BIN": str(yq_bin or YQ or tmp_path / "missing-yq"),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [str(CHECKER)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )


def _gh_args(log: Path) -> list[str]:
    if not log.exists():
        return []
    return [part.decode() for part in log.read_bytes().split(b"\0") if part]


def _make_clone(tmp_path: Path, origin: str) -> Path:
    clone = tmp_path / "clone"
    subprocess.run(["git", "init", str(clone)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(clone), "remote", "add", "origin", origin],
        check=True,
    )
    return clone


def test_missing_registry_warns_without_resolving_dependencies(tmp_path):
    result = _run_checker(
        tmp_path,
        tmp_path / "absent.yml",
        uv_bin=tmp_path / "missing-uv",
        yq_bin=tmp_path / "missing-yq",
    )

    assert result.returncode == 0
    assert "WARN" in result.stderr


def test_exact_public_stub_skips_without_uv_or_gh(tmp_path):
    registry = _write_registry(tmp_path, entries=[], relocated=True)

    result = _run_checker(tmp_path, registry, uv_bin=tmp_path / "missing-uv")

    assert result.returncode == 0
    assert "public stub" in result.stdout


@pytest.mark.parametrize(
    ("version", "relocated", "entries"),
    [
        (0.2, True, []),
        ("0.2", False, []),
        ("0.2", True, [_entry()]),
    ],
)
def test_public_stub_lookalikes_fail_closed(tmp_path, version, relocated, entries):
    registry = _write_registry(
        tmp_path,
        version=version,
        relocated=relocated,
        entries=entries,
    )

    result = _run_checker(tmp_path, registry, uv_bin=tmp_path / "missing-uv")

    assert result.returncode == 1


def test_malformed_yaml_is_not_treated_as_empty_stub(tmp_path):
    registry = tmp_path / "registry.yml"
    registry.write_text("registry_version: ['broken'\n", encoding="utf-8")

    result = _run_checker(tmp_path, registry)

    assert result.returncode == 1


def test_missing_yq_is_dependency_exit_two(tmp_path):
    registry = _write_registry(tmp_path)

    result = _run_checker(tmp_path, registry, yq_bin=tmp_path / "missing-yq")

    assert result.returncode == 2


def test_nonempty_registry_missing_or_failed_uv_exits_two(tmp_path):
    registry = _write_registry(tmp_path)
    missing = _run_checker(tmp_path, registry, uv_bin=tmp_path / "missing-uv")
    failed = _run_checker(tmp_path, registry, uv_bin=_fake_uv(tmp_path, fail=True))

    assert missing.returncode == 2
    assert failed.returncode == 2


def test_invalid_current_registry_exits_one(tmp_path):
    registry = _write_registry(tmp_path, entries=[_entry(ingestion_enabled=True)])

    result = _run_checker(tmp_path, registry)

    assert result.returncode == 1
    assert "ingestion_enabled" in result.stderr


def test_legacy_registry_warns_and_planned_row_avoids_gh(tmp_path):
    legacy = {
        "short_name": "example-client",
        "repo": REPO_SLUG,
        "visibility": "PRIVATE",
        "posture": "client-private",
        "status": "planned",
        "raw_roots": [],
    }
    registry = _write_registry(tmp_path, entries=[legacy], version=0.1)

    result = _run_checker(tmp_path, registry)

    assert result.returncode == 0
    assert "legacy" in (result.stdout + result.stderr).lower()


@pytest.mark.parametrize(
    "entry",
    [
        _entry(),
        _entry(status="retired"),
        _entry(raw_roots=["/unmounted/example"], raw_source_status="mounted"),
    ],
)
def test_disabled_planned_or_retired_rows_do_not_require_gh(tmp_path, entry):
    registry = _write_registry(tmp_path, entries=[entry])

    result = _run_checker(tmp_path, registry, gh_bin=tmp_path / "missing-gh")

    assert result.returncode == 0


@pytest.mark.parametrize("status", ["bootstrapped", "live"])
@pytest.mark.parametrize(
    ("payload", "gh_rc", "expected"),
    [
        ({"visibility": "PRIVATE", "isArchived": False}, 0, 0),
        ({"visibility": "PUBLIC", "isArchived": False}, 0, 1),
        ({"visibility": "PRIVATE", "isArchived": True}, 0, 1),
        ({"visibility": "PRIVATE", "isArchived": False}, 9, 1),
    ],
)
def test_live_rows_use_exact_gh_contract(tmp_path, status, payload, gh_rc, expected):
    registry = _write_registry(tmp_path, entries=[_entry(status=status)])
    gh, log, payload_file = _fake_gh(tmp_path)
    payload_file.write_text(json.dumps(payload), encoding="utf-8")

    result = _run_checker(
        tmp_path,
        registry,
        gh_bin=gh,
        extra_env={
            "FAKE_GH_LOG": str(log),
            "FAKE_GH_PAYLOAD": str(payload_file),
            "FAKE_GH_RC": str(gh_rc),
        },
    )

    assert result.returncode == expected
    assert _gh_args(log) == [
        "repo",
        "view",
        REPO_SLUG,
        "--json",
        "visibility,isArchived",
    ]


def test_live_row_missing_gh_is_dependency_exit_two(tmp_path):
    registry = _write_registry(tmp_path, entries=[_entry(status="live")])

    result = _run_checker(tmp_path, registry, gh_bin=tmp_path / "missing-gh")

    assert result.returncode == 2


@pytest.mark.parametrize(
    "origin",
    [
        f"https://github.com/{REPO_SLUG}",
        f"https://github.com/{REPO_SLUG}.git",
        f"git@github.com:{REPO_SLUG}.git",
    ],
)
def test_declared_clone_accepts_exact_origins(tmp_path, origin):
    clone = _make_clone(tmp_path, origin)
    registry = _write_registry(tmp_path, entries=[_entry(local_working_clone=str(clone))])

    result = _run_checker(tmp_path, registry)

    assert result.returncode == 0


@pytest.mark.parametrize("kind", ["missing", "nongit", "wrong-origin"])
def test_declared_clone_failures_are_detected_when_parent_exists(tmp_path, kind):
    clone = tmp_path / "clone"
    if kind == "nongit":
        clone.mkdir()
    elif kind == "wrong-origin":
        _make_clone(tmp_path, "https://example.invalid/lookalike")
    registry = _write_registry(tmp_path, entries=[_entry(local_working_clone=str(clone))])

    result = _run_checker(tmp_path, registry)

    assert result.returncode == 1
    assert "clone" in result.stderr.lower()


def test_clone_under_absent_parent_warns_and_skips(tmp_path):
    clone = tmp_path / "absent-parent" / "clone"
    registry = _write_registry(tmp_path, entries=[_entry(local_working_clone=str(clone))])

    result = _run_checker(tmp_path, registry)

    assert result.returncode == 0
    assert "WARN" in result.stderr


@pytest.mark.parametrize("kind", ["directory", "missing", "symlink"])
def test_raw_root_availability_uses_metadata_only(tmp_path, kind):
    parent = tmp_path / "raw-parent"
    parent.mkdir()
    root = parent / "raw root with spaces"
    if kind == "directory":
        root.mkdir()
        (root / "unreadable-sentinel").write_text("never read\n", encoding="utf-8")
    elif kind == "symlink":
        target = tmp_path / "real-raw"
        target.mkdir()
        root.symlink_to(target, target_is_directory=True)
    registry = _write_registry(
        tmp_path,
        entries=[_entry(raw_roots=[str(root)], raw_source_status="mounted")],
    )

    result = _run_checker(tmp_path, registry)

    assert result.returncode == (0 if kind == "directory" else 1)
    assert "never read" not in result.stdout + result.stderr


def test_public_wiki_raw_root_is_a_firewall_failure(tmp_path):
    registry = _write_registry(
        tmp_path,
        entries=[
            _entry(
                raw_roots=[str(REPO_ROOT.parent / "llm-wiki")],
                raw_source_status="mounted",
            )
        ],
    )

    result = _run_checker(tmp_path, registry)

    assert result.returncode == 1
    assert "firewall" in result.stderr.lower()


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
    result = _run_checker(tmp_path, registry)
    assert result.returncode == 0
