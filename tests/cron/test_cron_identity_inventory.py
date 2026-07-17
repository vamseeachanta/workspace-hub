"""Task 2 deterministic cron identity inventory tests."""
from __future__ import annotations

import json
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import yaml
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/cron/build-cron-identity-inventory.py"
SNAPSHOT_HELPER = ROOT / "scripts/lib/git_index_snapshot.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("cron_identity_inventory_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_snapshot_helper():
    assert SNAPSHOT_HELPER.is_file()
    spec = importlib.util.spec_from_file_location("git_index_snapshot_test", SNAPSHOT_HELPER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fixture_paths(tmp_path: Path, tasks: list[dict], classes: object | None = None):
    catalog = tmp_path / "catalog.yaml"
    registry = tmp_path / "registry.yaml"
    state_classes = tmp_path / "classes.yaml"
    output = tmp_path / "inventory.json"
    write_yaml(catalog, {"tasks": tasks})
    write_yaml(registry, {"machines": {"linux-a": {
        "hostname": "host-a", "hostname_aliases": ["alias-a"], "os": "linux",
        "workspace_root": "/canonical/workspace-hub",
        "harness_profile": {"roles": []},
    }}})
    write_yaml(state_classes, classes if classes is not None else {
        "preserved_external": [], "preserved_local": [],
    })
    command = [sys.executable, str(SCRIPT), "--catalog", str(catalog),
               "--registry", str(registry), "--state-classes", str(state_classes),
               "--output", str(output)]
    return catalog, state_classes, output, command


def write_yaml(path: Path, value: object) -> None:
    path.write_text(yaml.safe_dump(value), encoding="utf-8")


def test_inventory_is_deterministic_alias_safe_and_check_bound(tmp_path):
    catalog = tmp_path / "catalog.yaml"
    registry = tmp_path / "registry.yaml"
    classes = tmp_path / "classes.yaml"
    output = tmp_path / "inventory.json"
    write_yaml(catalog, {"tasks": [{
        "id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
        "command": "echo one", "machines": ["linux-a"], "roles": [],
    }]})
    write_yaml(registry, {"machines": {"linux-a": {
        "hostname": "host-a", "hostname_aliases": ["alias-a"], "os": "linux",
        "workspace_root": "/canonical/workspace-hub",
        "harness_profile": {"roles": []},
    }}})
    write_yaml(classes, {"preserved_external": [], "preserved_local": []})
    command = [sys.executable, str(SCRIPT), "--catalog", str(catalog),
               "--registry", str(registry), "--state-classes", str(classes),
               "--output", str(output)]
    assert subprocess.run(command, cwd=ROOT).returncode == 0
    first = output.read_bytes()
    payload = json.loads(first)
    assert payload["machines"] == ["linux-a"]
    assert payload["unsupported"] == []
    assert payload["collisions"] == []
    assert first.endswith(b"\n")
    assert subprocess.run(command + ["--check"], cwd=ROOT).returncode == 0
    equals_command = [
        sys.executable,
        str(SCRIPT),
        f"--catalog={catalog}",
        f"--registry={registry}",
        f"--state-classes={classes}",
        f"--output={output}",
        "--check",
    ]
    assert subprocess.run(equals_command, cwd=ROOT).returncode == 0
    catalog.write_text(catalog.read_text() + "\n", encoding="utf-8")
    assert subprocess.run(command + ["--check"], cwd=ROOT).returncode != 0


def test_inventory_rejects_tracked_input_alias_with_external_output(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--catalog",
            str(ROOT / "config/scheduled-tasks/schedule-tasks.yaml"),
            "--output",
            str(tmp_path / "external.json"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert completed.returncode != 0
    assert "tracked input alias" in completed.stderr


def test_inventory_uses_registry_workspace_not_checkout_environment(tmp_path, monkeypatch):
    generator = load_generator()
    catalog, classes, _output, _command = fixture_paths(tmp_path, [{
        "id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
        "command": "$WORKSPACE_HUB/scripts/run.sh", "machines": ["linux-a"],
        "roles": [],
    }])
    registry = tmp_path / "registry.yaml"
    registry_data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    registry_data["machines"]["linux-a"]["workspace_root"] = "/canonical/workspace-hub"
    write_yaml(registry, registry_data)

    monkeypatch.setenv("WORKSPACE_HUB", "/checkout/one")
    first = generator.build(catalog, registry, classes)
    monkeypatch.setenv("WORKSPACE_HUB", "/checkout/two")
    second = generator.build(catalog, registry, classes)

    assert first == second


def test_generator_source_is_in_versioned_digest_union(tmp_path):
    generator = load_generator()
    assert SCRIPT in generator.SOURCE_PATHS
    first = tmp_path / "first" / SCRIPT.name
    second = tmp_path / "second" / SCRIPT.name
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_bytes(SCRIPT.read_bytes())
    second.write_bytes(SCRIPT.read_bytes() + b"\n# source drift\n")
    assert generator.input_digest([first]) != generator.input_digest([second])


def test_input_digest_uses_posix_repository_paths(tmp_path, monkeypatch):
    generator = load_generator()
    root = tmp_path / "repo"
    source = root / "scripts" / "cron" / "source.py"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"same bytes")
    monkeypatch.setattr(generator, "ROOT", root)
    assert generator.logical_digest_name(source) == "scripts/cron/source.py"


def test_snapshot_helper_and_lockfiles_are_digest_sources():
    generator = load_generator()
    assert SNAPSHOT_HELPER in generator.SOURCE_PATHS
    assert ROOT / "pyproject.toml" in generator.SOURCE_PATHS
    assert ROOT / "uv.lock" in generator.SOURCE_PATHS


def test_post_capture_index_mutation_uses_captured_oids(tmp_path):
    helper = load_snapshot_helper()
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    payload = repo / "payload.txt"
    payload.write_text("captured\n", encoding="utf-8")
    subprocess.run(["git", "add", "payload.txt"], cwd=repo, check=True)
    tree_oid = subprocess.check_output(["git", "write-tree"], cwd=repo, text=True).strip()
    snapshot = helper.capture_tree(repo, tree_oid)
    payload.write_text("later\n", encoding="utf-8")
    subprocess.run(["git", "add", "payload.txt"], cwd=repo, check=True)
    assert snapshot.read_blob("payload.txt") == b"captured\n"


def _two_tree_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True)
    tree_a = subprocess.check_output(["git", "write-tree"], cwd=repo, text=True).strip()
    subprocess.run(["git", "rm", "-q", "--cached", "a.txt"], cwd=repo, check=True)
    (repo / "b.txt").write_text("b\n", encoding="utf-8")
    subprocess.run(["git", "add", "b.txt"], cwd=repo, check=True)
    tree_b = subprocess.check_output(["git", "write-tree"], cwd=repo, text=True).strip()
    return repo, tree_a, tree_b


def test_capture_tree_ignores_git_replace_refs(tmp_path):
    helper = load_snapshot_helper()
    repo, tree_a, tree_b = _two_tree_repo(tmp_path)
    subprocess.run(["git", "replace", tree_a, tree_b], cwd=repo, check=True)
    snapshot = helper.capture_tree(repo, tree_a)
    assert "a.txt" in snapshot.entries
    assert "b.txt" not in snapshot.entries


def test_frozen_index_is_built_from_captured_manifest(tmp_path):
    helper = load_snapshot_helper()
    repo, tree_a, tree_b = _two_tree_repo(tmp_path)
    snapshot = helper.capture_tree(repo, tree_a)
    subprocess.run(["git", "replace", tree_a, tree_b], cwd=repo, check=True)
    root = tmp_path / "isolated"
    root.mkdir()
    env = helper._frozen_git_env(snapshot, root, root / "index")
    paths = subprocess.check_output(
        ["git", "ls-files"], cwd=root, env=env, text=True
    ).splitlines()
    assert paths == ["a.txt"]


@pytest.mark.parametrize("staged_poison", [False, True])
def test_canonical_bootstrap_uses_captured_tree_not_working_files(
    tmp_path, staged_poison
):
    repo = tmp_path / "clone"
    subprocess.run(
        ["git", "-c", "core.longpaths=true", "clone", "-q", "--no-hardlinks",
         str(ROOT), str(repo)], check=True
    )
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=repo, check=True)
    helper_path = repo / "scripts/lib/git_index_snapshot.py"
    poison = b"\nraise SystemExit(97)\n"
    if staged_poison:
        helper_path.write_bytes(helper_path.read_bytes() + poison)
        subprocess.run(["git", "add", "scripts/lib/git_index_snapshot.py"], cwd=repo, check=True)
        clean = subprocess.check_output(
            ["git", "show", "HEAD:scripts/lib/git_index_snapshot.py"], cwd=repo
        )
        helper_path.write_bytes(clean)
    else:
        helper_path.write_bytes(helper_path.read_bytes() + poison)

    workflow = yaml.load(
        (repo / ".github/workflows/scheduler-mutation-main.yml").read_text(),
        Loader=yaml.BaseLoader,
    )
    command = next(
        step["run"]
        for step in workflow["jobs"]["scheduler-mutation-surfaces"]["steps"]
        if "run" in step
    )
    needle = "git --no-replace-objects rev-parse 'HEAD^{tree}'"
    assert command.count(needle) == 1
    command = command.replace(needle, "git --no-replace-objects write-tree")
    hostile = tmp_path / "hostile"
    hostile.mkdir()
    sentinel = tmp_path / "python-customization-ran"
    (hostile / "sitecustomize.py").write_text(
        f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('ran')\n",
        encoding="utf-8",
    )
    env = dict(os.environ, PYTHONPATH=str(hostile))
    hostile_uv_env = tmp_path / "hostile-uv-environment"
    env["UV_PROJECT_ENVIRONMENT"] = str(hostile_uv_env)
    env["UV_PYTHON"] = str(tmp_path / "attacker-python-does-not-exist")
    completed = subprocess.run(["bash", "-c", command], cwd=repo, env=env)
    assert completed.returncode == (1 if staged_poison else 0)
    assert not sentinel.exists()
    assert not hostile_uv_env.exists()


