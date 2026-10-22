"""Lock examples use a fixed clock: 10000 - 9800 = 200 seconds > 100-second policy.

Contention status 75 is the configured flock(1) -E value, not a success status.
No wall-clock age, host PID guesses or network connections are used.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

LIB = Path(__file__).resolve().parents[2] / 'scripts/readiness/lib/publish-lock.sh'


def command(path, body):
    path.write_text('#!/usr/bin/env bash\n' + body)
    path.chmod(0o755)


@pytest.fixture
def lock_env(tmp_path):
    bins = tmp_path / 'bin'
    bins.mkdir()
    for name in ('bash', 'mkdir', 'rmdir', 'rm', 'cat'):
        (bins / name).symlink_to(shutil.which(name))
    command(bins / 'date', 'echo 10000\n')
    env = {**os.environ, 'PATH': str(bins), 'PUBLISH_EQUALITY_LOCK': 'auto',
           'PUBLISH_EQUALITY_LOCK_STALE_SECONDS': '100', 'LOCK': str(tmp_path / 'publish')}
    return env, bins


def run(env, body='acquire_publish_lock "$LOCK" || exit $?\necho acquired\nrelease_publish_lock'):
    return subprocess.run(['bash', '-c', f'source "{LIB}"\n{body}'], env=env,
                          capture_output=True, text=True, check=False, timeout=10)


def owner(env, pid, stamp):
    path = Path(env['LOCK'] + '.d')
    path.mkdir()
    (path / 'owner').write_text(f'{pid} {stamp}\n')
    return path


def test_missing_flock_uses_directory(lock_env):
    env, _ = lock_env
    result = run(env)
    assert result.returncode == 0, result.stderr
    assert 'acquired' in result.stdout
    assert not Path(env['LOCK'] + '.d').exists()


def test_live_owner_is_contention_even_when_old(lock_env):
    env, _ = lock_env
    path = owner(env, os.getpid(), 9800)
    result = run(env)
    assert result.returncode == 75
    assert path.exists()


def test_dead_old_owner_is_reclaimed(lock_env):
    env, _ = lock_env
    dead = subprocess.Popen(['bash', '-c', 'exit 0'], env=env)
    dead.wait()
    path = owner(env, dead.pid, 9800)
    result = run(env)
    assert result.returncode == 0, result.stderr
    assert 'reclaimed stale' in result.stderr
    assert not path.exists()


def test_dead_recent_owner_is_not_reclaimed(lock_env):
    env, _ = lock_env
    dead = subprocess.Popen(['bash', '-c', 'exit 0'], env=env)
    dead.wait()
    owner(env, dead.pid, 9950)
    assert run(env).returncode == 75


def test_incomplete_owner_cannot_be_stolen(lock_env):
    env, _ = lock_env
    path = Path(env['LOCK'] + '.d')
    path.mkdir()
    assert run(env).returncode != 0
    assert path.exists()


@pytest.mark.parametrize('code,expected', [(0, 0), (75, 75), (88, 1)])
def test_flock_result_is_distinguished(lock_env, code, expected):
    env, bins = lock_env
    command(bins / 'flock', f'exit {code}\n')
    result = run(env)
    assert result.returncode == expected, result.stderr
    assert not Path(env['LOCK'] + '.d').exists()


def test_setup_failure_is_not_contention(lock_env):
    env, _ = lock_env
    Path(env['LOCK'] + '.d').write_text('not a directory')
    result = run(env)
    assert result.returncode == 1


def test_replaced_owner_is_preserved(lock_env):
    env, _ = lock_env
    result = run(env, 'acquire_publish_lock "$LOCK" || exit $?\n'
                 'echo "1 10000" > "$LOCK.d/owner"\nrelease_publish_lock')
    assert result.returncode != 0
    assert Path(env['LOCK'] + '.d/owner').read_text() == '1 10000\n'
