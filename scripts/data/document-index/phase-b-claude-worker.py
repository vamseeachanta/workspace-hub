#!/usr/bin/env python3
# ABOUTME: Phase B Claude CLI batch summarisation worker (WRK-309)
# ABOUTME: Run overnight: bash scripts/data/document-index/launch-batch.sh [shards] [source]
# ABOUTME: Sources: og_standards | ace_standards | workspace_spec | all (default)

"""
Usage (from a SEPARATE terminal, not inside Claude Code):
    bash scripts/data/document-index/launch-batch.sh 10 all
    # or single shard:
    python3 phase-b-claude-worker.py --shard 0 --total 10 --source all

Requires: claude CLI accessible on PATH, authenticated (OAuth session).
CLAUDECODE env var is automatically unset in subprocess calls to avoid nesting error.
"""

import argparse
import json
import logging
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [shard-%(shard)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

HUB_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = Path("/mnt/ace/O&G-Standards/_inventory.db")
INDEX_PATH = HUB_ROOT / "data/document-index/index.jsonl"
_DEFAULT_SUMMARIES = "/mnt/remote/ace-linux-1/ace/data/document-index/summaries"
SUMMARIES_DIR = Path(os.environ.get("SUMMARIES_DIR", _DEFAULT_SUMMARIES))

MAX_TEXT_CHARS = 5000   # ~1200 tokens — cover page + abstract + scope
CLAUDE_TIMEOUT = 90     # seconds per call

DISCIPLINES = (
    "structural|cathodic-protection|pipeline|marine|installation"
    "|energy-economics|materials|regulatory|drilling|workspace-spec|other"
)

PROMPT = (
    "You are classifying an engineering standards document. "
    "Reply with JSON only — no markdown fences, no extra text:\n"
    '{"discipline":"' + DISCIPLINES + '",'
    '"summary":"one sentence (max 25 words) describing scope",'
    '"keywords":["kw1","kw2","kw3"]}\n'
    "Use the metadata and text provided to classify accurately."
)


# ── Text extraction ────────────────────────────────────────────────────────────

def get_og_text(row: tuple) -> tuple[str, str]:
    """Extract text for og_standards row. Returns (text, method)."""
    doc_id, org, doc_num, title, target_path, content_hash, _, full_text, wc = row
    if full_text and (wc or 0) > 30:
        return full_text[:MAX_TEXT_CHARS], "og_sqlite"
    if target_path and os.path.exists(target_path):
        t = _pdftotext(target_path)
        if t:
            return t, "pdftotext_p3"
    return f"Title: {title}\nOrg: {org}\nDoc: {doc_num}", "metadata_only"


def _pdftotext(path: str, max_pages: int = 3) -> Optional[str]:
    try:
        r = subprocess.run(
            ["pdftotext", "-f", "1", "-l", str(max_pages), "-q", path, "-"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout[:MAX_TEXT_CHARS]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def _direct_read(path: str) -> Optional[str]:
    try:
        return Path(path).read_text(errors="replace")[:MAX_TEXT_CHARS]
    except OSError:
        return None


# ── Claude CLI call ────────────────────────────────────────────────────────────

def claude_summarise(text: str, meta: dict) -> Optional[dict]:
    """Call claude -p, return parsed dict or None."""
    context = (
        f"Metadata: org={meta.get('org','')}, "
        f"doc={meta.get('doc_number','')}, "
        f"title={meta.get('title','')}\n\n"
        f"Document text:\n{text}"
    )

    env = os.environ.copy()
    env.pop("CLAUDECODE", None)   # prevent nested-session error

    try:
        r = subprocess.run(
            [
                "claude", "-p", PROMPT,
                "--output-format", "json",
                "--model", "haiku",
                "--no-session-persistence",
                "--dangerously-skip-permissions",
                "--tools", "",
                "--max-turns", "1",
            ],
            input=context,
            capture_output=True,
            text=True,
            timeout=CLAUDE_TIMEOUT,
            env=env,
        )
        if r.returncode != 0:
            logging.warning("claude non-zero: %s", r.stderr[:200])
            return None

        # --output-format json may return multiple JSON objects on separate lines
        first_line = r.stdout.strip().splitlines()[0] if r.stdout.strip() else "{}"
        outer = json.loads(first_line)
        raw = outer.get("result", "")
        if not raw:
            return None
        # Strip markdown fences if present
        if raw.startswith("```"):
            lines = raw.strip().split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
        # Claude may return JSON followed by extra text — try full parse, then first line
        cleaned = raw.strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            first_raw_line = cleaned.splitlines()[0] if cleaned else ""
            return json.loads(first_raw_line)

    except subprocess.TimeoutExpired:
        logging.warning("claude timeout after %ds", CLAUDE_TIMEOUT)
    except (json.JSONDecodeError, KeyError) as e:
        logging.warning("parse error: %s | raw: %.100s", e, r.stdout if r else "")
    except OSError as e:
        logging.error("claude not found: %s", e)
        sys.exit(1)
    return None


# ── Summary file I/O ───────────────────────────────────────────────────────────

def needs_llm(sha: str) -> bool:
    p = SUMMARIES_DIR / f"{sha}.json"
    if not p.exists():
        return True
    try:
        return not json.loads(p.read_text()).get("discipline")
    except Exception:
        return True


def write_summary(sha: str, data: dict) -> None:
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    p = SUMMARIES_DIR / f"{sha}.json"
    existing = {}
    if p.exists():
        try:
            existing = json.loads(p.read_text())
        except Exception:
            pass
    existing.update(data)
    existing.setdefault("llm_at", datetime.now().isoformat(timespec="seconds"))
    existing["llm_method"] = "claude-haiku-cli"
    p.write_text(json.dumps(existing, ensure_ascii=False, indent=2))


# ── Source loaders ─────────────────────────────────────────────────────────────

def load_og_standards(
    shard: int, total: int,
    org_filter: Optional[str] = None,
    include_all: bool = False,
) -> list:
    conn = sqlite3.connect(str(DB_PATH), timeout=30)

    where_clauses = [
        "d.is_duplicate = 0",
        "d.target_path IS NOT NULL",
        "d.extension IN ('.pdf', '.PDF', '.docx', '.DOCX')",
    ]
    params: list = []

    if org_filter:
        where_clauses.append("d.organization = ?")
        params.append(org_filter)
    elif not include_all:
        where_clauses.append("d.organization NOT IN ('ASTM', 'Unknown')")

    sql = (
        "SELECT d.id, d.organization, d.doc_number, d.title,"
        "       d.target_path, d.content_hash, d.file_size,"
        "       dt.full_text, dt.word_count "
        "FROM documents d "
        "LEFT JOIN document_text dt ON d.id = dt.document_id "
        f"WHERE {' AND '.join(where_clauses)} "
        "ORDER BY d.id"
    )
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [r for i, r in enumerate(rows) if i % total == shard]


def load_index_source(source: str, shard: int, total: int) -> list:
    """Load records from index.jsonl for a given source, sharded."""
    records = []
    idx = 0
    valid_exts = {"pdf", "docx", "md", "txt", "yaml", "yml"}  # index stores ext without leading dot
    with open(INDEX_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("source") != source:
                continue
            if rec.get("is_cad"):
                continue
            if rec.get("ext", "").lower() not in valid_exts:
                continue
            sha = rec.get("content_hash", "")
            if not sha:
                continue
            if idx % total == shard:
                records.append(rec)
            idx += 1
    return records


# ── Per-source processing ──────────────────────────────────────────────────────

def process_og_row(row: tuple, validate: bool = False) -> bool:
    doc_id, org, doc_num, title, target_path, sha, _, full_text, wc = row
    if not sha:
        return False
    if not validate and not needs_llm(sha):
        return False

    text, method = get_og_text(row)
    if not text:
        return False

    meta = {"org": org, "doc_number": doc_num or "", "title": title or ""}
    result = claude_summarise(text, meta)
    if not result:
        result = {"discipline": "other", "summary": f"{org} {doc_num}: {title}", "keywords": [org]}

    llm_disc = result.get("discipline", "other")

    if validate:
        # Validation mode: write LLM result to llm_discipline, preserve discipline
        write_summary(sha, {
            "llm_discipline": llm_disc,
            "llm_summary": result.get("summary", ""),
            "llm_keywords": result.get("keywords", []),
        })
    else:
        write_summary(sha, {
            "path": target_path or "",
            "sha256": sha,
            "source": "og_standards",
            "org": org,
            "doc_number": doc_num or "",
            "title": title or "",
            "discipline": llm_disc,
            "summary": result.get("summary", ""),
            "keywords": result.get("keywords", []),
            "extraction_method": method,
        })
    return True


PATH_REMAPS = [
    ("/mnt/remote/ace-linux-2/dde/", "/mnt/dde/"),
    ("/mnt/remote/dev-secondary/dde/", "/mnt/dde/"),
]


def _remap_path(path: str) -> str:
    """Resolve cross-host mount paths to local equivalents."""
    for remote, local in PATH_REMAPS:
        if path.startswith(remote):
            return local + path[len(remote):]
    return path


def process_index_record(rec: dict) -> bool:
    sha = rec.get("content_hash", "")
    path = _remap_path(rec.get("path", ""))
    source = rec.get("source", "")
    if not sha or not needs_llm(sha):
        return False

    ext = Path(path).suffix.lower() if path else ""
    text = None
    if ext == ".pdf":
        text = _pdftotext(path)
    elif ext in (".md", ".txt", ".yaml", ".yml"):
        text = _direct_read(path)
    elif ext == ".docx":
        # basic fallback — try pdftotext (will fail gracefully), then direct
        text = _direct_read(path)

    if not text or len(text.strip()) < 50:
        write_summary(sha, {
            "path": path, "sha256": sha, "source": source,
            "discipline": "other", "summary": "No extractable text.",
            "keywords": [], "extraction_method": "no_text",
        })
        return False

    title = rec.get("title") or Path(path).stem
    org = rec.get("organization", "")
    meta = {"org": org, "doc_number": rec.get("doc_number", ""), "title": title}
    result = claude_summarise(text, meta)
    if not result:
        result = {"discipline": "other", "summary": title, "keywords": []}

    write_summary(sha, {
        "path": path, "sha256": sha, "source": source,
        "org": org, "title": title,
        "discipline": result.get("discipline", "other"),
        "summary": result.get("summary", ""),
        "keywords": result.get("keywords", []),
        "extraction_method": "pdftotext_p3" if ext == ".pdf" else "direct",
    })
    return True


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Phase B Claude batch worker (WRK-309)")
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--total", type=int, required=True)
    parser.add_argument("--source",
                        choices=["og_standards", "ace_standards", "ace_project",
                                 "dde_project", "va_hdd_2", "workspace_spec", "all"],
                        default="all")
    parser.add_argument("--org", default=None,
                        help="Process only this organization (e.g. API, DNV, ISO)")
    parser.add_argument("--include-all", action="store_true",
                        help="Include ASTM/Unknown orgs (normally excluded)")
    parser.add_argument("--validate", action="store_true",
                        help="Validation mode: bypass needs_llm, write to llm_discipline")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Cap docs per source (0=unlimited)")
    args = parser.parse_args()

    # Inject shard into log format
    old_factory = logging.getLogRecordFactory()
    shard_val = args.shard
    def record_factory(*a, **kw):
        rec = old_factory(*a, **kw)
        rec.shard = shard_val
        return rec
    logging.setLogRecordFactory(record_factory)
    logger = logging.getLogger()

    logger.info("shard %d/%d  source=%s  org=%s  include_all=%s  validate=%s  dry_run=%s",
                args.shard, args.total, args.source, args.org,
                args.include_all, args.validate, args.dry_run)

    done = skipped = errors = 0

    def run_og():
        nonlocal done, skipped, errors
        rows = load_og_standards(
            args.shard, args.total,
            org_filter=args.org, include_all=args.include_all,
        )
        if args.limit:
            rows = rows[:args.limit]
        logger.info("og_standards: %d rows in shard", len(rows))
        for i, row in enumerate(rows):
            sha = row[5]
            if not sha:
                skipped += 1
                continue
            if not args.validate and not needs_llm(sha):
                skipped += 1
                continue
            if args.dry_run:
                logger.info("[DRY] og %s %s", row[1], row[2])
                done += 1
                continue
            ok = process_og_row(row, validate=args.validate)
            if ok:
                done += 1
            else:
                errors += 1
            if (done + skipped + errors) % 25 == 0:
                logger.info("og progress: done=%d skipped=%d errors=%d", done, skipped, errors)

    def run_index(source_name: str):
        nonlocal done, skipped, errors
        recs = load_index_source(source_name, args.shard, args.total)
        if args.limit:
            recs = recs[:args.limit]
        logger.info("%s: %d records in shard", source_name, len(recs))
        for i, rec in enumerate(recs):
            sha = rec.get("content_hash", "")
            if not sha or not needs_llm(sha):
                skipped += 1
                continue
            if args.dry_run:
                logger.info("[DRY] %s %s", source_name, rec.get("path", "")[-60:])
                done += 1
                continue
            ok = process_index_record(rec)
            if ok:
                done += 1
            else:
                errors += 1
            if (done + skipped + errors) % 25 == 0:
                logger.info("%s progress: done=%d skipped=%d errors=%d",
                            source_name, done, skipped, errors)

    # Priority order: workspace_spec (small, fast) → og_standards → ace_standards → ace_project → dde_project
    if args.source in ("workspace_spec", "all"):
        run_index("workspace_spec")
    if args.source in ("og_standards", "all"):
        run_og()
    if args.source in ("ace_standards", "all"):
        run_index("ace_standards")
    if args.source in ("ace_project", "all"):
        run_index("ace_project")
    if args.source in ("dde_project", "all"):
        run_index("dde_project")
    if args.source in ("va_hdd_2", "all"):
        run_index("va_hdd_2")

    logger.info("Shard %d COMPLETE: done=%d skipped=%d errors=%d",
                args.shard, done, skipped, errors)
    return 0


if __name__ == "__main__":
    sys.exit(main())
