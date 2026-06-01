"""Hermes user plugin for Deckhand scope enforcement.
This plugin enforces Deckhand allow/deny decisions only. It does NOT inject a
scope PAT because Hermes pre_tool_call hooks cannot mutate the tool environment.
Allowed git/gh commands still run with ambient credentials until the B2
scoped-PAT executor lands.
"""
from __future__ import annotations
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import yaml

PLUGIN_DIR = Path(__file__).resolve().parent
REPO_ROOT = PLUGIN_DIR.parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
from deckhand import audit, engine, hook  # noqa: E402

CONFIG_DIR = REPO_ROOT / "config" / "deckhand"
GATED_TOOLS = {"terminal", "execute_code"}
TERMINAL_TOOLS = {"git", "gh", "hub"}
LOGGER = logging.getLogger(__name__)

def register(ctx: Any) -> None:
    ctx.register_command(
        "scope",
        handle_scope,
        description="Select active Deckhand scope",
        args_hint="[name]",
    )
    ctx.register_hook("pre_tool_call", on_pre_tool_call)

def handle_scope(raw_args: str = "") -> str:
    identity = _identity()
    scopes = _scopes()
    if not _has_identity(identity):
        return "denied: Deckhand cannot identify this operator/session"
    requested = (raw_args or "").strip()
    authorized = _authorized_scope_names(identity["operator_id"], scopes)
    if not requested:
        current = _active_scope_name(identity, scopes)
        current_text = current or "unset"
        scopes_text = ", ".join(authorized) if authorized else "none"
        return f"active scope = {current_text}; authorized scopes = {scopes_text}"
    scope = scopes.get(requested)
    if not isinstance(scope, dict):
        return f"denied: unknown Deckhand scope '{requested}'"
    if identity["operator_id"] not in _as_list(scope.get("operators")):
        return f"denied: operator is not authorized for Deckhand scope '{requested}'"
    _write_active_scope(identity, requested)
    return f"active scope = {requested} (write, destructive denied)"

def on_pre_tool_call(
    tool_name: str,
    args: dict[str, Any],
    task_id: str = "",
    session_id: str = "",
    tool_call_id: str = "",
    **kw: Any,
) -> dict[str, str] | None:
    if tool_name not in GATED_TOOLS:
        return None
    args = args if isinstance(args, dict) else {}
    try:
        if tool_name == "execute_code":
            return _handle_execute_code(args, task_id, session_id, tool_call_id)
        return _handle_terminal(args, task_id, session_id, tool_call_id)
    except Exception as exc:  # noqa: BLE001 - hook boundary must never throw into Hermes.
        return _handle_unexpected_error(tool_name, args, task_id, session_id, tool_call_id, exc)

def _handle_terminal(
    args: dict[str, Any],
    task_id: str,
    session_id: str,
    tool_call_id: str,
) -> dict[str, str] | None:
    command = str(args.get("command") or "")
    cwd = str(args.get("workdir") or os.getcwd())
    actions = hook.classify_command(command)
    if not actions:
        _audit_decision(
            decision="ALLOW",
            reason="no git/gh action detected",
            tool_name="terminal",
            command=command,
            task_id=task_id,
            session_id=session_id,
            tool_call_id=tool_call_id,
        )
        return None
    identity = _identity()
    config = _config()
    scope_name = _active_scope_name(identity, config.get("scopes", {}).get("scopes", {}))
    repo = _repo_from_cwd(cwd)
    request_context = {
        "operator_id": identity.get("operator_id"),
        "platform": identity.get("platform"),
        "scope_name": scope_name,
        "origin": {
            "is_dm": _best_effort_is_dm(identity),
            "channel_id": identity.get("chat_id"),
            "thread_id": identity.get("thread_id"),
        },
        "repo": repo,
    }
    outcome = hook.inspect(command, cwd=cwd, request_context=request_context, config=config)
    allowed = bool(outcome.get("allow"))
    reason = str(outcome.get("reason") or "denied")
    if _scope_missing_or_invalid(identity, scope_name, config) and _has_write_action(actions):
        allowed = False
        reason = "Deckhand scope required for git/gh writes; run /scope [name]"
    elif _has_write_action(actions) and not repo:
        # fail-closed: never allow a write whose target repo we cannot resolve
        # (engine treats empty target_repos as "nothing out of scope").
        allowed = False
        reason = "Deckhand: cannot resolve target repository for a write (run inside the scope's git repo)"
    decision = "ALLOW" if allowed else _deny_word()
    _audit_decision(
        decision=decision,
        reason=reason,
        tool_name="terminal",
        command=command,
        task_id=task_id,
        session_id=session_id,
        tool_call_id=tool_call_id,
        identity=identity,
        scope_name=scope_name,
        repo=repo,
        outcome=outcome,
    )
    if allowed or _report_mode():
        return None
    return {"action": "block", "message": reason}

