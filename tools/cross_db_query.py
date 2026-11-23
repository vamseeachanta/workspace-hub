#!/usr/bin/env python3
"""
cross_db_query.py -- Unified query interface for ace-knowledge + O&G-Standards databases.

Connects two SQLite databases via ATTACH DATABASE:
  - Knowledge DB (index.db):   1.19M assets with classification metadata
  - Inventory DB (_inventory.db): 28K O&G standards with extracted text + embeddings

The inventory is ATTACHed as 'inv', so SQL queries use unqualified names for
knowledge tables (assets, standards, ...) and inv.* for inventory tables
(inv.documents, inv.document_text, inv.text_chunks).

Subcommands:
  search <terms>       Full-text search across one or both databases
  joined <terms>       Search overlapping records with enriched cross-DB metadata
  overlap              Analyze record overlap between databases
  stats                Show row counts and breakdowns for both databases
  health               Database health check: row counts, freshness, orphans
  sql <query>          Run arbitrary read-only SQL across both databases

Environment variables:
  KNOWLEDGE_DB         Path to index.db     (default: /mnt/ace/.ace-knowledge/index.db)
  INVENTORY_DB         Path to _inventory.db (default: /mnt/ace/O&G-Standards/_inventory.db)

Examples:
  python3 cross_db_query.py search "API 650"
  python3 cross_db_query.py search "riser analysis" --db inventory
  python3 cross_db_query.py joined "pipeline design"
  python3 cross_db_query.py overlap --by-hash
  python3 cross_db_query.py stats
  python3 cross_db_query.py health
  python3 cross_db_query.py sql "SELECT COUNT(*) FROM assets WHERE engineering_domain='riser'"
"""

import argparse
import os
import sqlite3
import sys
import textwrap
from pathlib import Path

# --- Configuration -----------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

# Database paths — override via environment variables if needed
KNOWLEDGE_DB = os.environ.get(
    "KNOWLEDGE_DB", "/mnt/ace/.ace-knowledge/index.db"
)
INVENTORY_DB = os.environ.get(
    "INVENTORY_DB", "/mnt/ace/O&G-Standards/_inventory.db"
)

# --- Helpers -----------------------------------------------------------------


def _connect(readonly: bool = True) -> sqlite3.Connection:
    """Return a connection with both databases attached.

    The knowledge DB is the main connection; inventory is ATTACHed as 'inv'.
    """
    mode = "ro" if readonly else "rw"
    uri = f"file://{KNOWLEDGE_DB}?mode={mode}"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute(f"ATTACH DATABASE 'file://{INVENTORY_DB}?mode={mode}' AS inv")
    return conn


def _print_rows(rows, columns, max_col_width=60, limit=None):
    """Pretty-print rows as a table."""
    if not rows:
        print("  (no results)")
        return

    display = rows[:limit] if limit else rows

    # Compute column widths
    widths = [len(c) for c in columns]
    str_rows = []
    for row in display:
        sr = []
        for i, val in enumerate(row):
            s = str(val) if val is not None else ""
            if len(s) > max_col_width:
                s = s[: max_col_width - 3] + "..."
            sr.append(s)
            widths[i] = max(widths[i], len(s))
        str_rows.append(sr)

    # Header
    header = "  ".join(c.ljust(widths[i]) for i, c in enumerate(columns))
    print(header)
    print("  ".join("-" * widths[i] for i in range(len(columns))))

    for sr in str_rows:
        print("  ".join(sr[i].ljust(widths[i]) for i in range(len(columns))))

    if limit and len(rows) > limit:
        print(f"\n  ... {len(rows) - limit} more rows (showing {limit}/{len(rows)})")


# --- Commands ----------------------------------------------------------------


