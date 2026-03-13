"""Procedures promoter — renders procedure records as YAML skill files."""

import re
from pathlib import Path
from typing import Optional

from scripts.data.doc_intelligence.promoters.coordinator import (
    PromoteResult,
    register_promoter,
)
from scripts.data.doc_intelligence.promoters.text_utils import (
    content_hash,
    sanitize_identifier,
    source_citation,
    write_atomic,
)


def _parse_procedure(record: dict) -> Optional[dict]:
    """Extract procedure title and numbered steps from a record.

    Returns a dict with keys: title, procedure_id, steps, source, domain.
    Returns None if the record cannot be parsed.
    """
    text = record.get("text", "")
    lines = text.strip().split("\n")
    if not lines:
        return None

    # Extract title from "Procedure: <title>" pattern
    title_match = re.match(r"^Procedure:\s*(.+)$", lines[0].strip())
    if not title_match:
        return None
    title = title_match.group(1).strip()

    # Extract numbered steps (lines starting with digit(s) followed by ".")
    steps = []
    for line in lines[1:]:
        step_match = re.match(r"^\d+\.\s*(.+)$", line.strip())
        if step_match:
            steps.append(step_match.group(1).strip())

    if not steps:
        return None

    procedure_id = sanitize_identifier(title)
    return {
        "title": title,
        "procedure_id": procedure_id,
        "steps": steps,
        "source": record.get("source", {}),
        "domain": record.get("domain", "unknown"),
    }


def _render_yaml(parsed: dict) -> str:
    """Render a parsed procedure as a YAML skill file.

    Output has YAML frontmatter (between --- delimiters) followed by
    a steps block.
    """
    citation = source_citation(parsed["source"])
    procedure_id = parsed["procedure_id"]
    title = parsed["title"]
    domain = parsed["domain"]
    steps = parsed["steps"]

    # Build the steps block for hashing (the semantic content)
    steps_lines = []
    for step in steps:
        steps_lines.append(f"  - {step}")
    steps_block = "\n".join(steps_lines)

    body_hash = content_hash(steps_block)

    # Build the frontmatter as a kebab-case name
    name = procedure_id.replace("_", "-")

    lines = [
        "---",
        f"name: {name}",
        f"description: {title} procedure from {citation}",
        "type: procedure",
        f"source: {citation}",
        f"domain: {domain}",
        f"content_hash: {body_hash}",
        "---",
        "",
        "steps:",
    ]
    lines.extend(steps_lines)
    lines.append("")  # trailing newline
    return "\n".join(lines)


def promote_procedures(
    records: list[dict], project_root: Path, dry_run: bool = False
) -> PromoteResult:
    """Promote procedure records to YAML skill files.

    Each procedure is written to:
        {project_root}/.claude/skills/engineering/{domain}/{procedure_id}.yaml
    """
    result = PromoteResult()

    for record in records:
        parsed = _parse_procedure(record)
        if parsed is None:
            continue

        domain = parsed["domain"]
        procedure_id = parsed["procedure_id"]
        out_dir = (
            project_root / ".claude" / "skills" / "engineering" / domain
        )
        out_path = out_dir / f"{procedure_id}.yaml"

        content = _render_yaml(parsed)
        written = write_atomic(out_path, content, dry_run=dry_run)
        if written:
            result.files_written.append(str(out_path))
        else:
            result.files_skipped.append(str(out_path))

    return result


register_promoter("procedures", promote_procedures)
