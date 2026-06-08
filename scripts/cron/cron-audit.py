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
    flat = " ".join(command.split())
    m = _SCRIPT_PATH_RE.search(flat)
    if m:
        return m.group(0)
    return flat


def load_catalog_commands(path: Path = CATALOG_PATH) -> list[str]:
    """Build catalog_commands: a stable substring per catalog task command."""
    if not path.exists():
        raise FileNotFoundError(f"catalog not found at {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    tasks = data.get("tasks", []) or []
    fragments: list[str] = []
    for task in tasks:
        command = task.get("command")
        if not command:
            continue
        fragments.append(stable_command_fragment(command))
    return fragments


def load_external_fingerprints(path: Path = CLASSES_PATH) -> list[dict]:
    """Read preserved_external fingerprints from harness-state-classes.yaml."""
    if not path.exists():
        raise FileNotFoundError(f"state-classes file not found at {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get("preserved_external", []) or []
    fingerprints: list[dict] = []
    for entry in entries:
        fp = entry.get("fingerprint")
        if fp:
            fingerprints.append(fp)
    return fingerprints


# --- Live crontab ----------------------------------------------------------


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
        if "no crontab" in stderr or proc.stdout.strip() == "":
            return ""
        # A genuine failure (permissions etc.) — surface it.
        raise RuntimeError(
            f"`crontab -l` failed (exit {proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout


# --- Audit -----------------------------------------------------------------


def audit_crontab(
    crontab_text: str,
    catalog_commands: list[str],
    external_fingerprints: list[dict],
    classify_line,
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
        cls = classify_line(line, catalog_commands, external_fingerprints)
        counts[cls] = counts.get(cls, 0) + 1
        if cls == "ignore":
            continue
        results.append({"line": line, "class": cls})
    return {
        "lines": results,
        "counts": counts,
        "uncataloged": [r["line"] for r in results if r["class"] == "uncataloged"],
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
    catalog_commands = load_catalog_commands()
    external_fingerprints = load_external_fingerprints()
    crontab_text = read_live_crontab()

    audit = audit_crontab(
        crontab_text, catalog_commands, external_fingerprints, ct.classify_line
    )

    if args.json:
        print(
            json.dumps(
                {
                    "machine": args.machine,
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
