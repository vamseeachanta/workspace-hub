"""Behavioral checks for the pinned Codex setup baseline (#3555)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "scripts/setup/verify-setup.sh"
PIN = ROOT / "scripts/install/pin-codex.sh"


def _write_fake_codex(bin_dir: Path) -> None:
    """Create the CLI seam; its feature state is driven by isolated config."""
    fake = bin_dir / "codex"
    fake.write_text(
        """#!/usr/bin/env bash
set -eu
if [[ \"${1:-}\" == \"--version\" ]]; then
  echo \"codex-cli ${FAKE_CODEX_VERSION:-0.146.0}\"
  exit 0
fi
if [[ \"${1:-}\" == \"features\" && \"${2:-}\" == \"list\" ]]; then
  config=\"${CODEX_HOME}/config.toml\"
  if [[ -f \"$config\" ]] && grep -q 'web_search = "broken"' \"$config\"; then
    echo 'invalid enum value' >&2
    exit 2
  fi
  state=false
  if [[ -f \"$config\" ]] && grep -q 'default_mode_request_user_input = true' \"$config\"; then
    state=true
  fi
  if [[ \"${FAKE_FEATURE_MODE:-normal}\" == \"always-true\" ]]; then state=true; fi
  if [[ \"${FAKE_FEATURE_MODE:-normal}\" == \"missing\" ]]; then
    echo 'goals stable true'
  else
    echo \"default_mode_request_user_input under development $state\"
  fi
  exit 0
fi
echo "unexpected codex invocation: $*" >&2
exit 3
""",
        encoding="utf-8",
    )
    fake.chmod(0o755)


def _environment(tmp_path: Path, **extra: str) -> dict[str, str]:
    home = tmp_path / "home"
    codex_home = tmp_path / "candidate-home"
    bin_dir = tmp_path / "bin"
    (home / ".claude").mkdir(parents=True)
    bin_dir.mkdir()
    _write_fake_codex(bin_dir)
    env = os.environ | {
        "HOME": str(home),
        "CODEX_HOME": str(codex_home),
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
    }
    return env | extra


def _verify(tmp_path: Path, **extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(VERIFY)],
        cwd=ROOT,
        env=_environment(tmp_path, **extra),
        text=True,
        capture_output=True,
        check=False,
    )


def test_verifier_accepts_pinned_config_and_proves_feature_delta(tmp_path: Path) -> None:
    """Removing config-driven feature enablement must make verification fail."""
    result = _verify(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS  codex CLI found at pinned version 0.146.0" in result.stdout
    assert "PASS  codex feature default_mode_request_user_input: false -> true" in result.stdout
    assert "PASS  codex TUI footer selectors validated for 0.146.0" in result.stdout


def test_verifier_rejects_older_codex_before_feature_validation(tmp_path: Path) -> None:
    """Accepting 0.145.0 would run a baseline without the required feature."""
    result = _verify(tmp_path, FAKE_CODEX_VERSION="0.145.0")
    assert "FAIL  codex CLI version 0.145.0 is older than pinned 0.146.0" in result.stdout


def test_verifier_rejects_absent_feature_and_non_differential_output(tmp_path: Path) -> None:
    """A missing or always-enabled listing cannot prove config activation."""
    absent = _verify(tmp_path / "absent", FAKE_FEATURE_MODE="missing")
    assert "FAIL  codex feature default_mode_request_user_input is absent" in absent.stdout
    constant = _verify(tmp_path / "constant", FAKE_FEATURE_MODE="always-true")
    assert "FAIL  codex feature default_mode_request_user_input did not change false -> true" in constant.stdout


def test_verifier_rejects_typed_enum_load_error(tmp_path: Path) -> None:
    """A malformed typed value must fail the isolated CLI configuration load."""
    bad_config = tmp_path / "bad.toml"
    shutil.copyfile(ROOT / "config/agents/codex/config.toml", bad_config)
    bad_config.write_text(
        bad_config.read_text(encoding="utf-8").replace('web_search = "live"', 'web_search = "broken"'),
        encoding="utf-8",
    )
    result = _verify(tmp_path / "invalid", CODEX_CONFIG_TEMPLATE=str(bad_config))
    assert "FAIL  codex isolated config load failed" in result.stdout


def test_verifier_rejects_footer_outside_pinned_selector_allowlist(
    tmp_path: Path,
) -> None:
    """A typo must not pass merely because Codex silently accepts footer strings."""
    bad_config = tmp_path / "bad-footer.toml"
    shutil.copyfile(ROOT / "config/agents/codex/config.toml", bad_config)
    bad_config.write_text(
        bad_config.read_text(encoding="utf-8").replace(
            "current-dir", "unknown-footer"
        ),
        encoding="utf-8",
    )
    result = _verify(tmp_path / "bad-footer", CODEX_CONFIG_TEMPLATE=str(bad_config))
    assert "FAIL  codex TUI footer selectors are not in pinned allowlist" in result.stdout


def test_pin_script_uses_fixture_cli_without_network_install(tmp_path: Path) -> None:
    """A pinned fixture must short-circuit before npm can install from the network."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_fake_codex(bin_dir)
    npm_log = tmp_path / "npm.log"
    fake_npm = bin_dir / "npm"
    fake_npm.write_text(
        f"#!/usr/bin/env bash\necho \"$*\" >> {npm_log}\nexit 99\n",
        encoding="utf-8",
    )
    fake_npm.chmod(0o755)
    result = subprocess.run(
        ["bash", str(PIN)],
        cwd=ROOT,
        env=os.environ | {
            "CODEX_BIN": str(bin_dir / "codex"),
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
        },
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "already at pin 0.146.0" in result.stdout
    assert not npm_log.exists()


def test_pin_script_checks_npm_global_bin_before_installing(tmp_path: Path) -> None:
    """An existing pinned global binary must not be replaced when absent from PATH."""
    global_bin = tmp_path / "global-bin"
    global_bin.mkdir()
    _write_fake_codex(global_bin)
    npm_log = tmp_path / "npm.log"
    fake_npm = tmp_path / "npm"
    fake_npm.write_text(
        "#!/usr/bin/env bash\n"
        f"if [[ \"$1 $2\" == \"bin -g\" ]]; then echo {global_bin}; exit 0; fi\n"
        f"echo \"$*\" >> {npm_log}\nexit 99\n",
        encoding="utf-8",
    )
    fake_npm.chmod(0o755)
    result = subprocess.run(
        ["bash", str(PIN)],
        cwd=ROOT,
        env=os.environ | {"PATH": f"{tmp_path}:/usr/bin:/bin"},
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "already at pin 0.146.0" in result.stdout
    assert not npm_log.exists()