def _handle_execute_code(
    args: dict[str, Any],
    task_id: str,
    session_id: str,
    tool_call_id: str,
) -> dict[str, str] | None:
    src = str(args.get("code") or "")
    should_block = hook.scan_python_source(src)
    reason = (
        "code-execution touching git/gh must go through an approved Deckhand path"
        if should_block
        else "no git/gh code-execution pattern detected"
    )
    _audit_decision(
        decision=_deny_word() if should_block else "ALLOW",
        reason=reason,
        tool_name="execute_code",
        task_id=task_id,
        session_id=session_id,
        tool_call_id=tool_call_id,
        identity=_identity(),
    )
    if should_block and not _report_mode():
        return {"action": "block", "message": reason}
    return None

def _handle_unexpected_error(
    tool_name: str,
    args: dict[str, Any],
    task_id: str,
    session_id: str,
    tool_call_id: str,
    exc: Exception,
) -> dict[str, str] | None:
    command = str(args.get("command") or "")
    is_write = _command_may_write(command) if tool_name == "terminal" else bool(args.get("code"))
    reason = f"Deckhand hook error: {type(exc).__name__}"
    _audit_decision(
        decision="DENY" if is_write else "ALLOW",
        reason=reason,
        tool_name=tool_name,
        command=command,
        task_id=task_id,
        session_id=session_id,
        tool_call_id=tool_call_id,
        identity=_identity(),
        error={"type": type(exc).__name__},
    )
    LOGGER.warning("Deckhand hook failed", exc_info=exc)
    if is_write and not _report_mode():
        return {"action": "block", "message": "Deckhand failed closed for this write; retry after /scope"}
    return None

def _identity() -> dict[str, str]:
    try:
        from gateway.session_context import get_session_env
    except Exception:  # noqa: BLE001 - plugin must load outside Hermes for local tests.
        return {"operator_id": "", "platform": "", "chat_id": "", "thread_id": ""}
    return {
        "operator_id": str(get_session_env("HERMES_SESSION_USER_ID", "") or ""),
        "platform": str(get_session_env("HERMES_SESSION_PLATFORM", "") or ""),
        "chat_id": str(get_session_env("HERMES_SESSION_CHAT_ID", "") or ""),
        "thread_id": str(get_session_env("HERMES_SESSION_THREAD_ID", "") or ""),
    }

def _config() -> dict[str, Any]:
    try:
        policy = yaml.safe_load((CONFIG_DIR / "policy.yml").read_text(encoding="utf-8"))
        scopes = yaml.safe_load((CONFIG_DIR / "scopes.yml").read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {"policy": {}, "scopes": {"scopes": {}, "origin_bound_default": {"enabled": False}}}
    return {
        "policy": policy if isinstance(policy, dict) else {},
        "scopes": scopes if isinstance(scopes, dict) else {"scopes": {}, "origin_bound_default": {"enabled": False}},
    }

def _scopes() -> dict[str, Any]:
    return _config().get("scopes", {}).get("scopes", {})

def _state_path(identity: dict[str, str]) -> Path:
    return (
        Path.home()
        / ".hermes"
        / "deckhand"
        / "active-scope"
        / _path_part(identity.get("platform"))
        / _path_part(identity.get("chat_id"))
        / f"{_path_part(identity.get('operator_id'))}.json"
    )

def _write_active_scope(identity: dict[str, str], scope_name: str) -> None:
    path = _state_path(identity)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "schema_version": 1,
        "platform": identity.get("platform"),
        "chat_id": identity.get("chat_id"),
        "thread_id": identity.get("thread_id"),
        "operator_id": identity.get("operator_id"),
        "scope_name": scope_name,
        "selected_at": _now(),
        "source": "/scope",
    }
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(record, handle, sort_keys=True, separators=(",", ":"))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)

