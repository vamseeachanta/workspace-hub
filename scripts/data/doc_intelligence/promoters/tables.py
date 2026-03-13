"""Tables promoter — copies extracted CSV files to promoted directory."""

import os
import shutil
from pathlib import Path

from scripts.data.doc_intelligence.promoters.coordinator import (
    PromoteResult,
    register_promoter,
)


def promote_tables(
    records: list[dict],
    project_root: Path,
    dry_run: bool = False,
) -> PromoteResult:
    """Promote table CSV files to the standards/promoted directory.

    For each record, resolves the source CSV from
    ``{project_root}/data/doc-intelligence/{csv_path}`` and copies it to
    ``{project_root}/data/standards/promoted/{domain}/{filename}``.

    Idempotent: skips files whose content already matches the source.
    Missing source CSVs are recorded as errors (no exception raised).
    """
    result = PromoteResult()
    if not records:
        return result

    doc_intel_dir = project_root / "data" / "doc-intelligence"

    for rec in records:
        csv_path = rec.get("csv_path", "")
        domain = rec.get("domain", "unknown")
        filename = Path(csv_path).name

        src = doc_intel_dir / csv_path
        dest = project_root / "data" / "standards" / "promoted" / domain / filename

        if not src.exists():
            result.errors.append(f"Source CSV not found: {src}")
            continue

        # Idempotency: skip if destination has identical content
        if dest.exists():
            try:
                src_bytes = src.read_bytes()
                dest_bytes = dest.read_bytes()
                if src_bytes == dest_bytes:
                    result.files_skipped.append(str(dest))
                    continue
            except OSError:
                pass  # Re-copy on read error

        if dry_run:
            result.files_written.append(str(dest))
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        # Atomic copy: write to temp then rename
        tmp_dest = dest.with_suffix(dest.suffix + ".tmp")
        try:
            shutil.copy2(str(src), str(tmp_dest))
            os.replace(tmp_dest, dest)
            result.files_written.append(str(dest))
        except OSError as exc:
            # Clean up temp file on failure
            if tmp_dest.exists():
                tmp_dest.unlink()
            result.errors.append(f"Failed to copy {src} -> {dest}: {exc}")

    return result


register_promoter("tables", promote_tables)
