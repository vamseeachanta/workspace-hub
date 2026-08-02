#!/usr/bin/env python3
"""Generate a provider work queue from live GitHub issues + routing scorecard.

Also the home of the shared client-PII guard (#3768) used by the sibling
provider-artifact writers (provider-kanban.py, provider-autolabel.py). See the
`PiiGuard` docstring for why one implementation is deliberate.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE_HUB = Path(__file__).resolve().parents[2]
SCORECARD_PATH = WORKSPACE_HUB / "config" / "ai-tools" / "provider-routing-scorecard.json"
DEFAULT_JSON_OUT = WORKSPACE_HUB / "config" / "ai-tools" / "provider-work-queue.json"
DEFAULT_MD_OUT = WORKSPACE_HUB / "docs" / "reports" / "provider-work-queue.md"
PROVIDERS = ("claude", "codex", "agy")

# ── client-PII containment (#3768) ──────────────────────────────────────────
# workspace-hub is PUBLIC and these artifacts are regenerated 4-hourly by
# scripts/cron/provider-utilization-refresh.sh, then swept to `main` by
# `chore(sync): auto-sync` DIRECT PUSHES. The Client-PII Gate is
# `on: pull_request`, so it never sees this path — containment has to happen
# in the writer, at the moment the text is produced.
#
# Resolved independently of WORKSPACE_HUB so tests that repoint the repo root
# still find the real redaction engine.
REDACTOR_PATH = Path(__file__).resolve().parents[1] / "legal" / "redact-client-pii.py"
# Same sourcing precedence as scripts/legal/check-client-pii.py.
DEFAULT_PII_MAP = WORKSPACE_HUB / "config" / "agents" / ".client-codename-map.local.yaml"
PII_WITHHELD = "(withheld — client-codename map unavailable)"


def _load_redactor():
    """Import scripts/legal/redact-client-pii.py as the single matching engine.

    Reusing the redactor (rather than reimplementing matching) is what makes the
    writer and scripts/legal/check-client-pii.py incapable of disagreeing about
    what counts as a client identifier.
    """
    spec = importlib.util.spec_from_file_location("redact_client_pii", REDACTOR_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load redaction engine from {REDACTOR_PATH}")
    mod = importlib.util.module_from_spec(spec)
    # Register BEFORE exec: the engine uses @dataclass, which resolves its own
    # module out of sys.modules.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class PiiGuard:
    """Scrubs client identifiers out of free text before it lands in a public repo.

    Two modes, chosen by whether the private codename map is usable:

    * ``redacted``  — the map loaded; text is codename-redacted by the shared
      engine. Idempotent, so the 4-hourly regeneration does not churn diffs.
    * ``withheld``  — the map is missing (or PyYAML is unavailable under the
      cron's ``uv run --no-project``). Free text is replaced by
      :data:`PII_WITHHELD` rather than emitted raw.

    The withheld mode is the deliberate answer to "what if the map is absent on
    the cron host". Failing CLOSED would stop the refresh and silently freeze
    every dashboard; failing OPEN would reopen the leak this guard exists to
    close. Withholding keeps the refresh alive, cannot leak, and — because the
    mode is stamped into the JSON and printed as a banner in every rendered
    dashboard — the degradation is visible in the artifact itself.
    """

    def __init__(self, *, engine=None, rules=None, map_path: Path | None = None, reason: str = "ok"):
        self._engine = engine
        self._rules = rules
        self._map_path = map_path
        self._reason = reason

    @property
    def available(self) -> bool:
        return self._rules is not None and self._engine is not None

    def scrub(self, text: Any) -> str:
        """Return `text` with client identifiers removed. Empty stays empty."""
        value = "" if text is None else str(text)
        if not value:
            return value
        if not self.available:
            return PII_WITHHELD
        return self._engine.redact_text(value, self._rules)[0]

    def replacements(self) -> list[str]:
        """The codenames this guard substitutes (used to assert idempotency)."""
        return [rule.replacement for rule in (self._rules or [])]

    def metadata(self) -> dict[str, Any]:
        return {
            "mode": "redacted" if self.available else "withheld",
            "map_present": self.available,
            "map_path": str(self._map_path) if self._map_path else None,
            "reason": self._reason,
            "policy": (
                "Client identifiers are codename-redacted at write time (#3768). "
                "When the private map is unusable, free text is withheld rather "
                "than emitted raw; machine-readable fields (numbers, urls, labels) "
                "are never withheld."
            ),
        }

    def banner(self) -> str:
        """One-line, human-readable statement of the mode for .md/.html output."""
        if self.available:
            return "Client identifiers in issue titles and plan text are codename-redacted (#3768)."
        return (
            f"⚠ Client-codename map unavailable ({self._reason}) — issue titles and plan text "
            f"are {PII_WITHHELD} for this run. Provision the private map and re-run (#3768)."
        )


def load_pii_guard(map_path: str | Path | None = None) -> PiiGuard:
    """Build a :class:`PiiGuard`, degrading to withheld mode rather than raising.

    Precedence: explicit argument → ``$LEGAL_CLIENT_MAP`` → ``DEFAULT_PII_MAP``.
    """
    path = Path(map_path) if map_path else Path(os.environ.get("LEGAL_CLIENT_MAP", str(DEFAULT_PII_MAP)))
    if not path.is_file():
        return PiiGuard(map_path=path, reason="map_absent")
    try:
        engine = _load_redactor()
        rules = engine.load_rules(path)
    except (Exception, SystemExit) as exc:  # noqa: BLE001 — never crash the refresh
        # load_rules() calls sys.exit() on an empty map, hence SystemExit.
        return PiiGuard(map_path=path, reason=f"engine_unavailable:{type(exc).__name__}")
    return PiiGuard(engine=engine, rules=rules, map_path=path, reason="map_loaded")


def pii_banner(payload: dict[str, Any]) -> str:
    """Render the redaction banner from a payload's stamped metadata."""
    meta = payload.get("pii_redaction") or {}
    if meta.get("map_present"):
        return "Client identifiers in issue titles and plan text are codename-redacted (#3768)."
    return (
        f"⚠ Client-codename map unavailable ({meta.get('reason', 'unknown')}) — issue titles and "
        f"plan text are {PII_WITHHELD} for this run. Provision the private map and re-run (#3768)."
    )

RESEARCH_TERMS = {
    "research", "audit", "triage", "recon", "reconnaissance", "scan", "inventory",
    "discover", "classification", "prioritize", "summary", "knowledge", "wiki",
    "document-intelligence", "data-pipeline", "investigate",
}
IMPLEMENT_TERMS = {
    "fix", "test", "prepare", "normalize", "repair", "cleanup", "bounded",
    "implement", "writeback", "artifact", "regression", "validator", "script",
}
STRATEGY_TERMS = {
    "design", "epic", "strategy", "workflow", "review", "policy", "architecture",
    "operating model", "enforcement", "compliance",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def gh_issue_list() -> list[dict[str, Any]]:
    cmd = [
        "gh", "issue", "list", "--state", "open", "--limit", "200",
        "--json", "number,title,labels,assignees,updatedAt,body,url",
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def label_names(issue: dict[str, Any]) -> list[str]:
    return [str(label.get("name", "")) for label in issue.get("labels", [])]


def issue_text(issue: dict[str, Any]) -> str:
    text = f"{issue.get('title', '')}\n{issue.get('body', '')}".lower()
    return text


def existing_agent(issue: dict[str, Any]) -> str | None:
    for label in label_names(issue):
        if label.startswith("agent:"):
            return label.split(":", 1)[1]
    return None


def has_plan_approved(issue: dict[str, Any]) -> bool:
    return "status:plan-approved" in label_names(issue)


def priority_rank(issue: dict[str, Any]) -> int:
    labels = set(label_names(issue))
    if "priority:critical" in labels:
        return 0
    if "priority:high" in labels:
        return 1
    if "priority:medium" in labels:
        return 2
    if "priority:low" in labels:
        return 3
    return 4


def suggested_provider(issue: dict[str, Any]) -> tuple[str, str]:
    current = existing_agent(issue)
    if current in PROVIDERS:
        return current, f"existing {current} agent label"

    text = issue_text(issue)
    labels = " ".join(label_names(issue)).lower()
    haystack = f"{text}\n{labels}"

    if any(term in haystack for term in STRATEGY_TERMS):
        return "claude", "strategy/workflow/architecture language"
    if any(term in haystack for term in IMPLEMENT_TERMS):
        return "codex", "implementation/test/fix language"
    if any(term in haystack for term in RESEARCH_TERMS):
        return "agy", "research/triage/audit language"

    if "cat:data-pipeline" in labels or "cat:document-intelligence" in labels:
        return "agy", "data-pipeline/document-intelligence label"
    if "bug" in labels:
        return "codex", "bug label"
    return "claude", "default long-context routing"


def issue_summary(
    issue: dict[str, Any], scorecard: dict[str, Any], guard: PiiGuard | None = None
) -> dict[str, Any]:
    guard = guard or load_pii_guard()
    provider, reason = suggested_provider(issue)
    labels = label_names(issue)
    execution_ready = has_plan_approved(issue)
    provider_meta = next(item for item in scorecard["recommendations"] if item["provider"] == provider)
    # Routing/classification run on the RAW text (a client name is not a routing
    # term, and scrubbing first would make the heuristics depend on the map).
    # Only the emitted title is scrubbed.
    title = str(issue.get("title", ""))
    body = str(issue.get("body", ""))

    work_type = []
    body_lower = body.lower()
    title_lower = title.lower()
    if any(word in title_lower or word in body_lower for word in RESEARCH_TERMS):
        work_type.append("research")
    if any(word in title_lower or word in body_lower for word in IMPLEMENT_TERMS):
        work_type.append("implementation")
    if any(word in title_lower or word in body_lower for word in STRATEGY_TERMS):
        work_type.append("strategy")
    if not work_type:
        work_type.append("general")

    return {
        "number": issue["number"],
        # NOT omitted: scripts/ai/provider-autolabel.py provably reads
        # provider_queues[*].top_issues[].title to render its human-facing
        # routing-rationale table. Redacted instead (#3768).
        "title": guard.scrub(title),
        "url": issue["url"],
        "labels": labels,
        "updatedAt": issue["updatedAt"],
        "execution_ready": execution_ready,
        "priority_rank": priority_rank(issue),
        "suggested_provider": provider,
        "routing_reason": reason,
        "provider_priority": provider_meta["priority"],
        "provider_status": provider_meta["status"],
        "work_type": work_type,
    }


def sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
    return (
        0 if item["execution_ready"] else 1,
        item["priority_rank"],
        item["number"],
    )


def build_queue(
    scorecard: dict[str, Any], issues: list[dict[str, Any]], guard: PiiGuard | None = None
) -> dict[str, Any]:
    guard = guard or load_pii_guard()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    all_items = [issue_summary(issue, scorecard, guard) for issue in issues]
    for item in sorted(all_items, key=sort_key):
        grouped[item["suggested_provider"]].append(item)

    provider_queues = {}
    for provider in PROVIDERS:
        items = grouped.get(provider, [])
        provider_queues[provider] = {
            "provider": provider,
            "routing_priority": next(x for x in scorecard["recommendations"] if x["provider"] == provider)["priority"],
            "execution_ready_count": sum(1 for item in items if item["execution_ready"]),
            "total_candidates": len(items),
            "top_issues": items[:8],
            # Non-truncated candidate set for downstream Kanban/dispatcher consumers (#2665).
            # top_issues stays capped at 8 for human-readable Markdown; full_candidates
            # carries the complete provider-routed backlog.
            "full_candidates": items,
        }

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "generated_at": now,
        "pii_redaction": guard.metadata(),
        "current_week": scorecard["current_week"],
        "scorecard_generated_at": scorecard["generated_at"],
        "recommended_provider_order": scorecard["recommended_provider_order"],
        "provider_queues": provider_queues,
    }


def render_markdown(queue: dict[str, Any]) -> str:
    lines = [
        "# Provider work queue",
        "",
        f"Generated: {queue['generated_at']}",
        f"Current week: {queue['current_week']}",
        f"Recommended provider order: {', '.join(queue['recommended_provider_order'])}",
        "",
        "Execution-ready means the issue already carries `status:plan-approved`. agent:* labels are routing hints only and do not grant execution approval.",
        "",
        pii_banner(queue),
        "",
    ]
    for provider in PROVIDERS:
        bucket = queue["provider_queues"][provider]
        lines.extend(
            [
                f"## {provider}",
                "",
                f"- Routing priority: {bucket['routing_priority']}",
                f"- Execution-ready candidates: {bucket['execution_ready_count']}",
                f"- Total routed candidates: {bucket['total_candidates']}",
                "",
                "| Issue | Ready | Why routed here | Labels |",
                "|---|---|---|---|",
            ]
        )
        for item in bucket["top_issues"]:
            label_text = ", ".join(item["labels"][:6])
            ready = "yes" if item["execution_ready"] else "no"
            lines.append(
                f"| #{item['number']} {item['title']} | {ready} | {item['routing_reason']} | {label_text} |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate provider work queue from GitHub issues")
    parser.add_argument("--scorecard", default=str(SCORECARD_PATH))
    parser.add_argument("--issues-json", help="Optional pre-fetched issue JSON for tests/offline use")
    parser.add_argument("--output-json", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--output-md", default=str(DEFAULT_MD_OUT))
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--pii-map", default=None,
                        help="private client-codename map (default: $LEGAL_CLIENT_MAP, else "
                             "config/agents/.client-codename-map.local.yaml)")
    parser.add_argument("--require-pii-map", action="store_true",
                        help="fail instead of withholding free text when the map is unusable")
    args = parser.parse_args()

    scorecard = load_json(Path(args.scorecard))
    issues = load_json(Path(args.issues_json)) if args.issues_json else gh_issue_list()
    guard = load_pii_guard(args.pii_map)
    if args.require_pii_map and not guard.available:
        raise SystemExit(
            f"provider-work-queue: client-codename map unusable ({guard.metadata()['reason']}) "
            f"and --require-pii-map was given; refusing to generate."
        )
    if not guard.available:
        print(f"WARNING: {guard.banner()}")
    queue = build_queue(scorecard, issues, guard)

    json_out = Path(args.output_json)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    print(f"JSON → {json_out}")

    if not args.json_only:
        md_out = Path(args.output_md)
        md_out.parent.mkdir(parents=True, exist_ok=True)
        md_out.write_text(render_markdown(queue) + "\n", encoding="utf-8")
        print(f"Markdown → {md_out}")


if __name__ == "__main__":
    main()
