"""Global pytest bootstrap for workspace-hub test collection."""
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
for rel in ("src", "scripts"):
    candidate = str(REPO_ROOT / rel)
    if candidate not in sys.path:
        sys.path.insert(0, candidate)
