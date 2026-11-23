"""Opt-in new-destination clone plans using existing registry membership and URLs."""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # Direct CLI dry-run must not create import caches.

import argparse
import configparser
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from urllib.parse import urlsplit

import yaml

from repo_footprint import _has_symlink_component, _locator, _selection


def _relative(value: str, *, allow_hidden: bool = False) -> bool:
    pattern = r'[A-Za-z0-9_.][A-Za-z0-9_./-]*' if allow_hidden else r'[A-Za-z0-9_][A-Za-z0-9_./-]*'
    return bool(re.fullmatch(pattern, value)) and all(
        p not in {'', '.', '..'} and p.lower() != '.git' and not p.startswith('-')
        for p in value.split('/'))


def _destination(path: Path) -> tuple[int, int]:
    if not path.is_absolute() or path.name in {'', '.', '..', '.git'}:
        raise ValueError('destination must be an absolute new directory')
    if _has_symlink_component(path.parent) or not path.parent.is_dir():
        raise ValueError('destination parent must exist without redirects')
    if os.path.lexists(path):
        raise ValueError('destination already exists; it will not be replaced')
    info = os.lstat(path.parent)
    return info.st_dev, info.st_ino


def _valid_url(url: str) -> str:
    parsed = urlsplit(url)
    https = (parsed.scheme == 'https' and parsed.hostname and not parsed.username
             and not parsed.password and not parsed.query and not parsed.fragment
             and re.fullmatch(r'/[A-Za-z0-9_./-]+', parsed.path))
    ssh = re.fullmatch(r'git@[A-Za-z0-9.-]+:[A-Za-z0-9_./-]+', url)
    if not (https or ssh) or any(ord(c) < 33 for c in url):
        raise ValueError('only credential-free HTTPS or git@host:path URLs are supported')
    path = parsed.path.lstrip('/') if https else url.split(':', 1)[1]
    if any(p in {'', '.', '..'} or p.endswith('.') for p in path.split('/')):
        raise ValueError('unsafe repository URL path')
    return url


def _read_metadata(path: Path, limit: int) -> str:
    if _has_symlink_component(path) or not stat.S_ISREG(os.lstat(path).st_mode):
        raise ValueError('origin metadata must be a regular non-redirect file')
    with path.open('rb') as handle:
        raw = handle.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('oversized origin metadata')
    return raw.decode('utf-8')


def _origin_url(checkout: Path, repo: str) -> tuple[str, str]:
    if not checkout.is_absolute() or _has_symlink_component(checkout) or not checkout.is_dir():
        raise ValueError('URL source must be an absolute existing non-redirect checkout')
    metadata = checkout / '.git'
    if _has_symlink_component(metadata):
        raise ValueError('redirected Git metadata is not supported')
    private = _locator(metadata, 'gitdir: ') if metadata.is_file() else metadata
    common = _locator(private / 'commondir') if os.path.lexists(private / 'commondir') else private
    if not private.is_dir() or not common.is_dir() or _has_symlink_component(common / 'objects') or not (common / 'objects').is_dir():
        raise ValueError('local source Git structure is unavailable')
    head = _read_metadata(private / 'HEAD', 4096).strip()
    if not re.fullmatch(r'(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64}|ref: refs/heads/[A-Za-z0-9_./-]+)', head):
        raise ValueError('local source HEAD is malformed')
    config = common / 'config'
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read_string(_read_metadata(config, 1024 * 1024))
        if parser.defaults():
            raise ValueError('direct local origin cannot inherit ConfigParser defaults')
        url = _valid_url(parser.get('remote "origin"', 'url').strip())
    except (configparser.Error, UnicodeDecodeError) as exc:
        raise ValueError('direct local origin configuration is unavailable') from exc
    pathname = urlsplit(url).path if url.startswith('https://') else url.split(':', 1)[1]
    if pathname.rsplit('/', 1)[-1] not in {repo, repo + '.git'}:
        raise ValueError('source origin repository name does not match selected member')
    return url, str(config)


def _url(config: Path, repo: str, checkout: Path | None) -> tuple[str, str]:
    matches = []
    for line in config.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        name, separator, value = line.partition('=')
        if separator and name.strip() == repo:
            matches.append(value.strip())
    if not matches and checkout is not None:
        return _origin_url(checkout, repo)
    if checkout is not None:
        raise ValueError('local origin fallback cannot override existing repos.conf mapping')
    if len(matches) != 1:
        raise ValueError('repo must have exactly one URL in existing repos.conf')
    return _valid_url(matches[0]), str(config)


