"""Offline publication uses only a fixture bare remote and fixed UTC timestamps."""
import json
import os
import shutil
import subprocess
from pathlib import Path

from test_reconcile_inputs import executable, git

REPO = Path(__file__).resolve().parents[2]
PUBLISH = REPO / 'scripts/readiness/publish-equality.sh'


def prepare(fixture):
    root, _, bins, home, env = fixture
    for name in ('cp', 'mktemp', 'rmdir', 'mkdir', 'timeout', 'sleep', 'mv', 'rm'):
        (bins / name).symlink_to(shutil.which(name))
    executable(bins / 'date', 'case "$*" in *+%s*) echo 10000;; '
               '*) echo 2026-10-22T12:00:00Z;; esac\n')
    seam = home / 'evidence'
    seam.mkdir()
    (seam / 'equality-fixture.yaml').write_text(
        'generated_at: "2026-10-22T12:00:00Z"\nmachine: fixture\n')
    env.update(EQ_STATE_DIR=str(seam), EQ_MACHINE='fixture')
    return root, seam, env


def publish(root, env):
    return subprocess.run(['bash', str(PUBLISH), '--repo', str(root),
                           '--max-attempts', '1', '--retry-delay-seconds', '0'],
                          env=env, capture_output=True, text=True, check=False, timeout=30)


def test_absent_flock_publishes_and_records_health(fixture):
    root, seam, env = prepare(fixture)
    result = publish(root, env)
    assert result.returncode == 0, result.stderr
    health = json.loads((seam / 'publish-health.json').read_text())
    assert health['ts'] == '2026-10-22T12:00:00Z'
    assert health['rc'] == 0
    assert 'generated_at' in git(root, env, 'show', 'origin/main:.claude/state/equality-fixture.yaml')
    assert not (root / '.git/equality-publish.d').exists()


def test_failure_does_not_record_success(fixture):
    root, seam, env = prepare(fixture)
    git(root, env, 'remote', 'set-url', 'origin', str(seam / 'absent'))
    result = publish(root, env)
    assert result.returncode == 1
    assert not (seam / 'publish-health.json').exists()
    assert not (root / '.git/equality-publish.d').exists()


def test_contention_is_not_success(fixture):
    root, seam, env = prepare(fixture)
    lock = root / '.git/equality-publish.d'
    lock.mkdir()
    (lock / 'owner').write_text(f'{os.getpid()} 10000\n')
    assert publish(root, env).returncode == 75
    assert not (seam / 'publish-health.json').exists()
