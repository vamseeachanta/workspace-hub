#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Read-only publication evidence checks; no scheduler, network or Git writes.

Issue #3505 requires both a published fingerprint and green publish health.
This diagnostic inspects captured evidence, not installed scheduler state.
Exit zero only when every check passes; unavailable evidence is NOT_EVALUATED.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from functools import cache
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from equivalence_schema import (
    MACHINE_RE,
    require_rfc3339,
    validate_fingerprint,
)
from equivalence_state import (
    validate_publish_health,
)


class EvidenceUnavailable(RuntimeError):
    """A capture cannot be inspected; exception messages contain rule names only."""


@cache
def _matrix():
    """Reuse the matrix grader and its limits rather than creating another policy."""
    path = Path(__file__).resolve().parents[1] / "readiness/build-equality-matrix.py"
    spec = importlib.util.spec_from_file_location("publication_matrix", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _result(status, code):
    return {"status": status, "code": code}


def _overall(checks):
    statuses = {item["status"] for item in checks.values()}
    if "FAIL" in statuses:
        return "FAIL"
    return "NOT_EVALUATED" if "NOT_EVALUATED" in statuses else "PASS"


def _fresh(stamp, now):
    # Source: build-equality-matrix.py PUBLISH_STALE_H, publish-health contract
    # introduced in issue #3502 (2026). No independently chosen freshness limit.
    return timedelta() <= now - stamp <= timedelta(hours=_matrix().PUBLISH_STALE_H)


def _fingerprint(content, machine, now):
    value = validate_fingerprint(content)
    if value["machine_id"] != machine:
        raise ValueError("identity-mismatch")
    if not _fresh(require_rfc3339(value["ts"]), now):
        raise ValueError("fingerprint-time-invalid")
    return value


def assess(*, machine, published, local, health, report, now):
    """Assess known remote contents plus local captures at an explicit UTC instant.

    ``published=None`` means an inspected ref lacks the exact machine key.
    Unreadable refs must instead be marked NOT_EVALUATED by the caller.
    Other None arguments mean their capture is unavailable. Output never includes
    payloads, supplied identities, filesystem paths or exception text.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("as-of requires a timezone")
    checks = {}
    remote_fp = local_fp = receipt = None
    if published is None:
        checks["published_fingerprint"] = _result("FAIL", "absent-fingerprint")
    else:
        try:
            remote_fp = _fingerprint(published, machine, now)
            checks["published_fingerprint"] = _result("PASS", "published-fingerprint")
        except (ValueError, TypeError):
            checks["published_fingerprint"] = _result("FAIL", "invalid-published-fingerprint")

    if local is None or health is None:
        checks["local_publish"] = _result("NOT_EVALUATED", "local-capture-unavailable")
    else:
        try:
            local_fp = _fingerprint(local, machine, now)
            receipt = validate_publish_health(health)
            stamp = require_rfc3339(receipt["ts"])
            # Success and phase: equivalence_state.py validate_publish_health
            # and equivalence-sentinel.sh write-health contract (2026).
            if receipt["phase"] != "publish" or receipt["rc"] != 0:
                raise ValueError("publish-unsuccessful")
            if not _fresh(stamp, now) or stamp < require_rfc3339(local_fp["ts"]):
                raise ValueError("receipt-time-invalid")
            # Source: existing matrix PUBLISH_SLOW_S (issue #3502, 2026).
            if receipt["duration_s"] > _matrix().PUBLISH_SLOW_S:
                raise ValueError("publish-slow")
            if remote_fp is not None and remote_fp != local_fp:
                raise ValueError("fingerprint-mismatch")
            checks["local_publish"] = _result("PASS", "publish-succeeded")
        except (ValueError, TypeError):
            checks["local_publish"] = _result("FAIL", "invalid-local-publish")

    if report is None:
        checks["matrix_publish_health"] = _result("NOT_EVALUATED", "matrix-capture-unavailable")
    else:
        checks["matrix_publish_health"] = _check_matrix(report, machine, receipt, now)
    return {"status": _overall(checks), "checks": checks}


def _check_matrix(report, machine, receipt, now):
    try:
        if not isinstance(report, dict) or report.get("machine") != machine:
            return _result("FAIL", "matrix-identity-mismatch")
        generated = require_rfc3339(report.get("generated_at"))
        if not _fresh(generated, now):
            return _result("FAIL", "matrix-time-invalid")
        if not isinstance(report.get("dimensions"), dict):
            return _result("FAIL", "invalid-matrix")
        verdict = _matrix().publish_health_verdict(report, now=now)
        if verdict != "PUBLISH-OK":
            return _result("FAIL", verdict)
        if receipt is None:
            return _result("NOT_EVALUATED", "receipt-unavailable")
        dimension = report["dimensions"]["publish_health"]
        health_time = require_rfc3339(receipt["ts"])
        if (generated < health_time
                or require_rfc3339(dimension["last_publish_at"]) != health_time
                or dimension["last_publish_duration_s"] != receipt["duration_s"]
                or dimension["last_publish_rc"] != receipt["rc"]):
            return _result("FAIL", "receipt-mismatch")
        return _result("PASS", verdict)
    except (ValueError, TypeError, KeyError):
        return _result("FAIL", "invalid-matrix")


def _git(repo, *args):
    # Fixture/root isolation contract: inherited repository bindings must not
    # redirect an explicitly selected checkout. No commands here mutate Git.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    try:
        # Child-read bound follows the existing Windows renderer probe in
        # tests/readiness/test_windows_scheduler_single_source.py (2026).
        result = subprocess.run(["git", *args], cwd=repo, env=env,
                                capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise EvidenceUnavailable("git-read-unavailable") from None
    if result.returncode:
        raise EvidenceUnavailable(f"{args[0]}-unavailable")
    return result.stdout


def read_published(repo, ref, machine):
    """Read the exact regular blob in one pinned, locally available state commit.

    No fetch is performed. The caller is responsible for acquiring a current
    authorized snapshot. Git object names are pinned before reading the tree.
    """
    if not isinstance(machine, str) or not MACHINE_RE.fullmatch(machine):
        raise ValueError("invalid machine key")
    if not ref or ref.startswith("-"):
        raise ValueError("invalid state ref")
    revision = _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").decode("ascii").strip()
    tree = _git(repo, "ls-tree", "-z", revision)
    target = f"{machine}.json".encode()
    for entry in tree.split(b"\0"):
        meta, _, name = entry.partition(b"\t")
        if name != target:
            continue
        fields = meta.split()
        # Modes: existing equivalence_state.py _commit_fingerprint uses 100644.
        # Require a regular blob, never dereference a symlink or accept a subtree.
        if len(fields) != 3 or fields[:2] != [b"100644", b"blob"]:
            raise EvidenceUnavailable("invalid-state-entry")
        try:
            content = _git(repo, "cat-file", "blob", fields[2].decode("ascii")).decode("utf-8")
        except UnicodeError:
            raise EvidenceUnavailable("invalid-state-encoding") from None
        return content, revision
    return None, revision


def _read(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return None
    except UnicodeError:
        return ""  # Captured but invalid: fail rather than treating it as absent.


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--state-ref", required=True, help="locally available state ref or commit")
    parser.add_argument("--machine", required=True, help="exact registry key (never echoed)")
    parser.add_argument("--local-fingerprint", type=Path)
    parser.add_argument("--health", type=Path)
    parser.add_argument("--equality-report", type=Path)
    parser.add_argument("--as-of", help="RFC3339 evaluation time; defaults to current UTC")
    args = parser.parse_args(argv)
    try:
        now = require_rfc3339(args.as_of) if args.as_of else datetime.now(UTC)
        if not MACHINE_RE.fullmatch(args.machine):
            raise ValueError
    except (ValueError, TypeError):
        parser.error("invalid machine key or evaluation time")
    state = args.repo / ".claude/state"
    local = _read(args.local_fingerprint or state / "equivalence/local-fingerprint.json")
    health = _read(args.health or state / "equivalence/publish-health.json")
    raw_report = _read(args.equality_report or state / f"equality-{args.machine}.yaml")
    try:
        report = yaml.safe_load(raw_report) if raw_report is not None else None
        if raw_report is not None and report is None:
            report = {}  # An empty captured report is invalid, not unavailable.
    except yaml.YAMLError:
        report = {}
    remote_error = None
    revision = None
    try:
        published, revision = read_published(args.repo, args.state_ref, args.machine)
    except (EvidenceUnavailable, ValueError):
        published = None
        remote_error = "state-ref-unavailable"
    result = assess(machine=args.machine, published=published, local=local, health=health,
                    report=report, now=now)
    if remote_error:
        result["checks"]["published_fingerprint"] = _result("NOT_EVALUATED", remote_error)
        result["status"] = _overall(result["checks"])
    result["state_revision"] = revision
    print(json.dumps(result, indent=2))
    # CLI contract: success only when every evidence check passes.
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
