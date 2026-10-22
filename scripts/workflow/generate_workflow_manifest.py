#!/usr/bin/env python3
"""Ecosystem workflow discovery-manifest generator — #3284.

Aggregates each tier-1 repo's ``docs/registry/workflows.yaml`` into a single
provenance-stamped ``docs/registry/workflow-manifest.json`` enumerating every
callable workflow with exactly the field-set the reference resolver
``deckhand/src/deckhand/capability_smoke.py`` consumes, so a consumer can
round-trip a manifest entry through ``resolve_workflow()``.

Owner-confirmed decisions baked in (2026-06-28):
- D1: per-repo ``schema_version`` recorded, never assumed (target = v2 additive
  superset). ``invocation`` reads the TOP-LEVEL registry key only with
  ``{input}``-only substitution; ``request_schema``/``response_schema``/``result``
  are STRUCTURED passthrough (null when absent, NO ``str`` coercion).
- D3/D6: ``determinism`` is a reserved-null passthrough (no registry heuristic);
  #3283 (Wave 2) populates it via a key-allowlist.
- D4: ``workflow_id = "repo:id@version"`` + a ``latest`` resolver; per-row
  ``input`` PRESERVED; ``license_gated`` derives from
  ``runtime == 'requires-license'`` (NOT ``network_required``).

Pure aggregation (no engine import). The generator resolves repos via
``resolve_tier1_repo_path`` (SSoT, #3023) — never hardcodes absolute sibling paths.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

# Make scripts/lib importable for the SSoT tier-1 helpers.
_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from lib.tier1_repos import resolve_tier1_repo_path, tier1_python_repos  # noqa: E402

import yaml  # noqa: E402

MANIFEST_VERSION = 1  # manifest-format version (independent of per-repo registry schema_version)
RESOLVER = "deckhand/src/deckhand/capability_smoke.py"
GENERATOR = "scripts/workflow/generate_workflow_manifest.py"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_manifest_path() -> Path:
    return _repo_root() / "docs" / "registry" / "workflow-manifest.json"


def _git_head(repo_path: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0:
            return out.stdout.strip() or None
    except Exception:
        pass
    return None


def load_registry(repo_slug, resolve=resolve_tier1_repo_path):
    """Return ``(raw_text, parsed_dict|None, error|None)``.

    Issue #3450: resolution, absent registry and invalid/unreadable registry
    are distinct observations. Failed observations never carry a usable hash.
    """
    _, raw, parsed, error = _registry_observation(repo_slug, resolve)
    return raw, parsed, error


def _registry_observation(repo_slug, resolve):
    """Bind registry bytes and Git provenance to one resolution result."""
    try:
        repo_path = Path(resolve(repo_slug))
        if not repo_path.is_dir():
            return (None, None, None, "missing-repository")
    except (OSError, RuntimeError, TypeError, ValueError):
        return (None, None, None, "missing-repository")
    reg = repo_path / "docs" / "registry" / "workflows.yaml"
    try:
        raw = reg.read_text(encoding="utf-8")
    except FileNotFoundError:
        return (repo_path, None, None, "missing-registry")
    except (OSError, UnicodeError):
        return (repo_path, None, None, "invalid-registry")
    try:
        parsed = yaml.safe_load(raw)
    except yaml.YAMLError:
        return (repo_path, raw, None, "invalid-registry")
    if not isinstance(parsed, dict):
        return (repo_path, raw, None, "invalid-registry")
    rows = parsed.get("workflows", [])
    if rows is not None and (
        not isinstance(rows, list)
        or any(
            not isinstance(row, dict)
            or not isinstance(row.get("id"), str)
            or not row["id"].strip()
            for row in rows
        )
    ):
        return (repo_path, raw, None, "invalid-registry")
    return (repo_path, raw, parsed, None)


def row_version(row) -> int:
    """Mirror ``capability_smoke._row_version``: an unversioned row is v1."""
    try:
        return int(row.get("version") or 1)
    except (TypeError, ValueError):
        return 1


def normalize_row(repo_slug, registry, row) -> dict:
    ver = row_version(row)
    rid = f"{repo_slug}:{row['id']}"
    return {
        "workflow_id": f"{rid}@{ver}",                     # D4: repo:id@version
        "routing_id": rid,                                 # unversioned routing key
        "id": row["id"],
        "repo": repo_slug,
        "version": ver,
        "status": str(row.get("status") or "stable"),      # routing triple (D1)
        "latest": bool(row.get("latest", False)),
        "basename": row.get("basename"),
        "title": row.get("title"),
        "input": row.get("input"),                         # D4: PRESERVE per-row input
        "outputs": row.get("outputs", []),
        "runtime": row.get("runtime"),
        "invocation": registry.get("invocation"),          # D1: TOP-LEVEL only; {input}-only; NO row['test'] fallback
        "license_gated": (row.get("runtime") == "requires-license"),  # D4: from runtime
        "request_schema": row.get("request_schema"),       # D1: structured passthrough; null when absent
        "response_schema": row.get("response_schema"),     # D1: structured passthrough; null when absent
        "result": row.get("result"),                       # D1: 'result:' descriptor (owned by #3282); null until populated
        "data_source": row.get("data_source"),             # informational; NOT the license gate
        "determinism": None,                               # D3+D6: reserved passthrough; NO heuristic
    }


def latest_by_routing_id(workflows) -> dict:
    """Mirror ``capability_smoke._select_version`` for the unpinned case.

    For each routing_id: a ``latest: true`` stable row if flagged, else the
    highest-version stable row, else the highest-version row of any status.
    """
    groups: dict[str, list[dict]] = {}
    for w in workflows:
        groups.setdefault(w["routing_id"], []).append(w)
    out: dict[str, str] = {}
    for rid, group in groups.items():
        stable = [w for w in group if w["status"] == "stable"]
        flagged = [w for w in stable if w["latest"]]
        pool = flagged or stable or group
        out[rid] = max(pool, key=lambda w: w["version"])["workflow_id"]
    return out


def build_manifest(slugs=None, resolve=resolve_tier1_repo_path) -> dict:
    slugs = list(slugs) if slugs is not None else tier1_python_repos()
    repos: list[dict] = []
    workflows: list[dict] = []
    warnings: list[str] = []

    for slug in slugs:
        repo_path, raw, parsed, err = _registry_observation(slug, resolve)
        if err:
            warnings.append(f"{slug}: {err}")
            repos.append({"repo": slug, "status": err, "registry_sha256": None})
            continue
        sv = parsed.get("schema_version")
        if not parsed.get("invocation"):
            warnings.append(
                f"{slug}: missing top-level 'invocation' (pre-#3295 registry); invocation emitted null"
            )
        git_sha = _git_head(repo_path)
        rows = parsed.get("workflows") or []
        repos.append({
            "repo": slug,
            "schema_version": sv,                          # record per-repo; never assume one
            "registry_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "git_sha": git_sha,
            "row_count": len(rows),
            "status": "ok",
        })
        for row in rows:
            workflows.append(normalize_row(slug, parsed, row))

    workflows = sorted(workflows, key=lambda w: w["workflow_id"])
    return {
        "manifest_version": MANIFEST_VERSION,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "generator": GENERATOR,
        "resolver": RESOLVER,                              # D1: name the reference resolver
        "repos": repos,
        "workflow_count": len(workflows),
        "workflows": workflows,
        "latest_by_routing_id": latest_by_routing_id(workflows),  # D4: materialized latest resolver
        "warnings": warnings,
    }


def write_manifest(path=None, slugs=None, resolve=resolve_tier1_repo_path) -> Path:
    path = Path(path) if path is not None else default_manifest_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(slugs=slugs, resolve=resolve)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(manifest, fp, indent=2, sort_keys=False)
        fp.write("\n")
    return path


def _valid_digest(value) -> bool:
    """Require a complete lowercase SHA-256 hex digest before comparison."""
    return (
        isinstance(value, str)
        and len(value) == len(hashlib.sha256().hexdigest())
        and all(char in "0123456789abcdef" for char in value)
    )


def stale_report(manifest_path=None, slugs=None, resolve=resolve_tier1_repo_path) -> dict:
    """Partition observations per issue #3450; only valid hashes imply drift.

    Missing/invalid saved provenance is an invalid-registry observation with a
    reason, even if live bytes are readable. Equal null hashes never pass.
    """
    manifest_path = Path(manifest_path) if manifest_path is not None else default_manifest_path()
    try:
        saved = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        saved = {}
    fresh = build_manifest(slugs=slugs, resolve=resolve)
    saved_rows = saved.get("repos", []) if isinstance(saved, dict) else []
    if not isinstance(saved_rows, list):
        saved_rows = []
    saved_by_repo = {
        row["repo"]: row for row in saved_rows
        if isinstance(row, dict) and isinstance(row.get("repo"), str)
    }
    fresh_by_repo = {row["repo"]: row for row in fresh["repos"]}
    results = []
    for slug in sorted(saved_by_repo.keys() | fresh_by_repo.keys()):
        old = saved_by_repo.get(slug, {})
        live = fresh_by_repo.get(slug, {})
        status = live.get("status", "missing-repository")
        result = {
            "repo": slug,
            "status": status,
            "saved_registry_sha256": old.get("registry_sha256"),
            "registry_sha256": live.get("registry_sha256"),
        }
        if not live:
            result["reason"] = "not-visited"
        elif status == "ok":
            if old.get("status") != "ok" or not _valid_digest(old.get("registry_sha256")):
                result.update(status="invalid-registry", reason="invalid-saved-observation")
            elif not _valid_digest(live.get("registry_sha256")):
                result.update(status="invalid-registry", reason="invalid-live-observation")
            else:
                result["status"] = (
                    "unchanged" if old["registry_sha256"] == live["registry_sha256"] else "drifted"
                )
        results.append(result)
    return {"ok": all(row["status"] == "unchanged" for row in results), "repos": results}


def check_stale(manifest_path=None, slugs=None, resolve=resolve_tier1_repo_path, *, json_output=False) -> int:
    """Fail closed on drift OR failed observations; exclude generation time."""
    report = stale_report(manifest_path, slugs=slugs, resolve=resolve)
    if json_output:
        print(json.dumps(report, indent=2))
        return int(not report["ok"])
    drift = [row["repo"] for row in report["repos"] if row["status"] == "drifted"]
    if drift:
        print(f"STALE: registries changed since manifest: {drift}", file=sys.stderr)
    for row in report["repos"]:
        if row["status"] == "unchanged":
            print(f"UNCHANGED: {row['repo']}", file=sys.stderr)
        elif row["status"] != "drifted":
            reason = f" ({row['reason']})" if "reason" in row else ""
            print(f"UNAVAILABLE: {row['repo']}: {row['status']}{reason}", file=sys.stderr)
    return int(not report["ok"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Generate or check the ecosystem workflow manifest (#3284).")
    ap.add_argument("--write", action="store_true", help="regenerate the manifest (default)")
    ap.add_argument("--check", action="store_true", help="exit nonzero on drift or failed registry observations")
    ap.add_argument("--json", action="store_true", help="emit a structured --check report")
    ap.add_argument("--output", default=None, help="manifest path override")
    args = ap.parse_args(argv)
    if args.json and not args.check:
        ap.error("--json requires --check")

    if args.check:
        return check_stale(args.output, json_output=args.json)
    path = write_manifest(args.output)
    print(f"wrote workflow manifest to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