def _active_scope_name(identity: dict[str, str], scopes: dict[str, Any]) -> str | None:
    if not _has_identity(identity):
        return None
    try:
        record = json.loads(_state_path(identity).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if record.get("schema_version") != 1:
        return None
    if record.get("operator_id") != identity.get("operator_id"):
        return None
    if record.get("platform") != identity.get("platform") or record.get("chat_id") != identity.get("chat_id"):
        return None
    scope_name = record.get("scope_name")
    scope = scopes.get(scope_name)
    if not isinstance(scope, dict):
        return None
    if identity["operator_id"] not in _as_list(scope.get("operators")):
        return None
    return str(scope_name)

def _scope_missing_or_invalid(identity: dict[str, str], scope_name: str | None, config: dict[str, Any]) -> bool:
    scopes = config.get("scopes", {}).get("scopes", {})
    if not _has_identity(identity) or not scope_name:
        return True
    scope = scopes.get(scope_name)
    return not isinstance(scope, dict) or identity["operator_id"] not in _as_list(scope.get("operators"))

def _authorized_scope_names(operator_id: str, scopes: dict[str, Any]) -> list[str]:
    names = []
    for name, scope in scopes.items():
        if isinstance(scope, dict) and operator_id in _as_list(scope.get("operators")):
            names.append(str(name))
    return sorted(names)

def _repo_from_cwd(cwd: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "config", "--get", "remote.origin.url"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return _normalize_repo(result.stdout.strip())

def _normalize_repo(remote: str) -> str | None:
    if not remote:
        return None
    patterns = [
        r"^git@github\.com:(?P<repo>[^/]+/[^/]+?)(?:\.git)?$",
        r"^https?://github\.com/(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$",
        r"^ssh://git@github\.com/(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$",
    ]
    for pattern in patterns:
        match = re.match(pattern, remote)
        if match:
            return match.group("repo")
    return None

def _audit_decision(
    *,
    decision: str,
    reason: str,
    tool_name: str,
    command: str = "",
    task_id: str = "",
    session_id: str = "",
    tool_call_id: str = "",
    identity: dict[str, str] | None = None,
    scope_name: str | None = None,
    repo: str | None = None,
    outcome: dict[str, Any] | None = None,
    error: dict[str, Any] | None = None,
) -> None:
    try:
        policy = _config().get("policy", {})
        audit.append_raw(
            {
                "decision": decision,
                "reason": reason,
                "tool_name": tool_name,
                "command": command,
                "task_id": task_id,
                "session_id": session_id,
                "tool_call_id": tool_call_id,
                "operator": (identity or {}).get("operator_id"),
                "platform": (identity or {}).get("platform"),
                "scope": scope_name,
                "repos": [repo] if repo else [],
                "outcome": outcome,
                "error": error,
            },
            path=_audit_path(policy),
            clock=_now,
        )
    except Exception as exc:  # noqa: BLE001 - audit is best-effort at plugin boundary.
        LOGGER.warning("Deckhand audit append failed: %s", exc)

def _audit_path(policy: dict[str, Any]) -> Path:
    raw_store = ((policy.get("audit") or {}).get("raw_store") or {}) if isinstance(policy, dict) else {}
    return Path(_expand_env_default(str(raw_store.get("path") or ""))) if raw_store.get("path") else Path.home() / ".hermes" / "deckhand" / "audit" / "decisions.ndjson"

def _expand_env_default(value: str) -> str:
    pattern = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")
    def replace(match: re.Match[str]) -> str:
        name, default = match.group(1), match.group(2)
        return os.environ.get(name) or (default or "")
    return pattern.sub(replace, os.path.expandvars(value))

def _has_identity(identity: dict[str, str]) -> bool:
    return bool(identity.get("operator_id") and identity.get("platform") and identity.get("chat_id"))

def _has_write_action(actions: list[Any]) -> bool:
    return any(getattr(action, "action_class", None) != engine.READ_ACTION for action in actions)

def _command_may_write(command: str) -> bool:
    actions = hook.classify_command(command)
    return bool(actions and _has_write_action(actions))

def _best_effort_is_dm(identity: dict[str, str]) -> bool:
    chat_id = str(identity.get("chat_id") or "").lower()
    return chat_id.startswith("dm") or chat_id == str(identity.get("operator_id") or "")

def _report_mode() -> bool:
    return os.environ.get("DECKHAND_ENFORCE", "block").strip().lower() == "report"

def _deny_word() -> str:
    return "WOULD_BLOCK" if _report_mode() else "DENY"

def _path_part(value: str | None) -> str:
    text = str(value or "unknown")
    return re.sub(r"[^A-Za-z0-9_.-]", "_", text) or "unknown"

def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
