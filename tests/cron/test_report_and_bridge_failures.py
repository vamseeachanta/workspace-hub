"""Isolated regressions for report parsing and scheduled executable discovery."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]


def isolated_env(home):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["HOME"] = str(home)
    env.pop("CLAUDE_BIN", None)
    return env


@pytest.mark.parametrize("setting,expected", [
    ("test-model", "test-model"), ({"name": "test-model"}, "test-model"),
    (None, "not set"), ({}, "not set"),
])
def test_active_provider_config_accepts_string_and_object(tmp_path, setting, expected):
    source = (ROOT / "scripts/productivity/sections/ai-usage-summary.sh").read_text()
    # Only execute the pure report block; the whole section also probes CLIs.
    block = source.split("<<'PYEOF'\n")[-1].split("\nPYEOF")[0]
    config = tmp_path / ".gemini/antigravity-cli/settings.json"
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({"model": setting}))
    result = subprocess.run([sys.executable, "-", str(tmp_path)], input=block,
                            env=isolated_env(tmp_path), capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert f"| agy | {expected} |" in result.stdout


def bridge_fixture(tmp_path):
    script_dir = tmp_path / "repo/scripts/memory"
    script_dir.mkdir(parents=True)
    script = script_dir / "bridge-providers-to-dream.sh"
    shutil.copy(ROOT / "scripts/memory/bridge-providers-to-dream.sh", script)
    bindir = tmp_path / "bin"
    bindir.mkdir()
    # A bounded PATH proves discovery without exposing any installed model CLI.
    for name in ("bash", "dirname", "mkdir", "date", "tee", "git"):
        (bindir / name).symlink_to(shutil.which(name))
    uv = bindir / "uv"
    uv.write_text('#!/bin/sh\nif [ "${4:-}" = "-c" ]; then exit 0; fi\n'
                  'printf "%s\\n" "$CLAUDE_BIN" > "$CAPTURE"\n')
    uv.chmod(0o755)
    env = isolated_env(tmp_path / "home")
    env.update(PATH=str(bindir), CAPTURE=str(tmp_path / "selected"))
    return script, bindir, env


@pytest.mark.parametrize("location", ["path", ".local/bin", ".npm-global/bin"])
def test_bridge_resolves_cli_without_executing_it(tmp_path, location):
    script, bindir, env = bridge_fixture(tmp_path)
    folder = bindir if location == "path" else Path(env["HOME"]) / location
    folder.mkdir(parents=True, exist_ok=True)
    cli = folder / "claude"
    cli.write_text("#!/bin/sh\nexit 99\n")
    cli.chmod(0o755)
    result = subprocess.run([shutil.which("bash"), str(script)], env=env,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert Path(env["CAPTURE"]).read_text().strip() == str(cli)


def test_bridge_missing_cli_stops_before_distiller(tmp_path):
    script, _, env = bridge_fixture(tmp_path)
    result = subprocess.run([shutil.which("bash"), str(script)], env=env,
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert "CLI unavailable" in result.stdout + result.stderr
    assert not Path(env["CAPTURE"]).exists()
