"""Tests for contract path resolver."""
import os
from pathlib import Path

import pytest


def test_resolve_finds_folder_skill_contract(tmp_path):
    """Contract found in folder-skill location."""
    from resolve_contract import resolve_contract_path

    stage_dir = tmp_path / ".claude/skills/workspace-hub/stages/stage-01-capture"
    stage_dir.mkdir(parents=True)
    (stage_dir / "contract.yaml").write_text("name: Capture\n")

    result = resolve_contract_path(1, str(tmp_path))
    assert result is not None
    assert result.endswith("contract.yaml")
    assert "stage-01-capture" in result


def test_resolve_falls_back_to_old_location(tmp_path):
    """Falls back to scripts/work-queue/stages/ if folder-skill missing."""
    from resolve_contract import resolve_contract_path

    old_dir = tmp_path / "scripts/work-queue/stages"
    old_dir.mkdir(parents=True)
    (old_dir / "stage-01-capture.yaml").write_text("name: Capture\n")

    result = resolve_contract_path(1, str(tmp_path))
    assert result is not None
    assert "scripts/work-queue/stages" in result


def test_resolve_returns_none_when_missing(tmp_path):
    """Returns None when no contract found anywhere."""
    from resolve_contract import resolve_contract_path

    result = resolve_contract_path(99, str(tmp_path))
    assert result is None


def test_resolve_stages_dir():
    """resolve_stages_dir returns folder-skill stages path."""
    from resolve_contract import resolve_stages_dir

    result = resolve_stages_dir("/fake/repo")
    assert result == "/fake/repo/.claude/skills/workspace-hub/stages"
