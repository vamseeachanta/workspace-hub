"""Definitions promoter — renders JSONL definition records into domain glossary YAML files."""

from collections import defaultdict
from pathlib import Path
from typing import List, Tuple

from scripts.data.doc_intelligence.promoters.coordinator import (
    PromoteResult,
    register_promoter,
)
from scripts.data.doc_intelligence.promoters.text_utils import (
    content_hash,
    source_citation,
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


def render_glossary_yaml(records: List[dict], domain: str) -> str:
    """Render a list of definition records into a glossary YAML string.

    Generates YAML manually via string formatting to avoid yaml.dump
    quirks with multiline strings and quoting.
    """
    lines: List[str] = []

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

    lines.append(f"# Glossary — {domain}")
    lines.append(f"# content_hash: {chash}")
    lines.append("# Auto-promoted from doc-intelligence indexes. Do not edit manually.")
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

    # Group records by domain
    by_domain: dict[str, List[dict]] = defaultdict(list)
    for rec in records:
        domain = rec.get("domain", "unknown")
        by_domain[domain].append(rec)

    for domain, domain_records in sorted(by_domain.items()):
        out_path = (
            Path(project_root)
            / "data"
            / "standards"
            / "promoted"
            / domain
            / "glossary.yaml"
        )
        content = render_glossary_yaml(domain_records, domain)

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
