#!/usr/bin/env python3
"""Convert Claude Code agent .md files to Hermes SKILL.md format.

Usage:
    uv run python scripts/skills/convert-agent-to-skill.py --input <agent-path> --output <skills-dir>
    uv run python scripts/skills/convert-agent-to-skill.py --batch <agents-dir> --output <skills-dir> [--include a,b,c]
    uv run python scripts/skills/convert-agent-to-skill.py --input <agent-path> --output <skills-dir> --dry-run

Converts Claude Code agent markdown files (with optional YAML frontmatter) into
Hermes-compatible SKILL.md format with proper frontmatter and category inference.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# Category inference rules — order matters (first match wins)
CATEGORY_RULES: list[tuple[str, str]] = [
    ("orcaflex", "engineering"),
    ("orcawave", "engineering"),
    ("aqwa", "engineering"),
    ("freecad", "engineering"),
    ("cad", "engineering"),
    ("gmsh", "engineering"),
    ("mesh", "engineering"),
    ("cathodic", "engineering"),
    ("cp", "engineering"),
    ("github", "development"),
    ("testing", "development"),
    ("sparc", "development"),
    ("devops", "development"),
    ("development", "development"),
    ("architecture", "development"),
    ("core", "development"),
    ("code_quality", "development"),
    ("data", "data"),
    ("analysis", "data"),
    ("documentation", "documentation"),
    ("security", "security"),
    ("performance", "development"),
]

# Directories to skip during batch conversion (Claude-specific, not useful as skills)
SKIP_DIRS = {
    "flow-nexus",
    "hive-mind",
    "swarm",
    "neural",
    "consensus",
    "templates",
    "optimization",
    "goal",
    "agent-management",
    "helpers",
    "web-test-module",
    "fault-tolerance",
}

# Files to skip
SKIP_FILES = {"todo.md", "AGENT-ARCHITECTURE.md"}


def parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Parse YAML frontmatter from markdown content.

    Returns (metadata_dict, body_content).
    """
    if not content.startswith("---"):
        return {}, content

    # Find closing ---
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return {}, content

    frontmatter_text = content[3:end_idx].strip()
    body = content[end_idx + 3:].strip()

    metadata: dict[str, str] = {}
    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # Strip quotes
            if value and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]
            metadata[key] = value

    return metadata, body


def infer_category(path: str) -> str:
    """Infer skill category from the file path."""
    path_lower = path.lower()
    for pattern, category in CATEGORY_RULES:
        if pattern in path_lower:
            return category
    return "general"


def extract_description(metadata: dict[str, str], body: str) -> str:
    """Extract description from metadata or first paragraph of body."""
    if "description" in metadata and metadata["description"]:
        desc = metadata["description"]
        # Truncate long descriptions
        if len(desc) > 200:
            desc = desc[:197] + "..."
        return desc

    # Fall back to first non-empty, non-heading paragraph
    for line in body.split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("```"):
            if len(line) > 200:
                line = line[:197] + "..."
            return line

    return "Converted from Claude agent file"


def derive_skill_name(path: Path, metadata: dict[str, str]) -> str:
    """Derive a skill name from the path or metadata."""
    if "name" in metadata and metadata["name"]:
        return metadata["name"]

    # Use stem of file or directory name
    if path.is_dir():
        return path.name
    return path.stem


def build_skill_content(
    name: str,
    category: str,
    description: str,
    body: str,
    tags: list[str] | None = None,
) -> str:
    """Build a SKILL.md file content."""
    if tags is None:
        tags = []

    # Make a title from the name
    title = name.replace("-", " ").replace("_", " ").title()

    tag_str = ", ".join(tags) if tags else ""

    skill = f"""---
name: {name}
version: 1.0.0
category: {category}
description: {description}
type: reference
tags: [{tag_str}]
scripts_exempt: true
---
# {title}

{body}
"""
    return skill


def convert_single_file(
    input_path: Path,
    output_dir: Path,
    dry_run: bool = False,
) -> Path | None:
    """Convert a single agent .md file to SKILL.md.

    Returns the output path if written, or None if skipped.
    """
    if input_path.name in SKIP_FILES:
        log.info("  SKIP (excluded file): %s", input_path)
        return None

    content = input_path.read_text(encoding="utf-8", errors="replace")
    metadata, body = parse_frontmatter(content)

    name = derive_skill_name(input_path, metadata)
    category = infer_category(str(input_path))
    description = extract_description(metadata, body)

    # Determine output path
    skill_dir = output_dir / name
    skill_file = skill_dir / "SKILL.md"

    if skill_file.exists() and not dry_run:
        log.info("  SKIP (exists): %s", skill_file)
        return None

    skill_content = build_skill_content(name, category, description, body)

    if dry_run:
        log.info("  DRY-RUN: would write %s (%d bytes)", skill_file, len(skill_content))
        return skill_file

    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(skill_content, encoding="utf-8")
    log.info("  CREATED: %s", skill_file)
    return skill_file


