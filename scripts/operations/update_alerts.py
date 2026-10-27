"""Local pending/acknowledged failure view; see the operations README.

Reads only explicitly supplied journals. No notification transport is installed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Local CLI contract: operations README, "Failure alert journals".
DIAGNOSTIC_LIMIT = 20
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
# Hexadecimal SHA-256 IDs have the length produced by the standard library.
ID_PATTERN = re.compile(r"sha256:[0-9a-f]{%d}" % len(hashlib.sha256().hexdigest()))


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.strptime(value, TIMESTAMP_FORMAT)
        return parsed.strftime(TIMESTAMP_FORMAT) == value
    except ValueError:
        return False


def _unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("non-finite value")


def _event_id(event: dict) -> str:
    canonical = json.dumps(
        event, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _valid_event(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("status") not in ("pass", "fail"):
        return False
    if not isinstance(value.get("job"), str) or not value["job"].strip():
        return False
    if not _valid_timestamp(value.get("ts")):
        return False
    return all(
        isinstance(value[key], str)
        for key in ("source", "tool", "failure", "rollback", "details")
        if key in value
    )


def _valid_ack(value: object) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"id", "acknowledged_at"}
        and isinstance(value["id"], str)
        and ID_PATTERN.fullmatch(value["id"]) is not None
        and _valid_timestamp(value["acknowledged_at"])
    )


def _distinct_paths(events: Path, acknowledgements: Path) -> None:
    if events.resolve() == acknowledgements.resolve() or (
        events.exists() and acknowledgements.exists() and events.samefile(acknowledgements)
    ):
        raise ValueError("journal paths must be distinct")


def _load(events: Path, acknowledgements: Path) -> tuple[dict, set[str], set[str]]:
    _distinct_paths(events, acknowledgements)
    failures = {}
    acknowledged = set()
    diagnostics = []
    diagnostic_count = 0
    for kind, path, valid in (
        ("notifications", events, _valid_event),
        ("acknowledgements", acknowledgements, _valid_ack),
    ):
        try:
            stream = path.open("rb")
        except FileNotFoundError:
            if kind == "acknowledgements":
                continue
            raise
        with stream:
            # JSONL line numbers start at one, including malformed/blank rows.
            for line_number, raw in enumerate(stream, start=1):
                try:
                    value = json.loads(
                        raw.decode("utf-8"), object_pairs_hook=_unique_object,
                        parse_constant=_reject_constant,
                    )
                    if not valid(value):
                        raise ValueError("invalid record")
                    if kind == "notifications":
                        identity = _event_id(value)
                        if value["status"] == "fail":
                            failures.setdefault(identity, {"id": identity, "event": value})
                    else:
                        acknowledged.add(value["id"])
                except (ValueError, UnicodeError, RecursionError):
                    diagnostic_count += 1
                    if len(diagnostics) < DIAGNOSTIC_LIMIT:
                        reason = "invalid event" if kind == "notifications" else "invalid acknowledgement"
                        diagnostics.append({"journal": kind, "line": line_number, "reason": reason})
    view = {
        "pending": [alert for identity, alert in failures.items() if identity not in acknowledged],
        "diagnostics": diagnostics,
        "diagnostic_count": diagnostic_count,
    }
    return view, set(failures), acknowledged


def read_pending(notifications: Path, acknowledgements: Path) -> dict:
    """Return unique unacknowledged failures and bounded, payload-free diagnostics."""
    view, _, _ = _load(Path(notifications), Path(acknowledgements))
    return view


def acknowledge(notifications: Path, acknowledgements: Path, identity: str, at: str) -> bool:
    """Append a known failure ID once; never open the event journal for writing.

    Returns false on replay. Callers must serialize writers and keep journal
    paths stable during a call; this local CLI does not provide a shared lock.
    """
    if not _valid_timestamp(at):
        raise ValueError("invalid acknowledgement timestamp")
    view, known, acknowledged = _load(Path(notifications), Path(acknowledgements))
    if view["diagnostic_count"]:
        raise ValueError("journals contain malformed records")
    if identity not in known:
        raise ValueError("unknown failure identity")
    if identity in acknowledged:
        return False
    record = json.dumps({"id": identity, "acknowledged_at": at}, sort_keys=True) + "\n"
    # a+b preserves the journal and allows checking its final byte. A missing
    # final delimiter is appended before the new record; no old byte is changed.
    with Path(acknowledgements).open("a+b") as stream:
        stream.seek(0, 2)  # SEEK_END, as defined by the standard binary I/O API.
        if stream.tell():
            stream.seek(-1, 2)  # Inspect the last byte, without rewriting it.
            if stream.read() != b"\n":
                stream.write(b"\n")
        stream.write(record.encode("utf-8"))
    return True


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # Invalid arguments can contain private paths or other supplied values.
        self.exit(2, "error: invalid arguments; use --help\n")


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(prog="update_alerts", description=__doc__)
    parser.add_argument("--notifications", type=Path, required=True)
    parser.add_argument("--acknowledgements", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("pending", help="list unacknowledged failures as JSON")
    ack = commands.add_parser("ack", help="append an acknowledgement for a failure ID")
    ack.add_argument("identity")
    ack.add_argument("--at", help="UTC timestamp in YYYY-MM-DDTHH:MM:SSZ form; defaults to now")
    args = parser.parse_args(argv)
    try:
        if args.command == "pending":
            result = read_pending(args.notifications, args.acknowledgements)
            code = int(bool(result["diagnostic_count"]))
        else:
            at = args.at if args.at is not None else datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT)
            appended = acknowledge(args.notifications, args.acknowledgements, args.identity, at)
            result = {"acknowledged": args.identity, "appended": appended}
            code = 0
    except OSError:
        print("error: journal I/O failed", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    # JSON escaping keeps supplied control characters inert in terminal output.
    print(json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
