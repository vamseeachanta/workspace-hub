"""Synthetic filesystem examples; expected results follow PATH order by hand."""

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / 'scripts/maintenance/cli_consolidation_plan.py'


@pytest.fixture
def planner():
    spec = importlib.util.spec_from_file_location('cli_plan', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def npm(prefix, tool, version='fixture-version'):
    package = {'claude': '@anthropic-ai/claude-code', 'codex': '@openai/codex'}[tool]
    root = prefix / 'lib/node_modules' / package
    root.mkdir(parents=True)
    (root / 'package.json').write_text(json.dumps({'name': package, 'version': version}), encoding='utf-8', newline='\n')
    target = root / 'launcher'
    target.write_text('#!/bin/sh\nexit 99\n', encoding='utf-8', newline='\n')
    target.chmod(0o755)
    (prefix / 'bin').mkdir(exist_ok=True)
    launcher = prefix / 'bin' / tool
    launcher.symlink_to(target)
    return launcher


def layout(tmp_path):
    home, system = tmp_path / 'user', tmp_path / 'system'
    home.mkdir()
    system.mkdir()
    return home, system


def inventory(planner, home, system, path='', prefixes=()):
    return planner.inventory(home, path, system, prefixes)


def test_path_winner_and_alias_grouping(planner, tmp_path):
    """PATH A:B:A selects A; alias B resolves to A, hence one installation."""
    home, system = layout(tmp_path)
    first = npm(home / '.npm-global', 'codex')
    alias = home / 'bin/codex'
    alias.parent.mkdir()
    alias.symlink_to(first)
    rows = inventory(planner, home, system, os.pathsep.join(map(str, [alias.parent, first.parent, alias.parent])))
    assert len(rows) == 1
    assert rows[0].winner == alias
    assert set(rows[0].paths) == {alias, first}
    assert rows[0].version == 'fixture-version'
    assert 'REMOVE' not in planner.render(rows, home)


def test_user_npm_keep_system_remove(planner, tmp_path):
    """System first wins today; preferred user prefix is kept in the plan."""
    home, system = layout(tmp_path)
    user = npm(home / '.npm-global', 'claude', 'user-fixture')
    other = npm(system / 'usr/local', 'claude', 'system-fixture')
    rows = inventory(planner, home, system, str(other.parent))
    text = planner.render(rows, home)
    assert f'KEEP claude: {user}' in text
    assert f"npm uninstall --global --prefix {planner.q(other.parent.parent)}" in text
    assert next(r for r in rows if r.winner).winner == other


def test_missing_tools_requires_install_not_removal(planner, tmp_path):
    home, system = layout(tmp_path)
    text = planner.render(inventory(planner, home, system), home)
    assert 'MISSING claude' in text and 'MISSING codex' in text
    assert 'npm install --global --prefix' in text
    assert 'REMOVE' not in text


def test_nvm_and_explicit_prefix(planner, tmp_path):
    home, system = layout(tmp_path)
    old = npm(home / '.nvm/versions/node/fixture', 'codex')
    preferred = npm(home / 'custom prefix', 'codex')
    rows = inventory(planner, home, system, '', [preferred.parent.parent])
    text = planner.render(rows, home, [preferred.parent.parent])
    assert f'KEEP codex: {preferred}' in text
    assert 'version-manager npm' in text
    assert str(old.parent.parent) in text
    assert "'" in text  # Shell quoting preserves the space in the prefix.


def test_snap_wrappers_not_grouped_as_shared_snap_runner(planner, tmp_path):
    home, system = layout(tmp_path)
    snap_runner = system / 'usr/bin/snap'
    snap_runner.parent.mkdir(parents=True)
    snap_runner.write_text('never run', encoding='utf-8', newline='\n')
    snap_runner.chmod(0o755)
    for tool in ('claude', 'codex'):
        wrapper = system / 'snap/bin' / tool
        wrapper.parent.mkdir(parents=True, exist_ok=True)
        wrapper.symlink_to(snap_runner)
        meta = system / 'snap' / tool / 'current/meta/snap.yaml'
        meta.parent.mkdir(parents=True)
        meta.write_text(f'name: {tool}\nversion: "snap-fixture"\n', encoding='utf-8', newline='\n')
        npm(home / '.npm-global', tool)
    text = planner.render(inventory(planner, home, system, str(wrapper.parent)), home)
    assert text.count('snap-fixture') == 2
    assert 'sudo snap remove codex' in text
    assert 'sudo snap remove claude' in text


@pytest.mark.parametrize('payload', ['{', '[]', '{"name":"wrong","version":"bad"}'])
def test_invalid_metadata_is_unknown(planner, tmp_path, payload):
    home, system = layout(tmp_path)
    executable = npm(home / '.npm-global', 'codex')
    metadata = executable.resolve().parent / 'package.json'
    metadata.write_text(payload, encoding='utf-8', newline='\n')
    rows = inventory(planner, home, system)
    assert rows[0].version == 'UNKNOWN'
    assert rows[0].prefix is None
    assert 'uninstall' not in planner.render(rows, home)


def test_unknown_copy_not_removed(planner, tmp_path):
    home, system = layout(tmp_path)
    npm(home / '.npm-global', 'codex')
    unknown = home / 'bin/codex'
    unknown.parent.mkdir()
    unknown.write_text('#!/bin/sh\nexit 99\n', encoding='utf-8', newline='\n')
    unknown.chmod(0o755)
    text = planner.render(inventory(planner, home, system, str(unknown.parent)), home)
    assert 'MANUAL REVIEW' in text
    assert 'rm ' not in text


@pytest.mark.skipif(sys.platform == 'win32', reason='Requires POSIX shell or executable semantics')
@pytest.mark.parametrize('output_format', ['text', 'json'])
def test_no_execution_network_or_writes(planner, tmp_path, monkeypatch, capsys, output_format):
    """Before/after bytes and links match; all process/network/write APIs fail."""
    import builtins
    import io
    import socket
    import subprocess

    home, system = layout(tmp_path)
    npm(home / '.npm-global', 'claude')

    def snapshot():
        return {str(p): (os.readlink(p) if p.is_symlink() else p.read_bytes())
                for p in tmp_path.rglob('*') if p.is_file()}

    before = snapshot()

    def forbidden(*args, **kwargs):
        pytest.fail('Side effect attempted')

    original_open = builtins.open
    original_io_open = io.open

    def read_only(file, mode='r', buffering=-1, encoding='utf-8',
                  errors=None, newline=None, **kwargs):
        assert not any(flag in mode for flag in 'wax+')
        return original_open(file, mode, buffering, encoding=None if 'b' in mode else encoding,
                             errors=errors, newline=newline, **kwargs)

    def io_read_only(file, mode='r', buffering=-1, encoding='utf-8',
                     errors=None, newline=None, **kwargs):
        assert not any(flag in mode for flag in 'wax+')
        return original_io_open(file, mode, buffering, encoding=None if 'b' in mode else encoding,
                                errors=errors, newline=newline, **kwargs)

    monkeypatch.setattr(builtins, 'open', read_only)
    monkeypatch.setattr(io, 'open', io_read_only)
    for name in ('open', 'mkdir', 'unlink', 'remove', 'rename', 'replace', 'symlink', 'chmod'):
        monkeypatch.setattr(os, name, forbidden)
    for name in ('run', 'Popen', 'call', 'check_output', 'check_call'):
        monkeypatch.setattr(subprocess, name, forbidden)
    for name in ('system', 'popen', 'execv', 'execve', 'posix_spawn'):
        monkeypatch.setattr(os, name, forbidden)
    monkeypatch.setattr(socket, 'socket', forbidden)
    monkeypatch.setattr(Path, 'write_text', forbidden)
    monkeypatch.setattr(Path, 'write_bytes', forbidden)
    planner.main(['--home', str(home), '--system-root', str(system), '--path', '',
                  '--format', output_format])
    output = capsys.readouterr().out
    if output_format == 'text':
        assert 'DRY RUN ONLY' in output
    else:
        assert json.loads(output)['status'] == 'NOT_EVALUATED'
    assert snapshot() == before


@pytest.mark.skipif(sys.platform == 'win32', reason='Requires POSIX shell or executable semantics')
def test_non_executable_and_broken_link_not_path_winners(planner, tmp_path):
    home, system = layout(tmp_path)
    folder = home / 'bin'
    folder.mkdir()
    (folder / 'codex').write_text('not executable', encoding='utf-8', newline='\n')
    (folder / 'claude').symlink_to(folder / 'absent')
    rows = inventory(planner, home, system, str(folder))
    assert all(row.winner is None for row in rows)


def test_desktop_component_is_not_discovered(planner, tmp_path):
    home, system = layout(tmp_path)
    npm(home / 'desktop/resources', 'codex')
    assert inventory(planner, home, system) == []


def test_custom_prefix_on_path_metadata_is_discovered(planner, tmp_path):
    home, system = layout(tmp_path)
    executable = npm(home / 'custom', 'codex', 'custom-fixture')
    rows = inventory(planner, home, system, str(executable.parent))
    assert len(rows) == 1
    assert rows[0].version == 'custom-fixture'
    assert rows[0].prefix == executable.parent.parent


def test_regular_launcher_is_independent_of_adjacent_package(planner, tmp_path):
    home, system = layout(tmp_path)
    executable = npm(home / '.npm-global', 'claude')
    executable.unlink()
    executable.write_text('#!/bin/sh\nexit 99\n', encoding='utf-8', newline='\n')
    executable.chmod(0o755)
    rows = inventory(planner, home, system, str(executable.parent))
    assert len(rows) == 2
    native = next(row for row in rows if row.winner == executable)
    assert native.version == 'UNKNOWN'
    assert native.prefix is None
    assert f'MANUAL REVIEW claude: {planner.q(executable)}' in planner.render(rows, home)


def test_system_prefix_never_preferred(planner, tmp_path):
    home, system = layout(tmp_path)
    executable = npm(system / 'usr', 'codex')
    prefix = executable.parent.parent
    rows = inventory(planner, home, system, '', [prefix])
    text = planner.render(rows, home, [prefix])
    assert 'KEEP codex:' not in text
    assert 'uninstall' not in text


def test_incomplete_package_is_reported(planner, tmp_path):
    home, system = layout(tmp_path)
    executable = npm(home / '.npm-global', 'codex')
    executable.unlink()
    rows = inventory(planner, home, system)
    assert len(rows) == 1
    assert rows[0].winner is None
    assert rows[0].version == 'fixture-version'


def test_empty_path_element_means_current_directory(planner, tmp_path, monkeypatch):
    home, system = layout(tmp_path)
    executable = npm(home / '.npm-global', 'codex')
    monkeypatch.chdir(executable.parent)
    rows = inventory(planner, home, system, os.pathsep + str(system / 'absent'))
    assert rows[0].winner == executable


def test_custom_prefix_alias_includes_canonical_launcher(planner, tmp_path):
    home, system = layout(tmp_path)
    executable = npm(home / 'custom', 'codex')
    alias = home / 'bin/codex'
    alias.parent.mkdir()
    alias.symlink_to(executable)
    rows = inventory(planner, home, system, str(alias.parent))
    assert len(rows) == 1
    assert set(rows[0].paths) == {alias, executable}


@pytest.mark.parametrize('explicit', [False, True])
def test_path_inferred_user_prefix_is_kept(planner, tmp_path, explicit):
    home, system = layout(tmp_path)
    first = npm(home / '.npm-packages', 'codex')
    second = npm(home / 'another-prefix', 'codex')
    default = npm(home / '.npm-global', 'codex')
    prefixes = [second.parent.parent] if explicit else []
    path = os.pathsep.join(map(str, [first.parent, second.parent]))
    rows = inventory(planner, home, system, path, prefixes)
    text = planner.render(rows, home, prefixes)
    expected = second if explicit else first
    assert f'KEEP codex: {expected}' in text
    assert 'MISSING codex' not in text
    assert f'npm install --global --prefix {planner.q(expected.parent.parent)}' in text
    assert f'npm uninstall --global --prefix {planner.q(default.parent.parent)}' in text


def test_missing_wording_limits_metadata_claim(planner, tmp_path):
    home, system = layout(tmp_path)
    text = planner.render(inventory(planner, home, system), home)
    assert 'MISSING codex: metadata-matched preferred user npm installation' in text
    assert 'verified preferred' not in text


def test_windows_is_rejected_before_inventory(planner, monkeypatch, capsys):
    from types import SimpleNamespace

    def forbidden(*args, **kwargs):
        pytest.fail('Unsupported platform reached inventory')

    monkeypatch.setattr(planner, 'os', SimpleNamespace(name='nt', environ=os.environ))
    monkeypatch.setattr(planner, 'inventory', forbidden)
    with pytest.raises(SystemExit) as error:
        planner.main([])
    assert error.value.code == 2
    captured = capsys.readouterr()
    assert 'POSIX/Linux only' in captured.err
    assert captured.out == ''


def test_single_custom_path_prefix_avoids_duplicate_install(planner, tmp_path):
    home, system = layout(tmp_path)
    executable = npm(home / '.npm-packages', 'codex')
    rows = inventory(planner, home, system, str(executable.parent))
    text = planner.render(rows, home)
    assert f'KEEP codex: {executable}' in text
    assert 'MISSING codex' not in text
    assert f'--prefix {home / ".npm-global"} @openai/codex' not in text


def snap(system, tool='codex'):
    """Synthetic installed package; metadata can exist without a launcher."""
    root = system / 'snap' / tool / 'current'
    metadata = root / 'meta/snap.yaml'
    metadata.parent.mkdir(parents=True)
    metadata.write_text(f'name: {tool}\nversion: snap-fixture\n', encoding='utf-8', newline='\n')
    return root


def test_snap_without_launcher_is_still_an_installation(planner, tmp_path):
    """One npm root + one Snap root = two installations (issue 3964)."""
    home, system = layout(tmp_path)
    npm(home / '.npm-global', 'codex')
    root = snap(system)
    rows = inventory(planner, home, system)
    assert len(rows) == 2
    hidden = next(row for row in rows if row.identity == root)
    assert hidden.version == 'snap-fixture'
    assert hidden.winner is None
    assert 'sudo snap remove codex' in planner.render(rows, home)


def test_snap_alias_keeps_snap_identity(planner, tmp_path):
    """Alias -> Snap wrapper -> runner is one installation, not two."""
    home, system = layout(tmp_path)
    root = snap(system)
    runner = system / 'usr/bin/snap'
    runner.parent.mkdir(parents=True)
    runner.write_text('never run', encoding='utf-8', newline='\n')
    runner.chmod(0o755)
    wrapper = system / 'snap/bin/codex'
    wrapper.parent.mkdir(parents=True)
    wrapper.symlink_to(runner)
    alias = home / 'bin/codex'
    alias.parent.mkdir()
    alias.symlink_to(wrapper)
    rows = inventory(planner, home, system, str(alias.parent))
    assert len(rows) == 1
    assert rows[0].identity == root
    assert rows[0].winner == alias
    assert set(rows[0].paths) == {alias, wrapper}


def test_unknown_snap_metadata_remains_visible(planner, tmp_path):
    home, system = layout(tmp_path)
    root = snap(system)
    (root / 'meta/snap.yaml').write_text('name: unexpected\nversion: fixture\n', encoding='utf-8', newline='\n')
    rows = inventory(planner, home, system)
    assert len(rows) == 1
    assert rows[0].version == 'UNKNOWN'
    assert rows[0].snap_name is None
    assert 'sudo snap remove' not in planner.render(rows, home)


@pytest.mark.parametrize('file_alias', [False, True])
def test_snap_directory_alias_keeps_wrapper_identity(planner, tmp_path, file_alias):
    """Directory alias -> tool wrapper -> shared runner is one package."""
    home, system = layout(tmp_path)
    root = snap(system)
    runner = system / 'usr/bin/snap'
    runner.parent.mkdir(parents=True)
    runner.write_text('never run', encoding='utf-8', newline='\n')
    runner.chmod(0o755)
    wrapper = system / 'snap/bin/codex'
    wrapper.parent.mkdir(parents=True)
    wrapper.symlink_to(runner)
    directory = home / 'bin'
    directory.symlink_to(wrapper.parent, target_is_directory=True)
    alias = directory / 'codex'
    if file_alias:
        alias = home / '.local/bin/codex'
        alias.parent.mkdir(parents=True)
        alias.symlink_to(directory / 'codex')
    rows = inventory(planner, home, system, str(alias.parent))
    assert len(rows) == 1
    assert rows[0].identity == root
    assert rows[0].winner == alias
    assert {alias, directory / 'codex', wrapper} <= set(rows[0].paths)
    checks = planner.report(rows, home)['tools']['codex']['checks']
    assert checks['bounded_uniqueness'] == 'PASS'


@pytest.mark.parametrize('output_format', ['text', 'json'])
@pytest.mark.parametrize('launcher', [False, True])
def test_invalid_utf8_snap_metadata_is_unknown(
        planner, tmp_path, capsys, output_format, launcher):
    """Unreadable metadata retains the package, without authorizing removal."""
    home, system = layout(tmp_path)
    npm(home / '.npm-global', 'codex')
    root = snap(system)
    (root / 'meta/snap.yaml').write_bytes(b'name: codex\nversion: \xff\n')
    if launcher:
        wrapper = system / 'snap/bin/codex'
        wrapper.parent.mkdir(parents=True)
        wrapper.write_text('never run', encoding='utf-8', newline='\n')
        wrapper.chmod(0o755)
    rows = inventory(planner, home, system)
    unknown = next(row for row in rows if row.identity == root)
    assert unknown.version == 'UNKNOWN'
    assert unknown.snap_name is None
    assert 'sudo snap remove' not in planner.render(rows, home)
    planner.main(['--home', str(home), '--system-root', str(system), '--path', '',
                  '--format', output_format])
    output = capsys.readouterr().out
    if output_format == 'text':
        assert 'UNKNOWN' in output
        assert 'sudo snap remove' not in output
        assert 'MANUAL REVIEW codex:' in output
    else:
        codex = json.loads(output)['tools']['codex']
        assert codex['installation_count'] == 2
        assert codex['checks']['bounded_uniqueness'] == 'FAIL'
        assert any(row['metadata_version'] == 'UNKNOWN' for row in codex['installations'])


def test_report_paths_use_forward_slashes(planner):
    from pathlib import PureWindowsPath

    identity = PureWindowsPath('synthetic/package')
    command = identity / 'bin/codex'
    row = planner.Installation('codex', 'unknown', 'UNKNOWN', identity,
                               paths=[command], winner=command)
    result = planner.report([row], Path('synthetic'))['tools']['codex']['installations'][0]
    assert result['identity'] == 'synthetic/package'
    assert result['paths'] == ['synthetic/package/bin/codex']
    assert result['path_winner'] == 'synthetic/package/bin/codex'
    assert planner.q(command) == 'synthetic/package/bin/codex'


def test_report_is_conservative_for_single_user_install(planner, tmp_path):
    """One matching root and first PATH file satisfy only local checks."""
    home, system = layout(tmp_path)
    executable = npm(home / '.npm-global', 'codex')
    rows = inventory(planner, home, system, str(executable.parent))
    report = planner.report(rows, home)
    codex = report['tools']['codex']
    assert codex['installation_count'] == 1
    assert codex['checks'] == {
        'bounded_uniqueness': 'PASS',
        'preferred_user_npm': 'PASS',
        'supplied_path': 'PASS',
        'latest_release': 'NOT_EVALUATED',
        'fresh_shells': 'NOT_EVALUATED',
        'functionality': 'NOT_EVALUATED',
    }
    assert report['status'] == 'NOT_EVALUATED'
    assert codex['installations'][0]['identity'] == str(executable.resolve().parent)
    assert report['tools']['claude']['checks']['bounded_uniqueness'] == 'NOT_EVALUATED'


def test_report_duplicate_fails_even_when_path_is_correct(planner, tmp_path):
    """Correct PATH cannot hide the second independent Snap installation."""
    home, system = layout(tmp_path)
    executable = npm(home / '.npm-global', 'codex')
    snap(system)
    result = planner.report(inventory(planner, home, system, str(executable.parent)), home)
    checks = result['tools']['codex']['checks']
    assert checks['supplied_path'] == 'PASS'
    assert checks['bounded_uniqueness'] == 'FAIL'
    assert result['status'] == 'FAIL'


def test_report_wrong_path_fails(planner, tmp_path):
    home, system = layout(tmp_path)
    npm(home / '.npm-global', 'codex')
    other = npm(system / 'usr/local', 'codex')
    result = planner.report(inventory(planner, home, system, str(other.parent)), home)
    assert result['tools']['codex']['checks']['supplied_path'] == 'FAIL'


@pytest.mark.parametrize('state', ['unknown', 'no-path', 'missing'])
def test_report_incomplete_evidence_is_not_evaluated(planner, tmp_path, state):
    home, system = layout(tmp_path)
    if state != 'missing':
        executable = npm(home / '.npm-global', 'codex')
        if state == 'unknown':
            (executable.resolve().parent / 'package.json').write_text('{}', encoding='utf-8', newline='\n')
    rows = inventory(planner, home, system)
    checks = planner.report(rows, home)['tools']['codex']['checks']
    assert checks['supplied_path'] == 'NOT_EVALUATED'
    if state != 'no-path':
        assert checks['bounded_uniqueness'] == 'NOT_EVALUATED'


def test_report_honors_explicit_user_preference(planner, tmp_path):
    home, system = layout(tmp_path)
    default = npm(home / '.npm-global', 'codex')
    preferred = npm(home / 'custom', 'codex')
    prefixes = [preferred.parent.parent]
    rows = inventory(planner, home, system, str(default.parent), prefixes)
    report = planner.report(rows, home, prefixes)
    assert report['tools']['codex']['preferred_identity'] == str(preferred.resolve().parent)
    assert report['tools']['codex']['checks']['supplied_path'] == 'FAIL'


def test_json_cli_prints_parseable_report(planner, tmp_path, capsys):
    home, system = layout(tmp_path)
    planner.main(['--home', str(home), '--system-root', str(system), '--path', '',
                  '--format', 'json'])
    result = json.loads(capsys.readouterr().out)
    assert result['status'] == 'NOT_EVALUATED'
    assert result['tools']['codex']['installation_count'] == 0


def test_snap_aliases_do_not_merge_independent_runner_copy(planner, tmp_path):
    """A regular file pointing at no wrapper is a separate unknown command."""
    home, system = layout(tmp_path)
    snap(system)
    executable = home / 'bin/codex'
    executable.parent.mkdir()
    executable.write_text('independent binary', encoding='utf-8', newline='\n')
    rows = inventory(planner, home, system)
    assert len(rows) == 2
    assert planner.report(rows, home)['tools']['codex']['checks']['bounded_uniqueness'] == 'FAIL'


def test_link_cycle_is_not_a_snap_alias(planner, tmp_path):
    home, system = layout(tmp_path)
    first, second = home / 'first', home / 'second'
    first.symlink_to(second)
    second.symlink_to(first)
    assert planner.through_launcher(first, system / 'snap/bin/codex') is False


def test_relative_snap_alias_with_missing_wrapper_is_grouped(planner, tmp_path):
    """One Snap metadata root plus its broken alias is still one identity."""
    home, system = layout(tmp_path)
    root = snap(system)
    alias = home / 'bin/codex'
    alias.parent.mkdir()
    alias.symlink_to(Path('../../system/snap/bin/codex'))
    rows = inventory(planner, home, system, str(alias.parent))
    assert len(rows) == 1
    assert rows[0].identity == root
    assert rows[0].winner is None


def test_documented_report_matches_hand_counted_example(planner, tmp_path):
    """Issue 3964: npm + Snap = two roots; user npm wins but uniqueness fails.

    The guide gives the independently calculated expected count and statuses;
    package versions are synthetic labels and are not queried from a registry.
    """
    home, system = layout(tmp_path)
    executable = npm(home / '.npm-global', 'codex', 'user-fixture')
    snap(system)
    guide = SCRIPT.parents[2] / 'docs/ops/cli-consolidation.md'
    expected = json.loads(guide.read_text(encoding='utf-8').split('```json\n')[1].split('```')[0])
    result = planner.report(inventory(planner, home, system, str(executable.parent)), home)
    codex = result['tools']['codex']
    assert {key: codex[key] for key in expected} == expected


def test_known_system_only_install_is_not_preferred_user_npm(planner, tmp_path):
    """One system root satisfies bounded count but not the user-prefix policy."""
    home, system = layout(tmp_path)
    executable = npm(system / 'usr/local', 'codex')
    result = planner.report(inventory(planner, home, system, str(executable.parent)), home)
    checks = result['tools']['codex']['checks']
    assert checks['bounded_uniqueness'] == 'PASS'
    assert checks['preferred_user_npm'] == 'FAIL'
    assert checks['supplied_path'] == 'NOT_EVALUATED'
    assert result['status'] == 'FAIL'
