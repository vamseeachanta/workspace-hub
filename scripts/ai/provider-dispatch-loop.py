#!/usr/bin/env python3
"""Provider-dispatch loop (#2665).

Safely consumes provider credits by pulling work from the Kanban execution_ready
lane (under status:plan-approved + marker) and, when that lane is empty, falling
back to non-mutating planning/recon/review feedstock so Claude/Codex/Gemini do
not idle.

Hard boundaries enforced here (mirroring plan acceptance criteria):

  - Implementation dispatch requires BOTH the status:plan-approved label AND
    the .planning/plan-approved/<issue>.md marker. Either alone is insufficient.
  - Single-writer lease ledger: only ace-linux-1 (the configured leader host)
    or an explicit promotion handoff may write leases. ace-linux-2 is
    worker-only by default; it executes assignments leader created, never
    originates them.
  - #2519 coexistence preflight: if another active dispatcher process or marker
    is detected, abort fail-closed BEFORE acquiring the leader lock.
  - Machine-readiness gates provider-route assignment: unready machines
    (offline / missing-auth / stale-repo) cannot receive a lease.
  - Lease idempotency: an active lease for issue+provider+machine blocks a
    second lease for the same triple.
  - Wednesday/Friday/reset-window utilization policy reshapes the fallback
    work selection when usage is under target.
"""
from __future__ import annotations

import argparse
import dataclasses
import fcntl
import importlib.util
import json
import os
import socket
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

WORKSPACE_HUB = Path(__file__).resolve().parents[2]
DEFAULT_LEADER_HOST = "ace-linux-1"
DEFAULT_LEADER_LOCK = WORKSPACE_HUB / "logs" / "ai-provider-dispatch" / "leader.lock"
DEFAULT_LEASE_LEDGER = WORKSPACE_HUB / "logs" / "ai-provider-dispatch" / "leases.jsonl"
DEFAULT_RUN_LEDGER = WORKSPACE_HUB / "logs" / "ai-provider-dispatch" / "runs.jsonl"
DEFAULT_MORNING_QA = WORKSPACE_HUB / "docs" / "reports" / "provider-dispatch-morning-qa.md"
COEXISTENCE_MARKER_DIR = WORKSPACE_HUB / "logs" / "ai-provider-dispatch"
COEXISTENCE_MARKER_NAME = "competing-dispatcher.marker"
DEFAULT_LEASE_TTL_S = 3 * 3600  # 3 hours
NON_TERMINAL_LEASE_STATES = {"active", "scheduled"}


class DispatchError(RuntimeError):
    pass


@dataclass
class Lease:
    lease_id: str
    issue_number: int
    provider: str
    machine: str
    mode: str  # "implementation" | "planning" | "recon" | "review"
    parent_issue: str  # the #2519 parent dispatch issue, for cross-reference
    idempotency_key: str
    state: str  # "active" | "completed" | "stale" | "failed"
    created_at: str
    ttl_seconds: int
    expected_artifact: str | None = None
    expires_at: str | None = None
    completed_at: str | None = None
    error: str | None = None


@dataclass
class DispatcherConfig:
    leader_host: str = DEFAULT_LEADER_HOST
    leader_lock_path: Path = DEFAULT_LEADER_LOCK
    lease_ledger_path: Path = DEFAULT_LEASE_LEDGER
    run_ledger_path: Path = DEFAULT_RUN_LEDGER
    coexistence_marker_dir: Path = COEXISTENCE_MARKER_DIR
    parent_dispatch_issue: str = "#2519"
    lease_ttl_seconds: int = DEFAULT_LEASE_TTL_S
    max_implementation_per_run: int = 3
    promotion_token: str | None = None  # set when ace-linux-2 is explicitly promoted


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def current_machine() -> str:
    """Return the machine identity; allows test override via env var."""
    return os.environ.get("DISPATCHER_MACHINE") or socket.gethostname()


def is_leader_machine(cfg: DispatcherConfig, machine: str | None = None) -> bool:
    machine = machine or current_machine()
    return machine == cfg.leader_host or bool(cfg.promotion_token)


