"""Disk gate contracts with isolated filesystem command fixtures."""
import json
import os
import re
from pathlib import Path
import subprocess
import time

import pytest

ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / 'scripts/operations/storage/disk_gate.sh'


@pytest.fixture
def gate(tmp_path):
    tools = tmp_path / 'bin'
    tools.mkdir()
    df = tools / 'df'
    df.write_text('''#!/bin/sh
if [ "$DF_BAD" = 1 ]; then echo unreadable; exit 0; fi
if [ "$DF_FAIL" = 1 ]; then exit 1; fi
case "$*" in
 *-Pi*) if [ "$INODE_FAIL" = 1 ]; then exit 1; fi
 if [ "$INODE_BAD" = 1 ]; then echo 'bad-inode-data'; exit 0; fi
 if [ "$INODE_COUNTER_BAD" = 1 ]; then echo 'Filesystem Inodes IUsed IFree IUse% Mounted'; echo 'disk broken 100 900 10% /'; exit 0; fi
 echo 'Filesystem Inodes IUsed IFree IUse% Mounted'; echo "disk 1000 100 900 ${INODE:-10}% /";;
 *) echo 'Filesystem 1024-blocks Used Available Capacity Mounted';
 echo "disk 104857600 52428800 ${FREE:-52428800} ${PCT:-50}% /";;
esac
''')
    df.chmod(0o755)
    du = tools / 'du'
    du.write_text('''#!/bin/sh
if [ "$DU_FAIL" = 1 ]; then exit 1; fi
printf x >> "$DU_CALLS"
printf '%s\\t%s\\n' "${DU_KB:-1024}" "$4"
''')
    du.chmod(0o755)
    conf = tmp_path / 'floors.conf'
    conf.write_text('/ warn_pct=85 block_pct=90 floor_gb=1\n')
    env = {**os.environ, 'PATH': f'{tools}:{os.environ["PATH"]}',
           'DU_CALLS': str(tmp_path / 'du-calls')}

    def run(*args, **variables):
        return subprocess.run(['bash', str(GATE), '--conf', str(conf), *args],
                              env={**env, **variables}, text=True, capture_output=True)
    return run, conf, tmp_path


@pytest.mark.parametrize('variables,code', [
    ({'PCT': '84'}, 0), ({'PCT': '85'}, 10), ({'PCT': '90'}, 4),
    ({'FREE': '100'}, 4), ({'INODE': '95'}, 4),
    ({'DF_BAD': '1'}, 4), ({'DF_FAIL': '1'}, 4),
    ({'INODE_COUNTER_BAD': '1'}, 4), ({'INODE_BAD': '1'}, 4), ({'INODE_FAIL': '1'}, 4),
])
def test_exit_table(gate, variables, code):
    run, _, _ = gate
    result = run(**variables)
    assert result.returncode == code, result.stderr + result.stdout


def test_missing_settings(gate):
    run, conf, _ = gate
    conf.rename(conf.with_suffix('.saved'))
    assert run().returncode == 2


def test_json_and_mount_selection(gate):
    run, conf, _ = gate
    conf.write_text('/ warn_pct=40 block_pct=90 floor_gb=1\n/data warn_pct=40 block_pct=50 floor_gb=1\n')
    result = run('--json')
    assert result.returncode == 4
    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert rows[0]['state'] == 'WARN'
    assert rows[1]['state'] == 'BLOCK'
    assert set(rows[0]) == {'mount', 'size_kb', 'used_kb', 'free_kb', 'used_pct', 'inode_pct', 'state'}
    assert run('--mount', '/').returncode == 10
    assert run('--mount', '/unknown').returncode == 2


@pytest.mark.parametrize('setting', ['warn_pct=x', 'warn_pct=95 block_pct=90', 'floor_gb=-1', 'block_pct=101'])
def test_invalid_settings(gate, setting):
    run, conf, _ = gate
    conf.write_text(f'/ {setting}\n')
    assert run().returncode == 2


