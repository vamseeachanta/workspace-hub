"""Curate TDD fixtures from extraction reports.

Collects worked examples from YAML extraction reports, sets quality flags,
and merges deep records into worked_examples.jsonl (preferring deep over shallow).

Usage:
    uv run --no-project python scripts/data/doc_intelligence/curate_tdd_fixtures.py \
        --reports data/doc-intelligence/extraction-reports/naval-architecture \
        --jsonl data/doc-intelligence/worked_examples.jsonl
"""

import json
import os
from pathlib import Path

import yaml


def collect_examples_from_reports(reports_dir: str) -> list[dict]:
    """Read all extraction report YAMLs and collect worked examples."""
    examples = []
    for filename in sorted(os.listdir(reports_dir)):
        if not filename.endswith("-extraction-report.yaml"):
            continue
        filepath = os.path.join(reports_dir, filename)
        with open(filepath) as f:
            report = yaml.safe_load(f) or {}

        doc_name = report.get("document", filename)
        for ex in report.get("worked_examples", []):
            if not ex.get("expected_value"):
                continue
            has_inputs = (ex.get("input_count", 0) > 0)
            examples.append({
                "number": ex.get("number", "?"),
                "title": ex.get("title", ""),
                "source_book": doc_name,
                "expected_value": ex["expected_value"],
                "output_unit": ex.get("output_unit", ""),
                "input_count": ex.get("input_count", 0),
                "use_as_test": has_inputs and ex["expected_value"] is not None,
                "extraction_source": "deep",
                "domain": ex.get("domain", "naval-architecture"),
            })
    return examples


def merge_into_jsonl(
    deep_examples: list[dict],
    jsonl_path: str,
) -> dict:
    """Merge deep-extracted examples into JSONL, replacing shallow duplicates."""
    existing = []
    if os.path.exists(jsonl_path):
        with open(jsonl_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        existing.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

    # Build dedup key: (number, source_book)
    deep_keys = {
        (e["number"], e["source_book"]) for e in deep_examples
    }

    # Keep existing records that aren't overwritten by deep
    kept = [
        r for r in existing
        if (r.get("number"), r.get("source_book")) not in deep_keys
    ]

    merged = kept + deep_examples
    shallow_removed = len(existing) - len(kept)

    Path(jsonl_path).parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "w") as f:
        for record in merged:
            f.write(json.dumps(record, default=str) + "\n")

    return {
        "deep_added": len(deep_examples),
        "shallow_removed": shallow_removed,
        "total": len(merged),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Curate TDD fixtures")
    parser.add_argument("--reports", required=True)
    parser.add_argument("--jsonl", required=True)
    args = parser.parse_args()

    examples = collect_examples_from_reports(args.reports)
    print(f"Collected {len(examples)} examples from reports")
    testable = sum(1 for e in examples if e["use_as_test"])
    print(f"  Testable (use_as_test=True): {testable}")

    stats = merge_into_jsonl(examples, args.jsonl)
    print(f"Merged: {stats['deep_added']} deep, "
          f"{stats['shallow_removed']} shallow replaced, "
          f"{stats['total']} total")
