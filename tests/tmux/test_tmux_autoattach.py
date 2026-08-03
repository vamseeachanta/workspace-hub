"""Tests for config/tmux/autoattach.sh (workspace-hub#3784).

The guard decides whether an interactive SSH login is replaced by a tmux
session. It runs inside every login shell on the dispatch surface, so the
failure that matters is not "auto-attach did not happen" — it is auto-attach
happening on a path that must stay clean: BatchMode SSH, `ssh host '<cmd>'`,
scp, rsync. Those carry the fleet's dispatch traffic.

TDD: written before config/tmux/autoattach.sh exists; expected to FAIL first.

Fixture strategy mirrors tests/enforcement/test_check_no_conflict_markers.py —
each case builds a hermetic tmp_path with a stub `tmux` on PATH and invokes the
guard through `bash`, so nothing touches the developer's real shell or server.
The stub records its argv to a file; a subprocess cannot mutate our variables.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "config" / "tmux" / "autoattach.sh"


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def stub_tmux(tmp_path: Path) -> Path:
    """A `tmux` on PATH that records its argv and succeeds."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub = bin_dir / "tmux"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        'printf "%s\\n" "$*" >> "$(dirname "$0")/tmux_calls"\n'
        "exit 0\n"
    )
    stub.chmod(0o755)
    return bin_dir


