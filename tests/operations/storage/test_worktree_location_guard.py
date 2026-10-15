"""Filesystem probes are fixtures; no special mounted volume is required."""
import os
from pathlib import Path
import re
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[3]
GUARD = ROOT / "scripts/operations/storage/worktree_location_guard.sh"


def filesystem_env(tmp_path, monkeypatch):
    tools = tmp_path / "tools"
    tools.mkdir()
    scripts = {
        "stat": '[[ ${STAT_FAIL:-0} == 0 ]] || exit 1\n'
                'if [[ -n ${EXPECTED_ANCESTOR:-} && ${!#} != "$EXPECTED_ANCESTOR" ]]; then exit 1; fi\n'
                'printf "%s\\n" "${FS_TYPE-ext2/ext3}"\n',
        "findmnt": '[[ ${FINDMNT_FAIL:-0} == 0 ]] || exit 1\n'
                   'printf "%s\\n" "${FINDMNT_TYPE-${FS_TYPE-ext2/ext3}}"\n',
        "df": '[[ ${DF_FAIL:-0} == 0 ]] || exit 1\n'
              'printf "Filesystem 1024-blocks Used Available Capacity Mounted on\\n"\n'
              'printf "fixture 209715200 0 %s 0%% .\\n" "${FREE_KB:-62914560}"\n',
    }
    for name, body in scripts.items():
        path = tools / name
        path.write_text("#!/usr/bin/env bash\n" + body)
        path.chmod(0o755)
    monkeypatch.setenv("PATH", str(tools) + os.pathsep + os.environ["PATH"])
    monkeypatch.delenv("JOB_CHECKOUT_MIN_FREE_GB", raising=False)
    return tools


def run_guard(dest, *args):
    return subprocess.run(["bash", str(GUARD), "--dest", str(dest), *args],
                          capture_output=True, text=True)


def snapshot(root):
    return sorted((str(p.relative_to(root)), p.is_dir(),
                   p.read_bytes() if p.is_file() else b"") for p in root.rglob("*"))


@pytest.mark.parametrize("kind", ["fuseblk", "fuse", "fuse.sshfs", "ntfs", "ntfs3", "ntfs-3g"])
def test_slow_types_refuse_without_changes(tmp_path, monkeypatch, kind):
    filesystem_env(tmp_path, monkeypatch)
    monkeypatch.setenv("FS_TYPE", kind)
    dest = tmp_path / "new" / "checkout"
    before = snapshot(tmp_path)
    result = run_guard(dest)
    assert result.returncode == 3, result.stderr
    assert all(word in result.stderr for word in (str(dest), kind, "host SSD", "no fallback"))
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("kind", ["ext2/ext3", "xfs", "btrfs", "tmpfs", "overlayfs"])
def test_other_types_pass(tmp_path, monkeypatch, kind):
    filesystem_env(tmp_path, monkeypatch)
    monkeypatch.setenv("FS_TYPE", kind)
    result = run_guard(tmp_path / "checkout")
    assert result.returncode == 0, result.stderr
    assert f"worktree_location=ok fs={kind}" in result.stdout
    assert "free_gb=60.0" in result.stdout


def test_nearest_existing_ancestor(tmp_path, monkeypatch):
    filesystem_env(tmp_path, monkeypatch)
    monkeypatch.setenv("EXPECTED_ANCESTOR", str(tmp_path.resolve()))
    monkeypatch.setenv("FINDMNT_FAIL", "1")
    monkeypatch.setenv("FS_TYPE", "ntfs")
    assert run_guard(tmp_path / "absent" / "nested").returncode == 3


def test_symlink_ancestor_is_resolved(tmp_path, monkeypatch):
    filesystem_env(tmp_path, monkeypatch)
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    monkeypatch.setenv("EXPECTED_ANCESTOR", str(real.resolve()))
    monkeypatch.setenv("FINDMNT_FAIL", "1")
    result = run_guard(link / "missing")
    assert result.returncode == 0, result.stderr