def build_plan(*, repo: str, profile: str, destination: Path, include_dirs: list[str],
               branch: str, machine: str, registry: Path, repos_config: Path,
               url_source_checkout: Path | None = None, expected_head: str | None = None) -> dict:
    data = yaml.safe_load(registry.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('registry must be a mapping')
    _, core, source = _selection(data, machine, 'required')
    if repo not in core:
        raise ValueError('one required core repository must be explicitly selected')
    if profile not in {'lean', 'heavy'}:
        raise ValueError('profile must be lean or heavy')
    if expected_head is not None and (profile != 'lean' or not re.fullmatch(r'[0-9a-f]{40}', expected_head)):
        raise ValueError('expected head requires a lean profile and full lowercase revision')
    if not _relative(branch) or '..' in branch or branch.endswith(('/', '.', '.lock')):
        raise ValueError('unsafe or unsupported branch name')
    if profile == 'lean' and not include_dirs:
        raise ValueError('lean requires explicit --include-dir selections')
    if profile == 'heavy' and include_dirs:
        raise ValueError('heavy does not accept sparse selections')
    if len(include_dirs) > 20 or any(len(p) > 255 or not _relative(p, allow_hidden=True) for p in include_dirs):
        raise ValueError('unsafe or unsupported sparse directory')
    destination = Path(destination)
    if destination.name != repo:
        raise ValueError('destination basename must equal the selected repository')
    parent_id = _destination(destination)
    url, url_source = _url(Path(repos_config), repo, url_source_checkout)
    git = ['git', '-c', f'core.hooksPath={os.devnull}', '-c', 'protocol.version=2',
           '-c', 'submodule.recurse=false']
    clone = git + ['clone', '--no-checkout', '--single-branch', '--no-tags',
                   '--no-recurse-submodules', '--template=', '--branch', branch]
    commands = []
    if profile == 'lean':
        commands.append(git + ['ls-remote', '--heads', '--exit-code', url, f'refs/heads/{branch}'])
        clone += ['--filter=blob:none', '--depth=1']
    commands.append(clone + ['--', url, str(destination)])
    if profile == 'lean':
        commands += [git + ['-C', str(destination), 'config', '--get-regexp',
                           r'^remote\.origin\.(promisor|partialclonefilter)$']]
        commands += [git + ['-C', str(destination), 'cat-file', '-t', f'HEAD:{path}']
                     for path in dict.fromkeys(include_dirs)]
        commands += [git + ['-C', str(destination), 'sparse-checkout', 'set', '--cone', '--',
                            *dict.fromkeys(include_dirs)],
                     git + ['-C', str(destination), 'checkout', 'HEAD']]
    return {'schema_version': 1, 'repository': repo, 'profile': profile,
            'destination': str(destination), 'parent_identity': list(parent_id),
            'branch': branch, 'include_directories': list(dict.fromkeys(include_dirs)),
            'expected_head': expected_head,
            'membership_source': source, 'core_repositories': core, 'url_source': url_source,
            'commands': commands, 'runtime_readiness': 'not_verified',
            'notes': ['No existing checkout conversion, dependency installation, LFS or submodule hydration.',
                      'Lean requests shallow blob filtering; this is not a network byte cap.',
                      'Cone sparse checkout includes root and ancestor files in addition to selected directories.',
                      'Heavy downloads the full single-branch object history but leaves checkout unmaterialized.',
                      'No automatic cleanup: a failed new destination is retained.',
                      'The footprint checker and source/sibling/fixture checks remain required for readiness.']}


def _environment() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_TERMINAL_PROMPT='0', GIT_LFS_SKIP_SMUDGE='1', GIT_CONFIG_NOSYSTEM='1',
               GIT_CONFIG_GLOBAL=os.devnull, GIT_ALLOW_PROTOCOL='https:ssh')
    return env


def _unchanged(path: Path, expected: tuple[int, int]) -> None:
    if _has_symlink_component(path):
        raise ValueError('new destination or parent became redirected; retained')
    info = os.lstat(path)
    if not stat.S_ISDIR(info.st_mode) or (info.st_dev, info.st_ino) != expected:
        raise ValueError('new destination or parent identity changed; retained')


