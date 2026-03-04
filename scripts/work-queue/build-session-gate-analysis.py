#!/usr/bin/env python3
"""Build weekly session-gate-analysis artifacts from native agent session stores."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


SCRIPT_RE = re.compile(r"scripts/[A-Za-z0-9_./-]+\.(?:sh|py)")
WRK_RE = re.compile(r"WRK-\d+")


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _infer_scripts(text: str) -> list[str]:
    return sorted(set(SCRIPT_RE.findall(text)))


def _infer_skills(text: str, scripts: list[str]) -> list[str]:
    skills: set[str] = set()
    if "/work" in text or "scripts/agents/work.sh" in scripts:
        skills.add("work")
    for m in re.finditer(r'"skill(?:_name)?"\s*:\s*"([A-Za-z0-9_-]+)"', text):
        skills.add(m.group(1))
    return sorted(skills)


def _infer_tools(text: str) -> list[list[object]]:
    tool_counter: Counter[str] = Counter()
    for m in re.finditer(r'"tool"\s*:\s*"([^"]+)"', text):
        tool_counter[m.group(1)] += 1
    for m in re.finditer(r'"recipient_name"\s*:\s*"([^"]+)"', text):
        tool_counter[m.group(1)] += 1
    return [[name, count] for name, count in tool_counter.most_common(20)]


def infer_gate_signals(text: str, scripts: list[str]) -> dict[str, bool]:
    wrk_count = len(set(WRK_RE.findall(text)))
    checks = {
        "wrk_created": ("WRK-",),
        "init": ("scripts/agents/session.sh", "session.sh init"),
        "set_active_wrk": ("scripts/work-queue/set-active-wrk.sh", "set_active_wrk"),
        "triage_contract_complete": ("scripts/work-queue/assign-workstations.py", "scripts/work-queue/assign-providers.sh"),
        "plan_draft_complete": ("scripts/agents/plan.sh", "plan_draft_complete", "plan-review-draft"),
        "plan_html_review_draft": ("plan_html_review_draft", "stage=plan_draft", "plan_draft"),
        "plan_html_review_final": ("plan_html_review_final", "stage=plan_final", "plan_final"),
        "html_open_default_browser": ("html_open_default_browser", "xdg-open"),
        "work_queue_skill": ("scripts/agents/work.sh", "/work"),
        "work_execution": ("scripts/agents/execute.sh", "work_execution"),
        "artifact_generation": ("scripts/work-queue/generate-html-review.py", "scripts/review/render-structured-review.py"),
        "tdd_eval": ("pytest", "test-results", "tdd_eval"),
        "agent_cross_review": ("agent_cross_review", "scripts/review/submit-to-codex.sh", "scripts/review/submit-to-gemini.sh"),
        "verify_gate_evidence": ("scripts/work-queue/verify-gate-evidence.py", "verify_gate_evidence"),
        "cross_review": (
            "scripts/review/cross-review.sh",
            "scripts/review/submit-to-codex.sh",
            "scripts/review/submit-to-claude.sh",
            "scripts/review/submit-to-gemini.sh",
        ),
        "claim_evidence": ("scripts/work-queue/claim-item.sh", "claim-evidence.yaml", "claim.yaml"),
        "future_work": ("future-work.yaml", "future_work"),
        "resource_intelligence": ("scripts/work-queue/create-resource-pack.sh", "resource-intelligence"),
        "resource_intelligence_update": ("resource_intelligence_update", "resource-intelligence-update.yaml"),
        "user_review_close": ("user_review_close", "user-review-close.yaml", "stage=close_review"),
        "reclaim": ("reclaim",),
        "close_item": ("scripts/work-queue/close-item.sh", "close_item"),
        "archive_item": ("scripts/work-queue/archive-item.sh", "archive_item"),
        "close_or_archive": ("scripts/work-queue/close-item.sh", "scripts/work-queue/archive-item.sh"),
    }
    scripts_set = set(scripts)
    signal_map: dict[str, bool] = {}
    text_lower = text.lower()
    for signal, patterns in checks.items():
        if signal == "wrk_created":
            found = wrk_count > 0
        else:
            found = any(p in scripts_set for p in patterns) or any(p.lower() in text_lower for p in patterns)
        signal_map[signal] = found
    return signal_map


def _strict_relaxed(gate_signals: dict[str, bool]) -> tuple[bool, bool]:
    strict = all(
        gate_signals.get(k, False)
        for k in ("init", "set_active_wrk", "verify_gate_evidence", "cross_review", "claim_evidence", "close_or_archive")
    )
    relaxed = all(gate_signals.get(k, False) for k in ("init", "cross_review", "claim_evidence", "close_or_archive"))
    return strict, relaxed


def summarize_session(path: Path, source: str) -> dict[str, object]:
    text = _safe_read(path)
    scripts = _infer_scripts(text)
    gate_signals = infer_gate_signals(text, scripts)
    strict, relaxed = _strict_relaxed(gate_signals)
    return {
        "source": source,
        "path": str(path),
        "relaxed": relaxed,
        "strict": strict,
        "scripts": scripts,
        "skills": _infer_skills(text, scripts),
        "tools_top": _infer_tools(text),
        "wrks_count": len(set(WRK_RE.findall(text))),
        "gate_signals": gate_signals,
    }


def _iter_codex_files(start: date, end: date) -> list[Path]:
    base = Path.home() / ".codex" / "sessions"
    files: list[Path] = []
    if not base.exists():
        return files
    day = start
    while day <= end:
        p = base / f"{day.year:04d}" / f"{day.month:02d}" / f"{day.day:02d}"
        if p.exists():
            files.extend(sorted(p.glob("rollout-*.jsonl")))
        day += timedelta(days=1)
    return files


def _iter_gemini_files(start: date, end: date) -> list[Path]:
    base = Path.home() / ".gemini" / "tmp"
    files: list[Path] = []
    if not base.exists():
        return files
    for path in base.glob("*/chats/session-*.json"):
        m = re.search(r"session-(\d{4}-\d{2}-\d{2})T", path.name)
        if not m:
            continue
        d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        if start <= d <= end:
            files.append(path)
    return sorted(files)


def _iter_claude_files(start: date, end: date) -> list[Path]:
    base = Path.home() / ".claude" / "projects"
    files: list[Path] = []
    if not base.exists():
        return files
    start_dt = datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc)
    end_dt = datetime.combine(end + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    for path in base.glob("*/*.jsonl"):
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        except Exception:
            continue
        if start_dt <= mtime < end_dt:
            files.append(path)
    return sorted(files)


def _top_counts(sessions: list[dict[str, object]], attr: str, limit: int = 20) -> list[list[object]]:
    c: Counter[str] = Counter()
    for sess in sessions:
        values = sess.get(attr) or []
        if attr in {"scripts", "skills"}:
            for v in set(values):
                c[v] += 1
        elif attr == "tools_top":
            for name, count in values:
                c[str(name)] += int(count)
    return [[k, v] for k, v in c.most_common(limit)]


def build_report(days: int, as_of: date | None = None) -> dict:
    end = as_of or datetime.now(timezone.utc).date()
    start = end - timedelta(days=days - 1)

    sessions: list[dict[str, object]] = []
    for p in _iter_claude_files(start, end):
        sessions.append(summarize_session(p, "claude-native"))
    for p in _iter_codex_files(start, end):
        sessions.append(summarize_session(p, "codex-native"))
    for p in _iter_gemini_files(start, end):
        sessions.append(summarize_session(p, "gemini-native"))

    relaxed_sessions = [s for s in sessions if bool(s.get("relaxed"))]
    strict_sessions = [s for s in sessions if bool(s.get("strict"))]

    gate_keys = [
        "wrk_created",
        "init",
        "triage_contract_complete",
        "plan_draft_complete",
        "plan_html_review_draft",
        "plan_html_review_final",
        "html_open_default_browser",
        "set_active_wrk",
        "work_queue_skill",
        "work_execution",
        "artifact_generation",
        "tdd_eval",
        "agent_cross_review",
        "verify_gate_evidence",
        "cross_review",
        "claim_evidence",
        "future_work",
        "resource_intelligence",
        "resource_intelligence_update",
        "user_review_close",
        "reclaim",
        "close_item",
        "archive_item",
        "close_or_archive",
    ]
    gate_relaxed = {k: sum(1 for s in relaxed_sessions if (s.get("gate_signals") or {}).get(k, False)) for k in gate_keys}
    gate_strict = {k: sum(1 for s in strict_sessions if (s.get("gate_signals") or {}).get(k, False)) for k in gate_keys}

    by_source: Counter[str] = Counter(str(s.get("source") or "unknown") for s in sessions)

    return {
        "aggregate": {
            "window": {"start": str(start), "end": str(end)},
            "counts": {
                "relaxed_sessions": len(relaxed_sessions),
                "strict_sessions": len(strict_sessions),
                "unique_sessions": len(sessions),
            },
            "by_source": dict(by_source),
            "gate_relaxed": gate_relaxed,
            "gate_strict": gate_strict,
            "scripts_relaxed": _top_counts(relaxed_sessions, "scripts"),
            "skills_relaxed": _top_counts(relaxed_sessions, "skills"),
            "tools_relaxed": _top_counts(relaxed_sessions, "tools_top"),
            "scripts_strict": _top_counts(strict_sessions, "scripts"),
            "skills_strict": _top_counts(strict_sessions, "skills"),
            "tools_strict": _top_counts(strict_sessions, "tools_top"),
        },
        "sessions": sessions,
    }


def _write_md(path: Path, report: dict) -> None:
    agg = report["aggregate"]
    lines = [
        "# Session Gate Analysis (strict + relaxed)",
        "",
        f"Window: {agg['window']['start']} to {agg['window']['end']}",
        f"- Relaxed sessions: {agg['counts']['relaxed_sessions']}",
        f"- Strict sessions: {agg['counts']['strict_sessions']}",
        f"- Sources: {agg['by_source']}",
        "",
        "## Gate signal coverage",
        "| Signal | Relaxed | Strict |",
        "|---|---:|---:|",
    ]
    relaxed_total = max(agg["counts"]["relaxed_sessions"], 1)
    strict_total = max(agg["counts"]["strict_sessions"], 1)
    legacy = [
        "init",
        "set_active_wrk",
        "verify_gate_evidence",
        "cross_review",
        "claim_evidence",
        "future_work",
        "resource_intelligence",
        "reclaim",
        "close_or_archive",
    ]
    for signal in legacy:
        count = agg["gate_relaxed"].get(signal, 0)
        lines.append(f"| {signal} | {count}/{relaxed_total} | {agg['gate_strict'].get(signal, 0)}/{strict_total} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build session-gate analysis from native agent stores.")
    parser.add_argument("wrk_id", help="WRK id, e.g. WRK-690")
    parser.add_argument("--days", type=int, default=7, help="Lookback window in days (default: 7)")
    args = parser.parse_args()

    wrk_id = args.wrk_id if args.wrk_id.startswith("WRK-") else f"WRK-{args.wrk_id}"
    report = build_report(args.days)

    workspace_root = Path(__file__).resolve().parents[2]
    out_dir = workspace_root / ".claude/work-queue/assets" / wrk_id / "evidence"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "session-gate-analysis.json"
    out_md = out_dir / "session-gate-analysis.md"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    _write_md(out_md, report)

    mirror_dir = workspace_root / ".claude/work-queue/assets/WRK-624/followups" / wrk_id / "evidence"
    mirror_dir.mkdir(parents=True, exist_ok=True)
    (mirror_dir / out_json.name).write_text(out_json.read_text(encoding="utf-8"), encoding="utf-8")
    (mirror_dir / out_md.name).write_text(out_md.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_md}")
    print(f"Sessions analyzed: {report['aggregate']['counts']['unique_sessions']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
