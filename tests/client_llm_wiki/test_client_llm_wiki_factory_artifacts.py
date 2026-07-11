"""Executable contract tests for the public client-wiki factory recipe."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".claude/skills/coordination/client-llm-wiki-factory/SKILL.md"


def _factory_block() -> str:
    text = SKILL.read_text(encoding="utf-8")
    blocks = re.findall(r"```bash\n(.*?)```", text, re.DOTALL)
    return next(block for block in blocks if 'MANIFEST="$(mktemp' in block)


def _fake_tools(tmp_path: Path) -> tuple[Path, Path]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls"
    uv = bin_dir / "uv"
    uv.write_text(
        """#!/usr/bin/env python3
import os, pathlib, sys
args = sys.argv[1:]
with open(os.environ['CALL_LOG'], 'a') as stream:
    stream.write('uv ' + ' '.join(args) + '\\n')
command = next((name for name in ('render', 'finalize-scaffold', 'verify-private-repo') if name in args), '')
if os.environ.get('FAIL_STAGE') == command:
    raise SystemExit(1)
if command == 'render':
    destination = pathlib.Path(args[args.index('--manifest') + 1])
    destination.write_text('{"manifest":true}\\n')
""",
        encoding="utf-8",
    )
    uv.chmod(0o755)
    updater = bin_dir / "registry-update"
    updater.write_text(
        """#!/bin/sh
printf 'registry-update %s\\n' "$*" >> "$CALL_LOG"
""",
        encoding="utf-8",
    )
    updater.chmod(0o755)
    return bin_dir, log


def _run_block(
    tmp_path: Path, *, fail_stage: str = ""
) -> subprocess.CompletedProcess[str]:
    bin_dir, log = _fake_tools(tmp_path)
    manifest_dir = tmp_path / "evidence"
    manifest_dir.mkdir()
    env = os.environ.copy()
    env.update(
        PATH=f"{bin_dir}:{env['PATH']}",
        CALL_LOG=str(log),
        FAIL_STAGE=fail_stage,
        MANIFEST_DIR=str(manifest_dir),
        REGISTRY_UPDATE_TOOL=str(bin_dir / "registry-update"),
        WORKSPACE_HUB=str(ROOT),
        REGISTRY=str(tmp_path / "private-registry.yml"),
        SHORT="example",
        TARGET=str(tmp_path / "llm-wiki-example"),
        REPO="example/llm-wiki-example",
    )
    return subprocess.run(
        ["bash", "-euo", "pipefail", "-c", _factory_block()],
        env=env,
        capture_output=True,
        text=True,
    )


def test_factory_executes_render_finalize_attest_then_registry_update(tmp_path):
    result = _run_block(tmp_path)

    assert result.returncode == 0, result.stderr
    calls = (tmp_path / "calls").read_text(encoding="utf-8").splitlines()
    assert "render" in calls[0] and "--manifest" in calls[0]
    assert "finalize-scaffold" in calls[1] and "--manifest" in calls[1]
    assert "verify-private-repo" in calls[2]
    assert calls[3].startswith("registry-update ")


@pytest.mark.parametrize(
    "stage", ["render", "finalize-scaffold", "verify-private-repo"]
)
def test_factory_suppresses_registry_update_after_any_contract_failure(tmp_path, stage):
    result = _run_block(tmp_path, fail_stage=stage)

    assert result.returncode != 0
    calls = (tmp_path / "calls").read_text(encoding="utf-8")
    assert "registry-update" not in calls


def test_factory_recipe_has_no_stdout_manifest_or_pathname_git_mutations():
    text = SKILL.read_text(encoding="utf-8")

    assert "| tee" not in text
    assert re.search(r"render[\s\\]+.*--manifest", text, re.DOTALL)
    assert "CLIENT_WIKI_GIT_AUTHOR_NAME" in text
    assert "CLIENT_WIKI_GIT_AUTHOR_EMAIL" in text
    assert "credential.helper=!gh auth git-credential" in text
    assert "authoritative private registry" in text.lower()
    assert not re.search(r"git(?:\s+-C\s+\S+)?\s+(?:add|commit|push)\b", text)
