"""Read-only phase evidence assessment; never authorizes a live transaction.

Basis: issue 3878 acceptance (2026), phase-specific elapsed comparisons.
All time limits are supplied by a separately frozen policy, never defaults.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

BINDING_KEYS = {"source_sha256", "target_sha256", "policy_sha256"}


def number(value):
    """Time is finite and nonnegative; booleans are not measurements."""
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("time must be finite nonnegative seconds")
    return value


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("nonempty evidence reference or boundary required")
    return value


def policy_digest(policy):
    return hashlib.sha256(json.dumps(
        policy, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()).hexdigest()


def validate_policy(policy, binding):
    """Policy identity binds boundaries and allowances before measurement."""
    if set(binding) != BINDING_KEYS or any(
        not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v)
        for v in binding.values()
    ):
        raise ValueError("invalid source/target/policy binding")
    if binding["policy_sha256"] != policy_digest(policy):
        raise ValueError("policy digest mismatch; allowances cannot be rebound silently")
    cap = number(policy["cap_s"])
    text(policy["basis_ref"])
    checkpoints = policy["checkpoints"]
    if not isinstance(checkpoints, list) or not checkpoints:
        raise ValueError("policy requires ordered checkpoints")
    names = []
    for checkpoint in checkpoints:
        names.append(text(checkpoint["name"]))
        text(checkpoint["boundary"])
        if number(checkpoint["reserve_s"]) > cap:
            raise ValueError("policy reserve exceeds cap")
        required = checkpoint["required_io"]
        if not isinstance(required, list) or len(required) != len(set(required)):
            raise ValueError("policy I/O names must be unique")
        for name in required:
            text(name)
    if len(names) != len(set(names)):
        raise ValueError("policy checkpoint names must be unique")


def io_costs(records, required, start, end):
    """Retain traced spans; do not sum potentially overlapping I/O intervals."""
    if not isinstance(records, list):
        raise TypeError("phase I/O trace list required")
    costs = []
    names = []
    for record in records:
        names.append(text(record["name"]))
        text(record["trace_ref"])
        text(record["operation"])
        left, right = number(record["start_s"]), number(record["end_s"])
        if not start <= left <= right <= end:
            raise ValueError("I/O trace outside checkpoint phase")
        # Issue 3878 (2026): retain traced full-index costs, in seconds.
        costs.append({**record, "duration_s": right - left})
    if len(names) != len(set(names)) or not set(required) <= set(names):
        raise ValueError("required I/O coverage missing or duplicated")
    return costs


def assess_run(policy, binding, run):
    result = {"evidence": run, "status": "NOT_EVALUATED", "checkpoints": []}
    try:
        text(run["run_ref"])
        text(run["clock_ref"])
        if run["binding"] != binding or run["origin"] != "lock-acquired":
            raise ValueError("source/target/policy or lock origin mismatch")
        kind = run["kind"]
        if kind not in {"measured", "additive_estimate"}:
            raise ValueError("unknown evidence kind")
        if kind == "additive_estimate":
            text(run["basis_ref"])
        samples = run["checkpoints"]
        expected = policy["checkpoints"]
        if not isinstance(samples, list) or len(samples) != len(expected):
            raise ValueError("checkpoint coverage incomplete")
        previous = 0  # Elapsed origin is lock acquisition, per issue 3878 (2026).
        for checkpoint, sample in zip(expected, samples):
            if any(sample[key] != checkpoint[key] for key in ("name", "boundary")):
                raise ValueError("checkpoint order or exact boundary mismatch")
            elapsed = number(sample["elapsed_s"])
            if elapsed < previous:
                raise ValueError("checkpoint elapsed times are not monotonic")
            io = io_costs(sample["io"], checkpoint["required_io"], previous, elapsed)
            # Issue 3878 (2026): each guard retains its reserve independently.
            allowance = policy["cap_s"] - checkpoint["reserve_s"]
            margin = allowance - elapsed
            comparison = "BELOW" if margin > 0 else "AT_OR_ABOVE"
            status = ("PASS" if margin > 0 else "FAIL") if kind == "measured" else "ESTIMATED"
            result["checkpoints"].append({
                "name": checkpoint["name"], "boundary": checkpoint["boundary"],
                "phase_start_s": previous, "elapsed_s": elapsed,
                "allowance_s": allowance, "margin_s": margin,
                "comparison": comparison, "status": status, "io": io})
            previous = elapsed
        result["status"] = combine([p["status"] for p in result["checkpoints"]])
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        # Partial evidence is retained, but cannot produce a qualified verdict.
        result["reason"] = str(error)
    return result


def combine(statuses):
    if not statuses:
        return "NOT_EVALUATED"
    for status in ("FAIL", "NOT_EVALUATED", "ESTIMATED"):
        if status in statuses:
            return status
    return "PASS"


def evaluate(policy, binding, runs):
    """Compare every sample independently; totals and averages are not guards."""
    validate_policy(policy, binding)
    if not isinstance(runs, list):
        raise TypeError("runs must be a list")
    results = [assess_run(policy, binding, run) for run in runs]
    return {"status": combine([run["status"] for run in results]),
            "runtime_readiness": "NOT_ESTABLISHED", "policy": policy,
            "binding": binding, "runs": results}


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args(argv)
    try:
        packet = json.loads(args.evidence.read_text(), object_pairs_hook=unique)
        result = evaluate(packet["policy"], packet["binding"], packet["runs"])
        # Evidence is retained verbatim; non-finite values are invalid JSON output.
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0 if result["status"] == "PASS" else 1
    except (OSError, KeyError, TypeError, ValueError, OverflowError) as error:
        print(json.dumps({"status": "NOT_EVALUATED", "reason": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
