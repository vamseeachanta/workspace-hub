"""Query federated content indexes produced by the index builder."""

import json
from collections import Counter
from pathlib import Path
from typing import List, Optional


# Content types stored as individual JSONL files
_SECTION_TYPES = [
    "constants", "equations", "requirements",
    "procedures", "definitions", "worked_examples",
]

# Content types stored under subdirectories with index.jsonl
_SUBDIR_TYPES = {
    "tables": "tables/index.jsonl",
    "curves": "curves/index.jsonl",
}

ALL_CONTENT_TYPES = _SECTION_TYPES + list(_SUBDIR_TYPES.keys())


def _read_jsonl(path: Path) -> List[dict]:
    """Read a JSONL file, skipping malformed lines."""
    if not path.exists():
        return []
    records = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _matches_keyword(record: dict, keyword: str) -> bool:
    """Case-insensitive substring match across text fields."""
    kw = keyword.lower()
    for field_name in ("text", "title", "caption", "figure_id"):
        val = record.get(field_name)
        if val and kw in str(val).lower():
            return True
    # Check column names for tables
    columns = record.get("columns")
    if columns and any(kw in str(c).lower() for c in columns):
        return True
    return False


def query_indexes(
    index_dir: Path,
    content_type: Optional[str] = None,
    domain: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 20,
) -> List[dict]:
    """Query federated content indexes.

    Args:
        index_dir: Directory containing JSONL index files.
        content_type: Filter to a single content type (e.g. "constants", "tables").
        domain: Filter by domain (exact match).
        keyword: Case-insensitive substring match across text fields.
        limit: Maximum number of results to return.

    Returns:
        List of matching records, each with an added '_content_type' field.
    """
    index_dir = Path(index_dir)
    if not index_dir.exists():
        return []

    # Determine which types to query
    if content_type:
        types_to_query = [content_type]
    else:
        types_to_query = list(ALL_CONTENT_TYPES)

    results = []
    for ct in types_to_query:
        if ct in _SUBDIR_TYPES:
            path = index_dir / _SUBDIR_TYPES[ct]
        elif ct in _SECTION_TYPES:
            path = index_dir / f"{ct}.jsonl"
        else:
            continue

        for record in _read_jsonl(path):
            record["_content_type"] = ct

            if domain and record.get("domain") != domain:
                continue
            if keyword and not _matches_keyword(record, keyword):
                continue

            results.append(record)
            if len(results) >= limit:
                return results

    return results


def format_stage2_brief(results: List[dict], domain: str) -> str:
    """Format query results as a concise brief for Stage 2 injection.

    Args:
        results: Query results from query_indexes().
        domain: Domain label for the header.

    Returns:
        Compact multi-line string summarizing available content.
    """
    if not results:
        return f"No doc-intelligence content found for domain '{domain}'."

    counts = Counter(r["_content_type"] for r in results)
    lines = [f"doc-intelligence ({domain}): {len(results)} items"]
    for ct, n in sorted(counts.items()):
        lines.append(f"  {ct}: {n}")
    return "\n".join(lines)


def format_full(results: List[dict]) -> str:
    """Format query results with full detail including source references.

    Args:
        results: Query results from query_indexes().

    Returns:
        Detailed multi-line string with one block per result.
    """
    if not results:
        return "No results."

    blocks = []
    for i, r in enumerate(results, 1):
        ct = r.get("_content_type", "unknown")
        source = r.get("source", {})
        src_parts = []
        if source.get("document"):
            src_parts.append(source["document"])
        if source.get("page"):
            src_parts.append(f"p.{source['page']}")
        if source.get("section"):
            src_parts.append(f"s.{source['section']}")
        src_str = ", ".join(src_parts) if src_parts else "unknown"

        # Pick the main display text
        text = r.get("text") or r.get("title") or r.get("caption") or ""
        block = f"[{i}] ({ct}) {text}\n    source: {src_str}"
        if r.get("domain"):
            block += f" | domain: {r['domain']}"
        blocks.append(block)

    return "\n\n".join(blocks)
