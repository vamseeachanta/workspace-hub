#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""cron-audit.py — inventory + classify the CURRENT machine's live crontab (#2969, F2).

This is the fail-closed pre-cutover gate. It reads the live crontab, classifies
every non-ignore line against (a) the workspace-hub scheduled-task catalog and
(b) the `preserved_external` fingerprints (deckhand etc.), and EXITS NON-ZERO if
ANY line is `uncataloged` — so a cutover that would otherwise delete an unknown
live line is blocked until that line is classified.

Classification logic is delegated to the pure core in `cron_transaction.py`
(imported by file path so this CLI and that module stay decoupled).

Usage:
    uv run --no-project --with pyyaml scripts/cron/cron-audit.py [--machine ID] [--json]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

# --- Locations -------------------------------------------------------------

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent.parent  # scripts/cron/ -> scripts/ -> repo root
CATALOG_PATH = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
CLASSES_PATH = REPO_ROOT / "config" / "workstations" / "harness-state-classes.yaml"
CRON_TRANSACTION_PATH = THIS_DIR / "cron_transaction.py"
CRON_RENDER_PATH = THIS_DIR / "cron_render.py"


# --- cron_transaction import (by file path) --------------------------------


def load_cron_transaction(path: Path = CRON_TRANSACTION_PATH):
    """Import cron_transaction.py by file path.

    Coded defensively: if the module is not present yet (it is written in
    parallel), raise a clear error rather than a bare ImportError so the
    operator knows exactly what is missing.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"cron_transaction.py not found at {path}; the cron core module "
            "must be present before running cron-audit."
        )
    spec = importlib.util.spec_from_file_location("cron_transaction", str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"could not build import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_ownership_context(catalog, registry, state_classes, machine_id):
    return load_cron_transaction().build_ownership_context(
        catalog, registry, state_classes, machine_id
    )


def load_cron_render(path: Path = CRON_RENDER_PATH):
    if not path.exists():
        raise FileNotFoundError(f"cron_render.py not found at {path}")
    spec = importlib.util.spec_from_file_location("cron_render", str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"could not build import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cron_render"] = module
    spec.loader.exec_module(module)
    return module


# --- Catalog / classes loading ---------------------------------------------

# A script path like "scripts/foo/bar.sh" or "scripts/foo/bar.py" is the stable,
# machine-independent fragment of a catalog command (PATH=, $WORKSPACE_HUB, and
# log-redirect targets all vary or expand at install time).
_SCRIPT_PATH_RE = re.compile(r"scripts/[\w./-]+\.(?:sh|py)")


def stable_command_fragment(command: str) -> str:
    """Return the most stable substring of a catalog command for matching.

    Prefers the first `scripts/.../<name>.(sh|py)` token (invariant across
    machines). Falls back to the whole single-spaced command when no script
    path is present.
    """
    ct = load_cron_transaction()
    keys = ct.catalog_command_keys([{"command": command}])
    return keys[0] if keys else ""


def _combine_keys(*groups: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for key in group:
            if key and key not in seen:
                out.append(key)
                seen.add(key)
    return out


def _machine_roles(registry: dict, machine_id: str) -> list[str]:
    machine = (registry.get("machines") or {}).get(machine_id, {})
    return ((machine.get("harness_profile") or {}).get("roles")) or []


def _selected_for_machine(catalog: dict, registry: dict, machine_id: str) -> dict:
    ct = load_cron_transaction()
    render = load_cron_render()
    context = render.build_context(machine_id, registry=registry)
    roles = _machine_roles(registry, context["machine_id"])
    selected_raw, conflicts = ct.select_tasks(
        catalog.get("tasks", []) or [],
        roles,
        context.get("tokens", {context["machine_id"]}),
    )
    selected = [render.render_task(task, context) for task in selected_raw]
    return {
        "context": context,
        "roles": roles,
        "selected_raw": selected_raw,
        "selected": selected,
        "selected_task_ids": {task.get("id") for task in selected_raw if task.get("id")},
        "conflicts": conflicts,
    }


def load_catalog_commands(
    path: Path = CATALOG_PATH,
    *,
    registry_path: Path | None = None,
    machine_id: str | None = None,
) -> list[str]:
    """Build catalog_commands: a stable substring per catalog task command."""
    if not path.exists():
        raise FileNotFoundError(f"catalog not found at {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    tasks = data.get("tasks", []) or []
    ct = load_cron_transaction()
    if machine_id is None:
        return ct.catalog_command_keys(tasks, include_fingerprinted=False)

    registry_file = registry_path or (REPO_ROOT / "config" / "workstations" / "registry.yaml")
    registry = yaml.safe_load(registry_file.read_text(encoding="utf-8")) if registry_file.exists() else {}
    selected = _selected_for_machine(data, registry or {}, machine_id)
    return _combine_keys(
        ct.catalog_command_keys(selected["selected_raw"], include_fingerprinted=False),
        ct.catalog_command_keys(selected["selected"], include_fingerprinted=False),
    )


def load_external_fingerprints(path: Path = CLASSES_PATH) -> list[dict]:
    """Read preserved fingerprints from harness-state-classes.yaml.

    Merges preserved_external (other-repo-owned) + preserved_local (this host's own
    non-catalog workspace-hub crons, #2988) — both are the keep-verbatim bucket.
    """
    if not path.exists():
        raise FileNotFoundError(f"state-classes file not found at {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = (data.get("preserved_external", []) or []) + (data.get("preserved_local", []) or [])
    ct = load_cron_transaction()
    return ct.normalize_preserved_entries(entries)


# --- Live crontab ----------------------------------------------------------


class CronReadError(RuntimeError):
    def __init__(self, returncode: int, stderr: str, stdout: str = ""):
        self.returncode = returncode
        self.stderr = stderr
        self.stdout = stdout
        super().__init__(f"`crontab -l` failed (exit {returncode}): {stderr.strip()}")


def read_live_crontab() -> str:
    """Return the current user's live crontab text, or "" if none is installed.

    `crontab -l` exits non-zero with "no crontab for <user>" when empty; that is
    a normal, non-error state for this audit.
    """
    try:
        proc = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        # No crontab binary on this host (e.g. a CI container) — treat as empty.
        return ""
    if proc.returncode != 0:
        stderr = (proc.stderr or "").lower()
        if "no crontab" in stderr:
            return ""
        # A genuine failure (permissions etc.) — surface it.
        raise CronReadError(proc.returncode, proc.stderr or "", proc.stdout or "")
    return proc.stdout


# --- Audit -----------------------------------------------------------------


def audit_crontab(
    crontab_text: str,
    catalog_commands: list[str],
    external_fingerprints: list[dict],
    classify_line,
    selected_task_ids: set[str] | None = None,
    catalog_fingerprints: list[dict] | None = None,
    ownership_context: dict | None = None,
) -> dict:
    """Classify every line; return a structured result."""
    results: list[dict] = []
    counts = {
        "cataloged": 0,
        "preserved_external": 0,
        "uncataloged": 0,
        "ignore": 0,
    }
    for line in crontab_text.split("\n"):
        try:
            detail = classify_line(
                line,
                catalog_commands,
                external_fingerprints,
                selected_task_ids=selected_task_ids,
                catalog_fingerprints=catalog_fingerprints,
                ownership_context=ownership_context,
            )
            if isinstance(detail, str):
                detail = {"line": line, "class": detail}
        except TypeError:
            detail = {"line": line, "class": classify_line(line, catalog_commands, external_fingerprints)}
        cls = detail["class"]
        counts[cls] = counts.get(cls, 0) + 1
        if cls == "ignore":
            continue
        result = dict(detail)
        result.setdefault("line", line)
        result.setdefault("class", cls)
        results.append(result)
    return {
        "lines": results,
        "counts": counts,
        "uncataloged": [r["line"] for r in results if r["class"] == "uncataloged"],
    }


def build_audit_context(machine_id: str | None = None) -> dict:
    catalog = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8")) if CATALOG_PATH.exists() else {}
    registry_path = REPO_ROOT / "config" / "workstations" / "registry.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {}
    target_machine = machine_id
    if target_machine is None:
        render = load_cron_render()
        target_machine = render.build_context(None, registry=registry or {})["machine_id"]

    selected = _selected_for_machine(catalog or {}, registry or {}, target_machine)
    ct = load_cron_transaction()
    catalog_commands = _combine_keys(
        ct.catalog_command_keys(selected["selected_raw"], include_fingerprinted=False),
        ct.catalog_command_keys(selected["selected"], include_fingerprinted=False),
    )
    selected_task_ids = selected["selected_task_ids"]
    machine = selected["context"]["machine_id"]
    state_classes = yaml.safe_load(CLASSES_PATH.read_text(encoding="utf-8")) if CLASSES_PATH.exists() else {}
    ownership = build_ownership_context(
        catalog or {}, registry or {}, state_classes or {}, machine
    )
    return {
        "machine": machine,
        "catalog_commands": catalog_commands,
        "catalog_fingerprints": ct.catalog_owned_fingerprints(selected["selected_raw"]),
        "external_fingerprints": load_external_fingerprints(),
        "selected_task_ids": selected_task_ids,
        "ownership_context": ownership,
    }


# --- Reporting -------------------------------------------------------------


def print_human(machine: str | None, audit: dict) -> None:
    header = "cron-audit"
    if machine:
        header += f" — machine: {machine}"
    print(header)
    print("=" * len(header))
    if not audit["lines"]:
        print("(no classifiable crontab lines)")
    for r in audit["lines"]:
        print(f"  [{r['class']:<18}] {r['line']}")
    print()
    c = audit["counts"]
    print(
        "summary: "
        f"cataloged={c.get('cataloged', 0)} "
        f"preserved_external={c.get('preserved_external', 0)} "
        f"uncataloged={c.get('uncataloged', 0)} "
        f"ignore={c.get('ignore', 0)}"
    )
    if audit["uncataloged"]:
        print()
        print("FAIL: uncataloged live cron line(s) block cutover:")
        for line in audit["uncataloged"]:
            print(f"  - {line}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine", help="machine id label for the report", default=None)
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON instead of text"
    )
    args = parser.parse_args(argv)

    ct = load_cron_transaction()
    context = build_audit_context(args.machine)
    try:
        crontab_text = read_live_crontab()
    except CronReadError as exc:
        payload = {
            "machine": context.get("machine") or args.machine,
            "ok": False,
            "reason": "crontab-read-failed",
            "returncode": exc.returncode,
            "stderr": exc.stderr,
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"FAIL: {payload['reason']}: {payload['stderr']}")
        return 2

    audit = audit_crontab(
        crontab_text,
        context["catalog_commands"],
        context["external_fingerprints"],
        ct.classify_line_detail,
        selected_task_ids=context["selected_task_ids"],
        catalog_fingerprints=context.get("catalog_fingerprints", []),
        ownership_context=context["ownership_context"],
    )

    if args.json:
        print(
            json.dumps(
                {
                    "machine": context.get("machine") or args.machine,
                    "counts": audit["counts"],
                    "lines": audit["lines"],
                    "uncataloged": audit["uncataloged"],
                    "ok": not audit["uncataloged"],
                },
                indent=2,
            )
        )
    else:
        print_human(args.machine, audit)

    # Fail-closed: any uncataloged live line blocks a cutover.
    return 1 if audit["uncataloged"] else 0


if __name__ == "__main__":
    sys.exit(main())
