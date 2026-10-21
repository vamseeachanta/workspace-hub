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
    (root / 'package.json').write_text(json.dumps({'name': package, 'version': version}))
    target = root / 'launcher'
    target.write_text('#!/bin/sh\nexit 99\n')
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
    assert f"npm uninstall --global --prefix {other.parent.parent}" in text
    assert next(r for r in rows if r.winner).winner == other


def test_missing_tools_requires_install_not_removal(planner, tmp_path):
    home, system = layout(tmp_path)
    text = planner.render(inventory(planner, home, system), home)
    assert 'MISSING claude' in text and 'MISSING codex' in text
    assert 'npm install --global --prefix' in text
    assert 'REMOVE' not in text


@pytest.mark.skipif(sys.platform == 'win32', reason='Requires POSIX shell or executable semantics')
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
    snap_runner.write_text('never run')
    snap_runner.chmod(0o755)
    for tool in ('claude', 'codex'):
        wrapper = system / 'snap/bin' / tool
        wrapper.parent.mkdir(parents=True, exist_ok=True)
        wrapper.symlink_to(snap_runner)
        meta = system / 'snap' / tool / 'current/meta/snap.yaml'
        meta.parent.mkdir(parents=True)
        meta.write_text(f'name: {tool}\nversion: "snap-fixture"\n')
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
    metadata.write_text(payload)
    rows = inventory(planner, home, system)
    assert rows[0].version == 'UNKNOWN'
    assert rows[0].prefix is None
    assert 'uninstall' not in planner.render(rows, home)


def test_unknown_copy_not_removed(planner, tmp_path):
    home, system = layout(tmp_path)
    npm(home / '.npm-global', 'codex')
    unknown = home / 'bin/codex'
    unknown.parent.mkdir()
    unknown.write_text('#!/bin/sh\nexit 99\n')
    unknown.chmod(0o755)
    text = planner.render(inventory(planner, home, system, str(unknown.parent)), home)
    assert 'MANUAL REVIEW' in text
    assert 'rm ' not in text


@pytest.mark.skipif(sys.platform == 'win32', reason='Requires POSIX shell or executable semantics')
def test_no_execution_network_or_writes(planner, tmp_path, monkeypatch, capsys):
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

    def read_only(file, mode='r', *args, **kwargs):
        assert not any(flag in mode for flag in 'wax+')
        return original_open(file, mode, *args, **kwargs)

    def io_read_only(file, mode='r', *args, **kwargs):
        assert not any(flag in mode for flag in 'wax+')
        return original_io_open(file, mode, *args, **kwargs)

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
    planner.main(['--home', str(home), '--system-root', str(system), '--path', ''])
    assert 'DRY RUN ONLY' in capsys.readouterr().out
    assert snapshot() == before


@pytest.mark.skipif(sys.platform == 'win32', reason='Requires POSIX shell or executable semantics')
def test_non_executable_and_broken_link_not_path_winners(planner, tmp_path):
    home, system = layout(tmp_path)
    folder = home / 'bin'
    folder.mkdir()
    (folder / 'codex').write_text('not executable')
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
    executable.write_text('#!/bin/sh\nexit 99\n')
    executable.chmod(0o755)
    rows = inventory(planner, home, system, str(executable.parent))
    assert len(rows) == 2
    native = next(row for row in rows if row.winner == executable)
    assert native.version == 'UNKNOWN'
    assert native.prefix is None
    assert f'MANUAL REVIEW claude: {executable}' in planner.render(rows, home)


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
    assert f'npm install --global --prefix {expected.parent.parent}' in text
    assert f'npm uninstall --global --prefix {default.parent.parent}' in text


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