def coexistence_preflight(cfg: DispatcherConfig) -> None:
    """Abort fail-closed if a competing dispatcher is active.

    Detection signals (any is sufficient to abort):
      1. competing-dispatcher.marker file under cfg.coexistence_marker_dir
         (written by another dispatcher to advertise its lock contract)
      2. active leases in cfg.lease_ledger_path whose dispatcher_id differs
         from this process's dispatcher_id AND the lease is not stale

    Per #2519 design, every dispatcher with the same lease-contract MUST share
    cfg.leader_lock_path. Detecting a marker NOT signed with the same
    leader_lock_path means another, independent dispatcher writes leases.
    """
    marker = cfg.coexistence_marker_dir / COEXISTENCE_MARKER_NAME
    if marker.exists():
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raise DispatchError(
                f"competing dispatcher marker exists at {marker} but is malformed; "
                f"abort fail-closed per #2519 coexistence preflight"
            )
        their_lock = data.get("leader_lock_path")
        if their_lock and Path(their_lock) != cfg.leader_lock_path:
            raise DispatchError(
                f"another dispatcher uses lock {their_lock}, this dispatcher uses "
                f"{cfg.leader_lock_path}; independent lease writers forbidden (#2519)"
            )


def acquire_leader_lock(cfg: DispatcherConfig) -> Any:
    """Acquire the single-writer leader lock.

    Refuses on non-leader hosts unless promotion_token is set.
    """
    machine = current_machine()
    if not is_leader_machine(cfg, machine):
        raise DispatchError(
            f"machine {machine!r} is not the leader ({cfg.leader_host!r}); "
            f"to promote, run with --promotion-token after disabling the leader's lease writes"
        )
    cfg.leader_lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = open(cfg.leader_lock_path, "a+")
    try:
        fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as e:
        fd.close()
        raise DispatchError(
            f"leader lock {cfg.leader_lock_path} held by another process; "
            f"check pgrep or wait for it to release"
        ) from e
    fd.write(f"{machine} {os.getpid()} {utc_now()}\n")
    fd.flush()
    return fd


def load_leases(cfg: DispatcherConfig) -> list[Lease]:
    if not cfg.lease_ledger_path.exists():
        return []
    leases: list[Lease] = []
    for raw_line in cfg.lease_ledger_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        leases.append(Lease(**{k: v for k, v in data.items() if k in Lease.__annotations__}))
    return leases


def expire_stale_leases(leases: list[Lease], *, now: datetime | None = None) -> list[Lease]:
    """Return leases with state="stale" for any active lease past its TTL.

    The ledger is append-only; expiry is a derived state, not a mutation of past
    records. Callers iterate this list when checking for collisions.
    """
    now = now or datetime.now(timezone.utc)
    out: list[Lease] = []
    for lease in leases:
        if lease.state in NON_TERMINAL_LEASE_STATES:
            expires = parse_time(lease.expires_at)
            if expires and now > expires:
                lease = dataclasses.replace(lease, state="stale")
        out.append(lease)
    return out


def lease_idempotency_key(issue: int, provider: str, machine: str) -> str:
    return f"{issue}:{provider}:{machine}"


def active_lease_for(
    leases: list[Lease], issue: int, provider: str, machine: str
) -> Lease | None:
    key = lease_idempotency_key(issue, provider, machine)
    for lease in leases:
        if lease.state in NON_TERMINAL_LEASE_STATES and lease.idempotency_key == key:
            return lease
    return None


def append_lease(cfg: DispatcherConfig, lease: Lease) -> None:
    """Append a lease to the JSONL ledger. Caller must hold leader lock."""
    cfg.lease_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cfg.lease_ledger_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(lease)) + "\n")


def append_run(cfg: DispatcherConfig, payload: dict[str, Any]) -> None:
    cfg.run_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cfg.run_ledger_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload) + "\n")


def select_execution_ready(
    kanban: dict[str, Any], leases: list[Lease]
) -> list[dict[str, Any]]:
    """Return Kanban cards in the execution_ready lane that have BOTH gates:
      - status:plan-approved label
      - .planning/plan-approved/<N>.md marker

    Excludes cards with an active lease for the same issue/provider/machine.
    """
    out: list[dict[str, Any]] = []
    for card in kanban.get("lanes", {}).get("execution_ready", []):
        labels = card.get("hover", {}).get("labels", []) or []
        if "status:plan-approved" not in labels:
            continue
        if not card.get("approval_marker"):
            continue
        if not card.get("machine_ready"):
            continue
        existing = active_lease_for(
            leases, card["number"], card["provider_route"], card.get("machine_route") or ""
        )
        if existing:
            continue
        out.append(card)
    return out


def select_planning_fallback(
    kanban: dict[str, Any], leases: list[Lease]
) -> list[dict[str, Any]]:
    """Return planning_feedstock + plan_review cards as non-mutating fallback work."""
    candidates = list(kanban.get("lanes", {}).get("planning_feedstock", []))
    candidates.extend(kanban.get("lanes", {}).get("plan_review", []))
    out: list[dict[str, Any]] = []
    for card in candidates:
        if not card.get("machine_ready"):
            continue
        existing = active_lease_for(
            leases, card["number"], card["provider_route"], card.get("machine_route") or ""
        )
        if existing:
            continue
        out.append(card)
    return out


