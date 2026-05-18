#!/usr/bin/env python3
"""Build the OrcaWave + OrcaFlex Hermes kanban (HTML + JSON).

Sister to scripts/ai/provider-kanban.py. Mirrors the lane vocabulary used by
docs/dashboards/2026-05-09-tier1-gh-issue-kanban.html so the marine-domain
view folds cleanly into the broader Tier-1 kanban.

Usage:
    uv run --no-project python scripts/ai/build-orca-kanban.py

Inputs:
    Live `gh issue list` queries (paginated to 200 per query, 3 queries to
    cover orcaflex-title, orcawave-title, body-mention).

Outputs:
    docs/reports/YYYY-MM-DD-orca-kanban-data.json   — Hermes-readable data
    docs/dashboards/YYYY-MM-DD-orca-kanban.html     — self-contained HTML

Lane assignment rules (mirrors tier1 kanban):
    - status:plan-approved + has approval marker  -> Ready / Plan Approved
    - status:plan-approved without marker         -> Approved Label Drift
    - status:plan-review                          -> Plan Review / Needs Approval
    - status:working                              -> In Progress / Status Working
    - status:blocked                              -> Blocked / Waiting
    - state CLOSED                                -> Done (with completion note)
    - state OPEN, no status:* label               -> Triage Needed (un-labeled)

Domain assignment:
    - title contains both 'orcaflex' AND 'orcawave' -> BOTH (shows in both boards)
    - title contains 'orcaflex' only                -> OF
    - title contains 'orcawave' only                -> OW
    - body-only mention + marine label              -> categorized by which keyword wins
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE_HUB = Path(__file__).resolve().parents[2]
DIGITALMODEL_ROOT = WORKSPACE_HUB / "digitalmodel"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
DATA_PATH = WORKSPACE_HUB / "docs" / "reports" / f"{TODAY}-orca-kanban-data.json"
HTML_PATH = WORKSPACE_HUB / "docs" / "dashboards" / f"{TODAY}-orca-kanban.html"

LANES = [
    "Ready / Plan Approved",
    "Plan Review / Needs Approval",
    "In Progress / Status Working",
    "Approved Label Drift",
    "Triage Needed (no status label)",
    "Blocked / Waiting",
    "Done",
]


def gh_search(query: str) -> list[dict]:
    """Run `gh issue list --search` with full field set."""
    cmd = [
        "gh", "issue", "list",
        "--repo", "vamseeachanta/workspace-hub",
        "--search", query,
        "--state", "all",
        "--limit", "200",
        "--json", "number,title,state,labels,updatedAt,createdAt,closedAt,url,assignees",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def collect_issues() -> list[dict]:
    """Three-pass dedupe: orcaflex-title, orcawave-title, body-mentions filtered."""
    seen: dict[int, dict] = {}
    for q in ("orcaflex in:title", "orcawave in:title", "orcaflex OR orcawave in:body"):
        for issue in gh_search(q):
            seen.setdefault(issue["number"], issue)

    out = []
    for issue in seen.values():
        title_l = issue["title"].lower()
        has_ow = "orcawave" in title_l
        has_of = "orcaflex" in title_l
        labels = [l["name"] for l in issue.get("labels", [])]

        if has_ow and has_of:
            domain = "BOTH"
        elif has_ow:
            domain = "OW"
        elif has_of:
            domain = "OF"
        else:
            # body-only — keep only if marine-engineering relevant
            marine_lbls = {"domain:marine", "cat:engineering", "module:orcaflex", "module:orcawave"}
            if not (marine_lbls & set(labels)) and not any(
                k in title_l for k in ("mooring", "riser", "diffraction", "hydrostatic",
                                       "rao", "qtf", "panel", "vessel", "wave", "hydro")
            ):
                continue
            domain = "BODY-MARINE"

        issue["_domain"] = domain
        issue["_labels"] = labels
        issue["_status"] = next((l for l in labels if l.startswith("status:")), None)
        issue["_priority"] = next((l for l in labels if l.startswith("priority:")), None)
        out.append(issue)
    return out


def has_approval_marker(num: int) -> bool:
    return (WORKSPACE_HUB / ".planning" / "plan-approved" / f"{num}.md").exists()


def assign_lane(issue: dict) -> str:
    if issue["state"] == "CLOSED":
        return "Done"
    s = issue["_status"]
    labels = set(issue["_labels"])
    if s == "status:plan-approved":
        return "Ready / Plan Approved" if has_approval_marker(issue["number"]) else "Approved Label Drift"
    if s == "status:plan-review":
        return "Plan Review / Needs Approval"
    if s == "status:working":
        return "In Progress / Status Working"
    if s == "status:blocked" or "blocked" in labels:
        return "Blocked / Waiting"
    return "Triage Needed (no status label)"


def spot_check_done_claims(issues: list[dict]) -> dict:
    """For CLOSED issues whose title mentions a code module name, verify the module exists.

    Catches "claimed-done but reverted/never-landed" defect class.
    Returns a small audit report; not exhaustive — sample is the point.
    """
    of_modules = {p.stem for p in (DIGITALMODEL_ROOT / "src" / "digitalmodel" / "orcaflex").glob("*.py")}
    ow_modules = {p.stem for p in (DIGITALMODEL_ROOT / "src" / "digitalmodel" / "orcawave").glob("*.py")}

    claims_with_module = []
    for issue in issues:
        if issue["state"] != "CLOSED":
            continue
        title_l = issue["title"].lower()
        for mod in of_modules | ow_modules:
            if mod in title_l and len(mod) > 3:  # avoid false hits on tiny module names
                in_of = mod in of_modules
                module_path = (
                    DIGITALMODEL_ROOT / "src" / "digitalmodel" / ("orcaflex" if in_of else "orcawave") / f"{mod}.py"
                )
                claims_with_module.append({
                    "issue": issue["number"],
                    "title": issue["title"],
                    "module": mod,
                    "module_exists": module_path.exists(),
                    "module_path": str(module_path.relative_to(DIGITALMODEL_ROOT.parent)),
                })
                break

    return {
        "samples_checked": len(claims_with_module),
        "all_landed": all(c["module_exists"] for c in claims_with_module),
        "missing": [c for c in claims_with_module if not c["module_exists"]],
        "samples": claims_with_module,
    }


def build_data(issues: list[dict]) -> dict:
    by_lane = {lane: {"OW": [], "OF": []} for lane in LANES}

    def card(issue: dict) -> dict:
        return {
            "number": issue["number"],
            "title": issue["title"],
            "state": issue["state"],
            "labels": issue["_labels"],
            "status": issue["_status"],
            "priority": issue["_priority"],
            "url": issue["url"],
            "updated": issue["updatedAt"],
            "closed": issue.get("closedAt"),
            "domain": issue["_domain"],
        }

    for issue in issues:
        lane = assign_lane(issue)
        c = card(issue)
        if issue["_domain"] in ("OW", "BOTH"):
            by_lane[lane]["OW"].append(c)
        if issue["_domain"] in ("OF", "BOTH", "BODY-MARINE"):
            by_lane[lane]["OF"].append(c)

    spot = spot_check_done_claims(issues)

    counts = {
        "ow_total": sum(len(by_lane[l]["OW"]) for l in LANES),
        "of_total": sum(len(by_lane[l]["OF"]) for l in LANES),
        "ow_open": sum(len([c for c in by_lane[l]["OW"] if c["state"] == "OPEN"]) for l in LANES),
        "of_open": sum(len([c for c in by_lane[l]["OF"] if c["state"] == "OPEN"]) for l in LANES),
        "by_lane_ow": {l: len(by_lane[l]["OW"]) for l in LANES},
        "by_lane_of": {l: len(by_lane[l]["OF"]) for l in LANES},
    }

    way_forward = identify_way_forward(by_lane)

    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_repo": "vamseeachanta/workspace-hub",
        "code_repo_audited": str(DIGITALMODEL_ROOT),
        "lanes": LANES,
        "boards": {"OrcaWave": {l: by_lane[l]["OW"] for l in LANES},
                   "OrcaFlex":  {l: by_lane[l]["OF"] for l in LANES}},
        "counts": counts,
        "completion_audit": spot,
        "way_forward": way_forward,
        "methodology": (
            "Three-pass gh issue list (orcaflex-title, orcawave-title, body-marine) "
            "deduped by issue number. Body-only matches kept only if domain:marine / "
            "cat:engineering label or marine keyword in title. Lane assigned from "
            "status:* label + .planning/plan-approved/<n>.md marker presence. "
            "CLOSED issues whose title names a code module are spot-checked against "
            f"{DIGITALMODEL_ROOT}/src/ to catch revert/never-landed cases."
        ),
    }


def identify_way_forward(by_lane: dict) -> dict:
    """Pick the highest-leverage next actions per domain.

    Includes a "ripe-for-promotion" set drawn from Triage Needed: high-priority
    untriaged issues that should be the first targets of the bulk-label sweep.
    Without this surface, the kanban under-recommends action when marker drift
    is the dominant failure mode (which is exactly the current OF case).
    """
    def rank(card):
        prio = {"priority:high": 0, "priority:medium": 1, "priority:low": 2}.get(card["priority"], 3)
        return (prio, -int(card["updated"].split("T")[0].replace("-", "")))

    out = {}
    for board, code in (("OrcaWave", "OW"), ("OrcaFlex", "OF")):
        ready = sorted(by_lane["Ready / Plan Approved"][code], key=rank)
        review = sorted(by_lane["Plan Review / Needs Approval"][code], key=rank)
        drift = sorted(by_lane["Approved Label Drift"][code], key=rank)
        triage = sorted(by_lane["Triage Needed (no status label)"][code], key=rank)
        # Ripe = high-priority triage-needed; medium-priority if no high
        high_triage = [c for c in triage if c["priority"] == "priority:high"]
        ripe = high_triage[:5] if high_triage else triage[:5]
        out[board] = {
            "ready_to_execute": ready[:5],
            "needs_user_approval": review[:5],
            "needs_marker_repair": drift[:5],
            "ripe_for_promotion": ripe,
        }
    return out


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>OrcaWave + OrcaFlex Kanban — {date}</title>
<style>
body{{font-family:system-ui,Segoe UI,sans-serif;margin:20px;background:#0f172a;color:#e2e8f0}}
h1{{margin-top:0}} h2{{border-bottom:1px solid #334155;padding-bottom:6px}}
a{{color:#93c5fd;text-decoration:none}} a:hover{{text-decoration:underline}}
.note{{background:#1e293b;border-left:3px solid #38bdf8;padding:10px 14px;margin:12px 0;border-radius:4px}}
.boards{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px}}
.board{{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:14px}}
.lane{{margin:14px 0}}
.lane-h{{font-weight:600;color:#fbbf24;margin-bottom:6px;font-size:14px;text-transform:uppercase;letter-spacing:0.5px}}
.lane-h .ct{{color:#94a3b8;font-weight:400;font-size:12px;margin-left:6px}}
.card{{background:#0f172a;border:1px solid #334155;border-radius:6px;padding:8px 10px;margin:4px 0;font-size:13px}}
.card .num{{color:#fbbf24;font-weight:600}}
.card .title{{display:block;margin:2px 0}}
.card .pills{{margin-top:4px}}
.pill{{display:inline-block;background:#334155;border-radius:999px;padding:1px 7px;margin:1px 2px 1px 0;font-size:10px}}
.pill.high{{background:#7f1d1d;color:#fecaca}}
.pill.medium{{background:#78350f;color:#fed7aa}}
.pill.shared{{background:#1e3a8a;color:#bfdbfe}}
.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:14px 0}}
.stat{{background:#1e293b;border:1px solid #334155;border-radius:8px;padding:10px;text-align:center}}
.stat .n{{font-size:24px;font-weight:600;color:#fbbf24}}
.stat .l{{font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.4px}}
.warn{{background:#3b1d1d;border-left:3px solid #ef4444;padding:10px 14px;margin:12px 0;border-radius:4px}}
.ok{{background:#14342b;border-left:3px solid #10b981;padding:10px 14px;margin:12px 0;border-radius:4px}}
.way{{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:14px;margin:14px 0}}
.way h3{{margin-top:0;color:#fbbf24}}
ul{{margin:6px 0;padding-left:22px}}
li{{margin:4px 0;font-size:13px}}
code{{background:#0f172a;padding:1px 4px;border-radius:3px;font-size:12px}}
@media (max-width:900px){{.boards{{grid-template-columns:1fr}}}}
</style></head><body>

<h1>OrcaWave + OrcaFlex Kanban</h1>
<p>Generated <code>{generated}</code>. Source: <code>vamseeachanta/workspace-hub</code> issues.
Code-audit reference: <code>{digitalmodel_root}</code>. Lane vocabulary mirrors
<a href="2026-05-09-tier1-gh-issue-kanban.html">2026-05-09 Tier-1 kanban</a>.</p>

<div class="summary">
  <div class="stat"><div class="n">{ow_total}</div><div class="l">OrcaWave issues</div></div>
  <div class="stat"><div class="n">{ow_open}</div><div class="l">OrcaWave open</div></div>
  <div class="stat"><div class="n">{of_total}</div><div class="l">OrcaFlex issues</div></div>
  <div class="stat"><div class="n">{of_open}</div><div class="l">OrcaFlex open</div></div>
</div>

<div class="{audit_class}">
  <strong>Completion audit:</strong> {audit_msg}
</div>

<div class="warn">
  <strong>Governance gap:</strong> {triage_total} OPEN issues across both boards have NO <code>status:*</code> label
  ({triage_pct}% of open). They land in "Triage Needed" but represent unmanaged work — they cannot
  be picked up by Hermes <code>/goal</code> dispatch (which gates on <code>status:plan-approved</code> per
  <code>.claude/rules/goal-invocation.md</code>).
</div>

<div class="way"><h3>Way Forward — OrcaWave (a/)</h3>{way_ow}</div>
<div class="way"><h3>Way Forward — OrcaFlex (b/)</h3>{way_of}</div>

<div class="boards">
  <div class="board"><h2>OrcaWave</h2>{ow_lanes}</div>
  <div class="board"><h2>OrcaFlex</h2>{of_lanes}</div>
</div>

<div class="note">
  <strong>Methodology.</strong> {methodology}
</div>

<p style="color:#64748b;font-size:11px;margin-top:30px">
Regenerate: <code>uv run --no-project python scripts/ai/build-orca-kanban.py</code><br>
Data: <code>docs/reports/{date}-orca-kanban-data.json</code>
</p>
</body></html>
"""


