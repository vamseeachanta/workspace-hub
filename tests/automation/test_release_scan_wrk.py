"""TDD tests for release_scan_wrk.py — nightly release-notes scan WRK capture.

Covers: state parsing, version comparison, WRK generation, state update,
idempotency, dry-run, and edge cases.
"""

import os
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# Module under test — imported after fixture setup
SRC = Path(__file__).resolve().parent.parent.parent / "scripts" / "automation"

import importlib
import sys


@pytest.fixture()
def mod():
    """Import release_scan_wrk as a module object."""
    spec = importlib.util.spec_from_file_location(
        "release_scan_wrk", SRC / "release_scan_wrk.py"
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture()
def state_dir(tmp_path):
    """Create a temp workspace with config/ai-tools/ and work-queue dirs."""
    config_dir = tmp_path / "config" / "ai-tools"
    config_dir.mkdir(parents=True)
    pending_dir = tmp_path / ".claude" / "work-queue" / "pending"
    pending_dir.mkdir(parents=True)
    scripts_dir = tmp_path / ".claude" / "work-queue" / "scripts"
    scripts_dir.mkdir(parents=True)
    # Minimal generate-index.py stub
    (scripts_dir / "generate-index.py").write_text("# stub\n")
    return tmp_path


def _write_state(state_dir, versions, scan_at="2026-03-11T00:00:00Z"):
    """Helper: write release-scan-state.yaml."""
    state_file = state_dir / "config" / "ai-tools" / "release-scan-state.yaml"
    data = {
        "last_seen_version": versions,
        "last_scan_at": scan_at,
        "last_scan_by": "nightly",
        "notes": "",
    }
    state_file.write_text(yaml.dump(data, default_flow_style=False))
    return state_file


# ── 1. State YAML parsing ──────────────────────────────────────────


class TestParseState:
    def test_parse_all_providers(self, mod, state_dir):
        """All three providers parsed from state file."""
        _write_state(state_dir, {"claude": "2.1.72", "codex": "0.111.0", "gemini": "0.32.1"})
        state = mod.parse_state(state_dir / "config" / "ai-tools" / "release-scan-state.yaml")
        assert state["claude"] == "2.1.72"
        assert state["codex"] == "0.111.0"
        assert state["gemini"] == "0.32.1"

    def test_parse_empty_versions(self, mod, state_dir):
        """Empty string versions parse as empty string (first-scan scenario)."""
        _write_state(state_dir, {"claude": "", "codex": "", "gemini": ""})
        state = mod.parse_state(state_dir / "config" / "ai-tools" / "release-scan-state.yaml")
        assert state["claude"] == ""
        assert state["codex"] == ""
        assert state["gemini"] == ""

    def test_parse_missing_file_returns_empty(self, mod, tmp_path):
        """Missing state file returns empty dict for all providers."""
        state = mod.parse_state(tmp_path / "nonexistent.yaml")
        assert state == {"claude": "", "codex": "", "gemini": ""}


# ── 2. Version change detection ────────────────────────────────────


class TestDetectChanges:
    def test_new_version_detected(self, mod):
        """Newer version is detected as a change."""
        old = {"claude": "2.1.72", "codex": "0.111.0", "gemini": "0.32.1"}
        current = {"claude": "2.1.74", "codex": "0.111.0", "gemini": "0.32.1"}
        changes = mod.detect_changes(old, current)
        assert len(changes) == 1
        assert changes[0]["provider"] == "claude"
        assert changes[0]["old"] == "2.1.72"
        assert changes[0]["new"] == "2.1.74"

    def test_same_version_no_change(self, mod):
        """Same versions produce no changes."""
        old = {"claude": "2.1.72", "codex": "0.111.0", "gemini": "0.32.1"}
        changes = mod.detect_changes(old, old)
        assert changes == []

    def test_first_scan_detects_all(self, mod):
        """Empty old versions (first scan) detect all current versions."""
        old = {"claude": "", "codex": "", "gemini": ""}
        current = {"claude": "2.1.74", "codex": "0.111.0", "gemini": "0.32.1"}
        changes = mod.detect_changes(old, current)
        assert len(changes) == 3

    def test_downgrade_ignored(self, mod):
        """Downgrade (current < old) produces no change."""
        old = {"claude": "2.1.74", "codex": "0.111.0", "gemini": "0.32.1"}
        current = {"claude": "2.1.72", "codex": "0.111.0", "gemini": "0.32.1"}
        changes = mod.detect_changes(old, current)
        assert changes == []

    def test_unavailable_provider_skipped(self, mod):
        """Provider not installed (empty current) is skipped."""
        old = {"claude": "2.1.72", "codex": "0.111.0", "gemini": "0.32.1"}
        current = {"claude": "2.1.74", "codex": "", "gemini": "0.32.1"}
        changes = mod.detect_changes(old, current)
        assert len(changes) == 1
        assert changes[0]["provider"] == "claude"


# ── 3. WRK content generation ──────────────────────────────────────


class TestGenerateWrkContent:
    def test_single_provider_change(self, mod):
        """WRK body contains the changed provider and version table."""
        changes = [{"provider": "claude", "old": "2.1.72", "new": "2.1.74"}]
        content = mod.generate_wrk_content("WRK-1200", changes)
        assert "WRK-1200" in content
        assert "claude" in content
        assert "2.1.72" in content
        assert "2.1.74" in content
        assert "category: harness" in content
        assert "subcategory: tooling" in content
        assert "priority: medium" in content
        assert "complexity: simple" in content
        assert "/release-notes-adoption" in content

    def test_multi_provider_change(self, mod):
        """WRK body contains all changed providers."""
        changes = [
            {"provider": "claude", "old": "2.1.72", "new": "2.1.74"},
            {"provider": "codex", "old": "0.111.0", "new": "0.112.0"},
        ]
        content = mod.generate_wrk_content("WRK-1200", changes)
        assert "claude" in content
        assert "codex" in content
        assert "2.1.74" in content
        assert "0.112.0" in content


# ── 4. State update ────────────────────────────────────────────────


class TestUpdateState:
    def test_versions_and_timestamp_persisted(self, mod, state_dir):
        """State file updated with new versions and timestamp."""
        state_file = _write_state(
            state_dir, {"claude": "2.1.72", "codex": "0.111.0", "gemini": "0.32.1"}
        )
        changes = [{"provider": "claude", "old": "2.1.72", "new": "2.1.74"}]
        mod.update_state(state_file, changes)
        updated = yaml.safe_load(state_file.read_text())
        assert updated["last_seen_version"]["claude"] == "2.1.74"
        assert updated["last_seen_version"]["codex"] == "0.111.0"  # unchanged
        assert updated["last_scan_by"] == "nightly"
        assert "last_scan_at" in updated

    def test_update_state_missing_file(self, mod, tmp_path):
        """update_state creates the file when it does not exist (first scan)."""
        state_file = tmp_path / "config" / "ai-tools" / "release-scan-state.yaml"
        changes = [{"provider": "claude", "old": "(first scan)", "new": "2.1.74"}]
        mod.update_state(state_file, changes)
        assert state_file.exists()
        updated = yaml.safe_load(state_file.read_text())
        assert updated["last_seen_version"]["claude"] == "2.1.74"
        assert updated["last_scan_by"] == "nightly"


# ── 5. Idempotency ─────────────────────────────────────────────────


class TestIdempotency:
    def test_rerun_same_version_no_wrk(self, mod, state_dir):
        """Re-run with same versions creates no WRK."""
        _write_state(state_dir, {"claude": "2.1.74", "codex": "0.111.0", "gemini": "0.32.1"})
        current = {"claude": "2.1.74", "codex": "0.111.0", "gemini": "0.32.1"}
        state = mod.parse_state(state_dir / "config" / "ai-tools" / "release-scan-state.yaml")
        changes = mod.detect_changes(state, current)
        assert changes == []


class TestNoOpTimestamp:
    def test_no_change_updates_scan_timestamp(self, mod, state_dir):
        """No-op scan still updates last_scan_at for cron health auditing."""
        state_file = _write_state(
            state_dir,
            {"claude": "2.1.74", "codex": "0.111.0", "gemini": "0.32.1"},
            scan_at="2026-03-10T00:00:00Z",
        )
        mod.run_scan(
            workspace_root=state_dir,
            current_versions={"claude": "2.1.74", "codex": "0.111.0", "gemini": "0.32.1"},
            dry_run=False,
        )
        updated = yaml.safe_load(state_file.read_text())
        # Timestamp should be refreshed (not the old 2026-03-10)
        assert updated["last_scan_at"] != "2026-03-10T00:00:00Z"
        assert updated["last_scan_by"] == "nightly"


class TestDynamicHostname:
    def test_computer_field_uses_platform_node(self, mod):
        """WRK content uses runtime hostname, not hardcoded value."""
        import platform as _p

        changes = [{"provider": "claude", "old": "2.1.72", "new": "2.1.74"}]
        content = mod.generate_wrk_content("WRK-9999", changes)
        expected_host = _p.node() or "unknown"
        assert f"computer: {expected_host}" in content

    def test_computer_field_override(self, mod):
        """Explicit computer parameter overrides hostname detection."""
        changes = [{"provider": "claude", "old": "2.1.72", "new": "2.1.74"}]
        content = mod.generate_wrk_content("WRK-9999", changes, computer="acma-ansys05")
        assert "computer: acma-ansys05" in content


# ── 6. Dry-run ──────────────────────────────────────────────────────


class TestDryRun:
    def test_dry_run_no_file_writes(self, mod, state_dir):
        """Dry-run mode does not write WRK or update state."""
        state_file = _write_state(
            state_dir, {"claude": "2.1.72", "codex": "", "gemini": ""}
        )
        original_state = state_file.read_text()
        changes = [{"provider": "claude", "old": "2.1.72", "new": "2.1.74"}]
        # run_scan with dry_run=True should not create files
        pending_dir = state_dir / ".claude" / "work-queue" / "pending"
        existing_files = set(pending_dir.iterdir())
        mod.run_scan(
            workspace_root=state_dir,
            current_versions={"claude": "2.1.74", "codex": "", "gemini": ""},
            dry_run=True,
        )
        # No new files in pending
        new_files = set(pending_dir.iterdir()) - existing_files
        assert len(new_files) == 0
        # State file unchanged
        assert state_file.read_text() == original_state