def cmd_search(args):
    """Full-text + LIKE search across both databases."""
    conn = _connect()
    query = args.query
    limit = args.limit
    target = args.db  # 'both', 'knowledge', 'inventory'

    results_k = []
    results_i = []

    if target in ("both", "knowledge"):
        # FTS search on knowledge DB
        try:
            cur = conn.execute(
                """
                SELECT a.id, a.file_name, a.title, a.asset_type,
                       a.engineering_domain, a.file_size,
                       s.organization, s.doc_number
                FROM assets_fts fts
                JOIN assets a ON a.rowid = fts.rowid
                LEFT JOIN standards s ON s.asset_id = a.id
                WHERE assets_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (query, limit),
            )
            results_k = cur.fetchall()
        except sqlite3.OperationalError:
            # Fallback to LIKE
            like = f"%{query}%"
            cur = conn.execute(
                """
                SELECT a.id, a.file_name, a.title, a.asset_type,
                       a.engineering_domain, a.file_size,
                       s.organization, s.doc_number
                FROM assets a
                LEFT JOIN standards s ON s.asset_id = a.id
                WHERE a.title LIKE ? OR a.file_name LIKE ?
                   OR a.description LIKE ?
                LIMIT ?
                """,
                (like, like, like, limit),
            )
            results_k = cur.fetchall()

    if target in ("both", "inventory"):
        # FTS search on inventory DB
        try:
            cur = conn.execute(
                """
                SELECT d.id, d.filename, d.title, d.organization,
                       d.doc_type, d.doc_number, d.file_size,
                       dt.word_count
                FROM inv.documents_fts fts
                JOIN inv.documents d ON d.id = fts.rowid
                LEFT JOIN inv.document_text dt ON dt.document_id = d.id
                WHERE inv.documents_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (query, limit),
            )
            results_i = cur.fetchall()
        except sqlite3.OperationalError:
            like = f"%{query}%"
            cur = conn.execute(
                """
                SELECT d.id, d.filename, d.title, d.organization,
                       d.doc_type, d.doc_number, d.file_size,
                       dt.word_count
                FROM inv.documents d
                LEFT JOIN inv.document_text dt ON dt.document_id = d.id
                WHERE d.title LIKE ? OR d.filename LIKE ?
                LIMIT ?
                """,
                (like, like, limit),
            )
            results_i = cur.fetchall()

    # Display
    if target in ("both", "knowledge"):
        print(f"\n=== Knowledge DB (index.db): {len(results_k)} results ===")
        cols_k = [
            "id", "file_name", "title", "asset_type",
            "eng_domain", "size", "org", "doc_number",
        ]
        _print_rows(
            [tuple(r) for r in results_k], cols_k, limit=args.limit
        )

    if target in ("both", "inventory"):
        print(f"\n=== Inventory DB (_inventory.db): {len(results_i)} results ===")
        cols_i = [
            "id", "filename", "title", "org",
            "doc_type", "doc_number", "size", "word_count",
        ]
        _print_rows(
            [tuple(r) for r in results_i], cols_i, limit=args.limit
        )

    conn.close()