def execute(plan: dict, *, run=None) -> dict:
    """Only execute a validated plan; retain all failures and never retry unfiltered."""
    run = run or subprocess.run
    target = Path(plan['destination'])
    parent_id = tuple(plan['parent_identity'])
    env = _environment()
    commands = plan['commands']
    if plan['profile'] == 'lean':
        trace_env = dict(env, GIT_TRACE_PACKET='1')
        result = run(commands[0], capture_output=True, text=True, env=trace_env, timeout=30)
        if result.returncode or not re.search(r'<\s+fetch=[^\r\n]*\bfilter\b', result.stderr):
            raise ValueError('server filter capability not verified; no clone attempted')
        if plan.get('expected_head'):
            advertised = result.stdout.strip().splitlines()
            if advertised != [plan['expected_head'] + '\trefs/heads/' + plan['branch']]:
                raise ValueError('advertised branch differs from tested revision; no clone attempted')
        commands = commands[1:]
    _unchanged(target.parent, parent_id)
    try:
        target.mkdir()  # Atomic claim of a nonexistent destination, never reuse an empty dir.
    except FileExistsError as exc:
        raise ValueError('destination appeared after preflight; preserved') from exc
    target_id = (os.lstat(target).st_dev, os.lstat(target).st_ino)
    for index, command in enumerate(commands):
        _unchanged(target.parent, parent_id)
        _unchanged(target, target_id)
        if index:
            metadata = target / '.git'
            if _has_symlink_component(metadata) or not metadata.is_dir():
                raise ValueError('new Git metadata unavailable or redirected; retained')
        step_env = dict(env, GIT_NO_LAZY_FETCH='1') if 'cat-file' in command else env
        result = run(command, capture_output=True, text=True, env=step_env, timeout=120)
        _unchanged(target.parent, parent_id)
        _unchanged(target, target_id)
        if result.returncode:
            raise ValueError('Git step failed; new destination retained without cleanup')
        if index == 0 and plan['profile'] == 'lean' and re.search(
                r'filter[^\r\n]*(ignor|not |unsupported)|does not support filter', result.stderr, re.I):
            raise ValueError('server rejected filtering; new destination retained without checkout')
        if index == 0 and plan.get('expected_head'):
            prefix = command[:command.index('clone')]
            observed = run(prefix + ['-C', str(target), 'rev-parse', '--verify', 'HEAD'],
                           capture_output=True, text=True, env=dict(env, GIT_NO_LAZY_FETCH='1'), timeout=20)
            _unchanged(target.parent, parent_id)
            _unchanged(target, target_id)
            if observed.returncode or observed.stdout.strip() != plan['expected_head']:
                raise ValueError('cloned revision differs from tested revision; retained without checkout')
        if index == 1 and plan['profile'] == 'lean':
            values = dict(line.split(None, 1) for line in result.stdout.splitlines() if len(line.split(None, 1)) == 2)
            if values.get('remote.origin.promisor') != 'true' or values.get('remote.origin.partialclonefilter') != 'blob:none':
                raise ValueError('partial clone configuration not verified; retained without checkout')
            pack = target / '.git/objects/pack'
            if _has_symlink_component(pack) or not any(pack.glob('*.promisor')):
                raise ValueError('promisor object store not verified; retained without checkout')
        if 'cat-file' in command and result.stdout.strip() != 'tree':
            raise ValueError('selected source directory is not a tree; retained without checkout')
    return dict(plan, dry_run=False, status='created',
                checkout_materialized=plan['profile'] == 'lean',
                head_verification='expected_revision_verified_before_checkout' if plan.get('expected_head') else 'not_performed', core_profile_verified=False)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo')
    parser.add_argument('--profile', choices=['lean', 'heavy'], required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--include-dir', action='append', default=[])
    parser.add_argument('--branch', default='main')
    parser.add_argument('--expected-head', help='Optional tested revision; stop before clone if main moved and before checkout if clone raced')
    parser.add_argument('--baseline-profile', type=Path, help='Reviewed reusable lean recipe; membership stays in existing registry')
    parser.add_argument('--machine', default='dev-primary')
    parser.add_argument('--dry-run', action='store_true')
    root = Path(__file__).resolve().parents[2]
    parser.add_argument('--registry', type=Path, default=root / 'config/workstations/registry.yaml')
    parser.add_argument('--repos-config', type=Path, default=root / 'config/repos.conf')
    parser.add_argument('--url-source-checkout', type=Path,
                        help='Explicit existing local origin for a URL absent from repos.conf; metadata only')
    args = parser.parse_args(argv)
    try:
        if args.baseline_profile:
            from core_equivalence import load_profile
            contract = load_profile(args.baseline_profile, yaml.safe_load(args.registry.read_text(encoding='utf-8')))
            if args.profile != 'lean' or args.include_dir or args.expected_head or args.machine != contract['membership_machine'] or args.branch != 'main':
                raise ValueError('baseline profile requires lean/main, its registry authority and no sparse/pin overrides')
            recipe = contract['repositories'].get(args.repo)
            if not recipe:
                raise ValueError('repository absent from complete baseline profile')
            if recipe['clone_policy'] != 'new_destination':
                raise ValueError('baseline profile requires a sanitized existing checkout; no new clone planned')
            args.include_dir, args.expected_head = recipe['include_directories'], recipe['revision']
        plan = build_plan(repo=args.repo, profile=args.profile, destination=args.destination,
                          include_dirs=args.include_dir, branch=args.branch, machine=args.machine,
                          registry=args.registry, repos_config=args.repos_config,
                          url_source_checkout=args.url_source_checkout, expected_head=args.expected_head)
        if args.baseline_profile and recipe.get('origin_url_sha256'):
            from core_equivalence import origin_digest
            origin, _ = _url(args.repos_config, args.repo, args.url_source_checkout)
            if origin_digest(origin) != recipe['origin_url_sha256']:
                raise ValueError('configured direct origin differs from observed baseline; no clone planned')
        receipt = dict(plan, dry_run=True, status='planned') if args.dry_run else execute(plan)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f'clone profile failed: {exc}\n')
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
