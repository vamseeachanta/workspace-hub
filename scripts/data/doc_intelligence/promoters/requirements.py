"""Requirements promoter — renders extracted requirements as Python string constants."""

import textwrap
from collections import defaultdict
from pathlib import Path
from typing import List

from scripts.data.doc_intelligence.promoters.coordinator import (
    PromoteResult,
    register_promoter,
)
from scripts.data.doc_intelligence.promoters.text_utils import (
    content_hash,
    source_citation,
    write_atomic,
)

OUTPUT_DIR = Path("data/standards/promoted")
_WRAP_WIDTH = 70


def _wrap_requirement_text(text: str) -> str:
    """Format requirement text as a parenthesized string constant.

    Short strings (<=_WRAP_WIDTH) are rendered as a simple quoted string.
    Longer strings use parenthesized continuation with ~70-char lines.
    """
    if len(text) <= _WRAP_WIDTH:
        return f'"{text}"'

    wrapped = textwrap.wrap(text, width=_WRAP_WIDTH)
    parts = [f'    "{line}"' for line in wrapped]
    return "(\n" + "\n".join(parts) + "\n)"


def _render_module(domain: str, records: List[dict]) -> str:
    """Render a list of requirement records into a Python module string.

    Each requirement becomes a REQ_NNN string constant with a source
    citation docstring.
    """
    if not records:
        return ""

    lines: list[str] = []

    # Requirement assignments
    for idx, rec in enumerate(records, start=1):
        label = f"REQ_{idx:03d}"
        text = rec.get("text", "")
        value_str = _wrap_requirement_text(text)
        lines.append(f"{label} = {value_str}")

        citation = source_citation(rec.get("source", {}))
        lines.append(f'"""Source: {citation}"""')
        lines.append("")

    body = "\n".join(lines)

    # Build module docstring
    header = (
        f'"""Requirements — {domain} — '
        f"auto-promoted from doc-intelligence.\n"
        f"\n"
        f"# content-hash: {content_hash(body)}\n"
        f'"""\n\n'
    )
    return header + body


def promote_requirements(
    records: List[dict],
    project_root: Path,
    dry_run: bool = False,
) -> PromoteResult:
    """Group requirement records by domain and write one module per domain.

    Args:
        records: JSONL records from requirements.jsonl.
        project_root: Workspace root for output path resolution.
        dry_run: If True, report what would be written without writing.

    Returns:
        PromoteResult with written/skipped/error lists.
    """
    result = PromoteResult()

    if not records:
        return result

    # Group by domain
    by_domain: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        domain = rec.get("domain", "general")
        by_domain[domain].append(rec)

    for domain, domain_records in sorted(by_domain.items()):
        content = _render_module(domain, domain_records)
        if not content:
            continue

        out_path = (
            project_root / OUTPUT_DIR / domain / "requirements.py"
        )
        written = write_atomic(out_path, content, dry_run=dry_run)
        target = str(out_path)
        if written:
            result.files_written.append(target)
        else:
            result.files_skipped.append(target)

    return result


register_promoter("requirements", promote_requirements)
