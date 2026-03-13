#!/usr/bin/env python3
# ABOUTME: Extract formal worked examples from USNA EN400 manifest into structured YAML
# ABOUTME: Parses Example N.N patterns, extracts given/find/solution/answer blocks

"""
Usage:
    python extract-en400-examples.py [--out data/doc-intelligence/en400-worked-examples.yaml]
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
MANIFEST_PATH = (
    HUB_ROOT
    / "data/doc-intelligence/manifests/naval-architecture"
    / "USNA-EN400-Principles-Ship-Performance-2020.manifest.yaml"
)

# Chapter → topic mapping
CHAPTER_TOPICS = {
    "1": "engineering-fundamentals",
    "2": "hull-form-geometry",
    "3": "hydrostatics",
    "4": "stability",
    "5": "materials",
    "6": "ship-structure",
    "7": "resistance-powering",
    "8": "seakeeping",
    "9": "maneuverability",
    "10": "submarines",
}


def extract_example_block(text: str, example_id: str) -> Dict:
    """Extract a single worked example from section text."""
    # Find the example start
    pattern = rf"Example\s+{re.escape(example_id)}"
    match = re.search(pattern, text)
    if not match:
        return {}

    # Get text from example start to next Example or end
    start = match.start()
    next_example = re.search(r"Example\s+\d+\.\d+", text[start + len(match.group()):])
    if next_example:
        end = start + len(match.group()) + next_example.start()
    else:
        end = len(text)

    block = text[start:end].strip()

    # Extract structured parts
    result = {
        "raw_text": block[:2000],  # Cap at 2000 chars
    }

    # Try to find Given/Find/Solution structure
    given_match = re.search(r"(?i)given[:\s](.+?)(?=find|solution|$)", block, re.DOTALL)
    find_match = re.search(r"(?i)find[:\s](.+?)(?=given|solution|$)", block, re.DOTALL)
    solution_match = re.search(r"(?i)solution[:\s](.+?)$", block, re.DOTALL)

    if given_match:
        result["given"] = given_match.group(1).strip()[:500]
    if find_match:
        result["find"] = find_match.group(1).strip()[:500]
    if solution_match:
        result["solution"] = solution_match.group(1).strip()[:1000]

    # Extract numerical values from text (for parametrized tests)
    numbers = re.findall(
        r"(\d+[,.]?\d*)\s*(LT|ft|knots?|HP|lbs?|inches?|ft2|ft3|ft4|°F|degrees?|slugs?|in)",
        block,
    )
    if numbers:
        result["extracted_values"] = [
            {"value": float(n[0].replace(",", "")), "unit": n[1]}
            for n in numbers[:20]
        ]

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="data/doc-intelligence/en400-worked-examples.yaml",
    )
    args = parser.parse_args()

    with open(MANIFEST_PATH) as f:
        manifest = yaml.safe_load(f)

    sections = manifest.get("sections", [])

    # Find all formal examples
    examples = []
    seen_ids = set()

    for section in sections:
        text = section.get("text", "")
        page = section.get("source", {}).get("page", 0)

        # Find Example N.N patterns
        for match in re.finditer(r"Example\s+(\d+\.\d+)", text):
            example_id = match.group(1)
            # Deduplicate
            if example_id in seen_ids:
                continue
            seen_ids.add(example_id)

            chapter = example_id.split(".")[0]
            topic = CHAPTER_TOPICS.get(chapter, "unknown")

            block = extract_example_block(text, example_id)
            if not block:
                continue

            examples.append({
                "id": f"EN400-{example_id}",
                "example_number": example_id,
                "chapter": int(chapter),
                "topic": topic,
                "page": page,
                "source": "USNA-EN400-Principles-Ship-Performance-2020.pdf",
                **block,
            })

    # Sort by example number
    examples.sort(key=lambda x: [int(p) for p in x["example_number"].split(".")])

    output = {
        "metadata": {
            "source": "USNA EN400 Principles of Ship Performance (Summer 2020)",
            "total_examples": len(examples),
            "chapters_covered": sorted(set(e["chapter"] for e in examples)),
            "extraction_method": "regex on manifest sections",
        },
        "examples": examples,
    }

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = HUB_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False, width=120)

    print(f"Extracted {len(examples)} worked examples to {out_path}")
    print()
    for ch in sorted(set(e["chapter"] for e in examples)):
        topic = CHAPTER_TOPICS.get(str(ch), "?")
        ch_examples = [e for e in examples if e["chapter"] == ch]
        print(f"  Chapter {ch:2d} ({topic:25s}): {len(ch_examples)} examples")


if __name__ == "__main__":
    main()
