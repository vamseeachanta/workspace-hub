#!/usr/bin/env python3
# ABOUTME: Inspect local Claude/Codex/Gemini configs and session logs for auth/runtime drift and write provider-health.yaml.

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = REPO_ROOT / "config/ai_agents/provider-health.yaml"
HOME = Path.home()
NOW = datetime.now(timezone.utc)
SKILLS_ROOT = REPO_ROOT / ".claude" / "skills"


def iso_now() -> str:
    return NOW.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_version(cmd: list[str]) -> str | None:
    if not shutil.which(cmd[0]):
        return None
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False)
    except Exception:
        return None
    out = (res.stdout or res.stderr or "").strip().splitlines()
    return out[0].strip() if out else None


def extract_semver(text: str | None) -> str | None:
    if not text:
        return None
    m = re.search(r"(\d+\.\d+\.\d+)", text)
    return m.group(1) if m else None


def parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            if value > 1e12:
                value = value / 1000
            return datetime.fromtimestamp(value, tz=timezone.utc)
        text = str(value)
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def choose_status(*statuses: str) -> str:
    if "block" in statuses:
        return "block"
    if "warn" in statuses:
        return "warn"
    return "ok"


def routing_state(status: str) -> str:
    return {
        "ok": "eligible",
        "warn": "fallback_only",
        "block": "blocked",
    }[status]


