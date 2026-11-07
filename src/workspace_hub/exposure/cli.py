"""Exact identity lookup and surface projection for report/page consumers."""

from __future__ import annotations

import argparse
import json
import sys

from .policy import ExposureError, Surface, check_names, expose, forbidden_names
from .registry import load_registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry", help="Private JSON path (default: DATA_REGISTRY_PATH)"
    )
    parser.add_argument("--id", required=True, help="Exact registry identity")
    parser.add_argument(
        "--surface", required=True, help="One of: " + ", ".join(Surface)
    )
    parser.add_argument(
        "--client-id", help="Recipient identity from trusted caller context"
    )
    args = parser.parse_args(argv)
    try:
        surface = Surface(args.surface)
        records = load_registry(args.registry)
        if args.id not in records:
            raise ExposureError("Registry identity not found")
        output = expose(records[args.id], surface, client_id=args.client_id)
        for record in records.values():
            check_names(output, forbidden_names(record, surface, args.client_id))
        rendered = json.dumps(output, ensure_ascii=False, allow_nan=False)
    except (ExposureError, ValueError):
        print(
            "Exposure refused: check surface, recipient and private registry policy.",
            file=sys.stderr,
        )
        return 2
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