def test_consumers_caps_cache_and_block(gate):
    run, conf, tmp = gate
    cache = tmp / 'cache'
    cache.mkdir()
    with conf.open('a') as stream:
        stream.write(f'cache uv {cache} cap_gb=1\n')
    result = run('--consumers', '--json', DU_KB='2097152')
    assert result.returncode == 10, result.stderr
    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert any(row.get('path') == str(cache) and row['state'] == 'WARN' for row in rows)
    normal = run()
    assert normal.returncode == 10
    assert str(cache) in normal.stdout
    calls = (tmp / 'du-calls').read_text()
    assert run('--consumers', DU_KB='1').returncode == 10
    assert (tmp / 'du-calls').read_text() == calls
    result = run('--json', PCT='90')
    assert result.returncode == 4
    assert str(cache) in result.stdout
    assert (tmp / 'du-calls').read_text() == calls  # starts use cached measurements only
    state = conf.with_name(conf.name + '.consumers.tsv')
    old = time.time() - 21601
    header, rows = state.read_text().split("\n", 1)
    _, signature = header.split("\t", 1)
    state.write_text(f"{int(old)}\t{signature}\n{rows}")
    assert run('--consumers', DU_KB='1').returncode == 0
    assert len((tmp / 'du-calls').read_text()) > len(calls)


def test_consumer_unknown_is_warning(gate):
    run, conf, tmp = gate
    with conf.open('a') as stream:
        stream.write(f'cache uv {tmp / "missing"} cap_gb=1\n')
    result = run('--consumers', '--json')
    assert result.returncode == 10
    assert 'UNKNOWN' in result.stdout


def test_tmp_age_counts_and_largest(gate):
    run, conf, tmp = gate
    tree = tmp / 'temporary'
    tree.mkdir()
    for i in range(7):
        folder = tree / f'old-{i}'
        folder.mkdir()
        old = time.time() - 3.5 * 86400
        os.utime(folder, (old, old))
    (tree / 'recent').mkdir()
    with conf.open('a') as stream:
        stream.write(f'tmp {tree} old_days=3 cap_gb=1\n')
    result = run('--consumers', '--json')
    assert result.returncode == 0, result.stderr
    rows = [json.loads(line) for line in result.stdout.splitlines()]
    old_row = next(row for row in rows if 'count=' in row.get('path', ''))
    assert 'count=7' in old_row['path']
    assert old_row['bytes'] == 7 * 1024 * 1024
    assert sum('/old-' in row.get('path', '') for row in rows) == 5


def test_du_failure_is_unknown(gate):
    run, conf, tmp = gate
    with conf.open('a') as stream:
        stream.write(f'cache uv {tmp} cap_gb=1\n')
    result = run('--consumers', '--json', DU_FAIL='1')
    assert result.returncode == 10
    assert json.loads(result.stdout.splitlines()[-1])['bytes'] is None


def test_zero_consumer_cap_warns(gate):
    run, conf, tmp = gate
    with conf.open('a') as stream:
        stream.write(f'cache uv {tmp} cap_gb=0\n')
    assert run('--consumers').returncode == 10


@pytest.mark.parametrize('records', [
    '/ floor_gb=1', '/ floor_gb=1\n/data floor_gb=1',
    '/ floor_gb=1\r\n', '/ floor_gb=1\r\n\r\n',
])
def test_settings_line_endings_block_full_disk(gate, records):
    run, conf, _ = gate
    conf.write_bytes(records.encode())
    result = run(PCT='99')
    assert result.returncode == 4, result.stdout + result.stderr
    assert result.stdout.count('BLOCK') == records.count('floor_gb')


def extract_start_helper(readme):
    blocks = re.findall(r'^```bash[ \t]*\n(.*?)^```[ \t]*$', readme, re.M | re.S)
    matches = [block for block in blocks
               if 'disk_gate.sh --conf' in block
               and re.search(r'^case \$rc in\s*\n\s*0\|10\)', block, re.M)]
    if len(matches) != 1:
        raise ValueError(f'expected one disk gate start-helper block; found {len(matches)}')
    return matches[0]