def count_claude_auth_errors() -> dict[str, Any]:
    cutoff_14d = NOW - timedelta(days=14)
    cutoff_24h = NOW - timedelta(days=1)
    roots = [HOME / ".claude/projects/-mnt-workspace-hub", HOME / ".claude/projects/-mnt-local-analysis-workspace-hub"]
    raw_14d = 0
    raw_24h = 0
    unrecovered_14d = 0
    unrecovered_24h = 0
    recovered_14d = 0
    reasons: Counter[str] = Counter()
    days: set[str] = set()
    last_auth_failure_at = None
    last_auth_failure_reason = None
    last_successful_login_at = None

    def auth_reason(text: str) -> str:
        lowered = text.lower()
        if "expired" in lowered:
            return "expired_token"
        if "invalid authentication credentials" in lowered:
            return "invalid_credentials"
        return "auth_error"

    for root in roots:
        if not root.exists():
            continue
        for path in root.glob("*.jsonl"):
            pending_failures: list[tuple[datetime, str]] = []
            try:
                with path.open(encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                        except Exception:
                            continue
                        dt = parse_dt(obj.get("timestamp"))
                        if dt is None:
                            continue
                        text = json.dumps(obj)
                        if dt >= cutoff_14d and (
                            "authentication_failed" in text or "Please run /login" in text or "OAuth token has expired" in text
                        ):
                            reason = auth_reason(text)
                            pending_failures.append((dt, reason))
                            raw_14d += 1
                            if dt >= cutoff_24h:
                                raw_24h += 1
                            reasons[reason] += 1
                            days.add(dt.date().isoformat())
                            if last_auth_failure_at is None or dt > last_auth_failure_at:
                                last_auth_failure_at = dt
                                last_auth_failure_reason = reason
                            continue

                        login_success = "Login successful" in text
                        non_auth_activity = dt >= cutoff_14d and pending_failures and (
                            (obj.get("type") in {"assistant", "user", "progress", "system"} and "authentication_failed" not in text and "Please run /login" not in text)
                        )

                        if login_success:
                            last_successful_login_at = dt if last_successful_login_at is None or dt > last_successful_login_at else last_successful_login_at
                            continue

                        if non_auth_activity:
                            for fail_dt, _ in pending_failures:
                                recovered_14d += 1
                                if fail_dt >= cutoff_24h:
                                    # recovered within 24h still counts as recovered, not unrecovered
                                    pass
                            pending_failures.clear()

                for fail_dt, _ in pending_failures:
                    if fail_dt >= cutoff_14d:
                        unrecovered_14d += 1
                    if fail_dt >= cutoff_24h:
                        unrecovered_24h += 1
            except Exception:
                continue
    return {
        "recent_auth_errors_14d": raw_14d,
        "recent_auth_errors_24h": raw_24h,
        "unrecovered_auth_errors_14d": unrecovered_14d,
        "unrecovered_auth_errors_24h": unrecovered_24h,
        "recovered_auth_errors_14d": recovered_14d,
        "auth_error_days_14d": len(days),
        "recent_auth_error_reasons": dict(reasons),
        "last_auth_failure_at": last_auth_failure_at.isoformat().replace('+00:00', 'Z') if last_auth_failure_at else None,
        "last_auth_failure_reason": last_auth_failure_reason,
        "last_successful_login_at": last_successful_login_at.isoformat().replace('+00:00', 'Z') if last_successful_login_at else None,
    }


def analyze_codex_logs() -> dict[str, Any]:
    cutoff_30d = NOW - timedelta(days=30)
    cutoff_7d = NOW - timedelta(days=7)
    log_path = HOME / ".codex/log/codex-tui.log"
    out: dict[str, Any] = {
        "skill_load_errors_30d": 0,
        "skill_load_errors_7d": 0,
        "skill_error_days_30d": 0,
        "unique_failed_skills_30d": 0,
        "plugin_manager_warnings_30d": 0,
        "plugin_manager_warnings_7d": 0,
        "plugin_manager_days_30d": 0,
        "plugin_manifest_warnings_30d": 0,
        "plugin_manifest_warnings_7d": 0,
        "plugin_manifest_days_30d": 0,
        "unique_manifest_paths_30d": 0,
        "shell_snapshot_warnings_30d": 0,
        "shell_snapshot_warnings_7d": 0,
        "shell_snapshot_days_30d": 0,
        "recent_targets": {},
    }
    if not log_path.exists():
        return out

    line_re = re.compile(r"^(\S+)\s+")
    target_re = re.compile(r"\b(INFO|WARN|ERROR|DEBUG)\s+([^:]+(?:::[^:]+)*)")
    skill_re = re.compile(r"failed to load skill (.*?/SKILL\.md):")
    manifest_path_re = re.compile(r"path=([^\s]+)\s*$")
    recent_targets: Counter[str] = Counter()
    skill_days: set[str] = set()
    plugin_days: set[str] = set()
    manifest_days: set[str] = set()
    snapshot_days: set[str] = set()
    failed_skills: set[str] = set()
    manifest_paths: set[str] = set()

    try:
        with log_path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                m = line_re.match(line)
                if not m:
                    continue
                dt = parse_dt(m.group(1))
                if dt is None or dt < cutoff_30d:
                    continue
                day = dt.date().isoformat()
                if "failed to load skill" in line:
                    out["skill_load_errors_30d"] += 1
                    if dt >= cutoff_7d:
                        out["skill_load_errors_7d"] += 1
                    skill_days.add(day)
                    ms = skill_re.search(line)
                    if ms:
                        failed_skills.add(ms.group(1))
                if "WARN" in line and "codex_core::plugins::manager" in line:
                    out["plugin_manager_warnings_30d"] += 1
                    if dt >= cutoff_7d:
                        out["plugin_manager_warnings_7d"] += 1
                    plugin_days.add(day)
                if "WARN" in line and "codex_core::plugins::manifest" in line:
                    out["plugin_manifest_warnings_30d"] += 1
                    if dt >= cutoff_7d:
                        out["plugin_manifest_warnings_7d"] += 1
                    manifest_days.add(day)
                    mm = manifest_path_re.search(line.strip())
                    if mm:
                        manifest_paths.add(mm.group(1))
                if "WARN" in line and "codex_core::shell_snapshot" in line:
                    out["shell_snapshot_warnings_30d"] += 1
                    if dt >= cutoff_7d:
                        out["shell_snapshot_warnings_7d"] += 1
                    snapshot_days.add(day)
                mt = target_re.search(line)
                if mt:
                    recent_targets[mt.group(2)] += 1
    except Exception:
        pass

    out["skill_error_days_30d"] = len(skill_days)
    out["unique_failed_skills_30d"] = len(failed_skills)
    out["plugin_manager_days_30d"] = len(plugin_days)
    out["plugin_manifest_days_30d"] = len(manifest_days)
    out["unique_manifest_paths_30d"] = len(manifest_paths)
    out["shell_snapshot_days_30d"] = len(snapshot_days)
    out["recent_targets"] = dict(recent_targets.most_common(5))
    return out


def analyze_codex_live_skills() -> dict[str, Any]:
    dir_count = 0
    oversize_name_paths: list[str] = []
    if not SKILLS_ROOT.exists():
        return {
            "skills_tree_dirs_current": 0,
            "oversize_skill_names_current": 0,
            "oversize_skill_name_paths": [],
        }
    for _ in SKILLS_ROOT.glob("**/"):
        dir_count += 1
    for skill in SKILLS_ROOT.glob("**/SKILL.md"):
        try:
            text = skill.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            continue
        end = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                end = i
                break
        if end is None:
            continue
        frontmatter = "\n".join(lines[1:end])
        m = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+)", frontmatter)
        if m and len(m.group(1).strip()) > 64:
            oversize_name_paths.append(str(skill))
    return {
        "skills_tree_dirs_current": dir_count,
        "oversize_skill_names_current": len(oversize_name_paths),
        "oversize_skill_name_paths": oversize_name_paths[:10],
    }


