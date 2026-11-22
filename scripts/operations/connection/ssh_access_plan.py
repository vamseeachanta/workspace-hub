"""Assess private SSH alternatives from operator-supplied Boolean evidence.

Offline only: no probes, configuration changes, reconnects or credential reads.
Policy and evidence meanings: docs/ops/compute-ssh-access.md (Evidence method).
"""

import argparse
import json
import sys
from pathlib import Path

# Security basis: docs/ops/remote-linux-access.md, Security controls and
# Verification matrix; OpenSSH sshd_config(5), current manual, retrieved
# 2026-10-22: https://man.openbsd.org/sshd_config . These are propositions,
# not numeric limits. Missing evidence must never become a positive proof.
COMMON = (
    "private_only", "key_only", "password_disabled", "interactive_disabled",
    "root_disabled", "host_key_verified", "least_privilege", "recovery_verified",
    "headless_provisioning", "job_survives_disconnect", "ssh_data_transfer",
    "post_reboot",
)

# Ordered design preference, not a measured score; basis: canonical access
# runbook Architecture and the option decisions in compute-ssh-access.md.
OPTIONS = {
    "tailscale_openssh": ("device_controls", "manual_profile_independent"),
    "tailscale_subnet_openssh": (
        "device_controls", "subnet_route_verified", "manual_profile_independent",
    ),
    "lan_openssh": ("routed_private_path", "manual_profile_independent"),
    "cloudflare_openssh": ("unattended_policy", "manual_profile_independent"),
    "managed_wireguard": ("reconnect_verified",),
}


def assess(evidence: dict) -> dict:
    """Apply all-true qualification, preserving failed and missing proofs.

    A PASS reports only that supplied declarations meet this policy. It does
    not authenticate evidence, authorize rollout or confirm current access.
    """
    if not isinstance(evidence, dict) or evidence.keys() - OPTIONS.keys():
        raise ValueError("Invalid candidate schema")
    results = {}
    for candidate, extra in OPTIONS.items():
        required = (*COMMON, *extra)
        facts = evidence.get(candidate, {})
        if not isinstance(facts, dict) or facts.keys() - set(required):
            raise ValueError("Invalid evidence schema")
        if any(value is not None and type(value) is not bool for value in facts.values()):
            raise ValueError("Evidence must be Boolean or null")
        failed = [field for field in required if facts.get(field) is False]
        missing = [field for field in required if facts.get(field) is None]
        status = "FAIL" if failed else "NOT_EVALUATED" if missing else "PASS"
        results[candidate] = {"status": status, "failed": failed, "missing": missing}
    selected = next((key for key in OPTIONS if results[key]["status"] == "PASS"), None)
    return {
        "status": "PASS" if selected else "NOT_EVALUATED",
        "selected": selected,
        "manual_profile_independent": None if selected is None else selected != "managed_wireguard",
        "options": results,
    }


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate key")
        result[key] = value
    return result


def _reject_constant(_value):
    raise ValueError("Non-finite value")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path, help="Private Boolean-only JSON evidence file")
    args = parser.parse_args(argv)
    try:
        raw = args.evidence.read_text(encoding="utf-8")
    except OSError:
        print("Evidence could not be read.", file=sys.stderr)
        return 1
    except UnicodeError:
        print("Invalid evidence; expected the documented Boolean schema.", file=sys.stderr)
        return 1
    try:
        evidence = json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
        result = assess(evidence)
    except (ValueError, RecursionError):
        # Never echo file paths, raw input, unknown keys or parser diagnostics.
        print("Invalid evidence; expected the documented Boolean schema.", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    # Success means valid assessment, even when all access remains unverified.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
