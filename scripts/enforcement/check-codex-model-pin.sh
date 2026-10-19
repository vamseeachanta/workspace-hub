#!/usr/bin/env bash
# check-codex-model-pin.sh — keep shared Codex model defaults unpinned.
# Usage: bash scripts/enforcement/check-codex-model-pin.sh [--help]
# Exit codes: 0 = no unexpected pins; 1 = pin or stale exception; 2 = usage error.
# Uses Git and Python's standard-library line parser; no TOML library required.
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

# Explicit exceptions must retain a top-level model assignment.
ALLOWLIST = ()
MODEL = re.compile(r'''^\s*(?:model|"model"|'model')\s*=\s*(.*)''')


def pins(text):
    """Find root assignments, ignoring comments and multiline string contents."""
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
    # Every exception must name a tracked matching configuration.
    for name in sorted(set(ALLOWLIST).difference(names)):
        print(f'check-codex-model-pin: {name}: stale allowlist entry (not tracked)')
        failed = True
    for name in filter(None, names):
        found = list(pins((root / name).read_text(encoding='utf-8')))
        if name in ALLOWLIST:
            if found:
                print(f'check-codex-model-pin: ALLOW {name}')
            else:
                print(f'check-codex-model-pin: {name}: stale allowlist entry')
                failed = True
        else:
            for number, value in found:
                print(f'check-codex-model-pin: {name}:{number}: model = {value}')
                failed = True
    if not failed:
        print('check-codex-model-pin: PASS (no unexpected top-level model pins)')
    sys.exit(1 if failed else 0)
except (OSError, UnicodeError, subprocess.CalledProcessError):
    print('check-codex-model-pin: ERROR reading tracked Codex configurations', file=sys.stderr)
    sys.exit(1)
PY