def analyze_gemini() -> dict[str, Any]:
    base = HOME / ".gemini/tmp"
    cutoff_30d = NOW - timedelta(days=30)
    cutoff_7d = NOW - timedelta(days=7)
    errors_30d = 0
    errors_7d = 0
    workspace_last_seen: dict[str, datetime] = {}
    workspace_counts: Counter[str] = Counter()
    temp_workspace_re = re.compile(r"^(tmp|tmp-[a-z0-9]+)$")
    orphan_temp_roots = 0

    if not base.exists():
        return {
            "chat_errors_30d": 0,
            "chat_errors_7d": 0,
            "workspace_roots_30d": 0,
            "stale_workspace_roots_7d": 0,
            "temp_workspace_roots_30d": 0,
            "orphan_temp_workspace_roots_30d": 0,
            "workspace_counts": {},
        }

    def should_count_workspace(path: Path, dt: datetime | None) -> tuple[bool, str]:
        if dt is None or dt < cutoff_30d or "tmp" not in path.parts:
            return False, "out-of-window"
        workspace = path.parts[path.parts.index("tmp") + 1]
        if temp_workspace_re.match(workspace):
            project_root_file = path.parents[1] / workspace / ".project_root"
            if project_root_file.exists():
                try:
                    project_root = project_root_file.read_text(encoding="utf-8", errors="replace").strip()
                except Exception:
                    project_root = ""
                if project_root.startswith("/tmp") and not Path(project_root).exists():
                    return False, "orphan-temp-root"
        return True, workspace

    def note_workspace(path: Path, dt: datetime | None) -> None:
        nonlocal orphan_temp_roots
        ok, result = should_count_workspace(path, dt)
        if not ok:
            if result == "orphan-temp-root":
                orphan_temp_roots += 1
            return
        workspace = result
        prev = workspace_last_seen.get(workspace)
        if prev is None or dt > prev:
            workspace_last_seen[workspace] = dt
        workspace_counts[workspace] += 1

    for path in base.glob("**/chats/session-*.json"):
        try:
            obj = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        for msg in obj.get("messages", []):
            dt = parse_dt(msg.get("timestamp"))
            note_workspace(path, dt)
            if dt is None or dt < cutoff_30d:
                continue
            if msg.get("type") == "error":
                errors_30d += 1
                if dt >= cutoff_7d:
                    errors_7d += 1

    for path in base.glob("**/logs.json"):
        try:
            arr = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        for msg in arr:
            dt = parse_dt(msg.get("timestamp"))
            note_workspace(path, dt)
            if dt is None or dt < cutoff_30d:
                continue
            if msg.get("type") == "error":
                errors_30d += 1
                if dt >= cutoff_7d:
                    errors_7d += 1

    stale_7d = sum(1 for _, dt in workspace_last_seen.items() if dt < cutoff_7d)
    temp_roots = sum(1 for name in workspace_last_seen if temp_workspace_re.match(name))
    return {
        "chat_errors_30d": errors_30d,
        "chat_errors_7d": errors_7d,
        "workspace_roots_30d": len(workspace_last_seen),
        "stale_workspace_roots_7d": stale_7d,
        "temp_workspace_roots_30d": temp_roots,
        "orphan_temp_workspace_roots_30d": orphan_temp_roots,
        "workspace_counts": dict(workspace_counts.most_common(8)),
    }


