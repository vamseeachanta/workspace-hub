"""Controlled observations for legacy collector tests; complements collector isolation work.

Only fixture paths and synthetic SDK outcomes are used. Expected hardware values
are arbitrary test inputs; they express no engineering acceptance criterion.
"""
import os
import shlex
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def sandbox_env(root, env):
    env = dict(env or os.environ)
    if env.get('EQUALITY_SANDBOX'):
        return env
    runtime = root / 'collector-runtime'
    bins = runtime / 'bin'
    bins.mkdir(parents=True, exist_ok=True)
    home = runtime / 'user'
    home.mkdir(exist_ok=True)
    temp = runtime / 'tmp'
    temp.mkdir(exist_ok=True)
    quote = shlex.quote
    interpreter = quote(sys.executable)
    stub = ('#!/usr/bin/env bash\n'
            'if [[ "${1:-}" == -c && "${2:-}" == *OrcFxAPI* ]]; then exit 1; fi\n'
            f'exec {interpreter} "$@"\n')
    for name in ('python', 'python3'):
        target = bins / name
        target.write_text(stub)
        target.chmod(0o755)
    for name in ('bash', 'find', 'wc', 'tr', 'sed', 'sort', 'paste', 'jq',
                 'git', 'awk', 'grep', 'head', 'mktemp', 'mkdir', 'rm', 'mv', 'cat',
                 'cut', 'dirname', 'basename', 'date', 'stat', 'timeout', 'sleep',
                 'touch', 'rmdir', 'cp', 'seq', 'tee'):
        source = shutil.which(name)
        if source and not (bins / name).exists():
            (bins / name).symlink_to(source)
    observations = {
        'uname': 'echo Linux',
        'nproc': 'echo 8',
        'free': "echo 'Mem: 8192 1024 0 0 0 7168'",
        'df': "printf 'Filesystem Available\\nfixture 100G\\n'",
        'nvidia-smi': 'echo fixture',
        'sysctl': 'echo 8388608',
        'hostname': 'echo fixture',
        'gh': 'exit 1',
        'crontab': 'exit 1',
    }
    for name, body in observations.items():
        target = bins / name
        target.write_text('#!/usr/bin/env bash\n' + body + '\n')
        target.chmod(0o755)
    uv = bins / 'uv'
    uv.write_text('#!/usr/bin/env bash\n'
                  '[[ "$1" == run ]] || exit 2\nshift\n'
                  'while [[ "${1:-}" == -* || "${1:-}" == python ]]; do shift; done\n'
                  f'exec {interpreter} "$@"\n')
    uv.chmod(0o755)
    # Preserve explicit per-test shims, then controlled observations, then basic utilities.
    parts = [part for part in env.get('PATH', os.defpath).split(os.pathsep)
             if part.startswith(str(root)) and part != str(bins)]
    parts.append(str(bins))
    startup = runtime / 'startup.sh'
    startup.write_text(
        f'source {quote(str(REPO / "scripts/readiness/lib/probe-solvers.sh"))}\n'
        'probe_ansys_root() { echo absent; }\n'
        'probe_orcaflex_root() { echo absent; }\n'
        'probe_orcawave_root() { echo absent; }\n')
    env.update(PATH=os.pathsep.join(parts), BASH_ENV=str(startup),
               HOME=env.get('HOME', str(home)) if env.get('HOME', '').startswith(str(root)) else str(home),
               TMPDIR=str(temp),
               PYTHONDONTWRITEBYTECODE='1', EQUALITY_SANDBOX='1',
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
               UV_CACHE_DIR=os.environ['UV_CACHE_DIR'])
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE'):
        env.pop(key, None)
    return env
