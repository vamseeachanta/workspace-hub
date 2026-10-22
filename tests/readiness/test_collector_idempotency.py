"""An unchanged canonical payload must preserve bytes and file identity, without a hash tool.

The independent comparison removes only the documented volatile top-level and
indented fields. A checkout identifier is observation metadata, not content.
"""
import shutil
import subprocess
from pathlib import Path

import yaml
from collector_sandbox import sandbox_env

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / 'scripts/readiness/collect-equality.sh'


def environment(tmp_path):
    bins = tmp_path / 'utilities'
    bins.mkdir()
    for name in ('bash', 'uname', 'find', 'wc', 'tr', 'sed', 'sort', 'paste', 'jq',
                 'git', 'awk', 'grep', 'head', 'mktemp', 'mkdir', 'rm', 'mv', 'cat',
                 'cut', 'dirname'):
        source = shutil.which(name)
        if source:
            (bins / name).symlink_to(source)
    date = bins / 'date'
    date.write_text('#!/usr/bin/env bash\necho 2026-10-22T12:00:00Z\n')
    date.chmod(0o755)
    workspace = tmp_path / 'checkout'
    (workspace / '.claude/state').mkdir(parents=True)
    env = sandbox_env(tmp_path, {'PATH': str(bins), 'WORKSPACE_HUB': str(workspace)})
    env['EQ_STATE_DIR'] = str(workspace / '.claude/state')
    return workspace, env


def collect(env):
    return subprocess.run(['bash', str(SCRIPT), '--machine', 'fixture'], env=env,
                          capture_output=True, text=True, check=False, timeout=20)


def test_unchanged_without_hash_executable(tmp_path):
    workspace, env = environment(tmp_path)
    first = collect(env)
    assert first.returncode == 0, first.stderr
    out = workspace / '.claude/state/equality-fixture.yaml'
    before = out.read_bytes(), out.stat().st_ino, out.stat().st_mtime_ns
    second = collect(env)
    assert second.returncode == 0, second.stderr
    assert (out.read_bytes(), out.stat().st_ino, out.stat().st_mtime_ns) == before
    report = yaml.safe_load(out.read_text())
    assert report['generated_at'].endswith('Z')


def test_checkout_identifier_alone_is_not_content(tmp_path):
    workspace, env = environment(tmp_path)
    assert collect(env).returncode == 0
    out = workspace / '.claude/state/equality-fixture.yaml'
    out.write_text(out.read_text().replace('checkout_sha: "unknown"', 'checkout_sha: "other"'))
    before = out.read_bytes(), out.stat().st_mtime_ns
    assert collect(env).returncode == 0
    assert (out.read_bytes(), out.stat().st_mtime_ns) == before


def test_meaningful_change_rewrites_without_hash_executable(tmp_path):
    workspace, env = environment(tmp_path)
    assert collect(env).returncode == 0
    out = workspace / '.claude/state/equality-fixture.yaml'
    out.write_text(out.read_text().replace('dirty: false', 'dirty: true'))
    assert collect(env).returncode == 0
    assert 'dirty: false' in out.read_text()
