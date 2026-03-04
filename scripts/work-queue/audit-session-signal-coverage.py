#!/usr/bin/env python3
"""Audit whether required workflow signals are measured in session analysis."""

from __future__ import annotations

import json
from pathlib import Path


REQUIRED_SIGNALS: list[dict[str, object]] = [
    {"name": "wrk_created", "stage": "1 Capture", "required": True},
    {"name": "resource_intelligence", "stage": "2 Resource Intelligence", "required": True},
    {"name": "triage_contract_complete", "stage": "3 Triage", "required": True},
    {"name": "plan_draft_complete", "stage": "4 Plan Draft", "required": True},
    {"name": "plan_html_review_draft", "stage": "5 User Review - Plan (Draft)", "required": True},
    {"name": "html_open_default_browser", "stage": "5/7/17 User Reviews", "required": True},
    {"name": "cross_review", "stage": "6 Cross-Review", "required": True},
    {"name": "plan_html_review_final", "stage": "7 User Review - Plan (Final)", "required": True},
    {"name": "claim_evidence", "stage": "8 Claim / Activation", "required": True},
    {"name": "set_active_wrk", "stage": "8 Claim / Activation", "required": True},
    {"name": "work_queue_skill", "stage": "9 Work-Queue Routing", "required": True},
    {"name": "work_execution", "stage": "10 Work Execution", "required": True},
    {"name": "artifact_generation", "stage": "11 Artifact Generation", "required": True},
    {"name": "tdd_eval", "stage": "12 TDD / Eval", "required": True},
    {"name": "agent_cross_review", "stage": "13 Agent Cross-Review", "required": True},
    {"name": "verify_gate_evidence", "stage": "14 Verify Gate Evidence", "required": True},
    {"name": "future_work", "stage": "15 Future Work Synthesis", "required": True},
    {"name": "resource_intelligence_update", "stage": "16 Resource Intelligence Update", "required": True},
    {"name": "user_review_close", "stage": "17 User Review - Implementation", "required": True},
    {"name": "reclaim", "stage": "18 Reclaim", "required": False},
    {"name": "close_item", "stage": "19 Close", "required": True},
    {"name": "archive_item", "stage": "20 Archive", "required": True},
    {"name": "close_or_archive", "stage": "19/20 Terminal", "required": True},
    {"name": "init", "stage": "Session bootstrap", "required": True},
]


def _session_infers_signal(session: dict, signal: str) -> bool:
    gates = session.get("gate_signals") or {}
    scripts = set(session.get("scripts") or [])
    skills = set(session.get("skills") or [])
    path = str(session.get("path") or "")

    if signal in gates:
        return bool(gates.get(signal))
    if signal == "work_queue_skill":
        return "work" in skills or "scripts/agents/work.sh" in scripts
    if signal == "work_execution":
        return "scripts/agents/execute.sh" in scripts
    if signal == "artifact_generation":
        return (
            "scripts/work-queue/generate-html-review.py" in scripts
            or "scripts/review/render-structured-review.py" in scripts
        )
    if signal == "tdd_eval":
        return any(x in path for x in ("pytest", "test-results")) or any("pytest" in s for s in scripts)
    if signal == "plan_draft_complete":
        return "scripts/agents/plan.sh" in scripts
    if signal == "agent_cross_review":
        return (
            "scripts/review/cross-review.sh" in scripts
            or "scripts/review/submit-to-codex.sh" in scripts
            or "scripts/review/submit-to-gemini.sh" in scripts
        )
    if signal == "close_item":
        return "scripts/work-queue/close-item.sh" in scripts
    if signal == "archive_item":
        return "scripts/work-queue/archive-item.sh" in scripts
    # The remaining signals are not inferable from current session-gate schema.
    return False


def build_report(data: dict) -> dict:
    sessions = data.get("sessions") or []
    aggregate = data.get("aggregate") or {}
    measured_keys = set((aggregate.get("gate_relaxed") or {}).keys()) | set((aggregate.get("gate_strict") or {}).keys())

    rows = []
    for rule in REQUIRED_SIGNALS:
        signal = str(rule["name"])
        relaxed_hits = 0
        strict_hits = 0
        relaxed_total = 0
        strict_total = 0
        for session in sessions:
            inferred = _session_infers_signal(session, signal)
            if session.get("strict"):
                strict_total += 1
                strict_hits += 1 if inferred else 0
            if session.get("relaxed"):
                relaxed_total += 1
                relaxed_hits += 1 if inferred else 0
        rows.append(
            {
                "signal": signal,
                "stage": str(rule["stage"]),
                "required": bool(rule["required"]),
                "currently_measured": signal in measured_keys,
                "relaxed_inferred": f"{relaxed_hits}/{relaxed_total}" if relaxed_total else "0/0",
                "strict_inferred": f"{strict_hits}/{strict_total}" if strict_total else "0/0",
            }
        )

    required_missing = [r["signal"] for r in rows if r["required"] and not r["currently_measured"]]
    return {
        "required_signals": len([s for s in REQUIRED_SIGNALS if bool(s["required"])]),
        "measured_required_signals": len([r for r in rows if r["required"] and r["currently_measured"]]),
        "missing_required_signals": required_missing,
        "rows": rows,
    }


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# Session Signal Coverage Audit",
        "",
        f"- Required signals: {report['required_signals']}",
        f"- Required currently measured: {report['measured_required_signals']}",
        "",
        "| Signal | Stage | Required | Currently measured | Relaxed (inferred) | Strict (inferred) |",
        "|---|---|---|---|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['signal']} | {row['stage']} | {'Yes' if row['required'] else 'Conditional'} | "
            f"{'Yes' if row['currently_measured'] else 'No'} | {row['relaxed_inferred']} | {row['strict_inferred']} |"
        )
    if report["missing_required_signals"]:
        lines.extend(
            [
                "",
                "## Missing Required Signals",
                "",
                *[f"- `{sig}`" for sig in report["missing_required_signals"]],
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    workspace_root = Path(__file__).resolve().parents[2]
    src = workspace_root / ".claude/work-queue/assets/WRK-690/evidence/session-gate-analysis.json"
    if not src.exists():
        raise FileNotFoundError(f"missing input: {src}")
    data = json.loads(src.read_text(encoding="utf-8"))
    report = build_report(data)

    out_json = workspace_root / ".claude/work-queue/assets/WRK-690/evidence/session-signal-coverage-audit.json"
    out_md = workspace_root / ".claude/work-queue/assets/WRK-690/evidence/session-signal-coverage-audit.md"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(out_md, report)

    # Keep canonical parent followup mirror in sync.
    mirror_root = workspace_root / ".claude/work-queue/assets/WRK-624/followups/WRK-690/evidence"
    mirror_root.mkdir(parents=True, exist_ok=True)
    (mirror_root / out_json.name).write_text(out_json.read_text(encoding="utf-8"), encoding="utf-8")
    (mirror_root / out_md.name).write_text(out_md.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_md}")
    print(f"Measured required signals: {report['measured_required_signals']}/{report['required_signals']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
