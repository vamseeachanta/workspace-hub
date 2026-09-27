#!/usr/bin/env python3
"""Provider-credit Kanban generator (#2665).

Builds a per-issue Kanban view consumed by:
  - the static dashboard at docs/reports/provider-kanban-dashboard.{md,html}
  - the local approval server (scripts/ai/provider-kanban-server.py)
  - the dispatch loop (scripts/ai/provider-dispatch-loop.py)

The generator REUSES existing primitives instead of re-classifying:
  - scripts/ai/provider-work-queue.py emits full_candidates per provider (#2665)
  - scripts/ai/continuous-planning-pipeline.py exposes build_snapshot() which
    classifies every issue into lanes A/B/C/D/E with review/marker readiness

If full_candidates is missing in provider-work-queue.json, generation fails
closed rather than silently consuming top_issues[:8] (a #2665 regression
hazard the plan explicitly forbids).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

WORKSPACE_HUB = Path(__file__).resolve().parents[2]
WORK_QUEUE_JSON = WORKSPACE_HUB / "config" / "ai-tools" / "provider-work-queue.json"
SCORECARD_JSON = WORKSPACE_HUB / "config" / "ai-tools" / "provider-routing-scorecard.json"
UTILIZATION_JSON = WORKSPACE_HUB / "config" / "ai-tools" / "provider-utilization-weekly.json"
DEFAULT_JSON_OUT = WORKSPACE_HUB / "config" / "ai-tools" / "provider-kanban.json"
DEFAULT_MD_OUT = WORKSPACE_HUB / "docs" / "reports" / "provider-kanban-dashboard.md"
DEFAULT_HTML_OUT = WORKSPACE_HUB / "docs" / "reports" / "provider-kanban-dashboard.html"

# Map continuous-planning-pipeline lanes onto Kanban lane names.
LANE_MAP = {
    "C": "planning_feedstock",
    "A": "plan_review",
    "B": "execution_ready",
    "D": "running_leased",
    "E": "qa_closeout",
}


class KanbanError(RuntimeError):
    pass


def _load_pipeline_module():
    """Import scripts/ai/continuous-planning-pipeline.py at runtime."""
    path = WORKSPACE_HUB / "scripts" / "ai" / "continuous-planning-pipeline.py"
    spec = importlib.util.spec_from_file_location("_cpp", path)
    if spec is None or spec.loader is None:
        raise KanbanError(f"could not load continuous-planning-pipeline from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_cpp"] = mod
    spec.loader.exec_module(mod)
    return mod


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require_full_candidates(work_queue: dict[str, Any]) -> None:
    """Fail closed if provider-work-queue.json lacks the non-truncated field.

    Acceptance criterion: dashboard cannot silently omit backlog because the
    readable view emits only top 8. (#2665)
    """
    for provider, bucket in work_queue.get("provider_queues", {}).items():
        if "full_candidates" not in bucket:
            raise KanbanError(
                f"provider-work-queue.json missing 'full_candidates' for {provider}; "
                f"regenerate with the post-#2665 provider-work-queue.py "
                f"(see acceptance criterion in docs/plans/2026-05-12-issue-2665-*.md)"
            )


def workstation_for_provider(provider: str, workstations: dict[str, Any]) -> dict[str, Any]:
    """Pick the first reachable, authed, repo-fresh workstation that supports provider.

    Falls back to a 'no-workstation' record with blocker reason if none qualify.
    """
    for ws in workstations.get("workstations", []):
        if provider not in ws.get("providers", []):
            continue
        if ws.get("reachable") and ws.get("auth_ok") and ws.get("repo_fresh"):
            return {"name": ws["name"], "role": ws.get("role", "worker"), "ready": True}
    # No ready workstation
    for ws in workstations.get("workstations", []):
        if provider not in ws.get("providers", []):
            continue
        reasons = []
        if not ws.get("reachable"):
            reasons.append("unreachable")
        if not ws.get("auth_ok"):
            reasons.append("auth_missing")
        if not ws.get("repo_fresh"):
            reasons.append("stale_repo")
        return {"name": ws["name"], "role": ws.get("role", "worker"), "ready": False, "blocker": ",".join(reasons) or "unknown"}
    return {"name": None, "role": None, "ready": False, "blocker": "no_provider_capable_workstation"}


def plan_summary_text(plan_path: Path) -> str:
    """Return the first non-header, non-blockquote line of the plan as a one-line summary."""
    if not plan_path.exists():
        return ""
    for raw_line in plan_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith(">") or line.startswith("---"):
            continue
        return line[:280]
    return ""


def plan_risks_text(plan_path: Path) -> str:
    """Return concatenated risk bullets from the plan's Risks section, if present."""
    if not plan_path.exists():
        return ""
    text = plan_path.read_text(encoding="utf-8")
    if "Risks and Open Questions" not in text and "## Risks" not in text:
        return ""
    section_start = max(text.find("Risks and Open Questions"), text.find("## Risks"))
    section = text[section_start : section_start + 2000]
    bullets = [line.strip("- ").strip() for line in section.splitlines() if line.strip().startswith("- ")]
    return " | ".join(bullets[:3])[:400]


def plan_tests_text(plan_path: Path) -> str:
    """Return a one-line summary of the plan's TDD test count."""
    if not plan_path.exists():
        return ""
    text = plan_path.read_text(encoding="utf-8")
    if "TDD Test List" not in text:
        return ""
    section = text.split("TDD Test List", 1)[1].split("\n## ", 1)[0]
    test_rows = [line for line in section.splitlines() if line.strip().startswith("| `test_")]
    return f"{len(test_rows)} TDD tests defined" if test_rows else "TDD section present"


def build_hover_summary(
    issue: dict[str, Any],
    classification: dict[str, Any],
    workstation: dict[str, Any],
    provider: str,
    root: Path,
) -> dict[str, Any]:
    """Construct a hover card from durable issue/plan/review/workstation data.

    NO transient LLM-only summaries — acceptance criterion #2665 explicitly
    forbids them as readiness inputs.
    """
    plan_rel = classification.get("plan")
    plan_path = root / plan_rel if plan_rel else None
    plan = plan_summary_text(plan_path) if plan_path else ""
    risks = plan_risks_text(plan_path) if plan_path else ""
    tests = plan_tests_text(plan_path) if plan_path else ""
    return {
        "title": issue.get("title", ""),
        "labels": [
            (lbl.get("name", "") if isinstance(lbl, dict) else str(lbl))
            for lbl in issue.get("labels", [])
        ],
        "plan_summary": plan or "(no plan file found)",
        "risks": risks or "(no risks section captured)",
        "tests": tests or "(no TDD section)",
        "provider_route": provider,
        "machine_route": workstation.get("name") or "(none ready)",
        "machine_readiness": "ready" if workstation.get("ready") else f"blocked:{workstation.get('blocker', 'unknown')}",
    }


def approval_ready(
    classification: dict[str, Any],
    issue: dict[str, Any],
    *,
    served_localhost: bool = False,
    user_intent_metadata: dict[str, Any] | None = None,
) -> tuple[bool, list[str]]:
    """Return (ready, blockers).

    Plan acceptance criterion: real approval-ready is true only when
      - live issue open
      - canonical plan exists
      - latest reviews clean (no MAJOR/FAIL/UNAVAILABLE/pending)
      - explicit user approval intent
      - issue-specific marker path ready (no pre-existing final marker)
      - current status:plan-review label
      - per-issue approval lock acquirable (left to approve-provider-plan.py)
      - served from localhost with explicit user-action metadata

    In static-HTML mode (served_localhost=False), this returns (False, [...]) so
    the approval button is disabled — committed HTML cannot safely mutate state.
    """
    blockers: list[str] = []
    state = str(issue.get("state", "")).upper()
    if state != "OPEN":
        blockers.append(f"issue not OPEN (state={state})")
    labels = [
        (lbl.get("name", "") if isinstance(lbl, dict) else str(lbl))
        for lbl in issue.get("labels", [])
    ]
    if "status:plan-review" not in labels:
        blockers.append("missing status:plan-review label")
    if "status:plan-approved" in labels:
        blockers.append("already has status:plan-approved")
    if not classification.get("plan"):
        blockers.append("no canonical plan file")
    if not classification.get("review_clean"):
        warnings = classification.get("warnings") or []
        blocking_warnings = [
            w for w in warnings if w in {
                "missing_review", "empty_review", "major_review",
                "unavailable_review", "sha_mismatch_review", "unknown_review",
            }
        ]
        if blocking_warnings:
            blockers.append(f"reviews not clean: {','.join(blocking_warnings)}")
        else:
            blockers.append("review evidence not clean")
    if classification.get("approval_marker"):
        blockers.append("issue already has approval marker on disk")
    if not served_localhost:
        blockers.append("static dashboard: real approval requires provider-kanban-server.py")
    if served_localhost and not (user_intent_metadata and user_intent_metadata.get("user_action_token")):
        blockers.append("local server present but no explicit user_action_token")
    return (len(blockers) == 0, blockers)


def build_kanban(
    *,
    work_queue: dict[str, Any],
    scorecard: dict[str, Any],
    utilization: dict[str, Any],
    workstations: dict[str, Any],
    issues: list[dict[str, Any]],
    root: Path = WORKSPACE_HUB,
    served_localhost: bool = False,
    user_intent_metadata: dict[str, Any] | None = None,
    pipeline_module=None,
) -> dict[str, Any]:
    """Assemble the Kanban JSON state.

    Reuses continuous-planning-pipeline.build_snapshot() for lane classification.
    """
    require_full_candidates(work_queue)
    cpp = pipeline_module or _load_pipeline_module()
    snapshot = cpp.build_snapshot(issues, root=root, generated_at=utc_now())
    classification_by_issue = {entry["number"]: entry for entry in snapshot["items"]}

    cards: list[dict[str, Any]] = []
    lanes: dict[str, list[dict[str, Any]]] = {name: [] for name in LANE_MAP.values()}
    lanes["blocked"] = []

    # Build issue → provider routing map from the FULL candidate set (not top_issues).
    issue_to_provider: dict[int, tuple[str, str]] = {}
    for provider, bucket in work_queue.get("provider_queues", {}).items():
        for item in bucket.get("full_candidates", []):
            issue_to_provider.setdefault(item["number"], (provider, item.get("routing_reason", "")))

    for issue in issues:
        number = int(issue["number"])
        cls = classification_by_issue.get(number, {"warnings": ["not_classified"], "lane": None})
        provider, reason = issue_to_provider.get(number, ("claude", "default"))
        ws = workstation_for_provider(provider, workstations)
        hover = build_hover_summary(issue, cls, ws, provider, root)
        ready, blockers = approval_ready(
            cls, issue,
            served_localhost=served_localhost,
            user_intent_metadata=user_intent_metadata,
        )
        kanban_lane = LANE_MAP.get(cls.get("lane"), "blocked")
        card = {
            "number": number,
            "title": issue.get("title", ""),
            "url": issue.get("url", ""),
            "lane": kanban_lane,
            "pipeline_lane": cls.get("lane"),
            "provider_route": provider,
            "routing_reason": reason,
            "machine_route": ws.get("name"),
            "machine_role": ws.get("role"),
            "machine_ready": ws.get("ready"),
            "machine_blocker": ws.get("blocker"),
            "approval_ready": ready,
            "approval_blockers": blockers,
            "review_clean": cls.get("review_clean"),
            "approval_marker": cls.get("approval_marker"),
            "plan": cls.get("plan"),
            "warnings": cls.get("warnings", []),
            "hover": hover,
        }
        cards.append(card)
        lanes[kanban_lane].append(card)

    return {
        "generated_at": snapshot.get("generated_at", utc_now()),
        "scorecard_generated_at": scorecard.get("generated_at"),
        "utilization_generated_at": utilization.get("generated_at") if isinstance(utilization, dict) else None,
        "recommended_provider_order": scorecard.get("recommended_provider_order", []),
        "served_localhost": served_localhost,
        "lanes": lanes,
        "cards": cards,
        "buffer_health": snapshot.get("buffer_health", {}),
        "warning_summary": snapshot.get("warning_summary", {}),
    }


def render_markdown(kanban: dict[str, Any]) -> str:
    lines = [
        "# Provider-credit Kanban dashboard",
        "",
        f"Generated: {kanban['generated_at']}",
        f"Mode: {'served-localhost' if kanban['served_localhost'] else 'static (read-only)'}",
        "",
        "## How to approve",
        "",
        "Static dashboard mode renders disabled approval controls. To actually approve a plan,",
        "run the local approval server:",
        "",
        "```sh",
        "uv run --no-project python scripts/ai/provider-kanban-server.py --port 7665",
        "# then open http://127.0.0.1:7665 and click Approve",
        "```",
        "",
        "Or invoke the CLI directly with explicit user identity (TTY required without a token):",
        "",
        "```sh",
        "uv run --no-project python scripts/ai/approve-provider-plan.py \\",
        "  --issue <N> --mode dry-run    # validate planned transaction",
        "uv run --no-project python scripts/ai/approve-provider-plan.py \\",
        "  --issue <N> --mode real \\",
        "  --user-identity <email> --approval-source 'cli' --confirmation-token <tty>",
        "```",
        "",
    ]
    for lane_name in ("plan_review", "execution_ready", "running_leased", "qa_closeout", "planning_feedstock", "blocked"):
        cards = kanban["lanes"].get(lane_name, [])
        lines.extend([f"## Lane: {lane_name} ({len(cards)})", ""])
        if not cards:
            lines.append("- (empty)")
            lines.append("")
            continue
        lines.append("| # | Title | Provider | Machine | Approval ready | Blockers |")
        lines.append("|---|---|---|---|---|---|")
        for card in cards:
            ready = "✓" if card["approval_ready"] else "✗"
            machine = card["machine_route"] or "—"
            if not card["machine_ready"]:
                machine = f"{machine} (blocked:{card['machine_blocker']})"
            blockers = "; ".join(card["approval_blockers"][:3])
            lines.append(
                f"| #{card['number']} | {card['title']} | {card['provider_route']} "
                f"| {machine} | {ready} | {blockers} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def render_html(kanban: dict[str, Any]) -> str:
    """Render a static, read-only HTML dashboard.

    Hard rules per #2665 acceptance criteria:
      - NO secrets in output
      - NO external fetch / no JS that mutates remote state
      - approval buttons are visibly DISABLED unless served_localhost is True
        AND a user_action_token is present (handled by provider-kanban-server.py)
      - copy/paste dry-run / approval commands are explicit and auditable
    """
    served = kanban.get("served_localhost", False)
    button_state = "" if served else "disabled"
    button_label = "Approve plan" if served else "Approve plan (disabled — see header)"
    sections: list[str] = []
    head_note = (
        "Served by provider-kanban-server.py on localhost. Approve buttons are wired."
        if served
        else "Static read-only mode. Approve buttons disabled; use the CLI commands below."
    )
    sections.append(
        f"<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>Provider-credit Kanban</title>"
        f"<style>"
        f"body{{font-family:system-ui,Segoe UI,sans-serif;margin:1.2rem;max-width:1400px}}"
        f".lane{{margin-bottom:1.6rem;padding:0.8rem;border:1px solid #ddd;border-radius:6px;background:#fbfbfb}}"
        f".lane h2{{margin-top:0;font-size:1.05rem;color:#333}}"
        f".card{{background:#fff;border:1px solid #ccc;padding:0.6rem;margin:0.4rem 0;border-radius:4px}}"
        f".hover{{font-size:0.85rem;color:#555;margin-top:0.3rem}}"
        f".blocker{{color:#b00;font-size:0.85rem}}"
        f".commands{{background:#f4f4f4;padding:0.6rem;border-radius:4px;font-family:monospace;white-space:pre-wrap;font-size:0.85rem}}"
        f"button[disabled]{{opacity:0.5;cursor:not-allowed}}"
        f"</style></head><body>"
    )
    sections.append(
        f"<h1>Provider-credit Kanban dashboard</h1>"
        f"<p>Generated: <code>{escape(kanban['generated_at'])}</code></p>"
        f"<p><strong>Mode:</strong> {escape(head_note)}</p>"
    )
    sections.append(
        f"<details><summary>Approval commands (CLI fallback)</summary>"
        f"<div class='commands'>"
        f"uv run --no-project python scripts/ai/approve-provider-plan.py --issue &lt;N&gt; --mode dry-run\n"
        f"uv run --no-project python scripts/ai/approve-provider-plan.py --issue &lt;N&gt; --mode real \\\n"
        f"  --user-identity &lt;you@example&gt; --approval-source 'cli'\n"
        f"</div></details>"
    )

    for lane_name in ("plan_review", "execution_ready", "running_leased", "qa_closeout", "planning_feedstock", "blocked"):
        cards = kanban["lanes"].get(lane_name, [])
        sections.append(
            f"<section class='lane'><h2>{escape(lane_name)} ({len(cards)})</h2>"
        )
        if not cards:
            sections.append("<p><em>(empty)</em></p></section>")
            continue
        for card in cards:
            ready_attr = "" if (card["approval_ready"] and served) else "disabled"
            sections.append(
                f"<div class='card'>"
                f"<strong>#{card['number']}</strong> "
                f"<a href='{escape(card['url'])}'>{escape(card['title'])}</a> "
                f"<small>[{escape(card['provider_route'])} → {escape(card['machine_route'] or 'no-machine')}]</small> "
                f"<button {ready_attr}>{escape(button_label if not card['approval_ready'] else 'Approve plan')}</button>"
            )
            hover = card["hover"]
            sections.append(
                f"<div class='hover'>"
                f"<div><strong>Plan:</strong> {escape(hover['plan_summary'])}</div>"
                f"<div><strong>Risks:</strong> {escape(hover['risks'])}</div>"
                f"<div><strong>Tests:</strong> {escape(hover['tests'])}</div>"
                f"<div><strong>Labels:</strong> {escape(', '.join(hover['labels']))}</div>"
                f"<div><strong>Machine:</strong> {escape(hover['machine_route'])} "
                f"({escape(hover['machine_readiness'])})</div>"
                f"</div>"
            )
            if card["approval_blockers"]:
                sections.append(
                    f"<div class='blocker'>Blockers: "
                    f"{escape('; '.join(card['approval_blockers']))}</div>"
                )
            sections.append("</div>")
        sections.append("</section>")

    sections.append("</body></html>")
    return "".join(sections)


def gh_issue_list_full() -> list[dict[str, Any]]:
    """Fetch full issue list with comments for Kanban classification."""
    import subprocess
    cmd = [
        "gh", "issue", "list", "--state", "open", "--limit", "200",
        "--json", "number,title,labels,updatedAt,body,url,state",
    ]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate provider-credit Kanban dashboard (#2665)")
    parser.add_argument("--work-queue-json", default=str(WORK_QUEUE_JSON))
    parser.add_argument("--scorecard-json", default=str(SCORECARD_JSON))
    parser.add_argument("--utilization-json", default=str(UTILIZATION_JSON))
    parser.add_argument("--workstations-json", help="Optional fixture; otherwise empty workstations list")
    parser.add_argument("--issues-json", help="Optional offline issue fixture")
    parser.add_argument("--output-json", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--output-md", default=str(DEFAULT_MD_OUT))
    parser.add_argument("--output-html", default=str(DEFAULT_HTML_OUT))
    parser.add_argument("--served-localhost", action="store_true",
                        help="Set when invoked by provider-kanban-server.py with user-action metadata")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    work_queue = load_json(Path(args.work_queue_json))
    scorecard = load_json(Path(args.scorecard_json))
    utilization = load_json(Path(args.utilization_json)) if Path(args.utilization_json).exists() else {}
    workstations = load_json(Path(args.workstations_json)) if args.workstations_json else {"workstations": []}
    issues = load_json(Path(args.issues_json)) if args.issues_json else gh_issue_list_full()

    kanban = build_kanban(
        work_queue=work_queue, scorecard=scorecard, utilization=utilization,
        workstations=workstations, issues=issues,
        served_localhost=args.served_localhost,
    )

    json_out = Path(args.output_json)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(kanban, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"JSON → {json_out}")

    md_out = Path(args.output_md)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text(render_markdown(kanban), encoding="utf-8")
    print(f"Markdown → {md_out}")

    html_out = Path(args.output_html)
    html_out.parent.mkdir(parents=True, exist_ok=True)
    html_out.write_text(render_html(kanban), encoding="utf-8")
    print(f"HTML → {html_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
