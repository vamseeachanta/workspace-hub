"""Tests for schedule-tasks.yaml validator."""

import subprocess
import sys
import os
import importlib.util
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEDULE_FILE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
VALIDATOR = REPO_ROOT / "scripts" / "cron" / "validate-schedule.py"
SETUP_CRON = REPO_ROOT / "scripts" / "cron" / "setup-cron.sh"
CRON_RENDER = REPO_ROOT / "scripts" / "cron" / "cron_render.py"
CRON_APPLY = REPO_ROOT / "scripts" / "cron" / "cron_apply.py"
STATE_CLASSES = REPO_ROOT / "config" / "workstations" / "harness-state-classes.yaml"

REQUIRED_TASK_FIELDS = {"id", "label", "schedule", "machines", "command", "description"}
VALID_SCHEDULERS = {"cron", "windows-task-scheduler"}
REGISTRY_FILE = REPO_ROOT / "config" / "workstations" / "registry.yaml"


def _valid_machines_from_registry() -> set[str]:
    with open(REGISTRY_FILE) as f:
        data = yaml.safe_load(f)
    machines: set[str] = set()
    for name, machine in data.get("machines", {}).items():
        machines.add(name)
        machines.add(machine["hostname"])
        machines.update(machine.get("hostname_aliases", []))
    return machines


VALID_MACHINES = _valid_machines_from_registry()


def test_normal_validation_rejects_catalog_task_on_substring_identity(tmp_path):
    catalog = tmp_path / "catalog.yaml"
    classes = tmp_path / "classes.yaml"
    catalog.write_text(SCHEDULE_FILE.read_text(), encoding="utf-8")
    classes.write_text(
        "preserved_external: []\npreserved_local:\n"
        "  - owner: local\n    catalog_task_id: notification-purge\n"
        "    fingerprint: {command_contains: notification}\n",
        encoding="utf-8",
    )
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR), "--catalog", str(catalog),
         "--state-classes", str(classes)],
        cwd=REPO_ROOT, text=True, capture_output=True,
    )
    assert completed.returncode != 0
    assert "catalog_task_id requires legacy_exact_lines" in completed.stdout


def test_normal_validation_rejects_unbound_legacy_exact_lines(tmp_path):
    catalog = tmp_path / "catalog.yaml"
    classes = tmp_path / "classes.yaml"
    catalog.write_text(SCHEDULE_FILE.read_text(), encoding="utf-8")
    classes.write_text(
        "preserved_external: []\npreserved_local:\n"
        "  - owner: local\n"
        "    legacy_exact_lines: [{id: old, line: '0 1 * * * echo old'}]\n",
        encoding="utf-8",
    )
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR), "--catalog", str(catalog),
         "--state-classes", str(classes)],
        cwd=REPO_ROOT, text=True, capture_output=True,
    )
    assert completed.returncode != 0
    assert "legacy_exact_lines requires catalog_task_id" in completed.stdout


def test_state_class_schema_is_closed():
    validator = _load_module("validate_schedule_state_classes", VALIDATOR)
    task_ids = {"owned"}
    invalid = [
        {"unknown_top": []},
        {"preserved_external": [{"owner": "x", "fingerprint": {
            "command_contains": "x"}, "unknown": True}]},
        {"preserved_external": [{"owner": "x", "fingerprint": {
            "unknown_key": "x"}}]},
        {"preserved_external": [{"owner": "x", "fingerprint": {
            "command_contains": []}}]},
        {"preserved_local": [{"owner": "x", "legacy_exact_lines": [
            {"id": "old", "line": "0 1 * * * echo old"}]}]},
    ]
    for classes in invalid:
        assert validator.validate_state_classes(classes, task_ids), classes


