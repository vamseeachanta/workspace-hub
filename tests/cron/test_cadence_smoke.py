"""Standalone smoke contract; helper examples cite test_cadence_common.py."""

import shutil
import stat
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "scripts/cron/lib"
SMOKE = LIB / "smoke-test.sh"
PASS_OUTPUT = "cadence helpers: PASS\n"


def _snapshot(root):
    """Record names, contents, modes and modification times, including directories."""
    return {
        str(path.relative_to(root)): (
            path.lstat().st_mode,
            path.lstat().st_mtime_ns,
            path.read_bytes() if path.is_file() else None,
        )
        for path in root.rglob("*")
    }


@pytest.fixture
def isolated(tmp_path):
    """No repository or caller configuration; expose only helper dependencies."""
    cwd = tmp_path / "unrelated directory"
    cwd.mkdir()
    home = tmp_path / "configuration"
    home.mkdir()
    temp = tmp_path / "temporary"
    temp.mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for command in ("bash", "dirname", "awk", "cat"):
        executable = shutil.which(command)
        assert executable, f"Required command unavailable: {command}"
        (bin_dir / command).symlink_to(executable)
    # Any attempt to consult the clock, Git, the network or cadence wrappers
    # leaves evidence even if a helper catches the failing command's exit code.
    forbidden = bin_dir / "forbidden"
    forbidden.write_text(
        '#!/usr/bin/env bash\n'
        'printf "unexpected external command\\n" > "$TMPDIR/unexpected"\n'
        'exit 1\n'
    )
    forbidden.chmod(
        forbidden.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    )
    for command in ("date", "git", "curl", "wget", "crontab"):
        (bin_dir / command).symlink_to(forbidden)
    env = {
        "PATH": str(bin_dir),
        "HOME": str(home),
        "TMPDIR": str(temp),
        "TZ": "Pacific/Honolulu",
        "LC_ALL": "C",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    return tmp_path, cwd, env


def _run(script, isolated):
    root, cwd, env = isolated
    before = _snapshot(root)
    result = subprocess.run(
        ["bash", str(script)], cwd=cwd, env=env,
        capture_output=True, text=True, check=False,
        timeout=10,  # Existing subprocess budget: test_cadence_common.py.
    )
    assert _snapshot(root) == before, "Smoke changed the scratch tree"
    return result


def _copy_library(root):
    """Keep the script and real helper together, outside any configured repository."""
    target = root / "copied library"
    target.mkdir()
    shutil.copyfile(SMOKE, target / SMOKE.name)
    shutil.copyfile(LIB / "cadence-common.sh", target / "cadence-common.sh")
    return target


@pytest.mark.parametrize("copied", [False, True], ids=["checkout", "standalone"])
def test_smoke_is_deterministic_and_read_only(isolated, copied):
    root, _, _ = isolated
    script = _copy_library(root) / SMOKE.name if copied else SMOKE
    first = _run(script, isolated)
    second = _run(script, isolated)
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout == PASS_OUTPUT
    assert first.stderr == second.stderr == ""


# The boundary comments in cadence-common.sh require strict > comparisons:
# equality with warn is GREEN; equality with block is YELLOW. The header
# contract comes from test_emit_report_header_format in test_cadence_common.py.
# For the quarterly defect, independent arithmetic gives (4 - 1) // 3 + 1 = 2.
@pytest.mark.parametrize("original,defective,label", [
    ("$value > $warn", "$value >= $warn", "warn equality"),
    ("$value > $block", "$value >= $block", "block equality"),
    ("**Status:**", "**State:**", "header"),
    ("echo RED", "echo GREEN", "above block"),
    ("date +%Y-W%V", "printf 'broken\\n'", "weekly"),
    ("date +%Y-%m", "printf 'broken\\n'", "monthly"),
    ("/ 3 + 1", "/ 3 + 2", "quarterly"),
])
def test_smoke_rejects_defective_copied_helper(isolated, original, defective, label):
    root, _, _ = isolated
    target = _copy_library(root)
    helper = target / "cadence-common.sh"
    source = helper.read_text()
    assert source.count(original) == 1
    helper.write_text(source.replace(original, defective))
    result = _run(target / SMOKE.name, isolated)
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.startswith(f"cadence helpers: FAIL ({label})")
