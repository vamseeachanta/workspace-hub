"""Issue #3513: simulated Windows refusal preserves isolated runtime fixtures.

This covers shell detection and copy/failure emulation, not Windows objects.
Plan-lite:
- Scope: test-only coverage of existing refusal behavior in disposable roots.
- Acceptance: all 8 refusal cases and all 20 combined installer cases pass;
  repeated refusal preserves instruction and backup bytes, exact directory
  entries, and empty staging directories.
- Limitation: simulated Windows detection and link behavior on Linux do not
  establish actual Windows object behavior.

Expected bytes and directory entries below are handwritten fixture contracts.
Numeric basis: parents[2] ascends tests/agents to the repository; shell status
0 means success and 1 means failure; ln -s takes SOURCE and DEST as arguments
2 and 3. Mode 0o755 is user rwx plus group/other r-x. The 30-second subprocess
bound follows tests/enforcement/test_soul_auto_load.py::install.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_CASES = [
    (".codex", "AGENTS.md", "codex/AGENTS.runtime.md"),
    (".hermes", "SOUL.md", "hermes/SOUL.runtime.md"),
]


@pytest.fixture(params=RUNTIME_CASES, ids=["codex", "hermes"])
def isolated_installation(tmp_path, request):
    repo = tmp_path / "repo"
    user_root = tmp_path / "user"
    shims = tmp_path / "bin"
    temp = tmp_path / "temp"
    for directory in (user_root, shims, temp):
        directory.mkdir()
    for relative in (
        "scripts/agents/install-soul-runtime.sh",
        "scripts/setup/lib/detect-os.sh",
    ):
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    provider, filename, source_relative = request.param
    source = repo / "config/agents" / source_relative
    source.parent.mkdir(parents=True)
    source.write_bytes(b"Synthetic replacement runtime\n")
    destination_dir = user_root / provider
    destination_dir.mkdir()
    backup_name = filename + ".pre-install-backup.fixture"
    (destination_dir / backup_name).write_bytes(b"Existing backup\x00\xff\n")

    # No inherited HOME, Git bindings, shell startup files or provider settings.
    bash = shutil.which("bash")
    assert bash, "Bash is required for installer failure coverage"
    env = {
        "HOME": str(user_root),
        "PATH": os.pathsep.join((str(shims), str(Path(bash).parent), os.defpath)),
        "TMPDIR": str(temp),
        "TMP": str(temp),
        "TEMP": str(temp),
        "XDG_CONFIG_HOME": str(user_root / "config"),
        "XDG_CACHE_HOME": str(temp),
        "PYTHONDONTWRITEBYTECODE": "1",
        "OS_TRACE": str(tmp_path / "os-trace"),
        "LN_TRACE": str(tmp_path / "ln-trace"),
    }
    scripts = {
        "uname": """#!/usr/bin/env bash
set -eu
[[ "$*" == "-s" ]]
printf 'windows-detection\n' >> "$OS_TRACE"
printf 'MINGW_SYNTHETIC\n'
""",
        "ln": """#!/usr/bin/env bash
set -eu
[[ "$1" == "-s" ]]
case "$LINK_BEHAVIOR" in
    copy)
        cp -- "$2" "$3"
        [[ -f "$3" && ! -L "$3" ]]
        printf 'copy %s\n' "$MSYS" >> "$LN_TRACE"
        exit 0
        ;;
    fail)
        [[ ! -e "$3" && ! -L "$3" ]]
        printf 'fail %s\n' "$MSYS" >> "$LN_TRACE"
        printf 'Synthetic link creation failure\n' >&2
        exit 1
        ;;
esac
exit 1
""",
    }
    for name, content in scripts.items():
        shim = shims / name
        shim.write_text(content, encoding="utf-8")
        shim.chmod(0o755)
    return repo, user_root, provider, filename, backup_name, bash, env


def assert_repeated_refusal(installation, behavior, *, existing):
    repo, user_root, provider, filename, backup_name, bash, child_env = installation
    destination = user_root / provider / filename
    if existing:
        destination.write_bytes(b"Original instructions\x00\xff\n")
    expected_entries = {provider, f"{provider}/{backup_name}"}
    if existing:
        expected_entries.add(f"{provider}/{filename}")
    env = dict(child_env, LINK_BEHAVIOR=behavior)

    # Issue #3513 requires the first failure and a repeat against the same tree.
    for expected_os_trace, expected_ln_trace in (
        ("windows-detection\n", f"{behavior} winsymlinks:nativestrict\n"),
        (
            "windows-detection\nwindows-detection\n",
            f"{behavior} winsymlinks:nativestrict\n"
            f"{behavior} winsymlinks:nativestrict\n",
        ),
    ):
        result = subprocess.run(
            [bash, str(repo / "scripts/agents/install-soul-runtime.sh")],
            cwd=user_root,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        output = result.stdout + result.stderr
        assert result.returncode != 0, output
        assert "native symlink not created; existing runtime preserved" in output
        assert not any(line.startswith("LINK ") for line in output.splitlines())
        assert not any(line.startswith("BACKUP ") for line in output.splitlines())
        assert Path(env["OS_TRACE"]).read_text() == expected_os_trace
        assert Path(env["LN_TRACE"]).read_text() == expected_ln_trace
        if behavior == "fail":
            assert "Synthetic link creation failure" in output
        if existing:
            assert destination.is_file() and not destination.is_symlink()
            assert destination.read_bytes() == b"Original instructions\x00\xff\n"
        else:
            assert not destination.exists() and not destination.is_symlink()
        backup = user_root / provider / backup_name
        assert backup.is_file() and not backup.is_symlink()
        assert backup.read_bytes() == b"Existing backup\x00\xff\n"
        assert {p.relative_to(user_root).as_posix() for p in user_root.rglob("*")} == expected_entries
        assert not list(user_root.rglob(".soul-link.*"))
        assert not list(Path(env["TMPDIR"]).iterdir())
        source = repo / "config/agents" / dict(
            (case_provider, runtime) for case_provider, _, runtime in RUNTIME_CASES
        )[provider]
        assert source.read_bytes() == b"Synthetic replacement runtime\n"


def test_copy_emulation_preserves_existing_runtime(isolated_installation):
    assert_repeated_refusal(isolated_installation, "copy", existing=True)


def test_link_failure_repeat_does_not_accumulate_backups(isolated_installation):
    assert_repeated_refusal(isolated_installation, "fail", existing=True)


@pytest.mark.parametrize("behavior", ["copy", "fail"])
def test_failed_install_leaves_absent_destination(isolated_installation, behavior):
    assert_repeated_refusal(isolated_installation, behavior, existing=False)
