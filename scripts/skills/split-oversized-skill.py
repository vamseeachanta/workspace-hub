#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Split oversized SKILL.md files into hub + sub-skill directories.

Detects H2/H3 section boundaries and mechanically splits skills so that
each resulting file is under 200 lines. Follows the aqwa-analysis hub
pattern: hub retains frontmatter, When to Use, Prerequisites, condensed
API table, and Related Skills. Sub-skills get Core Capabilities (by H3),
Integration Examples, Best Practices, and Troubleshooting.

Usage:
    uv run --no-project python scripts/skills/split-oversized-skill.py SKILL.md
    uv run --no-project python scripts/skills/split-oversized-skill.py --dry-run SKILL.md
    uv run --no-project python scripts/skills/split-oversized-skill.py --trim SKILL.md
    uv run --no-project python scripts/skills/split-oversized-skill.py --batch .claude/skills/engineering/ --min-lines 200
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

LINE_LIMIT = 200

# H2 sections that stay in the hub (everything else is extractable)
HUB_SECTIONS = {
    "when to use", "when to use this skill", "prerequisites",
    "key classes", "python api", "api", "industry standards",
    "related skills", "references", "version history", "resources",
    "quick start", "overview", "sub-skills",
}

# Sections extracted in --trim mode (appendix-like, lower priority)
TRIM_SECTIONS = {
    "troubleshooting", "integration examples", "best practices",
    "version history", "resources", "references", "advanced usage",
    "error handling", "metrics", "quick reference", "dependencies",
    "common tasks", "execution checklist",
}


@dataclass
class Section:
    """A parsed H2 section from a SKILL.md file."""
    heading: str
    level: int  # 2 or 3
    content: str
    line_count: int
    children: list[Section] = field(default_factory=list)


@dataclass
class SplitPlan:
    """Plan for how a skill will be split."""
    hub_sections: list[str]
    sub_skills: list[SubSkillPlan]
    warnings: list[str]


@dataclass
class SubSkillPlan:
    """Plan for a single sub-skill to be created."""
    dir_name: str
    name: str
    heading: str
    content: str
    line_count: int


def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    """Extract YAML frontmatter and body from SKILL.md content."""
    stripped = content.lstrip()
    if not stripped.startswith("---"):
        return None, content
    end = stripped.find("---", 3)
    if end == -1:
        return None, content
    try:
        meta = yaml.safe_load(stripped[3:end].strip())
    except yaml.YAMLError:
        return None, content
    if not isinstance(meta, dict):
        return None, content
    body = stripped[end + 3:].lstrip("\n")
    return meta, body


def parse_sections(body: str) -> tuple[str, list[Section]]:
    """Parse body into intro text + H2 sections with optional H3 children.

    Returns (intro_text, sections) where intro_text is any content before
    the first H2 heading (e.g. H1 title and description).
    """
    sections: list[Section] = []
    current_h2: Section | None = None
    current_h3: Section | None = None
    buffer: list[str] = []
    intro_lines: list[str] = []
    seen_first_h2 = False

    def flush_buffer(target: Section | None) -> None:
        nonlocal buffer
        if target is not None:
            target.content = "\n".join(buffer)
            target.line_count = len(buffer)
        buffer = []

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            if not seen_first_h2:
                intro_lines = buffer[:]
                buffer = []
                seen_first_h2 = True
            # Flush current H3 if any
            if current_h3 is not None:
                flush_buffer(current_h3)
                if current_h2 is not None:
                    current_h2.children.append(current_h3)
                current_h3 = None
            # Flush current H2
            if current_h2 is not None:
                if not current_h2.children:
                    flush_buffer(current_h2)
                else:
                    flush_buffer(None)
                sections.append(current_h2)

            heading = stripped[3:].strip()
            current_h2 = Section(heading=heading, level=2, content="", line_count=0)
            buffer = []
        elif stripped.startswith("### "):
            # Flush current H3
            if current_h3 is not None:
                flush_buffer(current_h3)
                if current_h2 is not None:
                    current_h2.children.append(current_h3)
            elif current_h2 is not None and buffer:
                # Content between H2 heading and first H3
                current_h2.content = "\n".join(buffer)
                current_h2.line_count = len(buffer)
                buffer = []

            heading = stripped[4:].strip()
            current_h3 = Section(heading=heading, level=3, content="", line_count=0)
            buffer = []
        else:
            buffer.append(line)

    # Flush remaining
    if current_h3 is not None:
        flush_buffer(current_h3)
        if current_h2 is not None:
            current_h2.children.append(current_h3)
    elif current_h2 is not None:
        flush_buffer(current_h2)

    if current_h2 is not None:
        sections.append(current_h2)

    if not seen_first_h2:
        intro_lines = buffer[:]

    return "\n".join(intro_lines).strip(), sections


