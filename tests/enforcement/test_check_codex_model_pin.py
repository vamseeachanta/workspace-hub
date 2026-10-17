"""Offline checks for committed Codex model defaults."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/enforcement/check-codex-model-pin.sh"
EXCEPTIONS = tuple(
    f".codex/agents/fixture-{role}/config.toml" for role in ("one", "two", "three")
)


@pytest.fixture
def repo(tmp_path):
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
        env.pop(key, None)
    subprocess.run(["git", "init", "-q", str(tmp_path)], env=env, check=True)
    return tmp_path, env


@pytest.fixture
def exception_script(tmp_path):
    source, count = re.subn(
        r"^ALLOWLIST = \(.*?\)", f"ALLOWLIST = {EXCEPTIONS!r}",
        SCRIPT.read_text(), count=1, flags=re.DOTALL | re.MULTILINE,
    )
    assert count == 1
    path = tmp_path / "check-with-fixture-exceptions.sh"
    path.write_text(source)
    return path


def track(repo, name, text):
    root, env = repo
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    subprocess.run(["git", "add", "--", name], cwd=root, env=env, check=True)


def run(repo, *args, script=SCRIPT):
    root, env = repo
    return subprocess.run(
        ["bash", str(script), *args], cwd=root, env=env,
        text=True, capture_output=True, check=False,
    )


def test_clean_tree(repo):
    track(repo, ".codex/config.toml", 'model_provider = "local"\n')
    assert run(repo).returncode == 0


@pytest.mark.parametrize("name", [
    ".codex/config.toml", "config/agents/codex/config.toml",
    "config/agents/codex/nested/settings.toml",
    ".codex/agents/extra/config.toml", ".codex/agents/extra.toml",
])
def test_pin_fails_with_file_line_and_value(repo, name):
    track(repo, name, '# comment\nmodel = "unsupported"\n')
    result = run(repo)
    assert result.returncode == 1
    assert f'{name}:2:' in result.stdout + result.stderr
    assert '"unsupported"' in result.stdout + result.stderr


@pytest.mark.parametrize("text", [
    'model_reasoning_effort = "medium"\n',
    '[profiles.x]\nmodel = "local"\n',
    '[settings]\nmodel = "local"\n',
    '# model = "local"\n',
    'description = """\nmodel = "literal"\n"""\n',
    'description = "[settings]"\n',
])
def test_non_pins_pass(repo, text):
    track(repo, ".codex/config.toml", text)
    assert run(repo).returncode == 0


@pytest.mark.parametrize("key", ['"model"', "'model'", '   model   ', '  "model"  '])
def test_quoted_or_spaced_pin_fails(repo, key):
    track(repo, ".codex/config.toml", f'{key} = "unsupported"\n')
    assert run(repo).returncode == 1


def test_multiline_header_cannot_hide_pin(repo):
    track(repo, ".codex/config.toml", 'text = """\n[settings]\n"""\nmodel = "x"\n')
    assert run(repo).returncode == 1


@pytest.mark.parametrize("name", EXCEPTIONS)
def test_allowlisted_pin_passes(repo, exception_script, name):
    track(repo, name, 'model = "small"\n')
    result = run(repo, script=exception_script)
    assert result.returncode == 0
    assert f"ALLOW {name}" in result.stdout


def test_all_exceptions_and_fourth_pin(repo, exception_script):
    for name in EXCEPTIONS:
        track(repo, name, 'model = "small"\n')
    track(repo, ".codex/agents/fourth/config.toml", 'model = "x"\n')
    assert run(repo, script=exception_script).returncode == 1


def test_stale_allowlist_fails(repo, exception_script):
    track(repo, EXCEPTIONS[0], 'model_reasoning_effort = "medium"\n')
    result = run(repo, script=exception_script)
    assert result.returncode == 1
    assert f"{EXCEPTIONS[0]}: stale allowlist entry" in result.stdout + result.stderr


def test_worker_model_pin_readded_is_rejected(repo):
    name = ".codex/agents/worker/config.toml"
    track(repo, name, 'model_reasoning_effort = "medium"\nmodel = "unsupported"\n')
    result = run(repo)
    assert result.returncode == 1
    assert f'{name}:2: model = "unsupported"' in result.stdout
    assert "ALLOW" not in result.stdout


def test_untracked_config_is_not_checked(repo):
    root, _ = repo
    (root / ".codex").mkdir()
    (root / ".codex/config.toml").write_text('model = "x"\n')
    assert run(repo).returncode == 0


@pytest.mark.parametrize("args", [("--bad",), ("extra",), ("--help", "extra")])
def test_usage_errors(repo, args):
    assert run(repo, *args).returncode == 2


def test_help(repo):
    result = run(repo, "--help")
    assert result.returncode == 0
    assert "Usage:" in result.stdout


def test_repository_has_no_unexpected_pins():
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
        env.pop(key, None)
    result = run((ROOT, env))
    assert result.returncode == 0, result.stdout + result.stderr
