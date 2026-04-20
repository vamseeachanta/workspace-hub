"""Ensure `scripts/` is on sys.path so `import gtm.prospect_adapter` works.

This makes the tests runnable via `uv run pytest scripts/gtm/tests/...`
from the repo root without needing an installed package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