def slugify(text: str) -> str:
    """Convert heading text to a directory-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:50]


def _total_section_lines(section: Section) -> int:
    """Total lines including children."""
    total = section.line_count + 1  # +1 for heading
    for child in section.children:
        total += child.line_count + 1
    return total


def plan_split(
    meta: dict,
    sections: list[Section],
    trim_only: bool = False,
) -> SplitPlan:
    """Decide which sections go to hub vs sub-skills."""
    hub_sections: list[str] = []
    sub_skills: list[SubSkillPlan] = []
    warnings: list[str] = []

    for section in sections:
        heading_lower = section.heading.lower()

        # Hub sections always stay
        if heading_lower in HUB_SECTIONS:
            hub_sections.append(section.heading)
            continue

        # In trim mode, only extract appendix-like sections
        if trim_only and heading_lower not in TRIM_SECTIONS:
            hub_sections.append(section.heading)
            continue

        # For Core Capabilities with H3 children, group children into sub-skills
        if section.children and not trim_only:
            # Group H3 children into chunks that fit under LINE_LIMIT
            current_chunk: list[Section] = []
            current_lines = 0

            for child in section.children:
                child_lines = child.line_count + 2  # +heading +blank
                if child_lines > LINE_LIMIT:
                    warnings.append(
                        f"WARNING: H3 section '{child.heading}' has {child_lines} lines "
                        f"(>{LINE_LIMIT}) — needs manual review"
                    )
                if current_lines + child_lines > LINE_LIMIT - 20 and current_chunk:
                    # Emit current chunk as sub-skill
                    sub_skills.append(_chunk_to_subskill(
                        current_chunk, meta, section.heading,
                    ))
                    current_chunk = []
                    current_lines = 0
                current_chunk.append(child)
                current_lines += child_lines

            if current_chunk:
                sub_skills.append(_chunk_to_subskill(
                    current_chunk, meta, section.heading,
                ))
        else:
            # Extract entire H2 section as a sub-skill
            content_lines = []
            content_lines.append(f"## {section.heading}")
            content_lines.append("")
            content_lines.append(section.content)
            for child in section.children:
                content_lines.append(f"### {child.heading}")
                content_lines.append("")
                content_lines.append(child.content)

            sub_skills.append(SubSkillPlan(
                dir_name=slugify(section.heading),
                name=f"{meta.get('name', 'unknown')}-{slugify(section.heading)}",
                heading=section.heading,
                content="\n".join(content_lines),
                line_count=len(content_lines),
            ))

    return SplitPlan(
        hub_sections=hub_sections,
        sub_skills=sub_skills,
        warnings=warnings,
    )


def _chunk_to_subskill(
    children: list[Section],
    meta: dict,
    parent_heading: str,
) -> SubSkillPlan:
    """Convert a group of H3 sections into a sub-skill plan."""
    if len(children) == 1:
        dir_name = slugify(children[0].heading)
        display_name = children[0].heading
    else:
        dir_name = slugify(children[0].heading)
        display_name = f"{children[0].heading} (+{len(children) - 1})"

    content_lines: list[str] = []
    for child in children:
        content_lines.append(f"## {child.heading}")
        content_lines.append("")
        content_lines.append(child.content)
        content_lines.append("")

    skill_name = f"{meta.get('name', 'unknown')}-{dir_name}"

    return SubSkillPlan(
        dir_name=dir_name,
        name=skill_name,
        heading=display_name,
        content="\n".join(content_lines),
        line_count=sum(c.line_count + 2 for c in children),
    )


def render_hub(
    meta: dict,
    sections: list[Section],
    sub_skills: list[SubSkillPlan],
    hub_section_names: list[str],
    intro_text: str = "",
) -> str:
    """Render the hub SKILL.md with condensed content and see_also."""
    # Update frontmatter
    meta["see_also"] = [s.name for s in sub_skills]

    lines: list[str] = []
    lines.append("---")
    lines.append(yaml.dump(meta, default_flow_style=False, sort_keys=False).rstrip())
    lines.append("---")

    # Preserve intro text (H1 title, description between frontmatter and first H2)
    if intro_text:
        lines.append("")
        lines.extend(intro_text.splitlines())
        lines.append("")
    else:
        name = meta.get("name", "Skill")
        lines.append(f"\n# {name.replace('-', ' ').title()}")
        lines.append("")

    # Hub sections (keep full content — these are retained sections)
    for section in sections:
        if section.heading in hub_section_names:
            lines.append(f"## {section.heading}")
            lines.append("")
            lines.extend(section.content.strip().splitlines())
            for child in section.children:
                lines.append(f"### {child.heading}")
                lines.append("")
                lines.extend(child.content.strip().splitlines())
            lines.append("")

    # Sub-skill references
    if sub_skills:
        lines.append("## Sub-Skills")
        lines.append("")
        for ss in sub_skills:
            lines.append(f"- [{ss.heading}]({ss.dir_name}/SKILL.md)")
        lines.append("")

    return "\n".join(lines)


def render_sub_skill(sub: SubSkillPlan, parent_meta: dict) -> str:
    """Render a sub-skill SKILL.md with proper frontmatter.

    Truncates content if it would exceed LINE_LIMIT.
    """
    meta = {
        "name": sub.name,
        "description": f"Sub-skill of {parent_meta.get('name', 'unknown')}: {sub.heading}.",
        "version": parent_meta.get("version", "1.0.0"),
        "category": parent_meta.get("category", "unknown"),
        "type": "reference",
        "scripts_exempt": True,
    }

    header_lines: list[str] = []
    header_lines.append("---")
    header_lines.append(yaml.dump(meta, default_flow_style=False, sort_keys=False).rstrip())
    header_lines.append("---")
    header_lines.append("")
    header_lines.append(f"# {sub.heading}")
    header_lines.append("")

    # Count actual header lines (yaml.dump may produce multiple lines)
    header_count = len("\n".join(header_lines).splitlines())
    content_lines = sub.content.strip().splitlines()
    max_content = LINE_LIMIT - header_count - 3  # reserve for truncation note + blank

    if len(content_lines) > max_content:
        content_lines = content_lines[:max_content]
        content_lines.append("")
        content_lines.append("*Content truncated — see parent skill for full reference.*")

    return "\n".join(header_lines + content_lines) + "\n"


def split_skill(skill_path: Path, dry_run: bool = False, trim: bool = False) -> list[str]:
    """Split a single SKILL.md. Returns list of log messages."""
    logs: list[str] = []
    content = skill_path.read_text(encoding="utf-8")
    line_count = len(content.splitlines())

    if line_count <= LINE_LIMIT:
        logs.append(f"SKIP: {skill_path} ({line_count} lines, under limit)")
        return logs

    meta, body = parse_frontmatter(content)
    if meta is None:
        logs.append(f"ERROR: {skill_path} has no valid frontmatter, skipping")
        return logs

    intro_text, sections = parse_sections(body)
    plan = plan_split(meta, sections, trim_only=trim)

    for warning in plan.warnings:
        logs.append(warning)

    if not plan.sub_skills:
        logs.append(f"SKIP: {skill_path} — no extractable sections found")
        return logs

    if dry_run:
        logs.append(f"DRY RUN: {skill_path} ({line_count} lines)")
        logs.append(f"  Would create {len(plan.sub_skills)} sub-skills:")
        for ss in plan.sub_skills:
            logs.append(f"    - {ss.dir_name}/SKILL.md ({ss.line_count} lines) — {ss.heading}")
        return logs

    # Write hub
    hub_content = render_hub(meta, sections, plan.sub_skills, plan.hub_sections, intro_text)
    skill_path.write_text(hub_content, encoding="utf-8")
    hub_lines = len(hub_content.splitlines())
    logs.append(f"HUB: {skill_path} ({line_count} → {hub_lines} lines)")

    if hub_lines > LINE_LIMIT:
        logs.append(f"  WARNING: hub still {hub_lines} lines — may need manual trimming")

    # Write sub-skills
    skill_dir = skill_path.parent
    for ss in plan.sub_skills:
        sub_dir = skill_dir / ss.dir_name
        sub_dir.mkdir(parents=True, exist_ok=True)
        sub_content = render_sub_skill(ss, meta)
        sub_path = sub_dir / "SKILL.md"
        sub_path.write_text(sub_content, encoding="utf-8")
        sub_lines = len(sub_content.splitlines())
        logs.append(f"  SUB: {sub_path.name} ({sub_lines} lines) — {ss.heading}")

        if sub_lines > LINE_LIMIT:
            logs.append(f"    WARNING: sub-skill {sub_lines} lines — needs manual review")

    return logs


def batch_split(root: Path, min_lines: int, dry_run: bool, trim: bool) -> list[str]:
    """Process all oversized skills under a directory."""
    logs: list[str] = []
    skills = sorted(root.rglob("SKILL.md"))

    for skill_path in skills:
        try:
            line_count = len(skill_path.read_text(encoding="utf-8").splitlines())
        except OSError:
            continue
        if line_count > min_lines:
            logs.extend(split_skill(skill_path, dry_run=dry_run, trim=trim))

    return logs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split oversized SKILL.md files into hub + sub-skills"
    )
    parser.add_argument("path", nargs="?", help="Path to SKILL.md or directory for --batch")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing files")
    parser.add_argument("--trim", action="store_true",
                        help="Extract only appendix sections (for Tier 4 marginal skills)")
    parser.add_argument("--batch", type=str,
                        help="Process all oversized skills under this directory")
    parser.add_argument("--min-lines", type=int, default=LINE_LIMIT,
                        help="Minimum line count for batch processing")
    args = parser.parse_args()

    if args.batch:
        root = Path(args.batch).resolve()
        if not root.exists():
            print(f"Error: {root} does not exist", file=sys.stderr)
            return 2
        logs = batch_split(root, args.min_lines, args.dry_run, args.trim)
    elif args.path:
        skill_path = Path(args.path).resolve()
        if not skill_path.exists():
            print(f"Error: {skill_path} does not exist", file=sys.stderr)
            return 2
        logs = split_skill(skill_path, dry_run=args.dry_run, trim=args.trim)
    else:
        parser.print_help()
        return 2

    for log in logs:
        print(log)

    return 0


if __name__ == "__main__":
    sys.exit(main())
