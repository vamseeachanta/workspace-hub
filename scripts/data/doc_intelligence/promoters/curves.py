"""Curves promoter — scaffold Python modules and placeholder CSVs for figure references."""

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
    sanitize_identifier,
    source_citation,
    validate_source_doc_key,
    write_atomic,
)

# Placeholder CSV body — headers only, to be filled with digitized data.
# The provenance headers (# content-hash, # source_doc_key) are prepended
# at render time per the standards-codes-provenance-reuse contract §8.3.
_CSV_PLACEHOLDER_BODY = "x,y\n"


def _render_scaffold(
    domain: str, entries: list[dict], doc_keys: list[str],
) -> str:
    """Render a Python scaffold module for a single domain.

    Emits both:
    - ``# content-hash: <sha256>`` — output-integrity stamp over the body.
    - ``# source_doc_key: <algo>:<hex>`` — source-traceability field; one
      line per distinct source doc, sorted for determinism.
    """
    lines: list[str] = []
    lines.append(f'"""Curve interpolation scaffolds — {domain}.')
    lines.append("")
    lines.append("These functions will be populated when curve digitization "
                 "data becomes available.")
    lines.append('"""')
    lines.append("")
    lines.append("from pathlib import Path")
    lines.append("from typing import Optional")
    lines.append("")

    for entry in entries:
        caption = entry.get("caption") or entry.get("figure_id") or "unknown"
        figure_id = entry.get("figure_id") or ""
        citation = source_citation(entry["source"])
        curve_id = sanitize_identifier(caption)
        csv_rel = (
            f"data/standards/promoted/{domain}/curves/{curve_id}.csv"
        )
        lines.append(f"# Placeholder: {caption} ({figure_id})")
        lines.append(f"# Source: {citation}")
        lines.append(f"# CSV: {csv_rel}")
        lines.append("")

    body = "\n".join(lines)
    h = content_hash(body)
    # Self-loop guard: re-validate every doc_key now that the body hash is
    # known. An artifact cannot be its own source.
    for key in doc_keys:
        validate_source_doc_key(key, output_content_hash=h)

    header_parts = [f"# content-hash: {h}"]
    sdk_header = format_source_doc_key_header(doc_keys)
    if sdk_header:
        header_parts.append(sdk_header)
    return "\n".join(header_parts) + "\n" + body


def _render_placeholder_csv(doc_key: str) -> str:
    """Render the placeholder CSV body with provenance headers.

    The content-hash covers the placeholder body only (so existing
    idempotency semantics are preserved per-curve); the source_doc_key
    points at the figure's L1 source.
    """
    body_hash = content_hash(_CSV_PLACEHOLDER_BODY)
    # Self-loop guard on the per-curve placeholder body hash.
    validate_source_doc_key(doc_key, output_content_hash=body_hash)
    return (
        f"# content-hash: {body_hash}\n"
        f"# source_doc_key: {doc_key}\n"
        f"{_CSV_PLACEHOLDER_BODY}"
    )


def promote_curves(
    records: list[dict],
    project_root: Path,
    dry_run: bool = False,
) -> PromoteResult:
    """Scaffold Python modules and placeholder CSVs for curve references.

    Validates ``source.doc_key`` on every record before writing anything. A
    single invalid record fails the whole batch closed.

    Groups records by domain. For each domain:
      - Writes a Python scaffold at
        ``{project_root}/digitalmodel/src/digitalmodel/{domain_path}/curves.py``
      - Writes one placeholder CSV per curve at
        ``{project_root}/data/standards/promoted/{domain}/curves/{curve_id}.csv``

    Idempotent: skips files whose content already matches.
    """
    result = PromoteResult()
    if not records:
        return result

    # Validate all source_doc_keys up front. Any invalid record fails the
    # whole batch closed — partial promotion would emit artifacts without
    # verifiable provenance.
    validated: List[tuple[dict, str]] = []
    for rec in records:
        try:
            key = extract_source_doc_key(rec)
        except SourceDocKeyError as exc:
            result.errors.append(str(exc))
            return result
        validated.append((rec, key))

    # Group records (with their validated keys) by domain.
    by_domain: dict[str, list[tuple[dict, str]]] = defaultdict(list)
    for rec, key in validated:
        domain = rec.get("domain", "unknown")
        by_domain[domain].append((rec, key))

    for domain, pairs in by_domain.items():
        entries = [r for r, _ in pairs]
        domain_keys = [k for _, k in pairs]

        # Python scaffold
        domain_path = domain.replace("-", "_")
        py_rel = Path(
            f"digitalmodel/src/digitalmodel/{domain_path}/curves.py"
        )
        py_out = project_root / py_rel
        try:
            scaffold = _render_scaffold(domain, entries, domain_keys)
        except SourceDocKeyError as exc:
            result.errors.append(str(exc))
            return result
        written = write_atomic(py_out, scaffold, dry_run=dry_run)
        if written:
            result.files_written.append(str(py_out))
        else:
            result.files_skipped.append(str(py_out))

        # Placeholder CSVs — one per curve; each carries its own doc_key.
        for entry, doc_key in pairs:
            caption = entry.get("caption") or entry.get("figure_id") or "unknown"
            curve_id = sanitize_identifier(caption)
            csv_out = (
                project_root
                / "data"
                / "standards"
                / "promoted"
                / domain
                / "curves"
                / f"{curve_id}.csv"
            )
            try:
                csv_body = _render_placeholder_csv(doc_key)
            except SourceDocKeyError as exc:
                result.errors.append(str(exc))
                return result
            written = write_atomic(csv_out, csv_body, dry_run=dry_run)
            if written:
                result.files_written.append(str(csv_out))
            else:
                result.files_skipped.append(str(csv_out))

    return result


register_promoter("curves", promote_curves)
