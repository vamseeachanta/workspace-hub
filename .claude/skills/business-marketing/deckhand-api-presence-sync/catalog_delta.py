#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""catalog_delta.py — compute the weekly delta of Deckhand API paths (workflows).

Reads the Deckhand routing catalog (`domain-workflows.yaml`), normalizes every
workflow row into an "API path" record, and diffs the current set against a saved
snapshot (`state/api-catalog-snapshot.json`). Prints the weekly delta as JSON.

This is the read/compute helper for the `deckhand-api-presence-sync` skill. It has
NO side effects by default (does not write the snapshot, does not touch git/PRs).
Pass `--update-snapshot` ONLY after HITL draft PRs have been opened, per the skill.

Status derivation (single source of the live-vs-roadmap rule):
  - live_public  : artifact_residency == public-sandbox  -> publicly claimable
                   (has a public report.html on deckhand-sandbox)
  - live_private : artifact_residency == client-wiki      -> real delivery, NOT
                   publicly claimable (client-private)
  - internal     : artifact_residency == none             -> router/escalation only
  - roadmap      : a bound channel_domain with NO workflow row yet
                   ("owed later"; escalate-only). Listed, never claimed as capability.

Only `live_public` paths may be claimed on public presence surfaces
(resume / LinkedIn / website / README catalog counts).

Usage:
    uv run --no-project --with pyyaml python catalog_delta.py            # print delta JSON
    uv run --script catalog_delta.py --emit-current                     # print current paths only
    uv run --script catalog_delta.py --catalog <path> --snapshot <path> # override inputs
    uv run --script catalog_delta.py --update-snapshot                  # persist current (post-PR)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# --- Locations (no hardcoded absolute paths; resolve relative to this file) ---
# file -> deckhand-api-presence-sync(0) -> business-marketing(1) -> skills(2)
#      -> .claude(3) -> workspace-hub root(4)
THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SNAPSHOT = THIS_DIR / "state" / "api-catalog-snapshot.json"
# Public report URL scheme for live_public paths (deckhand-sandbox GitHub Pages).
REPORT_URL_BASE = "https://vamseeachanta.github.io/deckhand-sandbox"

STATUS_BY_RESIDENCY = {
    "public-sandbox": "live_public",
    "client-wiki": "live_private",
    "none": "internal",
}


def _default_catalog() -> Path:
    """Resolve the Deckhand catalog without hardcoding an absolute path.

    Precedence: $DECKHAND_CATALOG > $DECKHAND_REPO/... > sibling ../deckhand.
    """
    import os

    if env := os.environ.get("DECKHAND_CATALOG"):
        return Path(env)
    rel = Path("config") / "deckhand" / "routing" / "domain-workflows.yaml"
    if repo := os.environ.get("DECKHAND_REPO"):
        return Path(repo) / rel
    return REPO_ROOT.parent / "deckhand" / rel


