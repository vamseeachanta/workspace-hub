"""Read local installation metadata and print a dry-run plan (POSIX/Linux only).

Policy basis: issue 3964, user npm preference and desktop-component exclusion.
No registry queries, process execution, package changes or filesystem writes.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path, PurePath

PACKAGES = {'claude': '@anthropic-ai/claude-code', 'codex': '@openai/codex'}


@dataclass
class Installation:
    tool: str
    kind: str
    version: str
    identity: Path
    paths: list[Path] = field(default_factory=list)
    winner: Path | None = None
    prefix: Path | None = None
    snap_name: str | None = None


def resolved(path: Path) -> Path:
    try:
        return path.resolve()
    except (OSError, RuntimeError):
        return path.absolute()


def package_version(root: Path, tool: str) -> str:
    """Only a matching package name qualifies a version and npm removal."""
    try:
        data = json.loads((root / 'package.json').read_text(encoding='utf-8'))
        if isinstance(data, dict) and data.get('name') == PACKAGES[tool]:
            version = data.get('version')
            if isinstance(version, str) and version and not any(c.isspace() for c in version):
                return version
    except (OSError, ValueError):
        pass
    return 'UNKNOWN'


def snap_metadata(root: Path, tool: str) -> tuple[str, str | None]:
    """Read simple scalar fields only; unsupported YAML remains unknown."""
    try:
        text = (root / 'meta/snap.yaml').read_text(encoding='utf-8')
    except (OSError, UnicodeError):
        return 'UNKNOWN', None
    fields = {}
    for line in text.splitlines():
        match = re.fullmatch(r'(name|version):\s*[\'\"]?([\w.+-]+)[\'\"]?\s*', line)
        if match:
            fields[match[1]] = match[2]
    if fields.get('name') != tool:
        return 'UNKNOWN', None
    return fields.get('version', 'UNKNOWN'), tool


def prefixes_for(home: Path, system: Path, extra: list[Path]) -> list[Path]:
    prefixes = [*extra, home / '.npm-global', home / '.local', home / '.npm',
                system / 'usr/local', system / 'usr']
    for pattern in ('.nvm/versions/node/*', '.volta/tools/image/node/*',
                    '.local/share/fnm/node-versions/*/installation'):
        prefixes.extend(sorted(home.glob(pattern)))
    return list(dict.fromkeys(p.absolute() for p in prefixes))


def through_launcher(path: Path, launcher: Path) -> bool:
    """Resolve parent links (including junctions), preserving the final wrapper."""
    seen = set()
    path = Path(os.path.abspath(path))
    launcher = resolved(launcher.parent) / launcher.name
    while path not in seen:
        path = resolved(path.parent) / path.name
        if path == launcher:
            return True
        if path in seen:
            return False
        seen.add(path)
        try:
            if not path.is_symlink():
                return False
            target = path.readlink()
        except OSError:
            return False
        path = Path(os.path.abspath(target if target.is_absolute() else path.parent / target))
    return False


def classify(tool: str, path: Path, prefixes: list[Path], system: Path,
             home: Path) -> Installation:
    # Snap aliases share one shared executable: use the lexical command name.
    snap_bin = system / 'snap/bin'
    if through_launcher(path, snap_bin / tool):
        root = system / 'snap' / tool / 'current'
        version, name = snap_metadata(root, tool)
        return Installation(tool, 'snap (path inference)', version, root,
                            snap_name=name)
    target = resolved(path)
    for prefix in prefixes:
        root = prefix / 'lib/node_modules' / PACKAGES[tool]
        if target.is_relative_to(resolved(root)):
            version = package_version(root, tool)
            kind = 'npm (path inference)'
            if any(part in prefix.parts for part in ('.nvm', '.volta', 'fnm')):
                kind = 'version-manager npm (path inference)'
            elif prefix.is_relative_to(home):
                kind = 'user npm (path inference)'
            return Installation(tool, kind, version, resolved(root),
                                prefix=prefix if version != 'UNKNOWN' else None)
    # A native executable is never assumed to be an npm package or safe to remove.
    return Installation(tool, 'local/system binary (path inference)',
                        'UNKNOWN', target)


def inventory(home: Path, path_value: str, system: Path = Path('/'),
              extra_prefixes=()) -> list[Installation]:
    """Inspect bounded roots; PATH order decides winners, not glob order."""
    home, system = home.absolute(), system.absolute()
    prefixes = prefixes_for(home, system, list(extra_prefixes))
    path_dirs = [Path(p or '.').absolute() for p in path_value.split(os.pathsep)]
    if not path_value:
        path_dirs = []
    # Infer custom npm prefixes from PATH directories and resolved package targets.
    for directory in path_dirs:
        if directory.name == 'bin':
            prefixes.append(directory.parent)
        for tool in PACKAGES:
            target = resolved(directory / tool)
            for parent in target.parents:
                if parent.name == 'node_modules' and parent.parent.name == 'lib':
                    prefixes.append(parent.parent.parent)
                    break
    prefixes = list(dict.fromkeys(prefixes))
    dirs = list(dict.fromkeys([*path_dirs, home / 'bin', home / '.local/bin',
                              system / 'snap/bin', system / 'usr/bin',
                              system / 'usr/local/bin', system / 'bin',
                              *(p / 'bin' for p in prefixes)]))
    found = {}
    winners = set()
    for directory in dirs:
        for tool in PACKAGES:
            path = directory / tool
            if not (path.is_file() or path.is_symlink()):
                continue
            row = classify(tool, path, prefixes, system, home)
            key = (tool, row.identity)
            existing = found.setdefault(key, row)
            if path not in existing.paths:
                existing.paths.append(path)
            if (tool not in winners and directory in path_dirs
                    and path.is_file() and os.access(path, os.X_OK)):
                existing.winner = path
                winners.add(tool)
    # Packages with absent launchers still represent independent installations.
    for prefix in prefixes:
        for tool, package in PACKAGES.items():
            root = prefix / 'lib/node_modules' / package
            if (root / 'package.json').is_file():
                row = classify(tool, root / 'package.json', prefixes, system, home)
                key = (tool, row.identity)
                if key not in found:
                    row.paths.append(root)
                    found[key] = row
    # Issue 3964 requires independent installs, not just visible commands.
    # As with npm metadata, an installed Snap may have no working launcher.
    for tool in PACKAGES:
        root = system / 'snap' / tool / 'current'
        if root.exists() or root.is_symlink():
            row = classify(tool, system / 'snap/bin' / tool, prefixes, system, home)
            key = (tool, row.identity)
            if key not in found:
                row.paths.append(root)
                found[key] = row
    return list(found.values())


def q(value) -> str:
    return shlex.quote(value.as_posix() if isinstance(value, PurePath) else str(value))


def preferred_installation(copies: list[Installation], home: Path,
                           extra_prefixes=()) -> tuple[Installation | None, Path]:
    """Share the existing preference order between text and JSON output."""
    preferred = [Path(p).absolute() for p in extra_prefixes
                 if Path(p).absolute().is_relative_to(home.absolute())]
    defaults = [home / '.npm-global', home / '.local', home / '.npm']
    inferred = sorted(
        (r for r in copies if r.prefix is not None
         and r.kind == 'user npm (path inference)'
         and r.prefix.is_relative_to(home.absolute())),
        key=lambda r: r.winner is None,
    )
    candidates = [*preferred, *(r.prefix for r in inferred), *defaults]
    keep = next((r for prefix in candidates for r in copies
                 if r.prefix == prefix), None)
    return keep, keep.prefix if keep else candidates[0]


def report(rows: list[Installation], home: Path, extra_prefixes=()) -> dict:
    """Describe bounded evidence, never certify live maintenance completion.

    Acceptance count of one independent installation and fresh-shell/release
    checks: repository issue 3964, Acceptance paragraph. No version is assumed.
    """
    tools = {}
    for tool in PACKAGES:
        copies = [row for row in rows if row.tool == tool]
        keep, _ = preferred_installation(copies, home, extra_prefixes)
        winner = next((row for row in copies if row.winner is not None), None)
        known = bool(copies) and all(row.version != 'UNKNOWN' for row in copies)
        uniqueness = ('FAIL' if len(copies) > 1 else
                      'PASS' if len(copies) == 1 and known else 'NOT_EVALUATED')
        checks = {
            'bounded_uniqueness': uniqueness,
            'preferred_user_npm': ('PASS' if keep else 'FAIL' if known else 'NOT_EVALUATED'),
            'supplied_path': ('PASS' if winner is keep and keep is not None else
                              'FAIL' if winner is not None and keep is not None else
                              'NOT_EVALUATED'),
            'latest_release': 'NOT_EVALUATED',
            'fresh_shells': 'NOT_EVALUATED',
            'functionality': 'NOT_EVALUATED',
        }
        tools[tool] = {
            'installation_count': len(copies),
            'preferred_identity': keep.identity.as_posix() if keep else None,
            'checks': checks,
            'installations': [
                {'identity': row.identity.as_posix(), 'kind': row.kind,
                 'metadata_version': row.version,
                 'paths': [path.as_posix() for path in row.paths],
                 'path_winner': row.winner.as_posix() if row.winner else None}
                for row in copies
            ],
        }
    failed = any(value == 'FAIL' for tool in tools.values() for value in tool['checks'].values())
    return {
        'status': 'FAIL' if failed else 'NOT_EVALUATED',
        'scope': 'Bounded filesystem metadata and supplied PATH only; paths are private.',
        'tools': tools,
    }


def render(rows: list[Installation], home: Path, extra_prefixes=()) -> str:
    lines = ['DRY RUN ONLY: no commands are executed; no files are changed.',
             'path | inferred installation | metadata version | PATH winner']
    for row in rows:
        for path in row.paths:
            lines.append(f'{q(path)} | {row.kind} | {q(row.version)} | '
                         f'{"yes" if row.winner == path else "no"}')
    for tool, package in PACKAGES.items():
        copies = [r for r in rows if r.tool == tool]
        keep, destination = preferred_installation(copies, home, extra_prefixes)
        if keep:
            lines.append(f'KEEP {tool}: {keep.paths[0].as_posix()}')
        else:
            lines.append(f'MISSING {tool}: metadata-matched preferred user npm installation')
        lines += [(f'INSTALL/UPDATE (maintainer review): npm install --global '
                  f'--prefix {q(destination)} {q(package + "@latest")}'),
                  (f'PATH prerequisite: place {q(destination / "bin")} before other CLI directories; '
                  'preserve existing PATH entries and review shell startup files.')]
        for row in copies:
            if row is keep:
                continue
            # Never remove the only usable installation before a replacement works.
            if not keep:
                lines.append(f'MANUAL REVIEW {tool}: {q(row.paths[0])}; '
                             'establish the preferred installation before removal.')
            elif row.prefix:
                lines.append(f'REMOVE after replacement validation: npm uninstall --global '
                             f'--prefix {q(row.prefix)} {q(package)}')
            elif row.snap_name:
                lines.append(f'REMOVE after replacement validation: sudo snap remove {q(row.snap_name)}')
            else:
                lines.append(f'MANUAL REVIEW {tool}: {q(row.paths[0])}; '
                             'installation ownership is unverified; no removal command.')
    lines += ['Run only reviewed commands, after preserving package versions and shell configuration.',
              'Desktop-managed components are outside this plan; leave them unchanged.',
              'Metadata does not establish executable version or latest registry agreement.',
              'Re-run inventory in fresh login and interactive shells; validate functionality separately.']
    return '\n'.join(lines)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    if os.name == 'nt':
        parser.error('POSIX/Linux only; Windows npm layouts are unsupported')
    parser.add_argument('--home', type=Path, default=Path.home(), help='User installation root')
    parser.add_argument('--system-root', type=Path, default=Path('/'), help='System root (fixture support)')
    parser.add_argument('--path', default=os.environ.get('PATH', ''), help='PATH value to inspect')
    parser.add_argument('--npm-prefix', type=Path, action='append', default=[],
                        help='Additional npm prefix; first user prefix is preferred')
    parser.add_argument('--format', choices=('text', 'json'), default='text',
                        help='JSON includes bounded acceptance checks; neither format applies changes')
    args = parser.parse_args(argv)
    rows = inventory(args.home, args.path, args.system_root, args.npm_prefix)
    if args.format == 'json':
        print(json.dumps(report(rows, args.home.absolute(), args.npm_prefix), indent=2))
    else:
        print(render(rows, args.home.absolute(), args.npm_prefix))


if __name__ == '__main__':
    main()
