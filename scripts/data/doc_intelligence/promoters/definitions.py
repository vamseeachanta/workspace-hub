"""Definitions promoter — renders JSONL definition records into domain glossary YAML files."""

from collections import defaultdict
from pathlib import Path
from typing import List, Tuple

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


def parse_definition(text: str) -> Tuple[str, str]:
    """Split 'Term: Definition text' on the first colon.

    Returns (term, definition). If no colon is found, returns (text, "").
    """
    if not text:
        return ("", "")
    if ":" not in text:
        return (text.strip(), "")
    term, definition = text.split(":", 1)
    return (term.strip(), definition.strip())


def render_glossary_yaml(
    records: List[dict],
    domain: str,
    doc_keys: List[str],
) -> str:
    """Render a list of definition records into a glossary YAML string.

    Emits canonical ``# content-hash:`` and ``# source_doc_key:`` comment-form
    headers per the standards-codes-provenance-reuse contract §8.3.
    """
    # Build the terms body first so we can hash it
    term_lines: List[str] = []
    term_lines.append("terms:")
    for rec in records:
        term, definition = parse_definition(rec.get("text", ""))
        source = source_citation(rec.get("source", {}))
        term_lines.append(f'  - term: "{_escape_yaml(term)}"')
        term_lines.append(f'    definition: "{_escape_yaml(definition)}"')
        term_lines.append(f'    source: "{_escape_yaml(source)}"')

    body = "\n".join(term_lines) + "\n"
    chash = content_hash(body)

    # Self-loop guard now that the body hash is known.
    for key in doc_keys:
        validate_source_doc_key(key, output_content_hash=chash)

    lines: List[str] = []
    lines.append(f"# Glossary — {domain}")
    lines.append(f"# content-hash: {chash}")
    sdk_header = format_source_doc_key_header(doc_keys)
    if sdk_header:
        lines.append(sdk_header)
    lines.append(
        "# Auto-promoted from doc-intelligence indexes. Do not edit manually."
    )
    lines.append("")
    lines.append(body)

    return "\n".join(lines)


def _escape_yaml(value: str) -> str:
    """Escape double quotes inside a YAML double-quoted string."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def promote_definitions(
    records: List[dict], project_root: Path, dry_run: bool = False
) -> PromoteResult:
    """Promote definition records into per-domain glossary YAML files.

    Validates ``source.doc_key`` on every record before writing anything.
    A single invalid record fails the whole batch closed.

    Args:
        records: List of definition dicts from definitions.jsonl.
        project_root: Workspace root; output goes under
            {project_root}/data/standards/promoted/{domain}/glossary.yaml
        dry_run: If True, report what would be written without writing.

    Returns:
        PromoteResult with written/skipped/error counts.
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
        domain = rec.get("domain", "unknown")
        by_domain[domain].append((rec, key))

    for domain, pairs in sorted(by_domain.items()):
        out_path = (
            Path(project_root)
            / "data"
            / "standards"
            / "promoted"
            / domain
            / "glossary.yaml"
        )
        domain_records = [r for r, _ in pairs]
        domain_keys = [k for _, k in pairs]
        try:
            content = render_glossary_yaml(domain_records, domain, domain_keys)
        except SourceDocKeyError as exc:
            result.errors.append(str(exc))
            return result

        try:
            written = write_atomic(out_path, content, dry_run=dry_run)
            if written:
                result.files_written.append(str(out_path))
            else:
                result.files_skipped.append(str(out_path))
        except OSError as exc:
            result.errors.append(f"{out_path}: {exc}")

    return result


register_promoter("definitions", promote_definitions)
