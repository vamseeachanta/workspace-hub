#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Legacy compatibility wrapper for the retired work-queue gate verifier. "
            "This path is kept only to fail fast with a clear redirect to the current workflow."
        )
    )
    parser.add_argument("wrk_id", nargs="?", help="Legacy WRK identifier")
    parser.add_argument("--stage5-check", dest="stage5_check", help="Legacy Stage 5 gate check WRK identifier")
    parser.add_argument("--phase", default="close", help="Legacy phase name")
    parser.add_argument("--workspace-root", help="Optional workspace root override")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    wrk_id = args.stage5_check or args.wrk_id or "<WRK-ID>"
    repo_root = Path(args.workspace_root).resolve() if args.workspace_root else Path(__file__).resolve().parents[2]
    guidance = [
        f"✖ legacy verify-gate-evidence path retired for {wrk_id}",
        "This script no longer implements the historical work-queue stage gate logic.",
        "Use the current workflow surfaces instead:",
        f"- {repo_root / 'AGENTS.md'}",
        f"- {repo_root / 'docs' / 'work-queue-workflow.md'}",
        f"- {repo_root / 'docs' / 'governance' / 'SESSION-GOVERNANCE.md'}",
        f"- {repo_root / 'docs' / 'ops' / 'legacy-claude-reference-map.md'}",
        "Recommended action: migrate callers away from scripts/work-queue/verify-gate-evidence.py.",
        "Exit code 2 is intentional: treat as legacy infrastructure retired, not as a passing gate.",
    ]
    sys.stderr.write("\n".join(guidance) + "\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
