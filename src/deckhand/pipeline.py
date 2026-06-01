"""End-to-end Deckhand dry-run evaluation pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, MutableMapping

import yaml

from . import audit, engine, hook, runtime


Clock = Callable[[], str]
Executor = Callable[[dict[str, Any]], dict[str, Any]]
RateStore = MutableMapping[str, Any]


def evaluate(
    command: str,
    *,
    cwd: str | Path,
    request_context: dict[str, Any],
    config_dir: str | Path | dict[str, Any] = "config/deckhand",
    executor: Executor | None = None,
    clock: Clock,
    rate_store: RateStore,
    audit_path: str | Path,
) -> dict[str, Any]:
    """Evaluate one shell command through hook, runtime, and audit in dry-run mode."""
    loaded_config = load_config(config_dir, repo_root=_repo_root_from(cwd))
    hook_outcome = hook.inspect(
        command,
        cwd=str(cwd),
        request_context=request_context,
        config=loaded_config,
    )
    actions = list(hook_outcome.get("actions") or [])

    if not hook_outcome.get("allow"):
        persisted = audit.append_raw(
            _deny_audit_record(hook_outcome, request_context),
            path=audit_path,
            clock=clock,
        )
        return {
            "allow": False,
            "reason": hook_outcome.get("reason", "denied"),
            "dry_run": True,
            "actions": actions,
            "audit_decision_id": persisted["decision_id"],
            "would_execute": None,
        }

    request = _runtime_request(request_context, actions)
    selected_executor = executor or dry_run_executor
    runtime_outcome = runtime.handle(
        request,
        config=loaded_config,
        executor=selected_executor,
        clock=clock,
        rate_store=rate_store,
        audit_path=audit_path,
    )
    decision = runtime_outcome.get("decision") or {}
    result = runtime_outcome.get("result") or {}
    return {
        "allow": bool(decision.get("allow")),
        "reason": decision.get("reason", "denied"),
        "dry_run": bool(result.get("dry_run", True)),
        "actions": actions,
        "audit_decision_id": runtime_outcome.get("decision_id"),
        "would_execute": result.get("would_execute") if runtime_outcome.get("executed") else None,
    }


def dry_run_executor(request: dict[str, Any]) -> dict[str, Any]:
    """Return a safe execution summary without invoking git, gh, or any shell."""
    actions = request.get("actions")
    action_list = actions if isinstance(actions, list) else []
    git_or_gh = any(action.get("tool") in {"git", "gh", "hub"} for action in action_list if isinstance(action, dict))
    return {
        "dry_run": True,
        "would_execute": {
            "action_count": len(action_list),
            "git_or_gh": git_or_gh,
            "write": request.get("action_class") != engine.READ_ACTION,
        },
    }


def load_config(config_dir: str | Path | dict[str, Any], *, repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load Deckhand policy and scopes as the dict form expected by hook/engine/runtime."""
    if isinstance(config_dir, dict):
        return config_dir

    path = Path(config_dir)
    if not path.is_absolute():
        base = Path(repo_root) if repo_root is not None else _repo_root_from(Path.cwd())
        path = base / path

    policy = yaml.safe_load((path / "policy.yml").read_text(encoding="utf-8"))
    scopes = yaml.safe_load((path / "scopes.yml").read_text(encoding="utf-8"))
    if not isinstance(policy, dict) or not isinstance(scopes, dict):
        raise ValueError(f"invalid Deckhand config in {path}")
    return {"policy": policy, "scopes": scopes}


def _repo_root_from(path: str | Path) -> Path:
    candidate = Path(path).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for current in (candidate, *candidate.parents):
        if (current / ".git").exists():
            return current
    return candidate


def _runtime_request(request_context: dict[str, Any], actions: list[dict[str, Any]]) -> dict[str, Any]:
    selected = _selected_action(actions)
    repo = request_context.get("repo") or request_context.get("target_repo")
    target_repos = request_context.get("target_repos") or ([repo] if repo else [])
    return {
        "operator_id": request_context.get("operator_id"),
        "platform": request_context.get("platform"),
        "scope_name": request_context.get("scope_name"),
        "origin": request_context.get("origin") or {},
        "target_repos": target_repos,
        "action_class": selected.get("action_class", engine.READ_ACTION),
        "change": request_context.get("change") or {"files_deleted": 0, "touches_protected": False},
        "elevation_token": request_context.get("elevation_token"),
        "actions": actions,
    }


def _selected_action(actions: list[dict[str, Any]]) -> dict[str, Any]:
    for action in actions:
        if action.get("action_class") != engine.READ_ACTION:
            return action
    return actions[0] if actions else {"action_class": engine.READ_ACTION}


def _deny_audit_record(hook_outcome: dict[str, Any], request_context: dict[str, Any]) -> dict[str, Any]:
    denied_decision = next(
        (decision for decision in hook_outcome.get("decisions") or [] if not decision.get("allow")),
        None,
    )
    if isinstance(denied_decision, dict) and isinstance(denied_decision.get("audit"), dict):
        record = dict(denied_decision["audit"])
    else:
        action_class = _selected_action(list(hook_outcome.get("actions") or [])).get("action_class")
        repo = request_context.get("repo") or request_context.get("target_repo")
        record = {
            "operator": request_context.get("operator_id"),
            "platform": request_context.get("platform"),
            "scope": request_context.get("scope_name"),
            "repos": request_context.get("target_repos") or ([repo] if repo else []),
            "action_class": action_class,
            "decision": "DENY",
            "reason": hook_outcome.get("reason", "denied"),
        }
    record["status"] = "DENY"
    record["decision"] = "DENY"
    record["reason"] = hook_outcome.get("reason", record.get("reason", "denied"))
    return record
