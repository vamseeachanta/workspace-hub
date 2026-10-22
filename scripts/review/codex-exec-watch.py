#!/usr/bin/env python3
"""Bound a Codex exec and stop on the stdin diagnostic reported in issue #3442.

Only the submit wrapper invokes this helper. Stderr is retained for its existing
failure classifier; stdout is discarded as before. No prompt is read from stdin.
"""

import argparse
import math
import os
import selectors
import signal
import subprocess
import time
from pathlib import Path

# Source: issue #3442 (2026), exact reproduction diagnostic. Exit 7 is the
# existing unavailable contract in scripts/review/cross-review.sh.
SIGNATURE = b"Reading additional input from stdin"
UNAVAILABLE = 7
# Internal scheduling choices, documented in docs/review/codex-stdin-regression.md;
# these are resource bounds, not measured version-compatibility criteria.
POLL_SECONDS = 0.1
TERM_GRACE_SECONDS = 1
READ_BYTES = 65536


def scan(chunk: bytes, pending: bytes) -> tuple[bool, bytes]:
    """Match a diagnostic line, including split writes and missing final newline."""
    lines = (pending + chunk).split(b"\n")
    for line in lines:
        if line.rstrip(b"\r") in (SIGNATURE, SIGNATURE + b"..."):
            return True, b""
    tail = lines[-1]
    # A long unterminated line cannot equal the diagnostic. Preserve that fact
    # with a sentinel until its newline, without accumulating arbitrary stderr.
    if len(tail) > len(SIGNATURE) + len(b"...\r"):
        tail = b"\0"
    return False, tail


def stop_group(process: subprocess.Popen) -> None:
    """Reap the leader and kill descendants even when the leader already exited."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=TERM_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        pass
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def watch(command: list[str], timeout: float, stderr: Path) -> int:
    with stderr.open("wb") as errors:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            deadline = time.monotonic() + timeout
            pending = b""
            with selectors.DefaultSelector() as selector:
                selector.register(process.stderr, selectors.EVENT_READ)
                while True:
                    remaining = max(0, deadline - time.monotonic())
                    events = selector.select(min(POLL_SECONDS, remaining))
                    for key, _ in events:
                        chunk = os.read(key.fd, READ_BYTES)
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        errors.write(chunk)
                        errors.flush()
                        matched, pending = scan(chunk, pending)
                        if matched:
                            return UNAVAILABLE
                    # Drain stderr after a fast exit before accepting its code.
                    if process.poll() is not None and not events:
                        code = process.returncode
                        return code if code >= 0 else 128 - code
                    if time.monotonic() >= deadline:
                        errors.write(b"Codex exec timed out\n")
                        return 124  # Existing timeout contract in submit-to-codex.sh.
        finally:
            stop_group(process)
            process.stderr.close()


def interrupted(signum, _frame):
    raise SystemExit(128 + signum)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, required=True)
    parser.add_argument("--stderr", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be finite and positive")
    command = args.command
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("a command is required")
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, interrupted)
    return watch(command, args.timeout, args.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
