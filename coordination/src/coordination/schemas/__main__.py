"""CLI entrypoint: python -m coordination.schemas <file> [--json]"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from coordination.schemas import validate_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m coordination.schemas",
        description="Validate YAML state files against their Pydantic schemas.",
    )
    parser.add_argument("file", type=Path, help="Path to the YAML file to validate")
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        default=False,
        help="Output results as JSON",
    )

    args = parser.parse_args(argv)

    if not args.file.exists():
        msg = f"File not found: {args.file}"
        if args.json_output:
            print(json.dumps({"valid": False, "errors": [{"loc": [], "msg": msg, "type": "file_not_found"}]}))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 1

    errors = validate_file(args.file)

    if args.json_output:
        print(json.dumps({"valid": len(errors) == 0, "errors": errors}))
    else:
        if errors:
            print(f"INVALID: {args.file}", file=sys.stderr)
            for err in errors:
                loc = " -> ".join(str(x) for x in err["loc"]) if err["loc"] else "(root)"
                print(f"  {loc}: {err['msg']}", file=sys.stderr)
        else:
            print(f"VALID: {args.file}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