def test_start_helper_selection_ignores_earlier_bash_block(tmp_path):
    readme = (GATE.parent / 'README.md').read_text()
    copy = tmp_path / 'README.md'
    # Keep the decoy under the same heading: selection must depend on content.
    copy.write_text(readme.replace('## Disk gate\n',
                                  '## Disk gate\n\n```bash\nprintf decoy\n```\n', 1))
    snippet = extract_start_helper(copy.read_text())
    assert 'disk_gate.sh --conf' in snippet
    assert 'case $rc in' in snippet
    assert '0|10)' in snippet
    assert 'printf decoy' not in snippet


@pytest.mark.parametrize('count', [0, 2])
def test_start_helper_selection_requires_exactly_one_match(count):
    block = "```bash\nbash scripts/operations/storage/disk_gate.sh --conf \"$CONF\"\ncase $rc in\n  0|10) ;;\nesac\n```\n"
    with pytest.raises(ValueError, match=f'expected one disk gate start-helper block; found {count}'):
        extract_start_helper(block * count)


def test_combined_storage_readme_structure_and_exit_codes():
    readme = (GATE.parent / 'README.md').read_text()
    assert readme.startswith('# Storage operations\n')
    assert [line for line in readme.splitlines() if line.startswith('## ')] == [
        '## Worktree location guard', '## Disk gate']
    assert '| 4 | Space below the floor' in readme
    assert '| 4 | A disk reaches its block percentage' in readme
    assert 'exit 20' not in readme.lower()


@pytest.mark.parametrize('code', [0, 10, 4, 2, 1, 126, 127, 124, 137, 130, 143])
def test_documented_start_helper_allows_only_ok_or_warn(tmp_path, code):
    readme = (GATE.parent / 'README.md').read_text()
    snippet = extract_start_helper(readme)
    stub = tmp_path / 'scripts/operations/storage/disk_gate.sh'
    stub.parent.mkdir(parents=True)
    stub.write_text(f'#!/bin/sh\nexit {code}\n')
    result = subprocess.run(['bash', '-c', snippet + '\nprintf "START\\n"'],
                            cwd=tmp_path, text=True, capture_output=True,
                            env={**os.environ, 'CONF': 'settings', 'job': 'example',
                                 'mount': 'disk', 'used_pct': '99', 'free_gb': '0'})
    assert ('START' in result.stdout) == (code in (0, 10))
    assert result.returncode == (0 if code in (0, 10) else code)


@pytest.mark.parametrize('order', [('/', '/data'), ('/data', '/')])
def test_block_outranks_warning(gate, order):
    run, conf, tmp = gate
    conf.write_text(''.join(f'{mount} warn_pct=40 block_pct={50 if mount == "/data" else 90}\n'
                            for mount in order) + f'cache uv {tmp} cap_gb=0\n')
    assert run('--consumers').returncode == 4


def test_hosted_storage_step_is_present_once():
    workflow = (ROOT / '.github/workflows/baseline-check.yml').read_text()
    assert workflow.count('uv run python -m pytest tests/operations/storage -v --tb=short') == 1


@pytest.mark.parametrize('kind', ['cache', 'tmp'])
def test_unterminated_final_consumer_record(gate, kind):
    run, conf, tmp = gate
    cache = tmp / 'consumer'
    cache.mkdir()
    record = f'cache uv {cache} cap_gb=0' if kind == 'cache' else f'tmp {cache} cap_gb=0'
    conf.write_text('/ floor_gb=1\n' + record)
    result = run('--consumers', '--json', DU_KB='20971520')
    assert result.returncode == 10
    assert any(row.get('path') == str(cache) for row in map(json.loads, result.stdout.splitlines()))
