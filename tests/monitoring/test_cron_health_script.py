"""Static and behavioral checks for cron-health-check.sh.

ABOUTME: Verifies YAML parsing uses uv-run Python stdin mode and avoids fragile
python -c interpolation for schedule parsing.
"""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "monitoring" / "cron-health-check.sh"
SCHEDULE_PATH = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"


def test_cron_health_avoids_inline_python_c_for_yaml_parsing():
    script = SCRIPT_PATH.read_text()
    assert "uv run --no-project python3 -c" not in script
    assert "uv run --no-project python -c" not in script


def test_cron_health_uses_uv_run_python_stdin_mode():
    script = SCRIPT_PATH.read_text()
    assert "uv run --no-project python -" in script


def test_schedule_yaml_is_loadable():
    import yaml

    with open(SCHEDULE_PATH) as handle:
        data = yaml.safe_load(handle)
    assert isinstance(data, dict)
    assert isinstance(data.get("tasks"), list)
    assert len(data["tasks"]) > 0


# ── macOS registry alias parsing tests (#2240) ──────────────────────────────


def test_registry_includes_macbook_portable():
    """Verify macbook-portable is parseable in registry used by cron-health."""
    import yaml

    registry_path = REPO_ROOT / "config" / "workstations" / "registry.yaml"
    with open(registry_path) as f:
        data = yaml.safe_load(f)
    machines = data.get("machines", {})
    assert "macbook-portable" in machines, (
        f"macbook-portable not in registry. Keys: {list(machines.keys())}"
    )


def test_registry_alias_maps_to_macbook_portable():
    """Verify Vamsees-MacBook-Air.local alias resolves to macbook-portable."""
    import yaml

    registry_path = REPO_ROOT / "config" / "workstations" / "registry.yaml"
    with open(registry_path) as f:
        data = yaml.safe_load(f)
    mac = data["machines"]["macbook-portable"]
    aliases = mac.get("hostname_aliases", [])
    assert "Vamsees-MacBook-Air.local" in aliases, (
        f"Expected Vamsees-MacBook-Air.local in aliases, got {aliases}"
    )


def test_existing_registry_machines_preserved_after_macos_addition():
    """Verify adding macOS entry did not break existing machine entries."""
    import yaml

    registry_path = REPO_ROOT / "config" / "workstations" / "registry.yaml"
    with open(registry_path) as f:
        data = yaml.safe_load(f)
    machines = data.get("machines", {})
    for expected in ("dev-primary", "dev-secondary", "licensed-win-1", "licensed-win-2"):
        assert expected in machines, (
            f"{expected} missing from registry after macOS addition"
        )
