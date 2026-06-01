"""Config-driven Deckhand authorization and enforcement decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


READ_ACTION = "read"
WRITE_ACTION = "write"
FULL_VISIBILITY = "full"
GENERIC_VISIBILITY = "generic"


def decide(request: dict[str, Any], *, config: Any) -> dict[str, Any]:
    """Return a pure ALLOW/DENY decision for a Deckhand request."""
    loaded = _load_config(config)
    if loaded is None:
        return _decision(False, "config unavailable", request, None, GENERIC_VISIBILITY)

    policy, scopes_config = loaded
    scopes = scopes_config.get("scopes")
    if not isinstance(scopes, dict):
        return _decision(False, "config unavailable", request, None, GENERIC_VISIBILITY)

    operator_id = request.get("operator_id")
    platform = request.get("platform")
    action_class = request.get("action_class")
    is_write = action_class != READ_ACTION

    kill_switches = policy.get("kill_switches") or {}
    if is_write and kill_switches.get("disable_all_writes"):
        return _decision(False, "writes disabled", request, None, GENERIC_VISIBILITY)
    if operator_id in _as_list(kill_switches.get("disabled_operators")):
        return _decision(False, "operator disabled", request, None, GENERIC_VISIBILITY)
    if platform in _as_list(kill_switches.get("disabled_platforms")):
        return _decision(False, "platform disabled", request, None, GENERIC_VISIBILITY)

    if not _known_operator(operator_id, scopes):
        return _decision(False, "unknown operator", request, request.get("scope_name"), GENERIC_VISIBILITY)

    resolved = _resolve_scope(request, scopes, scopes_config)
    if resolved["error"]:
        return _decision(False, resolved["error"], request, resolved["scope_name"], GENERIC_VISIBILITY)

    scope_name = resolved["scope_name"]
    scope = resolved["scope"]
    visibility = _reply_visibility(scope, request)

    if scope_name in _as_list(kill_switches.get("disabled_scopes")):
        return _decision(False, "scope disabled", request, scope_name, visibility)

    if scope.get("external_disabled") and not _is_internal_operator(operator_id, policy):
        return _decision(False, "external operators disabled for scope", request, scope_name, visibility)

    operators = _as_list(scope.get("operators"))
    if operator_id not in operators:
        if resolved["origin_bound"]:
            reason = "operator not authorized for origin scope"
        else:
            reason = "operator not authorized for scope"
        return _decision(False, reason, request, scope_name, visibility)

    destructive_ops = set(_as_list(policy.get("destructive_ops")))
    if action_class in destructive_ops:
        return _decision(False, "destructive action denied", request, scope_name, visibility)

    target_repos = _as_list(request.get("target_repos"))
    outside = [repo for repo in target_repos if not _repo_in_scope(repo, scope)]
    if outside:
        return _decision(False, "repo outside scope allowlist", request, scope_name, visibility)

    if is_write:
        read_only_repo = _first_read_only_repo(target_repos, scope)
        if read_only_repo:
            return _decision(False, "repo is read-only", request, scope_name, visibility)

        risk_reason = _diff_risk_reason(request, policy)
        if risk_reason and not _valid_elevation(request.get("elevation_token"), policy):
            return _decision(False, risk_reason, request, scope_name, visibility)

    return _decision(True, "allowed", request, scope_name, visibility)


def _load_config(config: Any) -> tuple[dict[str, Any], dict[str, Any]] | None:
    try:
        if isinstance(config, (str, Path)):
            config_dir = Path(config)
            policy = yaml.safe_load((config_dir / "policy.yml").read_text(encoding="utf-8"))
            scopes = yaml.safe_load((config_dir / "scopes.yml").read_text(encoding="utf-8"))
            if not isinstance(policy, dict) or not isinstance(scopes, dict):
                return None
            return policy, scopes
        if isinstance(config, dict):
            policy = config.get("policy")
            scopes = config.get("scopes")
            if isinstance(policy, dict) and isinstance(scopes, dict):
                return policy, scopes
    except (OSError, yaml.YAMLError):
        return None
    return None


def _resolve_scope(
    request: dict[str, Any],
    scopes: dict[str, Any],
    scopes_config: dict[str, Any],
) -> dict[str, Any]:
    scope_name = request.get("scope_name")
    if scope_name:
        scope = scopes.get(scope_name)
        if not isinstance(scope, dict):
            return {"error": "unknown scope", "scope_name": scope_name, "scope": None, "origin_bound": False}
        return {"error": None, "scope_name": scope_name, "scope": scope, "origin_bound": False}

    origin_default = scopes_config.get("origin_bound_default") or {}
    if not origin_default.get("enabled", False):
        return {"error": "explicit scope required", "scope_name": None, "scope": None, "origin_bound": True}

    origin = request.get("origin") or {}
    platform = request.get("platform")
    channel_id = origin.get("channel_id")
    for candidate_name, candidate_scope in scopes.items():
        if not isinstance(candidate_scope, dict):
            continue
        for binding in _as_list(candidate_scope.get("channel_repo_bindings")):
            if not isinstance(binding, dict):
                continue
            if binding.get("platform") != platform or binding.get("channel_id") != channel_id:
                continue
            bound_repo = binding.get("repo")
            if not _repo_in_scope(bound_repo, candidate_scope):
                return {
                    "error": "origin repo outside scope allowlist",
                    "scope_name": candidate_name,
                    "scope": candidate_scope,
                    "origin_bound": True,
                }
            return {
                "error": None,
                "scope_name": candidate_name,
                "scope": candidate_scope,
                "origin_bound": True,
            }

    return {"error": "explicit scope required", "scope_name": None, "scope": None, "origin_bound": True}


def _decision(
    allow: bool,
    reason: str,
    request: dict[str, Any],
    scope_name: str | None,
    reply_visibility: str,
) -> dict[str, Any]:
    decision_word = "ALLOW" if allow else "DENY"
    audit = {
        "ts_placeholder": "PENDING_TS",
        "operator": request.get("operator_id"),
        "platform": request.get("platform"),
        "scope": scope_name,
        "repos": _as_list(request.get("target_repos")),
        "action_class": request.get("action_class"),
        "decision": decision_word,
        "reason": reason,
    }
    return {
        "allow": allow,
        "reason": reason,
        "scope_resolved": scope_name,
        "reply_visibility": reply_visibility,
        "audit": audit,
    }


def _known_operator(operator_id: Any, scopes: dict[str, Any]) -> bool:
    if not operator_id:
        return False
    return any(
        operator_id in _as_list(scope.get("operators"))
        for scope in scopes.values()
        if isinstance(scope, dict)
    )


def _repo_in_scope(repo: Any, scope: dict[str, Any]) -> bool:
    if not isinstance(repo, str):
        return False
    repositories = scope.get("repositories")
    if isinstance(repositories, list):
        return repo in repositories
    if isinstance(repositories, str) and repositories.startswith("owner:") and repositories.endswith("/*"):
        owner = repositories.removeprefix("owner:").removesuffix("/*")
        return repo.startswith(f"{owner}/")
    return False


def _first_read_only_repo(target_repos: list[Any], scope: dict[str, Any]) -> str | None:
    flags = scope.get("repository_flags") or {}
    if not isinstance(flags, dict):
        return None
    for repo in target_repos:
        repo_flags = flags.get(repo) or {}
        if isinstance(repo_flags, dict) and repo_flags.get("read_only"):
            return repo
    return None


def _diff_risk_reason(request: dict[str, Any], policy: dict[str, Any]) -> str | None:
    change = request.get("change") or {}
    defaults = policy.get("action_policy_defaults") or {}
    risk_gate = defaults.get("diff_risk_gate") or {}
    if not risk_gate.get("enabled", True):
        return None
    threshold = risk_gate.get("mass_deletion_file_threshold")
    if isinstance(threshold, int) and change.get("files_deleted", 0) >= threshold:
        return "mass deletion requires elevation"
    if change.get("touches_protected"):
        return "protected change requires elevation"
    return None


def _valid_elevation(elevation_token: Any, policy: dict[str, Any]) -> bool:
    approvers = set(_as_list((policy.get("elevation") or {}).get("approvers")))
    if isinstance(elevation_token, str):
        return elevation_token in approvers
    if isinstance(elevation_token, dict):
        return elevation_token.get("approver") in approvers
    return False


def _is_internal_operator(operator_id: Any, policy: dict[str, Any]) -> bool:
    approvers = _as_list((policy.get("elevation") or {}).get("approvers"))
    return operator_id in approvers


def _reply_visibility(scope: dict[str, Any], request: dict[str, Any]) -> str:
    if scope.get("sensitivity") == "internal":
        return FULL_VISIBILITY
    origin = request.get("origin") or {}
    if origin.get("is_dm"):
        return FULL_VISIBILITY
    channel_id = origin.get("channel_id")
    platform = request.get("platform")
    for binding in _as_list(scope.get("channel_repo_bindings")):
        if not isinstance(binding, dict):
            continue
        if binding.get("platform") == platform and binding.get("channel_id") == channel_id:
            return FULL_VISIBILITY
    return GENERIC_VISIBILITY


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