@pytest.mark.parametrize(
    "fingerprint",
    [
        {"command_tokens": "python x.py"},
        {"command_tokens": []},
        {"command_tokens": ["python", True]},
        {"cwd_contains": ["/repo"]},
        {"cwd_contains": True},
        {"cwd_basename": ["repo"]},
        {"script_basename": ["x.py"]},
        {"command_contains": True},
        {"command_contains": 7},
        {"command_contains": []},
        {"command_contains": ["x", False]},
    ],
)
def test_normal_validation_rejects_runtime_incompatible_fingerprint_types(
    tmp_path, fingerprint
):
    catalog = tmp_path / "catalog.yaml"
    classes = tmp_path / "classes.yaml"
    catalog.write_text(SCHEDULE_FILE.read_text(), encoding="utf-8")
    classes.write_text(yaml.safe_dump({
        "preserved_external": [{"owner": "external", "fingerprint": fingerprint}],
        "preserved_local": [],
    }), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR), "--catalog", str(catalog),
         "--state-classes", str(classes)],
        cwd=REPO_ROOT, text=True, capture_output=True,
    )
    assert completed.returncode != 0
    assert "fingerprint" in completed.stdout


@pytest.fixture(scope="module")
def schedule_data():
    assert SCHEDULE_FILE.exists(), f"{SCHEDULE_FILE} does not exist"
    with open(SCHEDULE_FILE) as f:
        data = yaml.safe_load(f)
    return data


@pytest.fixture(scope="module")
def tasks(schedule_data):
    return schedule_data.get("tasks", [])


def test_schedule_file_exists():
    assert SCHEDULE_FILE.exists()


def test_has_tasks_key(schedule_data):
    assert "tasks" in schedule_data
    assert isinstance(schedule_data["tasks"], list)
    assert len(schedule_data["tasks"]) > 0


def test_each_task_has_required_fields(tasks):
    for task in tasks:
        missing = REQUIRED_TASK_FIELDS - set(task.keys())
        assert not missing, f"Task {task.get('id', '?')} missing fields: {missing}"


def test_unique_task_ids(tasks):
    ids = [t["id"] for t in tasks]
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {[i for i in ids if ids.count(i) > 1]}"


def test_machines_are_valid(tasks):
    for task in tasks:
        for machine in task["machines"]:
            assert machine in VALID_MACHINES, (
                f"Task {task['id']} has unknown machine: {machine}"
            )


def test_scheduler_is_valid(tasks):
    for task in tasks:
        scheduler = task.get("scheduler", "cron")
        assert scheduler in VALID_SCHEDULERS, (
            f"Task {task['id']} has invalid scheduler: {scheduler}"
        )


def test_cron_schedule_format(tasks):
    """Cron tasks must have 5-field cron expressions."""
    for task in tasks:
        if task.get("scheduler", "cron") != "cron":
            continue
        parts = task["schedule"].split()
        assert len(parts) == 5, (
            f"Task {task['id']} schedule '{task['schedule']}' is not 5-field cron"
        )


def test_command_is_nonempty(tasks):
    for task in tasks:
        assert task["command"].strip(), f"Task {task['id']} has empty command"


def _invokes_claude_cli(command: str) -> bool:
    """Check if a command invokes the claude CLI (not just references .claude/ paths)."""
    import re
    return bool(re.search(r'\bclaude\b(?!\s*[/-])', command)) and \
        not all(m.start() == command.find('.claude') for m in re.finditer(r'\bclaude\b', command) if '.claude' in command[max(0,m.start()-1):m.start()+7])


def test_is_claude_task_field(tasks):
    """Tasks that invoke the claude CLI should have is_claude_task: true."""
    for task in tasks:
        if task.get("is_claude_task") is True:
            # If marked as claude task, that's fine — trust the annotation
            continue
        # Only flag if the command directly invokes `claude` as a CLI tool
        cmd = task["command"]
        # Simple heuristic: "claude " or "claude --" at word boundary, not ".claude/"
        import re
        if re.search(r'(?<!\.)(?<!/)\bclaude\s+--', cmd):
            assert task.get("is_claude_task") is True, (
                f"Task {task['id']} invokes claude CLI but is_claude_task != true"
            )


def test_linux_tasks_have_cron_scheduler(tasks):
    """Linux machines should use cron scheduler."""
    linux_machines = {"dev-primary", "dev-secondary", "gali-linux-compute-1"}
    for task in tasks:
        if set(task["machines"]) & linux_machines:
            assert task.get("scheduler", "cron") == "cron", (
                f"Task {task['id']} targets Linux machines but scheduler != cron"
            )


