#!/usr/bin/env bash
# check-codex-model-pin.sh — keep shared Codex model defaults unpinned.
# Usage: bash scripts/enforcement/check-codex-model-pin.sh [--help]
# Exit codes: 0 = no unexpected pins; 1 = pin, invalid TOML or stale exception;
# 2 = usage error. Requires Git and Python with standard-library tomllib.
# Policy and examples: docs/operations/codex-model-pin-checker.md
set -euo pipefail

if [[ $# -eq 1 && ( "$1" == --help || "$1" == -h ) ]]; then
    echo 'Usage: bash scripts/enforcement/check-codex-model-pin.sh [--help]'
    exit 0
fi
if [[ $# -ne 0 ]]; then
    echo 'check-codex-model-pin: unexpected argument; use --help' >&2
    exit 2
fi

python3 - <<'PY'
import pathlib
import re
import subprocess
import sys
import tomllib

# Explicit exceptions must retain a top-level model assignment.
ALLOWLIST = ()
MODEL = re.compile(r'''^\s*(?:model|"model"|'model')\s*=\s*(.*)''')


def pins(text):
    """Best-effort diagnostic locations; parsed TOML decides whether a pin exists."""
    quote = None
    for number, line in enumerate(text.splitlines(), 1):
        if quote is None:
            if line.lstrip().startswith('['):
                return
            match = MODEL.match(line)
            if match:
                yield number, match.group(1)
        index = 0
        while index < len(line):
            if quote:
                if quote.startswith('"') and line[index] == '\\':
                    index += 2
                elif line.startswith(quote, index):
                    index += len(quote)
                    quote = None
                else:
                    index += 1
            elif line[index] == '#':
                break
            elif line[index] in ('"', "'"):
                char = line[index]
                quote = char * 3 if line.startswith(char * 3, index) else char
                index += len(quote)
            else:
                index += 1


try:
    root = pathlib.Path(subprocess.check_output(
        ['git', 'rev-parse', '--show-toplevel'], text=True).strip())
    names = subprocess.check_output([
        'git', '-C', str(root), 'ls-files', '-z', '--', '.codex/config.toml',
        '.codex/agents/*.toml', 'config/agents/codex/*.toml',
    ]).decode().split('\0')
    failed = False
    allowed = []
    # Every exception must name a tracked matching configuration.
    for name in sorted(set(ALLOWLIST).difference(names)):
        print(f'check-codex-model-pin: {name}: stale allowlist entry (not tracked)')
        failed = True
    for name in filter(None, names):
        try:
            text = (root / name).read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            print(f'check-codex-model-pin: {name}: cannot read UTF-8 configuration',
                  file=sys.stderr)
            failed = True
            continue
        try:
            # TOML v1.0.0, Keys and Table: decoded keys identify root entries.
            # https://toml.io/en/v1.0.0#keys
            config = tomllib.loads(text)
        except tomllib.TOMLDecodeError:
            # Python tomllib docs, loads: invalid documents raise this error.
            # Do not echo exception text, which may contain configuration data.
            # https://docs.python.org/3.11/library/tomllib.html#tomllib.loads
            print(f'check-codex-model-pin: {name}: invalid TOML', file=sys.stderr)
            failed = True
            continue
        found = []
        if 'model' in config:
            found = list(pins(text)) or [('?', '<parsed root assignment>')]
        if name in ALLOWLIST:
            if found:
                allowed.append((name, config['model']))
            else:
                print(f'check-codex-model-pin: {name}: stale allowlist entry '
                      '(no root model key)')
                failed = True
        else:
            for number, value in found:
                print(f'check-codex-model-pin: {name}:{number}: model = {value} '
                      '(unexpected top-level pin)')
                failed = True
    print('check-codex-model-pin: Allowlisted pin inventory:')
    for name, value in allowed:
        print(f'  ALLOW {name}: model = {value!r}')
    if not allowed:
        print('  (none)')
    if not failed:
        print('check-codex-model-pin: PASS (no unexpected top-level model pins)')
    sys.exit(1 if failed else 0)
except (OSError, UnicodeError, subprocess.CalledProcessError):
    print('check-codex-model-pin: ERROR reading tracked Codex configurations', file=sys.stderr)
    sys.exit(1)
PY
