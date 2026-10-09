from __future__ import annotations

import os
import stat
import subprocess
import sys
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "maintenance" / "update-harness-tools.sh"


def _write_executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _fake_toolchain(tmp_path: Path) -> dict[str, str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    tool_log = log_dir / "tools.log"
    installer_log = log_dir / "installer.log"
    health_log = log_dir / "health.log"

    for tool in ("hermes", "claude", "codex", "npm", "agy"):
        _write_executable(
            bin_dir / tool,
            "#!/usr/bin/env bash\n"
            f"printf '{tool} %s\\n' \"$*\" >> \"{tool_log}\"\n",
        )

    installer = tmp_path / "install-hermes-b2.sh"
    _write_executable(
        installer,
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" >> \"{installer_log}\"\n",
    )

    health = tmp_path / "patch-health-check.py"
    health.write_text(
        "#!/usr/bin/env python3\n"
        "import os\n"
        f"open({str(health_log)!r}, 'a', encoding='utf-8').write('health\\n')\n",
        encoding="utf-8",
    )
    health.chmod(health.stat().st_mode | stat.S_IXUSR)

    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{bin_dir}:{env.get('PATH', '')}",
            "HOME": str(tmp_path / "home"),
            "DECKHAND_HERMES_INSTALLER": str(installer),
            "DECKHAND_HEALTH_CHECK": str(health),
            "DECKHAND_GATEWAY_PROCESS_PATTERN": "definitely-no-deckhand-gateway-for-test",
        }
    )
    return {
        "env": env,
        "installer_log": str(installer_log),
        "health_log": str(health_log),
    }


def _run_update(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_deckhand_inactive_skips_patch_steps_with_zero_exit(tmp_path: Path) -> None:
    ctx = _fake_toolchain(tmp_path)

    result = _run_update(ctx["env"])

    assert result.returncode == 0, result.stdout + result.stderr
    assert "skipped (deckhand inactive)" in result.stdout
    assert not Path(ctx["installer_log"]).exists()
    assert not Path(ctx["health_log"]).exists()


def test_deckhand_opt_in_runs_patch_and_health_steps(tmp_path: Path) -> None:
    ctx = _fake_toolchain(tmp_path)
    env = dict(ctx["env"], DECKHAND_PATCHES="1")

    result = _run_update(env)

    assert result.returncode == 0, result.stdout + result.stderr
    assert Path(ctx["installer_log"]).read_text(encoding="utf-8").splitlines() == [
        "--apply",
        "",
    ]
    assert Path(ctx["health_log"]).read_text(encoding="utf-8") == "health\n"


def test_running_gateway_runs_patch_and_health_steps(tmp_path: Path) -> None:
    ctx = _fake_toolchain(tmp_path)
    marker = f"deckhand-gateway-test-{os.getpid()}"
    env = dict(ctx["env"], DECKHAND_GATEWAY_PROCESS_PATTERN=marker)
    sleeper = subprocess.Popen(
        [
            sys.executable,
            "-c",
            textwrap.dedent(
                """
                import time
                time.sleep(60)
                """
            ),
            marker,
        ]
    )
    try:
        result = _run_update(env)
    finally:
        sleeper.terminate()
        try:
            sleeper.wait(timeout=5)
        except subprocess.TimeoutExpired:
            sleeper.kill()

    assert result.returncode == 0, result.stdout + result.stderr
    assert Path(ctx["installer_log"]).read_text(encoding="utf-8").splitlines() == [
        "--apply",
        "",
    ]
    assert Path(ctx["health_log"]).read_text(encoding="utf-8") == "health\n"