def cmd_overlap(args):
    """Analyze record overlap between the two databases."""
    conn = _connect()

    if args.by_hash:
        print("\n=== Overlap by content_hash ===")
        cur = conn.execute(
            """
            SELECT COUNT(*) FROM assets a
            JOIN inv.documents d ON a.content_hash = d.content_hash
            WHERE a.content_hash IS NOT NULL AND a.content_hash != ''
              AND d.content_hash IS NOT NULL AND d.content_hash != ''
            """
        )
        print(f"  Records sharing a content_hash: {cur.fetchone()[0]:,}")
    else:
        print("\n=== Overlap by file_path ===")
        cur = conn.execute(
            """
            SELECT COUNT(*) FROM assets a
            JOIN inv.documents d ON a.file_path = d.file_path
            """
        )
        count = cur.fetchone()[0]
        print(f"  Records sharing a file_path: {count:,}")

        cur = conn.execute("SELECT COUNT(*) FROM assets")
        total_k = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(*) FROM inv.documents")
        total_i = cur.fetchone()[0]

        print(f"  Knowledge-only records:  {total_k - count:,}")
        print(f"  Inventory-only records:  {total_i - count:,}")
        print(f"  Total knowledge: {total_k:,}  |  Total inventory: {total_i:,}")

    # Show enrichment potential: inventory records that have text but knowledge lacks it
    print("\n=== Enrichment potential ===")
    cur = conn.execute(
        """
        SELECT COUNT(*)
        FROM assets a
        JOIN inv.documents d ON a.file_path = d.file_path
        JOIN inv.document_text dt ON dt.document_id = d.id
        WHERE dt.word_count > 0
        """
    )
    print(f"  Overlapping files with extracted text in inventory: {cur.fetchone()[0]:,}")

    cur = conn.execute(
        """
        SELECT COUNT(*)
        FROM assets a
        JOIN inv.documents d ON a.file_path = d.file_path
        JOIN inv.text_chunks tc ON tc.document_id = d.id
        WHERE tc.embedding IS NOT NULL
        """
    )
    print(f"  Overlapping files with embeddings in inventory:    {cur.fetchone()[0]:,}")

    conn.close()


def cmd_stats(args):
    """Show summary statistics for both databases."""
    conn = _connect()

    print("\n=== Knowledge DB (index.db) ===")
    tables_k = [
        "assets", "asset_tags", "standards", "formulas",
        "code_patterns", "cross_references", "methodologies", "reference_data",
    ]
    for t in tables_k:
        cur = conn.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"  {t:25s} {cur.fetchone()[0]:>10,} rows")

    print("\n=== Inventory DB (_inventory.db) ===")
    tables_i = ["documents", "document_text", "text_chunks", "scan_history"]
    for t in tables_i:
        cur = conn.execute(f"SELECT COUNT(*) FROM inv.{t}")
        print(f"  {t:25s} {cur.fetchone()[0]:>10,} rows")

    # Asset type breakdown
    print("\n=== Knowledge asset_type breakdown ===")
    cur = conn.execute(
        "SELECT asset_type, COUNT(*) c FROM assets GROUP BY asset_type ORDER BY c DESC"
    )
    for r in cur.fetchall():
        print(f"  {r[0]:25s} {r[1]:>10,}")

    # Inventory extraction stats
    print("\n=== Inventory text extraction stats ===")
    cur = conn.execute(
        "SELECT extraction_method, COUNT(*) c FROM inv.document_text GROUP BY extraction_method ORDER BY c DESC"
    )
    for r in cur.fetchall():
        print(f"  {r[0]:25s} {r[1]:>10,}")

    conn.close()