def claude_status(binary_available: bool, config_present: bool, metrics: dict[str, Any]) -> tuple[str, str, str, str]:
    if not binary_available or not config_present:
        return (
            "block",
            "binary or config missing",
            "binary/config missing",
            "Install/configure Claude CLI and rerun health check",
        )
    if metrics["unrecovered_auth_errors_24h"] >= 1 or metrics["unrecovered_auth_errors_14d"] >= 2:
        return (
            "block",
            f"unrecovered auth errors exceed threshold (24h={metrics['unrecovered_auth_errors_24h']}, 14d={metrics['unrecovered_auth_errors_14d']})",
            "authentication currently unrecovered",
            "Run `claude login` in a plain terminal (not inside Claude Code), start and exit one clean `claude` session, then rerun `bash scripts/maintenance/ai-tools-status.sh`.",
        )
    if metrics["recent_auth_errors_24h"] >= 1 or metrics["recent_auth_errors_14d"] >= 1:
        return (
            "warn",
            f"recent auth failures detected but recovered (raw24h={metrics['recent_auth_errors_24h']}, raw14d={metrics['recent_auth_errors_14d']}, recovered14d={metrics['recovered_auth_errors_14d']})",
            "recent recovered auth drift",
            "If Claude fails again, run `claude login` in a plain terminal, confirm one clean `claude` session, then rerun `bash scripts/maintenance/ai-tools-status.sh`.",
        )
    return ("ok", "healthy", "none", "No action needed")


def codex_status(binary_available: bool, config_present: bool, log_metrics: dict[str, Any], live_metrics: dict[str, Any]) -> tuple[str, str, str, str]:
    if not binary_available or not config_present:
        return (
            "block",
            "binary or config missing",
            "binary/config missing",
            "Install/configure Codex CLI and rerun health check",
        )
    if live_metrics["skills_tree_dirs_current"] >= 2000:
        return (
            "block",
            f"live skill tree exceeds Codex scan cap ({live_metrics['skills_tree_dirs_current']} dirs)",
            "skill tree too large",
            "Keep archived skills out of .claude/skills and rerun health check",
        )
    if live_metrics["oversize_skill_names_current"] > 0:
        return (
            "block",
            f"current skill names exceed Codex length limit ({live_metrics['oversize_skill_names_current']})",
            "oversize skill names present",
            "Shorten current skill name fields to <=64 chars",
        )
    if log_metrics["skill_load_errors_7d"] >= 1:
        return (
            "warn",
            f"recent Codex skill-load errors in last 7d ({log_metrics['skill_load_errors_7d']})",
            "recent skill-load instability",
            "Confirm a clean Codex session now that live blockers are removed",
        )
    if (
        log_metrics["plugin_manager_warnings_30d"] >= 25
        or log_metrics["plugin_manifest_warnings_30d"] >= 10
        or log_metrics["shell_snapshot_warnings_30d"] >= 10
    ):
        return (
            "warn",
            "plugin/snapshot warnings detected",
            f"plugin_manager={log_metrics['plugin_manager_warnings_30d']}, plugin_manifest={log_metrics['plugin_manifest_warnings_30d']}",
            "Review Codex plugin cache noise; no active live skill blockers remain",
        )
    return ("ok", "healthy", "none", "No action needed")


def gemini_status(binary_available: bool, config_present: bool, node_compatible: bool, metrics: dict[str, Any]) -> tuple[str, str, str, str]:
    if not binary_available or not config_present or not node_compatible:
        return (
            "block",
            "binary/config missing or node<20",
            "runtime prerequisite failure",
            "Install/configure Gemini CLI and ensure Node >= 20",
        )
    if (
        metrics["chat_errors_7d"] >= 2
        or metrics["chat_errors_30d"] >= 4
        or (metrics["chat_errors_30d"] >= 2 and metrics["workspace_roots_30d"] > 15)
    ):
        return (
            "block",
            "recent runtime failures exceed threshold",
            f"chat_errors_7d={metrics['chat_errors_7d']}, chat_errors_30d={metrics['chat_errors_30d']}",
            "Stabilize Gemini runtime before automated routing",
        )
    if (
        metrics["chat_errors_7d"] >= 1
        or metrics["temp_workspace_roots_30d"] >= 1
        or metrics["orphan_temp_workspace_roots_30d"] >= 1
        or metrics["workspace_roots_30d"] >= 7
        or metrics["stale_workspace_roots_7d"] > 6
    ):
        return (
            "warn",
            f"recent Gemini hygiene/runtime warnings (chat7d={metrics['chat_errors_7d']}, roots30d={metrics['workspace_roots_30d']})",
            f"temp_roots={metrics['temp_workspace_roots_30d']}, stale_roots_7d={metrics['stale_workspace_roots_7d']}",
            "Clear temp/orphan Gemini workspaces and confirm a clean Gemini run after the last error",
        )
    return ("ok", "healthy", "none", "No action needed")