@pytest.mark.parametrize(
    "path",
    [
        "../escape",
        "/absolute",
        "C:/drive",
        "//server/share",
        "dir\\alias",
        "CON/file.txt",
        "trailing./file",
        "dir/file:stream",
        "dir/file?.txt",
        "dir/control\x01.txt",
        "COM¹.txt",
        "LPT².log",
    ],
)
def test_materialization_rejects_unsafe_paths(path):
    helper = load_snapshot_helper()
    entry = helper.Entry("100644", "0" * 40, path)
    with pytest.raises(helper.SnapshotError):
        helper.validate_materialization_entries([entry])


def test_materialization_rejects_case_and_unicode_collisions():
    helper = load_snapshot_helper()
    entries = [
        helper.Entry("100644", "0" * 40, "Dir/file.txt"),
        helper.Entry("100644", "1" * 40, "dir/FILE.txt"),
    ]
    with pytest.raises(helper.SnapshotError):
        helper.validate_materialization_entries(entries)


def test_materialization_rejects_file_directory_prefix_collision():
    helper = load_snapshot_helper()
    entries = [
        helper.Entry("100644", "0" * 40, "node"),
        helper.Entry("100644", "1" * 40, "node/child"),
    ]
    with pytest.raises(helper.SnapshotError):
        helper.validate_materialization_entries(entries)


