"""Readiness reporting for Telegram/Hermes multi-machine dispatch (#2720)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import yaml

SAFE_TRUE_VALUES = {"1", "true", "yes", "on"}
SECRET_KEY_RE = re.compile(r"(token|secret|api[_-]?key|password|credential)", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(r"\b(?:\d{6,}:[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]+)\b")
DISPATCH_REQUIRED_TOOLS = {"git", "gh", "hermes"}


def _walk_for_secrets(value: Any, path: str = "root") -> list[str]:
    failures: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if SECRET_KEY_RE.search(key_text):
                failures.append(f"registry contains secret-like field {child_path}")
            failures.extend(_walk_for_secrets(child, child_path))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            failures.extend(_walk_for_secrets(child, f"{path}[{idx}]"))
    elif isinstance(value, str) and SECRET_VALUE_RE.search(value):
        failures.append(f"registry contains secret-like value at {path}")
    return failures


def _base_host(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "hostname": raw.get("hostname"),
        "os": raw.get("os"),
        "role": raw.get("role"),
        "workspace_root": raw.get("workspace_root"),
        "dispatchable": False,
        "status": "fail",
        "failures": [],
        "warnings": [],
    }


def _load_registry(path: str | Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("machines"), dict):
            return None, ["registry must contain machines mapping"]
        secret_failures = _walk_for_secrets(data)
        if secret_failures:
            return None, secret_failures
        return data["machines"], []
    except Exception as exc:  # noqa: BLE001 - fail closed for malformed registry
        return None, [f"registry unreadable: {exc.__class__.__name__}"]


def _resolve_host_id(machines: dict[str, Any], selector: str) -> str | None:
    """Resolve a logical host id from host id, hostname, or hostname_aliases."""
    if selector in machines:
        return selector
    matches: list[str] = []
    for host_id, raw in machines.items():
        if not isinstance(raw, dict):
            continue
        aliases = raw.get("hostname_aliases") or []
        if raw.get("hostname") == selector or selector in aliases:
            matches.append(host_id)
    if len(matches) == 1:
        return matches[0]
    return None


def collect_readiness(registry_path: str | Path, *, host_id: str | None = None) -> dict[str, Any]:
    """Collect a secret-free readiness report from registry metadata.

    The report intentionally avoids printing env var values; unsafe settings are
    reported by name only.
    """
    machines, errors = _load_registry(registry_path)
    if errors:
        return {"overall_status": "fail", "hosts": {}, "errors": errors}

    assert machines is not None
    if host_id:
        resolved_id = _resolve_host_id(machines, host_id)
        if resolved_id is None:
            return {"overall_status": "fail", "hosts": {}, "errors": [f"unknown host_id: {host_id}"]}
        selected = {resolved_id: machines[resolved_id]}
    else:
        selected = machines
    hosts: dict[str, Any] = {}
    allow_all_users = os.environ.get("GATEWAY_ALLOW_ALL_USERS", "").strip().lower() in SAFE_TRUE_VALUES

    for hid, raw in selected.items():
        if not isinstance(raw, dict):
            hosts[hid] = {"status": "fail", "dispatchable": False, "failures": ["machine record is not a mapping"], "warnings": []}
            continue
        entry = _base_host(raw)
        tg = raw.get("telegram_hermes") or {}
        dispatch_enabled = bool(tg.get("dispatch_enabled", False))
        entry["telegram_mode"] = tg.get("telegram_mode", "disabled")
        entry["hermes_profile"] = tg.get("hermes_profile", "manual")
        entry["sync_policy"] = tg.get("sync_policy", "manual-status-only")

        workspace_root = raw.get("workspace_root")
        if workspace_root is None:
            entry["status"] = "not-onboarded"
            entry["failures"].append("workspace_root is not configured")
            hosts[hid] = entry
            continue

        if not dispatch_enabled:
            entry["status"] = "status-only"
            entry["warnings"].append("dispatch_enabled is false; host is manual/status-only")
            hosts[hid] = entry
            continue

        if allow_all_users:
            entry["failures"].append("GATEWAY_ALLOW_ALL_USERS is unsafe and must be false/unset")
        if not os.environ.get("TELEGRAM_HERMES_ALLOWED_USER_IDS", "").strip():
            entry["failures"].append("TELEGRAM_HERMES_ALLOWED_USER_IDS allowlist must be configured")

        tools = set((raw.get("capabilities") or {}).get("tools") or [])
        missing_tools = sorted(DISPATCH_REQUIRED_TOOLS - tools)
        if missing_tools:
            entry["failures"].append(f"dispatch host missing required tools: {', '.join(missing_tools)}")

        if raw.get("os") == "linux":
            root = Path(str(workspace_root))
            if not root.exists():
                entry["warnings"].append("workspace_root not present on this machine; treating as remote evidence")
            elif not (root / "AGENTS.md").exists():
                entry["failures"].append("AGENTS.md missing under workspace_root")

        required_tg = ["telegram_mode", "hermes_profile", "sync_policy", "data_access_profile", "readiness_freshness_thresholds"]
        for key in required_tg:
            if key not in tg:
                entry["failures"].append(f"telegram_hermes.{key} missing")

        if entry["failures"]:
            entry["status"] = "fail"
            entry["dispatchable"] = False
        elif entry["warnings"]:
            entry["status"] = "warn"
            entry["dispatchable"] = True
        else:
            entry["status"] = "pass"
            entry["dispatchable"] = True
        hosts[hid] = entry

    statuses = {h.get("status") for h in hosts.values()}
    overall = "fail" if "fail" in statuses else "warn" if ({"warn", "status-only", "not-onboarded"} & statuses) else "pass"
    return {"overall_status": overall, "hosts": hosts, "errors": []}


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Telegram/Hermes dispatch readiness")
    parser.add_argument("--registry", default="config/workstations/registry.yaml")
    parser.add_argument("--host")
    args = parser.parse_args(argv)
    print(json.dumps(collect_readiness(args.registry, host_id=args.host), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