def run_guard(
    bin_dir: Path,
    *,
    interactive: bool = True,
    env_overrides: dict | None = None,
    include_tmux: bool = True,
) -> subprocess.CompletedProcess:
    """Source the guard under a controlled shell and environment.

    `interactive` is emulated with `set -i`, because bash only sets the `i`
    flag in `$-` for a genuinely interactive shell and we cannot spawn one
    from pytest without a tty. The guard reads `$-`, so setting the flag
    exercises the real predicate.
    """
    env = {
        "PATH": f"{bin_dir}:/usr/bin:/bin" if include_tmux else "/usr/bin:/bin",
        "HOME": str(bin_dir.parent),
    }
    env.update(env_overrides or {})

    flag = "set -i; " if interactive else ""
    script = f"{flag}. {GUARD}\n"

    return subprocess.run(
        ["bash", "-c", script],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def tmux_invocations(bin_dir: Path) -> list:
    calls = bin_dir / "tmux_calls"
    if not calls.exists():
        return []
    return [ln for ln in calls.read_text().splitlines() if ln.strip()]


SSH_ENV = {"SSH_CONNECTION": "10.0.0.2 5555 10.0.0.1 22"}


# ── The path that should attach ───────────────────────────────────────────


def test_autoattach_fires_on_interactive_ssh(stub_tmux: Path) -> None:
    run_guard(stub_tmux, interactive=True, env_overrides=SSH_ENV)
    assert tmux_invocations(stub_tmux), "expected tmux to be invoked"


def test_autoattach_uses_attach_or_create(stub_tmux: Path) -> None:
    run_guard(stub_tmux, interactive=True, env_overrides=SSH_ENV)
    call = tmux_invocations(stub_tmux)[0]
    assert "new" in call and "-A" in call, f"expected attach-or-create, got: {call}"


def test_autoattach_defaults_session_to_main(stub_tmux: Path) -> None:
    """An unset WH_TMUX_SESSION must not pass an empty session name."""
    run_guard(stub_tmux, interactive=True, env_overrides=SSH_ENV)
    call = tmux_invocations(stub_tmux)[0]
    assert "-s main" in call, f"expected session 'main', got: {call}"


def test_autoattach_honours_session_override(stub_tmux: Path) -> None:
    run_guard(
        stub_tmux,
        interactive=True,
        env_overrides={**SSH_ENV, "WH_TMUX_SESSION": "custom"},
    )
    call = tmux_invocations(stub_tmux)[0]
    assert "-s custom" in call, f"expected session 'custom', got: {call}"


# ── The paths that must NOT attach ────────────────────────────────────────


def test_autoattach_skips_non_interactive(stub_tmux: Path) -> None:
    """BatchMode SSH and every scripted dispatch call land here."""
    run_guard(stub_tmux, interactive=False, env_overrides=SSH_ENV)
    assert tmux_invocations(stub_tmux) == []


def test_autoattach_skips_local_console(stub_tmux: Path) -> None:
    """No SSH_CONNECTION means a local login, not a remote session."""
    run_guard(stub_tmux, interactive=True)
    assert tmux_invocations(stub_tmux) == []


def test_autoattach_skips_when_already_in_tmux(stub_tmux: Path) -> None:
    run_guard(
        stub_tmux,
        interactive=True,
        env_overrides={**SSH_ENV, "TMUX": "/tmp/tmux-1000/default,123,0"},
    )
    assert tmux_invocations(stub_tmux) == []


def test_autoattach_skips_ssh_remote_command_shape(stub_tmux: Path) -> None:
    """`ssh host '<cmd>'`, scp and rsync are NON-INTERACTIVE with SSH_CONNECTION set.

    This is the real shape of those paths. sshd does NOT set
    SSH_ORIGINAL_COMMAND for them (see the separate ForceCommand test), so
    interactivity is the guard that actually protects file transfer here.
    """
    run_guard(stub_tmux, interactive=False, env_overrides=SSH_ENV)
    assert tmux_invocations(stub_tmux) == []


def test_autoattach_skips_forcecommand_shape(stub_tmux: Path) -> None:
    """Defence in depth only — sshd sets this just for ForceCommand/command=."""
    run_guard(
        stub_tmux,
        interactive=True,
        env_overrides={**SSH_ENV, "SSH_ORIGINAL_COMMAND": "rsync --server ."},
    )
    assert tmux_invocations(stub_tmux) == []


def test_autoattach_skips_with_escape_hatch(stub_tmux: Path) -> None:
    run_guard(
        stub_tmux,
        interactive=True,
        env_overrides={**SSH_ENV, "NO_TMUX_AUTOATTACH": "1"},
    )
    assert tmux_invocations(stub_tmux) == []


def test_autoattach_skips_when_tmux_absent(stub_tmux: Path) -> None:
    """A box without tmux must get a clean shell, not an error."""
    result = run_guard(
        stub_tmux, interactive=True, env_overrides=SSH_ENV, include_tmux=False
    )
    assert result.returncode == 0
    assert tmux_invocations(stub_tmux) == []


# ── Safety properties ─────────────────────────────────────────────────────


def test_autoattach_emits_nothing_when_non_interactive(stub_tmux: Path) -> None:
    """Any byte on stdout corrupts scp/sftp. Pin silence, not just non-firing."""
    result = run_guard(stub_tmux, interactive=False, env_overrides=SSH_ENV)
    assert result.stdout == "", f"stdout must be empty, got: {result.stdout!r}"
    assert result.stderr == "", f"stderr must be empty, got: {result.stderr!r}"


def test_autoattach_survives_tmux_failure(stub_tmux: Path) -> None:
    """A broken tmux must leave a working shell — never a lockout.

    This is why the guard does not use `exec`: with `exec`, a tmux that fails
    to start closes the connection outright and the operator cannot log in to
    repair it.
    """
    (stub_tmux / "tmux").write_text(
        "#!/usr/bin/env bash\n"
        'printf "%s\\n" "$*" >> "$(dirname "$0")/tmux_calls"\n'
        'echo "tmux: server start failed" >&2\n'
        "exit 1\n"
    )
    (stub_tmux / "tmux").chmod(0o755)

    result = run_guard(stub_tmux, interactive=True, env_overrides=SSH_ENV)

    assert tmux_invocations(stub_tmux), "tmux should have been attempted"
    assert result.returncode == 0, (
        "guard must return control to the shell when tmux fails, "
        f"got rc={result.returncode}"
    )


def test_autoattach_does_not_use_exec() -> None:
    """Structural guard on the lockout property above.

    `exec tmux ...` would replace the login shell, so a tmux failure ends the
    connection. The plan deliberately diverges from the originally-sketched
    `exec` form for this reason; pin it so the divergence is not undone.
    """
    assert "exec tmux" not in GUARD.read_text(), (
        "guard must not exec tmux — lockout risk"
    )
