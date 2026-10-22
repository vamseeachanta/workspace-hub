"""Read-only phone-media sync decision aid; no transfers or service changes.

Basis: docs/operations/phone-media-incremental-sync.html, prerequisite table.
The inputs are caller assertions, not live verification or activation authority.
Missing facts remain NOT_EVALUATED. No price or authentication interval is assumed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# USB is manual per issue 3587 and its existing USB/AFC runbook.
# PhotoSync: vendor home page, sections NAS and Autotransfer (read 2026-10-22).
# Actual Size and a device trial are required by issue 3587's quality constraint.
# icloudpd: upstream README, prerequisites and authentication (read 2026-10-22).
# ADP is a compatibility exclusion, never an instruction to reduce security.
REQUIREMENTS = {
    "usb": {
        "automation_required": False,
        "usb_access": True,
        "manual_accepted": True,
    },
    "photosync": {
        "photosync_entitlement": True,
        "actual_size_confirmed": True,
        "webdav_verified": True,
        "autotransfer_tested": True,
    },
    "icloudpd": {
        "icloud_photos_enabled": True,
        "icloud_web_access": True,
        "adp_enabled": False,
        "reauth_accepted": True,
    },
}
FIELDS = set().union(*(set(facts) for facts in REQUIREMENTS.values())) | {
    "backup_capacity_verified"
}


def _candidate(facts: dict, requirements: dict) -> dict:
    missing = [key for key in requirements if facts.get(key) is None]
    blockers = [
        key for key, expected in requirements.items()
        if facts.get(key) is not None and facts[key] is not expected
    ]
    # A known incompatibility dominates missing information (Boolean conjunction).
    status = "BLOCKED" if blockers else "NOT_EVALUATED" if missing else "ELIGIBLE"
    return {"status": status, "blockers": blockers, "missing": missing}


def evaluate(facts: dict, selected: str | None = None) -> dict:
    """Return candidate qualification and a separately gated proposed trial.

    ELIGIBLE means the supplied prerequisite conjunction holds, not that a
    transfer, backup or persistent sync service has been verified by this tool.
    """
    if not isinstance(facts, dict):
        raise TypeError("facts must be a JSON object")
    if set(facts) - FIELDS:
        raise ValueError("unknown fact fields")
    if any(value is not None and type(value) is not bool for value in facts.values()):
        raise ValueError("facts must be true, false or null")
    if selected is not None and selected not in REQUIREMENTS:
        raise ValueError("unknown sync method")
    candidates = {name: _candidate(facts, req) for name, req in REQUIREMENTS.items()}
    decision, trial = "AWAITING_SELECTION", "NOT_EVALUATED"
    if selected is not None:
        status = candidates[selected]["status"]
        decision = {"ELIGIBLE": "PROPOSED", "BLOCKED": "BLOCKED", "NOT_EVALUATED": "NEEDS_INPUT"}[status]
        if status == "BLOCKED" or facts.get("backup_capacity_verified") is False:
            trial = "BLOCKED"
        elif status == "ELIGIBLE" and facts.get("backup_capacity_verified") is True:
            trial = "READY_FOR_TRIAL"
    return {
        "decision": decision,
        "selected": selected,
        "candidates": candidates,
        "trial_status": trial,
        "capacity_status": {
            True: "CONFIRMED_BY_CALLER", False: "BLOCKED", None: "NOT_EVALUATED"
        }[facts.get("backup_capacity_verified")],
    }


def _unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("non-finite JSON constant")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("facts", type=Path, help="JSON object containing Boolean or null facts")
    parser.add_argument("--select", choices=REQUIREMENTS, help="explicit proposed method")
    args = parser.parse_args()
    try:
        facts = json.loads(
            args.facts.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object, parse_constant=_reject_constant,
        )
        result = evaluate(facts, args.select)
    except (OSError, UnicodeError, ValueError, TypeError):
        # argparse.ArgumentParser.error uses its documented usage-error exit code.
        # Do not echo input contents or local paths into error output.
        parser.error("facts file is unreadable or invalid; use known Boolean or null fields")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