def test_windows_tasks_have_windows_scheduler(tasks):
    """Windows-only tasks should use windows-task-scheduler."""
    windows_machines = {"ace-win-1", "ace-win-2", "licensed-win-1", "licensed-win-2"}
    for task in tasks:
        if set(task["machines"]) <= windows_machines:
            assert task.get("scheduler", "cron") == "windows-task-scheduler", (
                f"Task {task['id']} targets only Windows but scheduler != windows-task-scheduler"
            )


def test_validator_script_passes():
    """The validator script itself should exit 0."""
    env = os.environ.copy()
    env["UV_CACHE_DIR"] = str(REPO_ROOT / ".claude" / "state" / "uv-cache")
    result = subprocess.run(
        ["uv", "run", "--no-project", "python", str(VALIDATOR)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )
    assert result.returncode == 0, f"Validator failed:\n{result.stderr}\n{result.stdout}"


def test_dev_primary_has_comprehensive_learning(tasks):
    """Comprehensive learning must be scheduled on dev-primary."""
    found = any(
        t["id"] == "comprehensive-learning" and "dev-primary" in t["machines"]
        for t in tasks
    )
    assert found, "comprehensive-learning task not found for dev-primary"


def test_repo_sync_on_all_linux(tasks):
    """Repository sync should be on all Linux machines."""
    sync_tasks = [t for t in tasks if t["id"] == "repository-sync"]
    assert sync_tasks, "No repository-sync task found"
    machines = set()
    for t in sync_tasks:
        machines.update(t["machines"])
    assert "dev-primary" in machines
    assert "dev-secondary" in machines


def test_repository_sync_runtime_contract_is_bounded_and_singleton(tasks):
    task = next(t for t in tasks if t["id"] == "repository-sync")
    runtime = task["runtime"]
    assert runtime == {
        "singleton": True,
        "max_seconds": 10800,
        "state_dir": ".claude/state/cron-runtime/repository-sync",
        "filesystem_wait_wchans": ["request_wait_answer"],
    }
    assert "installed_fingerprint" not in task


def test_hermes_bridge_uses_canonical_rendered_identity(tasks):
    task = next(t for t in tasks if t["id"] == "hermes-claude-bridge")
    assert "installed_fingerprint" not in task


def test_deckhand_presence_sync_has_exact_installed_fingerprint(tasks):
    task = next(t for t in tasks if t["id"] == "deckhand-api-presence-sync")

    assert task["installed_fingerprint"] == {
        "command_tokens": [
            "python",
            ".claude/skills/business-marketing/deckhand-api-presence-sync/catalog_delta.py",
        ],
        "cwd_basename": "workspace-hub",
    }


def test_installed_fingerprint_schema_rejects_broad_or_malformed_values():
    validator = _load_module("validate_schedule_fingerprint", VALIDATOR)

    invalid = [
        {},
        {"command_contains": "deckhand"},
        {"command_token": "x.py", "cwd_basename": "workspace-hub"},
        {"command_tokens": ["python", "x.py"]},
        {"command_tokens": [], "cwd_basename": "workspace-hub"},
        {"command_tokens": ["python", "x.py"], "cwd_basename": ""},
        {"command_tokens": ["python", "x.py"], "owner_repo": "workspace-hub"},
        {"command_tokens": ["python", "x.py"], "cwd_basename": "workspace-hub", "unknown": "x"},
    ]
    for fingerprint in invalid:
        assert validator.validate_installed_fingerprint("task-a", fingerprint)

    assert validator.validate_installed_fingerprint(
        "task-a", {"command_tokens": ["python", "x.py"], "cwd_basename": "workspace-hub"}
    ) == []


@pytest.mark.parametrize("max_seconds", [59, 604801, 0, "10800"])
def test_runtime_max_seconds_must_be_integer_in_fixed_range(max_seconds):
    validator = _load_module("validate_schedule_runtime", VALIDATOR)
    errors = validator.validate_runtime_contract(
        "task-a",
        {
            "singleton": True,
            "max_seconds": max_seconds,
            "state_dir": ".claude/state/cron-runtime/task-a",
        },
        set(),
    )
    assert any("max_seconds" in error for error in errors)


@pytest.mark.parametrize("state_dir", ["/tmp/state", "../state", ".state/../escape"])
def test_runtime_state_dir_rejects_absolute_and_traversal(state_dir):
    validator = _load_module("validate_schedule_runtime_path", VALIDATOR)
    errors = validator.validate_runtime_contract(
        "task-a",
        {"singleton": True, "max_seconds": 60, "state_dir": state_dir},
        set(),
    )
    assert any("state_dir" in error for error in errors)


@pytest.mark.parametrize(
    "log_path",
    [
        "logs/bad path.log", "../logs/x.log", "/tmp/x.log", "logs/{a,b}.log",
        "logs/foo?.log", "logs/foo;bar.log", "logs/foo$(date).log",
    ],
)
def test_log_path_rejects_shell_splitting_and_unsafe_globs(log_path):
    validator = _load_module("validate_schedule_log_path", VALIDATOR)

    assert validator.validate_log_path("task-a", log_path)


@pytest.mark.parametrize("log_path", ["logs/research/*.log", "~/.deckhand/alarm.log"])
def test_log_path_accepts_controlled_workspace_and_home_patterns(log_path):
    validator = _load_module("validate_schedule_valid_log_path", VALIDATOR)

    assert validator.validate_log_path("task-a", log_path) == []


def test_repo_ecosystem_hygiene_task_contract(tasks):
    task = next((t for t in tasks if t["id"] == "repo-ecosystem-hygiene"), None)
    assert task is not None, "repo-ecosystem-hygiene task not found"
    ids = [t["id"] for t in tasks]
    assert ids.index("repo-ecosystem-hygiene") < ids.index("cron-health")
    assert task["schedule"] == "35 5 * * *"
    assert set(task["machines"]) >= {"dev-primary", "ace-linux-1", "vamsee-linux1"}
    assert task["requires"] == ["bash", "python3", "uv", "git", "gh", "timeout"]
    assert task["log"] == "logs/quality/repo-ecosystem-hygiene-*.log"
    assert task["stale_after_hours"] == 23
    assert "PATH=$HOME/.local/bin:$HOME/.npm-global/bin:$PATH" in task["command"]
    assert "repo-ecosystem-hygiene-audit.sh" in task["command"]
    assert "logs/quality/repo-ecosystem-hygiene-$(date +\\%Y\\%m\\%d).log" in task["command"]
    cron_health = next(t for t in tasks if t["id"] == "cron-health")
    assert set(task["machines"]) <= set(cron_health["machines"])


def test_setup_cron_installs_audit_and_health_for_hostname_alias(tmp_path):
    _install_empty_crontab_shim(tmp_path)
    hostname_shim = tmp_path / "hostname"
    hostname_shim.write_text("#!/usr/bin/env bash\nprintf 'vamsee-linux1\\n'\n")
    hostname_shim.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"
    env["WORKSPACE_HUB"] = str(REPO_ROOT)
    env["UV_CACHE_DIR"] = str(REPO_ROOT / ".claude" / "state" / "uv-cache")
    result = subprocess.run(
        ["bash", str(SETUP_CRON), "--dry-run"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "repo-ecosystem-hygiene-audit.sh" in result.stdout
    assert "cron-health-check.sh" in result.stdout


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _install_empty_crontab_shim(tmp_path: Path) -> None:
    shim = tmp_path / "crontab"
    shim.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"${1:-}\" == \"-l\" ]]; then echo 'no crontab for test' >&2; exit 1; fi\n"
        "exit 2\n"
    )
    shim.chmod(0o755)


def test_setup_cron_and_cron_apply_use_shared_renderer_for_same_task(tmp_path):
    _install_empty_crontab_shim(tmp_path)
    hostname_shim = tmp_path / "hostname"
    hostname_shim.write_text("#!/usr/bin/env bash\nprintf 'ace-linux-1\\n'\n")
    hostname_shim.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"
    env["WORKSPACE_HUB"] = str(REPO_ROOT)
    env["UV_CACHE_DIR"] = str(REPO_ROOT / ".claude" / "state" / "uv-cache")

    result = subprocess.run(
        ["bash", str(SETUP_CRON), "--dry-run"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )
    assert result.returncode == 0, result.stderr + result.stdout

    render = _load_module("cron_render_validate", CRON_RENDER)
    cron_apply = _load_module("cron_apply_validate", CRON_APPLY)
    catalog = yaml.safe_load(SCHEDULE_FILE.read_text(encoding="utf-8"))
    registry = yaml.safe_load(REGISTRY_FILE.read_text(encoding="utf-8"))
    repo_sync = next(task for task in catalog["tasks"] if task["id"] == "repository-sync")
    workspace_root = registry["machines"]["dev-primary"]["workspace_root"]
    context = render.build_context(
        "ace-linux-1", registry=registry, workspace_hub=workspace_root
    )
    expected_line = render.render_task(repo_sync, context)["line"]
    apply_plan = cron_apply.run_cutover("ace-linux-1", apply=False, ts="t", _read=lambda: "")

    assert expected_line in result.stdout
    assert expected_line in apply_plan["new_text"]


def test_setup_cron_delegates_placeholder_rendering_to_shared_renderer():
    source = SETUP_CRON.read_text(encoding="utf-8")
    assert "cron_render.py" in source
    assert ".replace('\\$WORKSPACE_HUB'" not in source
    assert ".replace('\\$LOG'" not in source


def test_setup_cron_dry_run_expands_workspace_hub_and_log(tmp_path):
    _install_empty_crontab_shim(tmp_path)
    hostname_shim = tmp_path / "hostname"
    hostname_shim.write_text("#!/usr/bin/env bash\nprintf 'ace-linux-1\\n'\n")
    hostname_shim.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"
    env["WORKSPACE_HUB"] = str(REPO_ROOT)
    env["UV_CACHE_DIR"] = str(REPO_ROOT / ".claude" / "state" / "uv-cache")

    result = subprocess.run(
        ["bash", str(SETUP_CRON), "--dry-run"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "$WORKSPACE_HUB" not in result.stdout
    assert "$LOG" not in result.stdout
    registry = yaml.safe_load(REGISTRY_FILE.read_text(encoding="utf-8"))
    assert registry["machines"]["dev-primary"]["workspace_root"] in result.stdout
    assert "scripts/cron-repository-sync.sh" in result.stdout
    assert "/tmp/workspace-hub-cron.log" not in result.stdout


def test_setup_cron_renderer_failure_aborts_before_crontab_write(tmp_path):
    hostname_shim = tmp_path / "hostname"
    hostname_shim.write_text("#!/usr/bin/env bash\nprintf 'ace-linux-1\\n'\n")
    hostname_shim.chmod(0o755)

    crontab_marker = tmp_path / "crontab-invoked"
    crontab_shim = tmp_path / "crontab"
    crontab_shim.write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" >> {crontab_marker}\n"
        "if [[ \"${1:-}\" == \"-l\" ]]; then exit 0; fi\n"
        "if [[ \"${1:-}\" == \"-\" ]]; then cat >/dev/null; exit 0; fi\n"
        "exit 0\n"
    )
    crontab_shim.chmod(0o755)

    uv_count = tmp_path / "uv-count"
    uv_shim = tmp_path / "uv"
    uv_shim.write_text(
        "#!/usr/bin/env bash\n"
        f"count_file={uv_count}\n"
        "count=0\n"
        "[[ -f \"$count_file\" ]] && count=$(cat \"$count_file\")\n"
        "count=$((count + 1))\n"
        "printf '%s' \"$count\" > \"$count_file\"\n"
        "if [[ \"$count\" == \"1\" ]]; then printf 'full\\n'; exit 0; fi\n"
        "printf 'partial cron line\\n'\n"
        "printf 'renderer exploded\\n' >&2\n"
        "exit 3\n"
    )
    uv_shim.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"
    env["WORKSPACE_HUB"] = str(REPO_ROOT)
    env["UV_CACHE_DIR"] = str(REPO_ROOT / ".claude" / "state" / "uv-cache")

    result = subprocess.run(
        ["bash", str(SETUP_CRON)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )

    assert result.returncode != 0
    assert "renderer exploded" in result.stderr
    assert "partial cron line" not in result.stdout
    assert not crontab_marker.exists()
