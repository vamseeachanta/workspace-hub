"""Private run-time overlay for owner-specific lists (C19).

This public repository carries no client or contractor names, no client email
domains and no real mailbox addresses. Scripts that need them on the owner's
machines read them at run time from a private JSON file that never enters git:

    $WORKSPACE_HUB_PRIVATE_LISTS            (override, e.g. for tests)
    ~/.config/workspace-hub/private-lists.json   (default)

Behaviour
- File absent: ``load()`` returns ``{}``. Every consumer then runs on its public
  defaults only. This is the documented safe default: no private entry is added,
  and account resolution by address fails closed (``config_missing``).
- File present but unreadable, not JSON, of an unknown version, carrying an
  unknown key or a value of the wrong type: ``PrivateOverlayError``. A partial
  private list is never used silently. The message names the path and the
  offending key, never a value.

Schema (version 1; every section and key is optional)::

    {
      "version": 1,
      "email": {
        "vip_domains":    {"<account alias>": ["domain", ...]},
        "client_domains": ["domain", ...],
        "domain_company": {"domain": "Display name"},
        "routing_rules":  {"<sender key>": "<repo path> | DELETE | REVIEW"},
        "mailboxes":      {"<account alias>": "address"}
      },
      "job_market": {
        "priority_companies": ["lower-case name fragment", ...],
        "career_urls":        {"Company": "https://..."}
      },
      "outputs": {
        "job_market_dir":     "/absolute/path/in/a/private/checkout",
        "contact_report_dir": "/absolute/path/in/a/private/checkout"
      }
    }

``outputs`` names where generated artefacts that carry names or addresses are
written. ``require_output_dir`` fails closed when the key is unset, the path is
relative, the directory does not exist, or it lies inside the public repository.

Standard library only, so stdlib-only scripts can import it.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

ENV_VAR = "WORKSPACE_HUB_PRIVATE_LISTS"
DEFAULT_RELATIVE = Path(".config") / "workspace-hub" / "private-lists.json"
SCHEMA_VERSION = 1

# section -> key -> kind
_SCHEMA: dict[str, dict[str, str]] = {
    "email": {
        "vip_domains": "map_of_lists",
        "client_domains": "list",
        "domain_company": "map",
        "routing_rules": "map",
        "mailboxes": "map",
    },
    "job_market": {
        "priority_companies": "list",
        "career_urls": "map",
    },
    "outputs": {
        "job_market_dir": "str",
        "contact_report_dir": "str",
    },
}


class PrivateOverlayError(ValueError):
    """The private overlay exists but cannot be used safely."""


def resolve_path(env: Mapping[str, str] | None = None) -> Path:
    active = os.environ if env is None else env
    override = active.get(ENV_VAR)
    if override:
        return Path(override).expanduser()
    return Path.home() / DEFAULT_RELATIVE


def _is_str_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def _is_str_map(value: Any) -> bool:
    return isinstance(value, dict) and all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    )


def _validate(payload: Any, path: Path) -> dict:
    if not isinstance(payload, dict):
        raise PrivateOverlayError(f"{path}: top level must be a JSON object")
    if payload.get("version") != SCHEMA_VERSION:
        raise PrivateOverlayError(f"{path}: 'version' must be {SCHEMA_VERSION}")
    for section, body in payload.items():
        if section == "version":
            continue
        if section not in _SCHEMA:
            raise PrivateOverlayError(f"{path}: unknown section '{section}'")
        if not isinstance(body, dict):
            raise PrivateOverlayError(f"{path}: section '{section}' must be an object")
        for key, value in body.items():
            kind = _SCHEMA[section].get(key)
            if kind is None:
                raise PrivateOverlayError(f"{path}: unknown key '{section}.{key}'")
            ok = (
                isinstance(value, str) if kind == "str"
                else _is_str_list(value) if kind == "list"
                else _is_str_map(value) if kind == "map"
                else isinstance(value, dict) and all(
                    isinstance(k, str) and _is_str_list(v) for k, v in value.items()
                )
            )
            if not ok:
                raise PrivateOverlayError(
                    f"{path}: '{section}.{key}' has the wrong type (expected {kind})"
                )
    return payload


def load(path: str | os.PathLike[str] | None = None,
         env: Mapping[str, str] | None = None) -> dict:
    """Return the validated overlay, ``{}`` when the file is absent."""
    target = Path(path).expanduser() if path is not None else resolve_path(env)
    if not target.is_file():
        return {}
    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise PrivateOverlayError(f"{target}: unreadable ({exc.__class__.__name__})") from None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PrivateOverlayError(
            f"{target}: not valid JSON (line {exc.lineno}, column {exc.colno})"
        ) from None
    return _validate(payload, target)


def _get(overlay: Mapping[str, Any], dotted: str) -> Any:
    section, _, key = dotted.partition(".")
    return (overlay.get(section) or {}).get(key)


def get_list(overlay: Mapping[str, Any], dotted: str) -> list[str]:
    return list(_get(overlay, dotted) or [])


def get_mapping(overlay: Mapping[str, Any], dotted: str) -> dict:
    return dict(_get(overlay, dotted) or {})


def check_private_dir(value: str | os.PathLike[str], label: str,
                      public_root: str | os.PathLike[str]) -> Path:
    """Return ``value`` resolved, or raise when it is not a usable private directory.

    It must be absolute, exist as a directory and lie outside ``public_root``.
    Messages name ``label`` only, never the path.
    """
    raw = Path(value).expanduser()
    if not raw.is_absolute():
        raise PrivateOverlayError(f"{label}: must be an absolute path")
    target = raw.resolve()
    if not target.is_dir():
        raise PrivateOverlayError(f"{label}: directory does not exist")
    root = Path(public_root).resolve()
    if target == root or root in target.parents:
        raise PrivateOverlayError(f"{label}: lies inside the public repository")
    return target


def require_output_dir(overlay: Mapping[str, Any], dotted: str,
                       public_root: str | os.PathLike[str]) -> Path:
    """Private output directory named by ``dotted`` (e.g. ``outputs.job_market_dir``).

    Fails closed (``PrivateOverlayError``) when the key is unset or the directory
    fails ``check_private_dir``. Nothing is created.
    """
    value = _get(overlay, dotted)
    if not value:
        raise PrivateOverlayError(
            f"'{dotted}' is not set in the private overlay ({ENV_VAR} or "
            f"~/{DEFAULT_RELATIVE.as_posix()}); refusing to write outputs"
        )
    return check_private_dir(value, f"'{dotted}'", public_root)