def test_findmnt_fallback(tmp_path, monkeypatch):
    filesystem_env(tmp_path, monkeypatch)
    monkeypatch.setenv("STAT_FAIL", "1")
    monkeypatch.setenv("FINDMNT_TYPE", "ntfs3")
    result = run_guard(tmp_path / "checkout")
    assert result.returncode == 3
    assert "ntfs3" in result.stderr


@pytest.mark.parametrize("kind", ["", "unknown", "UNKNOWN", " "])
def test_unknown_type_refused(tmp_path, monkeypatch, kind):
    filesystem_env(tmp_path, monkeypatch)
    monkeypatch.setenv("FS_TYPE", kind)
    monkeypatch.setenv("STAT_FAIL", "1")
    monkeypatch.setenv("FINDMNT_FAIL", "1")
    result = run_guard(tmp_path / "checkout")
    assert result.returncode == 3
    assert "filesystem type could not be read" in result.stderr


def test_floor_and_defaults(tmp_path, monkeypatch):
    filesystem_env(tmp_path, monkeypatch)
    dest = tmp_path / "checkout"
    monkeypatch.setenv("FREE_KB", str(20 * 1024 * 1024))
    result = run_guard(dest, "--min-free-gb", "50")
    assert result.returncode == 4
    assert all(x in result.stderr for x in ("20.0", "50", str(dest), "mount"))
    monkeypatch.setenv("JOB_CHECKOUT_MIN_FREE_GB", "10")
    assert run_guard(dest).returncode == 0
    assert run_guard(dest, "--min-free-gb", "50").returncode == 4
    monkeypatch.setenv("FREE_KB", str(60 * 1024 * 1024))
    assert run_guard(dest).returncode == 0
    monkeypatch.setenv("FREE_KB", str(50 * 1024 * 1024))
    assert run_guard(dest, "--min-free-gb", "50").returncode == 0
    monkeypatch.setenv("FREE_KB", str(50 * 1024 * 1024 - 1))
    assert run_guard(dest, "--min-free-gb", "50").returncode == 4


@pytest.mark.parametrize("value", ["broken", "", "-2"])
def test_unreadable_free_space_refused(tmp_path, monkeypatch, value):
    filesystem_env(tmp_path, monkeypatch)
    monkeypatch.setenv("FREE_KB", value)
    if not value:
        monkeypatch.setenv("DF_FAIL", "1")
    assert run_guard(tmp_path / "checkout").returncode == 4


@pytest.mark.parametrize("args", [[], ["--dest"], ["--bogus"], ["--dest", ""],
                                    ["--dest", ".", "--min-free-gb", "bad"],
                                    ["--dest", ".", "--min-free-gb", "-1"]])
def test_usage(args):
    result = subprocess.run(["bash", str(GUARD), *args], capture_output=True, text=True)
    assert result.returncode == 2


def test_guard_is_read_only():
    source = GUARD.read_text()
    code = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("#"))
    assert not re.search(r"\b(?:mkdir|sudo)\b|\bln\s+-s|\b(?:mount|rm|cp)\s", code)
    assert not re.search(r"(?:fallback|alternate|secondary)_?(?:dest|path|root)\s*=", code)


@pytest.mark.parametrize("kind", ["", "unknown", "UNKNOWN", " "])
def test_invalid_probe_values_refused(tmp_path, monkeypatch, kind):
    filesystem_env(tmp_path, monkeypatch)
    monkeypatch.setenv("FS_TYPE", kind)
    monkeypatch.setenv("FINDMNT_TYPE", kind)
    result = run_guard(tmp_path / "checkout")
    assert result.returncode == 3
    assert "filesystem type could not be read" in result.stderr


def test_findmnt_fallback_safe(tmp_path, monkeypatch):
    filesystem_env(tmp_path, monkeypatch)
    monkeypatch.setenv("STAT_FAIL", "1")
    monkeypatch.setenv("FINDMNT_TYPE", "xfs")
    result = run_guard(tmp_path / "checkout")
    assert result.returncode == 0
    assert "fs=xfs" in result.stdout
