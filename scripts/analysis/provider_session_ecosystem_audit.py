#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.bash_command_prefixes import cleanup_bash_command, normalize_command_to_prefix
from workspace_hub.workstations.resolver import WorkstationPathResolver
LOGS_ROOT = REPO_ROOT / "logs" / "orchestrator"
CLAUDE_PRECOMPUTED = REPO_ROOT / "analysis" / "claude-session-ecosystem-audit-2026-04-09.json"
DEFAULT_MARKDOWN = REPO_ROOT / "docs" / "reports" / "provider-session-ecosystem-audit.md"
DEFAULT_JSON = REPO_ROOT / "analysis" / "provider-session-ecosystem-audit.json"

PROVIDERS = ("claude", "codex", "hermes", "gemini")
CODEX_SPACED_CMD_RE = re.compile(r"\s+")
PROMPT_RE = re.compile(r"prompt", re.IGNORECASE)
SYMBOLIC_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")
SYMBOLIC_SLASH_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)+$")
TILDE_PATH_RE = re.compile(r"^(~|~/)")
GITHUB_URI_RE = re.compile(r"^github://", re.IGNORECASE)
WORKSTATION_RESOLVER = WorkstationPathResolver.for_repo(REPO_ROOT)
KNOWN_REPO_NAMES = {
    str(repo_name)
    for machine in WORKSTATION_RESOLVER._machines.values()
    for repo_name in (machine.raw.get("repos", []) or [])
    if str(repo_name).strip()
}
NON_REPO_ARTIFACT_EXACT_PATHS = {"build.js", "vercel.json", "package.json"}
NON_REPO_ARTIFACT_PREFIXES = (
    "content/demos/",
    "content/partials/",
    "examples/demos/gtm/output/",
)

LEGACY_REMEDIATION_RULES = [
    {
        "rule_id": "legacy_work_queue_transition",
        "patterns": [
            "scripts/work-queue/verify-gate-evidence.py",
            "scripts/work-queue/start_stage.py",
            "scripts/work-queue/exit_stage.py",
            "scripts/work-queue/verify_checklist.py",
            "scripts/work-queue/stage_exit_checks.py",
            ".claude/hooks/enforce-active-stage.sh",
        ],
        "canonical_targets": [
            "docs/governance/SESSION-GOVERNANCE.md",
            "docs/governance/TRUST-ARCHITECTURE.md",
            "scripts/workflow/governance-checkpoints.yaml",
            ".claude/hooks/plan-approval-gate.sh",
            ".claude/hooks/session-governor-check.sh",
            "scripts/review/cross-review.sh",
        ],
        "guidance": "Legacy stage-transition tooling was removed during workflow migration; redirect callers to governance docs/hooks instead of recreating the old executables.",
        "reference_doc": "docs/ops/legacy-claude-reference-map.md",
    },
    {
        "rule_id": "legacy_work_queue_html_review",
        "patterns": ["scripts/work-queue/generate-html-review.py"],
        "canonical_targets": [
            "scripts/review/cross-review.sh",
            "templates/review-standard.html",
            "docs/work-queue-workflow.md",
        ],
        "guidance": "Historical HTML review generation is no longer canonical; use the current cross-review workflow and stored review evidence instead.",
        "reference_doc": "docs/ops/legacy-claude-reference-map.md",
    },
    {
        "rule_id": "legacy_work_queue_lifecycle",
        "patterns": [
            "scripts/work-queue/close-item.sh",
            "scripts/work-queue/whats-next.sh",
            "scripts/work-queue/archive-item.sh",
            "scripts/work-queue/claim-item.sh",
            ".claude/work-queue/scripts/generate-index.py",
        ],
        "canonical_targets": [
            "scripts/refresh-agent-work-queue.py",
            "scripts/refresh-agent-work-queue.sh",
            "notes/agent-work-queue.md",
            ".planning/",
            "GitHub issues",
        ],
        "guidance": "The repo no longer uses local queue scripts as the source of truth; prefer GitHub issue updates plus .planning evidence.",
        "reference_doc": "docs/ops/legacy-claude-reference-map.md",
    },
    {
        "rule_id": "legacy_work_queue_skills",
        "patterns": [
            ".claude/skills/workspace-hub/work-queue-workflow/SKILL.md",
            ".claude/skills/coordination/workspace/work-queue/SKILL.md",
            ".claude/skills/workspace-hub/workflow-gatepass/SKILL.md",
        ],
        "canonical_targets": [
            "AGENTS.md",
            ".claude/commands/gsd/*",
            ".gemini/get-shit-done/workflows/*",
            "docs/work-queue-workflow.md",
        ],
        "guidance": "The old work-queue skill tree was replaced by GSD-oriented command/workflow surfaces; redirect readers instead of restoring deleted skill files.",
        "reference_doc": "docs/ops/legacy-claude-reference-map.md",
    },
    {
        "rule_id": "legacy_agent_wrapper_tree",
        "patterns": ["scripts/agents/"],
        "canonical_targets": [
            "AGENTS.md",
            "docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md",
            "docs/work-queue-workflow.md",
            "scripts/review/cross-review.sh",
            "scripts/planning/ensemble-plan.sh",
        ],
        "guidance": "The old scripts/agents wrapper tree is gone; use the current policy-first workflow and current review/planning surfaces instead.",
        "reference_doc": "docs/ops/legacy-claude-reference-map.md",
    },
    {
        "rule_id": "legacy_local_work_queue_items",
        "patterns": [".claude/work-queue/"],
        "canonical_targets": [
            "GitHub issues",
            ".planning/",
            "notes/agent-work-queue.md",
            "docs/work-queue-workflow.md",
        ],
        "guidance": "Local queue item files are compatibility surfaces, not canonical work tracking; prefer the GitHub issue and .planning artifact instead.",
        "reference_doc": "docs/ops/legacy-claude-reference-map.md",
    },
]


def match_remediation_rule(path: str) -> dict | None:
    for rule in LEGACY_REMEDIATION_RULES:
        for pattern in rule["patterns"]:
            if path == pattern or path.startswith(pattern):
                return rule
    return None