def cmd_sql(args):
    """Run an arbitrary read-only SQL query across both databases.

    Tables from knowledge DB: assets, asset_tags, standards, formulas, etc.
    Tables from inventory DB: inv.documents, inv.document_text, inv.text_chunks, etc.
    """
    conn = _connect()
    try:
        cur = conn.execute(args.query)
        rows = cur.fetchall()
        if rows:
            columns = [desc[0] for desc in cur.description]
            _print_rows([tuple(r) for r in rows], columns, limit=args.limit)
        else:
            print("  (no results)")
    except sqlite3.Error as e:
        print(f"SQL error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


def cmd_joined_search(args):
    """Search overlapping records, enriching knowledge metadata with inventory text."""
    conn = _connect()
    like = f"%{args.query}%"

    cur = conn.execute(
        """
        SELECT
            a.file_name,
            a.title                     AS k_title,
            a.asset_type,
            a.engineering_domain,
            s.organization,
            s.doc_number,
            d.title                     AS inv_title,
            dt.word_count,
            dt.page_count,
            substr(dt.full_text, 1, 200) AS text_preview
        FROM assets a
        JOIN inv.documents d ON a.file_path = d.file_path
        LEFT JOIN standards s ON s.asset_id = a.id
        LEFT JOIN inv.document_text dt ON dt.document_id = d.id
        WHERE a.title LIKE ? OR a.file_name LIKE ?
           OR d.title LIKE ? OR dt.full_text LIKE ?
        LIMIT ?
        """,
        (like, like, like, like, args.limit),
    )
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    print(f"\n=== Joined search ({len(rows)} results) ===")
    _print_rows([tuple(r) for r in rows], columns, limit=args.limit)
    conn.close()


def cmd_health(args):
    """Database health check: row counts, index freshness, and orphaned records."""
    conn = _connect()
    ok = True

    # --- Row counts ---
    print("\n=== Row Counts ===")
    counts = {}
    for label, query in [
        ("knowledge.assets", "SELECT COUNT(*) FROM assets"),
        ("knowledge.standards", "SELECT COUNT(*) FROM standards"),
        ("knowledge.code_patterns", "SELECT COUNT(*) FROM code_patterns"),
        ("inventory.documents", "SELECT COUNT(*) FROM inv.documents"),
        ("inventory.document_text", "SELECT COUNT(*) FROM inv.document_text"),
        ("inventory.text_chunks", "SELECT COUNT(*) FROM inv.text_chunks"),
    ]:
        val = conn.execute(query).fetchone()[0]
        counts[label] = val
        print(f"  {label:35s} {val:>12,}")

    # --- Overlap ---
    print("\n=== Overlap (file_path join) ===")
    overlap = conn.execute(
        "SELECT COUNT(*) FROM assets a JOIN inv.documents d ON a.file_path = d.file_path"
    ).fetchone()[0]
    print(f"  Shared records:                     {overlap:>12,}")
    print(f"  Knowledge-only:                     {counts['knowledge.assets'] - overlap:>12,}")
    print(f"  Inventory-only:                     {counts['inventory.documents'] - overlap:>12,}")

    # --- Index freshness ---
    print("\n=== Index Freshness ===")
    newest_k = conn.execute(
        "SELECT MAX(scan_date) FROM assets WHERE scan_date IS NOT NULL"
    ).fetchone()[0]
    newest_i = conn.execute(
        "SELECT MAX(scan_date) FROM inv.documents WHERE scan_date IS NOT NULL"
    ).fetchone()[0]
    print(f"  Knowledge newest scan_date:  {newest_k or '(none)'}")
    print(f"  Inventory newest scan_date:  {newest_i or '(none)'}")

    scan_hist = conn.execute(
        "SELECT scan_date, source_dirs, files_scanned, files_added FROM inv.scan_history ORDER BY scan_date DESC LIMIT 1"
    ).fetchall()
    if scan_hist:
        row = scan_hist[0]
        print(f"  Last inventory scan run:     {row[0]}")
        print(f"    source_dirs:  {row[1]}")
        print(f"    scanned/added: {row[2]:,} / {row[3]:,}")

    # --- Orphan checks ---
    print("\n=== Orphan / Integrity Checks ===")

    # Standards without matching asset
    orphan_std = conn.execute(
        "SELECT COUNT(*) FROM standards s "
        "WHERE NOT EXISTS (SELECT 1 FROM assets a WHERE a.id = s.asset_id)"
    ).fetchone()[0]
    status = "OK" if orphan_std == 0 else "WARN"
    if orphan_std > 0:
        ok = False
    print(f"  [{status}] Standards without parent asset:     {orphan_std:,}")

    # Inventory documents without extracted text
    inv_no_text = conn.execute(
        "SELECT COUNT(*) FROM inv.documents d "
        "WHERE NOT EXISTS (SELECT 1 FROM inv.document_text dt WHERE dt.document_id = d.id)"
    ).fetchone()[0]
    pct = (inv_no_text / counts["inventory.documents"] * 100) if counts["inventory.documents"] else 0
    status = "OK" if pct < 5 else "WARN"
    if pct >= 5:
        ok = False
    print(f"  [{status}] Inventory docs without text:        {inv_no_text:,} ({pct:.1f}%)")

    # Inventory text without parent document
    text_orphan = conn.execute(
        "SELECT COUNT(*) FROM inv.document_text dt "
        "WHERE NOT EXISTS (SELECT 1 FROM inv.documents d WHERE d.id = dt.document_id)"
    ).fetchone()[0]
    status = "OK" if text_orphan == 0 else "WARN"
    if text_orphan > 0:
        ok = False
    print(f"  [{status}] Orphaned text records (no doc):     {text_orphan:,}")

    # Chunks without parent document
    chunk_orphan = conn.execute(
        "SELECT COUNT(*) FROM inv.text_chunks tc "
        "WHERE NOT EXISTS (SELECT 1 FROM inv.documents d WHERE d.id = tc.document_id)"
    ).fetchone()[0]
    status = "OK" if chunk_orphan == 0 else "WARN"
    if chunk_orphan > 0:
        ok = False
    print(f"  [{status}] Orphaned chunks (no doc):           {chunk_orphan:,}")

    # Text extraction errors
    ext_errors = conn.execute(
        "SELECT COUNT(*) FROM inv.document_text WHERE extraction_method = 'error'"
    ).fetchone()[0]
    status = "OK" if ext_errors < 50 else "WARN"
    if ext_errors >= 50:
        ok = False
    print(f"  [{status}] Text extraction errors:             {ext_errors:,}")

    # --- Summary ---
    print(f"\n{'HEALTHY' if ok else 'ISSUES DETECTED'}")
    conn.close()
    sys.exit(0 if ok else 1)


# --- CLI entry point ---------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Unified query interface for ace-knowledge + O&G-Standards databases.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
        Examples:
          %(prog)s search "API 650"
          %(prog)s search "riser fatigue" --db inventory
          %(prog)s joined "pipeline design"
          %(prog)s overlap
          %(prog)s overlap --by-hash
          %(prog)s stats
          %(prog)s health
          %(prog)s sql "SELECT COUNT(*) FROM assets WHERE engineering_domain='riser'"

        Environment variables:
          KNOWLEDGE_DB   Override path to index.db
          INVENTORY_DB   Override path to _inventory.db
        """),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    p_search = sub.add_parser("search", help="Full-text search across databases")
    p_search.add_argument("query", help="Search terms")
    p_search.add_argument(
        "--db",
        choices=["both", "knowledge", "inventory"],
        default="both",
        help="Which database(s) to search (default: both)",
    )
    p_search.add_argument("--limit", type=int, default=25, help="Max results per DB")
    p_search.set_defaults(func=cmd_search)

    # joined
    p_joined = sub.add_parser(
        "joined", help="Search overlapping records with enriched metadata"
    )
    p_joined.add_argument("query", help="Search terms (LIKE match)")
    p_joined.add_argument("--limit", type=int, default=25)
    p_joined.set_defaults(func=cmd_joined_search)

    # overlap
    p_overlap = sub.add_parser("overlap", help="Analyze record overlap")
    p_overlap.add_argument(
        "--by-hash", action="store_true", help="Match by content_hash instead of file_path"
    )
    p_overlap.set_defaults(func=cmd_overlap)

    # stats
    p_stats = sub.add_parser("stats", help="Show summary statistics")
    p_stats.set_defaults(func=cmd_stats)

    # health
    p_health = sub.add_parser("health", help="Database health check: counts, freshness, orphans")
    p_health.set_defaults(func=cmd_health)

    # sql
    p_sql = sub.add_parser("sql", help="Run arbitrary read-only SQL")
    p_sql.add_argument("query", help="SQL query (use inv. prefix for inventory tables)")
    p_sql.add_argument("--limit", type=int, default=50)
    p_sql.set_defaults(func=cmd_sql)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
