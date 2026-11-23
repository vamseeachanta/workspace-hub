"""Pure synthetic event-v1 mapping; not a native hook or an authority service.

Missing/unbounded context is needs-context; malformed types/fields are unsupported.
Recognized shape conflicts remain unmapped. Only the harness calls assess().
"""
from copy import deepcopy

from evidence_threshold_eligibility import normalize_changed_paths
from workflow_decision import EFFECTS, FIELDS
from workflow_receipt import canonical_bytes, load_json

ENVELOPE_FIELDS = {"schema_version", "provider", "event_kind", "payload", "evidence_reference"}
KINDS = {"file.write", "file.edit", "file.patch", "shell.exec"}
CONTEXT_REQUIRED = {"schema_version", "provider", "operation_kind", "scope", "changed_paths", "effects"}
SCOPE_FIELDS = {"repository_id", "task_id", "operation_id", "bounded"}


class _Unmapped(Exception):
    def __init__(self, reason, status="needs-context"):
        self.reason = reason
        self.status = status


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _path_shapes(entries):
    if not isinstance(entries, list):
        raise ValueError("Path list required")
    for entry in entries:
        if isinstance(entry, str):
            continue
        if (not isinstance(entry, dict) or set(entry) != {"old_path", "new_path"}
                or any(not isinstance(value, str) for value in entry.values())):
            raise ValueError("String or exact rename pair required")


def _envelope(event):
    if set(event) != ENVELOPE_FIELDS:
        raise ValueError("Exact event envelope required")
    if any(not isinstance(event[k], str) for k in ("schema_version", "provider", "event_kind")):
        raise ValueError("Event identifiers must be strings")
    if not _text(event["evidence_reference"]):
        raise ValueError("Nonempty inert evidence reference required")
    if (event["schema_version"] != "1" or event["provider"] not in {"claude", "codex"}
            or event["event_kind"] not in KINDS):
        raise _Unmapped("UNSUPPORTED_EVENT", "unsupported")
    if not isinstance(event["payload"], dict):
        raise ValueError("Payload object required")


def _context(context):
    if not isinstance(context, dict):
        raise ValueError("Context object required")
    canonical_bytes(context)
    if set(context) - FIELDS:
        raise ValueError("Unknown context field")
    if not CONTEXT_REQUIRED <= set(context):
        raise _Unmapped("MISSING_CONTEXT")
    for key in ("schema_version", "provider", "operation_kind"):
        if not _text(context[key]):
            raise ValueError("Context identifiers must be nonempty strings")
    scope = context["scope"]
    if not isinstance(scope, dict) or set(scope) != SCOPE_FIELDS:
        raise ValueError("Exact scope object required")
    if any(not _text(scope[k]) or len(scope[k]) > 4096 for k in SCOPE_FIELDS - {"bounded"}):
        raise ValueError("Scope identities required")
    if type(scope["bounded"]) is not bool:
        raise ValueError("Bounded must be boolean")
    if not scope["bounded"]:
        raise _Unmapped("MISSING_CONTEXT")
    _path_shapes(context["changed_paths"])
    effects = context["effects"]
    if (not isinstance(effects, list) or not effects or any(not isinstance(e, str) for e in effects)
            or len(effects) != len(set(effects)) or set(effects) - EFFECTS):
        raise ValueError("Invalid effects")
    reference = context.get("authorization_reference")
    if reference is not None and (not _text(reference) or len(reference) > 4096):
        raise ValueError("Invalid authorization reference")


def _event_paths(event):
    payload = event["payload"]
    if event["event_kind"] in {"file.write", "file.edit"}:
        if set(payload) != {"path"} or not isinstance(payload["path"], str):
            raise ValueError("Exact file path payload required")
        return [payload["path"]]
    if set(payload) != {"changes"} or not isinstance(payload["changes"], list) or not payload["changes"]:
        raise ValueError("Nonempty structured changes required")
    _path_shapes(payload["changes"])
    return payload["changes"]


def _bind(event_paths, context):
    try:
        observed = normalize_changed_paths(event_paths)
        supplied = normalize_changed_paths(context["changed_paths"])
    except ValueError as exc:
        raise _Unmapped("PATH_BINDING_MISMATCH") from exc
    if observed != supplied:
        raise _Unmapped("PATH_BINDING_MISMATCH")
    return observed


def _mapped_request(event, context):
    if event["event_kind"] == "shell.exec":
        raise _Unmapped("INCOMPLETE_EFFECTS")
    paths = _bind(_event_paths(event), context)
    if (context["schema_version"] != "1" or context["provider"] != event["provider"]
            or context["operation_kind"] != "edit" or "local-reversible" not in context["effects"]
            or "read-only" in context["effects"]):
        raise _Unmapped("INCOMPLETE_EFFECTS")
    request = deepcopy(context)
    request["changed_paths"] = paths
    # Additional declared substantial/consequential effects are preserved verbatim.
    return request


def normalize_event(event, context):
    """Map bounded raw JSON plus unverified context without performing assessment or IO."""
    try:
        event = load_json(event, max_bytes=1048576)
        _envelope(event)
        _context(context)
        return {"mapping_status": "mapped", "request": _mapped_request(event, context),
                "reason_codes": ["MAPPED_EVENT"]}
    except _Unmapped as exc:
        return {"mapping_status": exc.status, "request": None, "reason_codes": [exc.reason]}
    except (ValueError, TypeError, UnicodeError, RecursionError):
        return {"mapping_status": "unsupported", "request": None, "reason_codes": ["MALFORMED_EVENT"]}
