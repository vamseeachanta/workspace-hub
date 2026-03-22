#!/usr/bin/env python3
"""Generate canonical stage-number to stage-folder-name mapping.

Reads all 20 stage contract YAMLs from scripts/work-queue/stages/ and
outputs a structured YAML mapping to stdout.

Usage:
    python generate-stage-mapping.py              # print to stdout
    python generate-stage-mapping.py --write      # write to references/
"""

import argparse
import glob
import os
import re
import sys

import yaml

REPO = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
            )
        )
    )
)
STAGES_DIR = os.path.join(REPO, "scripts", "work-queue", "stages")
REFS_DIR = os.path.join(
    REPO, ".claude", "skills", "workspace-hub",
    "work-queue-orchestrator", "references",
)


def build_mapping():
    """Build canonical stage mapping from contract YAMLs."""
    pattern = os.path.join(STAGES_DIR, "stage-*-*.yaml")
    files = sorted(glob.glob(pattern))

    stages = []
    for filepath in files:
        filename = os.path.basename(filepath)
        match = re.match(r"stage-(\d{2})-(.+)\.yaml", filename)
        if not match:
            continue

        slug = match.group(2)
        with open(filepath) as f:
            contract = yaml.safe_load(f)

        rel_contract = os.path.relpath(filepath, REPO)
        micro_skill = (
            f".claude/skills/workspace-hub/stages/"
            f"stage-{contract['order']:02d}-{slug}.md"
        )

        stages.append({
            "order": contract["order"],
            "name": contract["name"],
            "slug": slug,
            "contract": rel_contract,
            "micro_skill": micro_skill,
            "weight": contract.get("weight", "light"),
            "human_gate": contract.get("human_gate", False),
            "invocation": contract.get("invocation", "task_agent"),
        })

    stages.sort(key=lambda s: s["order"])
    return {"stages": stages}


def main():
    parser = argparse.ArgumentParser(
        description="Generate canonical stage mapping"
    )
    parser.add_argument(
        "--write", action="store_true",
        help="Write output to references/stage-mapping.yaml",
    )
    args = parser.parse_args()

    mapping = build_mapping()
    output = yaml.dump(mapping, default_flow_style=False, sort_keys=False)

    if args.write:
        os.makedirs(REFS_DIR, exist_ok=True)
        dest = os.path.join(REFS_DIR, "stage-mapping.yaml")
        with open(dest, "w") as f:
            f.write(output)
        print(f"Written to {dest}", file=sys.stderr)
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
