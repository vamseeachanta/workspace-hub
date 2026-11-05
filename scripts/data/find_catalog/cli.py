"""Build a private catalog and find owner records by keyword."""

import argparse
import json
import os
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import yaml
from catalog_sources import EXPOSURES, load_config, records
from catalog_store import build, find


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=os.environ.get("FIND_CATALOG_CONFIG"))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("build", help="atomically refresh the configured private catalog")
    commands.add_parser("inventory", help="count source records without writing an index")
    search = commands.add_parser("find", help="find records containing every query term")
    search.add_argument("query")
    search.add_argument("--domain")
    search.add_argument("--source")
    search.add_argument("--exposure", choices=sorted(EXPOSURES))
    search.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)
    if args.config is None:
        parser.error("--config or FIND_CATALOG_CONFIG is required")
    try:
        config = load_config(args.config)
        if args.command == "build":
            result = build(config)
        elif args.command == "inventory":
            counts = Counter({source["id"]: 0 for source in config["sources"]})
            counts.update(row["source"] for row in records(config))
            result = dict(counts)
        else:
            result = find(config["database"], args.query, domain=args.domain,
                          source=args.source, exposure=args.exposure, limit=args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError, sqlite3.Error) as exc:
        # Source exceptions may contain private locators; keep details on the local CLI only.
        print(f"catalog error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