def render_lane(cards: list[dict], lane: str) -> str:
    if not cards:
        return ""
    parts = [f'<div class="lane"><div class="lane-h">{lane} <span class="ct">{len(cards)}</span></div>']
    for c in sorted(cards, key=lambda x: (x["priority"] or "z", -int((x["updated"].split("T")[0]).replace("-", "")))):
        prio_pill = ""
        if c["priority"] == "priority:high":
            prio_pill = '<span class="pill high">P:high</span>'
        elif c["priority"] == "priority:medium":
            prio_pill = '<span class="pill medium">P:med</span>'
        shared = '<span class="pill shared">shared OW+OF</span>' if c["domain"] == "BOTH" else ""
        status = f'<span class="pill">{c["status"]}</span>' if c["status"] else ""
        parts.append(
            f'<div class="card"><a href="{c["url"]}" target="_blank">'
            f'<span class="num">#{c["number"]}</span></a> '
            f'<span class="title">{c["title"]}</span>'
            f'<div class="pills">{prio_pill}{status}{shared}</div></div>'
        )
    parts.append("</div>")
    return "".join(parts)


def render_way(picks: dict) -> str:
    out = []
    for label, key in (("Ready to execute", "ready_to_execute"),
                       ("Needs user approval (status:plan-review)", "needs_user_approval"),
                       ("Needs marker repair (label drift) — UNBLOCKS HERMES /goal", "needs_marker_repair"),
                       ("Ripe for promotion from Triage (high-priority untriaged)", "ripe_for_promotion")):
        items = picks[key]
        if not items:
            out.append(f"<p><strong>{label}:</strong> <em>none</em></p>")
            continue
        out.append(f"<p><strong>{label}:</strong></p><ul>")
        for c in items:
            out.append(f'<li><a href="{c["url"]}">#{c["number"]}</a> — {c["title"]}</li>')
        out.append("</ul>")
    return "".join(out)


