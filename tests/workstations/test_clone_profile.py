"""Explicit clone profiles use disposable fixtures, never a real network source."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts/workstations/clone_profile.py'


@pytest.fixture
def mod():
    spec = importlib.util.spec_from_file_location('clone_profile', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPT.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


@pytest.fixture
def inputs(tmp_path):
    registry = tmp_path / 'registry.yaml'
    registry.write_text(yaml.safe_dump({'machines': {'dev-primary': {
        'repos': ['digitalmodel', 'assetutilities', 'heavy-store'],
        'tier1_baseline': {'required': ['digitalmodel', 'assetutilities']}}}}))
    urls = tmp_path / 'repos.conf'
    urls.write_text('digitalmodel=https://example.invalid/digitalmodel.git\n'
                    'assetutilities=git@example.invalid:owner/assetutilities.git\n'
                    'heavy-store=https://example.invalid/heavy.git\n')
    return dict(repo='digitalmodel', profile='lean', destination=tmp_path / 'digitalmodel',
                include_dirs=['src', 'tests/unit'], branch='main', machine='dev-primary',
                registry=registry, repos_config=urls)


def test_dry_run_has_no_git_or_filesystem_mutation(mod, inputs, monkeypatch):
    monkeypatch.setattr(mod.subprocess, 'run', lambda *a, **k: pytest.fail('Git called'))
    before = sorted(inputs['destination'].parent.iterdir())
    plan = mod.build_plan(**inputs)
    assert plan['profile'] == 'lean'
    assert plan['membership_source'] == 'machines.dev-primary.tier1_baseline.required'
    assert plan['core_repositories'] == ['digitalmodel', 'assetutilities']
    assert '--filter=blob:none' in plan['commands'][1]
    assert '--no-checkout' in plan['commands'][1]
    assert '--no-recurse-submodules' in plan['commands'][1]
    assert sorted(inputs['destination'].parent.iterdir()) == before
    assert not inputs['destination'].exists()


@pytest.mark.parametrize('value', ['main','A'*40,'a'*39,'a'*41,'../main'])
def test_expected_revision_validation(mod,inputs,value):
    with pytest.raises(ValueError,match='expected head'):
        mod.build_plan(**inputs,expected_head=value)


def test_expected_revision_preflight_stops_before_any_clone(mod,inputs):
    plan=mod.build_plan(**inputs,expected_head='b'*40);calls=[]
    with pytest.raises(ValueError,match='advertised branch'):
        mod.execute(plan,run=fake_runner(plan,calls))
    assert len(calls)==1 and not inputs['destination'].exists()


@pytest.mark.parametrize('observed',['b'*40,'a'*40])
def test_expected_revision_checked_before_checkout(mod,inputs,observed):
    plan=mod.build_plan(**inputs,expected_head='a'*40);calls=[];base=fake_runner(plan,calls)
    def run(cmd,**kwargs):
        if 'rev-parse' in cmd:
            calls.append((cmd,kwargs));return subprocess.CompletedProcess(cmd,0,observed+'\n','')
        return base(cmd,**kwargs)
    if observed!='a'*40:
        with pytest.raises(ValueError,match='cloned revision'):
            mod.execute(plan,run=run)
        assert not any('checkout' in c for c,_ in calls);assert Path(plan['destination']).exists()
    else:
        assert mod.execute(plan,run=run)['status']=='created'


@pytest.mark.parametrize('path', ['.agents', '.codex', '.claude', 'config/.defaults'])
def test_hidden_workflow_directories_are_explicit_sparse_inputs(mod, inputs, path):
    inputs['include_dirs'] = ['src', path]
    plan = mod.build_plan(**inputs)
    assert path in plan['include_directories']
    assert plan['commands'][-2][-1] == path
    assert not inputs['destination'].exists()


@pytest.mark.parametrize('path', ['.GIT', 'src/.Git', '.agents/../config', '.agents/-option'])
def test_hidden_paths_keep_git_metadata_traversal_and_option_guards(mod, inputs, path):
    inputs['include_dirs'] = [path]
    with pytest.raises(ValueError, match='sparse directory'):
        mod.build_plan(**inputs)


def test_hidden_workflow_support_does_not_relax_branch_validation(mod, inputs):
    inputs['branch'] = '.agents'
    with pytest.raises(ValueError, match='branch'):
        mod.build_plan(**inputs)


@pytest.mark.parametrize('kind', ['empty', 'file', 'repo', 'dangling'])
def test_any_existing_destination_is_rejected(mod, inputs, kind):
    target = inputs['destination']
    if kind == 'file':
        target.write_text('held')
    elif kind == 'dangling':
        target.symlink_to(target.parent / 'absent', target_is_directory=True)
    else:
        target.mkdir()
        if kind == 'repo':
            (target / '.git/objects/pack').mkdir(parents=True)
            (target / '.git/objects/pack/fixture.promisor').write_text('')
    with pytest.raises(ValueError):
        mod.build_plan(**inputs)
    assert os.path.lexists(target)


@pytest.mark.parametrize('path', ['../data', '/data', 'C:/data', '-src', 'src/../data',
                                  'src/*', '.', '.git', 'src/.git', 'src\nname', 'src\\data'])
def test_unsafe_sparse_paths_are_rejected(mod, inputs, path):
    inputs['include_dirs'] = [path]
    with pytest.raises(ValueError):
        mod.build_plan(**inputs)


@pytest.mark.parametrize('branch', ['--upload-pack=x', 'a..b', 'a@{b', 'a//b', 'a b'])
def test_unsafe_branches_are_rejected(mod, inputs, branch):
    inputs['branch'] = branch
    with pytest.raises(ValueError):
        mod.build_plan(**inputs)


def test_lean_requires_dirs_heavy_rejects_dirs_and_membership_is_required(mod, inputs):
    inputs['include_dirs'] = []
    with pytest.raises(ValueError):
        mod.build_plan(**inputs)
    inputs['profile'] = 'heavy'
    heavy = mod.build_plan(**inputs)
    assert '--filter=blob:none' not in heavy['commands'][0]
    assert '--no-checkout' in heavy['commands'][0]
    assert len(heavy['commands']) == 1  # explicit heavy object store; no checkout/hydration
    inputs['include_dirs'] = ['src']
    with pytest.raises(ValueError):
        mod.build_plan(**inputs)
    inputs.update(repo='heavy-store', destination=inputs['destination'].parent / 'heavy-store', include_dirs=[])
    with pytest.raises(ValueError):
        mod.build_plan(**inputs)


def fake_runner(plan, calls, *, filter_supported=True, clone_warning='', fail_step=None):
    def run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        step = len(calls)
        if 'ls-remote' in cmd:
            return subprocess.CompletedProcess(cmd, 0, 'a' * 40 + '\trefs/heads/main\n',
                'packet: git< fetch=shallow filter\n' if filter_supported else 'packet: git< fetch=shallow\n')
        if 'clone' in cmd:
            target = Path(plan['destination'])
            (target / '.git/objects/pack').mkdir(parents=True)
            (target / '.git/objects/pack/fixture.promisor').write_text('')
        output = ('remote.origin.promisor true\nremote.origin.partialclonefilter blob:none\n' if 'config' in cmd
                  else 'tree\n' if 'cat-file' in cmd else '')
        return subprocess.CompletedProcess(cmd, 1 if step == fail_step else 0, output, clone_warning if 'clone' in cmd else '')
    return run


def test_unsupported_filter_stops_before_destination_and_clone(mod, inputs):
    plan = mod.build_plan(**inputs)
    calls = []
    with pytest.raises(ValueError, match='filter'):
        mod.execute(plan, run=fake_runner(plan, calls, filter_supported=False))
    assert len(calls) == 1
    assert not inputs['destination'].exists()


@pytest.mark.parametrize('warning', ['warning: filtering not recognized by server, ignoring',
                                     'warning: server does not support filter'])
def test_filter_rejection_retains_destination_without_checkout(mod, inputs, warning):
    plan = mod.build_plan(**inputs)
    calls = []
    with pytest.raises(ValueError, match='filter'):
        mod.execute(plan, run=fake_runner(plan, calls, clone_warning=warning))
    assert inputs['destination'].exists()
    assert len(calls) == 2


def test_partial_clone_failure_retains_target_and_sibling(mod, inputs):
    sibling = inputs['destination'].parent / 'held-original'
    sibling.write_bytes(b'original')
    plan = mod.build_plan(**inputs)
    calls = []
    with pytest.raises(ValueError):
        mod.execute(plan, run=fake_runner(plan, calls, fail_step=2))
    assert inputs['destination'].exists()
    assert sibling.read_bytes() == b'original'
    assert len(calls) == 2


def test_inherited_git_bindings_are_removed_and_no_hydration_helpers(mod, inputs, monkeypatch):
    monkeypatch.setenv('GIT_DIR', '/held/original/.git')
    monkeypatch.setenv('GIT_WORK_TREE', '/held/original')
    monkeypatch.setenv('GIT_CONFIG_COUNT', '1')
    plan = mod.build_plan(**inputs)
    calls = []
    mod.execute(plan, run=fake_runner(plan, calls))
    assert len(calls) == 7
    for cmd, kwargs in calls:
        env = kwargs['env']
        assert 'GIT_DIR' not in env and 'GIT_WORK_TREE' not in env and 'GIT_CONFIG_COUNT' not in env
        assert env['GIT_LFS_SKIP_SMUDGE'] == '1'
        assert env['GIT_TERMINAL_PROMPT'] == '0'
        assert kwargs['timeout'] <= 120
        assert 'submodule' not in cmd and 'lfs' not in cmd
        if 'cat-file' in cmd:
            assert env['GIT_NO_LAZY_FETCH'] == '1'


def test_destination_race_is_rejected_without_git_clone(mod, inputs):
    plan = mod.build_plan(**inputs)
    calls = []
    runner = fake_runner(plan, calls)
    def race(cmd, **kwargs):
        result = runner(cmd, **kwargs)
        if 'ls-remote' in cmd:
            inputs['destination'].mkdir()
            (inputs['destination'] / 'held').write_text('preserve')
        return result
    with pytest.raises(ValueError):
        mod.execute(plan, run=race)
    assert (inputs['destination'] / 'held').read_text() == 'preserve'
    assert len(calls) == 1


def test_parent_redirect_is_rejected(mod, inputs):
    alias = inputs['destination'].parent / 'alias'
    alias.symlink_to(inputs['destination'].parent, target_is_directory=True)
    inputs['destination'] = alias / 'digitalmodel'
    with pytest.raises(ValueError):
        mod.build_plan(**inputs)


def test_cli_dry_run_reads_existing_registry_and_outputs_plan(inputs):
    result = subprocess.run([sys.executable, str(SCRIPT), 'digitalmodel', '--profile', 'lean',
        '--destination', str(inputs['destination']), '--include-dir', 'src', '--dry-run',
        '--registry', str(inputs['registry']), '--repos-config', str(inputs['repos_config'])],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['dry_run'] is True
    assert not inputs['destination'].exists()


def test_profile_dispatch_precedes_sync_helper_and_dry_run_is_read_only(inputs, tmp_path):
    bash = Path('C:/Program Files/Git/bin/bash.exe')
    if not bash.exists():
        pytest.skip('Git Bash unavailable')
    hub = tmp_path / 'entry-fixture'
    scripts = hub / 'scripts'
    helper_dir = scripts / 'workstations'
    helper_dir.mkdir(parents=True)
    shutil.copyfile(ROOT / 'scripts/repository_sync', scripts / 'repository_sync')
    for name in ['clone_profile.py', 'repo_footprint.py']:
        shutil.copyfile(SCRIPT.parent / name, helper_dir / name)
    marker = tmp_path / 'sync-helper-sourced'
    (scripts / 'repository_sync-auto').write_text('echo unexpected > "' + marker.as_posix() + '"\nexit 99\n')
    env = dict(os.environ, REPOSITORY_SYNC_PYTHON=sys.executable.replace('\\', '/'),
               PYTHONDONTWRITEBYTECODE='1')
    result = subprocess.run([str(bash), str(scripts / 'repository_sync'), 'clone', 'digitalmodel',
        '--profile', 'lean', '--destination', str(inputs['destination']), '--include-dir', 'src',
        '--dry-run', '--registry', str(inputs['registry']), '--repos-config', str(inputs['repos_config'])],
        env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['dry_run'] is True
    assert not marker.exists()
    assert not inputs['destination'].exists()
    assert not list(helper_dir.rglob('__pycache__'))


def test_direct_cli_dry_run_does_not_create_bytecode(inputs, tmp_path):
    helpers = tmp_path / 'bytecode-probe'
    helpers.mkdir()
    for name in ['clone_profile.py', 'repo_footprint.py']:
        shutil.copyfile(SCRIPT.parent / name, helpers / name)
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONDONTWRITEBYTECODE'}
    result = subprocess.run([sys.executable, str(helpers / 'clone_profile.py'), 'digitalmodel',
        '--profile', 'lean', '--destination', str(inputs['destination']), '--include-dir', 'src',
        '--dry-run', '--registry', str(inputs['registry']), '--repos-config', str(inputs['repos_config'])],
        env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert not list(helpers.rglob('__pycache__'))


def test_missing_selected_source_directory_stops_before_checkout(mod, inputs):
    plan = mod.build_plan(**inputs)
    calls = []
    runner = fake_runner(plan, calls)
    def missing(cmd, **kwargs):
        result = runner(cmd, **kwargs)
        if 'cat-file' in cmd:
            return subprocess.CompletedProcess(cmd, 1, '', 'missing')
        return result
    with pytest.raises(ValueError):
        mod.execute(plan, run=missing)
    assert not any('checkout' in cmd or 'sparse-checkout' in cmd for cmd, _ in calls)


@pytest.mark.parametrize('profile', ['lean', 'heavy'])
def test_disposable_local_source_sparse_clone_preserves_originals(mod, inputs, tmp_path, profile):
    source = tmp_path / 'fixture-source'
    source.mkdir()
    def git(path, *args):
        return subprocess.run(['git', '-c', f'core.hooksPath={os.devnull}', '-C', str(path), *args],
                              capture_output=True, text=True, check=True)
    git(source, 'init', '-q', '-b', 'main')
    git(source, 'config', 'uploadpack.allowFilter', 'true')
    for directory in ['src', 'tests/unit', 'data']:
        (source / directory).mkdir(parents=True)
    (source / 'src/module.py').write_bytes(b'VALUE = 1\n')
    (source / 'tests/unit/test_module.py').write_bytes(b'assert 1 == 1\n')
    (source / 'data/held.bin').write_bytes(b'held synthetic evidence' * 1024)
    (source / 'README.md').write_bytes(b'root files are intentionally included\n')
    git(source, 'add', '.')
    git(source, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')
    commit = git(source, 'rev-parse', 'HEAD').stdout.strip()
    git(source, 'update-index', '--add', '--cacheinfo', f'160000,{commit},deps/sub')
    (source / '.gitmodules').write_bytes(b'[submodule "sub"]\n path = deps/sub\n url = https://example.invalid/never\n')
    git(source, 'add', '.gitmodules')
    git(source, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'submodule fixture')
    before = {str(p.relative_to(source)): p.read_bytes() for p in source.rglob('*') if p.is_file()}
    calls = []
    inputs['profile'] = profile
    if profile == 'heavy':
        inputs['include_dirs'] = []
    plan = mod.build_plan(**inputs)
    def local_transport(command, **kwargs):
        calls.append(command)
        command = [source.as_uri() if arg == 'https://example.invalid/digitalmodel.git' else arg
                   for arg in command]
        kwargs['env'] = dict(kwargs['env'], GIT_ALLOW_PROTOCOL='file')
        return subprocess.run(command, **kwargs)
    receipt = mod.execute(plan, run=local_transport)
    target = inputs['destination']
    assert receipt['status'] == 'created'
    assert receipt['checkout_materialized'] is (profile == 'lean')
    if profile == 'lean':
        assert (target / 'src/module.py').read_bytes() == b'VALUE = 1\n'
        assert (target / 'tests/unit/test_module.py').exists()
        assert (target / 'README.md').exists()
        assert git(target, 'config', '--get', 'remote.origin.partialclonefilter').stdout.strip() == 'blob:none'
        assert git(target, 'rev-parse', '--is-shallow-repository').stdout.strip() == 'true'
    else:
        assert not (target / 'src').exists()
        assert not (target / 'README.md').exists()
    assert not (target / 'data').exists()
    assert not (target / 'deps').exists()
    assert git(target, 'rev-parse', 'HEAD').stdout == git(source, 'rev-parse', 'HEAD').stdout
    assert not any('submodule' in command or 'lfs' in command for command in calls)
    after = {str(p.relative_to(source)): p.read_bytes() for p in source.rglob('*') if p.is_file()}
    assert before == after


def test_replaced_parent_identity_stops_before_clone(mod, inputs, tmp_path):
    parent = tmp_path / 'new-parent'
    parent.mkdir()
    (parent / 'held').write_bytes(b'preserve')
    inputs['destination'] = parent / 'digitalmodel'
    plan = mod.build_plan(**inputs)
    parent.rename(tmp_path / 'saved-parent')
    parent.mkdir()
    calls = []
    with pytest.raises(ValueError, match='identity'):
        mod.execute(plan, run=fake_runner(plan, calls))
    assert len(calls) == 1
    assert not inputs['destination'].exists()
    assert (tmp_path / 'saved-parent/held').read_bytes() == b'preserve'


def test_clone_timeout_retains_new_target_and_stops(mod, inputs):
    plan = mod.build_plan(**inputs)
    calls = []
    runner = fake_runner(plan, calls)
    def timeout(command, **kwargs):
        result = runner(command, **kwargs)
        if 'clone' in command:
            raise subprocess.TimeoutExpired(command, kwargs['timeout'])
        return result
    with pytest.raises(subprocess.TimeoutExpired):
        mod.execute(plan, run=timeout)
    assert inputs['destination'].exists()
    assert len(calls) == 2


def origin_fixture(inputs, tmp_path, url='https://example.invalid/owner/digitalmodel.git'):
    inputs['repos_config'].write_text('assetutilities=git@example.invalid:owner/assetutilities.git\n')
    checkout = tmp_path / 'existing-checkout'
    (checkout / '.git').mkdir(parents=True)
    (checkout / '.git/objects').mkdir()
    (checkout / '.git/HEAD').write_text('ref: refs/heads/main\n')
    (checkout / '.git/config').write_text('[remote "origin"]\n url = ' + url + '\n')
    return checkout


def test_missing_url_resolves_from_explicit_existing_origin_without_git_or_writes(mod, inputs, tmp_path, monkeypatch):
    checkout = origin_fixture(inputs, tmp_path)
    before = (checkout / '.git/config').read_bytes()
    monkeypatch.setattr(mod.subprocess, 'run', lambda *a, **k: pytest.fail('Git called'))
    plan = mod.build_plan(**inputs, url_source_checkout=checkout)
    assert plan['url_source'] == str(checkout / '.git/config')
    assert 'https://example.invalid/owner/digitalmodel.git' in plan['commands'][0]
    assert (checkout / '.git/config').read_bytes() == before
    assert not inputs['destination'].exists()


@pytest.mark.parametrize('url', ['https://secret@example.invalid/owner/digitalmodel.git',
                               'https://example.invalid/owner/different.git',
                               'ext::unsafe', 'https://example.invalid/owner/digitalmodel.git?token=secret'])
def test_origin_fallback_rejects_credentials_wrong_repo_and_unsafe_transport(mod, inputs, tmp_path, url):
    checkout = origin_fixture(inputs, tmp_path, url)
    with pytest.raises(ValueError):
        mod.build_plan(**inputs, url_source_checkout=checkout)


def test_origin_fallback_does_not_override_existing_url(mod, inputs, tmp_path):
    checkout = tmp_path / 'existing'
    checkout.mkdir()
    with pytest.raises(ValueError):
        mod.build_plan(**inputs, url_source_checkout=checkout)


def test_origin_fallback_redirect_is_rejected(mod, inputs, tmp_path):
    checkout = origin_fixture(inputs, tmp_path)
    alias = tmp_path / 'alias-checkout'
    alias.symlink_to(checkout, target_is_directory=True)
    with pytest.raises(ValueError):
        mod.build_plan(**inputs, url_source_checkout=alias)


def test_origin_fallback_never_follows_includes(mod, inputs, tmp_path):
    checkout = origin_fixture(inputs, tmp_path)
    external = tmp_path / 'external.conf'
    external.write_text('[remote "origin"]\nurl = https://example.invalid/owner/digitalmodel.git\n')
    (checkout / '.git/config').write_text('[include]\npath = ' + str(external) + '\n')
    with pytest.raises(ValueError, match='direct local origin'):
        mod.build_plan(**inputs, url_source_checkout=checkout)


def test_origin_fallback_supports_existing_worktree_locator(mod, inputs, tmp_path):
    checkout = origin_fixture(inputs, tmp_path)
    private = checkout / '.git/worktrees/linked'
    private.mkdir(parents=True)
    (private / 'HEAD').write_text('a' * 40 + '\n')
    (private / 'commondir').write_text('../..\n')
    linked = tmp_path / 'linked-source'
    linked.mkdir()
    (linked / '.git').write_text('gitdir: ' + str(private) + '\n')
    plan = mod.build_plan(**inputs, url_source_checkout=linked)
    assert 'https://example.invalid/owner/digitalmodel.git' in plan['commands'][0]


@pytest.mark.parametrize('fault', ['oversized', 'redirect-config', 'missing-objects'])
def test_invalid_origin_structure_rejected_without_git(mod, inputs, tmp_path, fault, monkeypatch):
    checkout = origin_fixture(inputs, tmp_path)
    if fault == 'oversized':
        (checkout / '.git/config').write_bytes(b'x' * (1024 * 1024 + 1))
    elif fault == 'redirect-config':
        config = checkout / '.git/config'
        config.rename(checkout / '.git/saved-config')
        config.symlink_to(checkout / '.git/saved-config')
    else:
        (checkout / '.git/objects').rename(checkout / '.git/saved-objects')
    monkeypatch.setattr(mod.subprocess, 'run', lambda *a, **k: pytest.fail('Git called'))
    with pytest.raises(ValueError):
        mod.build_plan(**inputs, url_source_checkout=checkout)


def test_origin_fallback_never_inherits_configparser_defaults(mod, inputs, tmp_path):
    checkout = origin_fixture(inputs, tmp_path)
    (checkout / '.git/config').write_text('[DEFAULT]\nurl = https://example.invalid/owner/digitalmodel.git\n'
                                        '[remote "origin"]\nfetch = +refs/heads/*:refs/remotes/origin/*\n')
    with pytest.raises(ValueError, match='direct local origin'):
        mod.build_plan(**inputs, url_source_checkout=checkout)
