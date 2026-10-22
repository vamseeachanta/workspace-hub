"""Read-only workflow preflight over the existing discovery manifest.

Contract sources: docs/registry/README.md (identity, version selection and
invocation), workflow-manifest.schema.json (format), and
docs/architecture/agent-data-handling-contract.md (metadata is not readiness).
This module never imports an engine, renders a command or executes a workflow.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import string
import sys
from pathlib import Path


class ManifestError(ValueError):
    """The manifest or requested reference cannot be resolved unambiguously."""


_SLUG = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
# SHA-256 representation: agent-data-handling-contract.md, "Descriptor v1".
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
# Manifest format version: generate_workflow_manifest.py, MANIFEST_VERSION.
_MANIFEST_VERSION = 1


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value):
    raise ManifestError("non-finite JSON value")


def _finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ManifestError("non-finite JSON value")
    return result


def load_manifest(path: Path) -> dict:
    """Read strict JSON; diagnostics never echo source content or filesystem paths."""
    try:
        manifest = json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object, parse_constant=_reject_constant,
            parse_float=_finite_float,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        raise ManifestError("cannot read valid manifest JSON") from exc
    validate_manifest(manifest)
    return manifest


def validate_manifest(manifest: dict) -> None:
    """Validate consumer invariants, not the entire discovery JSON Schema.

    Recompute the materialized latest index with the producer's documented
    ordering: flagged stable, highest stable, then highest available version.
    A mismatch is rejected rather than silently repaired.
    """
    if not isinstance(manifest, dict):
        raise ManifestError("manifest must be an object")
    version = manifest.get("manifest_version")
    if type(version) is not int or version != _MANIFEST_VERSION:
        raise ManifestError("unsupported manifest version")
    rows = manifest.get("workflows")
    repos = manifest.get("repos")
    index = manifest.get("latest_by_routing_id")
    count = manifest.get("workflow_count")
    if not isinstance(rows, list) or not isinstance(repos, list) or not isinstance(index, dict):
        raise ManifestError("invalid manifest collections")
    if type(count) is not int or count != len(rows):
        raise ManifestError("workflow count mismatch")

    repo_names = set()
    for repo in repos:
        name = repo.get("repo") if isinstance(repo, dict) else None
        if not isinstance(name, str) or not _SLUG.fullmatch(name) or name in repo_names:
            raise ManifestError("invalid or duplicate repository identity")
        repo_names.add(name)

    identities = set()
    groups = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ManifestError("workflow row must be an object")
        for key in ("repo", "id"):
            value = row.get(key)
            if not isinstance(value, str) or not _SLUG.fullmatch(value):
                raise ManifestError("invalid workflow identity")
        version = row.get("version")
        # Positive versions: registry README, repo:id@version routing contract.
        if type(version) is not int or version < 1:
            raise ManifestError("invalid workflow version")
        if type(row.get("latest")) is not bool or not isinstance(row.get("status"), str):
            raise ManifestError("invalid workflow selection fields")
        if not row["status"].strip():
            raise ManifestError("empty workflow status")
        routing_id = f"{row['repo']}:{row['id']}"
        workflow_id = f"{routing_id}@{version}"
        if row.get("routing_id") != routing_id or row.get("workflow_id") != workflow_id:
            raise ManifestError("inconsistent workflow identity")
        if workflow_id in identities:
            raise ManifestError("duplicate workflow identity")
        identities.add(workflow_id)
        groups.setdefault(routing_id, []).append(row)

    expected = {}
    for routing_id, group in groups.items():
        stable = [row for row in group if row["status"] == "stable"]
        flagged = [row for row in stable if row["latest"]]
        selected = max(flagged or stable or group, key=lambda row: row["version"])
        expected[routing_id] = selected["workflow_id"]
    if index != expected:
        raise ManifestError("latest routing index mismatch")


def _resolve_validated(manifest: dict, ref: str) -> dict:
    if not isinstance(ref, str):
        raise ManifestError("reference must be text")
    workflow_id = manifest["latest_by_routing_id"].get(ref, ref)
    for row in manifest["workflows"]:
        if row["workflow_id"] == workflow_id:
            return row
    raise ManifestError("unknown workflow reference")


def resolve_workflow(manifest: dict, ref: str) -> dict:
    """Resolve an exact identity or documented latest index without engine access."""
    validate_manifest(manifest)
    return _resolve_validated(manifest, ref)


def _relative_input(value) -> bool:
    return (
        isinstance(value, str) and bool(value.strip())
        and not value.startswith("/") and "\\" not in value and ":" not in value
        and all(part not in {"", ".", ".."} for part in value.split("/"))
        and value.isprintable()
    )


def _input_template(value) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        fields = [(name, spec, conversion)
                  for _, name, spec, conversion in string.Formatter().parse(value)
                  if name is not None]
    except ValueError:
        return False
    # README "Field-set": only {input} substitution; no test-node fallback.
    return bool(fields) and all(field == ("input", "", None) for field in fields)


def _assess_row(row: dict, repos: list[dict]) -> dict:
    checks = []

    def record(name, status, reason):
        checks.append({"name": name, "status": status, "reason": reason})

    def declaration(name, valid, reason):
        record(name, "PASS" if valid else "FAIL", reason)

    declaration("stable_version", row["status"] == "stable", "Selected version must be stable.")
    runtime, gate = row.get("runtime"), row.get("license_gated")
    if runtime == "requires-license" or gate is True:
        record("license_policy", "FAIL", "Licensed execution is outside this preflight.")
    elif gate is None:
        record("license_policy", "NOT_EVALUATED", "License declaration is absent.")
    else:
        declaration("license_policy", gate is False, "An explicit boolean license declaration is required.")
    record("offline_runtime", "PASS" if runtime == "offline" else "NOT_EVALUATED",
           "Only an explicit offline runtime is recognized; runtime behavior is untested.")
    declaration("input_declared", _relative_input(row.get("input")),
                "Input must be a nonempty repository-relative locator; existence is untested.")
    declaration("invocation_declared", _input_template(row.get("invocation")),
                "Invocation must declare input-only substitution; command safety is untested.")
    result = row.get("result")
    if result is None:
        record("result_declared", "NOT_EVALUATED", "Result descriptor is absent.")
    else:
        declaration("result_declared", isinstance(result, dict) and result.get("kind") in
                    ("files", "in_memory"), "Only the result kind declaration is checked.")
    repo = next((repo for repo in repos if repo["repo"] == row["repo"]), {})
    digest = repo.get("registry_sha256")
    provenance = (repo.get("status") == "ok" and isinstance(digest, str)
                  and bool(_DIGEST.fullmatch(digest)))
    record("registry_provenance", "PASS" if provenance else "NOT_EVALUATED",
           "Registry status and digest syntax only; bytes and revision are unverified.")
    for name, reason in (
        ("registry_freshness", "Live registry bytes were not compared with the snapshot."),
        ("live_access", "Scope, authorization, privacy and quotas require live validation."),
        ("runtime_execution", "No engine was imported or workflow executed."),
        ("artifact_delivery", "Artifact integrity, publication and delivery were not exercised."),
        ("engineering_basis", "Sources, units and intended-use criteria require workflow-specific review."),
    ):
        record(name, "NOT_EVALUATED", reason)
    status = "BLOCKED" if any(check["status"] == "FAIL" for check in checks) else "NOT_EVALUATED"
    return {"workflow_id": row["workflow_id"], "status": status, "checks": checks}


def audit_manifest(manifest: dict, refs: list[str] | None = None) -> dict:
    """Assess every version by default, or explicitly requested references.

    Output contains identities and fixed diagnostics, never source commands,
    input locators, arbitrary descriptors or warnings. NOT_EVALUATED cannot
    be promoted to READY from metadata, even when all declarations pass.
    """
    validate_manifest(manifest)
    rows = manifest["workflows"] if refs is None else [_resolve_validated(manifest, ref) for ref in refs]
    selected = {row["workflow_id"]: row for row in rows}
    workflows = [_assess_row(selected[key], manifest["repos"]) for key in sorted(selected)]
    blocked = sum(row["status"] == "BLOCKED" for row in workflows)
    return {
        "status": "BLOCKED" if blocked else "NOT_EVALUATED",
        "workflow_count": len(workflows), "blocked_count": blocked,
        "not_evaluated_count": len(workflows) - blocked, "workflows": workflows,
    }


def render_html(report: dict) -> str:
    """Render a self-contained report with escaped text and no remote resources."""
    def escaped(value):
        return html.escape(str(value), quote=True)

    lines = ["<!doctype html>", '<html lang="en"><meta charset="utf-8">',
             "<title>Workflow readiness assessment</title><body>",
             "<h1>Workflow readiness assessment</h1>",
             (f"<p>Status: {escaped(report['status'])}. "
             f"Assessed: {escaped(report['workflow_count'])}; "
             f"blocked: {escaped(report['blocked_count'])}; "
             f"not evaluated: {escaped(report['not_evaluated_count'])}.</p>"),
             "<p>Declaration checks cannot establish live readiness or authorization.</p>"]
    for workflow in report["workflows"]:
        lines.extend([f"<h2>{escaped(workflow['workflow_id'])}: {escaped(workflow['status'])}</h2>",
                      "<table><thead><tr><th>Check</th><th>Status</th><th>Basis</th></tr></thead><tbody>"])
        for check in workflow["checks"]:
            cells = "".join(f"<td>{escaped(check[key])}</td>" for key in ("name", "status", "reason"))
            lines.append(f"<tr>{cells}</tr>")
        lines.append("</tbody></table>")
    return "\n".join([*lines, "</body></html>", ""])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path,
                        default=Path(__file__).resolve().parents[2] / "docs/registry/workflow-manifest.json")
    parser.add_argument("--ref", action="append", dest="refs", help="exact or unpinned reference; repeatable")
    parser.add_argument("--format", choices=("json", "html"), default="json")
    args = parser.parse_args(argv)
    try:
        report = audit_manifest(load_manifest(args.manifest), args.refs)
    except ManifestError as exc:
        print(f"Cannot assess manifest: {exc}", file=sys.stderr)
        # Exit-code source: check-engineering-register.py module docstring.
        return 2
    print(render_html(report) if args.format == "html" else json.dumps(report, indent=2))
    return int(report["status"] == "BLOCKED")


if __name__ == "__main__":
    raise SystemExit(main())