def render_html(data: dict) -> str:
    audit = data["completion_audit"]
    if audit["samples_checked"] == 0:
        audit_class, audit_msg = "note", "No closed issues had a title-mentioned code module to spot-check."
    elif audit["all_landed"]:
        audit_class = "ok"
        audit_msg = (
            f"Spot-checked {audit['samples_checked']} closed issues whose titles named a code module — "
            f"all corresponding modules exist in <code>digitalmodel/src/</code>. "
            f"No silent reverts detected in this sample."
        )
    else:
        audit_class = "warn"
        missing_list = ", ".join(f"#{m['issue']} ({m['module']})" for m in audit["missing"])
        audit_msg = (
            f"Spot-checked {audit['samples_checked']} closed issues — "
            f"{len(audit['missing'])} reference modules that do NOT exist on disk: {missing_list}. "
            "Investigate before relying on closed-status as proof of completion."
        )

    triage_total = (data["counts"]["by_lane_ow"]["Triage Needed (no status label)"] +
                    data["counts"]["by_lane_of"]["Triage Needed (no status label)"])
    open_total = data["counts"]["ow_open"] + data["counts"]["of_open"]
    triage_pct = round(100 * triage_total / open_total) if open_total else 0

    ow_lanes = "".join(render_lane(data["boards"]["OrcaWave"][l], l) for l in LANES)
    of_lanes = "".join(render_lane(data["boards"]["OrcaFlex"][l], l) for l in LANES)

    return HTML_TEMPLATE.format(
        date=TODAY,
        generated=data["generated_utc"],
        ow_total=data["counts"]["ow_total"],
        ow_open=data["counts"]["ow_open"],
        of_total=data["counts"]["of_total"],
        of_open=data["counts"]["of_open"],
        audit_class=audit_class,
        audit_msg=audit_msg,
        triage_total=triage_total,
        triage_pct=triage_pct,
        way_ow=render_way(data["way_forward"]["OrcaWave"]),
        way_of=render_way(data["way_forward"]["OrcaFlex"]),
        ow_lanes=ow_lanes or "<p><em>No issues</em></p>",
        of_lanes=of_lanes or "<p><em>No issues</em></p>",
        methodology=data["methodology"],
        digitalmodel_root=str(DIGITALMODEL_ROOT),
    )


def main() -> int:
    print("Collecting issues from gh...", file=sys.stderr)
    issues = collect_issues()
    print(f"  collected {len(issues)} unique issues", file=sys.stderr)

    print("Classifying lanes + spot-checking completion...", file=sys.stderr)
    data = build_data(issues)

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, indent=2, sort_keys=True))
    HTML_PATH.write_text(render_html(data))

    print(f"\nWrote: {DATA_PATH.relative_to(WORKSPACE_HUB)}")
    print(f"Wrote: {HTML_PATH.relative_to(WORKSPACE_HUB)}")
    print(f"\nOrcaWave: {data['counts']['ow_total']} total ({data['counts']['ow_open']} open)")
    print(f"OrcaFlex: {data['counts']['of_total']} total ({data['counts']['of_open']} open)")
    print(f"\nLane distribution (OW / OF):")
    for lane in LANES:
        print(f"  {data['counts']['by_lane_ow'][lane]:3d} / {data['counts']['by_lane_of'][lane]:3d}  {lane}")
    print(f"\nCompletion audit: {data['completion_audit']['samples_checked']} samples, "
          f"all-landed={data['completion_audit']['all_landed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
