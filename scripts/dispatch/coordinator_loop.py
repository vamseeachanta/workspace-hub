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
LINUX_HOSTS = ("dev-primary", "dev-secondary")
ROLE_ALIASES = {
    "ace-linux-1": "dev-primary",
    "ace-linux-2": "dev-secondary",
    "ace-win-2": "ace-win-2",
    "dev-primary": "dev-primary",
    "dev-secondary": "dev-secondary",
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
    return int((routing.get("hosts") or {}).get(host, {}).get("max_local_lanes") or 0)


def host_supports(routing: dict, host: str, provider: str) -> bool:
    return provider in ((routing.get("hosts") or {}).get(host, {}).get("ai_lanes") or [])


def active_lanes(host_state: dict, host: str) -> int:
    return int((host_state.get(host) or {}).get("active_lanes") or 0)


def first_linux_host(routing: dict, provider: str, host_state: dict) -> str | None:
    for host in LINUX_HOSTS:
        if host_supports(routing, host, provider) and active_lanes(host_state, host) < host_cap(routing, host):
            return host
    return None


def route_issue(issue: dict, routing: dict, current_host: str, host_state: dict) -> Route | None:
    provider = provider_for(issue)
    if not provider:
        return None
    requested = label_value(issue, "machine:")
    requested_host = ROLE_ALIASES.get(requested or "", requested)
    if provider == "codex":
        host = first_linux_host(routing, provider, host_state)
        if requested_host == current_host and active_lanes(host_state, current_host) >= host_cap(routing, current_host):
            return Route(host or "dev-primary", provider, f"{current_host} local lane cap reached", refused_host=current_host)
        return Route(host or "dev-primary", provider, "codex lanes run on Linux")
    if requested_host and host_supports(routing, requested_host, provider):
        host = requested_host
    elif current_host and host_supports(routing, current_host, provider):
        host = current_host
    else:
        host = first_linux_host(routing, provider, host_state)
    if host == current_host and active_lanes(host_state, host) >= host_cap(routing, host):
        fallback = first_linux_host(routing, provider, host_state)
        if fallback:
            return Route(fallback, provider, f"{host} local lane cap reached", refused_host=host)
    return Route(host or "dev-primary", provider, "routed by host-role-routing.yaml")


def plan_for(issue: dict, route: Route) -> dict:
    return {
        "issue": issue["number"],
        "url": issue.get("url"),
        "provider": route.provider,
        "host": route.host,
        "refused_host": route.refused_host,
        "route_reason": route.reason,
    }


def run_once(*, gh, runner, routing: dict, current_host: str, host_state: dict,
             apply: bool, now: datetime) -> dict:
    result = {"dry_run": not apply, "started": [], "skipped": []}
    ready = sorted(gh.list_issues(READY), key=lambda item: parse_time(item.get("createdAt")))
    for item in ready:
        if has_prefix(item, "decision:"):
            result["skipped"].append({"issue": item["number"], "reason": "decision-label"})
            continue
        route = route_issue(item, routing, current_host, host_state)
        if not route:
            result["skipped"].append({"issue": item["number"], "reason": "no-provider"})
            continue
        plan = plan_for(item, route)
        result["started"].append(plan)
        if apply:
            gh.relabel(item["number"], remove=(READY,), add=(ACTIVE,))
            runner.start(plan)
    return result


def target_for_stall(issue: dict) -> str:
    return BLOCKED if has_prefix(issue, "decision:") or "blocked" in " ".join(labels(issue)).lower() else READY


def handle_stalls(*, gh, now: datetime, apply: bool, stall_hours: int) -> dict:
    result = {"dry_run": not apply, "stalled": []}
    for item in sorted(gh.list_issues(ACTIVE), key=lambda obj: obj["number"]):
        comments = gh.issue_comments(item["number"])
        if comments:
            continue
        age_h = (now - parse_time(item.get("updatedAt") or item.get("createdAt"))).total_seconds() / 3600
        if age_h <= stall_hours:
            continue
        target = target_for_stall(item)
        note = (
            f"Coordinator stall rule fired: stalled dispatch:active for "
            f"{age_h:.1f} h with no issue comment. Moving to `{target}`."
        )
        result["stalled"].append({"issue": item["number"], "age_hours": age_h, "target": target})
        if apply:
            gh.comment(item["number"], note)
            gh.relabel(item["number"], remove=(ACTIVE,), add=(target,))
    return result


def load_host_state(path: str | None) -> dict:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    raw = os.environ.get("WH_COORDINATOR_HOST_STATE_JSON")
    return json.loads(raw) if raw else {}


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
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    gh = GhCli(args.repo)
    if args.stalls:
        result = handle_stalls(gh=gh, now=now, apply=args.apply, stall_hours=args.stall_hours)
    else:
        if args.apply and not args.runner_command:
            parser.error("--runner-command is required with --apply")
        result = run_once(
            gh=gh,
            runner=Runner(args.runner_command),
            routing=load_routing(args.routing),
            current_host=ROLE_ALIASES.get(args.current_host, args.current_host),
            host_state=load_host_state(args.host_state_json),
            apply=args.apply,
            now=now,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
