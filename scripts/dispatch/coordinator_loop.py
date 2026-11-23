#!/usr/bin/env python3
"""Coordinator dispatch loop for rewire L3 (#4000).

Default mode is a dry-run. `--apply` is required before labels change or a
runner starts.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: run with `uv run --with pyyaml`")

READY = "dispatch:ready"
ACTIVE = "dispatch:active"
BLOCKED = "dispatch:blocked"
LANES = {"claude", "codex"}
LINUX_HOSTS = ("ace-linux-1", "ace-linux-2")
DEFAULT_STALL_DECISION_LABEL = "decision:ecosystem"
ROUTING_KEYS = {
    "ace-linux-1": "dev-primary",
    "ace-linux-2": "dev-secondary",
    "ace-win-2": "ace-win-2",
}


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if out.returncode == 0:
        return Path(out.stdout.strip())
    return Path(__file__).resolve().parents[2]


def parse_time(raw: str | None) -> datetime:
    if not raw:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def load_routing(path: Path | None = None) -> dict:
    path = path or repo_root() / "config" / "agents" / "host-role-routing.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def labels(issue: dict) -> list[str]:
    raw = issue.get("labels") or []
    if raw and isinstance(raw[0], dict):
        return [item["name"] for item in raw]
    return list(raw)


def label_value(issue: dict, prefix: str) -> str | None:
    for label in labels(issue):
        if label.startswith(prefix):
            return label.split(":", 1)[1]
    return None


def has_prefix(issue: dict, prefix: str) -> bool:
    return any(label.startswith(prefix) for label in labels(issue))


def canonical_host(raw: str | None) -> str | None:
    if not raw:
        return None
    if raw == "dev-primary":
        return "ace-linux-1"
    if raw == "dev-secondary":
        return "ace-linux-2"
    return raw


def routing_key(host: str) -> str:
    return ROUTING_KEYS.get(host, host)


class GhCli:
    def __init__(self, repo: str):
        self.repo = repo

    def _run(self, args: list[str]) -> str:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=120)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
        return proc.stdout

    def list_issues(self, label: str) -> list[dict]:
        out = self._run([
            "gh", "issue", "list", "--repo", self.repo, "--state", "open",
            "--label", label, "--limit", "100",
            "--json", "number,title,url,state,createdAt,updatedAt,labels",
        ])
        return json.loads(out)

    def issue_comments(self, number: int) -> list[dict]:
        out = self._run([
            "gh", "issue", "view", str(number), "--repo", self.repo,
            "--json", "comments",
        ])
        return json.loads(out).get("comments") or []

    def relabel(self, number: int, *, remove: Iterable[str] = (), add: Iterable[str] = ()):
        args = ["gh", "issue", "edit", str(number), "--repo", self.repo]
        for label in remove:
            args += ["--remove-label", label]
        for label in add:
            args += ["--add-label", label]
        self._run(args)

    def comment(self, number: int, body: str):
        self._run(["gh", "issue", "comment", str(number), "--repo", self.repo, "--body", body])


class Runner:
    def __init__(self, command: str | None):
        self.command = command

    def start(self, plan: dict):
        if not self.command:
            raise RuntimeError("--runner-command is required with --apply")
        payload = json.dumps(plan, sort_keys=True)
        subprocess.run([self.command, payload], check=True, timeout=120)


@dataclass
class Route:
    host: str
    provider: str
    reason: str
    refused_host: str | None = None


def provider_for(issue: dict) -> str | None:
    lane = label_value(issue, "lane:")
    if lane in LANES:
        return lane
    ai = label_value(issue, "ai:")
    if ai in LANES:
        return ai
    return None


def host_cap(routing: dict, host: str) -> int:
    return int((routing.get("hosts") or {}).get(routing_key(host), {}).get("max_local_lanes") or 0)


def host_supports(routing: dict, host: str, provider: str) -> bool:
    return provider in ((routing.get("hosts") or {}).get(routing_key(host), {}).get("ai_lanes") or [])


def active_lanes(host_state: dict, host: str) -> int:
    return int((host_state.get(host) or {}).get("active_lanes") or 0)


def increment_active_lanes(host_state: dict, host: str) -> None:
    entry = host_state.setdefault(host, {})
    entry["active_lanes"] = active_lanes(host_state, host) + 1


def host_has_room(routing: dict, host_state: dict, host: str, provider: str) -> bool:
    return host_supports(routing, host, provider) and active_lanes(host_state, host) < host_cap(routing, host)


def first_linux_host(routing: dict, provider: str, host_state: dict) -> str | None:
    for host in LINUX_HOSTS:
        if host_has_room(routing, host_state, host, provider):
            return host
    return None


def route_issue(issue: dict, routing: dict, current_host: str, host_state: dict) -> Route | None:
    provider = provider_for(issue)
    if not provider:
        return None
    requested = label_value(issue, "machine:")
    requested_host = canonical_host(requested)
    if provider == "codex":
        host = first_linux_host(routing, provider, host_state)
        if not host:
            return None
        if requested_host and requested_host != host:
            return Route(host, provider, f"{requested_host} local lane cap reached", refused_host=requested_host)
        return Route(host, provider, "codex lanes run on Linux")

    refused_host = None
    candidates = [requested_host, current_host, *LINUX_HOSTS]
    for host in dict.fromkeys(item for item in candidates if item):
        if not host_supports(routing, host, provider):
            continue
        if host_has_room(routing, host_state, host, provider):
            reason = "routed by host-role-routing.yaml"
            if refused_host:
                reason = f"{refused_host} local lane cap reached"
            return Route(host, provider, reason, refused_host=refused_host)
        refused_host = refused_host or host
    return None


def plan_for(issue: dict, route: Route) -> dict:
    return {
        "issue": issue["number"],
        "url": issue.get("url"),
        "provider": route.provider,
        "host": route.host,
        "refused_host": route.refused_host,
        "route_reason": route.reason,
    }


def derive_host_state_from_active(gh, routing: dict) -> dict:
    state = {host: {"active_lanes": 0} for host in LINUX_HOSTS}
    for host in ("ace-win-1", "ace-win-2", "gpu-claw", "macbook-portable"):
        if routing_key(host) in (routing.get("hosts") or {}):
            state[host] = {"active_lanes": 0}
    unknown_active_providers: set[str] = set()
    for item in gh.list_issues(ACTIVE):
        provider = provider_for(item)
        host = canonical_host(label_value(item, "machine:"))
        if host and host in state:
            increment_active_lanes(state, host)
        elif provider:
            unknown_active_providers.add(provider)
    for provider in unknown_active_providers:
        for host in state:
            if host_supports(routing, host, provider):
                state[host]["active_lanes"] = host_cap(routing, host)
    return state


def run_once(*, gh, runner, routing: dict, current_host: str, host_state: dict,
             apply: bool, now: datetime, max_dispatches_per_run: int = 1) -> dict:
    result = {"dry_run": not apply, "started": [], "skipped": [], "runner_failed": []}
    effective_host_state = (
        derive_host_state_from_active(gh, routing)
        if host_state is None
        else {host: dict(value) for host, value in host_state.items()}
    )
    dispatches_this_run = 0
    ready = sorted(gh.list_issues(READY), key=lambda item: parse_time(item.get("createdAt")))
    for item in ready:
        if dispatches_this_run >= max_dispatches_per_run:
            result["skipped"].append({"issue": item["number"], "reason": "max-dispatches-per-run"})
            continue
        if has_prefix(item, "decision:"):
            result["skipped"].append({"issue": item["number"], "reason": "decision-label"})
            continue
        provider = provider_for(item)
        route = route_issue(item, routing, current_host, effective_host_state)
        if not route:
            reason = "all-hosts-at-cap" if provider else "no-provider"
            result["skipped"].append({"issue": item["number"], "reason": reason})
            continue
        plan = plan_for(item, route)
        if apply:
            gh.relabel(item["number"], remove=(READY,), add=(ACTIVE,))
            try:
                runner.start(plan)
            except Exception as exc:
                gh.relabel(item["number"], remove=(ACTIVE,), add=(READY,))
                gh.comment(item["number"], f"Coordinator runner failed; returned to `{READY}`: {exc}")
                result["runner_failed"].append({"issue": item["number"], "error": str(exc)})
                continue
        result["started"].append(plan)
        increment_active_lanes(effective_host_state, route.host)
        dispatches_this_run += 1
    return result


def latest_comment_time(comments: list[dict]) -> datetime | None:
    if not comments:
        return None
    return max(parse_time(item.get("createdAt")) for item in comments)


def handle_stalls(
    *,
    gh,
    now: datetime,
    apply: bool,
    stall_hours: int,
    decision_label: str = DEFAULT_STALL_DECISION_LABEL,
) -> dict:
    result = {"dry_run": not apply, "stalled": []}
    for item in sorted(gh.list_issues(ACTIVE), key=lambda obj: obj["number"]):
        comments = gh.issue_comments(item["number"])
        reference_time = latest_comment_time(comments) or parse_time(item.get("updatedAt") or item.get("createdAt"))
        age_h = (now - reference_time).total_seconds() / 3600
        if age_h <= stall_hours:
            continue
        target = BLOCKED
        note = (
            f"Coordinator stall rule fired: stalled dispatch:active for "
            f"{age_h:.1f} h since the latest issue comment. Moving to `{target}`."
        )
        result["stalled"].append({"issue": item["number"], "age_hours": age_h, "target": target})
        if apply:
            gh.comment(item["number"], note)
            gh.relabel(item["number"], remove=(ACTIVE,), add=(target, decision_label))
    return result


def load_host_state(path: str | None) -> dict | None:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    raw = os.environ.get("WH_COORDINATOR_HOST_STATE_JSON")
    return json.loads(raw) if raw else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="vamseeachanta/workspace-hub")
    parser.add_argument("--routing", type=Path)
    parser.add_argument("--current-host", default=os.environ.get("WH_COORDINATOR_HOST", "ace-win-2"))
    parser.add_argument("--host-state-json")
    parser.add_argument("--runner-command")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--stalls", action="store_true")
    parser.add_argument("--stall-hours", type=int, default=48)
    parser.add_argument("--stall-decision-label", default=DEFAULT_STALL_DECISION_LABEL)
    parser.add_argument("--max-dispatches-per-run", type=int, default=1)
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    gh = GhCli(args.repo)
    if args.stalls:
        result = handle_stalls(
            gh=gh,
            now=now,
            apply=args.apply,
            stall_hours=args.stall_hours,
            decision_label=args.stall_decision_label,
        )
    else:
        if args.apply and not args.runner_command:
            parser.error("--runner-command is required with --apply")
        result = run_once(
            gh=gh,
            runner=Runner(args.runner_command),
            routing=load_routing(args.routing),
            current_host=canonical_host(args.current_host),
            host_state=load_host_state(args.host_state_json),
            apply=args.apply,
            now=now,
            max_dispatches_per_run=args.max_dispatches_per_run,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
