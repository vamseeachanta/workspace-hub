"""Behavioral checks for the pinned Codex setup baseline (#3555)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


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
  if [[ \"${FAKE_FEATURE_MODE:-normal}\" == \"before-error\" && ! -f "$config" ]]; then
    echo 'default_mode_request_user_input under development false'
    exit 9
  fi
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
    fake_claude = bin_dir / "claude"
    fake_claude.write_text("#!/bin/sh\necho 'claude fixture 1.0'\n", encoding="utf-8")
    fake_claude.chmod(0o755)
    env = os.environ | {
        "HOME": str(home),
        "CODEX_HOME": str(codex_home),
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
    }
    return env | extra


def _verify(tmp_path: Path, **extra: str) -> subprocess.CompletedProcess[str]:
    return _run_verifier(_environment(tmp_path, **extra))


def _run_verifier(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(VERIFY), "--strict"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _mutated_config(tmp_path: Path, old: str, new: str) -> Path:
    candidate = tmp_path / "candidate.toml"
    text = (ROOT / "config/agents/codex/config.toml").read_text(encoding="utf-8")
    assert old in text
    candidate.write_text(text.replace(old, new, 1), encoding="utf-8")
    return candidate


def _assert_rejected(result: subprocess.CompletedProcess[str], message: str) -> None:
    assert result.returncode != 0, result.stdout + result.stderr
    assert message in result.stdout


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
    _assert_rejected(
        result, "FAIL  codex CLI version 0.145.0 is older than pinned 0.146.0"
    )


def test_verifier_rejects_absent_feature_and_non_differential_output(tmp_path: Path) -> None:
    """A missing or always-enabled listing cannot prove config activation."""
    absent = _verify(tmp_path / "absent", FAKE_FEATURE_MODE="missing")
    _assert_rejected(
        absent, "FAIL  codex feature default_mode_request_user_input is absent"
    )
    constant = _verify(tmp_path / "constant", FAKE_FEATURE_MODE="always-true")
    _assert_rejected(
        constant,
        "FAIL  codex feature default_mode_request_user_input did not change false -> true",
    )


def test_verifier_rejects_typed_enum_load_error(tmp_path: Path) -> None:
    """A malformed typed value must fail the isolated CLI configuration load."""
    bad_config = tmp_path / "bad.toml"
    shutil.copyfile(ROOT / "config/agents/codex/config.toml", bad_config)
    bad_config.write_text(
        bad_config.read_text(encoding="utf-8").replace('web_search = "live"', 'web_search = "broken"'),
        encoding="utf-8",
    )
    result = _verify(tmp_path / "invalid", CODEX_CONFIG_TEMPLATE=str(bad_config))
    _assert_rejected(result, "FAIL  codex isolated config load failed")


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
    _assert_rejected(
        result, "FAIL  codex canonical config does not match owned baseline"
    )


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('plan_mode_reasoning_effort = "high"', 'plan_mode_reasoning_effort = "low"'),
        ('personality = "pragmatic"', 'personality = "friendly"'),
        ('web_search = "live"', 'web_search = "cached"'),
        ("default_mode_request_user_input = true", "default_mode_request_user_input = false"),
        ("goals = true", "goals = false"),
        ("multi_agent = true", "multi_agent = false"),
        ("hooks = true", "hooks = false"),
        ("enabled = true", "enabled = false"),
        ("interrupt_message = true", "interrupt_message = false"),
        ('resume_cwd = "session"', 'resume_cwd = "current"'),
    ],
)
def test_verifier_rejects_drift_of_every_owned_scalar(
    tmp_path: Path, old: str, new: str
) -> None:
    """Every owned scalar is part of the exact semantic fleet contract."""
    candidate = _mutated_config(tmp_path, old, new)
    result = _verify(tmp_path / "verify", CODEX_CONFIG_TEMPLATE=str(candidate))
    _assert_rejected(
        result, "FAIL  codex canonical config does not match owned baseline"
    )


@pytest.mark.parametrize(
    "forbidden",
    [
        'model = "gpt-local"',
        'model_reasoning_effort = "medium"',
        "memories = true",
        "approval_reviewers = true",
        "status_line_use_colors = true",
    ],
)
def test_verifier_rejects_every_forbidden_key(
    tmp_path: Path, forbidden: str
) -> None:
    """Local ownership and undocumented keys must remain absent from the template."""
    source = ROOT / "config/agents/codex/config.toml"
    candidate = tmp_path / "forbidden.toml"
    candidate.write_text(f"{forbidden}\n{source.read_text()}", encoding="utf-8")
    result = _verify(tmp_path / "verify", CODEX_CONFIG_TEMPLATE=str(candidate))
    _assert_rejected(
        result, "FAIL  codex canonical config does not match owned baseline"
    )


@pytest.mark.parametrize(
    ("old", "new"),
    [
        (
            '  "model-with-reasoning",\n  "context-remaining",',
            '  "context-remaining",\n  "model-with-reasoning",',
        ),
        ('  "current-dir",', '  "current-dir",\n  "current-dir",'),
    ],
)
def test_verifier_rejects_footer_order_drift_and_duplicates(
    tmp_path: Path, old: str, new: str
) -> None:
    """The footer is an ordered array, not a set."""
    candidate = _mutated_config(tmp_path, old, new)
    result = _verify(tmp_path / "verify", CODEX_CONFIG_TEMPLATE=str(candidate))
    _assert_rejected(
        result, "FAIL  codex canonical config does not match owned baseline"
    )


def test_verifier_rejects_nonzero_baseline_probe_with_false_output(
    tmp_path: Path,
) -> None:
    """Misleading output from a failed control command is not evidence."""
    result = _verify(tmp_path, FAKE_FEATURE_MODE="before-error")
    _assert_rejected(result, "FAIL  codex isolated baseline feature probe failed")


def test_verifier_rejects_malformed_cli_version_without_arithmetic_error(
    tmp_path: Path,
) -> None:
    """Only strict numeric semver may reach numeric comparison."""
    result = _verify(tmp_path, FAKE_CODEX_VERSION="release-candidate")
    _assert_rejected(result, "FAIL  codex CLI version is malformed: release-candidate")
    assert "syntax error" not in result.stderr


def test_verifier_rejects_pin_without_matching_selector_attestation(
    tmp_path: Path,
) -> None:
    """A new pin cannot reuse the selector evidence recorded for 0.146.0."""
    pin_env = tmp_path / "codex-pin.env"
    pin_env.write_text("CODEX_PIN_VERSION=0.147.0\n", encoding="utf-8")
    result = _verify(
        tmp_path / "verify",
        CODEX_PIN_ENV=str(pin_env),
        FAKE_CODEX_VERSION="0.147.0",
    )
    _assert_rejected(
        result, "FAIL  no TUI selector attestation for pinned Codex 0.147.0"
    )


def test_verifier_uses_uv_python_seam_when_python3_is_unavailable(
    tmp_path: Path,
) -> None:
    """Canonical validation must run through uv, not a bare Python binary."""
    env = _environment(tmp_path)
    python_log = tmp_path / "python3.log"
    python3 = tmp_path / "bin" / "python3"
    python3.write_text(f"#!/bin/sh\necho called > {python_log}\nexit 99\n")
    python3.chmod(0o755)
    result = _run_verifier(env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not python_log.exists()


def test_verifier_uses_platform_safe_mktemp_directory(tmp_path: Path) -> None:
    """Temporary directory creation must not embed a POSIX-only root path."""
    env = _environment(tmp_path)
    env["REAL_MKTEMP"] = shutil.which("mktemp") or "mktemp"
    mktemp_log = tmp_path / "mktemp.log"
    fake_mktemp = tmp_path / "bin" / "mktemp"
    fake_mktemp.write_text(
        f"#!/bin/sh\necho \"$*\" > {mktemp_log}\n"
        'exec "$REAL_MKTEMP" "$@"\n'
    )
    fake_mktemp.chmod(0o755)
    result = _run_verifier(env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert mktemp_log.read_text(encoding="utf-8").strip() == "-d"


def test_verifier_rejects_unexpected_semantic_validator_status(
    tmp_path: Path,
) -> None:
    """A validator infrastructure error must not disappear behind a green probe."""
    env = _environment(tmp_path)
    fake_uv = tmp_path / "bin" / "uv"
    fake_uv.write_text("#!/bin/sh\nexit 7\n", encoding="utf-8")
    fake_uv.chmod(0o755)
    result = _run_verifier(env)
    assert "PASS  codex feature default_mode_request_user_input: false -> true" in result.stdout
    _assert_rejected(
        result, "FAIL  codex canonical config validator failed with status 7"
    )


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
