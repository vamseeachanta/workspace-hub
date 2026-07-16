#!/usr/bin/env python3
import sys
from pathlib import Path


def _main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root / "src"))
    from workspace_hub.workstations.connection_command import main

    return main()


if __name__ == "__main__":
    raise SystemExit(_main())
