"""Resolve the active Deckhand scope PAT environment variable for shims."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "deckhand" / "scopes.yml"


def identity_from_env(env: Mapping[str, str] | None = None) -> dict[str, str]:
    source = env or os.environ
    return {
        "operator_id": str(source.get("HERMES_SESSION_USER_ID", "") or ""),
        "platform": str(source.get("HERMES_SESSION_PLATFORM", "") or ""),
        "chat_id": str(source.get("HERMES_SESSION_CHAT_ID", "") or ""),
        "thread_id": str(source.get("HERMES_SESSION_THREAD_ID", "") or ""),
    }


def resolve_pat_env(
    *,
    env: Mapping[str, str] | None = None,
    config_path: str | Path | None = None,
    home: str | Path | None = None,
) -> str | None:
    identity = identity_from_env(env)
    if not _has_identity(identity):
        return None

    scopes = _load_scopes(config_path)
    scope_name = _scope_from_state(identity, scopes, home=home) or _scope_from_binding(identity, scopes)
    if not scope_name:
        return None

    scope = scopes.get(scope_name)
    if not isinstance(scope, dict):
        return None
    if identity["operator_id"] not in _as_list(scope.get("operators")):
        return None

    pat_env = scope.get("pat_env")
    if not isinstance(pat_env, str) or not pat_env.strip():
        return None
    return pat_env.strip()


def main() -> int:
    pat_env = resolve_pat_env()
    if not pat_env:
        return 3
    print(pat_env)
    return 0


def _load_scopes(config_path: str | Path | None) -> dict[str, Any]:
    path = Path(config_path) if config_path else Path(os.environ.get("DECKHAND_SCOPES_CONFIG", DEFAULT_CONFIG_PATH))
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    if not isinstance(data, dict):
        return {}
    scopes = data.get("scopes")
    return scopes if isinstance(scopes, dict) else {}


def _scope_from_state(identity: dict[str, str], scopes: dict[str, Any], *, home: str | Path | None) -> str | None:
    try:
        record = json.loads(_state_path(identity, home=home).read_text(encoding="utf-8"))
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


def _scope_from_binding(identity: dict[str, str], scopes: dict[str, Any]) -> str | None:
    platform = identity.get("platform")
    chat_id = str(identity.get("chat_id") or "")
    operator_id = identity.get("operator_id")
    for name, scope in scopes.items():
        if not isinstance(scope, dict):
            continue
        if operator_id not in _as_list(scope.get("operators")):
            continue
        for binding in _as_list(scope.get("channel_repo_bindings")):
            if (
                isinstance(binding, dict)
                and binding.get("platform") == platform
                and str(binding.get("channel_id")) == chat_id
            ):
                return str(name)
    return None


def _state_path(identity: dict[str, str], *, home: str | Path | None) -> Path:
    root = Path(home) if home else Path.home()
    return (
        root
        / ".hermes"
        / "deckhand"
        / "active-scope"
        / _path_part(identity.get("platform"))
        / _path_part(identity.get("chat_id"))
        / f"{_path_part(identity.get('operator_id'))}.json"
    )


def _has_identity(identity: dict[str, str]) -> bool:
    return bool(identity.get("operator_id") and identity.get("platform") and identity.get("chat_id"))


def _path_part(value: str | None) -> str:
    text = str(value or "unknown")
    return re.sub(r"[^A-Za-z0-9_.-]", "_", text) or "unknown"


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


if __name__ == "__main__":
    sys.exit(main())
