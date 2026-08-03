"""Tests for scripts/tmux/tmux-autosave.sh (workspace-hub#3784).

The defect this fixes: tmux-continuum drives its autosave from `status-right`,
which tmux only evaluates for an ATTACHED client. A detached session — the
exact case persistence exists for — silently stops being saved. Measured on
ace-linux-1: last save was 75.8 h stale against a declared 15-minute interval,
with zero attached clients.

The wrapper is invoked by a systemd user timer so saving no longer depends on
anyone looking at the session.

The load-bearing design decision, and what most of these tests pin: the wrapper
delegates to continuum_save.sh and MUST NOT call resurrect's save.sh directly.
An earlier draft of the plan proposed guarding on a "restore in progress"
marker; adversarial review refuted it — no such durable marker exists
(resurrect's restore.sh uses a process-local shell variable). continuum_save.sh
already carries the protections that matter:

    acquire_lock                     PID-keyed auto-expiring mkdir lock,
                                     commented "otherwise we can get
                                     corrupted saved state"
    enough_time_since_last_run_passed  interval self-throttle
    set_last_save_timestamp          keeps @continuum-save-last-timestamp
                                     coherent — the very signal the defect
                                     was measured from

TDD: written before scripts/tmux/tmux-autosave.sh exists; expected to FAIL.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER = REPO_ROOT / "scripts" / "tmux" / "tmux-autosave.sh"


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def env_dir(tmp_path: Path) -> Path:
    """A fake HOME with a stub tmux and (optionally) the continuum plugin."""
    (tmp_path / "bin").mkdir()
    return tmp_path


def install_tmux(env_dir: Path, *, server_running: bool = True) -> None:
    """Stub tmux. `has-session` decides whether a server appears to exist."""
    stub = env_dir / "bin" / "tmux"
    rc = 0 if server_running else 1
    stub.write_text(
        "#!/usr/bin/env bash\n"
        'printf "%s\\n" "$*" >> "$(dirname "$0")/tmux_calls"\n'
        'if [[ "$1" == "has-session" || "$1" == "list-sessions" ]]; then\n'
        f"  exit {rc}\n"
        "fi\n"
        "exit 0\n"
    )
    stub.chmod(0o755)


def install_continuum(env_dir: Path) -> Path:
    """The plugin script the wrapper is required to delegate to."""
    d = env_dir / ".tmux" / "plugins" / "tmux-continuum" / "scripts"
    d.mkdir(parents=True)
    script = d / "continuum_save.sh"
    script.write_text(
        "#!/usr/bin/env bash\n"
        f'printf "called\\n" >> "{env_dir}/continuum_calls"\n'
        "exit 0\n"
    )
    script.chmod(0o755)
    return script


def install_resurrect(env_dir: Path) -> Path:
    """resurrect's raw save.sh — present, but must NOT be called directly."""
    d = env_dir / ".tmux" / "plugins" / "tmux-resurrect" / "scripts"
    d.mkdir(parents=True)
    script = d / "save.sh"
    script.write_text(
        "#!/usr/bin/env bash\n"
        f'printf "called\\n" >> "{env_dir}/resurrect_calls"\n'
        "exit 0\n"
    )
    script.chmod(0o755)
    return script


def run_wrapper(env_dir: Path, *, isolate_path: bool = False
                ) -> subprocess.CompletedProcess:
    """Run the wrapper against a fake HOME.

    `isolate_path` drops the system directories from PATH. It is required for
    the "no tmux on this machine" case: without it the wrapper finds the REAL
    /usr/bin/tmux and probes this host's REAL server, so the test passes or
    fails according to whether the developer happens to have tmux running. An
    earlier draft did exactly that and reported a false failure against a
    correct wrapper.
    """
    path = str(env_dir / "bin") if isolate_path else f"{env_dir / 'bin'}:/usr/bin:/bin"
    # Absolute interpreter: PATH here governs only the WRAPPER's own lookups
    # (its `command -v tmux`), never our ability to start a shell.
    bash = shutil.which("bash") or "/bin/bash"
    return subprocess.run(
        [bash, str(WRAPPER)],
        env={"PATH": path, "HOME": str(env_dir)},
        capture_output=True,
        text=True,
        timeout=30,
    )


def called(env_dir: Path, name: str) -> int:
    f = env_dir / f"{name}_calls"
    return len(f.read_text().splitlines()) if f.exists() else 0


# ── Fail-soft preconditions ───────────────────────────────────────────────
#
# The wrapper runs on a timer on every machine, including ones with no tmux
# and no plugins. Each absent precondition is a normal resting state, not an
# error — a unit that fails noisily every 15 minutes trains people to ignore it.


def test_autosave_noop_without_tmux(env_dir: Path) -> None:
    install_continuum(env_dir)
    result = run_wrapper(env_dir, isolate_path=True)
    assert result.returncode == 0
    assert called(env_dir, "continuum") == 0


def test_autosave_noop_without_server(env_dir: Path) -> None:
    install_tmux(env_dir, server_running=False)
    install_continuum(env_dir)
    result = run_wrapper(env_dir)
    assert result.returncode == 0
    assert called(env_dir, "continuum") == 0


def test_autosave_noop_without_plugin(env_dir: Path) -> None:
    install_tmux(env_dir)
    result = run_wrapper(env_dir)
    assert result.returncode == 0, "an unplugged box must not fail the unit"


def test_autosave_is_quiet_when_idle(env_dir: Path) -> None:
    """A timer that chatters every 15 minutes gets muted, then ignored."""
    install_tmux(env_dir, server_running=False)
    install_continuum(env_dir)
    result = run_wrapper(env_dir)
    assert result.stdout == "", f"unexpected stdout: {result.stdout!r}"
    assert result.stderr == "", f"unexpected stderr: {result.stderr!r}"


# ── The core delegation contract ──────────────────────────────────────────


def test_autosave_invokes_continuum_when_ready(env_dir: Path) -> None:
    install_tmux(env_dir)
    install_continuum(env_dir)
    result = run_wrapper(env_dir)
    assert result.returncode == 0
    assert called(env_dir, "continuum") == 1


def test_autosave_delegates_to_continuum_not_resurrect(env_dir: Path) -> None:
    """The whole design in one assertion.

    Calling resurrect's save.sh directly would bypass continuum's lock, its
    interval throttle, and its timestamp bookkeeping — and two savers writing
    one state file is the corruption continuum's lock exists to prevent.
    """
    install_tmux(env_dir)
    install_continuum(env_dir)
    install_resurrect(env_dir)

    run_wrapper(env_dir)

    assert called(env_dir, "continuum") == 1, "must delegate to continuum_save.sh"
    assert called(env_dir, "resurrect") == 0, (
        "must NOT call resurrect's save.sh directly — that bypasses the "
        "PID-keyed lock and the interval throttle"
    )


def test_autosave_does_not_reference_resurrect_save_directly() -> None:
    """Structural backstop for the assertion above, comments excluded."""
    code = "\n".join(
        line for line in WRAPPER.read_text().splitlines()
        if not line.lstrip().startswith("#")
    )
    assert "tmux-resurrect/scripts/save.sh" not in code, (
        "wrapper must reach resurrect only through continuum_save.sh"
    )
