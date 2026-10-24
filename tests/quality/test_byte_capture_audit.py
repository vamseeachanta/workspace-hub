"""Independent syntax fixtures for the offline byte-capture inventory.

Expected sites are hand-counted literal calls; no target utility is executed.
Python 3.11 subprocess docs, Frequently Used Arguments, define text mode.
https://docs.python.org/3.11/library/subprocess.html#frequently-used-arguments
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_audit():
    spec = importlib.util.spec_from_file_location(
        "byte_capture_audit", ROOT / "scripts/quality/byte_capture_audit.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("option", [
    "text=True", "universal_newlines=True", "encoding='utf-8'", "errors='replace'",
])
def test_python_capture_aliases_and_rewrite(option):
    """One aliased capture and one write are present by literal inspection."""
    audit = load_audit()
    result = audit.inspect_python(
        f"import subprocess as sp\nr = sp.run(['git', 'show'], {option})\n"
        "p.write_bytes(r.stdout)\n"
    )
    assert [(s['line'], s['kind']) for s in result['sites']] == [(2, 'text capture')]
    assert result['rewrite']


def test_python_import_alias_and_binary_capture():
    audit = load_audit()
    result = audit.inspect_python(
        "from subprocess import check_output as capture\n"
        "a = capture(['git'], universal_newlines=True)\n"
        "b = capture(['git'], text=False)\n"
        "c = capture(['git'])\n"
    )
    assert [s['line'] for s in result['sites']] == [2]
    assert not result['rewrite']


def test_decode_defaults_and_explicit_decode_are_candidates():
    audit = load_audit()
    result = audit.inspect_python("a.decode()\nb.decode('utf-8')\nc.decode(errors='replace')\n")
    assert [s['kind'] for s in result['sites']] == [
        'default decode', 'explicit decode', 'default decode',
    ]


def test_injected_runner_and_unknown_options_are_not_silently_excluded():
    audit = load_audit()
    result = audit.inspect_python(
        "runner(command, text=True)\nsubprocess.run(command, **options)\n"
    )
    assert [s['kind'] for s in result['sites']] == ['text capture', 'dynamic options']


def test_shell_substitution_redirection_and_embedded_python():
    """Bash Command Substitution documents removal of trailing LF, not CR.

    https://www.gnu.org/software/bash/manual/html_node/Command-Substitution.html
    Each of the three literal lines has one candidate site.
    """
    audit = load_audit()
    result = audit.inspect_shell(
        'content="$(cat "$input")"\nprintf "%s" "$content" > "$output"\n'
        'content=`cat "$input"`\nsubprocess.run(cmd, text=True)\n'
    )
    assert result['rewrite']
    assert [s['line'] for s in result['sites']] == [1, 3, 4]


def test_syntax_errors_remain_visible():
    result = load_audit().inspect_python('def broken(:\n')
    assert result['error'] == 'NOT_EVALUATED: Python syntax'


def test_report_uses_codes_without_source_paths_or_snippets(tmp_path):
    """Opaque codes must also cover adversarial filenames, without a denylist."""
    audit = load_audit()
    script = tmp_path / 'scripts' / 'restricted-name.py'
    script.parent.mkdir()
    script.write_text("subprocess.run(command, text=True)\np.write_text(data)\n")
    rows, mapping = audit.inventory(tmp_path, ['scripts/restricted-name.py'])
    report = audit.render_report(rows)
    assert 'S001' in report
    assert 'restricted-name' not in report
    assert 'subprocess.run(command' not in report
    assert mapping['S001']['path'] == 'scripts/restricted-name.py'
    assert rows[0]['promise'] == 'NOT_EVALUATED'
    assert rows[0]['mode'] == 'rewrite candidate'


def test_report_is_deterministic_and_escapes_generated_fields(tmp_path):
    audit = load_audit()
    root = tmp_path / 'scripts'
    root.mkdir()
    (root / 'a.sh').write_text('echo "$(date)"\n')
    rows, _ = audit.inventory(tmp_path, ['scripts/a.sh'])
    assert audit.render_report(rows) == audit.render_report(rows)
    assert rows[0]['mode'] == 'read-only candidate'


def test_symlinks_cannot_escape_scan_root(tmp_path):
    audit = load_audit()
    (tmp_path / 'scripts').mkdir()
    target = tmp_path / 'outside.py'
    target.write_text('subprocess.run(cmd, text=True)\n')
    (tmp_path / 'scripts/link.py').symlink_to(target)
    rows, mapping = audit.inventory(tmp_path, ['scripts/link.py'])
    assert rows[0]['verdict'] == 'NOT_EVALUATED: path not followed'
    assert mapping['S001']['sha256'] is None


def test_guard_rejects_new_text_capture_in_protected_utility():
    audit = load_audit()
    source = 'def repair():\n    return subprocess.run(cmd, text=True)\n'
    assert audit.guard_source(source, []) == ['line 2: unreviewed text capture']


def test_guard_detects_content_reuse_of_metadata_wrapper():
    audit = load_audit()
    assert audit.guard_source("git_output(repo, ['show', blob])\n", []) == [
        'line 1: content command needs byte capture',
    ]


def test_guard_requires_exact_call_and_reason_and_rejects_stale_entries():
    audit = load_audit()
    source = 'def metadata():\n    return subprocess.run(cmd, text=True)\n'
    site = audit.inspect_python(source)['sites'][0]
    entry = {k: site[k] for k in ('scope', 'fingerprint')}
    entry['reason'] = 'Metadata output is parsed; it never becomes file content.'
    assert audit.guard_source(source, [entry]) == []
    assert audit.guard_source(source.replace('cmd', 'other'), [entry])
    assert audit.guard_source(source, [{**entry, 'reason': ''}])
    assert audit.guard_source('pass\n', [entry]) == ['stale allowlist entry']
    # Duplicating an allowed call must not create a second exception.
    assert audit.guard_source(source + source, [entry])


def test_guard_rejects_implicit_decode_and_dynamic_process_options():
    audit = load_audit()
    assert audit.guard_source('raw.decode()\nsubprocess.run(cmd, **options)\n', []) == [
        'line 1: unreviewed default decode',
        'line 2: unreviewed dynamic options',
    ]


def test_reviewed_byte_utilities_have_no_unreviewed_text_captures():
    audit = load_audit()
    assert audit.guard_repository(ROOT) == []


def test_guard_allows_direct_binary_content_capture():
    audit = load_audit()
    assert audit.guard_source(
        "subprocess.run(['git', 'show', blob], capture_output=True)\n", [],
    ) == []


@pytest.mark.parametrize('path', ['../outside.py', '/absolute.py', 'other/script.py'])
def test_scan_rejects_paths_outside_scripts(tmp_path, path):
    with pytest.raises(ValueError, match='repository-relative'):
        load_audit().inventory(tmp_path, [path])


def test_reviewed_generator_has_no_raw_byte_contract(tmp_path):
    audit = load_audit()
    relative = 'scripts/skills/generate_skills_index.py'
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text('subprocess.run(cmd, text=True)\noutput.write_text(rendered)\n')
    rows, _ = audit.inventory(tmp_path, [relative])
    assert rows[0]['promise'] == 'no'
    assert 'generated index' in rows[0]['verdict']


def test_git_enumeration_ignores_inherited_repository_bindings(tmp_path, monkeypatch):
    """Git ls-files --others must enumerate this disposable tree, not its caller.

    https://git-scm.com/docs/git-ls-files documents --others and -z. The only
    expected path is the single literal untracked fixture created below.
    """
    import os
    import subprocess

    audit = load_audit()
    root = tmp_path / 'tree'
    root.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    subprocess.run(['git', 'init', '--quiet', str(root)], check=True, env=env)
    fixture = root / 'scripts' / 'demo.py'
    fixture.parent.mkdir()
    fixture.write_text('pass\n')
    head = (root / '.git/HEAD').read_bytes()
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE'):
        monkeypatch.setenv(key, str(tmp_path / 'wrong-tree'))
    assert audit.script_paths(root) == ['scripts/demo.py']
    assert (root / '.git/HEAD').read_bytes() == head
    assert fixture.read_bytes() == b'pass\n'


def test_cli_refuses_mapping_inside_repository_before_writing(tmp_path):
    import subprocess
    import sys

    report = tmp_path / 'report.html'
    mapping = tmp_path / 'map.json'
    result = subprocess.run(
        [sys.executable, str(ROOT / 'scripts/quality/byte_capture_audit.py'),
         '--root', str(tmp_path), '--report', str(report), '--local-map', str(mapping)],
        capture_output=True, check=False,
    )
    assert result.returncode != 0
    assert b'local mapping must be outside the repository' in result.stderr
    assert not report.exists()
    assert not mapping.exists()


def test_guard_allows_imported_binary_run():
    audit = load_audit()
    assert audit.guard_source(
        "from subprocess import run\nrun(['git', 'show', blob], capture_output=True)\n", [],
    ) == []