def load_catalog(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def extract_paths(catalog: dict) -> list[dict]:
    """Normalize workflow rows + uncovered bound domains into API-path records."""
    paths: list[dict] = []
    workflows = catalog.get("workflows", {}) or {}
    covered_domains: set[str] = set()

    for ref, wf in workflows.items():
        route = wf.get("route", {}) or {}
        residency = wf.get("artifact_residency", "none")
        status = STATUS_BY_RESIDENCY.get(residency, "internal")
        channel_domain = route.get("channel_domain")
        if channel_domain:
            covered_domains.add(channel_domain)
        desc = (wf.get("description") or "").strip().splitlines()
        record = {
            "ref": ref,
            "kind": "workflow",
            "scope": route.get("scope"),
            "channel_domain": channel_domain,
            "subdomains": route.get("subdomains"),
            "residency": residency,
            "status": status,
            "claimable_public": status == "live_public",
            "owner_repo": wf.get("owner_repo"),
            "description": desc[0] if desc else "",
        }
        if status == "live_public":
            record["report_url_hint"] = (
                f"{REPORT_URL_BASE}/.../{ref}/report.html"
            )
        paths.append(record)

    # Roadmap rows: bound channel domains with no workflow row yet ("owed later").
    bound = catalog.get("channel_domain_subdomains", {}) or {}
    for domain, subdomains in bound.items():
        if domain in covered_domains:
            continue
        paths.append({
            "ref": f"roadmap:{domain}",
            "kind": "roadmap",
            "scope": None,
            "channel_domain": domain,
            "subdomains": subdomains or [],
            "residency": "none",
            "status": "roadmap",
            "claimable_public": False,
            "owner_repo": "deckhand",
            "description": f"Bound channel domain '{domain}' — escalate-only, workflow row owed later.",
        })

    paths.sort(key=lambda r: r["ref"])
    return paths


def load_snapshot(path: Path) -> dict:
    if not path.exists():
        return {"paths": []}
    with open(path) as f:
        return json.load(f)


def compute_delta(current: list[dict], snapshot: dict) -> dict:
    prev_by_ref = {p["ref"]: p for p in snapshot.get("paths", [])}
    cur_by_ref = {p["ref"]: p for p in current}

    new_refs = [r for r in cur_by_ref if r not in prev_by_ref]
    removed_refs = [r for r in prev_by_ref if r not in cur_by_ref]
    # Status transitions (e.g., a roadmap row that became live_public).
    changed = []
    for r in cur_by_ref:
        if r in prev_by_ref and cur_by_ref[r]["status"] != prev_by_ref[r].get("status"):
            changed.append({
                "ref": r,
                "from": prev_by_ref[r].get("status"),
                "to": cur_by_ref[r]["status"],
            })

    new_paths = [cur_by_ref[r] for r in sorted(new_refs)]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_as_of": snapshot.get("generated_at"),
        "counts": {
            "current_total": len(current),
            "current_live_public": sum(1 for p in current if p["status"] == "live_public"),
            "new": len(new_refs),
            "removed": len(removed_refs),
            "status_changed": len(changed),
        },
        "new_paths": new_paths,
        "new_live_public": [p for p in new_paths if p["status"] == "live_public"],
        "new_roadmap": [p for p in new_paths if p["status"] == "roadmap"],
        "removed_paths": [prev_by_ref[r] for r in sorted(removed_refs)],
        "status_changed": changed,
    }


def write_snapshot(path: Path, current: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "deckhand/config/deckhand/routing/domain-workflows.yaml",
        "paths": current,
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--catalog", type=Path, default=None,
                    help="Path to domain-workflows.yaml (default: sibling deckhand repo).")
    ap.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT,
                    help="Path to api-catalog-snapshot.json.")
    ap.add_argument("--emit-current", action="store_true",
                    help="Print the current normalized path list and exit (no diff).")
    ap.add_argument("--update-snapshot", action="store_true",
                    help="Persist current paths to the snapshot. Use ONLY after PRs are opened.")
    args = ap.parse_args(argv)

    catalog_path = args.catalog or _default_catalog()
    if not catalog_path.exists():
        print(f"ERROR: catalog not found: {catalog_path}", file=sys.stderr)
        return 1

    catalog = load_catalog(catalog_path)
    current = extract_paths(catalog)

    if args.emit_current:
        json.dump({"source": str(catalog_path), "paths": current}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    snapshot = load_snapshot(args.snapshot)
    delta = compute_delta(current, snapshot)
    json.dump(delta, sys.stdout, indent=2)
    sys.stdout.write("\n")

    c = delta["counts"]
    print(
        f"\n[delta] current={c['current_total']} "
        f"live_public={c['current_live_public']} "
        f"new={c['new']} removed={c['removed']} status_changed={c['status_changed']}",
        file=sys.stderr,
    )

    if args.update_snapshot:
        write_snapshot(args.snapshot, current)
        print(f"[snapshot] updated {args.snapshot}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
