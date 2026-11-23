#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""venue_absence_detector.py — fleet-wide SILENT-STOP detector (issue #2971, F4).

Why this exists
---------------
F4 gates the Telegram escalation-sweep behind a single-active-venue lease so that
at most one host mirrors client escalations. That introduces a fleet-wide
SILENT-STOP risk: if NO host validly holds the venue lease (CAS loss, clock skew,
every host no-ops), the client 24h-SLA escalation mirroring quietly stops and
nobody notices until SLAs breach.

This detector is the safety net. It runs DECOUPLED from the venue lease — it must
NOT hold or depend on the lease — and it alerts if EITHER:
  (a) no valid venue holder exists, OR
  (b) any pending escalation / last-sweep-success heartbeat is staler than a
      threshold that is strictly BELOW the 24h SLA, so we catch a stall with
      margin to act before SLA breach.

The decision logic (`evaluate`) is PURE: no IO, no clock, no subprocess. All
freshness is expressed as ages-in-hours computed by the caller, so the core is
fully unit-testable and deterministic. The CLI is a thin shell that gathers the
inputs and routes each alert to `scripts/notify.sh`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

# --------------------------------------------------------------------------- #
# PURE CORE
# --------------------------------------------------------------------------- #


def evaluate(
    lease_present: bool,
    lease_valid: bool,
    mirror_ages_h: list[float],
    heartbeat_age_h: float | None,
    sla_h: float = 24.0,
    warn_fraction: float = 0.5,
) -> list[dict]:
    """Return alert dicts for any silent-stop condition. Empty list == healthy.

    PURE: no IO, no clock. Caller supplies all freshness as ages in hours.

    Args:
        lease_present:   True if SOME host currently holds the venue lease ref.
        lease_valid:     True if that held lease is valid (unexpired, well-formed
                         fencing token, etc.). Both must be true for a holder.
        mirror_ages_h:   age (hours) of each PENDING escalation awaiting mirror.
        heartbeat_age_h: age (hours) since the last SUCCESSFUL sweep, or None if
                         no heartbeat is available to evaluate.
        sla_h:           the client SLA window in hours (default 24h).
        warn_fraction:   fraction of the SLA at which staleness becomes an alert
                         (default 0.5 → alert at 12h, leaving margin before 24h).

    Returns:
        A list of {"kind", "detail", "severity"} dicts. Alert kinds:
          - "no-holder"       : not lease_present or not lease_valid
          - "stale-mirror"    : any mirror age > sla_h * warn_fraction
          - "stale-heartbeat" : heartbeat_age_h is not None and > threshold
    """
    # (0) Input validation — malformed telemetry must FAIL CLOSED, never be read as
    # healthy (#2971 code-review MAJOR #5).
    import math
    if not (isinstance(sla_h, (int, float)) and sla_h > 0):
        raise ValueError(f"sla_h must be a positive number, got {sla_h!r}")
    if not (isinstance(warn_fraction, (int, float)) and 0 < warn_fraction <= 1):
        raise ValueError(f"warn_fraction must be in (0,1], got {warn_fraction!r}")
    for a in mirror_ages_h or []:
        if isinstance(a, bool) or not isinstance(a, (int, float)) or math.isnan(a) or a < 0:
            raise ValueError(f"mirror age must be a non-negative number, got {a!r}")
    if heartbeat_age_h is not None and (
        isinstance(heartbeat_age_h, bool)
        or not isinstance(heartbeat_age_h, (int, float))
        or math.isnan(heartbeat_age_h) or heartbeat_age_h < 0
    ):
        raise ValueError(f"heartbeat_age_h must be None or a non-negative number, got {heartbeat_age_h!r}")

    threshold_h = sla_h * warn_fraction
    alerts: list[dict] = []

    # (a0) UNKNOWN telemetry is NOT health (#2971 code-review MAJOR #4): if we have
    # neither a sweep heartbeat NOR any pending-mirror signal, we cannot prove the
    # sweep is alive — a dead sweep produces exactly this empty picture. Alert.
    if heartbeat_age_h is None and not (mirror_ages_h or []):
        alerts.append({
            "kind": "unknown-telemetry",
            "detail": ("no sweep heartbeat and no pending-mirror signal — cannot prove "
                       "the venue sweep is alive (a dead sweep looks identical)"),
            "severity": "critical",
        })

    # (a) No valid venue holder — the lease itself has silently stopped.
    if not lease_present or not lease_valid:
        if not lease_present:
            reason = "no host holds the venue lease"
        else:
            reason = "venue lease held but invalid (expired/clock-skew/bad-token)"
        alerts.append(
            {
                "kind": "no-holder",
                "detail": (
                    f"{reason}; escalation mirroring is unguarded "
                    f"(sla={sla_h}h)"
                ),
                "severity": "critical",
            }
        )

    # (b1) A pending escalation has aged past the warn threshold.
    for age in mirror_ages_h:
        if age > threshold_h:
            alerts.append(
                {
                    "kind": "stale-mirror",
                    "detail": (
                        f"pending escalation un-mirrored for {age:.2f}h "
                        f"(> {threshold_h:.2f}h = {warn_fraction:.0%} of "
                        f"{sla_h}h SLA)"
                    ),
                    "severity": "critical",
                }
            )

    # (b2) The last successful sweep heartbeat is stale.
    if heartbeat_age_h is not None and heartbeat_age_h > threshold_h:
        alerts.append(
            {
                "kind": "stale-heartbeat",
                "detail": (
                    f"last successful sweep was {heartbeat_age_h:.2f}h ago "
                    f"(> {threshold_h:.2f}h = {warn_fraction:.0%} of "
                    f"{sla_h}h SLA)"
                ),
                "severity": "critical",
            }
        )

    return alerts


