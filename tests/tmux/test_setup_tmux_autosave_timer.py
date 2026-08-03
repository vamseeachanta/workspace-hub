"""Tests for scripts/install/setup-tmux-autosave-timer.sh (workspace-hub#3784).

This installer writes and enables a systemd **user** timer, which makes it a
scheduler mutation surface under .claude/rules/scheduler-mutation-safety.md.
It is deliberately split out of scripts/setup/deploy-tmux.sh so that the
general onboarding script does not itself become governed.

Two properties carry most of the risk and get the most tests here:

* **The unit content.** `Persistent=` must be absent and `OnBootSec` must be
  at least 5 minutes. At a fresh tmux server start
  `@continuum-save-last-timestamp` defaults to 0, so an early tick would fire
  a save straight over an in-flight continuum restore and repoint the `last`
  state file at a half-rebuilt session tree. The wrapper cannot defend against
  this — no durable restore-in-progress marker exists — so the schedule is the
  only guard.

* **Never clobber without a backup.** An existing unit is backed up before it
  is overwritten, and a failed post-write verification rolls back to it.

TDD: written before the installer exists; expected to FAIL first.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = REPO_ROOT / "scripts" / "install" / "setup-tmux-autosave-timer.sh"
SERVICE_SRC = REPO_ROOT / "config" / "tmux" / "tmux-autosave.service"
TIMER_SRC = REPO_ROOT / "config" / "tmux" / "tmux-autosave.timer"
REGISTRY = REPO_ROOT / "config" / "scheduled-tasks" / "mutation-surfaces.yaml"

UNIT_BASE = "tmux-autosave"


# ── Harness ───────────────────────────────────────────────────────────────


@pytest.fixture
def fake_home(tmp_path: Path) -> Path:
    (tmp_path / "bin").mkdir()
    return tmp_path


def install_systemctl(home: Path, *, available: bool = True,
                      fail_on: str | None = None) -> None:
    """Stub `systemctl` recording every invocation.

    `available=False` emulates a box with no systemd --user (the installer must
    degrade to a warning, never a hard failure — it is called from onboarding).
    """
    stub = home / "bin" / "systemctl"
    if not available:
        if stub.exists():
            stub.unlink()
        return
    fail_clause = ""
    if fail_on:
        fail_clause = (
            f'if [[ "$*" == *"{fail_on}"* ]]; then\n'
            '  echo "stub: forced failure" >&2\n'
            "  exit 1\n"
            "fi\n"
        )
    stub.write_text(
        "#!/usr/bin/env bash\n"
        'printf "%s\\n" "$*" >> "$(dirname "$0")/systemctl_calls"\n'
        f"{fail_clause}"
        "exit 0\n"
    )
    stub.chmod(0o755)


def run_installer(home: Path) -> subprocess.CompletedProcess:
    bash = shutil.which("bash") or "/bin/bash"
    return subprocess.run(
        [bash, str(INSTALLER)],
        env={
            "PATH": f"{home / 'bin'}:/usr/bin:/bin",
            "HOME": str(home),
        },
        capture_output=True,
        text=True,
        timeout=60,
    )


def unit_dir(home: Path) -> Path:
    return home / ".config" / "systemd" / "user"


def systemctl_calls(home: Path) -> list:
    f = home / "bin" / "systemctl_calls"
    return f.read_text().splitlines() if f.exists() else []


# ── Unit content — the boot-race guard ────────────────────────────────────


def test_timer_source_has_no_persistent() -> None:
    """`Persistent=` must not appear.

    It is also inert on a monotonic timer — systemd.timer(5) applies it to
    OnCalendar= only — so its presence would additionally be misleading about
    where the boot-race protection actually comes from.
    """
    assert "Persistent=" not in TIMER_SRC.read_text()


def test_timer_source_delays_first_boot_tick() -> None:
    text = TIMER_SRC.read_text()
    m = re.search(r"OnBootSec=(\d+)min", text)
    assert m, f"expected an OnBootSec=<N>min line, got:\n{text}"
    assert int(m.group(1)) >= 5, "first tick must clear an in-flight restore"


def test_timer_source_repeats_on_interval() -> None:
    assert re.search(r"OnUnitActiveSec=\d+min", TIMER_SRC.read_text())


def test_service_source_is_oneshot_with_execstart() -> None:
    text = SERVICE_SRC.read_text()
    assert "Type=oneshot" in text
    assert "ExecStart=" in text
    assert "tmux-autosave.sh" in text


# ── Install behaviour ─────────────────────────────────────────────────────


def test_installer_writes_both_units(fake_home: Path) -> None:
    install_systemctl(fake_home)
    result = run_installer(fake_home)
    assert result.returncode == 0, result.stderr
    assert (unit_dir(fake_home) / f"{UNIT_BASE}.service").exists()
    assert (unit_dir(fake_home) / f"{UNIT_BASE}.timer").exists()


def test_installer_enables_the_timer_not_the_service(fake_home: Path) -> None:
    """A oneshot service must not be enabled — the timer is what schedules it."""
    install_systemctl(fake_home)
    run_installer(fake_home)
    joined = "\n".join(systemctl_calls(fake_home))
    assert "enable" in joined and f"{UNIT_BASE}.timer" in joined
    assert not re.search(rf"enable.*{UNIT_BASE}\.service", joined)


def test_installer_uses_user_scope_only(fake_home: Path) -> None:
    """physical-local, user scope. It must never touch system-level systemd."""
    install_systemctl(fake_home)
    run_installer(fake_home)
    for call in systemctl_calls(fake_home):
        assert "--user" in call, f"non-user systemctl call: {call!r}"
        assert "--system" not in call, f"system-scope call: {call!r}"


def test_installer_is_idempotent(fake_home: Path) -> None:
    install_systemctl(fake_home)
    run_installer(fake_home)
    first = (unit_dir(fake_home) / f"{UNIT_BASE}.timer").read_text()
    result = run_installer(fake_home)
    assert result.returncode == 0
    assert (unit_dir(fake_home) / f"{UNIT_BASE}.timer").read_text() == first
    assert len(list(unit_dir(fake_home).glob(f"{UNIT_BASE}.timer"))) == 1


def test_installer_backs_up_an_existing_unit(fake_home: Path) -> None:
    """Never overwrite a hand-edited unit without keeping a copy."""
    install_systemctl(fake_home)
    unit_dir(fake_home).mkdir(parents=True, exist_ok=True)
    existing = unit_dir(fake_home) / f"{UNIT_BASE}.timer"
    existing.write_text("[Timer]\n# hand-edited by the operator\nOnBootSec=1min\n")

    run_installer(fake_home)

    backups = list(unit_dir(fake_home).glob(f"{UNIT_BASE}.timer.bak-*"))
    assert backups, "existing unit must be backed up before being replaced"
    assert "hand-edited by the operator" in backups[0].read_text()


def test_installer_degrades_without_systemd(fake_home: Path) -> None:
    """No systemd --user on this box — warn, do not fail onboarding."""
    install_systemctl(fake_home, available=False)
    result = run_installer(fake_home)
    assert result.returncode == 0, "must not fail a box without systemd"
    assert result.stdout.strip() or result.stderr.strip(), (
        "a silent skip is indistinguishable from success — say something"
    )


def test_installer_reports_failure_when_enable_fails(fake_home: Path) -> None:
    """A failed enable must be visible, not swallowed."""
    install_systemctl(fake_home, fail_on="enable")
    result = run_installer(fake_home)
    assert result.returncode != 0 or "fail" in (
        result.stdout + result.stderr
    ).lower()


# ── Registry governance ───────────────────────────────────────────────────


def test_installer_is_registered_as_a_mutation_surface() -> None:
    """.claude/rules/scheduler-mutation-safety.md requires registry inclusion."""
    assert "scripts/install/setup-tmux-autosave-timer.sh" in REGISTRY.read_text()


def test_registry_entry_declares_systemd_user_primitives() -> None:
    text = REGISTRY.read_text()
    idx = text.find("scripts/install/setup-tmux-autosave-timer.sh")
    assert idx != -1, "installer not registered"
    block = text[idx:idx + 2000]
    assert "systemd-user-unit-write" in block
    assert "systemd-user-enable-disable" in block
    assert "execution_host_binding: physical-local" in block
    assert "local-user-systemd-tmux-autosave" in block
