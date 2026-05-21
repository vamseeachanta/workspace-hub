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
    SourceDocKeyError,
    content_hash,
    extract_source_doc_key,
    format_source_doc_key_header,
    source_citation,
    validate_source_doc_key,
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


def _render_module(
    domain: str, records: List[dict], doc_keys: List[str],
) -> str:
    """Render a list of requirement records into a Python module string.

    Emits both ``# content-hash:`` (output integrity) and one or more
    ``# source_doc_key:`` lines (source traceability) per the
    standards-codes-provenance-reuse contract §8.3.
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
    h = content_hash(body)
    # Self-loop guard: re-validate every doc_key against the body hash.
    for key in doc_keys:
        validate_source_doc_key(key, output_content_hash=h)

    sdk_header = format_source_doc_key_header(doc_keys)
    sdk_block = f"\n{sdk_header}" if sdk_header else ""

    # Build module docstring with content-hash and source_doc_key headers.
    header = (
        f'"""Requirements — {domain} — '
        f"auto-promoted from doc-intelligence.\n"
        f"\n"
        f"# content-hash: {h}{sdk_block}\n"
        f'"""\n\n'
    )
    return header + body


def promote_requirements(
    records: List[dict],
    project_root: Path,
    dry_run: bool = False,
) -> PromoteResult:
    """Group requirement records by domain and write one module per domain.

    Validates ``source.doc_key`` on every record before writing anything.
    A single invalid record fails the whole batch closed.

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

    # Validate every doc_key up front.
    validated: List[tuple[dict, str]] = []
    for rec in records:
        try:
            key = extract_source_doc_key(rec)
        except SourceDocKeyError as exc:
            result.errors.append(str(exc))
            return result
        validated.append((rec, key))

    # Group by domain, preserving keys alongside records.
    by_domain: dict[str, list[tuple[dict, str]]] = defaultdict(list)
    for rec, key in validated:
        domain = rec.get("domain", "general")
        by_domain[domain].append((rec, key))

    for domain, pairs in sorted(by_domain.items()):
        domain_records = [r for r, _ in pairs]
        domain_keys = [k for _, k in pairs]
        try:
            content = _render_module(domain, domain_records, domain_keys)
        except SourceDocKeyError as exc:
            result.errors.append(str(exc))
            return result
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
