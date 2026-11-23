#!/usr/bin/env python3
"""Launch five Codex audit swarms with closed stdin.

This intentionally uses Python subprocess rather than shell redirection because
Codex 0.130.0 hangs under Hermes when stdin remains open.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path('/mnt/local-analysis/workspace-hub')
BASE = ROOT / 'docs/plans/agent-swarm-audits/2026-05-10'
LOGS = BASE / 'logs'
LOGS.mkdir(parents=True, exist_ok=True)

swarm_names = {
    1: 'live-state-gate-audit',
    2: 'capability-gap-map',
    3: 'plan-review-drift',
    4: 'execution-readiness-partition',
    5: 'learning-transfer',
}

pid_lines = []
for i, name in swarm_names.items():
    prompt_path = BASE / f'prompt-swarm-{i}-{name}.md'
    prompt = prompt_path.read_text()
    jsonl_path = LOGS / f'swarm-{i}-codex.jsonl'
    last_path = LOGS / f'swarm-{i}-last-message.txt'
    stdout = jsonl_path.open('wb')
    proc = subprocess.Popen(
        [
            'codex', 'exec',
            '--cd', str(ROOT),
            '--sandbox', 'workspace-write',
            '--json',
            '--output-last-message', str(last_path),
            prompt,
        ],
        cwd=str(ROOT),
        stdin=subprocess.PIPE,
        stdout=stdout,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    # Close immediately: Codex gets EOF and does not block on extra stdin.
    assert proc.stdin is not None
    proc.stdin.close()
    stdout.close()
    pid_lines.append(f'swarm-{i} {proc.pid} {jsonl_path} {last_path}')

pid_file = LOGS / 'codex-swarm-pids.txt'
pid_file.write_text('\n'.join(pid_lines) + '\n')
print(pid_file)
print('\n'.join(pid_lines))
