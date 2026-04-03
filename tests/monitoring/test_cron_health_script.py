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
