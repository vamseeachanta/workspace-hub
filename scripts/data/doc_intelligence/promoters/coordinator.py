"""Promotion coordinator — reads JSONL indexes and dispatches to type-specific promoters."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass
class PromoteResult:
    """Result from a single promoter run."""

    files_written: List[str] = field(default_factory=list)
    files_skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class PromoteStats:
    """Aggregated statistics across all promoters."""

    total_written: int = 0
    total_skipped: int = 0
    total_errors: int = 0
    results_by_type: Dict[str, PromoteResult] = field(default_factory=dict)


def _read_jsonl(path: Path) -> List[dict]:
    """Read a JSONL file into a list of dicts. Returns empty list if missing."""
    if not path.exists():
        return []
    records = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# Type alias for promoter functions
PromoterFunc = Callable[[List[dict], Path, bool], PromoteResult]

# Registry populated by imports
_PROMOTER_REGISTRY: Dict[str, PromoterFunc] = {}


def register_promoter(content_type: str, func: PromoterFunc) -> None:
    """Register a promoter function for a content type."""
    _PROMOTER_REGISTRY[content_type] = func


# Map content types to their JSONL file paths (relative to index_dir)
CONTENT_TYPE_PATHS = {
    "constants": "constants.jsonl",
    "equations": "equations.jsonl",
    "tables": "tables/index.jsonl",
    "worked_examples": "worked_examples.jsonl",
    "curves": "curves/index.jsonl",
    "procedures": "procedures.jsonl",
    "requirements": "requirements.jsonl",
    "definitions": "definitions.jsonl",
}


def _ensure_promoters_registered() -> None:
    """Import all promoter modules to trigger registration."""
    if _PROMOTER_REGISTRY:
        return
    import importlib

    for mod_name in [
        "constants", "curves", "definitions", "equations",
        "procedures", "requirements", "tables", "worked_examples",
    ]:
        try:
            importlib.import_module(
                f"scripts.data.doc_intelligence.promoters.{mod_name}"
            )
        except ImportError:
            pass  # Module not yet implemented


def promote_all(
    index_dir: Path,
    project_root: Path,
    dry_run: bool = False,
    verbose: bool = False,
    types: Optional[List[str]] = None,
) -> PromoteStats:
    """Run all registered promoters against their JSONL indexes.

    Args:
        index_dir: Directory containing JSONL indexes (data/doc-intelligence/).
        project_root: Workspace root for output path resolution.
        dry_run: If True, report what would be written without writing.
        verbose: Print per-type details.
        types: If set, only run these content types.

    Returns:
        PromoteStats with aggregated results.
    """
    _ensure_promoters_registered()
    stats = PromoteStats()
    target_types = types or list(CONTENT_TYPE_PATHS.keys())

    for ct in target_types:
        if ct not in CONTENT_TYPE_PATHS:
            result = PromoteResult(errors=[f"Unknown content type: {ct}"])
            stats.results_by_type[ct] = result
            stats.total_errors += 1
            continue

        jsonl_path = index_dir / CONTENT_TYPE_PATHS[ct]
        records = _read_jsonl(jsonl_path)

        if verbose:
            print(f"  {ct}: {len(records)} records from {jsonl_path}")

        if ct not in _PROMOTER_REGISTRY:
            result = PromoteResult(errors=[f"No promoter registered for: {ct}"])
            stats.results_by_type[ct] = result
            stats.total_errors += 1
            continue

        promoter = _PROMOTER_REGISTRY[ct]
        result = promoter(records, project_root, dry_run)
        stats.results_by_type[ct] = result
        stats.total_written += len(result.files_written)
        stats.total_skipped += len(result.files_skipped)
        stats.total_errors += len(result.errors)

        if verbose:
            if result.files_written:
                for f in result.files_written:
                    print(f"    wrote: {f}")
            if result.files_skipped:
                print(f"    skipped: {len(result.files_skipped)} unchanged")
            if result.errors:
                for e in result.errors:
                    print(f"    ERROR: {e}")

    return stats