def convert_directory(
    input_dir: Path,
    output_dir: Path,
    dry_run: bool = False,
) -> list[Path]:
    """Convert a directory-based agent to a single SKILL.md.

    Concatenates README.md + other .md files into one skill body.
    """
    md_files = sorted(input_dir.glob("**/*.md"))
    if not md_files:
        log.info("  SKIP (no .md files): %s", input_dir)
        return []

    # README.md goes first
    readme_files = [f for f in md_files if f.name.lower() == "readme.md"]
    other_files = [f for f in md_files if f.name.lower() != "readme.md" and f.name not in SKIP_FILES]

    ordered = readme_files + other_files
    if not ordered:
        log.info("  SKIP (only excluded files): %s", input_dir)
        return []

    # Parse the first file for metadata
    first_content = ordered[0].read_text(encoding="utf-8", errors="replace")
    metadata, first_body = parse_frontmatter(first_content)

    # Concatenate all bodies
    bodies = [first_body]
    for f in ordered[1:]:
        content = f.read_text(encoding="utf-8", errors="replace")
        _, body = parse_frontmatter(content)
        if body.strip():
            rel = f.relative_to(input_dir)
            bodies.append(f"\n\n---\n\n## Source: {rel}\n\n{body}")

    combined_body = "\n".join(bodies)

    name = derive_skill_name(input_dir, metadata)
    category = infer_category(str(input_dir))
    description = extract_description(metadata, combined_body)

    # Build output
    skill_dir = output_dir / name
    skill_file = skill_dir / "SKILL.md"

    if skill_file.exists() and not dry_run:
        log.info("  SKIP (exists): %s", skill_file)
        return []

    skill_content = build_skill_content(name, category, description, combined_body)

    if dry_run:
        log.info("  DRY-RUN: would write %s (%d bytes, %d source files)",
                 skill_file, len(skill_content), len(ordered))
        return [skill_file]

    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(skill_content, encoding="utf-8")
    log.info("  CREATED: %s (%d source files)", skill_file, len(ordered))
    return [skill_file]


def convert_agent(
    input_path: Path,
    output_dir: Path,
    dry_run: bool = False,
) -> list[Path]:
    """Convert a single agent (file or directory) to SKILL.md."""
    if input_path.is_file():
        result = convert_single_file(input_path, output_dir, dry_run)
        return [result] if result else []

    if input_path.is_dir():
        return convert_directory(input_path, output_dir, dry_run)

    log.warning("Path not found: %s", input_path)
    return []


def batch_convert(
    agents_dir: Path,
    output_dir: Path,
    include: set[str] | None = None,
    dry_run: bool = False,
) -> list[Path]:
    """Convert all agents in a directory tree.

    Processes:
    - Top-level .md files as single-file agents
    - Top-level directories as directory-based agents
    """
    created: list[Path] = []

    if not agents_dir.is_dir():
        log.error("Agents directory not found: %s", agents_dir)
        return created

    # Process top-level entries
    entries = sorted(agents_dir.iterdir())

    for entry in entries:
        name = entry.stem if entry.is_file() else entry.name

        # Apply include filter
        if include and name not in include:
            log.info("  SKIP (not included): %s", entry.name)
            continue

        # Skip known non-useful dirs
        if entry.is_dir() and entry.name in SKIP_DIRS:
            log.info("  SKIP (excluded dir): %s", entry.name)
            continue

        # Skip non-md files
        if entry.is_file() and entry.suffix != ".md":
            continue

        # Skip known excluded files
        if entry.is_file() and entry.name in SKIP_FILES:
            log.info("  SKIP (excluded file): %s", entry.name)
            continue

        log.info("Converting: %s", entry)
        results = convert_agent(entry, output_dir, dry_run)
        created.extend(results)

    return created


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert Claude Code agent .md files to Hermes SKILL.md format"
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Single agent .md file or directory to convert",
    )
    parser.add_argument(
        "--batch",
        type=Path,
        help="Directory of agents to batch convert",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Target skills directory",
    )
    parser.add_argument(
        "--include",
        type=str,
        default=None,
        help="Comma-separated list of agent names to include (batch mode)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview conversions without writing files",
    )

    args = parser.parse_args()

    if not args.input and not args.batch:
        parser.error("Either --input or --batch is required")

    include_set = None
    if args.include:
        include_set = {s.strip() for s in args.include.split(",")}

    if args.batch:
        log.info("Batch converting: %s -> %s", args.batch, args.output)
        created = batch_convert(args.batch, args.output, include_set, args.dry_run)
    else:
        log.info("Converting: %s -> %s", args.input, args.output)
        created = convert_agent(args.input, args.output, args.dry_run)

    log.info("\n=== Summary ===")
    log.info("Skills created: %d", len(created))
    for p in created:
        log.info("  %s", p)

    return 0


if __name__ == "__main__":
    sys.exit(main())
