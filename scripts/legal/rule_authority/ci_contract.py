"""Pure Phase A CI trust-boundary and dual-slot preview helpers."""

from __future__ import annotations

import re
from collections.abc import Callable

from .models import ModelError, validate_anchor

OID = re.compile(r"[0-9a-f]{40}\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


def _oid(value: object) -> str:
    if not isinstance(value, str) or OID.fullmatch(value) is None:
        raise ValueError("invalid workflow object ID")
    return value


def _repository(value: object) -> str:
    if not isinstance(value, str) or REPOSITORY.fullmatch(value) is None:
        raise ValueError("invalid workflow repository")
    return value


def validate_workflow_context(request: object) -> dict[str, str]:
    """Validate the closed trusted caller context without shell interpretation."""
    fields = {"base_ref", "event_name", "head_repository", "head_sha",
              "repository", "tool_sha"}
    if not isinstance(request, dict) or set(request) != fields:
        raise ValueError("invalid workflow context")
    if request["event_name"] != "pull_request_target":
        raise ValueError("invalid workflow event")
    if request["base_ref"] != "refs/heads/main":
        raise ValueError("invalid workflow base ref")
    repository = _repository(request["repository"])
    head_repository = _repository(request["head_repository"])
    if repository != head_repository:
        raise ValueError("owner review required")
    return {**request, "head_sha": _oid(request["head_sha"]),
            "tool_sha": _oid(request["tool_sha"])}


def classify_pull_request(*, repository: str, head_repository: str,
                          base_ref: str, head_sha: str,
                          authority_loader: Callable[[], object]) -> object:
    """Return the constant fork result before touching authority state."""
    if repository != head_repository:
        return {"message": "owner review required", "rc": 1}
    context = {
        "base_ref": base_ref, "event_name": "pull_request_target",
        "head_repository": head_repository, "head_sha": head_sha,
        "repository": repository, "tool_sha": "0" * 40,
    }
    validate_workflow_context(context)
    return authority_loader()


def _anchor(value: object, slot: str) -> dict:
    try:
        validate_anchor(value)
    except ModelError as exc:
        raise ValueError("invalid slot anchor") from exc
    if value["slot"] != slot:
        raise ValueError("invalid slot anchor")
    return value


def select_slot(head_sha: str, current: dict, pending: dict | None) -> dict:
    """Select PENDING only for its exact bound head; otherwise retain CURRENT."""
    head_sha = _oid(head_sha)
    current = _anchor(current, "current")
    if pending is None:
        return current
    pending = _anchor(pending, "pending")
    return pending if pending["expected_head_oid"] == head_sha else current


def cutover_preview(current: dict, pending: dict, *, expected_head: str,
                    expected_tree: str, observed_current: dict) -> dict:
    """Validate a no-side-effect compare-and-swap and its bounded rollback."""
    current = _anchor(current, "current")
    pending = _anchor(pending, "pending")
    expected_head, expected_tree = _oid(expected_head), _oid(expected_tree)
    if observed_current != current or pending["expected_head_oid"] != expected_head:
        raise ValueError("cutover compare-and-swap mismatch")
    return {
        "compare_and_swap": True, "expected_head": expected_head,
        "expected_tree": expected_tree, "from_manifest_mac": current["manifest_mac"],
        "rollback": "restore-current-if-and-only-if-promoted-identity-matches",
        "to_manifest_mac": pending["manifest_mac"],
    }
