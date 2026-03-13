"""Curves promoter — scaffold Python modules and placeholder CSVs for figure references."""

from collections import defaultdict
from pathlib import Path
from typing import List

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

# Placeholder CSV content — headers only, to be filled with digitized data
_CSV_PLACEHOLDER = "x,y\n"


def _render_scaffold(domain: str, entries: list[dict]) -> str:
    """Render a Python scaffold module for a single domain.

    Each entry becomes a comment block referencing the curve caption,
    source citation, and placeholder CSV path.
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
    return f'# content-hash: {h}\n{body}'


def promote_curves(
    records: list[dict],
    project_root: Path,
    dry_run: bool = False,
) -> PromoteResult:
    """Scaffold Python modules and placeholder CSVs for curve references.

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

    # Group records by domain
    by_domain: dict[str, List[dict]] = defaultdict(list)
    for rec in records:
        domain = rec.get("domain", "unknown")
        by_domain[domain].append(rec)

    for domain, entries in by_domain.items():
        # Python scaffold
        domain_path = domain.replace("-", "_")
        py_rel = Path(
            f"digitalmodel/src/digitalmodel/{domain_path}/curves.py"
        )
        py_out = project_root / py_rel
        scaffold = _render_scaffold(domain, entries)
        written = write_atomic(py_out, scaffold, dry_run=dry_run)
        if written:
            result.files_written.append(str(py_out))
        else:
            result.files_skipped.append(str(py_out))

        # Placeholder CSVs — one per curve
        for entry in entries:
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
            written = write_atomic(csv_out, _CSV_PLACEHOLDER, dry_run=dry_run)
            if written:
                result.files_written.append(str(csv_out))
            else:
                result.files_skipped.append(str(csv_out))

    return result


register_promoter("curves", promote_curves)