def test_duplicate_exact_lines_emit_collision_and_non_unique_rows(tmp_path):
    tasks = [
        {"id": task_id, "scheduler": "cron", "schedule": "0 1 * * *",
         "command": "echo same", "machines": ["linux-a"], "roles": []}
        for task_id in ("one", "two")
    ]
    _catalog, _classes, output, command = fixture_paths(tmp_path, tasks)
    assert subprocess.run(command, cwd=ROOT).returncode != 0
    payload = json.loads(output.read_bytes())
    assert payload["collisions"]
    assert {row["unique"] for row in payload["identities"]} == {False}


def test_unsupported_render_is_named_and_fails(tmp_path):
    task = {"id": "bad", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo bad", "machines": ["linux-a"],
            "roles": [{"unsupported": "mapping"}]}
    _catalog, _classes, output, command = fixture_paths(tmp_path, [task])
    assert subprocess.run(command, cwd=ROOT).returncode != 0
    assert json.loads(output.read_bytes())["unsupported"]


def test_unbound_legacy_variant_is_named_and_fails(tmp_path):
    task = {"id": "other", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo other", "machines": ["elsewhere"], "roles": []}
    classes = {"preserved_external": [], "preserved_local": [{
        "owner": "linux-a", "catalog_task_id": "other",
        "legacy_exact_lines": [{"id": "old", "line": "0 1 * * * echo old"}],
    }]}
    _catalog, _classes, output, command = fixture_paths(tmp_path, [task], classes)
    assert subprocess.run(command, cwd=ROOT).returncode != 0
    unsupported = json.loads(output.read_bytes())["unsupported"]
    assert unsupported == [{"error": "legacy variant is not bound in a canonical Linux context",
                            "task_id": "other", "variant_id": "old"}]


@pytest.mark.parametrize("malformed", [None, 7, ["not", "a", "mapping"]])
def test_malformed_state_classes_fail_without_traceback(tmp_path, malformed):
    task = {"id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo one", "machines": ["linux-a"], "roles": []}
    _catalog, state_classes, output, command = fixture_paths(tmp_path, [task])
    state_classes.write_text(yaml.safe_dump(malformed), encoding="utf-8")
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode != 0
    assert not output.exists()
    assert "state classes root must be a mapping" in completed.stderr
    assert "Traceback" not in completed.stderr


@pytest.mark.parametrize(
    ("catalog_data", "registry_data", "message"),
    [
        (None, {"machines": {"linux-a": {"os": "linux"}}}, "catalog root"),
        ({}, {"machines": {"linux-a": {"os": "linux"}}}, "non-empty tasks"),
        ({"tasks": []}, {"machines": {"linux-a": {"os": "linux"}}}, "non-empty tasks"),
        ({"tasks": [{"id": "one"}]}, None, "registry root"),
        ({"tasks": [{"id": "one"}]}, {}, "canonical Linux machine"),
        ({"tasks": [{"id": "one"}]}, {"machines": {}}, "canonical Linux machine"),
        ({"tasks": [{"id": "one"}]}, {"machines": {"win": {"os": "windows"}}},
         "canonical Linux machine"),
    ],
)
def test_inventory_rejects_empty_or_missing_required_roots(
    tmp_path, catalog_data, registry_data, message
):
    catalog = tmp_path / "catalog.yaml"
    registry = tmp_path / "registry.yaml"
    classes = tmp_path / "classes.yaml"
    output = tmp_path / "inventory.json"
    write_yaml(catalog, catalog_data)
    write_yaml(registry, registry_data)
    write_yaml(classes, {"preserved_external": [], "preserved_local": []})
    command = [sys.executable, str(SCRIPT), "--catalog", str(catalog),
               "--registry", str(registry), "--state-classes", str(classes),
               "--output", str(output)]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode != 0
    assert message in completed.stderr
    assert not output.exists()


def test_inventory_rejects_duplicate_task_ids_in_write_and_check_modes(tmp_path):
    task = {"id": "duplicate", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo one", "machines": ["linux-a"], "roles": []}
    catalog, _classes, output, command = fixture_paths(tmp_path, [task, dict(task)])
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode != 0
    assert "duplicate task id" in completed.stderr
    assert not output.exists()
    output.write_text("{}\n", encoding="utf-8")
    checked = subprocess.run(command + ["--check"], cwd=ROOT, text=True, capture_output=True)
    assert checked.returncode != 0
    assert "duplicate task id" in checked.stderr


def test_inventory_rejects_legacy_lines_without_task_binding(tmp_path):
    task = {"id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo one", "machines": ["linux-a"], "roles": []}
    classes = {"preserved_external": [], "preserved_local": [{
        "owner": "local",
        "legacy_exact_lines": [{"id": "old", "line": "0 1 * * * echo old"}],
    }]}
    _catalog, _classes, output, command = fixture_paths(tmp_path, [task], classes)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode != 0
    assert "legacy_exact_lines requires catalog_task_id" in completed.stderr
    assert not output.exists()


@pytest.mark.parametrize(
    "fingerprint",
    [
        {"command_tokens": "python x.py"},
        {"command_tokens": ["python", True]},
        {"cwd_contains": ["/repo"]},
        {"cwd_basename": False},
        {"script_basename": ["x.py"]},
        {"command_contains": 7},
        {"command_contains": []},
    ],
)
def test_inventory_rejects_runtime_incompatible_fingerprint_types(
    tmp_path, fingerprint
):
    task = {"id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo one", "machines": ["linux-a"], "roles": []}
    classes = {"preserved_external": [{
        "owner": "external", "fingerprint": fingerprint,
    }], "preserved_local": []}
    _catalog, _classes, output, command = fixture_paths(tmp_path, [task], classes)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode != 0
    assert "fingerprint" in completed.stderr
    assert not output.exists()
