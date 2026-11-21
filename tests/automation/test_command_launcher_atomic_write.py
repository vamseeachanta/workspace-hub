"""Caller contracts in disposable repositories; no synchronization is invoked.

The ordinary launcher source is frozen from create_command_links before the
atomic-write integration. Argument indexes follow Python's sys.argv convention.
Unicode byte expectations are hand-encoded per RFC 3629 section 3. Permission
expectations use POSIX symbolic flags from stat, rather than decimal constants.
"""

import ast
import hashlib
import io
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.automation import sync_and_propagate_commands as generator
from scripts.utils import atomic_write as atomic


BEFORE = b"# prior launcher\n"
PRIOR_MODE = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
EXECUTABLE_MODE = (
    PRIOR_MODE | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
)
# Frozen pre-integration source; independent of the generator's renderer.
EXPECTED_LAUNCHER = b'''#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add commands directory to path
commands_dir = Path(__file__).parent / ".agent-os" / "commands"
sys.path.insert(0, str(commands_dir))

# Import and run the requested command
if len(sys.argv) > 1:
    cmd = sys.argv[1].lstrip('/')
    if cmd in ['git', 'spec', 'task', 'test', 'project', 'data', 'ai-agent', 'uv-env', 'verify']:
        module = {'git': 'git.py', 'spec': 'spec.py', 'task': 'task.py', 'test': 'test.py', 'project': 'project.py', 'data': 'data.py', 'ai-agent': 'ai_agent.py', 'uv-env': 'uv_environment_manager.py', 'verify': 'verify-ai-work.py'}.get(cmd)
        if module:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                module.replace('.py', ''),
                commands_dir / module
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, 'main'):
                sys.argv = [cmd] + sys.argv[2:]
                mod.main()
'''


@pytest.fixture
def repository(tmp_path):
    repo = tmp_path / "repository"
    (repo / ".git").mkdir(parents=True)
    (repo / ".agent-os" / "commands").mkdir(parents=True)
    return repo


@pytest.fixture
def prior_launcher(repository):
    launcher = repository / "agos"
    launcher.write_bytes(BEFORE)
    launcher.chmod(PRIOR_MODE)
    return launcher


@pytest.fixture
def single_byte_default(monkeypatch):
    """Force implicit text opens to Latin-1, including Path.write_text.

    Python io.open defines the default buffering sentinel as -1; pathlib may
    resolve an unspecified encoding to io.text_encoding's "locale" sentinel.
    """
    real_open = io.open

    def latin1_open(file, mode="r", buffering=-1, encoding=None, *args, **kwargs):
        if "b" not in mode and encoding in (None, "locale"):
            encoding = "latin-1"
        return real_open(file, mode, buffering, encoding, *args, **kwargs)

    monkeypatch.setattr(io, "open", latin1_open)


def assert_no_staging_residue(repository):
    assert set(repository.iterdir()) == {
        repository / ".git", repository / ".agent-os", repository / "agos"
    }


def test_launcher_unicode_round_trips_without_default_encoding(
    repository, single_byte_default
):
    # Demonstrate that the fixture changes real default text I/O, not only locale.
    probe = repository / "encoding-probe"
    with pytest.raises(UnicodeEncodeError):
        probe.write_text("→ café")
    # Keep the fixture probe outside the generated repository's output inventory.
    probe.rename(repository.parent / "encoding-probe")

    def render_unicode(template, **values):
        return template.format(**values) + "# → café\n"

    receipt = generator.create_command_links(repository, render_launcher=render_unicode)
    launcher = repository / "agos"
    # RFC 3629 section 3: U+2192 -> e2 86 92, U+00E9 -> c3 a9.
    expected = EXPECTED_LAUNCHER + b"# \xe2\x86\x92 caf\xc3\xa9\n"
    assert launcher.read_bytes() == expected
    ast.parse(launcher.read_bytes().decode("utf-8"))
    assert receipt["written_sha"] == hashlib.sha256(expected).hexdigest()
    assert_no_staging_residue(repository)


def test_launcher_ordinary_python_is_unchanged(repository):
    generator.create_command_links(repository)
    launcher = repository / "agos"
    assert ast.dump(ast.parse(launcher.read_bytes())) == ast.dump(
        ast.parse(EXPECTED_LAUNCHER)
    )
    assert launcher.read_bytes() == EXPECTED_LAUNCHER
    assert stat.S_IMODE(launcher.stat().st_mode) == EXECUTABLE_MODE
    assert_no_staging_residue(repository)


@pytest.mark.parametrize("phase", ["stage", "replace"])
def test_launcher_failed_stage_preserves_prior_bytes(prior_launcher, monkeypatch, phase):
    def refuse(*args):
        raise PermissionError("injected write failure")

    monkeypatch.setattr(atomic.os, "write" if phase == "stage" else "replace", refuse)
    with pytest.raises(atomic.AtomicWriteError) as failure:
        generator.create_command_links(prior_launcher.parent)
    error = failure.value
    assert isinstance(error.__cause__, PermissionError)
    assert error.before_bytes == BEFORE
    assert error.before_mode == PRIOR_MODE
    assert error.receipt["before_sha"] == hashlib.sha256(BEFORE).hexdigest()
    assert error.receipt["attempted_sha"] == hashlib.sha256(EXPECTED_LAUNCHER).hexdigest()
    assert error.receipt["written_sha"] is None
    assert prior_launcher.read_bytes() == BEFORE
    assert stat.S_IMODE(prior_launcher.stat().st_mode) == PRIOR_MODE
    assert_no_staging_residue(prior_launcher.parent)


def test_launcher_concurrent_change_is_retained(prior_launcher, monkeypatch):
    stage = atomic._stage
    concurrent_bytes = b"# concurrent launcher\n"
    concurrent_mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP

    def stage_then_change(*args):
        staged = stage(*args)
        prior_launcher.write_bytes(concurrent_bytes)
        prior_launcher.chmod(concurrent_mode)
        return staged

    monkeypatch.setattr(atomic, "_stage", stage_then_change)
    with pytest.raises(atomic.ConcurrentChangeError) as failure:
        generator.create_command_links(prior_launcher.parent)
    assert failure.value.before_bytes == BEFORE
    assert failure.value.before_mode == PRIOR_MODE
    assert failure.value.receipt["written_sha"] is None
    assert prior_launcher.read_bytes() == concurrent_bytes
    assert stat.S_IMODE(prior_launcher.stat().st_mode) == concurrent_mode
    assert_no_staging_residue(prior_launcher.parent)


def test_launcher_retains_executable_mode(prior_launcher):
    generator.create_command_links(prior_launcher.parent)
    assert prior_launcher.read_bytes() == EXPECTED_LAUNCHER
    assert stat.S_IMODE(prior_launcher.stat().st_mode) == EXECUTABLE_MODE
    assert_no_staging_residue(prior_launcher.parent)


def test_generator_imports_outside_checkout(tmp_path):
    # Isolated Python removes checkout/PYTHONPATH help; run_path never invokes main.
    env = os.environ.copy()
    for name in ("PYTHONPATH", "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        env.pop(name, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [
            sys.executable, "-I", "-B", "-c",
            "import runpy, sys; "
            "module = runpy.run_path(sys.argv[1], run_name='generator_import'); "
            "assert callable(module['create_command_links'])",
            str(Path(generator.__file__).resolve()),
        ],
        cwd=tmp_path, env=env, capture_output=True, text=True, check=True,
    )
    assert result.stdout == ""
    assert result.stderr == ""
    assert not list(tmp_path.iterdir())
