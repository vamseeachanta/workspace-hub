#!/usr/bin/env python3
"""CLI for querying federated doc-intelligence content indexes."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

_project_root = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
)
sys.path.insert(0, str(_project_root))

from scripts.data.doc_intelligence.query import (  # noqa: E402
    ALL_CONTENT_TYPES,
    format_full,
    format_stage2_brief,
    query_indexes,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Query federated doc-intelligence content indexes."
    )
    parser.add_argument(
        "--type",
        dest="content_type",
        choices=ALL_CONTENT_TYPES,
        default=None,
        help="Filter by content type",
    )
    parser.add_argument(
        "--domain", default=None, help="Filter by domain (exact match)"
    )
    parser.add_argument(
        "--keyword", default=None, help="Case-insensitive substring match"
    )
    parser.add_argument(
        "--stage2-brief",
        action="store_true",
        help="Concise output for Stage 2 injection",
    )
    parser.add_argument(
        "--full", action="store_true", help="Detailed output with source refs"
    )
    parser.add_argument(
        "--limit", type=int, default=20, help="Max results (default: 20)"
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Raw JSON output"
    )
    parser.add_argument(
        "--index-dir",
        default=str(_project_root / "data" / "doc-intelligence"),
        help="Index directory (default: data/doc-intelligence)",
    )

    args = parser.parse_args()
    index_dir = Path(args.index_dir)

    try:
        results = query_indexes(
            index_dir,
            content_type=args.content_type,
            domain=args.domain,
            keyword=args.keyword,
            limit=args.limit,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    if not results:
        if not args.json_output:
            print("No results found.", file=sys.stderr)
        else:
            print("[]")
        return 1

    if args.json_output:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif args.stage2_brief:
        domain_label = args.domain or "all"
        print(format_stage2_brief(results, domain_label))
    elif args.full:
        print(format_full(results))
    else:
        # Default: compact one-line-per-result
        for r in results:
            ct = r.get("_content_type", "?")
            text = r.get("text") or r.get("title") or r.get("caption") or ""
            text_preview = text[:80].replace("\n", " ")
            print(f"[{ct}] {text_preview}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