def local_provider_health() -> dict[str, Any]:
    node_raw = run_version(["node", "--version"])
    node_semver = extract_semver(node_raw)
    node_major = int(node_semver.split(".")[0]) if node_semver else None

    claude_raw = run_version(["claude", "--version"])
    codex_raw = run_version(["codex", "--version"])
    gemini_raw = run_version(["gemini", "--version"])

    claude_metrics = count_claude_auth_errors()
    codex_log_metrics = analyze_codex_logs()
    codex_live_metrics = analyze_codex_live_skills()
    gemini_metrics = analyze_gemini()

    providers: dict[str, dict[str, Any]] = {}

    claude_bin = claude_raw is not None
    claude_cfg = (HOME / ".claude/settings.json").exists()
    status, note, signal, remediation = claude_status(claude_bin, claude_cfg, claude_metrics)
    providers["claude"] = {
        "binary_available": claude_bin,
        "version_raw": claude_raw,
        "version": extract_semver(claude_raw),
        "config_present": claude_cfg,
        **claude_metrics,
        "status": status,
        "routing_state": routing_state(status),
        "severity_reason": signal,
        "note": note,
        "remediation": remediation,
    }

    codex_bin = codex_raw is not None
    codex_cfg = (REPO_ROOT / ".codex/config.toml").exists() or (HOME / ".codex/config.toml").exists()
    status, note, signal, remediation = codex_status(codex_bin, codex_cfg, codex_log_metrics, codex_live_metrics)
    providers["codex"] = {
        "binary_available": codex_bin,
        "version_raw": codex_raw,
        "version": extract_semver(codex_raw),
        "config_present": codex_cfg,
        **codex_log_metrics,
        **codex_live_metrics,
        "status": status,
        "routing_state": routing_state(status),
        "severity_reason": signal,
        "note": note,
        "remediation": remediation,
    }

    gemini_bin = gemini_raw is not None
    gemini_cfg = (HOME / ".gemini/settings.json").exists()
    node_compatible = bool(node_major and node_major >= 20)
    status, note, signal, remediation = gemini_status(gemini_bin, gemini_cfg, node_compatible, gemini_metrics)
    providers["gemini"] = {
        "binary_available": gemini_bin,
        "version_raw": gemini_raw,
        "version": extract_semver(gemini_raw),
        "config_present": gemini_cfg,
        "node_raw": node_raw,
        "node_version": node_semver,
        "node_compatible": node_compatible,
        **gemini_metrics,
        "status": status,
        "routing_state": routing_state(status),
        "severity_reason": signal,
        "note": note,
        "remediation": remediation,
    }

    overall_status = choose_status(*(provider["status"] for provider in providers.values()))
    return {
        "last_updated": iso_now(),
        "machine": "dev-primary",
        "overall_status": overall_status,
        "overall_routing_state": routing_state(overall_status),
        "providers": providers,
    }


def yaml_scalar(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace('"', '\\"')
    return f'"{text}"'


def dump_yaml(data: Any, indent: int = 0) -> list[str]:
    pad = " " * indent
    lines: list[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{pad}{key}:")
                lines.extend(dump_yaml(value, indent + 2))
            else:
                lines.append(f"{pad}{key}: {yaml_scalar(value)}")
    elif isinstance(data, list):
        if not data:
            lines.append(f"{pad}[]")
        else:
            for item in data:
                if isinstance(item, (dict, list)):
                    lines.append(f"{pad}-")
                    lines.extend(dump_yaml(item, indent + 2))
                else:
                    lines.append(f"{pad}- {yaml_scalar(item)}")
    return lines


def main() -> None:
    report = local_provider_health()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    content = ["# Auto-generated by scripts/maintenance/provider-health-check.py"]
    content.extend(dump_yaml(report))
    OUTPUT.write_text("\n".join(content) + "\n", encoding="utf-8")
    print(str(OUTPUT))


if __name__ == "__main__":
    main()
