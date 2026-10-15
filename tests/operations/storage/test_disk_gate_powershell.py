"""Exercise Windows disk thresholds using a mocked filesystem drive."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / 'scripts/operations/storage/disk_gate.ps1'
PWSH = shutil.which('pwsh')
pytestmark = pytest.mark.skipif(not PWSH, reason='pwsh not installed')


@pytest.mark.parametrize('used,free,inode,code', [
    (84, 16, 10, 0), (85, 15, 10, 10), (90, 10, 10, 4),
    (0.5, 0.5, 10, 4), (50, 50, 95, 4),
])
def test_windows_exit_codes(tmp_path, used, free, inode, code):
    conf = tmp_path / 'floors.conf'
    conf.write_text('C: warn_pct=85 block_pct=90 floor_gb=1\n')
    # Freeze the size at 100 GiB except for the independent free-floor case.
    command = f'''
function Get-PSDrive {{ [pscustomobject]@{{Used={used}GB;Free={free}GB;InodePct={inode}}} }}
& $env:GATE -Conf $env:CONF -Json
'''
    import os
    result = subprocess.run([PWSH, '-NoProfile', '-Command', command],
                            env={**os.environ, 'GATE': str(SCRIPT), 'CONF': str(conf)},
                            text=True, capture_output=True)
    assert result.returncode == code, result.stderr
    row = json.loads(result.stdout)
    assert set(row) == {'mount', 'size_kb', 'used_kb', 'free_kb', 'used_pct', 'inode_pct', 'state'}


@pytest.mark.parametrize('mode,code', [('missing', 2), ('unreadable', 4), ('mixed', 4)])
def test_windows_errors_and_multiple_mounts(tmp_path, mode, code):
    conf = tmp_path / 'floors.conf'
    if mode != 'missing':
        conf.write_text('C: warn_pct=85 block_pct=90 floor_gb=1\nD: warn_pct=85 block_pct=90 floor_gb=1\n')
    command = '''
function Get-PSDrive {
    param($Name, $PSProvider)
    if ($env:MODE -eq 'unreadable') { throw 'unreadable fixture' }
    if ($Name -eq 'C') { [pscustomobject]@{Used=85GB;Free=15GB} }
    else { [pscustomobject]@{Used=90GB;Free=10GB} }
}
& $env:GATE -Conf $env:CONF -Json
'''
    import os
    result = subprocess.run([PWSH, '-NoProfile', '-Command', command],
                            env={**os.environ, 'GATE': str(SCRIPT), 'CONF': str(conf), 'MODE': mode},
                            text=True, capture_output=True)
    assert result.returncode == code, result.stderr