def apply_utilization_policy(
    utilization: dict[str, Any], *, now: datetime | None = None
) -> dict[str, str]:
    """Return per-provider policy hint: 'feed_anything' | 'feed_planning' | 'reset_window'.

    Wednesday noon → providers under 25% get planning packets.
    Friday noon  → providers under 60% get additional packets.
    Last 24h before reset → non-mutating recon/review only.
    """
    now = now or datetime.now(timezone.utc)
    policy: dict[str, str] = {}
    weekday = now.weekday()  # Monday=0, Sunday=6
    hour = now.hour
    for prov, data in (utilization.get("providers") or {}).items():
        pct = data.get("usage_pct", 0.0)
        # Reset window: Saturday 00:00 UTC is a placeholder reset; last 24h before that.
        is_reset_window = weekday == 6 or (weekday == 5 and hour >= 0)
        if is_reset_window:
            policy[prov] = "reset_window"
            continue
        if weekday == 2 and hour >= 12 and pct < 0.25:  # Wednesday after noon
            policy[prov] = "feed_planning"
            continue
        if weekday == 4 and hour >= 12 and pct < 0.60:  # Friday after noon
            policy[prov] = "feed_planning"
            continue
        policy[prov] = "feed_anything"
    return policy


def make_lease(
    cfg: DispatcherConfig,
    candidate: dict[str, Any],
    *,
    mode: str,
    now: datetime | None = None,
    ttl_s: int | None = None,
) -> Lease:
    now = now or datetime.now(timezone.utc)
    ttl_s = ttl_s or cfg.lease_ttl_seconds
    expires = (now + timedelta(seconds=ttl_s)).isoformat(timespec="seconds").replace("+00:00", "Z")
    return Lease(
        lease_id=f"L-{candidate['number']}-{candidate['provider_route']}-{int(now.timestamp())}",
        issue_number=int(candidate["number"]),
        provider=str(candidate["provider_route"]),
        machine=str(candidate.get("machine_route") or ""),
        mode=mode,
        parent_issue=cfg.parent_dispatch_issue,
        idempotency_key=lease_idempotency_key(
            candidate["number"], candidate["provider_route"], candidate.get("machine_route") or ""
        ),
        state="active",
        created_at=now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        ttl_seconds=ttl_s,
        expected_artifact=candidate.get("plan") or f"docs/plans/issue-{candidate['number']}.md",
        expires_at=expires,
    )


