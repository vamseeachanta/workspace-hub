#!/usr/bin/env python3
"""Generate ship dimension template YAML for manual data entry.

Reads ship-plans-index.yaml and creates a template with null dimension
fields for every drawing-only plan (has_text: false).

Usage:
    uv run --no-project python scripts/data/doc-intelligence/generate-ship-dimension-template.py
    uv run --no-project python scripts/data/doc-intelligence/generate-ship-dimension-template.py --dry-run
"""

import argparse
import sys
from pathlib import Path

# Add project root to path for imports
_project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_project_root))

import yaml  # noqa: E402

from scripts.data.doc_intelligence.generate_ship_dimension_template import (  # noqa: E402
    build_template_document,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate ship dimension template for manual data entry.",
    )
    parser.add_argument(
        "--plans-index",
        type=Path,
        default=_project_root / "data" / "doc-intelligence" / "ship-plans-index.yaml",
        help="Path to ship-plans-index.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_project_root / "data" / "doc-intelligence" / "ship-dimensions.yaml",
        help="Output path for the dimension template",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print to stdout instead of writing to file",
    )
    args = parser.parse_args()

    if not args.plans_index.exists():
        print(f"Error: plans index not found: {args.plans_index}", file=sys.stderr)
        return 1

    with open(args.plans_index) as f:
        index_data = yaml.safe_load(f)

    plans = index_data.get("plans", [])
    doc = build_template_document(plans)

    output_yaml = yaml.dump(
        doc,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    if args.dry_run:
        print(output_yaml)
        print(f"\n# {doc['total_entries']} entries would be written", file=sys.stderr)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output_yaml)
        print(f"Wrote {doc['total_entries']} entries to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
