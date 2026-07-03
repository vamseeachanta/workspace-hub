from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
assert (REPO_ROOT / "config").is_dir(), "_pathnorm_shim moved? repo-root resolution broke"

DRIVE_INDEX_SEARCH = REPO_ROOT / "scripts/data/drive-index-search"
if str(DRIVE_INDEX_SEARCH) not in sys.path:
    sys.path.insert(0, str(DRIVE_INDEX_SEARCH))

from pathnorm import canonicalize, canonicalize_tree, is_canonical, load_alias_map  # noqa: E402,F401
