#!/usr/bin/env python3
"""Verification prototype for issue #3711.

Measures, on any POSIX host:
  A. today's host dependence of `cron_render.workspace_hub_path`
  B. that lexical normalisation makes inventory generation byte-identical to the
     committed baseline on BOTH macOS and Linux
  C. that the proposed CI-provable tests are RED on today's `main` on Linux
  D. that regenerating the inventory from git-index bytes reproduces the committed
     artifact (feasibility of a contents check in the enforcement checker)

Read-only.  Writes nothing into the repo.  Never invokes crontab.
Usage: python proto_3711.py <repo-root>
"""
from __future__ import annotations

import importlib.util
import json
import os
import platform
import subprocess
import sys
from pathlib import Path, PurePosixPath

RESULTS: list[tuple[str, str, str]] = []


def record(section: str, name: str, value) -> None:
    RESULTS.append((section, name, str(value)))
    print(f"[{section}] {name}: {value}")


def load(root: Path):
    sys.path.insert(0, str(root / "scripts/cron"))
    spec = importlib.util.spec_from_file_location(
        "bcii", root / "scripts/cron/build-cron-identity-inventory.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    import cron_render
    return mod, cron_render


# ---------------------------------------------------------------- the proposal
def declared_workspace_root(value) -> PurePosixPath:
    """PROPOSED: normalise a registry-declared workspace_root lexically.

    Touches no filesystem: no expanduser(), no resolve(), no stat().
    """
    return PurePosixPath(os.path.normpath(str(value)))


def unfaithful_declared_roots(registry: dict) -> list[tuple[str, str, str]]:
    """PROPOSED fail-closed guard: declared roots that cannot be rendered faithfully."""
    bad = []
    for machine_id, row in sorted((registry.get("machines") or {}).items()):
        if (row or {}).get("os") != "linux":
            continue
        declared = (row or {}).get("workspace_root")
        if declared is None:
            continue
        text = str(declared)
        if not text.startswith("/"):
            bad.append((machine_id, text, "workspace_root is not an absolute POSIX path"))
        elif str(declared_workspace_root(text)) != text:
            bad.append((machine_id, text, "workspace_root is not in normal form"))
    return bad


def patched_workspace_hub_path(cron_render):
    def _fn(workspace_hub=None):
        override = workspace_hub or os.environ.get("WORKSPACE_HUB")
        return declared_workspace_root(override) if override else cron_render.REPO_ROOT
    return _fn


# ------------------------------------------------------------------ A: today
def section_a(root: Path, mod, cron_render, registry):
    for machine_id, row in sorted((registry.get("machines") or {}).items()):
        if (row or {}).get("os") != "linux" or not (row or {}).get("workspace_root"):
            continue
        declared = row["workspace_root"]
        today = str(cron_render.workspace_hub_path(declared))
        fixed = str(declared_workspace_root(declared))
        record("A", f"{machine_id} declared", declared)
        record("A", f"{machine_id} today .resolve()", f"{today}  faithful={today == declared}")
        record("A", f"{machine_id} proposed lexical", f"{fixed}  faithful={fixed == declared}")


# ------------------------------------------- B: byte-identity of the artifact
def _generate(mod) -> bytes:
    return mod.render(mod.build(mod.DEFAULT_CATALOG, mod.DEFAULT_REGISTRY, mod.DEFAULT_CLASSES))


def section_b(root: Path, mod, cron_render):
    committed = (root / "docs/reports/issue-3475-command-identity-inventory.json").read_bytes()
    today = _generate(mod)
    record("B", "today: generated == committed", today == committed)

    original = cron_render.workspace_hub_path
    cron_render.workspace_hub_path = patched_workspace_hub_path(cron_render)
    try:
        fixed = _generate(mod)
    finally:
        cron_render.workspace_hub_path = original
    record("B", "PROPOSED: generated == committed", fixed == committed)
    record("B", "PROPOSED == today", fixed == today)

    cj, tj = json.loads(committed), json.loads(today)
    diff = [(r["machine_id"], r["task_id"]) for r in tj["identities"]
            if r not in cj["identities"]]
    record("B", "today rows differing from committed", sorted(diff))
    record("B", "today input_digest == committed input_digest",
           tj["input_digest"] == cj["input_digest"])
    record("B", "=> wrong rows can carry a correct digest",
           bool(diff) and tj["input_digest"] == cj["input_digest"])


# ------------------------------------ C: the CI-provable tests, on this host
def section_c(root: Path, cron_render, registry, tmp: Path):
    # C1 - symlink fixture, the portable stand-in for the macOS /home firmlink.
    real = tmp / "Volumes" / "Data" / "home" / "undi" / "ws" / "workspace-hub"
    real.mkdir(parents=True, exist_ok=True)
    link = tmp / "home"
    if not link.is_symlink():
        link.symlink_to(tmp / "Volumes" / "Data" / "home")
    declared = f"{link}/undi/ws/workspace-hub"
    synthetic = {"machines": {"gpu-claw-fixture": {
        "os": "linux", "hostname": "gpu-claw-fixture",
        "workspace_root": declared, "schedule_variant": "full"}}}

    today_ctx = cron_render.build_context(
        "gpu-claw-fixture", registry=synthetic, workspace_hub=declared)["workspace_hub"]
    record("C1", "declared", declared)
    record("C1", "today build_context workspace_hub", today_ctx)
    record("C1", "today faithful (test would PASS)", today_ctx == declared)

    original = cron_render.workspace_hub_path
    cron_render.workspace_hub_path = patched_workspace_hub_path(cron_render)
    try:
        fixed_ctx = cron_render.build_context(
            "gpu-claw-fixture", registry=synthetic, workspace_hub=declared)["workspace_hub"]
    finally:
        cron_render.workspace_hub_path = original
    record("C1", "PROPOSED build_context workspace_hub", fixed_ctx)
    record("C1", "PROPOSED faithful (test PASSES)", fixed_ctx == declared)

    # C2 - no-filesystem assertion: forbid every path-resolving syscall, then render.
    def _blow_up(*_a, **_k):
        raise AssertionError("declared workspace_root render touched the filesystem")

    saved = (Path.resolve, Path.expanduser, os.path.realpath, os.stat, os.lstat)
    Path.resolve, Path.expanduser = _blow_up, _blow_up
    os.path.realpath, os.stat, os.lstat = _blow_up, _blow_up, _blow_up
    try:
        try:
            cron_render.workspace_hub_path("/home/undi/ws/workspace-hub")
            today_fs = "PASS (no filesystem access)"
        except AssertionError as exc:
            today_fs = f"FAIL ({exc})"
        patched = patched_workspace_hub_path(cron_render)
        try:
            patched("/home/undi/ws/workspace-hub")
            fixed_fs = "PASS (no filesystem access)"
        except AssertionError as exc:
            fixed_fs = f"FAIL ({exc})"
    finally:
        (Path.resolve, Path.expanduser, os.path.realpath, os.stat, os.lstat) = saved
    record("C2", "today", today_fs)
    record("C2", "PROPOSED", fixed_fs)

    # C3 - the fail-closed guard against the real registry.
    record("C3", "unfaithful declared roots in registry.yaml", unfaithful_declared_roots(registry))
    poisoned = json.loads(json.dumps(registry))
    poisoned["machines"]["gpu-claw"]["workspace_root"] = "~/ws/workspace-hub"
    record("C3", "guard on a '~'-declared root", unfaithful_declared_roots(poisoned))
    poisoned2 = json.loads(json.dumps(registry))
    poisoned2["machines"]["gpu-claw"]["workspace_root"] = "/home/undi/../undi/ws/workspace-hub"
    record("C3", "guard on a non-normal root", unfaithful_declared_roots(poisoned2))


# --------------------------- D: regenerate from git-index bytes (contents check)
def section_d(root: Path, mod, cron_render):
    import yaml
    sources = ["config/scheduled-tasks/schedule-tasks.yaml",
               "config/workstations/registry.yaml",
               "config/workstations/harness-state-classes.yaml"]
    try:
        blobs = {}
        for rel in sources:
            blobs[rel] = subprocess.run(
                ["git", "cat-file", "blob", f":{rel}"], cwd=root, check=True,
                capture_output=True).stdout
        inv_bytes = subprocess.run(
            ["git", "cat-file", "blob", ":docs/reports/issue-3475-command-identity-inventory.json"],
            cwd=root, check=True, capture_output=True).stdout
    except (subprocess.CalledProcessError, OSError) as exc:
        record("D", "git index read", f"UNAVAILABLE: {exc}")
        return
    record("D", "index blobs read", f"{len(blobs)} sources + inventory")

    # Regenerate identity rows from index bytes only, with the proposed lexical render.
    docs = {rel: yaml.safe_load(blobs[rel].decode()) for rel in sources}
    original = cron_render.workspace_hub_path
    cron_render.workspace_hub_path = patched_workspace_hub_path(cron_render)
    try:
        payload = _build_from_documents(mod, docs[sources[0]], docs[sources[1]], docs[sources[2]])
    finally:
        cron_render.workspace_hub_path = original
    committed_inventory = json.loads(inv_bytes)
    record("D", "identities regenerated from index == committed identities",
           payload["identities"] == committed_inventory["identities"])
    record("D", "machines regenerated from index == committed machines",
           payload["machines"] == committed_inventory["machines"])
    record("D", "regenerated row count", len(payload["identities"]))


def _build_from_documents(mod, catalog, registry, classes):
    """PROPOSED pure core of build(): documents in, identity rows out, no Paths."""
    import hashlib
    errors = mod.validate_inventory_inputs(catalog, registry)
    tasks = catalog.get("tasks") if isinstance(catalog, dict) else []
    task_ids = {t.get("id") for t in tasks or [] if isinstance(t, dict)}
    errors = errors + mod.validate_state_classes(classes, task_ids)
    if errors:
        raise ValueError("; ".join(errors))
    machines = sorted(m for m, row in (registry.get("machines") or {}).items()
                      if row.get("os") == "linux")
    rows, unsupported, collisions, bound = [], [], [], set()
    for machine_id in machines:
        mod._build_machine(catalog, registry, classes, machine_id, rows,
                           unsupported, collisions, bound)
    return {"machines": machines, "identities": rows,
            "unsupported": unsupported, "collisions": collisions}


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    tmp = Path(sys.argv[2]) if len(sys.argv) > 2 else root.parent / ".proto3711"
    tmp.mkdir(parents=True, exist_ok=True)
    import yaml
    mod, cron_render = load(root)
    registry = yaml.safe_load((root / "config/workstations/registry.yaml").read_text())
    print(f"=== host={platform.system()} node={platform.node()} root={root} ===")
    section_a(root, mod, cron_render, registry)
    section_b(root, mod, cron_render)
    section_c(root, cron_render, registry, tmp)
    section_d(root, mod, cron_render)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
