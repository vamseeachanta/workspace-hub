#!/usr/bin/env python3
# ABOUTME: Deterministic ASTM classifier — maps designation prefix to discipline (WRK-1188)
# ABOUTME: Processes 25,537 ASTM docs without LLM; flags ambiguous docs for LLM follow-up

"""
Deterministic classifier for ASTM standards.

ASTM designation prefixes map predictably to disciplines:
  A-F → materials (ferrous/nonferrous metals, cement, misc, testing, applications)
  G   → cathodic-protection (corrosion, deterioration, degradation)

Usage:
    uv run --no-project python scripts/data/document-index/phase_b_astm_classifier.py
    uv run --no-project python scripts/data/document-index/phase_b_astm_classifier.py --dry-run
    uv run --no-project python scripts/data/document-index/phase_b_astm_classifier.py --limit 100
"""

import argparse
import json
import logging
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [astm] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

HUB_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = Path("/mnt/ace/O&G-Standards/_inventory.db")
SUMMARIES_DIR = HUB_ROOT / "data/document-index/summaries"

# ASTM designation prefix → discipline
PREFIX_MAP = {
    "A": "materials",
    "B": "materials",
    "C": "materials",
    "D": "materials",
    "E": "materials",
    "F": "materials",
    "G": "cathodic-protection",
}

# Regex to find "Standard Specification for\n<title>" or similar patterns
TITLE_PATTERNS = [
    re.compile(
        r"Standard\s+(?:Specification|Test\s+Method|Practice|Guide|"
        r"Classification|Terminology)\s+(?:for|of)\s*\n?\s*(.+?)(?:\d*\s*\n\s*This\s+standard)",
        re.IGNORECASE | re.DOTALL,
    ),
]


def prefix_to_discipline(prefix: str) -> str:
    """Map ASTM designation prefix letter to discipline."""
    if not prefix:
        return "other"
    return PREFIX_MAP.get(prefix[0].upper(), "other")


def extract_title_from_text(text: str | None) -> str | None:
    """Extract real title from ASTM document text header (first 500 chars)."""
    if not text:
        return None
    snippet = text[:500]
    for pattern in TITLE_PATTERNS:
        m = pattern.search(snippet)
        if m:
            title = m.group(1).strip()
            # Clean up line breaks within title
            title = re.sub(r"\s*\n\s*", " ", title)
            # Remove trailing footnote numbers
            title = re.sub(r"\d+$", "", title).strip()
            if title:
                return title
    return None


def extract_designation_prefix(doc_number: str, title: str) -> str | None:
    """Extract the letter prefix from doc_number or title.

    Tries doc_number first, falls back to title.
    Returns single uppercase letter or None.
    """
    for candidate in [doc_number, title]:
        if not candidate:
            continue
        cleaned = candidate.strip()
        # Strip "ASTM " prefix
        if cleaned.upper().startswith("ASTM"):
            cleaned = cleaned[4:].strip()
        # First alpha char is the prefix
        for ch in cleaned:
            if ch.isalpha():
                return ch.upper()
            if ch.isdigit():
                break  # numeric before alpha → no valid prefix
    return None


def classify_astm_row(row: tuple) -> dict | None:
    """Classify a single ASTM DB row deterministically.

    Row format: (id, org, doc_number, title, target_path,
                  content_hash, file_size, full_text, word_count)

    Returns summary dict or None if content_hash is missing.
    """
    doc_id, org, doc_number, title, target_path, content_hash, \
        file_size, full_text, word_count = row

    if not content_hash:
        return None

    prefix = extract_designation_prefix(doc_number or "", title or "")
    discipline = prefix_to_discipline(prefix) if prefix else "other"
    method = "astm_deterministic" if prefix else "astm_deterministic_ambiguous"

    # Try to extract real title from text
    extracted_title = extract_title_from_text(full_text)
    summary_text = extracted_title or title or f"ASTM {doc_number}"

    # Build keywords from prefix + extracted title
    keywords = ["ASTM"]
    if doc_number:
        keywords.append(f"ASTM {doc_number}")
    if prefix:
        keywords.append(f"ASTM-{prefix}")

    return {
        "path": target_path or "",
        "sha256": content_hash,
        "source": "og_standards",
        "org": org or "ASTM",
        "doc_number": doc_number or "",
        "title": title or "",
        "discipline": discipline,
        "summary": summary_text,
        "keywords": keywords,
        "extraction_method": method,
    }


def write_astm_summary(
    result: dict, summaries_dir: Path = SUMMARIES_DIR,
) -> None:
    """Write summary JSON, merging with existing file if present."""
    summaries_dir.mkdir(parents=True, exist_ok=True)
    sha = result["sha256"]
    p = summaries_dir / f"{sha}.json"

    existing = {}
    if p.exists():
        try:
            existing = json.loads(p.read_text())
        except Exception:
            pass

    existing.update(result)
    existing.setdefault("llm_at", datetime.now().isoformat(timespec="seconds"))
    existing["llm_method"] = "astm_deterministic"
    p.write_text(json.dumps(existing, ensure_ascii=False, indent=2))


def needs_classification(sha: str, summaries_dir: Path = SUMMARIES_DIR) -> bool:
    """Check if this doc still needs classification."""
    p = summaries_dir / f"{sha}.json"
    if not p.exists():
        return True
    try:
        return not json.loads(p.read_text()).get("discipline")
    except Exception:
        return True


def classify_and_write_batch(
    rows: list[tuple],
    summaries_dir: Path = SUMMARIES_DIR,
    dry_run: bool = False,
) -> dict:
    """Classify a batch of rows. Returns stats dict."""
    done = 0
    skipped = 0
    errors = 0
    ambiguous = 0

    for row in rows:
        sha = row[5]  # content_hash
        if not sha or not needs_classification(sha, summaries_dir):
            skipped += 1
            continue

        result = classify_astm_row(row)
        if result is None:
            errors += 1
            continue

        if result["extraction_method"] == "astm_deterministic_ambiguous":
            ambiguous += 1

        if not dry_run:
            write_astm_summary(result, summaries_dir=summaries_dir)

        done += 1

        if (done + skipped) % 5000 == 0:
            logger.info(
                "progress: done=%d skipped=%d errors=%d ambiguous=%d",
                done, skipped, errors, ambiguous,
            )

    return {
        "done": done,
        "skipped": skipped,
        "errors": errors,
        "ambiguous": ambiguous,
    }


def load_astm_rows(limit: int = 0) -> list[tuple]:
    """Load all ASTM rows from the og_standards SQLite database."""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    rows = conn.execute("""
        SELECT d.id, d.organization, d.doc_number, d.title,
               d.target_path, d.content_hash, d.file_size,
               dt.full_text, dt.word_count
        FROM documents d
        LEFT JOIN document_text dt ON d.id = dt.document_id
        WHERE d.is_duplicate = 0
          AND d.organization = 'ASTM'
        ORDER BY d.id
    """).fetchall()
    conn.close()
    if limit:
        rows = rows[:limit]
    logger.info("Loaded %d ASTM rows", len(rows))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic ASTM classifier (WRK-1188)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--limit", type=int, default=0, help="Cap docs (0=unlimited)",
    )
    args = parser.parse_args()

    logger.info("dry_run=%s limit=%d", args.dry_run, args.limit)
    rows = load_astm_rows(limit=args.limit)
    stats = classify_and_write_batch(rows, dry_run=args.dry_run)
    logger.info(
        "COMPLETE: done=%d skipped=%d errors=%d ambiguous=%d",
        stats["done"], stats["skipped"], stats["errors"], stats["ambiguous"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
