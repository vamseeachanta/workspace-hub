#!/usr/bin/env python3
"""Classify project skill ownership without following native-root entries.

CLI: native/absent exit 0; blocked exit 2. Ownership is not readiness.
"""
from __future__ import annotations

import os
import stat
import sys
from pathlib import Path


def classify_native_root(repo_root: Path) -> str:
    """Inspect exact components beneath the caller's selected repository root."""
    if os.name not in ("posix", "nt"):
        return "blocked"
    for entry in (repo_root / ".agents", repo_root / ".agents" / "skills"):
        try:
            metadata = os.lstat(entry)
        except FileNotFoundError:
            return "absent"
        except OSError:
            return "blocked"
        if not stat.S_ISDIR(metadata.st_mode):
            return "blocked"
        if os.name == "nt":
            attributes = getattr(metadata, "st_file_attributes", None)
            if attributes is None or attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                return "blocked"
    return "native"


def main() -> int:
    state = classify_native_root(Path(sys.argv[1])) if len(sys.argv) == 2 else "blocked"
    print(state)
    return 2 if state == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
