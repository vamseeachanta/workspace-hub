"""Pytest tests for workstation-handoff.sh and workstation-status.sh."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tarfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
HANDOFF_SCRIPT = REPO_ROOT / "scripts" / "operations" / "workstation-handoff.sh"
STATUS_SCRIPT = REPO_ROOT / "scripts" / "operations" / "workstation-status.sh"
REGISTRY_FILE = REPO_ROOT / "config" / "workstations" / "registry.yaml"


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a subprocess with sane defaults for testing."""
    defaults = dict(capture_output=True, text=True, timeout=60, cwd=str(REPO_ROOT))
    defaults.update(kwargs)
    return subprocess.run(cmd, **defaults)


# ── Handoff tests ─────────────────────────────────────────────────────────────


class TestHandoffDryRun:
    """test_handoff_dry_run_exits_zero"""

    def test_handoff_dry_run_exits_zero(self):
        result = _run(["bash", str(HANDOFF_SCRIPT), "--phase", "1", "--dry-run"])
        assert result.returncode == 0, (
            f"dry-run failed (rc={result.returncode})\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


class TestHandoffCreatesBundle:
    """test_handoff_creates_bundle"""

    def test_handoff_creates_bundle(self, tmp_path: Path):
        output = tmp_path / "handoff-test.tar.gz"
        result = _run([
            "bash", str(HANDOFF_SCRIPT),
            "--phase", "1",
            "--output", str(output),
        ])
        assert result.returncode == 0, (
            f"handoff failed (rc={result.returncode})\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert output.exists(), f"Expected bundle at {output}"
        assert output.stat().st_size > 0, "Bundle is empty"


class TestHandoffBundleContents:
    """test_handoff_bundle_contains_required_files"""

    @pytest.fixture()
    def bundle_path(self, tmp_path: Path) -> Path:
        output = tmp_path / "handoff-contents.tar.gz"
        result = _run([
            "bash", str(HANDOFF_SCRIPT),
            "--phase", "1",
            "--output", str(output),
        ])
        assert result.returncode == 0, (
            f"handoff failed (rc={result.returncode})\nstderr: {result.stderr}"
        )
        return output

    def test_handoff_bundle_contains_required_files(self, bundle_path: Path):
        with tarfile.open(bundle_path, "r:gz") as tar:
            names = tar.getnames()
        assert "handoff/HANDOFF.md" in names, (
            f"HANDOFF.md missing from bundle. Contents: {names}"
        )
        assert "handoff/HANDOFF.json" in names, (
            f"HANDOFF.json missing from bundle. Contents: {names}"
        )

    def test_handoff_json_has_required_fields(self, bundle_path: Path, tmp_path: Path):
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()
        with tarfile.open(bundle_path, "r:gz") as tar:
            tar.extractall(path=extract_dir)

        json_path = extract_dir / "handoff" / "HANDOFF.json"
        assert json_path.exists(), "HANDOFF.json not found after extraction"

        data = json.loads(json_path.read_text())
        required_fields = [
            "version",
            "timestamp",
            "source_machine",
            "phase",
            "git_branch",
            "git_sha",
            "result_branch",
            "files_included",
        ]
        for field in required_fields:
            assert field in data, f"Missing required field '{field}' in HANDOFF.json"

    def test_handoff_md_contains_phase_info(self, bundle_path: Path, tmp_path: Path):
        extract_dir = tmp_path / "extract_md"
        extract_dir.mkdir()
        with tarfile.open(bundle_path, "r:gz") as tar:
            tar.extractall(path=extract_dir)

        md_path = extract_dir / "handoff" / "HANDOFF.md"
        assert md_path.exists(), "HANDOFF.md not found after extraction"

        content = md_path.read_text()
        assert "1" in content, "Phase number not found in HANDOFF.md"
        assert "handoff/" in content, (
            "Expected 'handoff/' branch reference in HANDOFF.md"
        )


class TestHandoffNoPlanningDir:
    """test_handoff_no_planning_dir_fails"""

    def test_handoff_no_planning_dir_fails(self, tmp_path: Path):
        # Create a minimal git repo with no .planning/ directory
        fake_repo = tmp_path / "fake-repo"
        fake_repo.mkdir()

        # Initialize git repo so `git rev-parse --show-toplevel` works
        subprocess.run(
            ["git", "init"],
            cwd=str(fake_repo),
            capture_output=True, text=True, timeout=30,
        )
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "init"],
            cwd=str(fake_repo),
            capture_output=True, text=True, timeout=30,
        )

        # Copy the handoff script and its library so the script can run
        ops_dir = fake_repo / "scripts" / "operations"
        ops_dir.mkdir(parents=True)
        shutil.copy2(str(HANDOFF_SCRIPT), str(ops_dir / "workstation-handoff.sh"))

        lib_src = REPO_ROOT / "scripts" / "lib" / "workstation-lib.sh"
        if lib_src.exists():
            lib_dir = fake_repo / "scripts" / "lib"
            lib_dir.mkdir(parents=True)
            shutil.copy2(str(lib_src), str(lib_dir / "workstation-lib.sh"))

        result = subprocess.run(
            ["bash", str(ops_dir / "workstation-handoff.sh"), "--phase", "1"],
            capture_output=True, text=True, timeout=60,
            cwd=str(fake_repo),
        )
        assert result.returncode != 0, (
            "Expected non-zero exit when .planning/ is missing\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "does not exist" in result.stderr or "Nothing to hand off" in result.stderr, (
            f"Expected error message about missing .planning/\nstderr: {result.stderr}"
        )


