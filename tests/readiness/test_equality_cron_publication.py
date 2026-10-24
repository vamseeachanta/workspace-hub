"""Cron success requires publication success and a current health record.

Fixed clock noon UTC; 11:59:59 is older by one second, so cannot describe
this invocation. Exit 75 is the configured lock-contention status.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('optimized', [False, True])
@pytest.mark.parametrize('code,stamp,ok', [
    (1, None, False), (75, None, False), (0, None, False),
    (0, '2026-10-22T11:59:59Z', False),
    (0, '2026-10-22T12:00:00Z', True),
])
def test_cron_requires_current_publication(tmp_path, code, stamp, ok, optimized):
    root = tmp_path / 'repo'
    scripts = root / 'scripts/readiness'
    scripts.mkdir(parents=True)
    (scripts / 'lib').mkdir()
    shutil.copyfile(REPO / 'scripts/readiness/equality-matrix-cron.sh', scripts / 'equality-matrix-cron.sh')
    shutil.copyfile(REPO / 'scripts/readiness/lib/eq-seam.sh', scripts / 'lib/eq-seam.sh')
    (scripts / 'collect-equality.sh').write_text('exit 0\n')
    (root / 'scripts/notify.sh').write_text('exit 0\n')
    seam = tmp_path / 'evidence'
    seam.mkdir()
    body = ''
    if stamp:
        body = (f"printf '%s' '{{\"schema_version\":1,\"ts\":\"{stamp}\",\"phase\":\"publish\","
                '\"duration_s\":0,\"rc\":0}\' > "$EQ_STATE_DIR/publish-health.json"\n')
    (scripts / 'publish-equality.sh').write_text(body + f'exit {code}\n')
    bins = tmp_path / 'bin'
    bins.mkdir()
    for name in ('bash', 'dirname', 'git', 'python3'):
        (bins / name).symlink_to(shutil.which(name))
    for name, text in [('uv', 'exit 0'), ('date', 'echo 2026-10-22T12:00:00Z')]:
        path = bins / name
        path.write_text('#!/usr/bin/env bash\n' + text + '\n')
        path.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(PATH=str(bins), EQ_STATE_DIR=str(seam),
               PYTHONOPTIMIZE="1" if optimized else "")
    subprocess.run(['git', 'init', '-q', str(root)], env=env, check=True)
    result = subprocess.run(['bash', str(scripts / 'equality-matrix-cron.sh')],
                            env=env, capture_output=True, text=True, check=False, timeout=10)
    assert (result.returncode == 0) is ok, result.stderr
    assert ('equality-matrix-cron OK' in result.stdout) is ok
