# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Automated research brief generator.

Queries document index + standards ledger + capability map and produces a
structured research brief YAML covering Steps 1-4 of the research-literature
skill workflow.
"""
import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import yaml


def query_document_index(
    index_path: str,
    category: str,
    subcategory: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Read a JSONL index file and return records matching category/subcategory.

    Reads line-by-line to handle 1M+ record files without loading all into RAM.
    """
    path = Path(index_path)
    if not path.exists():
        return []

    results: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            if len(results) >= limit:
                break
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("category") != category:
                continue
            if subcategory is not None and record.get("subcategory") != subcategory:
                continue
            results.append(record)
    return results


def query_standards_ledger(
    ledger_path: str,
    category: str,
) -> list[dict[str, Any]]:
    """Read a YAML standards ledger and return entries relevant to category.

    Returns an empty list if the file does not exist.
    """
    path = Path(ledger_path)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    standards = data.get("standards", [])
    return [s for s in standards if s.get("category") == category]


def query_capability_map(
    capmap_path: str,
    category: str,
) -> dict[str, list[str]]:
    """Read a YAML capability map and return implemented/gap function names.

    Returns ``{"implemented": [], "gaps": []}`` if the file does not exist.
    """
    empty: dict[str, list[str]] = {"implemented": [], "gaps": []}
    path = Path(capmap_path)
    if not path.exists():
        return empty

    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    functions = data.get("functions", [])
    implemented: list[str] = []
    gaps: list[str] = []
    for fn in functions:
        if fn.get("category") != category:
            continue
        name = fn.get("name", "")
        if fn.get("status") == "implemented":
            implemented.append(name)
        elif fn.get("status") == "gap":
            gaps.append(name)
    return {"implemented": implemented, "gaps": gaps}


def generate_brief(
    category: str,
    subcategory: str | None = None,
    index_path: str | None = None,
    ledger_path: str | None = None,
    capmap_path: str | None = None,
) -> dict[str, Any]:
    """Orchestrate queries and build a research brief dict.

    Missing optional source files return empty results rather than crashing.
    """
    default_index = "data/document-index/index.jsonl"

    documents = query_document_index(
        index_path or default_index,
        category,
        subcategory=subcategory,
    )
    standards = query_standards_ledger(ledger_path or "", category) if ledger_path else []
    capabilities = (
        query_capability_map(capmap_path, category) if capmap_path else {"implemented": [], "gaps": []}
    )

    by_source: dict[str, int] = dict(Counter(d.get("source", "unknown") for d in documents))

    recommended: list[str] = [
        f"Implement gap: {gap}" for gap in capabilities.get("gaps", [])
    ]

    return {
        "category": category,
        "subcategory": subcategory,
        "generated_at": date.today().isoformat(),
        "document_coverage": {
            "total_documents": len(documents),
            "by_source": by_source,
        },
        "relevant_standards": standards,
        "capability_status": {
            "implemented": capabilities.get("implemented", []),
            "gaps": capabilities.get("gaps", []),
        },
        "recommended_actions": recommended,
    }


def main() -> None:
    """CLI entry-point for the research brief generator."""
    parser = argparse.ArgumentParser(
        description="Generate a structured research brief YAML for a given category."
    )
    parser.add_argument("--category", required=True, help="Engineering category to query")
    parser.add_argument("--subcategory", default=None, help="Optional subcategory filter")
    parser.add_argument(
        "--index",
        default="data/document-index/index.jsonl",
        help="Path to document index JSONL",
    )
    parser.add_argument("--ledger", default=None, help="Path to standards ledger YAML")
    parser.add_argument("--capmap", default=None, help="Path to capability map YAML")
    parser.add_argument("--output", default=None, help="Output YAML file path")
    args = parser.parse_args()

    brief = generate_brief(
        category=args.category,
        subcategory=args.subcategory,
        index_path=args.index,
        ledger_path=args.ledger,
        capmap_path=args.capmap,
    )

    output_yaml = yaml.dump(brief, default_flow_style=False, sort_keys=False)

    if args.output:
        Path(args.output).write_text(output_yaml, encoding="utf-8")
        print(f"Research brief written to {args.output}")
    else:
        sys.stdout.write(output_yaml)


if __name__ == "__main__":
    main()