# ── Status tests ──────────────────────────────────────────────────────────────


class TestStatusQuick:
    """test_status_quick_exits_zero"""

    def test_status_quick_exits_zero(self):
        result = _run(["bash", str(STATUS_SCRIPT), "--quick"])
        assert result.returncode == 0, (
            f"--quick failed (rc={result.returncode})\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


class TestStatusJson:
    """test_status_json_valid"""

    @pytest.fixture()
    def status_json(self) -> dict:
        result = _run(["bash", str(STATUS_SCRIPT), "--quick", "--json"])
        assert result.returncode == 0, (
            f"--quick --json failed (rc={result.returncode})\nstderr: {result.stderr}"
        )
        data = json.loads(result.stdout)
        return data

    def test_status_json_valid(self, status_json: dict):
        assert "machines" in status_json, "JSON output missing 'machines' key"
        assert isinstance(status_json["machines"], list), "'machines' should be a list"
        assert "timestamp" in status_json, "JSON output missing 'timestamp' key"

    def test_status_json_has_all_registry_machines(self, status_json: dict):
        with open(REGISTRY_FILE) as f:
            registry = yaml.safe_load(f)
        expected_count = len(registry.get("machines", {}))
        actual_count = len(status_json["machines"])
        assert actual_count == expected_count, (
            f"Expected {expected_count} machines from registry, got {actual_count}"
        )

    def test_status_local_machine_detected(self, status_json: dict):
        local_machines = [
            m for m in status_json["machines"] if m.get("status") == "local"
        ]
        assert len(local_machines) == 1, (
            f"Expected exactly 1 machine with status='local', found {len(local_machines)}: "
            f"{[m.get('name') for m in local_machines]}"
        )


# ── macOS registry parity tests (#2240) ─────────────────────────────────────


class TestRegistryMacOSEntry:
    """Verify macbook-portable exists in registry with correct metadata."""

    @pytest.fixture()
    def registry(self) -> dict:
        with open(REGISTRY_FILE) as f:
            return yaml.safe_load(f)

    def test_registry_includes_macbook_portable(self, registry: dict):
        machines = registry.get("machines", {})
        assert "macbook-portable" in machines, (
            f"macbook-portable not in registry. Keys: {list(machines.keys())}"
        )

    def test_macbook_portable_os_is_macos(self, registry: dict):
        mac = registry["machines"]["macbook-portable"]
        assert mac.get("os") == "macos", f"Expected os=macos, got {mac.get('os')}"

    def test_macbook_portable_workspace_root(self, registry: dict):
        mac = registry["machines"]["macbook-portable"]
        assert mac.get("workspace_root") == "/Users/krishna/workspace-hub", (
            f"Expected /Users/krishna/workspace-hub, got {mac.get('workspace_root')}"
        )

    def test_macbook_portable_hostname_alias(self, registry: dict):
        mac = registry["machines"]["macbook-portable"]
        aliases = mac.get("hostname_aliases", [])
        assert "Vamsees-MacBook-Air.local" in aliases, (
            f"Expected Vamsees-MacBook-Air.local in aliases, got {aliases}"
        )

    def test_macbook_portable_schedule_variant_none(self, registry: dict):
        mac = registry["machines"]["macbook-portable"]
        assert mac.get("schedule_variant") == "none", (
            f"Expected schedule_variant=none, got {mac.get('schedule_variant')}"
        )

    def test_existing_machines_preserved(self, registry: dict):
        machines = registry.get("machines", {})
        for expected in ("dev-primary", "dev-secondary", "licensed-win-1"):
            assert expected in machines, (
                f"{expected} missing from registry after macOS addition"
            )
