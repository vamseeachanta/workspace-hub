#!/usr/bin/env python3
"""Validate and render the #2487 inventory-readiness matrix.

The YAML config is the source of truth. This script validates readiness claims
without mutating input files and can render a derived markdown dispatch board.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import yaml

READINESS_STAGES = [
    "raw_data",
    "inventory",
    "llm_wiki",
    "calculation_code",
    "parametric_outputs",
    "website_gtm",
]
READINESS_VALUES = {"READY", "PARTIAL", "MISSING", "STALE", "BLOCKED"}
PROVIDERS = {"codex", "gemini", "claude"}
DEPENDENCY_ROLES = {"blocking", "partial_only", "downstream_only"}
ISSUE_RELATIONS = {"downstream_candidate", "dependency", "reference"}
APPROVAL_STATES = {"plan-approved", "plan-review", "open", "closed", "unknown"}
COUNT_KEYS = ["codex_candidates", "gemini_tasks", "claude_reviews"]
STAGE_EVIDENCE_KEYS = {
    "raw_data": "raw_data_paths",
    "inventory": "inventory_artifacts",
    "llm_wiki": "wiki_doc_keys",
    "calculation_code": "calculation_artifacts",
    "parametric_outputs": "parametric_artifacts",
    "website_gtm": "website_gtm_artifacts",
}


class InventoryReadinessError(ValueError):
    """Raised when the inventory-readiness matrix is invalid."""


def _fail(message: str) -> None:
    raise InventoryReadinessError(message)


def _require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{path} must be a mapping")
    return value


def _require_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(f"{path} must be a list")
    return value


def _require_key(mapping: dict[str, Any], key: str, path: str) -> Any:
    if key not in mapping:
        _fail(f"missing required field {path}.{key}" if path else f"missing required field {key}")
    return mapping[key]


def _validate_provider(value: Any, path: str, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if value not in PROVIDERS:
        _fail(f"{path} has unknown provider {value!r}; allowed: codex, gemini, claude")


def _nonempty_list(value: Any, path: str) -> bool:
    return isinstance(value, list) and len(value) > 0


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        _fail(f"config path does not exist: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return _require_mapping(data, "<root>")


def load_and_validate(path: Path) -> dict[str, Any]:
    data = load_yaml(path)
    return validate_matrix(data)


def validate_matrix(data: dict[str, Any]) -> dict[str, Any]:
    schema_version = _require_key(data, "schema_version", "")
    if schema_version != 1:
        _fail(f"schema_version must be 1, got {schema_version!r}")

    snapshot = _validate_snapshot(_require_key(data, "provider_queue_snapshot", ""))
    families = _require_list(_require_key(data, "package_families", ""), "package_families")
    if not families:
        _fail("package_families must contain at least one package family")

    seen_ids: set[str] = set()
    dispatch_counts: Counter[str] = Counter({provider: 0 for provider in PROVIDERS})
    validated_families: list[dict[str, Any]] = []
    for index, raw_family in enumerate(families):
        family_path = f"package_families[{index}]"
        family = _require_mapping(raw_family, family_path)
        package_id = _require_key(family, "id", family_path)
        if not isinstance(package_id, str) or not package_id:
            _fail(f"{family_path}.id must be a non-empty string")
        if package_id in seen_ids:
            _fail(f"duplicate package id {package_id!r}")
        seen_ids.add(package_id)
        _validate_family(family, family_path)
        provider = family["dispatch"].get("ready_for_provider")
        if provider is not None:
            dispatch_counts[provider] += 1
        validated_families.append(family)

    return {
        "schema_version": schema_version,
        "provider_queue_snapshot": snapshot,
        "package_count": len(validated_families),
        "dispatch_counts": dict(dispatch_counts),
        "package_families": validated_families,
    }


def _validate_snapshot(raw_snapshot: Any) -> dict[str, Any]:
    snapshot = _require_mapping(raw_snapshot, "provider_queue_snapshot")
    _require_key(snapshot, "generated_at", "provider_queue_snapshot")
    source = _require_key(snapshot, "source", "provider_queue_snapshot")
    counts = _require_mapping(
        _require_key(snapshot, "current_counts", "provider_queue_snapshot"),
        "provider_queue_snapshot.current_counts",
    )
    for key in COUNT_KEYS:
        value = _require_key(counts, key, "provider_queue_snapshot.current_counts")
        if value is not None and (not isinstance(value, int) or value < 0):
            _fail(f"provider_queue_snapshot.current_counts.{key} must be an integer >= 0 or null")
    if source is None:
        if any(counts[key] is not None for key in COUNT_KEYS):
            _fail("provider_queue_snapshot.source null requires all current_counts values to be null")
    return snapshot


def _validate_family(family: dict[str, Any], family_path: str) -> None:
    _require_key(family, "title", family_path)
    _validate_provider(_require_key(family, "owner_provider", family_path), f"{family_path}.owner_provider")
    _validate_provider(
        _require_key(family, "preferred_next_provider", family_path),
        f"{family_path}.preferred_next_provider",
    )
    readiness = _require_mapping(_require_key(family, "readiness", family_path), f"{family_path}.readiness")
    evidence = _require_mapping(_require_key(family, "evidence", family_path), f"{family_path}.evidence")
    dependency_roles = _require_list(
        _require_key(family, "dependency_roles", family_path), f"{family_path}.dependency_roles"
    )
    dispatch = _require_mapping(_require_key(family, "dispatch", family_path), f"{family_path}.dispatch")

    _validate_evidence(evidence, f"{family_path}.evidence")
    _validate_dependency_roles(dependency_roles, f"{family_path}.dependency_roles")
    _validate_dispatch(dispatch, f"{family_path}.dispatch")
    _validate_dispatch_dependency_mirror(evidence, dispatch, f"{family_path}.dispatch")

    blocking_dependencies = [role for role in dependency_roles if role["role"] == "blocking"]
    for stage in READINESS_STAGES:
        status = _require_key(readiness, stage, f"{family_path}.readiness")
        if status not in READINESS_VALUES:
            _fail(f"{family_path}.readiness.{stage} has unknown status {status!r}")
        _validate_stage_status(stage, status, evidence, blocking_dependencies, f"{family_path}.readiness.{stage}")

    extra_stages = sorted(set(readiness) - set(READINESS_STAGES))
    if extra_stages:
        _fail(f"{family_path}.readiness has unknown stages: {', '.join(extra_stages)}")


def _validate_evidence(evidence: dict[str, Any], evidence_path: str) -> None:
    for key in [*STAGE_EVIDENCE_KEYS.values(), "stale_artifacts", "issue_refs"]:
        _require_list(_require_key(evidence, key, evidence_path), f"{evidence_path}.{key}")

    for index, raw_ref in enumerate(evidence["issue_refs"]):
        ref_path = f"{evidence_path}.issue_refs[{index}]"
        ref = _require_mapping(raw_ref, ref_path)
        issue = _require_key(ref, "issue", ref_path)
        if not isinstance(issue, int):
            _fail(f"{ref_path}.issue must be an integer")
        relation = _require_key(ref, "relation", ref_path)
        if relation not in ISSUE_RELATIONS:
            _fail(f"{ref_path}.relation has unknown relation {relation!r}")
        approval_state = _require_key(ref, "approval_state", ref_path)
        if approval_state not in APPROVAL_STATES:
            _fail(f"{ref_path}.approval_state has unknown state {approval_state!r}")
        produces = _require_list(_require_key(ref, "produces_stages", ref_path), f"{ref_path}.produces_stages")
        for stage in produces:
            if stage not in READINESS_STAGES:
                _fail(f"{ref_path}.produces_stages contains unknown stage {stage!r}")
        _require_list(_require_key(ref, "implemented_artifacts", ref_path), f"{ref_path}.implemented_artifacts")
        if "artifact_contract" not in ref:
            _fail(f"missing required field {ref_path}.artifact_contract")


def _validate_dependency_roles(roles: list[Any], roles_path: str) -> None:
    for index, raw_role in enumerate(roles):
        role_path = f"{roles_path}[{index}]"
        role = _require_mapping(raw_role, role_path)
        if not isinstance(_require_key(role, "issue", role_path), int):
            _fail(f"{role_path}.issue must be an integer")
        role_value = _require_key(role, "role", role_path)
        if role_value not in DEPENDENCY_ROLES:
            _fail(f"{role_path}.role has unknown role {role_value!r}")
        reason = _require_key(role, "reason", role_path)
        if not isinstance(reason, str) or not reason.strip():
            _fail(f"{role_path}.reason must be a non-empty string")


def _validate_dispatch(dispatch: dict[str, Any], dispatch_path: str) -> None:
    _validate_provider(_require_key(dispatch, "ready_for_provider", dispatch_path), f"{dispatch_path}.ready_for_provider", nullable=True)
    rationale = _require_key(dispatch, "rationale", dispatch_path)
    if not isinstance(rationale, str) or not rationale.strip():
        _fail(f"{dispatch_path}.rationale must be a non-empty string")
    dependency_issues = _require_list(_require_key(dispatch, "dependency_issues", dispatch_path), f"{dispatch_path}.dependency_issues")
    for issue in dependency_issues:
        if not isinstance(issue, int):
            _fail(f"{dispatch_path}.dependency_issues entries must be integers")
    if "expected_output_artifact" not in dispatch:
        _fail(f"missing required field {dispatch_path}.expected_output_artifact")
    expected = dispatch["expected_output_artifact"]
    if expected is not None and not isinstance(expected, str):
        _fail(f"{dispatch_path}.expected_output_artifact must be a string or null")


def _validate_dispatch_dependency_mirror(evidence: dict[str, Any], dispatch: dict[str, Any], dispatch_path: str) -> None:
    """Ensure dispatch dependencies mirror non-reference issue evidence.

    Reference-only issues can document context without being a dependency for the
    next action. Downstream candidates and dependencies are actionable issue refs
    and must remain visible in dispatch.dependency_issues.
    """
    dependency_issues = set(dispatch["dependency_issues"])
    required_issues = {
        ref["issue"]
        for ref in evidence["issue_refs"]
        if ref.get("relation") in {"downstream_candidate", "dependency"}
    }
    missing = sorted(required_issues - dependency_issues)
    if missing:
        missing_refs = ", ".join(str(issue) for issue in missing)
        _fail(f"{dispatch_path}.dependency_issues must mirror actionable issue_refs; missing {missing_refs}")


def _validate_stage_status(
    stage: str,
    status: str,
    evidence: dict[str, Any],
    blocking_dependencies: list[dict[str, Any]],
    status_path: str,
) -> None:
    evidence_key = STAGE_EVIDENCE_KEYS[stage]
    if status == "READY":
        if not _nonempty_list(evidence[evidence_key], f"evidence.{evidence_key}"):
            if stage == "llm_wiki":
                _fail(f"{status_path} READY requires doc_key evidence in evidence.wiki_doc_keys")
            if stage in {"calculation_code", "parametric_outputs", "website_gtm"}:
                _fail(f"{status_path} READY requires implemented artifacts in evidence.{evidence_key}")
            _fail(f"{status_path} READY requires evidence.{evidence_key}")
    if status == "STALE" and not evidence["stale_artifacts"]:
        _fail(f"{status_path} STALE requires evidence.stale_artifacts")
    if status == "BLOCKED" and not blocking_dependencies:
        _fail(f"{status_path} BLOCKED requires a dependency_roles entry with role: blocking")
    if status == "PARTIAL" and not _stage_has_partial_evidence(stage, evidence):
        _fail(f"{status_path} PARTIAL requires stage-specific evidence or issue_refs; approved plans cannot satisfy the wrong stage")


def _stage_has_partial_evidence(stage: str, evidence: dict[str, Any]) -> bool:
    if evidence[STAGE_EVIDENCE_KEYS[stage]]:
        return True
    for ref in evidence["issue_refs"]:
        if stage in ref.get("produces_stages", []):
            return True
    return False


def render_markdown(validated: dict[str, Any], data: dict[str, Any]) -> str:
    snapshot = validated["provider_queue_snapshot"]
    counts = snapshot["current_counts"]
    lines = [
        "# Inventory Readiness Matrix",
        "",
        f"Generated from `config/knowledge/inventory-readiness.yaml` on {date.today().isoformat()}.",
        "",
        "## Provider queue snapshot",
        "",
        f"Source: `{snapshot.get('source')}`" if snapshot.get("source") else "Source: unknown",
        f"Snapshot generated at: `{snapshot.get('generated_at')}`",
        "",
        "These are observed queue values from the provider work queue, not acceptance thresholds.",
        "",
        "| Count | Observed value |",
        "|---|---:|",
    ]
    for key in COUNT_KEYS:
        value = counts.get(key)
        lines.append(f"| {key} | {value if value is not None else 'unknown'} |")
    lines.extend([
        "",
        "## Package readiness",
        "",
        "| Package | Owner | Preferred next | Raw data | Inventory | LLM wiki | Calculation code | Parametric outputs | Website/GTM |",
        "|---|---|---|---|---|---|---|---|---|",
    ])
    families = validated["package_families"]
    for family in families:
        readiness = family["readiness"]
        lines.append(
            "| {id} | {owner} | {preferred} | {raw} | {inventory} | {wiki} | {calc} | {param} | {gtm} |".format(
                id=family["id"],
                owner=family["owner_provider"],
                preferred=family["preferred_next_provider"],
                raw=readiness["raw_data"],
                inventory=readiness["inventory"],
                wiki=readiness["llm_wiki"],
                calc=readiness["calculation_code"],
                param=readiness["parametric_outputs"],
                gtm=readiness["website_gtm"],
            )
        )

    for provider in ["codex", "gemini", "claude"]:
        lines.extend(["", f"## {provider.title()} Dispatch", ""])
        provider_rows = [f for f in families if f["dispatch"].get("ready_for_provider") == provider]
        if not provider_rows:
            lines.append("No package currently dispatchable for this provider.")
            continue
        lines.extend(["| Package | Rationale | Dependencies | Expected output |", "|---|---|---|---|"])
        for family in provider_rows:
            dispatch = family["dispatch"]
            dependencies = ", ".join(f"#{issue}" for issue in dispatch["dependency_issues"]) or "none"
            expected = dispatch["expected_output_artifact"] or "null / provider task will create artifact"
            lines.append(f"| {family['id']} | {dispatch['rationale']} | {dependencies} | `{expected}` |")

    lines.extend(["", "## Downstream issue references", ""])
    issue_refs = []
    for family in families:
        for ref in family["evidence"]["issue_refs"]:
            issue_refs.append((family["id"], ref))
    if issue_refs:
        lines.extend(["| Package | Issue | Relation | Approval state | Produces stages | Implemented here? |", "|---|---:|---|---|---|---|"])
        for package_id, ref in issue_refs:
            produces = ", ".join(ref["produces_stages"]) or "none"
            implemented_here = "no — downstream/reference only"
            lines.append(
                f"| {package_id} | #{ref['issue']} | {ref['relation']} | {ref['approval_state']} | {produces} | {implemented_here} |"
            )
    else:
        lines.append("No downstream issue references recorded.")

    lines.extend(["", "## Blocked / partial / missing evidence", ""])
    lines.extend(["| Package | Stage | Status | Evidence interpretation |", "|---|---|---|---|"])
    gap_rows = 0
    for family in families:
        evidence = family["evidence"]
        for stage in READINESS_STAGES:
            status = family["readiness"][stage]
            if status == "READY":
                continue
            gap_rows += 1
            if status == "PARTIAL":
                stage_refs = [
                    f"#{ref['issue']}"
                    for ref in evidence["issue_refs"]
                    if stage in ref.get("produces_stages", [])
                ]
                detail = "approved-plan evidence only; implemented artifact still required for READY"
                if stage_refs:
                    detail += f" ({', '.join(stage_refs)})"
            elif status == "MISSING":
                detail = "no usable evidence recorded for this stage"
            elif status == "BLOCKED":
                detail = "blocked by dependency_roles entry with role: blocking"
            elif status == "STALE":
                detail = "stale_artifacts records the stale source or review artifact"
            else:
                detail = "non-ready evidence state"
            lines.append(f"| {family['id']} | {stage} | {status} | {detail} |")
    if not gap_rows:
        lines.append("| none | none | READY | all stages have concrete READY evidence |")

    lines.extend([
        "",
        "## Evidence notes",
        "",
        "- `READY` requires concrete implemented artifact evidence for the relevant stage.",
        "- Approved plans and downstream issue references can justify `PARTIAL`, but not `READY`, without implemented artifacts.",
        "- Downstream issues are candidates/dependencies only; #2487 does not execute them.",
    ])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="Path to inventory-readiness YAML config")
    parser.add_argument("--output", type=Path, help="Path to write rendered markdown report")
    parser.add_argument("--validate-only", action="store_true", help="Validate config without writing a report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        data = load_yaml(args.config)
        validated = validate_matrix(data)
        if args.validate_only:
            print(f"valid inventory-readiness matrix: {validated['package_count']} package family/families")
            return 0
        if args.output is None:
            _fail("--output is required unless --validate-only is set")
        report = render_markdown(validated, data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"wrote {args.output}")
        return 0
    except InventoryReadinessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
