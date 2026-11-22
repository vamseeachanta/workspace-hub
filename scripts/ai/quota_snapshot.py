"""Write a timestamped quota snapshot atomically without querying providers."""

import argparse
import json
import os
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path


def write_snapshot(data, destination, now):
    if not isinstance(data, dict) or not isinstance(data.get("agents"), list):
        raise TypeError("snapshot requires an agents array")
    # RFC 3339 (2002), section 5.6: UTC Internet profile of ISO 8601.
    stamp = now.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    data = dict(data)
    agents = []
    for entry in data["agents"]:
        if not isinstance(entry, dict):
            raise TypeError("agent entry must be a mapping")
        entry = dict(entry)
        entry["source"] = entry.get("source") or "unavailable"
        # Only these existing provider source contracts represent live observations.
        # Unknown/cached evidence keeps its original date; null means not established.
        if entry["source"] == "app-server-live":
            entry.setdefault("as_of", stamp)
        else:
            entry.setdefault("as_of", None)
        agents.append(entry)
    data["agents"] = agents
    data["generated_at"] = {"iso8601": stamp, "epoch": int(now.timestamp())}
    data["timestamp"] = stamp  # Compatibility with the existing statusline consumer.
    encoded = json.dumps(data, indent=2, allow_nan=False) + "\n"
    destination.parent.mkdir(parents=True, exist_ok=True)
    # The temporary and final files share a directory and filesystem for rename.
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent,
                                     prefix=".quota-", suffix=".partial", delete=False) as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
        temporary = stream.name
    try:
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        write_snapshot(json.load(sys.stdin), args.destination, datetime.now(UTC))
    except (ValueError, TypeError, OSError):
        print("quota snapshot: invalid input or atomic write failed; previous file retained", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
