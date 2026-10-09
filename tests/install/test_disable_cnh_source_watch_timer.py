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


def install_systemctl(
    home: Path,
    *,
    enabled: str = "enabled",
    active: str = "active",
    next_elapse: str = "1234567890",
    drift_on_second_show: bool = False,
    bad_disable: bool = False,
) -> None:
    bin_dir = home / "bin"
    bin_dir.mkdir()
    state = home / "state"
    state.mkdir()
    (state / "enabled").write_text(enabled)
    (state / "active").write_text(active)
    (state / "next_elapse").write_text(next_elapse)
    (state / "show_count").write_text("0")
    stub = bin_dir / "systemctl"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        "state_dir=\"${HOME}/state\"\n"
        f"drift_on_second_show={str(drift_on_second_show).lower()}\n"
        f"bad_disable={str(bad_disable).lower()}\n"
        "printf '%s\\n' \"$*\" >> \"${state_dir}/systemctl.calls\"\n"
        "if [ \"$1\" != \"--user\" ]; then exit 20; fi\n"
        "shift\n"
        "case \"$1\" in\n"
        "  show)\n"
        "    count=$(cat \"${state_dir}/show_count\")\n"
        "    count=$((count + 1))\n"
        "    echo \"$count\" > \"${state_dir}/show_count\"\n"
        "    if [ \"$drift_on_second_show\" = true ] && [ \"$count\" -ge 2 ]; then\n"
        "      echo 9876543210 > \"${state_dir}/next_elapse\"\n"
        "    fi\n"
        "    printf 'UnitFileState=%s\\nActiveState=%s\\nNextElapseUSecRealtime=%s\\n' \"$(cat \"${state_dir}/enabled\")\" \"$(cat \"${state_dir}/active\")\" \"$(cat \"${state_dir}/next_elapse\")\" ;;\n"
        "  status) printf '%s status\\n' \"$2\" ;;\n"
        "  is-enabled) cat \"${state_dir}/enabled\" ;;\n"
        "  is-active) cat \"${state_dir}/active\" ;;\n"
        "  list-timers) printf '%s listed\\n' \"$2\" ;;\n"
        "  disable) [ \"$2\" = \"--now\" ] || exit 21; echo disabled > \"${state_dir}/enabled\"; if [ \"$bad_disable\" = true ]; then echo failed > \"${state_dir}/active\"; else echo inactive > \"${state_dir}/active\"; fi ;;\n"
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
    assert f"--user show -p UnitFileState,ActiveState,NextElapseUSecRealtime {UNIT}" in joined
    assert f"disable --now {UNIT}" not in joined
    assert "current-state: UnitFileState=enabled ActiveState=active" in result.stdout
    assert "rollback" in result.stdout
    assert list((tmp_path / "xdg-state" / "workspace-hub" / "scheduler-mutations").glob("*.baseline"))


def test_no_flag_defaults_to_check_mode_and_prints_state(tmp_path: Path) -> None:
    install_systemctl(tmp_path, enabled="disabled", active="inactive")
    result = run_mutator(tmp_path)
    assert result.returncode == 0, result.stderr
    joined = "\n".join(calls(tmp_path))
    assert f"disable --now {UNIT}" not in joined
    assert "current-state: UnitFileState=disabled ActiveState=inactive" in result.stdout


def test_unknown_flag_is_rejected_without_systemctl_calls(tmp_path: Path) -> None:
    install_systemctl(tmp_path)
    result = run_mutator(tmp_path, "--definitely-not-real")
    assert result.returncode == 2
    assert "unknown argument" in result.stderr
    assert calls(tmp_path) == []


def test_apply_refuses_when_exact_show_state_drifts(tmp_path: Path) -> None:
    install_systemctl(tmp_path, drift_on_second_show=True)
    result = run_mutator(tmp_path, "--apply")
    assert result.returncode == 3
    joined = "\n".join(calls(tmp_path))
    assert f"--user show -p UnitFileState,ActiveState,NextElapseUSecRealtime {UNIT}" in joined
    assert "list-timers" not in joined
    assert f"disable --now {UNIT}" not in joined
    assert "timer state changed between baseline and apply" in result.stderr


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


def test_failed_post_disable_state_rolls_back_after_state_check(tmp_path: Path) -> None:
    install_systemctl(tmp_path, bad_disable=True)
    result = run_mutator(tmp_path, "--apply")
    assert result.returncode == 4
    call_lines = calls(tmp_path)
    enable_index = call_lines.index(f"--user enable --now {UNIT}")
    prior_show_index = max(
        idx
        for idx, line in enumerate(call_lines)
        if line == f"--user show -p UnitFileState,ActiveState,NextElapseUSecRealtime {UNIT}" and idx < enable_index
    )
    assert prior_show_index < enable_index
    assert (tmp_path / "state" / "enabled").read_text().strip() == "enabled"
    assert (tmp_path / "state" / "active").read_text().strip() == "active"
    assert "rollback pre-state: UnitFileState=disabled ActiveState=failed" in result.stderr


def test_registry_declares_cnh_timer_mutator() -> None:
    text = REGISTRY.read_text()
    idx = text.find("scripts/install/disable-cnh-source-watch-timer.sh")
    assert idx != -1
    block = text[idx:idx + 1600]
    assert "local-user-systemd-claude-routine-mx-720-cnh-source-watch" in block
    assert "systemd-user-enable-disable" in block
    assert "execution_host_binding: physical-local" in block
    assert "disposition_group: cnh-source-watch-disable" in block
