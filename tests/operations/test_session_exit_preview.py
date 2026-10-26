"""Synthetic examples for issue #2256; expectations authored independently.

Issue numbers and exit codes below are example identifiers and CLI conventions,
not measured quantities. The expected Markdown is hand-transcribed from the
schema: supplied order, literal states, and explicit missing/empty observations.
"""

import io
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from operations import session_exit_preview as preview

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/operations/session_exit_preview.py"
INPUT = r'''{
  "issues": [
    {"number": 17, "state": "open"},
    {"number": 23, "state": "unknown"},
    {"number": 31},
    {"number": 47, "state": "closed"}
  ],
  "dirty_paths": ["docs/example.md", "scripts/example.py"],
  "next_steps": ["Review supplied changes", "Run supplied checks"]
}'''
EXPECTED = """# Exit preview

## Issues
- Issue 17: open
- Issue 23: unknown
- Issue 31: missing
- Issue 47: closed

## Dirty paths
- docs/example\\.md
- scripts/example\\.py

## Supplied next steps
- Review supplied changes
- Run supplied checks
"""


def test_literal_expected_markdown_and_determinism():
    assert preview.render_preview(INPUT) == EXPECTED
    reordered = json.dumps(dict(reversed(list(json.loads(INPUT).items()))))
    assert preview.render_preview(reordered) == EXPECTED
    assert preview.render_preview(INPUT) == EXPECTED


def test_missing_and_empty_are_distinct():
    assert preview.render_preview('{}') == """# Exit preview

## Issues
- missing

## Dirty paths
- missing

## Supplied next steps
- missing
"""
    assert preview.render_preview(
        '{"issues": [], "dirty_paths": [], "next_steps": []}'
    ) == """# Exit preview

## Issues
- none supplied

## Dirty paths
- none supplied

## Supplied next steps
- none supplied
"""


@pytest.mark.parametrize("raw,diagnostic", [
    ('', '$: invalid JSON'),
    ('{', '$: invalid JSON'),
    ('[]', '$: expected object'),
    ('null', '$: expected object'),
    ('{"untrusted-value": true}', '$: unknown field'),
    ('{"issues": null}', 'issues: expected array'),
    ('{"dirty_paths": "untrusted-value"}', 'dirty_paths: expected array'),
    ('{"next_steps": {}}', 'next_steps: expected array'),
    ('{"issues": [null]}', 'issues[]: expected object'),
    ('{"issues": [{}]}', 'issues[].number: required'),
    ('{"issues": [{"number": true}]}', 'issues[].number: expected positive integer'),
    ('{"issues": [{"number": 0}]}', 'issues[].number: expected positive integer'),
    ('{"issues": [{"number": -17}]}', 'issues[].number: expected positive integer'),
    ('{"issues": [{"number": 17.0}]}', 'issues[].number: expected positive integer'),
    ('{"issues": [{"number": "untrusted-value"}]}', 'issues[].number: expected positive integer'),
    ('{"issues": [{"number": 17, "labels": []}]}', 'issues[]: unknown field'),
    ('{"issues": [{"number": 17, "state": "approved"}]}', 'issues[].state: expected open, closed or unknown'),
    ('{"issues": [{"number": 17, "state": null}]}', 'issues[].state: expected open, closed or unknown'),
    ('{"issues": [{"number": 17, "state": []}]}', 'issues[].state: expected open, closed or unknown'),
    ('{"dirty_paths": [false]}', 'dirty_paths[]: expected nonempty single-line string'),
    ('{"next_steps": [17]}', 'next_steps[]: expected nonempty single-line string'),
    ('{"next_steps": [""]}', 'next_steps[]: expected nonempty single-line string'),
    ('{"next_steps": ["  "]}', 'next_steps[]: expected nonempty single-line string'),
    ('{"next_steps": ["untrusted-value\\nmore"]}', 'next_steps[]: expected nonempty single-line string'),
    ('{"next_steps": ["untrusted-value\\u001b"]}', 'next_steps[]: expected nonempty single-line string'),
    ('{"next_steps": ["untrusted-value\\u2028more"]}', 'next_steps[]: expected nonempty single-line string'),
    ('{"next_steps": ["\\ud800"]}', 'next_steps[]: expected nonempty single-line string'),
    ('{"next_steps": [], "next_steps": []}', '$: duplicate field'),
    ('{"issues": [{"number": 17, "number": 23}]}', '$: duplicate field'),
    ('{"untrusted-value": NaN}', '$: invalid JSON'),
    ('{"untrusted-value": Infinity}', '$: invalid JSON'),
])
def test_invalid_input_has_only_fixed_field_diagnostics(raw, diagnostic):
    with pytest.raises(preview.PreviewError) as exc:
        preview.render_preview(raw)
    assert str(exc.value) == diagnostic
    assert 'untrusted-value' not in str(exc.value)


