"""Readiness reporting for Telegram/Hermes multi-machine dispatch (#2720)."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import socket
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.telegram_dispatch.redaction import redact_status
except ModuleNotFoundError:  # pragma: no cover - exercised by direct script invocation
    _redaction_path = Path(__file__).resolve().parents[1] / "telegram_dispatch" / "redaction.py"
    _redaction_spec = importlib.util.spec_from_file_location("telegram_dispatch_redaction", _redaction_path)
    if _redaction_spec is None or _redaction_spec.loader is None:
        raise
    _redaction_module = importlib.util.module_from_spec(_redaction_spec)
    _redaction_spec.loader.exec_module(_redaction_module)
    redact_status = _redaction_module.redact_status

SAFE_TRUE_VALUES = {"1", "true", "yes", "on"}
SECRET_KEY_RE = re.compile(r"(token|secret|api[_-]?key|password|credential)", re.IGNORECASE)
PRIVATE_TELEGRAM_METADATA_KEY_RE = re.compile(r"(allowed_?user_?ids?|chat_?id|invite_?link|phone(_?number)?)", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(r"\b(?:\d{6,}:[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]+)\b")
REDACTION = "[REDACTED]"
DISPATCH_REQUIRED_TOOLS = {"git", "gh", "hermes"}
DEFAULT_BOT_TOKEN_ENV = "TELEGRAM_HERMES_BOT_TOKEN"
DEFAULT_ALLOWED_USER_IDS_ENV = "TELEGRAM_HERMES_ALLOWED_USER_IDS"
ENV_POINTER_FIELDS = {"bot_token_env", "allowed_user_ids_env"}
EXPECTED_EVIDENCE_TYPE = "telegram-hermes-host-local-readiness"
EXPECTED_EVIDENCE_PRODUCER = "scripts/readiness/telegram_hermes_readiness.py"
REQUIRED_HOST_LOCAL_CHECKS = {"env_gates", "tool_contract", "workspace_contract", "git_sync", "data_access"}


def _redact_output(value: Any) -> Any:
    """Return a JSON-safe copy with secret-like values removed before CLI output."""
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, child in value.items():
            key_text = str(key)
            if key_text not in ENV_POINTER_FIELDS and (SECRET_KEY_RE.search(key_text) or PRIVATE_TELEGRAM_METADATA_KEY_RE.search(key_text)):
                redacted[key_text] = REDACTION
            else:
                redacted[key_text] = _redact_output(child)
        return redacted
    if isinstance(value, list):
        return [_redact_output(item) for item in value]
    if isinstance(value, str):
        return redact_status(SECRET_VALUE_RE.sub(REDACTION, value))
    return value


def _walk_for_secrets(value: Any, path: str = "root") -> list[str]:
    failures: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if SECRET_KEY_RE.search(key_text) and key_text not in ENV_POINTER_FIELDS:
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
        "dirty": False,
        "ahead": 0,
        "behind": 0,
        "missing_data": [],
        "failures": [],
        "warnings": [],
    }


def _is_local_host(host_id: str, raw: dict[str, Any]) -> bool:
    """Return whether registry host metadata refers to this execution host."""
    local_names = {socket.gethostname(), socket.getfqdn()}
    host_names = {host_id, str(raw.get("hostname") or "")}
    host_names.update(str(alias) for alias in (raw.get("hostname_aliases") or []))
    return bool(local_names & host_names)


def _collect_git_sync_state(root: Path) -> tuple[bool, int, int, list[str]]:
    """Return dirty/ahead/behind plus fail-closed git readiness failures."""
    failures: list[str] = []
    if not (root / ".git").exists():
        return True, 0, 0, ["workspace_root has no .git metadata"]
    dirty = False
    ahead = 0
    behind = 0
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
            timeout=60,
        )
        dirty = bool(status.stdout.strip()) if status.returncode == 0 else True
    except Exception as exc:  # noqa: BLE001 - readiness must be fail-soft
        dirty = True
        failures.append(f"git status unavailable: {exc.__class__.__name__}")
    try:
        upstream = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
            timeout=60,
        )
        if upstream.returncode == 0:
            counts = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", "HEAD...@{u}"],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False,
                timeout=60,
            )
            if counts.returncode == 0:
                left, right = counts.stdout.strip().split("\t", 1)
                ahead = int(left)
                behind = int(right)
            else:
                failures.append("git ahead/behind counts unavailable")
        else:
            failures.append("git upstream tracking branch unavailable")
    except Exception as exc:  # noqa: BLE001 - readiness must be fail-soft
        failures.append(f"git ahead/behind unavailable: {exc.__class__.__name__}")
    return dirty, ahead, behind, failures


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


def _parse_evidence_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _readiness_report_hours(raw: dict[str, Any]) -> float:
    tg = raw.get("telegram_hermes") or {}
    thresholds = tg.get("readiness_freshness_thresholds") or {}
    try:
        return float(thresholds.get("report_hours", 0))
    except (TypeError, ValueError):
        return 0.0


def _load_host_local_evidence(evidence_dir: str | Path | None, host_id: str, raw: dict[str, Any]) -> dict[str, Any] | None:
    """Load a host-local readiness evidence snapshot for remote hosts."""
    if evidence_dir is None:
        return None
    evidence_path = Path(evidence_dir) / f"{host_id}.json"
    if not evidence_path.exists():
        return None
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - malformed evidence is a readiness failure
        return {"failures": [f"host-local readiness evidence unreadable: {exc.__class__.__name__}"], "_invalid": True}
    if not isinstance(evidence, dict):
        return {"failures": ["host-local readiness evidence must be a JSON object"], "_invalid": True}

    failures: list[str] = []
    if evidence.get("evidence_type") != EXPECTED_EVIDENCE_TYPE:
        failures.append("host-local readiness evidence_type invalid or missing")
    if evidence.get("schema_version") != 1:
        failures.append("host-local readiness schema_version invalid or missing")
    if evidence.get("producer") != EXPECTED_EVIDENCE_PRODUCER:
        failures.append("host-local readiness evidence producer invalid or missing")

    checks = evidence.get("host_local_checks")
    if not isinstance(checks, dict):
        failures.append("host-local readiness evidence host_local_checks missing")
    else:
        missing_checks = sorted(REQUIRED_HOST_LOCAL_CHECKS - set(checks))
        if missing_checks:
            failures.append(f"host-local readiness evidence host_local_checks missing: {', '.join(missing_checks)}")
        for check_name in sorted(REQUIRED_HOST_LOCAL_CHECKS & set(checks)):
            if checks.get(check_name) is not True:
                failures.append(f"host-local readiness evidence host_local_checks.{check_name} is not true")

    if "host_id" not in evidence:
        failures.append("host-local readiness evidence host_id missing")
    elif evidence.get("host_id") != host_id:
        failures.append("host-local readiness evidence host_id mismatch")

    hostname = raw.get("hostname")
    if hostname and evidence.get("hostname") != hostname:
        failures.append("host-local readiness evidence hostname mismatch")

    generated_at = _parse_evidence_timestamp(evidence.get("generated_at"))
    if generated_at is None:
        failures.append("host-local readiness evidence generated_at missing or invalid")
    else:
        max_age_hours = _readiness_report_hours(raw)
        if max_age_hours <= 0:
            failures.append("host-local readiness freshness threshold missing or invalid")
        else:
            age_hours = (datetime.now(UTC) - generated_at).total_seconds() / 3600
            if age_hours < 0:
                failures.append("host-local readiness evidence generated_at is in the future")
            elif age_hours > max_age_hours:
                failures.append(f"host-local readiness evidence stale: {age_hours:.1f}h old exceeds {max_age_hours:.1f}h threshold")

    if failures:
        evidence_failures = evidence.get("failures") or []
        if not isinstance(evidence_failures, list):
            evidence_failures = ["host-local readiness evidence failures must be a list"]
        return {**evidence, "failures": [str(item) for item in evidence_failures] + failures, "_invalid": True}
    return evidence


def _apply_host_local_evidence(entry: dict[str, Any], evidence: dict[str, Any]) -> None:
    """Apply remote-host evidence and fail closed unless it proves clean/pass."""
    def coerce_int(field: str) -> int:
        value = evidence.get(field, 0) or 0
        try:
            return int(value)
        except (TypeError, ValueError):
            entry["failures"].append(f"host-local readiness evidence {field} must be an integer")
            return 0

    def coerce_str_list(field: str) -> list[str]:
        value = evidence.get(field) or []
        if not isinstance(value, list):
            entry["failures"].append(f"host-local readiness evidence {field} must be a list")
            return []
        return [str(item) for item in value]

    entry["dirty"] = bool(evidence.get("dirty", False))
    entry["ahead"] = coerce_int("ahead")
    entry["behind"] = coerce_int("behind")
    entry["missing_data"] = coerce_str_list("missing_data")
    entry["warnings"].extend(coerce_str_list("warnings"))
    entry["failures"].extend(coerce_str_list("failures"))
    if evidence.get("_invalid"):
        return
    if evidence.get("status") != "pass" or entry["dirty"] or entry["ahead"] or entry["behind"] or entry["missing_data"]:
        entry["failures"].append("host-local evidence is not clean/pass")


def collect_readiness(registry_path: str | Path, *, host_id: str | None = None, evidence_dir: str | Path | None = None) -> dict[str, Any]:
    """Collect a secret-free readiness report from registry metadata.

    The report intentionally avoids printing env var values; unsafe settings are
    reported by name only.
    """
    machines, errors = _load_registry(registry_path)
    if errors:
        return _redact_output({"overall_status": "fail", "hosts": {}, "errors": errors})

    assert machines is not None
    if host_id:
        resolved_id = _resolve_host_id(machines, host_id)
        if resolved_id is None:
            return _redact_output({"overall_status": "fail", "hosts": {}, "errors": [f"unknown host_id: {host_id}"]})
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

        local_host = _is_local_host(hid, raw)
        remote_evidence: dict[str, Any] | None = None
        if local_host:
            if allow_all_users:
                entry["failures"].append("GATEWAY_ALLOW_ALL_USERS is unsafe and must be false/unset")
            allowed_user_ids_env = str(tg.get("allowed_user_ids_env") or DEFAULT_ALLOWED_USER_IDS_ENV)
            if not os.environ.get(allowed_user_ids_env, "").strip():
                entry["failures"].append(f"{allowed_user_ids_env} allowlist must be configured")
            bot_token_env = str(tg.get("bot_token_env") or DEFAULT_BOT_TOKEN_ENV)
            if not os.environ.get(bot_token_env, "").strip():
                entry["failures"].append(f"{bot_token_env} bot token env var must be configured")
        else:
            remote_evidence = _load_host_local_evidence(evidence_dir, hid, raw)
            if remote_evidence is None:
                entry["warnings"].append("remote dispatch host; env gates require host-local readiness evidence")
                entry["missing_data"].append("host-local-readiness-evidence")
                entry["failures"].append("host-local readiness evidence missing for remote dispatch host")
            else:
                _apply_host_local_evidence(entry, remote_evidence)

        tools = set((raw.get("capabilities") or {}).get("tools") or [])
        missing_tools = sorted(DISPATCH_REQUIRED_TOOLS - tools)
        if missing_tools:
            entry["failures"].append(f"dispatch host missing required tools: {', '.join(missing_tools)}")

        if not local_host:
            if remote_evidence is None:
                entry["warnings"].append("remote dispatch host; filesystem and git checks skipped on control surface")
        else:
            root = Path(str(workspace_root))
            if not root.exists():
                entry["failures"].append("workspace_root not present on this machine")
            elif not (root / "AGENTS.md").exists():
                entry["failures"].append("AGENTS.md missing under workspace_root")
            else:
                dirty, ahead, behind, git_failures = _collect_git_sync_state(root)
                entry["dirty"] = dirty
                entry["ahead"] = ahead
                entry["behind"] = behind
                entry["failures"].extend(git_failures)
                if dirty:
                    entry["failures"].append("workspace_root has uncommitted or untracked git changes")
                if ahead:
                    entry["failures"].append(f"workspace_root is ahead of upstream by {ahead} commit(s)")
                if behind:
                    entry["failures"].append(f"workspace_root is behind upstream by {behind} commit(s)")

            data_access = tg.get("data_access_profile") or {}
            for storage_root in data_access.get("storage_roots") or []:
                if storage_root and not Path(str(storage_root)).exists():
                    entry["missing_data"].append(str(storage_root))
                    entry["failures"].append(f"data_access_profile.storage_roots missing: {storage_root}")
            for remote_mount in data_access.get("remote_mounts") or []:
                if remote_mount and not Path(str(remote_mount)).exists():
                    entry["missing_data"].append(str(remote_mount))
                    entry["failures"].append(f"data_access_profile.remote_mounts missing: {remote_mount}")

        required_tg = ["telegram_mode", "hermes_profile", "sync_policy", "data_access_profile", "readiness_freshness_thresholds"]
        for key in required_tg:
            if key not in tg:
                entry["failures"].append(f"telegram_hermes.{key} missing")

        if entry["failures"]:
            entry["status"] = "fail"
            entry["dispatchable"] = False
        elif entry["warnings"]:
            entry["status"] = "warn"
            entry["dispatchable"] = False
        else:
            entry["status"] = "pass"
            entry["dispatchable"] = True
        hosts[hid] = entry

    statuses = {h.get("status") for h in hosts.values()}
    overall = "fail" if "fail" in statuses else "warn" if ({"warn", "status-only", "not-onboarded"} & statuses) else "pass"
    return _redact_output({"overall_status": overall, "hosts": hosts, "errors": []})


def _build_host_local_evidence(host_id: str, host: dict[str, Any]) -> dict[str, Any]:
    """Build a host-local evidence snapshot for remote control surfaces."""
    failures = list(host.get("failures") or [])
    return {
        "evidence_type": EXPECTED_EVIDENCE_TYPE,
        "schema_version": 1,
        "producer": EXPECTED_EVIDENCE_PRODUCER,
        "host_id": host_id,
        "hostname": host.get("hostname"),
        "generated_at": datetime.now(UTC).isoformat(),
        "status": host.get("status"),
        "dirty": bool(host.get("dirty", False)),
        "ahead": int(host.get("ahead", 0) or 0),
        "behind": int(host.get("behind", 0) or 0),
        "missing_data": list(host.get("missing_data") or []),
        "failures": failures,
        "warnings": list(host.get("warnings") or []),
        "host_local_checks": {
            "env_gates": not any("ALLOW_ALL_USERS" in item or "allowlist" in item or "bot token env" in item for item in failures),
            "tool_contract": not any("missing required tools" in item for item in failures),
            "workspace_contract": not any("workspace_root" in item or "AGENTS.md" in item for item in failures),
            "git_sync": not bool(host.get("dirty") or host.get("ahead") or host.get("behind") or any("git" in item.lower() for item in failures)),
            "data_access": not bool(host.get("missing_data") or any("data_access_profile" in item for item in failures)),
        },
    }


def _write_local_evidence_if_requested(
    registry_path: str | Path,
    *,
    host_id: str | None,
    evidence_dir: str | Path | None,
    report: dict[str, Any],
) -> None:
    """Write host-local evidence only for the selected local host."""
    if not host_id or evidence_dir is None or len(report.get("hosts") or {}) != 1:
        return
    machines, errors = _load_registry(registry_path)
    if errors or machines is None:
        return
    resolved_id = _resolve_host_id(machines, host_id)
    if resolved_id is None:
        return
    raw = machines.get(resolved_id)
    if not isinstance(raw, dict) or not _is_local_host(resolved_id, raw):
        return
    host = report.get("hosts", {}).get(resolved_id)
    if not isinstance(host, dict):
        return
    output_dir = Path(evidence_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{resolved_id}.json").write_text(json.dumps(_redact_output(_build_host_local_evidence(resolved_id, host)), indent=2, sort_keys=True), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Telegram/Hermes dispatch readiness")
    parser.add_argument("--registry", default="config/workstations/registry.yaml")
    parser.add_argument("--host")
    parser.add_argument("--evidence-dir", help="Directory containing host-local readiness JSON evidence files")
    args = parser.parse_args(argv)
    report = collect_readiness(args.registry, host_id=args.host, evidence_dir=args.evidence_dir)
    _write_local_evidence_if_requested(args.registry, host_id=args.host, evidence_dir=args.evidence_dir, report=report)
    print(json.dumps(_redact_output(report), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
