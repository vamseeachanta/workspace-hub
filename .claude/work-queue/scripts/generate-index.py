#!/usr/bin/env python3
from __future__ import annotations

import sys


def main() -> int:
    sys.stderr.write(
        "[retired] .claude/work-queue indexes are no longer generated; "
        "use notes/agent-work-queue.md from scripts/refresh-agent-work-queue.py\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