@pytest.mark.parametrize("path", [
    '/absolute/example', 'C:/example', r'C:\example', r'\\server\share',
    r'\rooted', 'C:example', '../example', 'docs/../example', '.', './example',
    'docs//example', 'docs/', '', 'docs\\example',
])
def test_absolute_and_noncanonical_paths_rejected(path, tmp_path):
    # Runtime-generated absolute path also exercises the platform's native form.
    for supplied in (path, str(tmp_path / 'example')):
        with pytest.raises(preview.PreviewError) as exc:
            preview.render_preview(json.dumps({'dirty_paths': [supplied]}))
        assert str(exc.value).startswith('dirty_paths[]: ')
        if supplied:
            assert supplied not in str(exc.value)


def test_markdown_is_inert_and_supplied_order_is_preserved():
    raw = json.dumps({
        'next_steps': ['[review](https://example.invalid)', '<b>check</b>', '# title', '`code`'],
        'dirty_paths': ['docs/[example].md'],
    })
    assert preview.render_preview(raw) == r'''# Exit preview

## Issues
- missing

## Dirty paths
- docs/\[example\]\.md

## Supplied next steps
- \[review\]\(https://example\.invalid\)
- &lt;b&gt;check&lt;/b&gt;
- \# title
- \`code\`
'''


def test_no_process_network_or_file_access(monkeypatch, tmp_path, capsys):
    import builtins
    import socket

    def forbidden(*args, **kwargs):
        pytest.fail('preview attempted an external side effect')

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, 'stdin', io.StringIO(INPUT))
    with monkeypatch.context() as guard:
        for obj, names in (
            (subprocess, ('Popen', 'run', 'call', 'check_call', 'check_output')),
            (os, ('system', 'popen', 'posix_spawn', 'posix_spawnp', 'open')),
            (socket, ('socket', 'create_connection', 'getaddrinfo')),
            (builtins, ('open',)),
            (io, ('open',)),
        ):
            for name in names:
                if hasattr(obj, name):
                    guard.setattr(obj, name, forbidden)
        assert preview.main([]) == 0
    output = capsys.readouterr()
    assert output.out == EXPECTED
    assert output.err == ''
    assert list(tmp_path.iterdir()) == []


def cli(tmp_path, *args, raw=INPUT):
    return subprocess.run(
        [sys.executable, '-B', str(SCRIPT), *args], input=raw, text=True,
        capture_output=True, cwd=tmp_path, check=False,
        env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
    )


def test_cli_success_and_help(tmp_path):
    result = cli(tmp_path)
    assert (result.returncode, result.stdout, result.stderr) == (0, EXPECTED, '')
    help_result = cli(tmp_path, '--help', raw='')
    assert help_result.returncode == 0
    assert 'stdin' in help_result.stdout
    assert 'dirty_paths' in help_result.stdout
    assert help_result.stderr == ''
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize('args,raw,diagnostic', [
    ([], '{"dirty_paths": ["/untrusted-value"]}', 'dirty_paths[]:'),
    ([], '{', '$: invalid JSON'),
    (['--untrusted-value'], INPUT, 'arguments:'),
])
def test_cli_failure_never_echoes_values_or_emits_partial_markdown(
    tmp_path, args, raw, diagnostic,
):
    result = cli(tmp_path, *args, raw=raw)
    assert result.returncode != 0
    assert result.stdout == ''
    assert diagnostic in result.stderr
    assert 'untrusted-value' not in result.stderr
    assert 'Traceback' not in result.stderr
    assert list(tmp_path.iterdir()) == []


def test_cli_with_runtime_side_effect_control(tmp_path):
    # Audit events cover native process APIs as well as subprocess helpers.
    # File flags below are the standard library's symbolic open-mode contract.
    bootstrap = r"""
import os
import runpy
import subprocess
import sys


def guard(event, args):
    if event.startswith(('subprocess.', 'socket.', 'os.exec', 'os.spawn',
                         'os.posix_spawn', 'os.fork')) or event == 'os.system':
        raise RuntimeError('external action blocked')
    if event in {'os.mkdir', 'os.rename', 'os.remove', 'os.rmdir', 'os.link',
                 'os.symlink', 'os.truncate'}:
        raise RuntimeError('file mutation blocked')
    if event == 'open':
        _, mode, flags = args
        if (mode and any(char in mode for char in 'wax+')) or flags & (
            os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
        ):
            raise RuntimeError('file write blocked')


sys.addaudithook(guard)
try:
    subprocess.run([sys.executable, '-c', 'pass'], check=True)
except RuntimeError:
    pass
else:
    raise AssertionError('process control did not block')
script = sys.argv.pop()
runpy.run_path(script, run_name='__main__')
"""
    result = subprocess.run(
        [sys.executable, '-B', '-c', bootstrap, str(SCRIPT)],
        input=INPUT, text=True, capture_output=True, cwd=tmp_path, check=False,
        env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
    )
    assert (result.returncode, result.stdout, result.stderr) == (0, EXPECTED, '')
    assert list(tmp_path.iterdir()) == []


def test_cli_read_error_is_fixed_diagnostic(monkeypatch, capsys):
    class Unreadable:
        def read(self):
            raise OSError('untrusted-value')

    monkeypatch.setattr(sys, 'stdin', Unreadable())
    assert preview.main([]) != 0
    output = capsys.readouterr()
    assert output.out == ''
    assert output.err == 'stdin: unable to read text\n'
