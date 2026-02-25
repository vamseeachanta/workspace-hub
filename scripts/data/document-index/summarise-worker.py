#!/usr/bin/env python3
# ABOUTME: Targeted summarisation worker — processes a shard of og_standards docs via Gemini CLI
# ABOUTME: Uses existing DB text or pdftotext -l 3; writes JSON summaries for agent use

import argparse
import hashlib
import json
import logging
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [shard-%(shard)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

HUB_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = Path("/mnt/ace/O&G-Standards/_inventory.db")
SUMMARIES_DIR = HUB_ROOT / "data/document-index/summaries"

PROMPT = (
    'Reply with JSON only, no markdown:\n'
    '{"discipline":"structural|cathodic-protection|pipeline|marine|installation'
    '|energy-economics|materials|regulatory|drilling|other",'
    '"summary":"one sentence scope",'
    '"repos":["digitalmodel","worldenergydata","assethold","doris","OGManufacturing","acma-projects"],'
    '"keywords":["word1","word2","word3"]}'
    "\nPick only repos genuinely relevant. Use the metadata and text to classify."
)

MAX_TEXT_CHARS = 6000  # ~1500 tokens — cover page + abstract + scope
GEMINI_TIMEOUT = 90


def get_shard_docs(shard: int, total: int) -> list:
    """Query og_standards DB for this worker's shard of non-ASTM docs."""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    rows = conn.execute("""
        SELECT d.id, d.organization, d.doc_number, d.title,
               d.target_path, d.content_hash, d.file_size,
               dt.full_text, dt.word_count
        FROM documents d
        LEFT JOIN document_text dt ON d.id = dt.document_id
        WHERE d.is_duplicate = 0
          AND d.organization NOT IN ('ASTM', 'Unknown')
          AND d.target_path IS NOT NULL
          AND d.extension IN ('.pdf', '.PDF', '.docx', '.DOCX')
        ORDER BY d.id
    """).fetchall()
    conn.close()

    # Slice this shard
    mine = [r for i, r in enumerate(rows) if i % total == shard]
    return mine


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
    except OSError:
        return hashlib.sha256(path.encode()).hexdigest()
    return h.hexdigest()


def get_text(row: tuple) -> tuple[str, str]:
    """Return (text, method). Priority: DB full_text → pdftotext -l 3."""
    doc_id, org, doc_num, title, target_path, content_hash, size, full_text, wc = row

    if full_text and (wc or 0) > 30:
        return full_text[:MAX_TEXT_CHARS], "og_sqlite"

    if not target_path or not os.path.exists(target_path):
        return "", "missing"

    ext = Path(target_path).suffix.lower()
    if ext in (".pdf",):
        try:
            result = subprocess.run(
                ["pdftotext", "-f", "1", "-l", "3", "-q", target_path, "-"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout[:MAX_TEXT_CHARS], "pdftotext_p3"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Fallback: just use metadata
    return f"Title: {title}\nOrganisation: {org}\nDocument: {doc_num}", "metadata_only"


def gemini_summarise(text: str, meta: dict) -> dict | None:
    """Call gemini CLI and parse JSON response."""
    context = (
        f"Document metadata: org={meta['org']}, "
        f"doc_number={meta['doc_number']}, title={meta['title']}\n\n"
        f"Document text (first pages):\n{text}"
    )
    try:
        result = subprocess.run(
            ["gemini", "-p", PROMPT],
            input=context,
            capture_output=True,
            text=True,
            timeout=GEMINI_TIMEOUT,
        )
        output = result.stdout.strip()
        if not output:
            return None
        # Strip markdown fences if present
        if output.startswith("```"):
            lines = output.split("\n")
            output = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        return json.loads(output)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return None


def write_summary(sha: str, data: dict) -> Path:
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    out = SUMMARIES_DIR / f"{sha}.json"
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Targeted summarisation worker (WRK-309)")
    parser.add_argument("--shard", type=int, required=True, help="0-based shard index")
    parser.add_argument("--total", type=int, required=True, help="Total number of shards")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    logger = logging.getLogger()
    # Inject shard into log format
    old_factory = logging.getLogRecordFactory()
    shard_val = args.shard
    def record_factory(*a, **kw):
        record = old_factory(*a, **kw)
        record.shard = shard_val
        return record
    logging.setLogRecordFactory(record_factory)

    docs = get_shard_docs(args.shard, args.total)
    logger.info("Shard %d/%d — %d docs to process", args.shard, args.total, len(docs))

    done = skipped = errors = 0

    for i, row in enumerate(docs):
        doc_id, org, doc_num, title, target_path, content_hash, size, full_text, wc = row
        sha = content_hash or sha256_of(target_path or str(doc_id))

        # Resume-safe: skip only if LLM summary already present (has 'discipline')
        out_path = SUMMARIES_DIR / f"{sha}.json"
        if out_path.exists():
            try:
                existing = json.loads(out_path.read_text())
                if existing.get("discipline"):
                    skipped += 1
                    continue
            except (json.JSONDecodeError, OSError):
                pass

        text, method = get_text(row)
        if not text:
            errors += 1
            continue

        meta = {"org": org, "doc_number": doc_num or "", "title": title or ""}

        if args.dry_run:
            logger.info("[DRY] %s %s — %s (%d chars)", org, doc_num, method, len(text))
            done += 1
            continue

        summary_data = gemini_summarise(text, meta)
        if summary_data is None:
            # Fallback: write minimal summary from metadata
            summary_data = {
                "title": title or "",
                "org": org,
                "doc_number": doc_num or "",
                "summary": f"{org} standard {doc_num}: {title}",
                "discipline": "other",
                "keywords": [org, doc_num or ""],
                "target_repos": [],
                "key_clauses": "",
            }

        summary_data.update({
            "path": target_path or "",
            "sha256": sha,
            "extraction_method": method,
            "extracted_at": datetime.now().isoformat(timespec="seconds"),
        })

        write_summary(sha, summary_data)
        done += 1

        if (done + skipped) % 20 == 0:
            logger.info("Progress: %d done, %d skipped, %d errors", done, skipped, errors)

    logger.info("Complete: %d done, %d skipped, %d errors", done, skipped, errors)
    return 0


if __name__ == "__main__":
    sys.exit(main())