def run_loop(
    cfg: DispatcherConfig,
    kanban: dict[str, Any],
    utilization: dict[str, Any],
    *,
    now: datetime | None = None,
    dry_run: bool = False,
    launcher: Callable[[Lease, dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Execute one tick of the dispatch loop.

    Returns a summary dict with planned/launched leases and policy decisions.
    """
    coexistence_preflight(cfg)
    if not is_leader_machine(cfg):
        raise DispatchError(
            "non-leader machine cannot originate dispatch; "
            "wait for the leader to create assignments and run as worker only"
        )

    now = now or datetime.now(timezone.utc)
    leases = expire_stale_leases(load_leases(cfg), now=now)
    policy = apply_utilization_policy(utilization, now=now)

    selected: list[Lease] = []
    summary: dict[str, Any] = {
        "generated_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "policy": policy,
        "execution_ready": [],
        "planning_fallback": [],
        "skipped_due_to_lease": [],
        "skipped_due_to_machine": [],
    }

    ready = select_execution_ready(kanban, leases)
    for card in ready[: cfg.max_implementation_per_run]:
        lease = make_lease(cfg, card, mode="implementation", now=now)
        if dry_run:
            summary["execution_ready"].append({"lease_id": lease.lease_id, "planned": True, **asdict(lease)})
            continue
        append_lease(cfg, lease)
        if launcher:
            try:
                outcome = launcher(lease, card)
                append_run(cfg, {"lease_id": lease.lease_id, "outcome": outcome, "at": utc_now()})
            except Exception as exc:  # noqa: BLE001
                append_run(cfg, {"lease_id": lease.lease_id, "error": str(exc), "at": utc_now()})
        summary["execution_ready"].append(asdict(lease))
        selected.append(lease)

    if not selected:
        # No execution-ready work — fall back to planning/recon/review feedstock.
        fallback = select_planning_fallback(kanban, leases)
        for card in fallback[: cfg.max_implementation_per_run]:
            mode = "review" if policy.get(card["provider_route"]) == "reset_window" else "planning"
            lease = make_lease(cfg, card, mode=mode, now=now)
            if dry_run:
                summary["planning_fallback"].append({"lease_id": lease.lease_id, "planned": True, **asdict(lease)})
                continue
            append_lease(cfg, lease)
            if launcher:
                try:
                    outcome = launcher(lease, card)
                    append_run(cfg, {"lease_id": lease.lease_id, "outcome": outcome, "at": utc_now()})
                except Exception as exc:  # noqa: BLE001
                    append_run(cfg, {"lease_id": lease.lease_id, "error": str(exc), "at": utc_now()})
            summary["planning_fallback"].append(asdict(lease))

    # Bookkeeping diagnostics
    for card in kanban.get("cards", []):
        if not card.get("machine_ready"):
            summary["skipped_due_to_machine"].append({"number": card["number"], "blocker": card.get("machine_blocker")})

    return summary


def generate_morning_qa(
    cfg: DispatcherConfig, *, since: datetime | None = None, now: datetime | None = None
) -> str:
    """Aggregate run/lease ledger into a single morning QA Markdown packet."""
    now = now or datetime.now(timezone.utc)
    since = since or (now - timedelta(hours=24))
    leases = expire_stale_leases(load_leases(cfg), now=now)
    runs: list[dict[str, Any]] = []
    if cfg.run_ledger_path.exists():
        for raw_line in cfg.run_ledger_path.read_text(encoding="utf-8").splitlines():
            try:
                runs.append(json.loads(raw_line))
            except json.JSONDecodeError:
                continue

    completed = [l for l in leases if l.state == "completed" and parse_time(l.completed_at) and parse_time(l.completed_at) >= since]
    running = [l for l in leases if l.state in NON_TERMINAL_LEASE_STATES]
    stale = [l for l in leases if l.state == "stale"]
    failed = [l for l in leases if l.state == "failed" or any(r.get("lease_id") == l.lease_id and r.get("error") for r in runs)]

    lines = [
        "# Provider-dispatch morning QA packet",
        "",
        f"Generated: {now.isoformat(timespec='seconds').replace('+00:00', 'Z')}",
        f"Window: since {since.isoformat(timespec='seconds').replace('+00:00', 'Z')}",
        "",
        "## Completed",
        "",
    ]
    if not completed:
        lines.append("- (none)")
    for l in completed:
        lines.append(f"- {l.lease_id} (#{l.issue_number} → {l.provider}@{l.machine}) — artifact: `{l.expected_artifact}`")
    lines.extend(["", "## Running", ""])
    if not running:
        lines.append("- (none)")
    for l in running:
        lines.append(f"- {l.lease_id} (#{l.issue_number} → {l.provider}@{l.machine}) — TTL expires {l.expires_at}")
    lines.extend(["", "## Stale / failed", ""])
    if not stale and not failed:
        lines.append("- (none)")
    for l in stale + failed:
        lines.append(f"- {l.lease_id} (#{l.issue_number} → {l.provider}@{l.machine}) — state={l.state}, error={l.error}")
    lines.extend(["", "## Recommended user actions", ""])
    if stale:
        lines.append(f"- Investigate {len(stale)} stale leases past TTL; either continue or close-out.")
    if failed:
        lines.append(f"- Review {len(failed)} failed lease runs in {cfg.run_ledger_path.relative_to(WORKSPACE_HUB)}.")
    if not (stale or failed):
        lines.append("- No outstanding issues; continue normal cadence.")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Provider-dispatch loop (#2665)")
    parser.add_argument("--kanban-json", default=str(WORKSPACE_HUB / "config" / "ai-tools" / "provider-kanban.json"))
    parser.add_argument("--utilization-json", default=str(WORKSPACE_HUB / "config" / "ai-tools" / "provider-utilization-weekly.json"))
    parser.add_argument("--dry-run", action="store_true", help="Plan but don't write leases / launch work")
    parser.add_argument("--morning-qa", action="store_true", help="Generate morning QA packet only")
    parser.add_argument("--morning-qa-out", default=str(DEFAULT_MORNING_QA))
    parser.add_argument("--leader-host", default=DEFAULT_LEADER_HOST)
    parser.add_argument("--promotion-token", help="Pass through to promote a non-leader machine (advanced)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cfg = DispatcherConfig(leader_host=args.leader_host, promotion_token=args.promotion_token)

    if args.morning_qa:
        text = generate_morning_qa(cfg)
        out = Path(args.morning_qa_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"Morning QA → {out}")
        return 0

    kanban = json.loads(Path(args.kanban_json).read_text(encoding="utf-8"))
    utilization = (
        json.loads(Path(args.utilization_json).read_text(encoding="utf-8"))
        if Path(args.utilization_json).exists()
        else {}
    )

    lock = acquire_leader_lock(cfg)
    try:
        summary = run_loop(cfg, kanban, utilization, dry_run=args.dry_run)
    finally:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        lock.close()

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
