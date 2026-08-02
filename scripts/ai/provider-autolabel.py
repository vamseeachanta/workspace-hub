#!/usr/bin/env python3
"""Confidence-weighted GitHub agent auto-labeler.

Default behavior is dry-run: generate a candidate list and optional report.
Use --apply for conservative live labeling of only high-confidence issues.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE_HUB = Path(__file__).resolve().parents[2]


def _load_work_queue_module():
    """Load the sibling writer for its shared client-PII guard (#3768).

    The guard lives in exactly one place on purpose: three copies of a security
    control drift, and only one of them gets fixed.
    """
    path = Path(__file__).resolve().parent / "provider-work-queue.py"
    spec = importlib.util.spec_from_file_location("provider_work_queue_for_autolabel", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


_wq = _load_work_queue_module()
PiiGuard = _wq.PiiGuard
load_pii_guard = _wq.load_pii_guard
pii_banner = _wq.pii_banner
PII_WITHHELD = _wq.PII_WITHHELD
WORK_QUEUE_PATH = WORKSPACE_HUB / "config" / "ai-tools" / "provider-work-queue.json"
DEFAULT_JSON_OUT = WORKSPACE_HUB / "config" / "ai-tools" / "provider-autolabel-candidates.json"
DEFAULT_MD_OUT = WORKSPACE_HUB / "docs" / "reports" / "provider-autolabel-candidates.md"
CONFIDENCE_THRESHOLD = 0.90
PROVIDERS = ("claude", "codex", "agy")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def has_agent_label(issue: dict[str, Any]) -> bool:
    return any(label.startswith("agent:") for label in issue.get("labels", []))


def compute_confidence(provider: str, issue: dict[str, Any]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []
    if issue.get("execution_ready"):
        score += 0.35
        reasons.append("execution-ready")
    if issue.get("priority_rank") in (0, 1, 2):
        score += 0.15
        reasons.append("priority-labeled")
    routing_reason = str(issue.get("routing_reason", ""))
    if routing_reason == "implementation/test/fix language" and provider == "codex":
        score += 0.35
        reasons.append("strong-codex-language-match")
    elif routing_reason == "strategy/workflow/architecture language" and provider == "claude":
        score += 0.35
        reasons.append("strong-claude-language-match")
    elif routing_reason == "research/triage/audit language" and provider == "agy":
        score += 0.35
        reasons.append("strong-agy-language-match")
    elif routing_reason.startswith("existing "):
        score = 0.0
        reasons.append("already-labeled")
    else:
        score += 0.10
        reasons.append("weak-heuristic-match")

    provider_priority = str(issue.get("provider_priority", ""))
    if provider_priority == "highest":
        score += 0.10
        reasons.append("provider-highest-priority")
    elif provider_priority == "high":
        score += 0.05
        reasons.append("provider-high-priority")

    if has_agent_label(issue):
        score = 0.0
        reasons.append("agent-label-exists")

    return round(min(score, 1.0), 2), reasons


def collect_candidates(work_queue: dict[str, Any], guard: PiiGuard | None = None) -> list[dict[str, Any]]:
    guard = guard or load_pii_guard()
    candidates: list[dict[str, Any]] = []
    for provider in PROVIDERS:
        for issue in work_queue["provider_queues"][provider]["top_issues"]:
            confidence, reasons = compute_confidence(provider, issue)
            if has_agent_label(issue):
                continue
            candidates.append(
                {
                    **issue,
                    # Titles arrive from provider-work-queue.json already scrubbed;
                    # re-scrubbing is defence-in-depth against a stale upstream file
                    # and is a no-op because redaction is idempotent (#3768).
                    "title": guard.scrub(issue.get("title", "")),
                    "target_label": f"agent:{provider}",
                    "confidence": confidence,
                    "confidence_reasons": reasons,
                    "eligible": confidence >= CONFIDENCE_THRESHOLD,
                }
            )
    candidates.sort(key=lambda item: (-item["confidence"], item["priority_rank"], item["number"]))
    return candidates


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Provider autolabel candidates",
        "",
        f"Generated: {payload['generated_at']}",
        f"Apply mode: {payload['apply_mode']}",
        f"Threshold: {payload['threshold']}",
        "",
        pii_banner(payload),
        "",
        "| Issue | Target label | Confidence | Eligible | Reasons |",
        "|---|---|---:|---|---|",
    ]
    for item in payload["candidates"]:
        eligible = "yes" if item["eligible"] else "no"
        lines.append(
            f"| #{item['number']} {item['title']} | {item['target_label']} | {item['confidence']:.2f} | {eligible} | {', '.join(item['confidence_reasons'])} |"
        )
    return "\n".join(lines)


def gh_issue_edit_add_label(issue_number: int, label: str) -> None:
    subprocess.run(
        ["gh", "issue", "edit", str(issue_number), "--add-label", label],
        check=True,
        capture_output=True,
        text=True,
    )


def autolabel_json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Strip issue titles from the machine-readable candidate list (#3768).

    Verified by grep: nothing in the ecosystem reads a title out of
    provider-autolabel-candidates.json — the candidate list is keyed on
    `number` / `url` / `labels`. Where nothing reads the field, omission beats
    redaction: it removes the leak surface instead of narrowing it. The
    human-facing Markdown report renders from the in-memory payload, which
    keeps the redacted title.
    """
    stripped = dict(payload)
    stripped["candidates"] = [
        {key: value for key, value in candidate.items() if key != "title"}
        for candidate in payload.get("candidates", [])
    ]
    return stripped


def build_payload(
    work_queue: dict[str, Any], apply_mode: bool, limit: int, guard: PiiGuard | None = None
) -> dict[str, Any]:
    guard = guard or load_pii_guard()
    candidates = collect_candidates(work_queue, guard)
    eligible = [item for item in candidates if item["eligible"]]
    applied: list[dict[str, Any]] = []

    if apply_mode:
        for item in eligible[:limit]:
            gh_issue_edit_add_label(item["number"], item["target_label"])
            applied.append({
                "number": item["number"],
                "target_label": item["target_label"],
                "confidence": item["confidence"],
            })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "pii_redaction": guard.metadata(),
        "apply_mode": apply_mode,
        "threshold": CONFIDENCE_THRESHOLD,
        "eligible_count": len(eligible),
        "applied": applied,
        "candidates": candidates,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Confidence-weighted GitHub agent auto-labeler")
    parser.add_argument("--work-queue", default=str(WORK_QUEUE_PATH))
    parser.add_argument("--output-json", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--output-md", default=str(DEFAULT_MD_OUT))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--limit", type=int, default=3, help="max labels to apply in one run")
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--pii-map", default=None,
                        help="private client-codename map (default: $LEGAL_CLIENT_MAP, else "
                             "config/agents/.client-codename-map.local.yaml)")
    parser.add_argument("--require-pii-map", action="store_true",
                        help="fail instead of withholding free text when the map is unusable")
    args = parser.parse_args()

    guard = load_pii_guard(args.pii_map)
    if args.require_pii_map and not guard.available:
        raise SystemExit(
            f"provider-autolabel: client-codename map unusable ({guard.metadata()['reason']}) "
            f"and --require-pii-map was given; refusing to generate."
        )
    if not guard.available:
        print(f"WARNING: {guard.banner()}")

    work_queue = load_json(Path(args.work_queue))
    payload = build_payload(work_queue, apply_mode=args.apply, limit=args.limit, guard=guard)

    json_out = Path(args.output_json)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(autolabel_json_payload(payload), indent=2) + "\n", encoding="utf-8")
    print(f"JSON → {json_out}")

    if not args.json_only:
        md_out = Path(args.output_md)
        md_out.parent.mkdir(parents=True, exist_ok=True)
        md_out.write_text(render_markdown(payload) + "\n", encoding="utf-8")
        print(f"Markdown → {md_out}")

    if payload["applied"]:
        print("Applied labels:")
        for item in payload["applied"]:
            print(f"- #{item['number']} -> {item['target_label']} ({item['confidence']})")


if __name__ == "__main__":
    main()
