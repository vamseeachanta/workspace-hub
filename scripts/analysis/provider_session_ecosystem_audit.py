#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
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
WORKSTATION_RESOLVER = WorkstationPathResolver.for_repo(REPO_ROOT)

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

    if TILDE_PATH_RE.match(text):
        expanded = Path(text).expanduser()
        return expanded.as_posix(), "external", safe_exists(expanded)

    if "/" not in text and "\\" not in text and not text.startswith("~"):
        if SYMBOLIC_NAME_RE.fullmatch(text):
            return text, "symbolic", False

    if SYMBOLIC_SLASH_NAME_RE.fullmatch(text):
        candidate = repo_root / text
        if not safe_exists(candidate):
            return text, "symbolic", False

    path = Path(text)
    if path.is_absolute():
        try:
            rel = path.relative_to(repo_root)
            return rel.as_posix(), "repo", safe_exists(path)
        except ValueError:
            return text, "external", safe_exists(path)

    candidate = repo_root / text
    return text, "repo", safe_exists(candidate)


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


def top_items(counter: Counter, limit: int, key_name: str) -> list[dict]:
    return [{key_name: key, "count": value} for key, value in counter.most_common(limit)]


def summarize_raw_provider(provider: str, logs_dir: Path, repo_root: Path) -> dict:
    sessions = sorted(logs_dir.glob("session_*.jsonl"))
    corrections_dir = logs_dir / "corrections"
    correction_sessions = sorted(corrections_dir.glob("session_*.jsonl")) if corrections_dir.exists() else []

    post_records = 0
    tool_counts: Counter[str] = Counter()
    repo_counts: Counter[str] = Counter()
    read_counts: Counter[str] = Counter()
    missing_repo_reads: Counter[str] = Counter()
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



def build_provider_audit(repo_root: Path = REPO_ROOT, logs_root: Path = LOGS_ROOT) -> dict:
    provider_summaries: dict[str, dict] = {}

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

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_root": str(repo_root),
        "logs_root": str(logs_root),
        "providers": provider_summaries,
        "executive_summary": {"migration_debt": build_migration_debt_summary(provider_summaries)},
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
        emit_rows(f"{provider} top Bash command families", summary.get("top_bash_command_families", []), "prefix")
        emit_rows(f"{provider} top missing repo reads", summary.get("top_missing_repo_reads", []), "path")
        emit_remediation_hints(
            f"{provider} remediation hints for stale repo reads",
            summary.get("missing_repo_read_remediation_hints", []),
        )
        emit_rows(f"{provider} top missing external reads", summary.get("top_missing_external_reads", []), "path")

    lines += [
        "## Ecosystem strengthening recommendations",
        "1. Record every provider into `logs/orchestrator/<provider>/session_*.jsonl`; Gemini currently has no corpus, which blocks parity analysis.",
        "2. Treat symbolic skill/tool reads separately from filesystem reads. Hermes emits many skill names in `file`, and counting them as missing files creates noisy false positives.",
        "3. Normalize Codex command logging before analysis. Its spaced command encoding hides policy violations unless commands are de-spaced first.",
        "4. Add a recurring provider audit run that refreshes both JSON and markdown artifacts so refactors can prove drift is shrinking.",
        "5. Keep pushing `uv run ... python` migration. Hermes and Codex still show meaningful bare `python3` usage density.",
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
