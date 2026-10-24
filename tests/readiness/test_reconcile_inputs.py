"""Offline reconciliation examples: three remote commits minus zero local commits = three behind."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


def executable(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('#!/usr/bin/env bash\n' + text)
    path.chmod(0o755)


def git(root, env, *args):
    return subprocess.run(['git', '-C', str(root), *args], env=env, check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def fixture(tmp_path):
    bins = tmp_path / 'bin'
    bins.mkdir()
    # Allow only these commands; no real provider, hardware or network probes.
    for name in ('bash', 'dirname', 'basename', 'git', 'tr', 'sed', 'grep',
                 'awk', 'python3', 'cat'):
        source = shutil.which(name)
        if source:
            (bins / name).symlink_to(source)
    executable(bins / 'hostname', 'echo fixture\n')
    executable(bins / 'date', 'echo 2026-10-22T12:00:00Z\n')
    home = tmp_path / 'user'
    home.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(PATH=str(bins), HOME=str(home), RECONCILE_MACHINE='fixture',
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CONFIG_COUNT='2', GIT_CONFIG_KEY_0='user.name',
               GIT_CONFIG_VALUE_0='fixture', GIT_CONFIG_KEY_1='user.email',
               GIT_CONFIG_VALUE_1='fixture@invalid')
    bare = tmp_path / 'origin.git'
    root = tmp_path / 'checkouts' / 'repo'
    root.mkdir(parents=True)
    git(tmp_path, env, 'init', '--bare', '-b', 'main', str(bare))
    git(root, env, 'init', '-b', 'main')
    for rel in ('scripts/readiness/reconcile-ecosystem.sh',
                'scripts/readiness/lib/machine-identity.sh'):
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / rel, target)
    git(root, env, 'add', '.')
    git(root, env, 'commit', '-m', 'initial')
    git(root, env, 'remote', 'add', 'origin', str(bare))
    git(root, env, 'push', '-u', 'origin', 'main')
    return root, bare, bins, home, env


def run(fixture, *args):
    root, _, _, _, env = fixture
    return subprocess.run(['bash', str(root / 'scripts/readiness/reconcile-ecosystem.sh'),
                           '--json', *args], env=env, capture_output=True, text=True, check=False, timeout=30)


def uv_at(path, payload='{"fixture":{"compute":"CONFORMS"}}', rc=0):
    executable(path, f"printf '%s\\n' '{payload}'\nexit {rc}\n")


def test_user_level_uv_off_path(fixture):
    uv_at(fixture[3] / '.local/bin/uv', '{"fixture":{"compute":"BELOW-BASELINE"}}')
    result = run(fixture)
    assert result.returncode == 0, result.stderr
    assert 'BELOW-BASELINE' not in result.stdout  # existing human remediation text
    assert len(json.loads(result.stdout)['plan']) == 1


def test_missing_uv_cannot_emit_plan(fixture):
    result = run(fixture)
    assert result.returncode != 0
    assert 'cannot read equality verdicts' in result.stderr
    assert 'plan' not in result.stdout


@pytest.mark.parametrize('payload,rc', [('', 1), ('garbage', 0), ('{}', 0),
                                      ('{"fixture":{}}', 0)])
def test_unreadable_matrix_cannot_emit_plan(fixture, payload, rc):
    uv_at(fixture[2] / 'uv', payload, rc)
    result = run(fixture)
    assert result.returncode != 0
    assert 'cannot read equality verdicts' in result.stderr
    assert not result.stdout


def test_fetch_discovers_three_commits(fixture, tmp_path):
    root, bare, bins, _, env = fixture
    uv_at(bins / 'uv')
    writer = tmp_path / 'writer'
    git(tmp_path, env, 'clone', str(bare), str(writer))
    for i in range(3):
        git(writer, env, 'commit', '--allow-empty', '-m', f'advance {i}')
    git(writer, env, 'push', 'origin', 'main')
    assert git(root, env, 'rev-list', '--count', 'HEAD..origin/main') == '0'
    result = run(fixture)
    assert result.returncode == 0, result.stderr
    assert 'behind upstream by 3' in result.stdout
    assert json.loads(result.stdout)['refs'] == 'fetched'


def test_no_fetch_banner(fixture):
    uv_at(fixture[2] / 'uv')
    result = run(fixture, '--no-fetch')
    assert result.returncode == 0, result.stderr
    assert 'possibly stale refs' in result.stderr
    assert json.loads(result.stdout)['refs'] == 'not-fetched'


def test_unreachable_remote_is_incomplete(fixture):
    root, _, bins, home, env = fixture
    uv_at(bins / 'uv')
    git(root, env, 'remote', 'set-url', 'origin', str(home / 'absent.git'))
    result = run(fixture)
    assert result.returncode != 0
    report = json.loads(result.stdout)
    assert report['complete'] is False
    assert any('fetch failed' in x['action'] for x in report['plan'])


def test_empty_map_is_invalid_when_python_optimized(fixture):
    fixture[4]['PYTHONOPTIMIZE'] = '1'
    uv_at(fixture[2] / 'uv', '{"fixture":{}}')
    result = run(fixture)
    assert result.returncode != 0
    assert not result.stdout