def build_missing_read_remediation_hints(rows: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for row in rows:
        path = str(row.get("path", "") or "")
        count = int(row.get("count", 0) or 0)
        rule = match_remediation_rule(path)
        if not rule:
            continue
        hint = grouped.setdefault(
            rule["rule_id"],
            {
                "rule_id": rule["rule_id"],
                "total_count": 0,
                "matched_paths": [],
                "canonical_targets": rule["canonical_targets"],
                "guidance": rule["guidance"],
                "reference_doc": rule["reference_doc"],
            },
        )
        hint["total_count"] += count
        hint["matched_paths"].append({"path": path, "count": count})

    hints = list(grouped.values())
    hints.sort(key=lambda item: item["total_count"], reverse=True)
    for hint in hints:
        hint["matched_paths"].sort(key=lambda item: item["count"], reverse=True)
    return hints


def safe_exists(path: Path) -> bool:
    try:
        return path.exists()
    except (OSError, PermissionError):
        return False


def normalize_cmd(provider: str, raw_cmd: str | None) -> str:
    text = str(raw_cmd or "")
    if provider == "codex":
        stripped = text.strip()
        tokens = [token for token in stripped.split(" ") if token]
        single_char_tokens = sum(1 for token in tokens if len(token) == 1)
        looks_spaced_encoded = bool(tokens) and single_char_tokens / len(tokens) >= 0.6
        if not looks_spaced_encoded:
            return stripped
        decoded_parts: list[str] = []
        space_run = 0
        for ch in text:
            if ch == " ":
                space_run += 1
                continue
            if space_run >= 3:
                decoded_parts.append(" ")
            space_run = 0
            decoded_parts.append(ch)
        if space_run >= 3:
            decoded_parts.append(" ")
        return "".join(decoded_parts).strip()
    return text


def normalize_repo_alias(text: str, repo_root: Path) -> str:
    return WORKSTATION_RESOLVER.rewrite_workspace_path(text, current_repo_root=repo_root)


def is_non_repo_artifact_path(text: str) -> bool:
    """Return true for attested generated-site/adjacent-project paths.

    These paths are repo-relative strings observed in provider logs, but they are
    not actionable workspace-hub stale-path debt and should not inflate missing
    repo read counts.
    """
    return text in NON_REPO_ARTIFACT_EXACT_PATHS or any(
        text.startswith(prefix) for prefix in NON_REPO_ARTIFACT_PREFIXES
    )


def classify_repo_relative_target(text: str, repo_root: Path) -> tuple[str, str, bool]:
    candidate = repo_root / text
    first_component = text.split("/", 1)[0]
    if first_component in KNOWN_REPO_NAMES and first_component != repo_root.name and not safe_exists(candidate):
        return text, "sibling_repo", False
    if is_non_repo_artifact_path(text) and not safe_exists(candidate):
        return text, "non_repo_artifact", False
    return text, "repo", safe_exists(candidate)


def classify_read_target(raw_path: str | None, repo_root: Path, record: dict | None = None) -> tuple[str, str, bool]:
    if raw_path is None:
        return "", "blank", False

    text = str(raw_path).strip()
    if not text:
        return "", "blank", False

    provider_tool = str((record or {}).get("hermes_tool", "") or "")
    if provider_tool in {"skill_view", "session_search"}:
        return text, "symbolic", False

    text = normalize_repo_alias(text, repo_root)

    if GITHUB_URI_RE.match(text):
        return text, "symbolic", False

    if TILDE_PATH_RE.match(text):
        expanded = Path(text).expanduser()
        return expanded.as_posix(), "external", safe_exists(expanded)

    if "/" not in text and "\\" not in text and not text.startswith("~"):
        if SYMBOLIC_NAME_RE.fullmatch(text):
            return text, "symbolic", False

    if SYMBOLIC_SLASH_NAME_RE.fullmatch(text):
        first_component = text.split("/", 1)[0]
        candidate = repo_root / text
        if not text.startswith(".") and not safe_exists(repo_root / first_component) and not safe_exists(candidate):
            return text, "symbolic", False

    path = Path(text)
    if path.is_absolute():
        try:
            rel = path.relative_to(repo_root)
            return rel.as_posix(), "repo", safe_exists(path)
        except ValueError:
            return text, "external", safe_exists(path)

    return classify_repo_relative_target(text, repo_root)


def iter_post_records(logs_dir: Path) -> Iterable[dict]:
    for log_path in sorted(logs_dir.glob("session_*.jsonl")):
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("hook") == "post":
                record["_session_file"] = log_path.name
                yield record


def parse_record_timestamp(record: dict) -> float | None:
    epoch = record.get("epoch")
    if epoch is not None:
        try:
            return float(epoch)
        except (TypeError, ValueError):
            return None

    raw_ts = str(record.get("ts", "") or "")
    if not raw_ts:
        return None
    try:
        return datetime.fromisoformat(raw_ts.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def top_items(counter: Counter, limit: int, key_name: str) -> list[dict]:
    return [{key_name: key, "count": value} for key, value in counter.most_common(limit)]


def compute_activity_window(
    provider: str,
    logs_dir: Path,
    repo_root: Path,
    *,
    start_ts: float,
    end_ts: float | None = None,
) -> dict:
    post_records = 0
    session_ids: Counter[str] = Counter()
    tool_counts: Counter[str] = Counter()
    missing_repo_reads: Counter[str] = Counter()
    sibling_repo_reads: Counter[str] = Counter()
    non_repo_artifact_reads: Counter[str] = Counter()
    recent_reads: Counter[str] = Counter()
    recent_writes: Counter[str] = Counter()
    recent_edits: Counter[str] = Counter()
    bash_family_counts: Counter[str] = Counter()

    for record in iter_post_records(logs_dir):
        record_ts = parse_record_timestamp(record)
        if record_ts is None or record_ts <= start_ts:
            continue
        if end_ts is not None and record_ts > end_ts:
            continue

        post_records += 1
        session_id = str(record.get("session_id", "") or "")
        if session_id:
            session_ids[session_id] += 1

        tool = str(record.get("tool", "unknown"))
        tool_counts[tool] += 1

        if tool == "Bash":
            cmd = normalize_cmd(provider, record.get("cmd"))
            prefix = normalize_command_to_prefix(cmd, cleanup=True)
            if prefix:
                bash_family_counts[prefix] += 1

        file_target = record.get("file")
        if tool == "Read":
            normalized, scope, exists = classify_read_target(file_target, repo_root, record)
            if normalized:
                recent_reads[normalized] += 1
            if scope == "repo" and not exists:
                missing_repo_reads[normalized] += 1
            elif scope == "sibling_repo":
                sibling_repo_reads[normalized] += 1
            elif scope == "non_repo_artifact":
                non_repo_artifact_reads[normalized] += 1
        elif tool == "Write" and file_target:
            recent_writes[str(file_target)] += 1
        elif tool == "Edit" and file_target:
            recent_edits[str(file_target)] += 1

    return {
        "post_records": post_records,
        "sessions": len(session_ids),
        "top_tools": top_items(tool_counts, 5, "tool"),
        "top_missing_repo_reads": top_items(missing_repo_reads, 5, "path"),
        "top_sibling_repo_reads": top_items(sibling_repo_reads, 5, "path"),
        "top_non_repo_artifact_reads": top_items(non_repo_artifact_reads, 5, "path"),
        "non_repo_artifact_read_total": sum(non_repo_artifact_reads.values()),
        "top_reads": top_items(recent_reads, 5, "path"),
        "top_writes": top_items(recent_writes, 5, "path"),
        "top_edits": top_items(recent_edits, 5, "path"),
        "top_bash_command_families": [
            {"prefix": prefix, "count": count}
            for prefix, count in bash_family_counts.most_common(8)
        ],
    }


def compute_recent_activity_since(provider: str, logs_dir: Path, repo_root: Path, cutoff_ts: float) -> dict:
    return compute_activity_window(provider, logs_dir, repo_root, start_ts=cutoff_ts)


def summarize_raw_provider(provider: str, logs_dir: Path, repo_root: Path) -> dict:
    sessions = sorted(logs_dir.glob("session_*.jsonl"))
    corrections_dir = logs_dir / "corrections"
    correction_sessions = sorted(corrections_dir.glob("session_*.jsonl")) if corrections_dir.exists() else []

    post_records = 0
    tool_counts: Counter[str] = Counter()
    repo_counts: Counter[str] = Counter()
    read_counts: Counter[str] = Counter()
    missing_repo_reads: Counter[str] = Counter()
    sibling_repo_reads: Counter[str] = Counter()
    non_repo_artifact_reads: Counter[str] = Counter()
    missing_external_reads: Counter[str] = Counter()
    symbolic_reads: Counter[str] = Counter()
    blank_reads = 0
    session_ids: Counter[str] = Counter()
    special_counts: Counter[str] = Counter()
    python3_bash_calls = 0
    uv_python_bash_calls = 0
    prompt_reads = 0
    bash_family_counts: Counter[str] = Counter()
    bash_family_examples: dict[str, str] = {}

    for record in iter_post_records(logs_dir):
        post_records += 1
        tool = str(record.get("tool", "unknown"))
        tool_counts[tool] += 1
        repo_counts[str(record.get("repo", "unknown"))] += 1

        session_id = str(record.get("session_id", "") or "")
        if session_id:
            session_ids[session_id] += 1

        cmd = normalize_cmd(provider, record.get("cmd"))
        if tool == "Bash" and "python3" in cmd:
            python3_bash_calls += 1
        if tool == "Bash" and "uvrun" in cmd.replace(" ", "") and "python" in cmd.replace(" ", ""):
            uv_python_bash_calls += 1
        if tool == "Bash" and cmd.strip():
            prefix = normalize_command_to_prefix(cmd, cleanup=True)
            if prefix:
                bash_family_counts[prefix] += 1
                bash_family_examples.setdefault(prefix, cmd)

        if provider == "codex":
            codex_tool = str(record.get("codex_tool", "") or "")
            if codex_tool:
                special_counts[codex_tool] += 1
        else:
            memory_action = str(record.get("memory_action", "") or "")
            skill_action = str(record.get("skill_action", "") or "")
            if memory_action:
                special_counts[f"memory_{memory_action}"] += 1
            if skill_action:
                special_counts[f"skill_{skill_action}"] += 1

        if tool != "Read":
            continue

        normalized, scope, exists = classify_read_target(record.get("file"), repo_root, record)
        if PROMPT_RE.search(normalized):
            prompt_reads += 1
        if scope == "blank":
            blank_reads += 1
            continue
        if scope == "symbolic":
            symbolic_reads[normalized] += 1
            continue

        read_counts[normalized] += 1
        if exists:
            continue
        if scope == "repo":
            missing_repo_reads[normalized] += 1
        elif scope == "sibling_repo":
            sibling_repo_reads[normalized] += 1
        elif scope == "non_repo_artifact":
            non_repo_artifact_reads[normalized] += 1
        elif scope == "external":
            missing_external_reads[normalized] += 1

    top_missing_repo_reads = top_items(missing_repo_reads, 10, "path")
    summary = {
        "source": "raw_logs",
        "sessions": len(sessions),
        "correction_sessions": len(correction_sessions),
        "unique_runtime_sessions": len(session_ids),
        "post_records": post_records,
        "prompt_reads": prompt_reads,
        "blank_reads": blank_reads,
        "missing_repo_reads": sum(missing_repo_reads.values()),
        "python3_bash_calls": python3_bash_calls,
        "uv_python_bash_calls": uv_python_bash_calls,
        "top_tools": top_items(tool_counts, 8, "tool"),
        "top_repos": top_items(repo_counts, 8, "repo"),
        "top_reads": top_items(read_counts, 10, "path"),
        "top_missing_repo_reads": top_missing_repo_reads,
        "top_sibling_repo_reads": top_items(sibling_repo_reads, 10, "path"),
        "sibling_repo_read_total": sum(sibling_repo_reads.values()),
        "top_non_repo_artifact_reads": top_items(non_repo_artifact_reads, 10, "path"),
        "non_repo_artifact_read_total": sum(non_repo_artifact_reads.values()),
        "missing_repo_read_remediation_hints": build_missing_read_remediation_hints(top_missing_repo_reads),
        "top_missing_external_reads": top_items(missing_external_reads, 10, "path"),
        "top_symbolic_reads": top_items(symbolic_reads, 10, "name"),
        "top_bash_command_families": [
            {
                "prefix": prefix,
                "count": count,
                "share_of_bash_calls": round((count / tool_counts.get("Bash", 1)) * 100, 2),
                "example_command": bash_family_examples[prefix],
            }
            for prefix, count in bash_family_counts.most_common(8)
        ],
        "special_counts": dict(special_counts),
    }
    if provider == "claude" and not session_ids:
        summary["limitations"] = [
            "Claude raw orchestrator logs do not persist session_id, so unique runtime sessions are unavailable in this audit."
        ]
    if post_records:
        summary["python3_per_1k_records"] = round(python3_bash_calls * 1000 / post_records, 2)
        summary["uv_python_per_1k_records"] = round(uv_python_bash_calls * 1000 / post_records, 2)
    return summary


def summarize_claude_precomputed(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    top_missing_repo_reads = payload.get("top_missing_repo_reads", [])
    summary = {
        "source": "precomputed_report",
        "sessions": payload.get("sessions_analyzed", 0),
        "post_records": payload.get("post_records", 0),
        "prompt_reads": payload.get("prompt_read_total", 0),
        "python3_bash_calls": payload.get("python3_bash_calls", 0),
        "uv_python_bash_calls": payload.get("uv_python_bash_calls", 0),
        "missing_repo_reads": payload.get("missing_repo_read_total", 0),
        "missing_external_reads": payload.get("missing_external_read_total", 0),
        "top_tools": payload.get("tool_distribution", []),
        "top_repos": payload.get("repo_distribution", []),
        "top_reads": payload.get("top_reads", []),
        "top_missing_repo_reads": top_missing_repo_reads,
        "missing_repo_read_remediation_hints": build_missing_read_remediation_hints(top_missing_repo_reads),
        "top_missing_external_reads": payload.get("top_missing_external_reads", []),
        "limitations": [
            "Claude raw orchestrator logs are not present in this checkout; summary comes from the saved 2026-04-09 audit artifact.",
            "Symbolic read targets cannot be reclassified without the original raw log corpus.",
        ],
    }
    post_records = summary["post_records"] or 0
    if post_records:
        summary["python3_per_1k_records"] = round(summary["python3_bash_calls"] * 1000 / post_records, 2)
        summary["uv_python_per_1k_records"] = round(summary["uv_python_bash_calls"] * 1000 / post_records, 2)
    return summary


def build_migration_debt_summary(provider_summaries: dict[str, dict]) -> dict:
    ranked: list[dict] = []
    for provider, summary in provider_summaries.items():
        hints = summary.get("missing_repo_read_remediation_hints", [])
        known_reads = sum(int(hint.get("total_count", 0) or 0) for hint in hints)
        post_records = int(summary.get("post_records", 0) or 0)
        density = round(known_reads * 1000 / post_records, 2) if post_records else 0.0
        top_hint = hints[0] if hints else {}
        top_reads = int(top_hint.get("total_count", 0) or 0)
        top_share = round(top_reads * 100 / known_reads, 2) if known_reads else 0.0
        ranked.append(
            {
                "provider": provider,
                "known_migration_debt_reads": known_reads,
                "known_migration_debt_per_1k_records": density,
                "known_migration_debt_rule_count": len(hints),
                "top_migration_rule_id": top_hint.get("rule_id"),
                "top_migration_rule_reads": top_reads,
                "top_migration_rule_share_pct": top_share,
                "migration_debt_status": (
                    "none" if known_reads == 0 else "concentrated" if top_share >= 40 else "mixed"
                ),
                "scope_note": "Based on remediation-mapped stale reads from top missing repo reads.",
            }
        )
    ranked.sort(
        key=lambda item: (
            -item["known_migration_debt_per_1k_records"],
            -item["known_migration_debt_reads"],
            -item["top_migration_rule_reads"],
            item["provider"],
        )
    )
    for idx, item in enumerate(ranked, start=1):
        item["migration_debt_rank"] = idx
    return {
        "ranked_providers": ranked,
        "highest_density_provider": ranked[0]["provider"] if ranked else None,
        "highest_volume_provider": max(ranked, key=lambda item: item["known_migration_debt_reads"])["provider"] if ranked else None,
        "scope_note": "Migration-debt figures are based on remediation-mapped entries from each provider's top missing repo reads.",
    }


def load_previous_generated_at(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    generated_at = payload.get("generated_at")
    return str(generated_at) if generated_at else None


def load_previous_audit(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def load_github_issue_index(repo_root: Path, limit: int = 500) -> list[dict]:
    command = ["gh", "issue", "list", "--state", "all", "--limit", str(limit), "--json", "number,title,state,url"]
    try:
        result = subprocess.run(
            command,
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    try:
        payload = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return []
    issues: list[dict] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        issues.append(
            {
                "number": item.get("number"),
                "title": title,
                "state": str(item.get("state", "")).upper() or None,
                "url": item.get("url"),
            }
        )
    return issues


def compute_activity_status(recent_post: int, recent_sessions: int, recent_status: str) -> str:
    if recent_post >= 100 or recent_sessions >= 3:
        return "active"
    if recent_post > 0 or recent_sessions > 0:
        return "quiet"
    if recent_status == "ok":
        return "idle"
    return "unavailable"


def compute_python_hygiene_status(python3_rate: float, uv_rate: float) -> str:
    if python3_rate == 0 and uv_rate == 0:
        return "no_python_usage"
    if uv_rate >= 2 * python3_rate:
        return "uv_preferred"
    if uv_rate < 0.5 * python3_rate:
        return "python3_heavy"
    return "mixed"


def compare_direction(current: float | None, previous: float | None, *, better_when_lower: bool, tolerance: float = 0.01) -> str:
    if current is None or previous is None:
        return "unavailable"
    delta = current - previous
    if abs(delta) <= tolerance:
        return "stable"
    if better_when_lower:
        return "improving" if delta < 0 else "worsening"
    return "improving" if delta > 0 else "worsening"


def compare_activity_direction(current_status: str, previous_status: str) -> str:
    rank = {"unavailable": -1, "idle": 0, "quiet": 1, "active": 2}
    if current_status not in rank or previous_status not in rank:
        return "unavailable"
    if current_status == "unavailable" or previous_status == "unavailable":
        return "unavailable"
    delta = rank[current_status] - rank[previous_status]
    if delta == 0:
        return "stable"
    return "increasing" if delta > 0 else "decreasing"


def summarize_urgency_rank_movement(
    row: dict,
    previous_rank: int | None,
    previous_score: float | None,
) -> tuple[str, int | None, float | None, str]:
    current_rank = int(row.get("urgency_rank", 0) or 0)
    current_score = float(row.get("urgency_score", 0) or 0)
    score_delta = round(current_score - previous_score, 2) if previous_score is not None else None

    if previous_rank is None:
        return ("new", None, score_delta, "new to ranked urgency summary since the previous audit")

    rank_delta = previous_rank - current_rank
    if rank_delta > 0:
        direction = "up"
    elif rank_delta < 0:
        direction = "down"
    else:
        direction = "stable"

    reason_bits: list[str] = []
    activity_trend = str(row.get("activity_trend", ""))
    if activity_trend == "increasing":
        reason_bits.append("recent activity increased")
    elif activity_trend == "decreasing":
        reason_bits.append("recent activity cooled")

    debt_trend = str(row.get("debt_trend", ""))
    if debt_trend == "worsening":
        reason_bits.append("migration debt worsened")
    elif debt_trend == "improving":
        reason_bits.append("migration debt improved")

    drift_trend = str(row.get("drift_trend", ""))
    if drift_trend == "worsening":
        reason_bits.append("path drift worsened")
    elif drift_trend == "improving":
        reason_bits.append("path drift improved")

    python_trend = str(row.get("python_hygiene_trend", ""))
    if python_trend == "worsening":
        reason_bits.append("python hygiene worsened")
    elif python_trend == "improving":
        reason_bits.append("python hygiene improved")

    corpus_status = str(row.get("corpus_status", ""))
    if corpus_status == "corpus_pruned_or_rebuilt":
        reason_bits.append("corpus was pruned or rebuilt")
    elif corpus_status == "positive_corpus_growth_beyond_recent_activity":
        reason_bits.append("corpus grew faster than event-time activity")

    score_clause = (
        f"urgency {current_score:.2f} ({score_delta:+.2f} vs previous audit)"
        if score_delta is not None
        else f"urgency {current_score:.2f}"
    )

    if direction == "stable":
        if not reason_bits:
            return (direction, rank_delta, score_delta, f"rank unchanged at #{current_rank}; {score_clause}")
        return (direction, rank_delta, score_delta, f"rank unchanged at #{current_rank}; {score_clause}; {'; '.join(reason_bits)}")

    movement = f"moved {direction} {abs(rank_delta)} slot"
    if abs(rank_delta) != 1:
        movement += "s"
    movement += f" to #{current_rank}; {score_clause}"
    if reason_bits:
        movement += f"; {'; '.join(reason_bits)}"
    return (direction, rank_delta, score_delta, movement)


def determine_activity_window_profile(last_24h_post_records: int, last_7d_post_records: int) -> str:
    if last_24h_post_records <= 0 and last_7d_post_records <= 0:
        return "dormant"
    if last_24h_post_records > 0 and last_7d_post_records <= last_24h_post_records * 2:
        return "burst_active"
    if last_7d_post_records >= max(200, 4 * max(last_24h_post_records, 1)):
        return "sustained_background"
    return "light_recent"


def summarize_health_status(
    *,
    urgency_tier: str,
    debt_status: str,
    debt_trend: str,
    drift_trend: str,
    python_hygiene_status: str,
    corpus_status: str,
    activity_status: str,
    activity_window_profile: str,
) -> tuple[str, list[str], str]:
    reasons: list[str] = []
    if urgency_tier == "urgent_now":
        reasons.append("urgent action tier")
    if debt_status == "high_debt":
        reasons.append("high migration debt")
    elif debt_status == "moderate_debt":
        reasons.append("moderate migration debt")
    elif debt_status == "drift_only":
        reasons.append("unmapped path drift remains")
    if debt_trend == "worsening":
        reasons.append("migration debt worsening")
    if drift_trend == "worsening":
        reasons.append("path drift worsening")
    if python_hygiene_status == "python3_heavy":
        reasons.append("python3-heavy command hygiene")
    if corpus_status in {"corpus_pruned_or_rebuilt", "positive_corpus_growth_beyond_recent_activity"}:
        reasons.append("corpus anomaly needs interpretation")
    if activity_window_profile == "burst_active":
        reasons.append("24h burst activity")
    elif activity_window_profile == "sustained_background":
        reasons.append("7d sustained activity")
    if activity_status == "active":
        reasons.append("currently active")

    if urgency_tier == "urgent_now" or (
        urgency_tier == "next_up"
        and (
            debt_status == "high_debt"
            or corpus_status in {"corpus_pruned_or_rebuilt", "positive_corpus_growth_beyond_recent_activity"}
            or activity_window_profile in {"burst_active", "sustained_background"}
            or activity_status == "active"
        )
    ):
        health_status = "red"
    elif (
        urgency_tier in {"next_up", "investigate"}
        or debt_status in {"high_debt", "moderate_debt", "drift_only"}
        or drift_trend == "worsening"
        or python_hygiene_status == "python3_heavy"
    ):
        health_status = "yellow"
    else:
        health_status = "green"

    if not reasons:
        reasons.append("no acute anomaly")
    summary = f"{health_status}: " + "; ".join(reasons[:4])
    return health_status, reasons, summary


def build_watchlist(rows: list[dict]) -> list[dict]:
    watchlist: list[dict] = []
    for row in rows:
        provider = str(row.get("provider", ""))
        health_status = str(row.get("health_status", "green"))
        urgency_tier = str(row.get("urgency_tier", "monitor"))
        activity_window_profile = str(row.get("activity_window_profile", "dormant"))
        corpus_status = str(row.get("corpus_status", "aligned"))
        python_hygiene_status = str(row.get("python_hygiene_status", "no_python_usage"))
        primary_issue = str(row.get("primary_issue", "no acute anomaly"))
        recommended_action = str(row.get("recommended_action", "no immediate intervention; monitor next audit"))
        health_summary = str(row.get("health_summary", ""))

        if health_status == "red" and urgency_tier == "urgent_now":
            trigger_level = "page"
            trigger_reason = f"urgent-now provider with {primary_issue}"
            suggested_followup = f"Escalate immediately on {provider}: {recommended_action}"
        elif health_status == "red":
            trigger_level = "act_this_week"
            trigger_reason = f"red health due to {primary_issue}"
            suggested_followup = f"Prioritize this week on {provider}: {recommended_action}"
        elif health_status == "yellow" and activity_window_profile == "sustained_background":
            trigger_level = "investigate"
            trigger_reason = f"yellow health with sustained 7d activity and {primary_issue}"
            suggested_followup = f"Sample current traces on {provider} and verify whether {primary_issue} needs remap or docs cleanup"
        elif health_status == "yellow" and python_hygiene_status == "python3_heavy":
            trigger_level = "investigate"
            trigger_reason = "yellow health driven by python hygiene"
            suggested_followup = f"Audit command hygiene on {provider} and convert python3-heavy paths to uv-oriented usage"
        else:
            trigger_level = "monitor"
            trigger_reason = health_summary or "no acute anomaly"
            suggested_followup = f"Monitor {provider} in the next audit cycle"

        if corpus_status in {"corpus_pruned_or_rebuilt", "positive_corpus_growth_beyond_recent_activity"} and trigger_level != "page":
            trigger_reason += "; corpus anomaly present"

        watchlist.append(
            {
                "provider": provider,
                "trigger_level": trigger_level,
                "trigger_reason": trigger_reason,
                "suggested_followup": suggested_followup,
                "health_status": health_status,
                "urgency_tier": urgency_tier,
                "primary_issue": primary_issue,
            }
        )

    trigger_rank = {"page": 3, "act_this_week": 2, "investigate": 1, "monitor": 0}
    watchlist.sort(
        key=lambda item: (-trigger_rank.get(str(item.get("trigger_level", "monitor")), 0), str(item.get("provider", "")))
    )
    return watchlist


def build_change_alerts(rows: list[dict], watchlist: list[dict], previous_audit: dict | None) -> list[dict]:
    if not previous_audit:
        return []

    previous_interpretation = previous_audit.get("executive_summary", {}).get("provider_interpretation_summary", {})
    previous_rows = previous_interpretation.get("providers", []) if isinstance(previous_interpretation, dict) else []
    previous_by_provider = {
        row.get("provider"): row
        for row in previous_rows
        if isinstance(row, dict) and row.get("provider")
    }
    previous_watchlist = previous_interpretation.get("watchlist", []) if isinstance(previous_interpretation, dict) else []
    previous_watchlist_by_provider = {
        item.get("provider"): item
        for item in previous_watchlist
        if isinstance(item, dict) and item.get("provider")
    }

    current_watchlist_by_provider = {
        item.get("provider"): item
        for item in watchlist
        if isinstance(item, dict) and item.get("provider")
    }

    alerts: list[dict] = []
    trigger_rank = {"page": 3, "act_this_week": 2, "investigate": 1, "monitor": 0}
    health_rank = {"red": 2, "yellow": 1, "green": 0}

    for row in rows:
        provider = str(row.get("provider", ""))
        if not provider:
            continue
        previous_row = previous_by_provider.get(provider, {})
        previous_watch = previous_watchlist_by_provider.get(provider, {})
        current_watch = current_watchlist_by_provider.get(provider, {})

        previous_trigger = str(previous_watch.get("trigger_level", "monitor")) if previous_watch else "monitor"
        current_trigger = str(current_watch.get("trigger_level", "monitor")) if current_watch else "monitor"
        previous_health = str(previous_row.get("health_status", "green")) if previous_row else "green"
        current_health = str(row.get("health_status", "green"))
        previous_rank_value = int(previous_row.get("urgency_rank", 0) or 0) if previous_row else None
        current_rank_value = int(row.get("urgency_rank", 0) or 0)

        change_type = None
        summary = None

        if not previous_watch and current_trigger != "monitor":
            change_type = "new_watchlist_entry"
            summary = f"{provider} entered watchlist at {current_trigger}"
        elif previous_watch and current_trigger == "monitor":
            change_type = "cleared_watchlist"
            summary = f"{provider} cleared watchlist from {previous_trigger}"
        elif trigger_rank.get(current_trigger, 0) > trigger_rank.get(previous_trigger, 0):
            change_type = "trigger_escalated"
            summary = f"{provider} trigger escalated from {previous_trigger} to {current_trigger}"
        elif health_rank.get(current_health, 0) > health_rank.get(previous_health, 0):
            change_type = "health_worsened"
            summary = f"{provider} health worsened from {previous_health} to {current_health}"
        elif previous_rank_value and current_rank_value and current_rank_value < previous_rank_value:
            change_type = "urgency_rank_improved_priority"
            summary = f"{provider} moved up from rank #{previous_rank_value} to #{current_rank_value}"

        if not change_type:
            continue

        alerts.append(
            {
                "provider": provider,
                "change_type": change_type,
                "previous_trigger_level": previous_trigger,
                "current_trigger_level": current_trigger,
                "previous_health_status": previous_health,
                "current_health_status": current_health,
                "previous_urgency_rank": previous_rank_value,
                "current_urgency_rank": current_rank_value,
                "summary": summary,
                "suggested_followup": current_watch.get("suggested_followup") or row.get("recommended_action"),
            }
        )

    change_rank = {
        "trigger_escalated": 4,
        "health_worsened": 3,
        "new_watchlist_entry": 2,
        "urgency_rank_improved_priority": 1,
        "cleared_watchlist": 0,
    }
    alerts.sort(key=lambda item: (-change_rank.get(str(item.get("change_type", "")), 0), str(item.get("provider", ""))))
    return alerts


def build_remediation_playbooks(provider_summaries: dict[str, dict], rows: list[dict], watchlist: list[dict]) -> list[dict]:
    rule_by_id = {rule["rule_id"]: rule for rule in LEGACY_REMEDIATION_RULES}
    playbooks: list[dict] = []
    watchlist_by_provider = {
        item.get("provider"): item
        for item in watchlist
        if isinstance(item, dict) and item.get("provider")
    }

    generic_playbooks = {
        "unmapped path drift": {
            "inspect_paths": ["analysis/provider-session-ecosystem-audit.json", "docs/reports/provider-session-ecosystem-audit.md"],
            "canonical_targets": ["docs/ops/legacy-claude-reference-map.md", "docs/work-queue-workflow.md"],
            "first_steps": [
                "Sample the provider's top missing repo reads from the audit JSON and group them by path family.",
                "Decide whether each path family is a legitimate missing file, a deleted legacy path, or a symbolic/non-file surface that needs remapping.",
                "Update redirect docs/exporter mappings before treating the drift as active repo debt.",
            ],
            "reference_doc": "docs/ops/legacy-claude-reference-map.md",
            "guidance": "Separate benign drift from actionable stale-path debt before opening remediation work.",
            "owner_surface": "docs/ops/legacy-claude-reference-map.md",
            "owner_team": "drift-triage",
            "preferred_fix_lane": "drift-triage",
        },
        "backfill/export growth beyond event-time activity": {
            "inspect_paths": ["analysis/provider-session-ecosystem-audit.json", "scripts/cron/provider-session-ecosystem-audit.sh"],
            "canonical_targets": ["analysis/provider-session-ecosystem-audit.json", "docs/reports/provider-session-ecosystem-audit.md"],
            "first_steps": [
                "Compare recent event-time activity with corpus delta for the affected provider.",
                "Check whether exporter rebuilds, backfills, or state resets explain the gap.",
                "Avoid using trend deltas for operational decisions until the corpus anomaly is explained.",
            ],
            "reference_doc": "docs/reports/provider-session-ecosystem-audit.md",
            "guidance": "Corpus growth beyond event-time activity usually means backfill or export-behavior drift, not new live work.",
            "owner_surface": "scripts/cron/provider-session-ecosystem-audit.sh",
            "owner_team": "exporter-maintainers",
            "preferred_fix_lane": "exporter-schema",
        },
        "corpus prune/rebuild drift": {
            "inspect_paths": ["analysis/provider-session-ecosystem-audit.json", "scripts/cron/provider-session-ecosystem-audit.sh"],
            "canonical_targets": ["analysis/provider-session-ecosystem-audit.json", "docs/reports/provider-session-ecosystem-audit.md"],
            "first_steps": [
                "Check whether export state, pruning, or corpus rebuild logic changed since the previous audit.",
                "Confirm the event-time recent activity still matches the raw logs before escalating provider behavior changes.",
                "Only treat the provider as operationally quieter after ruling out export resets or pruning.",
            ],
            "reference_doc": "docs/reports/provider-session-ecosystem-audit.md",
            "guidance": "Pruned/rebuilt corpus snapshots can make provider urgency appear to move without real workflow changes.",
            "owner_surface": "scripts/cron/provider-session-ecosystem-audit.sh",
            "owner_team": "exporter-maintainers",
            "preferred_fix_lane": "exporter-schema",
        },
        "no acute anomaly": {
            "inspect_paths": ["docs/reports/provider-session-ecosystem-audit.md"],
            "canonical_targets": ["analysis/provider-session-ecosystem-audit.json"],
            "first_steps": [
                "No immediate remediation needed.",
                "Recheck the provider on the next audit run.",
                "Escalate only if health, watchlist trigger, or change alerts worsen.",
            ],
            "reference_doc": "docs/reports/provider-session-ecosystem-audit.md",
            "guidance": "Use monitoring rather than intervention when no acute anomaly is present.",
            "owner_surface": "docs/reports/provider-session-ecosystem-audit.md",
            "owner_team": "audit-operators",
            "preferred_fix_lane": "monitoring",
        },
    }

    lane_by_issue = {
        "legacy_work_queue_transition": ("docs/governance/SESSION-GOVERNANCE.md", "governance-maintainers", "governance-docs"),
        "legacy_work_queue_html_review": ("scripts/review/cross-review.sh", "review-workflow-maintainers", "review-workflow"),
        "legacy_work_queue_lifecycle": ("notes/agent-work-queue.md", "planning-ops", "planning-workflow"),
        "legacy_work_queue_skills": ("docs/work-queue-workflow.md", "prompt-maintainers", "prompt-adapter"),
        "legacy_agent_wrapper_tree": ("AGENTS.md", "prompt-maintainers", "prompt-adapter"),
        "legacy_local_work_queue_items": ("notes/agent-work-queue.md", "planning-ops", "planning-workflow"),
        "unmapped path drift": ("docs/ops/legacy-claude-reference-map.md", "drift-triage", "drift-triage"),
        "backfill/export growth beyond event-time activity": ("scripts/cron/provider-session-ecosystem-audit.sh", "exporter-maintainers", "exporter-schema"),
        "corpus prune/rebuild drift": ("scripts/cron/provider-session-ecosystem-audit.sh", "exporter-maintainers", "exporter-schema"),
        "no acute anomaly": ("docs/reports/provider-session-ecosystem-audit.md", "audit-operators", "monitoring"),
    }
    severity_by_trigger = {
        "page": "critical",
        "act_this_week": "high",
        "investigate": "medium",
        "monitor": "low",
    }

    for row in rows:
        provider = str(row.get("provider", ""))
        if not provider:
            continue
        primary_issue = str(row.get("primary_issue", "no acute anomaly"))
        source_summary = provider_summaries.get(provider, {}) if isinstance(provider_summaries, dict) else {}
        hints = source_summary.get("missing_repo_read_remediation_hints", []) if isinstance(source_summary, dict) else []
        matched_hint = None
        for hint in hints:
            if isinstance(hint, dict) and hint.get("rule_id") == primary_issue:
                matched_hint = hint
                break
        if matched_hint is None and primary_issue in rule_by_id:
            rule = rule_by_id[primary_issue]
            matched_hint = {
                "canonical_targets": rule.get("canonical_targets", []),
                "guidance": rule.get("guidance"),
                "reference_doc": rule.get("reference_doc"),
                "matched_paths": [{"path": path, "count": 0} for path in rule.get("patterns", [])[:3]],
            }

        fallback = generic_playbooks.get(primary_issue, generic_playbooks["no acute anomaly"])
        inspect_paths = [item.get("path") for item in matched_hint.get("matched_paths", [])[:3] if isinstance(item, dict) and item.get("path")] if matched_hint else []
        canonical_targets = list(matched_hint.get("canonical_targets", [])) if matched_hint else list(fallback.get("canonical_targets", []))
        if not inspect_paths:
            inspect_paths = list(fallback.get("inspect_paths", []))
        guidance = matched_hint.get("guidance") if matched_hint and matched_hint.get("guidance") else fallback.get("guidance")
        reference_doc = matched_hint.get("reference_doc") if matched_hint and matched_hint.get("reference_doc") else fallback.get("reference_doc")
        trigger = watchlist_by_provider.get(provider, {})

        first_steps = list(fallback.get("first_steps", []))
        if matched_hint and primary_issue in rule_by_id:
            first_steps = [
                f"Inspect the top matched stale paths for {primary_issue} and confirm they should redirect rather than be recreated.",
                f"Open the canonical targets and migrate prompts/docs/tooling toward: {', '.join(canonical_targets[:3]) or 'documented canonical surfaces'}.",
                "Update redirect docs, prompts, or exporter mappings so the legacy path family stops appearing in future audits.",
            ]
        owner_surface, owner_team, preferred_fix_lane = lane_by_issue.get(
            primary_issue,
            (
                fallback.get("owner_surface", "docs/reports/provider-session-ecosystem-audit.md"),
                fallback.get("owner_team", "audit-operators"),
                fallback.get("preferred_fix_lane", "monitoring"),
            ),
        )
        trigger_level = trigger.get("trigger_level", "monitor")
        playbooks.append(
            {
                "provider": provider,
                "primary_issue": primary_issue,
                "trigger_level": trigger_level,
                "severity": severity_by_trigger.get(str(trigger_level), "low"),
                "inspect_paths": inspect_paths,
                "canonical_targets": canonical_targets,
                "first_steps": first_steps,
                "reference_doc": reference_doc,
                "guidance": guidance,
                "owner_surface": owner_surface,
                "owner_team": owner_team,
                "preferred_fix_lane": preferred_fix_lane,
            }
        )

    return playbooks


def build_followup_issue_drafts(rows: list[dict], watchlist: list[dict], remediation_playbooks: list[dict], previous_audit: dict | None) -> list[dict]:
    watchlist_by_provider = {
        item.get("provider"): item
        for item in watchlist
        if isinstance(item, dict) and item.get("provider")
    }
    playbook_by_provider = {
        item.get("provider"): item
        for item in remediation_playbooks
        if isinstance(item, dict) and item.get("provider")
    }
    previous_drafts = (
        previous_audit.get("executive_summary", {}).get("provider_interpretation_summary", {}).get("followup_issue_drafts", [])
        if isinstance(previous_audit, dict)
        else []
    )
    previous_draft_map = {
        item.get("provider"): item
        for item in previous_drafts
        if isinstance(item, dict) and item.get("provider")
    }

    drafts: list[dict] = []
    for row in rows:
        provider = str(row.get("provider", ""))
        if not provider:
            continue
        watch = watchlist_by_provider.get(provider, {})
        playbook = playbook_by_provider.get(provider, {})
        trigger_level = str(watch.get("trigger_level", "monitor"))
        if trigger_level == "monitor":
            continue

        primary_issue = str(row.get("primary_issue", "no acute anomaly"))
        severity = str(playbook.get("severity", "low"))
        owner_team = str(playbook.get("owner_team", "audit-operators"))
        preferred_fix_lane = str(playbook.get("preferred_fix_lane", "monitoring"))
        owner_surface = str(playbook.get("owner_surface", "docs/reports/provider-session-ecosystem-audit.md"))
        inspect_paths = list(playbook.get("inspect_paths", []))
        canonical_targets = list(playbook.get("canonical_targets", []))
        first_steps = list(playbook.get("first_steps", []))
        trigger_reason = str(watch.get("trigger_reason", ""))
        suggested_followup = str(watch.get("suggested_followup", ""))
        guidance = str(playbook.get("guidance", ""))
        reference_doc = str(playbook.get("reference_doc", ""))

        title = f"[{severity}] {provider}: remediate {primary_issue}"
        summary = (
            f"Provider `{provider}` is currently at trigger level `{trigger_level}` with health `{row.get('health_status')}` "
            f"and urgency tier `{row.get('urgency_tier')}`."
        )
        body_lines = [
            f"Summary: {summary}",
            f"Primary issue: {primary_issue}",
            f"Owner team: {owner_team}",
            f"Preferred fix lane: {preferred_fix_lane}",
            f"Owner surface: {owner_surface}",
            f"Watchlist trigger: {trigger_reason}",
            f"Suggested follow-up: {suggested_followup}",
            f"Guidance: {guidance}",
            f"Reference doc: {reference_doc}",
            "Inspect paths:",
        ]
        body_lines.extend(f"- {path}" for path in inspect_paths)
        body_lines.append("Canonical targets:")
        body_lines.extend(f"- {path}" for path in canonical_targets)
        body_lines.append("First steps:")
        body_lines.extend(f"- {step}" for step in first_steps)
        body = "\n".join(body_lines)

        dedupe_scope = f"{provider}:{primary_issue}:{preferred_fix_lane}"
        linkage_key = f"{provider}:{primary_issue}:{severity}:{preferred_fix_lane}"
        stripped_title = re.sub(r"^\[[^\]]+\]\s*", "", title).strip()
        previous_draft = previous_draft_map.get(provider, {}) if isinstance(previous_draft_map, dict) else {}
        previous_title = str(previous_draft.get("title")) if previous_draft and previous_draft.get("title") else None
        linkage_aliases = [title, stripped_title, linkage_key, dedupe_scope]
        if previous_title:
            linkage_aliases.append(previous_title)
            stripped_previous_title = re.sub(r"^\[[^\]]+\]\s*", "", previous_title).strip()
            if stripped_previous_title:
                linkage_aliases.append(stripped_previous_title)
        linkage_aliases = list(dict.fromkeys(alias for alias in linkage_aliases if alias))
        fingerprint_source = {
            "provider": provider,
            "primary_issue": primary_issue,
            "preferred_fix_lane": preferred_fix_lane,
            "owner_team": owner_team,
            "severity": severity,
            "trigger_level": trigger_level,
        }
        draft_key = hashlib.sha256(json.dumps(fingerprint_source, sort_keys=True).encode("utf-8")).hexdigest()[:16]
        previous_draft_key = previous_draft.get("draft_key") if previous_draft else None
        if not previous_draft:
            draft_state = "new"
        elif previous_draft_key == draft_key:
            draft_state = "unchanged"
        else:
            draft_state = "changed"

        evidence_gaps: list[str] = []
        if not inspect_paths:
            evidence_gaps.append("inspect_paths")
        if not canonical_targets:
            evidence_gaps.append("canonical_targets")
        if not first_steps:
            evidence_gaps.append("first_steps")
        if not reference_doc:
            evidence_gaps.append("reference_doc")
        if not guidance:
            evidence_gaps.append("guidance")
        if not trigger_reason:
            evidence_gaps.append("trigger_reason")
        if not suggested_followup:
            evidence_gaps.append("suggested_followup")
        if not owner_team:
            evidence_gaps.append("owner_team")
        if not preferred_fix_lane:
            evidence_gaps.append("preferred_fix_lane")
        minimum_evidence_present = not evidence_gaps

        if not minimum_evidence_present:
            should_open_issue = False
            issue_open_reason = None
            blocker_reason = f"missing minimum evidence: {', '.join(evidence_gaps)}"
        elif draft_state == "unchanged":
            should_open_issue = False
            issue_open_reason = None
            blocker_reason = "draft unchanged since previous audit; avoid duplicate issue creation until linked issue state is known"
        else:
            should_open_issue = True
            issue_open_reason = f"{draft_state} actionable draft with minimum evidence present"
            blocker_reason = None

        drafts.append(
            {
                "provider": provider,
                "title": title,
                "severity": severity,
                "owner_team": owner_team,
                "preferred_fix_lane": preferred_fix_lane,
                "body": body,
                "draft_key": draft_key,
                "dedupe_scope": dedupe_scope,
                "linkage_key": linkage_key,
                "linkage_aliases": linkage_aliases,
                "duplicate_of_previous_draft_key": previous_draft_key if previous_draft_key == draft_key else None,
                "draft_state": draft_state,
                "previous_title": previous_draft.get("title") if previous_draft else None,
                "previous_severity": previous_draft.get("severity") if previous_draft else None,
                "previous_owner_team": previous_draft.get("owner_team") if previous_draft else None,
                "minimum_evidence_present": minimum_evidence_present,
                "should_open_issue": should_open_issue,
                "issue_open_reason": issue_open_reason,
                "blocker_reason": blocker_reason,
                "evidence_gaps": evidence_gaps,
            }
        )

    severity_rank = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    drafts.sort(key=lambda item: (-severity_rank.get(str(item.get("severity", "low")), 0), str(item.get("provider", ""))))
    return drafts


def build_cleared_followup_issue_drafts(followup_issue_drafts: list[dict], previous_audit: dict | None) -> list[dict]:
    if not previous_audit:
        return []
    previous_drafts = (
        previous_audit.get("executive_summary", {}).get("provider_interpretation_summary", {}).get("followup_issue_drafts", [])
        if isinstance(previous_audit, dict)
        else []
    )
    active_providers = {
        item.get("provider")
        for item in followup_issue_drafts
        if isinstance(item, dict) and item.get("provider")
    }
    cleared: list[dict] = []
    for item in previous_drafts:
        if not isinstance(item, dict):
            continue
        provider = item.get("provider")
        if not provider or provider in active_providers:
            continue
        cleared.append(
            {
                "provider": provider,
                "draft_state": "cleared",
                "previous_title": item.get("title"),
                "previous_severity": item.get("severity"),
                "previous_owner_team": item.get("owner_team"),
                "previous_draft_key": item.get("draft_key"),
            }
        )
    cleared.sort(key=lambda item: str(item.get("provider", "")))
    return cleared


def build_issue_posting_readiness(followup_issue_drafts: list[dict], github_issues: list[dict] | None = None) -> list[dict]:
    severity_rank = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    github_issues = github_issues or []

    def find_linked_issue(draft: dict) -> tuple[dict | None, str, str]:
        current_title = str(draft.get("title", "")).strip()
        previous_title = str(draft.get("previous_title", "")).strip()
        linkage_aliases = [str(alias).strip() for alias in draft.get("linkage_aliases", []) if str(alias).strip()]
        for issue in github_issues:
            if not isinstance(issue, dict):
                continue
            issue_title = str(issue.get("title", "")).strip()
            if current_title and issue_title == current_title:
                return issue, "exact_title", "matched current title exactly"
        for issue in github_issues:
            if not isinstance(issue, dict):
                continue
            issue_title = str(issue.get("title", "")).strip()
            if previous_title and issue_title == previous_title:
                return issue, "previous_title", "matched previous title exactly"
        for issue in github_issues:
            if not isinstance(issue, dict):
                continue
            issue_title = str(issue.get("title", "")).strip()
            if issue_title and issue_title in linkage_aliases:
                return issue, "alias", "matched linkage alias exactly"
        return None, "none", "no linked issue match found"

    readiness: list[dict] = []
    for draft in followup_issue_drafts:
        if not isinstance(draft, dict) or not draft.get("provider"):
            continue
        provider = str(draft.get("provider", ""))
        severity = str(draft.get("severity", "low"))
        current_title = str(draft.get("title", "")).strip()
        previous_title = str(draft.get("previous_title", "")).strip()
        stripped_title = re.sub(r"^\[[^\]]+\]\s*", "", current_title).strip()
        preferred_fix_lane = str(draft.get("preferred_fix_lane", "monitoring") or "monitoring")
        issue_slug = "unknown_issue"
        if ": remediate " in stripped_title:
            issue_slug = stripped_title.split(": remediate ", 1)[1].strip().replace(" ", "_")
        linkage_key = draft.get("linkage_key") or f"{provider}:{issue_slug}:{severity}:{preferred_fix_lane}"
        linkage_aliases = list(draft.get("linkage_aliases", []))
        if not linkage_aliases:
            linkage_aliases = [current_title, stripped_title, linkage_key]
            if previous_title:
                linkage_aliases.append(previous_title)
                stripped_previous_title = re.sub(r"^\[[^\]]+\]\s*", "", previous_title).strip()
                if stripped_previous_title:
                    linkage_aliases.append(stripped_previous_title)
            linkage_aliases = list(dict.fromkeys(alias for alias in linkage_aliases if alias))
        linked_issue, linkage_confidence, linked_issue_match_reason = find_linked_issue(
            {
                **draft,
                "linkage_key": linkage_key,
                "linkage_aliases": linkage_aliases,
            }
        )
        linked_issue_number = linked_issue.get("number") if linked_issue else None
        linked_issue_url = linked_issue.get("url") if linked_issue else None
        linked_issue_state = str(linked_issue.get("state", "")).upper() if linked_issue else None
        minimum_evidence_present = bool(draft.get("minimum_evidence_present"))
        should_open_issue = bool(draft.get("should_open_issue"))
        issue_open_reason = draft.get("issue_open_reason")
        blocker_reason = draft.get("blocker_reason")
        draft_state = str(draft.get("draft_state", "new"))

        final_open_reason: str | None = None
        final_blocker_reason: str | None = None
        if not minimum_evidence_present:
            should_open_issue_final = False
            final_blocker_reason = str(blocker_reason) if blocker_reason else "missing minimum evidence"
        elif linked_issue_state == "OPEN" and linked_issue_number is not None:
            should_open_issue_final = False
            final_blocker_reason = f"linked open issue already exists: #{linked_issue_number}"
        elif linked_issue_state == "CLOSED" and linked_issue_number is not None:
            should_open_issue_final = True
            final_open_reason = f"linked issue #{linked_issue_number} is closed; safe to open a fresh follow-up"
        elif should_open_issue:
            should_open_issue_final = True
            final_open_reason = f"{draft_state} actionable draft with no linked issue found"
        elif draft_state == "unchanged":
            should_open_issue_final = True
            final_open_reason = "unchanged draft has no linked issue; safe to open once"
        else:
            should_open_issue_final = False
            final_blocker_reason = str(blocker_reason) if blocker_reason else "posting remains blocked"

        readiness.append(
            {
                "provider": str(draft.get("provider", "")),
                "severity": str(draft.get("severity", "low")),
                "draft_state": draft_state,
                "posting_status": "ready" if should_open_issue else "blocked",
                "minimum_evidence_present": minimum_evidence_present,
                "should_open_issue": should_open_issue,
                "issue_open_reason": issue_open_reason,
                "blocker_reason": blocker_reason,
                "evidence_gaps": list(draft.get("evidence_gaps", [])),
                "linkage_key": linkage_key,
                "linkage_aliases": linkage_aliases,
                "linked_issue_number": linked_issue_number,
                "linked_issue_url": linked_issue_url,
                "linked_issue_state": linked_issue_state,
                "matched_on": linkage_confidence,
                "linked_issue_match_reason": linked_issue_match_reason,
                "linkage_confidence": linkage_confidence,
                "should_open_issue_final": should_open_issue_final,
                "final_posting_status": "ready" if should_open_issue_final else "blocked",
                "final_open_reason": final_open_reason,
                "final_blocker_reason": final_blocker_reason,
            }
        )
    readiness.sort(
        key=lambda item: (
            0 if item.get("should_open_issue_final") else 1,
            -severity_rank.get(str(item.get("severity", "low")), 0),
            str(item.get("provider", "")),
        )
    )
    return readiness


def build_recent_activity_summary(
    provider_summaries: dict[str, dict], logs_root: Path, repo_root: Path, previous_generated_at: str | None
) -> dict:
    if not previous_generated_at:
        return {
            "previous_generated_at": None,
            "status": "no_prior_audit",
            "providers": {},
        }

    try:
        cutoff_ts = datetime.fromisoformat(previous_generated_at.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return {
            "previous_generated_at": previous_generated_at,
            "status": "invalid_prior_audit_timestamp",
            "providers": {},
        }

    recent_by_provider: dict[str, dict] = {}
    for provider in PROVIDERS:
        logs_dir = logs_root / provider
        summary = provider_summaries.get(provider, {})
        if not logs_dir.exists() or summary.get("source") not in {"raw_logs", "precomputed_report"}:
            recent_by_provider[provider] = {
                "post_records": 0,
                "sessions": 0,
                "top_tools": [],
                "top_missing_repo_reads": [],
                "top_reads": [],
                "top_writes": [],
                "top_edits": [],
                "top_bash_command_families": [],
            }
            continue
        if summary.get("source") == "precomputed_report":
            recent_by_provider[provider] = {
                "post_records": 0,
                "sessions": 0,
                "top_tools": [],
                "top_missing_repo_reads": [],
                "top_bash_command_families": [],
                "limitations": [
                    "Recent event-time activity since the prior audit timestamp cannot be reconstructed from the precomputed fallback artifact alone."
                ],
            }
            continue
        recent_by_provider[provider] = compute_recent_activity_since(provider, logs_dir, repo_root, cutoff_ts)

    ranked = sorted(
        (
            {"provider": provider, **stats}
            for provider, stats in recent_by_provider.items()
            if stats.get("post_records", 0) or stats.get("sessions", 0)
        ),
        key=lambda item: (-int(item.get("post_records", 0)), -int(item.get("sessions", 0)), item["provider"]),
    )
    return {
        "previous_generated_at": previous_generated_at,
        "status": "ok",
        "scope_note": "This is event-time activity since the previous audit timestamp, not a census of newly exported historical/backfilled records.",
        "providers": recent_by_provider,
        "ranked_providers": [
            {
                "provider": item["provider"],
                "post_records": item.get("post_records", 0),
                "sessions": item.get("sessions", 0),
            }
            for item in ranked
        ],
    }


def build_activity_window_summary(
    provider_summaries: dict[str, dict],
    logs_root: Path,
    repo_root: Path,
    generated_at: str,
) -> dict:
    generated_ts = datetime.fromisoformat(generated_at.replace("Z", "+00:00")).timestamp()
    windows = [
        ("last_24h", 24 * 60 * 60, "Last 24 hours of event-time activity ending at this audit timestamp."),
        ("last_7d", 7 * 24 * 60 * 60, "Last 7 days of event-time activity ending at this audit timestamp."),
    ]
    summary: dict[str, dict] = {}

    for window_name, duration_seconds, scope_note in windows:
        start_ts = generated_ts - duration_seconds
        window_by_provider: dict[str, dict] = {}
        for provider in PROVIDERS:
            logs_dir = logs_root / provider
            provider_summary = provider_summaries.get(provider, {})
            if not logs_dir.exists() or provider_summary.get("source") not in {"raw_logs", "precomputed_report"}:
                window_by_provider[provider] = {
                    "post_records": 0,
                    "sessions": 0,
                    "top_tools": [],
                    "top_missing_repo_reads": [],
                    "top_reads": [],
                    "top_writes": [],
                    "top_edits": [],
                    "top_bash_command_families": [],
                }
                continue
            if provider_summary.get("source") == "precomputed_report":
                window_by_provider[provider] = {
                    "post_records": 0,
                    "sessions": 0,
                    "top_tools": [],
                    "top_missing_repo_reads": [],
                    "top_reads": [],
                    "top_writes": [],
                    "top_edits": [],
                    "top_bash_command_families": [],
                    "limitations": [
                        "Rolling event-time windows cannot be reconstructed from the precomputed fallback artifact alone."
                    ],
                }
                continue
            window_by_provider[provider] = compute_activity_window(
                provider,
                logs_dir,
                repo_root,
                start_ts=start_ts,
                end_ts=generated_ts,
            )

        ranked = sorted(
            (
                {"provider": provider, **stats}
                for provider, stats in window_by_provider.items()
                if stats.get("post_records", 0) or stats.get("sessions", 0)
            ),
            key=lambda item: (-int(item.get("post_records", 0)), -int(item.get("sessions", 0)), item["provider"]),
        )
        summary[window_name] = {
            "window_start": datetime.fromtimestamp(start_ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "window_end": generated_at,
            "status": "ok",
            "scope_note": scope_note,
            "providers": window_by_provider,
            "ranked_providers": [
                {
                    "provider": item["provider"],
                    "post_records": item.get("post_records", 0),
                    "sessions": item.get("sessions", 0),
                }
                for item in ranked
            ],
        }

    return {
        "generated_at": generated_at,
        "status": "ok",
        "windows": summary,
    }


def build_corpus_change_summary(
    provider_summaries: dict[str, dict], previous_audit: dict | None, recent_activity: dict
) -> dict:
    if not previous_audit:
        return {
            "previous_generated_at": None,
            "status": "no_prior_audit",
            "providers": {},
        }

    previous_generated_at = str(previous_audit.get("generated_at", "") or "") or None
    previous_providers = previous_audit.get("providers", {}) if isinstance(previous_audit, dict) else {}
    recent_providers = recent_activity.get("providers", {}) if isinstance(recent_activity, dict) else {}

    by_provider: dict[str, dict] = {}
    ranked: list[dict] = []
    for provider in PROVIDERS:
        current = provider_summaries.get(provider, {})
        previous = previous_providers.get(provider, {}) if isinstance(previous_providers, dict) else {}
        if not previous:
            by_provider[provider] = {
                "status": "unavailable",
                "previous_source": None,
                "current_source": current.get("source"),
                "interpretation": "No previous provider snapshot available for comparison.",
            }
            continue

        current_post = int(current.get("post_records", 0) or 0)
        previous_post = int(previous.get("post_records", 0) or 0)
        current_sessions = int(current.get("sessions", 0) or 0)
        previous_sessions = int(previous.get("sessions", 0) or 0)
        current_missing = int(current.get("missing_repo_reads", 0) or 0)
        previous_missing = int(previous.get("missing_repo_reads", 0) or 0)
        recent_post = int(recent_providers.get(provider, {}).get("post_records", 0) or 0)
        recent_sessions = int(recent_providers.get(provider, {}).get("sessions", 0) or 0)

        post_delta = current_post - previous_post
        session_delta = current_sessions - previous_sessions
        missing_delta = current_missing - previous_missing
        reconciliation_gap = post_delta - recent_post
        source_changed = current.get("source") != previous.get("source")

        if source_changed:
            status = "source_changed"
            interpretation = "Provider source changed between audits, so snapshot deltas should be treated cautiously."
        elif reconciliation_gap == 0:
            status = "aligned"
            interpretation = "Snapshot post-record change aligns with recent event-time activity."
        elif reconciliation_gap > 0:
            status = "positive_corpus_growth_beyond_recent_activity"
            interpretation = "Snapshot grew more than recent event-time activity, suggesting backfill or expanded export coverage."
        else:
            status = "corpus_pruned_or_rebuilt"
            interpretation = "Snapshot shrank relative to recent event-time activity, suggesting pruning, rebuild, or reclassification."

        row = {
            "status": status,
            "previous_source": previous.get("source"),
            "current_source": current.get("source"),
            "previous_post_records": previous_post,
            "current_post_records": current_post,
            "post_record_delta": post_delta,
            "previous_sessions": previous_sessions,
            "current_sessions": current_sessions,
            "session_delta": session_delta,
            "previous_missing_repo_reads": previous_missing,
            "current_missing_repo_reads": current_missing,
            "missing_repo_read_delta": missing_delta,
            "event_time_post_records_since_previous_audit": recent_post,
            "event_time_sessions_since_previous_audit": recent_sessions,
            "reconciliation_gap_post_records": reconciliation_gap,
            "interpretation": interpretation,
        }
        by_provider[provider] = row
        ranked.append(
            {
                "provider": provider,
                "post_record_delta": post_delta,
                "event_time_post_records_since_previous_audit": recent_post,
                "reconciliation_gap_post_records": reconciliation_gap,
                "status": status,
            }
        )

    ranked.sort(key=lambda item: (-abs(item.get("reconciliation_gap_post_records", 0)), item["provider"]))
    largest_positive = max(ranked, key=lambda item: item.get("reconciliation_gap_post_records", float("-inf")), default=None)
    largest_negative = min(ranked, key=lambda item: item.get("reconciliation_gap_post_records", float("inf")), default=None)
    return {
        "previous_generated_at": previous_generated_at,
        "status": "ok",
        "scope_note": "Snapshot-to-snapshot corpus deltas reflect export additions/removals/reclassification and should be interpreted separately from event-time recent activity.",
        "providers": by_provider,
        "ranked_providers": ranked,
        "largest_positive_reconciliation_gap_provider": largest_positive["provider"] if largest_positive else None,
        "largest_negative_reconciliation_gap_provider": largest_negative["provider"] if largest_negative else None,
    }


def build_provider_interpretation_summary(
    provider_summaries: dict[str, dict],
    migration_debt: dict,
    recent_activity: dict,
    corpus_change: dict,
    previous_audit: dict | None,
    rolling_windows: dict | None,
    github_issues: list[dict] | None = None,
) -> dict:
    debt_by_provider = {
        row.get("provider"): row
        for row in migration_debt.get("ranked_providers", [])
        if isinstance(row, dict) and row.get("provider")
    }
    recent_by_provider = recent_activity.get("providers", {}) if isinstance(recent_activity, dict) else {}
    corpus_by_provider = corpus_change.get("providers", {}) if isinstance(corpus_change, dict) else {}
    previous_providers = previous_audit.get("providers", {}) if isinstance(previous_audit, dict) else {}
    previous_migration_rows = (
        previous_audit.get("executive_summary", {}).get("migration_debt", {}).get("ranked_providers", [])
        if isinstance(previous_audit, dict)
        else []
    )
    previous_migration_by_provider = {
        row.get("provider"): row
        for row in previous_migration_rows
        if isinstance(row, dict) and row.get("provider")
    }
    previous_recent_by_provider = (
        previous_audit.get("executive_summary", {}).get("recent_activity_since_previous_audit", {}).get("providers", {})
        if isinstance(previous_audit, dict)
        else {}
    )
    previous_interpretation_rows = (
        previous_audit.get("executive_summary", {}).get("provider_interpretation_summary", {}).get("providers", [])
        if isinstance(previous_audit, dict)
        else []
    )
    previous_rank_by_provider = {
        row.get("provider"): index + 1
        for index, row in enumerate(previous_interpretation_rows)
        if isinstance(row, dict) and row.get("provider")
    }
    previous_interpretation_by_provider = {
        row.get("provider"): row
        for row in previous_interpretation_rows
        if isinstance(row, dict) and row.get("provider")
    }
    window_map = rolling_windows.get("windows", {}) if isinstance(rolling_windows, dict) else {}
    last_24h_by_provider = (
        window_map.get("last_24h", {}).get("providers", {})
        if isinstance(window_map.get("last_24h", {}), dict)
        else {}
    )
    last_7d_by_provider = (
        window_map.get("last_7d", {}).get("providers", {})
        if isinstance(window_map.get("last_7d", {}), dict)
        else {}
    )

    rows: list[dict] = []
    for provider in PROVIDERS:
        summary = provider_summaries.get(provider, {})
        debt = debt_by_provider.get(provider, {})
        recent = recent_by_provider.get(provider, {}) if isinstance(recent_by_provider, dict) else {}
        corpus = corpus_by_provider.get(provider, {}) if isinstance(corpus_by_provider, dict) else {}

        recent_post = int(recent.get("post_records", 0) or 0)
        recent_sessions = int(recent.get("sessions", 0) or 0)
        activity_status = compute_activity_status(recent_post, recent_sessions, str(recent_activity.get("status", "")))

        corpus_status = corpus.get("status", "unavailable") if corpus_change.get("status") == "ok" else "unavailable"

        known_debt_reads = int(debt.get("known_migration_debt_reads", 0) or 0)
        debt_density = float(debt.get("known_migration_debt_per_1k_records", 0) or 0)
        missing_repo_reads = int(summary.get("missing_repo_reads", 0) or 0)
        if known_debt_reads == 0 and missing_repo_reads == 0:
            debt_status = "none"
        elif known_debt_reads == 0 and missing_repo_reads > 0:
            debt_status = "drift_only"
        elif debt_density >= 10:
            debt_status = "high_debt"
        else:
            debt_status = "moderate_debt"

        python3_rate = float(summary.get("python3_per_1k_records", 0) or 0)
        uv_rate = float(summary.get("uv_python_per_1k_records", 0) or 0)
        python_hygiene_status = compute_python_hygiene_status(python3_rate, uv_rate)

        post_records = int(summary.get("post_records", 0) or 0)
        missing_repo_reads_per_1k_records = round(missing_repo_reads * 1000 / post_records, 2) if post_records else 0.0
        previous_provider = previous_providers.get(provider, {}) if isinstance(previous_providers, dict) else {}
        previous_post_records = int(previous_provider.get("post_records", 0) or 0)
        previous_missing_repo_reads = int(previous_provider.get("missing_repo_reads", 0) or 0)
        previous_missing_repo_reads_per_1k_records = (
            round(previous_missing_repo_reads * 1000 / previous_post_records, 2) if previous_post_records else None
        )
        previous_debt = previous_migration_by_provider.get(provider, {})
        previous_debt_density = (
            float(previous_debt.get("known_migration_debt_per_1k_records", 0) or 0)
            if previous_debt
            else None
        )
        previous_recent = previous_recent_by_provider.get(provider, {}) if isinstance(previous_recent_by_provider, dict) else {}
        previous_activity_status = compute_activity_status(
            int(previous_recent.get("post_records", 0) or 0),
            int(previous_recent.get("sessions", 0) or 0),
            str(previous_audit.get("executive_summary", {}).get("recent_activity_since_previous_audit", {}).get("status", ""))
            if isinstance(previous_audit, dict)
            else "",
        )
        previous_python_hygiene_status = (
            compute_python_hygiene_status(
                float(previous_provider.get("python3_per_1k_records", 0) or 0),
                float(previous_provider.get("uv_python_per_1k_records", 0) or 0),
            )
            if previous_provider
            else "unavailable"
        )

        debt_trend = compare_direction(debt_density, previous_debt_density, better_when_lower=True)
        drift_trend = compare_direction(
            missing_repo_reads_per_1k_records,
            previous_missing_repo_reads_per_1k_records,
            better_when_lower=True,
        )
        activity_trend = compare_activity_direction(activity_status, previous_activity_status)
        python_rank_map = {"unavailable": None, "no_python_usage": 0.0, "uv_preferred": 1.0, "mixed": 2.0, "python3_heavy": 3.0}
        python_hygiene_trend = compare_direction(
            python_rank_map.get(python_hygiene_status),
            python_rank_map.get(previous_python_hygiene_status),
            better_when_lower=True,
        )

        python_hygiene_points = {
            "python3_heavy": 6.0,
            "mixed": 3.0,
            "uv_preferred": 0.0,
            "no_python_usage": 0.0,
        }[python_hygiene_status]
        last_24h = last_24h_by_provider.get(provider, {}) if isinstance(last_24h_by_provider, dict) else {}
        last_7d = last_7d_by_provider.get(provider, {}) if isinstance(last_7d_by_provider, dict) else {}
        last_24h_post_records = int(last_24h.get("post_records", 0) or 0)
        last_24h_sessions = int(last_24h.get("sessions", 0) or 0)
        last_7d_post_records = int(last_7d.get("post_records", 0) or 0)
        last_7d_sessions = int(last_7d.get("sessions", 0) or 0)
        activity_window_profile = determine_activity_window_profile(last_24h_post_records, last_7d_post_records)
        urgency_score = (
            min(40.0, 3.0 * debt_density)
            + min(20.0, known_debt_reads / 50.0)
            + min(20.0, recent_post / 10.0 + 5.0 * recent_sessions)
            + (8.0 if corpus_status not in {"aligned", "unavailable"} else 0.0)
            + (min(10.0, missing_repo_reads_per_1k_records / 2.0) if known_debt_reads == 0 else 0.0)
            + python_hygiene_points
        )
        if urgency_score >= 70:
            urgency_tier = "urgent_now"
        elif urgency_score >= 35:
            urgency_tier = "next_up"
        elif urgency_score >= 10:
            urgency_tier = "investigate"
        else:
            urgency_tier = "monitor"

        if known_debt_reads > 0:
            primary_issue = debt.get("top_migration_rule_id") or "mapped migration debt"
            recommended_action = "prioritize legacy-path redirect cleanup and prompt/doc updates"
        elif missing_repo_reads > 0:
            primary_issue = "unmapped path drift"
            recommended_action = "sample top missing repo reads to separate remap work from benign variance"
        elif corpus_status == "positive_corpus_growth_beyond_recent_activity":
            primary_issue = "backfill/export growth beyond event-time activity"
            recommended_action = "verify exporter/backfill behavior before using trend deltas for decisions"
        elif corpus_status == "corpus_pruned_or_rebuilt":
            primary_issue = "corpus prune/rebuild drift"
            recommended_action = "check export resets/pruning before drawing provider usage conclusions"
        else:
            primary_issue = "no acute anomaly"
            recommended_action = "no immediate intervention; monitor next audit"

        health_status, health_reasons, health_summary = summarize_health_status(
            urgency_tier=urgency_tier,
            debt_status=debt_status,
            debt_trend=debt_trend,
            drift_trend=drift_trend,
            python_hygiene_status=python_hygiene_status,
            corpus_status=corpus_status,
            activity_status=activity_status,
            activity_window_profile=activity_window_profile,
        )

        rows.append(
            {
                "provider": provider,
                "urgency_score": round(urgency_score, 2),
                "urgency_tier": urgency_tier,
                "activity_status": activity_status,
                "activity_trend": activity_trend,
                "corpus_status": corpus_status,
                "debt_status": debt_status,
                "debt_trend": debt_trend,
                "python_hygiene_status": python_hygiene_status,
                "python_hygiene_trend": python_hygiene_trend,
                "drift_trend": drift_trend,
                "last_24h_post_records": last_24h_post_records,
                "last_24h_sessions": last_24h_sessions,
                "last_7d_post_records": last_7d_post_records,
                "last_7d_sessions": last_7d_sessions,
                "activity_window_profile": activity_window_profile,
                "health_status": health_status,
                "health_reasons": health_reasons,
                "health_summary": health_summary,
                "recent_post_records": recent_post,
                "recent_sessions": recent_sessions,
                "known_migration_debt_reads": known_debt_reads,
                "known_migration_debt_per_1k_records": debt_density,
                "missing_repo_reads_per_1k_records": missing_repo_reads_per_1k_records,
                "primary_issue": primary_issue,
                "recommended_action": recommended_action,
            }
        )

    debt_rank = {"high_debt": 3, "moderate_debt": 2, "drift_only": 1, "none": 0}
    python_rank = {"python3_heavy": 3, "mixed": 2, "uv_preferred": 1, "no_python_usage": 0}
    rows.sort(
        key=lambda row: (
            -float(row.get("urgency_score", 0) or 0),
            -debt_rank.get(str(row.get("debt_status", "none")), 0),
            -int(row.get("recent_post_records", 0) or 0),
            -int(row.get("known_migration_debt_reads", 0) or 0),
            -float(row.get("missing_repo_reads_per_1k_records", 0) or 0),
            -python_rank.get(str(row.get("python_hygiene_status", "no_python_usage")), 0),
            str(row.get("provider", "")),
        )
    )

    for index, row in enumerate(rows, start=1):
        row["urgency_rank"] = index
        previous_rank = previous_rank_by_provider.get(row["provider"])
        previous_interpretation = previous_interpretation_by_provider.get(row["provider"], {})
        previous_score = float(previous_interpretation.get("urgency_score", 0) or 0) if previous_interpretation else None
        direction, rank_delta, score_delta, summary = summarize_urgency_rank_movement(
            row,
            previous_rank,
            previous_score,
        )
        row["previous_urgency_rank"] = previous_rank
        row["urgency_rank_delta"] = rank_delta
        row["urgency_rank_direction"] = direction
        row["urgency_score_delta"] = score_delta
        row["urgency_movement_summary"] = summary

    focus_this_week = None
    recommended_actions: list[dict] = []
    rank_movements: list[dict] = []
    health_overview = [
        {
            "provider": row["provider"],
            "health_status": row.get("health_status"),
            "health_summary": row.get("health_summary"),
        }
        for row in rows
    ]
    watchlist = build_watchlist(rows)
    change_alerts = build_change_alerts(rows, watchlist, previous_audit)
    remediation_playbooks = build_remediation_playbooks(provider_summaries, rows, watchlist)
    followup_issue_drafts = build_followup_issue_drafts(rows, watchlist, remediation_playbooks, previous_audit)
    issue_posting_readiness = build_issue_posting_readiness(followup_issue_drafts, github_issues)
    cleared_followup_issue_drafts = build_cleared_followup_issue_drafts(followup_issue_drafts, previous_audit)
    if rows:
        primary = rows[0]
        focus_this_week = (
            f"Focus this week: {primary['recommended_action']} on {primary['provider']} "
            f"(urgency {primary['urgency_score']}, issue: {primary['primary_issue']})"
        )
        if len(rows) > 1 and float(rows[1].get("urgency_score", 0) or 0) >= 10:
            secondary = rows[1]
            focus_this_week += (
                f", then address {secondary['provider']} "
                f"(urgency {secondary['urgency_score']}, issue: {secondary['primary_issue']})."
            )
        else:
            focus_this_week += "."

        for row in rows:
            if row["urgency_tier"] == "monitor":
                continue
            recommended_actions.append(
                {
                    "provider": row["provider"],
                    "urgency_tier": row["urgency_tier"],
                    "urgency_score": row["urgency_score"],
                    "urgency_rank": row["urgency_rank"],
                    "previous_urgency_rank": row.get("previous_urgency_rank"),
                    "urgency_rank_direction": row.get("urgency_rank_direction"),
                    "urgency_rank_delta": row.get("urgency_rank_delta"),
                    "urgency_score_delta": row.get("urgency_score_delta"),
                    "urgency_movement_summary": row.get("urgency_movement_summary"),
                    "health_status": row.get("health_status"),
                    "health_summary": row.get("health_summary"),
                    "primary_issue": row["primary_issue"],
                    "recommended_action": row["recommended_action"],
                }
            )
        rank_movements = [
            {
                "provider": row["provider"],
                "urgency_rank": row["urgency_rank"],
                "previous_urgency_rank": row.get("previous_urgency_rank"),
                "urgency_rank_direction": row.get("urgency_rank_direction"),
                "urgency_rank_delta": row.get("urgency_rank_delta"),
                "urgency_score": row.get("urgency_score"),
                "urgency_score_delta": row.get("urgency_score_delta"),
                "summary": row.get("urgency_movement_summary"),
            }
            for row in rows
            if row.get("urgency_rank_direction") in {"up", "down", "new"}
        ]

    return {
        "providers": rows,
        "focus_this_week": focus_this_week,
        "recommended_actions": recommended_actions,
        "rank_movements": rank_movements,
        "health_overview": health_overview,
        "watchlist": watchlist,
        "change_alerts": change_alerts,
        "remediation_playbooks": remediation_playbooks,
        "followup_issue_drafts": followup_issue_drafts,
        "issue_posting_readiness": issue_posting_readiness,
        "cleared_followup_issue_drafts": cleared_followup_issue_drafts,
    }


def build_provider_audit(repo_root: Path = REPO_ROOT, logs_root: Path = LOGS_ROOT) -> dict:
    provider_summaries: dict[str, dict] = {}
    previous_audit_path = repo_root / "analysis" / "provider-session-ecosystem-audit.json"
    previous_generated_at = load_previous_generated_at(previous_audit_path)
    previous_audit = load_previous_audit(previous_audit_path)
    github_issues = load_github_issue_index(repo_root)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for provider in PROVIDERS:
        logs_dir = logs_root / provider
        has_raw_sessions = logs_dir.exists() and any(logs_dir.glob("session_*.jsonl"))

        if provider == "claude" and has_raw_sessions:
            provider_summaries[provider] = summarize_raw_provider(provider, logs_dir, repo_root)
            continue

        if provider == "claude" and CLAUDE_PRECOMPUTED.exists():
            provider_summaries[provider] = summarize_claude_precomputed(CLAUDE_PRECOMPUTED)
            continue

        if not logs_dir.exists() or not has_raw_sessions:
            provider_summaries[provider] = {
                "source": "missing_log_directory" if not logs_dir.exists() else "empty_log_directory",
                "sessions": 0,
                "post_records": 0,
                "limitations": [
                    f"No log directory at {logs_dir}"
                    if not logs_dir.exists()
                    else f"No session_*.jsonl files under {logs_dir}"
                ],
            }
            continue

        provider_summaries[provider] = summarize_raw_provider(provider, logs_dir, repo_root)

    recent_activity = build_recent_activity_summary(provider_summaries, logs_root, repo_root, previous_generated_at)
    rolling_windows = build_activity_window_summary(provider_summaries, logs_root, repo_root, generated_at)
    corpus_change = build_corpus_change_summary(provider_summaries, previous_audit, recent_activity)
    migration_debt = build_migration_debt_summary(provider_summaries)
    provider_interpretation = build_provider_interpretation_summary(
        provider_summaries,
        migration_debt,
        recent_activity,
        corpus_change,
        previous_audit,
        rolling_windows,
        github_issues,
    )

    executive_actions = {
        "focus_this_week": provider_interpretation.get("focus_this_week"),
        "recommended_actions": provider_interpretation.get("recommended_actions", []),
        "rank_movements": provider_interpretation.get("rank_movements", []),
        "health_overview": provider_interpretation.get("health_overview", []),
        "watchlist": provider_interpretation.get("watchlist", []),
        "change_alerts": provider_interpretation.get("change_alerts", []),
        "remediation_playbooks": provider_interpretation.get("remediation_playbooks", []),
        "followup_issue_drafts": provider_interpretation.get("followup_issue_drafts", []),
        "issue_posting_readiness": provider_interpretation.get("issue_posting_readiness", []),
        "cleared_followup_issue_drafts": provider_interpretation.get("cleared_followup_issue_drafts", []),
    }

    return {
        "generated_at": generated_at,
        "repo_root": str(repo_root),
        "logs_root": str(logs_root),
        "providers": provider_summaries,
        "executive_summary": {
            "migration_debt": migration_debt,
            "provider_interpretation_summary": provider_interpretation,
            "executive_actions": executive_actions,
            "recent_activity_since_previous_audit": recent_activity,
            "recent_activity_windows": rolling_windows,
            "corpus_change_since_previous_audit": corpus_change,
        },
    }


def render_markdown(audit: dict) -> str:
    lines = [
        f"# Provider session ecosystem audit — {audit['generated_at'][:10]}",
        "",
        f"Scope: provider session artifacts rooted at `{Path(audit['logs_root']).as_posix()}` with saved provider artifacts used only as fallback when raw logs are unavailable.",
        "",
        "## Executive summary",
    ]

    for provider, summary in audit["providers"].items():
        lines.append(
            f"- `{provider}` — source={summary.get('source')} | sessions={summary.get('sessions', 0)} | post_records={summary.get('post_records', 0)} | python3/1k={summary.get('python3_per_1k_records', 0)} | uv-python/1k={summary.get('uv_python_per_1k_records', 0)}"
        )
    lines.append("")

    migration_debt = audit.get("executive_summary", {}).get("migration_debt", {})
    ranked_debt = migration_debt.get("ranked_providers", [])
    if ranked_debt:
        density_summary = ", ".join(
            f"`{item['provider']}` {item['known_migration_debt_per_1k_records']}"
            for item in ranked_debt
        )
        lines.append(f"- Migration debt density (known stale reads with redirect hints per 1k records): {density_summary}.")
        highest_volume = max(ranked_debt, key=lambda item: item.get("known_migration_debt_reads", 0))
        if highest_volume.get("known_migration_debt_reads", 0) > 0:
            lines.append(
                f"- Highest-volume known migration debt: `{highest_volume['provider']}` with {highest_volume['known_migration_debt_reads']} mapped stale reads across {highest_volume['known_migration_debt_rule_count']} rule clusters; top hotspot: `{highest_volume.get('top_migration_rule_id')}` ({highest_volume.get('top_migration_rule_reads', 0)})."
            )
        highest_density = ranked_debt[0]
        if highest_density.get("known_migration_debt_reads", 0) > 0:
            lines.append(
                f"- Highest-density known migration debt: `{highest_density['provider']}` with {highest_density['known_migration_debt_reads']} mapped stale reads; top hotspot: `{highest_density.get('top_migration_rule_id')}` ({highest_density.get('top_migration_rule_reads', 0)}, {highest_density.get('top_migration_rule_share_pct', 0)}% of known debt)."
            )
        unmapped = [
            item["provider"]
            for item in ranked_debt
            if item.get("known_migration_debt_reads", 0) == 0
            and audit.get("providers", {}).get(item["provider"], {}).get("missing_repo_reads", 0) > 0
        ]
        if unmapped:
            lines.append(
                f"- Unmapped missing repo reads remain for: {', '.join(f'`{provider}`' for provider in unmapped)}; this looks more like general path drift than known migration debt."
            )
        lines.append(f"- Scope note: {migration_debt.get('scope_note', '')}")
        lines.append("")

    interpretation_summary = audit.get("executive_summary", {}).get("provider_interpretation_summary", {})
    interpretation_rows = interpretation_summary.get("providers", []) if isinstance(interpretation_summary, dict) else []
    if interpretation_rows:
        lines.append("## Provider interpretation summary")
        focus_this_week = interpretation_summary.get("focus_this_week")
        if focus_this_week:
            lines.append(f"- {focus_this_week}")
        recommended_actions = interpretation_summary.get("recommended_actions", [])
        if recommended_actions:
            lines.append("- Recommended actions:")
            for action in recommended_actions:
                lines.append(
                    f"  - `{action['provider']}` [{action.get('urgency_tier')}] — {action.get('recommended_action')} (urgency {action.get('urgency_score')}, issue: {action.get('primary_issue')}; health={action.get('health_status')}; movement: {action.get('urgency_movement_summary')})"
                )
        health_overview = interpretation_summary.get("health_overview", [])
        if health_overview:
            lines.append("- Health overview:")
            for health in health_overview:
                lines.append(
                    f"  - `{health['provider']}` [{health.get('health_status')}] — {health.get('health_summary')}"
                )
        watchlist = interpretation_summary.get("watchlist", [])
        if watchlist:
            lines.append("- Watchlist triggers:")
            for item in watchlist:
                lines.append(
                    f"  - `{item['provider']}` [{item.get('trigger_level')}] — {item.get('trigger_reason')} | follow-up: {item.get('suggested_followup')}"
                )
        change_alerts = interpretation_summary.get("change_alerts", [])
        if change_alerts:
            lines.append("- Change alerts:")
            for alert in change_alerts:
                lines.append(
                    f"  - `{alert['provider']}` [{alert.get('change_type')}] — {alert.get('summary')} | follow-up: {alert.get('suggested_followup')}"
                )
        remediation_playbooks = interpretation_summary.get("remediation_playbooks", [])
        if remediation_playbooks:
            lines.append("- Remediation playbooks:")
            for playbook in remediation_playbooks:
                steps = playbook.get("first_steps", [])
                step_summary = " | ".join(str(step) for step in steps[:2]) if steps else "no immediate steps recorded"
                lines.append(
                    f"  - `{playbook['provider']}` [{playbook.get('trigger_level')}] — issue={playbook.get('primary_issue')} | lane={playbook.get('preferred_fix_lane')} | owner={playbook.get('owner_team')} | owner_surface={playbook.get('owner_surface')} | inspect={', '.join(playbook.get('inspect_paths', [])[:3])} | targets={', '.join(playbook.get('canonical_targets', [])[:3])} | steps: {step_summary}"
                )
        followup_issue_drafts = interpretation_summary.get("followup_issue_drafts", [])
        if followup_issue_drafts:
            lines.append("- Follow-up issue drafts:")
            for draft in followup_issue_drafts:
                lines.append(
                    f"  - `{draft['provider']}` [{draft.get('severity')}] — {draft.get('title')} | state={draft.get('draft_state')} | owner={draft.get('owner_team')} | lane={draft.get('preferred_fix_lane')}"
                )
        issue_posting_readiness = interpretation_summary.get("issue_posting_readiness", [])
        if issue_posting_readiness:
            lines.append("- Issue posting readiness:")
            for item in issue_posting_readiness:
                evidence_status = "complete" if item.get("minimum_evidence_present") else "gapped"
                linked_issue = (
                    f"#{item.get('linked_issue_number')} ({item.get('linked_issue_state')})"
                    if item.get("linked_issue_number")
                    else "none"
                )
                reason = item.get("final_open_reason") if item.get("should_open_issue_final") else item.get("final_blocker_reason")
                reason_label = "reason" if item.get("should_open_issue_final") else "blocker"
                lines.append(
                    f"  - `{item['provider']}` [{item.get('final_posting_status')}] — should_open_issue={'yes' if item.get('should_open_issue') else 'no'} | final_should_open={'yes' if item.get('should_open_issue_final') else 'no'} | evidence={evidence_status} | linked_issue={linked_issue} | matched_on={item.get('matched_on')} | {reason_label}={reason}"
                )
        cleared_followup_issue_drafts = interpretation_summary.get("cleared_followup_issue_drafts", [])
        if cleared_followup_issue_drafts:
            lines.append("- Cleared follow-up issue drafts:")
            for draft in cleared_followup_issue_drafts:
                lines.append(
                    f"  - `{draft['provider']}` [cleared] — previous_title={draft.get('previous_title')} | previous_severity={draft.get('previous_severity')} | previous_owner={draft.get('previous_owner_team')}"
                )
        rank_movements = interpretation_summary.get("rank_movements", [])
        if rank_movements:
            lines.append("- Rank movements since previous audit:")
            for movement in rank_movements:
                lines.append(f"  - `{movement['provider']}` — {movement.get('summary')}")
        for row in interpretation_rows:
            lines.append(
                f"- `{row['provider']}` — rank={row.get('urgency_rank')} (prev={row.get('previous_urgency_rank')}, move={row.get('urgency_rank_direction')}) | health={row.get('health_status')} | profile={row.get('activity_window_profile')} | 24h={row.get('last_24h_post_records')} posts/{row.get('last_24h_sessions')} sessions | 7d={row.get('last_7d_post_records')} posts/{row.get('last_7d_sessions')} sessions | urgency={row.get('urgency_score')} | tier={row.get('urgency_tier')} | activity={row.get('activity_status')} ({row.get('activity_trend')}) | corpus={row.get('corpus_status')} | debt={row.get('debt_status')} ({row.get('debt_trend')}) | drift={row.get('drift_trend')} | python={row.get('python_hygiene_status')} ({row.get('python_hygiene_trend')}) | health summary: {row.get('health_summary')} | movement: {row.get('urgency_movement_summary')} | primary issue: {row.get('primary_issue')} | action: {row.get('recommended_action')}"
            )
        lines.append("")

    recent_activity = audit.get("executive_summary", {}).get("recent_activity_since_previous_audit", {})
    recent_status = recent_activity.get("status")
    if recent_status == "ok":
        previous_generated_at = recent_activity.get("previous_generated_at")
        if previous_generated_at:
            lines.append("## Recent activity since previous audit")
            lines.append(f"- Previous audit timestamp: `{previous_generated_at}`")
            ranked_recent = recent_activity.get("ranked_providers", [])
            if ranked_recent:
                coverage_summary = ", ".join(
                    f"`{item['provider']}` {item['post_records']} post records / {item['sessions']} sessions"
                    for item in ranked_recent
                )
                lines.append(f"- Recent post-audit activity: {coverage_summary}.")
            scope_note = recent_activity.get("scope_note")
            if scope_note:
                lines.append(f"- Scope note: {scope_note}")
            lines.append("")
    elif recent_status == "no_prior_audit":
        lines.append("## Recent activity since previous audit")
        lines.append("- No prior tracked provider audit artifact was available, so recent delta analysis is not yet available.")
        lines.append("")
    elif recent_status == "invalid_prior_audit_timestamp":
        lines.append("## Recent activity since previous audit")
        lines.append(
            f"- Prior audit timestamp `{recent_activity.get('previous_generated_at')}` was invalid, so recent delta analysis was skipped."
        )
        lines.append("")

    recent_windows = audit.get("executive_summary", {}).get("recent_activity_windows", {})
    if recent_windows.get("status") == "ok":
        window_map = recent_windows.get("windows", {}) if isinstance(recent_windows, dict) else {}
        if window_map:
            lines.append("## Rolling activity windows")
            for window_name in ("last_24h", "last_7d"):
                window = window_map.get(window_name, {}) if isinstance(window_map, dict) else {}
                if not window:
                    continue
                lines.append(
                    f"- `{window_name}` — `{window.get('window_start')}` → `{window.get('window_end')}`"
                )
                if window.get("scope_note"):
                    lines.append(f"  - Scope note: {window.get('scope_note')}")
                ranked_window = window.get("ranked_providers", [])
                if ranked_window:
                    coverage_summary = ", ".join(
                        f"`{item['provider']}` {item['post_records']} post records / {item['sessions']} sessions"
                        for item in ranked_window
                    )
                    lines.append(f"  - Activity leaders: {coverage_summary}.")
                else:
                    lines.append("  - Activity leaders: no provider activity captured in this window.")
            lines.append("")

    corpus_change = audit.get("executive_summary", {}).get("corpus_change_since_previous_audit", {})
    corpus_status = corpus_change.get("status")
    if corpus_status == "ok":
        lines.append("## Corpus change since previous audit")
        previous_generated_at = corpus_change.get("previous_generated_at")
        if previous_generated_at:
            lines.append(f"- Previous audit timestamp: `{previous_generated_at}`")
        scope_note = corpus_change.get("scope_note")
        if scope_note:
            lines.append(f"- Scope note: {scope_note}")
        if corpus_change.get("largest_negative_reconciliation_gap_provider"):
            lines.append(
                f"- Largest negative reconciliation gap: `{corpus_change.get('largest_negative_reconciliation_gap_provider')}`"
            )
        if corpus_change.get("largest_positive_reconciliation_gap_provider"):
            lines.append(
                f"- Largest positive reconciliation gap: `{corpus_change.get('largest_positive_reconciliation_gap_provider')}`"
            )
        lines.append("")
    elif corpus_status == "no_prior_audit":
        lines.append("## Corpus change since previous audit")
        lines.append("- No prior tracked provider audit artifact was available, so snapshot-to-snapshot corpus comparison is not yet available.")
        lines.append("")

    def emit_rows(title: str, rows: list[dict], key: str) -> None:
        lines.append(f"### {title}")
        if not rows:
            lines.append("- none")
            lines.append("")
            return
        for row in rows:
            lines.append(f"- `{row[key]}` — {row['count']}")
        lines.append("")

    def emit_remediation_hints(title: str, hints: list[dict]) -> None:
        lines.append(f"### {title}")
        if not hints:
            lines.append("- none")
            lines.append("")
            return
        for hint in hints:
            matched = ", ".join(f"`{row['path']}` ({row['count']})" for row in hint.get("matched_paths", []))
            targets = ", ".join(f"`{target}`" for target in hint.get("canonical_targets", []))
            lines.append(f"- {matched} — {hint.get('total_count', 0)} combined reads")
            lines.append(f"  - Redirect to: {targets}")
            lines.append(f"  - Guidance: {hint.get('guidance', '')}")
            lines.append(f"  - Reference: `{hint.get('reference_doc', '')}`")
        lines.append("")

    for provider, summary in audit["providers"].items():
        lines.append(f"## {provider}")
        lines.append(f"- Source: {summary.get('source')}" )
        lines.append(f"- Sessions: {summary.get('sessions', 0)}")
        lines.append(f"- Post-hook records: {summary.get('post_records', 0)}")
        if "correction_sessions" in summary:
            lines.append(f"- Correction sessions: {summary.get('correction_sessions', 0)}")
        if "unique_runtime_sessions" in summary:
            lines.append(f"- Unique runtime sessions: {summary.get('unique_runtime_sessions', 0)}")
        if "prompt_reads" in summary:
            lines.append(f"- Prompt-like reads: {summary.get('prompt_reads', 0)}")
        if "blank_reads" in summary:
            lines.append(f"- Blank read targets: {summary.get('blank_reads', 0)}")
        if "missing_repo_reads" in summary:
            lines.append(f"- Missing repo reads: {summary.get('missing_repo_reads', 0)}")
        if "missing_external_reads" in summary:
            lines.append(f"- Missing external reads: {summary.get('missing_external_reads', 0)}")
        lines.append(f"- Bare python3 bash calls: {summary.get('python3_bash_calls', 0)}")
        lines.append(f"- `uv run ... python` bash calls: {summary.get('uv_python_bash_calls', 0)}")
        if summary.get("limitations"):
            for limitation in summary["limitations"]:
                lines.append(f"- Limitation: {limitation}")
        lines.append("")
        emit_rows(f"{provider} top tools", summary.get("top_tools", []), "tool")
        emit_rows(f"{provider} top repos", summary.get("top_repos", []), "repo")
        emit_rows(f"{provider} top reads", summary.get("top_reads", []), "path")
        emit_rows(f"{provider} top symbolic reads", summary.get("top_symbolic_reads", []), "name")
        emit_rows(f"{provider} top sibling-repo reads", summary.get("top_sibling_repo_reads", []), "path")
        emit_rows(f"{provider} top non-repo artifact reads", summary.get("top_non_repo_artifact_reads", []), "path")
        emit_rows(f"{provider} top Bash command families", summary.get("top_bash_command_families", []), "prefix")
        recent_provider = recent_activity.get("providers", {}).get(provider, {}) if recent_status == "ok" else {}
        if recent_provider:
            lines.append(f"### {provider} recent activity since previous audit")
            lines.append(f"- Post-hook records since prior audit: {recent_provider.get('post_records', 0)}")
            lines.append(f"- Runtime sessions since prior audit: {recent_provider.get('sessions', 0)}")
            limitations = recent_provider.get("limitations", [])
            for limitation in limitations:
                lines.append(f"- Limitation: {limitation}")
            lines.append("")
            emit_rows(f"{provider} recent top tools", recent_provider.get("top_tools", []), "tool")
            emit_rows(f"{provider} recent top reads", recent_provider.get("top_reads", []), "path")
            emit_rows(f"{provider} recent top writes", recent_provider.get("top_writes", []), "path")
            emit_rows(f"{provider} recent top edits", recent_provider.get("top_edits", []), "path")
            emit_rows(
                f"{provider} recent top Bash command families",
                recent_provider.get("top_bash_command_families", []),
                "prefix",
            )
            emit_rows(
                f"{provider} recent top missing repo reads",
                recent_provider.get("top_missing_repo_reads", []),
                "path",
            )
            emit_rows(
                f"{provider} recent top sibling-repo reads",
                recent_provider.get("top_sibling_repo_reads", []),
                "path",
            )
            emit_rows(
                f"{provider} recent top non-repo artifact reads",
                recent_provider.get("top_non_repo_artifact_reads", []),
                "path",
            )
        corpus_provider = corpus_change.get("providers", {}).get(provider, {}) if corpus_status == "ok" else {}
        if corpus_provider:
            lines.append(f"### {provider} corpus change since previous audit")
            lines.append(
                f"- Post-hook records: current {corpus_provider.get('current_post_records', 0)} vs previous {corpus_provider.get('previous_post_records', 0)} (delta {corpus_provider.get('post_record_delta', 0)})"
            )
            lines.append(
                f"- Sessions: current {corpus_provider.get('current_sessions', 0)} vs previous {corpus_provider.get('previous_sessions', 0)} (delta {corpus_provider.get('session_delta', 0)})"
            )
            lines.append(
                f"- Missing repo reads: current {corpus_provider.get('current_missing_repo_reads', 0)} vs previous {corpus_provider.get('previous_missing_repo_reads', 0)} (delta {corpus_provider.get('missing_repo_read_delta', 0)})"
            )
            lines.append(
                f"- Event-time post records since prior audit: {corpus_provider.get('event_time_post_records_since_previous_audit', 0)}"
            )
            lines.append(
                f"- Reconciliation gap vs event-time delta: {corpus_provider.get('reconciliation_gap_post_records', 0)}"
            )
            lines.append(f"- Status: {corpus_provider.get('status', 'unknown')}")
            lines.append(f"- Interpretation: {corpus_provider.get('interpretation', '')}")
            lines.append("")
        emit_rows(f"{provider} top missing repo reads", summary.get("top_missing_repo_reads", []), "path")
        emit_rows(f"{provider} top sibling-repo reads", summary.get("top_sibling_repo_reads", []), "path")
        emit_rows(f"{provider} top non-repo artifact reads", summary.get("top_non_repo_artifact_reads", []), "path")
        emit_remediation_hints(
            f"{provider} remediation hints for stale repo reads",
            summary.get("missing_repo_read_remediation_hints", []),
        )
        emit_rows(f"{provider} top missing external reads", summary.get("top_missing_external_reads", []), "path")

    lines += [
        "## Ecosystem strengthening recommendations",
        "1. Keep exporting every provider into `logs/orchestrator/<provider>/session_*.jsonl` before the audit so the recent-delta section stays trustworthy.",
        "2. Treat symbolic skill/tool reads separately from filesystem reads. Hermes emits many skill names in `file`, and counting them as missing files creates noisy false positives.",
        "3. Preserve Codex command-shape fidelity in both export and audit layers. Recent native sessions use a mix of spaced-encoded commands and ordinary shell strings.",
        "4. Use the recent-activity section to prioritize follow-up review on providers with actual post-audit event-time work instead of re-reading the full historical corpus every time. Recent read/write/edit hotspots should drive the next docs/tests hardening pass.",
        "5. Keep pushing `uv run ... python` migration. Hermes, Gemini, and Codex still show meaningful bare `python3` usage density.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit provider session logs and saved provider artifacts.")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--stdout", action="store_true", help="Print markdown to stdout instead of only writing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_provider_audit()
    markdown = render_markdown(audit)

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown + "\n", encoding="utf-8")

    if args.stdout:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