# --------------------------------------------------------------------------- #
# THIN CLI
# --------------------------------------------------------------------------- #


def _default_notify(alert: dict) -> None:
    """Real notifier: append a JSONL fail event via scripts/notify.sh."""
    notify_sh = Path(__file__).resolve().parents[2] / "scripts" / "notify.sh"
    detail = f"{alert.get('kind', '?')}: {alert.get('detail', '')}"
    subprocess.run(
        ["bash", str(notify_sh), "cron", "venue-absence", "fail", detail],
        check=False,
    )


def _gather_inputs(args: argparse.Namespace) -> dict:
    """Collect detector inputs. Minimal/stub: prefer --json, else flags.

    Real deployment can replace this with live probes (read the lease ref,
    list pending escalations, read the last-sweep heartbeat file). The CORE
    `evaluate` is what carries the safety guarantee and is fully tested.
    """
    if args.json:
        raw = json.loads(Path(args.json).read_text() if Path(args.json).exists() else args.json)
        return {
            "lease_present": bool(raw.get("lease_present", False)),
            "lease_valid": bool(raw.get("lease_valid", False)),
            "mirror_ages_h": [float(x) for x in raw.get("mirror_ages_h", [])],
            "heartbeat_age_h": (
                None if raw.get("heartbeat_age_h") is None
                else float(raw["heartbeat_age_h"])
            ),
            "sla_h": float(raw.get("sla_h", 24.0)),
            "warn_fraction": float(raw.get("warn_fraction", 0.5)),
        }
    return {
        "lease_present": args.lease_present,
        "lease_valid": args.lease_valid,
        "mirror_ages_h": list(args.mirror_age_h or []),
        "heartbeat_age_h": args.heartbeat_age_h,
        "sla_h": args.sla_h,
        "warn_fraction": args.warn_fraction,
    }


def run_cli(
    args: argparse.Namespace,
    notify_fn: Callable[[dict], None] = _default_notify,
) -> int:
    """Evaluate inputs and fire one notify_fn per alert. Returns exit code.

    Returns 0 when healthy, 1 when any alert fired. notify_fn is injectable so
    tests can assert call count without shelling out to notify.sh.
    """
    inputs = _gather_inputs(args)
    alerts = evaluate(**inputs)
    for alert in alerts:
        notify_fn(alert)
    if alerts:
        print(
            f"venue-absence: {len(alerts)} alert(s) — SILENT-STOP risk",
            file=sys.stderr,
        )
        for alert in alerts:
            print(f"  [{alert['severity']}] {alert['kind']}: {alert['detail']}",
                  file=sys.stderr)
        return 1
    print("venue-absence: healthy (valid holder, fresh mirrors + heartbeat)")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Venue ABSENCE detector — alerts on escalation silent-stop "
        "(decoupled from the venue lease)."
    )
    p.add_argument("--json", help="JSON file path or inline JSON of inputs.")
    p.add_argument("--lease-present", action="store_true",
                   help="A host currently holds the venue lease.")
    p.add_argument("--lease-valid", action="store_true",
                   help="The held lease is valid (unexpired/well-formed).")
    p.add_argument("--mirror-age-h", type=float, action="append", default=[],
                   help="Age (hours) of a pending escalation; repeatable.")
    p.add_argument("--heartbeat-age-h", type=float, default=None,
                   help="Hours since last successful sweep (omit if none).")
    p.add_argument("--sla-h", type=float, default=24.0,
                   help="Client SLA window in hours (default 24).")
    p.add_argument("--warn-fraction", type=float, default=0.5,
                   help="Fraction of SLA at which staleness alerts (default 0.5).")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    return run_cli(args)


if __name__ == "__main__":
    raise SystemExit(main())
