"""Capacity arithmetic and read-only phone-media verification; no backup writes.

Sources: rclone check/about command documentation, retrieved 2026-10-22:
https://rclone.org/commands/rclone_check/
https://rclone.org/commands/rclone_about/
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path


def capacity_plan(free_bytes, next_bytes, growth_bytes_per_month, months, reserve_bytes):
    """Apply byte accounting; all policy values are required caller inputs.

    Independent derivation: projected new bytes = next + monthly growth * months;
    required free bytes = projected new bytes + retained free reserve.
    rclone about documents free space in bytes; no unit conversion is applied.
    READY means arithmetic fits these inputs, not evidence of a verified backup.
    """
    values = (free_bytes, next_bytes, growth_bytes_per_month, months, reserve_bytes)
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("capacity inputs must be nonnegative integers")
    required = next_bytes + growth_bytes_per_month * months + reserve_bytes
    return {"required_bytes": required, "headroom_bytes": free_bytes - required,
            "status": "READY" if free_bytes >= required else "BLOCKED"}


def _validate_source(source):
    """Reject absent, empty, linked or special-file archives before remote access."""
    source = Path(source)
    if not source.is_absolute() or source.is_symlink() or not source.is_dir():
        raise ValueError("source must be an absolute, real, nonempty directory")
    count = 0
    # os.walk onerror avoids silently accepting an unreadable subtree.
    def raise_walk_error(error):
        raise error

    for root, dirs, files in os.walk(source, followlinks=False, onerror=raise_walk_error):
        for name in dirs + files:
            entry = Path(root) / name
            if entry.is_symlink() or not (entry.is_file() or entry.is_dir()):
                raise ValueError("archive contains a linked or special entry")
        count += len(files)
    if not count:
        raise ValueError("source contains no media files")
    return source.resolve()


def _notify(alert_command, timeout_seconds):
    """Execute a configured notification adapter without shell interpolation."""
    try:
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("notification deadline is not configured")
        # One argument is the adapter contract; the input deadline also bounds alerts.
        result = subprocess.run(
            [alert_command, "Phone-media verification failed; inspect the user journal."],
            check=False, timeout=timeout_seconds,
        )
        if result.returncode:
            raise ValueError("notification adapter returned failure")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        print("phone-media notification failed; inspect the user journal", file=sys.stderr)


def verify(source, remote, timeout_seconds, alert_command):
    """Compare full contents both ways, preserving originals and remote data."""
    try:
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout must be positive and finite")
        if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*:[^\r\n]+", remote):
            raise ValueError("remote must name a configured remote and archive prefix")
        if not remote.split(":", 1)[1].strip("/ "):
            raise ValueError("remote archive prefix must not be empty")
        source = _validate_source(source)
        # rclone check docs: --download compares contents without relying on hashes;
        # omitting --one-way detects destination-only files too. Neither copy nor
        # sync is invoked. One checker/transfer is an explicit resource policy.
        result = subprocess.run(
            ["rclone", "check", str(source), remote, "--download",
             "--checkers", "1", "--transfers", "1"],
            check=False, timeout=timeout_seconds,
            # Ambient global flags (notably filters) must not narrow coverage.
            # Preserve configured-remote credentials and the private config locator.
            env={key: value for key, value in os.environ.items()
                 if not key.startswith("RCLONE_") or key == "RCLONE_CONFIG"
                 or key.startswith("RCLONE_CONFIG_")},
        )
        if result.returncode == 0:
            print("phone-media verification passed")
            return 0
        print("phone-media verification failed; rclone reported a difference or error",
              file=sys.stderr)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        # Avoid repeating local paths, remote configuration or credential diagnostics.
        print(f"phone-media verification failed ({type(error).__name__})", file=sys.stderr)
    _notify(alert_command, timeout_seconds)
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="compare free bytes with an input projection")
    for name in ("free-bytes", "next-bytes", "growth-bytes-per-month", "months", "reserve-bytes"):
        plan.add_argument(f"--{name}", type=int, required=True)
    check = commands.add_parser("check", help="read-only full-content comparison")
    check.add_argument("--source", required=True)
    check.add_argument("--remote", required=True)
    check.add_argument("--timeout-seconds", type=float, required=True)
    check.add_argument("--alert-command", required=True,
                       help="notification executable accepting one message argument")
    args = parser.parse_args(argv)
    if args.command == "check":
        return verify(args.source, args.remote, args.timeout_seconds, args.alert_command)
    try:
        result = capacity_plan(args.free_bytes, args.next_bytes, args.growth_bytes_per_month,
                               args.months, args.reserve_bytes)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "READY" else 1


if __name__ == "__main__":
    sys.exit(main())
