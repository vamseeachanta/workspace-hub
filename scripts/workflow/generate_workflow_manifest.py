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
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0:
            return out.stdout.strip() or None
    except Exception:
        pass
    return None


def load_registry(repo_slug, resolve=resolve_tier1_repo_path):
    """Return ``(raw_text, parsed_dict|None, error|None)``.

    ``error`` is ``"missing-registry"`` (no file / unresolvable repo) or
    ``"unparseable-registry"`` (invalid YAML or non-dict top-level). Robustness
    contract per wed#450.
    """
    try:
        repo_path = resolve(repo_slug)
    except Exception:
        return (None, None, "missing-registry")
    reg = Path(repo_path) / "docs" / "registry" / "workflows.yaml"
    if not reg.is_file():
        return (None, None, "missing-registry")
    raw = reg.read_text(encoding="utf-8")
    try:
        parsed = yaml.safe_load(raw)
    except Exception:
        return (raw, None, "unparseable-registry")
    if not isinstance(parsed, dict):
        return (raw, None, "unparseable-registry")
    return (raw, parsed, None)


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
        raw, parsed, err = load_registry(slug, resolve=resolve)
        if err:
            warnings.append(f"{slug}: {err}")
            repos.append({"repo": slug, "status": err, "registry_sha256": None})
            continue
        sv = parsed.get("schema_version")
        if not parsed.get("invocation"):
            warnings.append(
                f"{slug}: missing top-level 'invocation' (pre-#3295 registry); invocation emitted null"
            )
        try:
            repo_path = resolve(slug)
            git_sha = _git_head(Path(repo_path))
        except Exception:
            git_sha = None
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
            if not isinstance(row, dict) or "id" not in row:
                warnings.append(f"{slug}: row missing id")
                continue
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


def check_stale(manifest_path=None, slugs=None, resolve=resolve_tier1_repo_path) -> int:
    """Return 1 if any repo's live registry hash drifts from the committed
    manifest (fail closed; never silently serve stale), else 0. ``generated_at``
    is excluded from the comparison."""
    manifest_path = Path(manifest_path) if manifest_path is not None else default_manifest_path()
    saved = json.loads(manifest_path.read_text(encoding="utf-8"))
    fresh = build_manifest(slugs=slugs, resolve=resolve)
    saved_h = {r["repo"]: r.get("registry_sha256") for r in saved.get("repos", [])}
    fresh_h = {r["repo"]: r.get("registry_sha256") for r in fresh.get("repos", [])}
    drift = sorted(s for s in saved_h if saved_h[s] != fresh_h.get(s))
    drift += sorted(s for s in fresh_h if s not in saved_h)
    if drift:
        print(f"STALE: registries changed since manifest: {drift}", file=sys.stderr)
        return 1
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Generate or check the ecosystem workflow manifest (#3284).")
    ap.add_argument("--write", action="store_true", help="regenerate the manifest (default)")
    ap.add_argument("--check", action="store_true", help="stale-detection gate: exit 1 on registry drift")
    ap.add_argument("--output", default=None, help="manifest path override")
    args = ap.parse_args(argv)

    if args.check:
        return check_stale(args.output)
    path = write_manifest(args.output)
    print(f"wrote workflow manifest to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
