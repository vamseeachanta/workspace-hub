"""Tests for the Mexico CNH source-watch timer mutator."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MUTATOR = REPO_ROOT / "scripts" / "install" / "disable-cnh-source-watch-timer.sh"
REGISTRY = REPO_ROOT / "config" / "scheduled-tasks" / "mutation-surfaces.yaml"
UNIT = "claude-routine-mx-720-cnh-source-watch.timer"


def install_systemctl(home: Path, *, enabled: str = "enabled", active: str = "active") -> None:
    bin_dir = home / "bin"
    bin_dir.mkdir()
    state = home / "state"
    state.mkdir()
    (state / "enabled").write_text(enabled)
    (state / "active").write_text(active)
    stub = bin_dir / "systemctl"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        "state_dir=\"${HOME}/state\"\n"
        "printf '%s\\n' \"$*\" >> \"${state_dir}/systemctl.calls\"\n"
        "if [ \"$1\" != \"--user\" ]; then exit 20; fi\n"
        "shift\n"
        "case \"$1\" in\n"
        "  show) printf 'Id=%s\\nActiveState=%s\\n' \"$2\" \"$(cat \"${state_dir}/active\")\" ;;\n"
        "  status) printf '%s status\\n' \"$2\" ;;\n"
        "  is-enabled) cat \"${state_dir}/enabled\" ;;\n"
        "  is-active) cat \"${state_dir}/active\" ;;\n"
        "  list-timers) printf '%s listed\\n' \"$2\" ;;\n"
        "  disable) [ \"$2\" = \"--now\" ] || exit 21; echo disabled > \"${state_dir}/enabled\"; echo inactive > \"${state_dir}/active\" ;;\n"
        "  enable) [ \"$2\" = \"--now\" ] || exit 22; echo enabled > \"${state_dir}/enabled\"; echo active > \"${state_dir}/active\" ;;\n"
        "  *) exit 23 ;;\n"
        "esac\n"
    )
    stub.chmod(0o755)


def run_mutator(home: Path, *args: str) -> subprocess.CompletedProcess[str]:
    bash = shutil.which("bash") or "/bin/bash"
    env = os.environ.copy()
    env.update({
        "PATH": f"{home / 'bin'}:/usr/bin:/bin",
        "HOME": str(home),
        "XDG_STATE_HOME": str(home / "xdg-state"),
    })
    return subprocess.run(
        [bash, str(MUTATOR), *args],
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )


def calls(home: Path) -> list[str]:
    path = home / "state" / "systemctl.calls"
    return path.read_text().splitlines() if path.exists() else []


def test_check_mode_captures_baseline_without_disabling(tmp_path: Path) -> None:
    install_systemctl(tmp_path)
    result = run_mutator(tmp_path, "--check")
    assert result.returncode == 0, result.stderr
    joined = "\n".join(calls(tmp_path))
    assert f"show {UNIT}" in joined
    assert f"disable --now {UNIT}" not in joined
    assert "rollback" in result.stdout
    assert list((tmp_path / "xdg-state" / "workspace-hub" / "scheduler-mutations").glob("*.baseline"))


def test_apply_disables_exact_timer_and_verifies_state(tmp_path: Path) -> None:
    install_systemctl(tmp_path)
    result = run_mutator(tmp_path, "--apply")
    assert result.returncode == 0, result.stderr
    joined = "\n".join(calls(tmp_path))
    assert f"disable --now {UNIT}" in joined
    assert "daemon-reload" not in joined
    assert "rm " not in joined
    assert (tmp_path / "state" / "enabled").read_text().strip() == "disabled"
    assert (tmp_path / "state" / "active").read_text().strip() == "inactive"
    assert "rollback: systemctl --user enable --now" in result.stdout


def test_registry_declares_cnh_timer_mutator() -> None:
    text = REGISTRY.read_text()
    idx = text.find("scripts/install/disable-cnh-source-watch-timer.sh")
    assert idx != -1
    block = text[idx:idx + 1600]
    assert "local-user-systemd-claude-routine-mx-720-cnh-source-watch" in block
    assert "systemd-user-enable-disable" in block
    assert "execution_host_binding: physical-local" in block
    assert "disposition_group: cnh-source-watch-disable" in block
