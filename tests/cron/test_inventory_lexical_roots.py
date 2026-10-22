"""Declared roots are data; an unrelated filesystem must not rewrite them.

Basis: the existing PurePosixPath branch in cron_render.workspace_hub_path and
issue 3711. The expected line is assembled independently from declared strings.
"""
import hashlib
import importlib.util
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/cron"))
import cron_identity


def test_inventory_root_is_independent_of_realpath(tmp_path, monkeypatch):
    """One task yields one identical identity before and after fake remapping."""
    spec = importlib.util.spec_from_file_location(
        "lexical_inventory", ROOT / "scripts/cron/build-cron-identity-inventory.py",
    )
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    root_component = "home"
    declared = f"/{root_component}/user/ws/workspace-hub"
    machine = "fixture"
    catalog = {"tasks": [{"id": "one", "schedule": "0 1 * * *",
                          "command": "cd $WORKSPACE_HUB && echo one",
                          "machines": [machine]}]}
    registry = {"machines": {machine: {"os": "linux", "workspace_root": declared}}}
    classes = {"preserved_external": [], "preserved_local": []}
    paths = [tmp_path / name for name in ("catalog.yaml", "registry.yaml", "classes.yaml")]
    for path, value in zip(paths, (catalog, registry, classes)):
        path.write_text(yaml.safe_dump(value))
    expected = "0 1 * * * cd " + declared + " && echo one"
    baseline = generator.build(*paths)
    realpath = os.path.realpath

    def remap(path, *args, **kwargs):
        text = os.fsdecode(path)
        if text == declared or text.startswith(declared + "/"):
            return "/System/Volumes/Data" + text
        return realpath(path, *args, **kwargs)

    monkeypatch.setattr(os.path, "realpath", remap)
    assert generator.build(*paths) == baseline
    context = cron_identity.build_ownership_context(catalog, registry, classes, machine)
    assert context["canonical_exact_lines"] == {"one": [expected]}
    assert baseline["identities"] == [{
        "canonical_line_sha256": hashlib.sha256(expected.encode()).hexdigest(),
        "legacy_variant_ids": [], "machine_id": machine, "task_id": "one", "unique": True,
    }]
