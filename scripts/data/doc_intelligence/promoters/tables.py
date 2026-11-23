"""Tables promoter — copies extracted CSV files to promoted directory.

Each promoted CSV carries provenance headers (``# content-hash:`` and
``# source_doc_key:``) prepended as ``#``-prefixed comment lines per the
standards-codes-provenance-reuse contract §8.3. Comment-aware CSV parsers
(pandas ``comment='#'``, polars ``comment_char='#'``) skip them; strict
parsers will treat them as ignored header rows.
"""

import os
from pathlib import Path

from scripts.data.doc_intelligence.promoters.coordinator import (
    PromoteResult,
    register_promoter,
)
from scripts.data.doc_intelligence.promoters.text_utils import (
    SourceDocKeyError,
    content_hash,
    extract_source_doc_key,
    format_source_doc_key_header,
    validate_source_doc_key,
)


def _render_with_headers(src_bytes: bytes, doc_key: str) -> bytes:
    """Prepend canonical provenance headers to the source CSV bytes.

    The content-hash is computed over the original source bytes (the data
    payload) so that re-running the promoter on an unchanged source
    produces an identical promoted artifact (idempotency preserved).
    """
    src_text = src_bytes.decode("utf-8")
    body_hash = content_hash(src_text)
    # Self-loop guard against the body hash.
    validate_source_doc_key(doc_key, output_content_hash=body_hash)

    sdk_header = format_source_doc_key_header([doc_key])
    header_lines = [f"# content-hash: {body_hash}"]
    if sdk_header:
        header_lines.append(sdk_header)
    header_block = "\n".join(header_lines) + "\n"
    return header_block.encode("utf-8") + src_bytes


def promote_tables(
    records: list[dict],
    project_root: Path,
    dry_run: bool = False,
) -> PromoteResult:
    """Promote table CSV files to the standards/promoted directory.

    Validates ``source.doc_key`` on every record before writing anything.
    A single invalid record fails the whole batch closed.

    For each record, resolves the source CSV from
    ``{project_root}/data/doc-intelligence/{csv_path}`` and writes a copy
    with prepended provenance headers to
    ``{project_root}/data/standards/promoted/{domain}/{filename}``.

    Idempotent: skips files whose content already matches what we would
    write (header block + source body).
    """
    result = PromoteResult()
    if not records:
        return result

    doc_intel_dir = project_root / "data" / "doc-intelligence"

    # Validate every doc_key up front.
    validated: list[tuple[dict, str]] = []
    for rec in records:
        try:
            key = extract_source_doc_key(rec)
        except SourceDocKeyError as exc:
            result.errors.append(str(exc))
            return result
        validated.append((rec, key))

    for rec, doc_key in validated:
        csv_path = rec.get("csv_path", "")
        domain = rec.get("domain", "unknown")
        filename = Path(csv_path).name

        src = doc_intel_dir / csv_path
        dest = (
            project_root / "data" / "standards" / "promoted" / domain / filename
        )

        if not src.exists():
            result.errors.append(f"Source CSV not found: {src}")
            continue

        try:
            src_bytes = src.read_bytes()
        except OSError as exc:
            result.errors.append(f"Failed to read {src}: {exc}")
            continue

        try:
            new_bytes = _render_with_headers(src_bytes, doc_key)
        except SourceDocKeyError as exc:
            result.errors.append(str(exc))
            return result
        except UnicodeDecodeError as exc:
            result.errors.append(f"Non-UTF-8 source CSV {src}: {exc}")
            continue

        # Idempotency: skip if destination has identical bytes.
        if dest.exists():
            try:
                if dest.read_bytes() == new_bytes:
                    result.files_skipped.append(str(dest))
                    continue
            except OSError:
                pass  # Re-write on read error

        if dry_run:
            result.files_written.append(str(dest))
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        # Atomic write: temp + rename.
        tmp_dest = dest.with_suffix(dest.suffix + ".tmp")
        try:
            tmp_dest.write_bytes(new_bytes)
            os.replace(tmp_dest, dest)
            result.files_written.append(str(dest))
        except OSError as exc:
            if tmp_dest.exists():
                tmp_dest.unlink()
            result.errors.append(f"Failed to write {dest}: {exc}")

    return result


register_promoter("tables", promote_tables)
