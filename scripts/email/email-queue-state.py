#!/usr/bin/env python3
"""Executable wrapper for the importable email queue-state CLI."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.email.state.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
