#!/usr/bin/env python3
"""
knowledge-db-cleanup.py
Identifies and marks stale entries in /mnt/ace/.ace-knowledge/index.db
- Checks if file_path entries still exist on disk
- Detects symlinks and records canonical paths
- Marks missing files with status='removed'
"""

import sqlite3
import os
import sys
import time
from collections import Counter

DB_PATH = "/mnt/ace/.ace-knowledge/index.db"
BATCH_SIZE = 10_000
PREFIX = "/mnt/ace/"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    cur = conn.cursor()

    # Add status and canonical_path columns if missing
    cols = {r[1] for r in cur.execute("PRAGMA table_info(assets)").fetchall()}
    if "status" not in cols:
        cur.execute("ALTER TABLE assets ADD COLUMN status TEXT DEFAULT 'active'")
        print("Added 'status' column")
    if "canonical_path" not in cols:
        cur.execute("ALTER TABLE assets ADD COLUMN canonical_path TEXT")
        print("Added 'canonical_path' column")
    conn.commit()

    # Count total
    total = cur.execute("SELECT count(*) FROM assets").fetchone()[0]
    print(f"Total records: {total:,}")

    stats = Counter()
    t0 = time.time()
    processed = 0

    # Batch through all records
    cur.execute("SELECT id, file_path FROM assets")
    while True:
        rows = cur.fetchmany(BATCH_SIZE)
        if not rows:
            break

        updates_removed = []
        updates_symlink = []
        updates_valid = []

        for row_id, file_path in rows:
            # Skip paths not under /mnt/ace/ (other mounts)
            if not file_path.startswith(PREFIX):
                stats["skipped_other_mount"] += 1
                continue

            if os.path.islink(file_path):
                # It's a symlink — resolve canonical path
                try:
                    canon = os.path.realpath(file_path)
                    if os.path.exists(canon):
                        updates_symlink.append((canon, row_id))
                        stats["symlink_valid"] += 1
                    else:
                        # Dangling symlink
                        updates_removed.append((row_id,))
                        stats["symlink_dangling"] += 1
                except OSError:
                    updates_removed.append((row_id,))
                    stats["symlink_error"] += 1
            elif os.path.exists(file_path):
                stats["valid"] += 1
            else:
                updates_removed.append((row_id,))
                stats["missing"] += 1

        # Batch updates
        if updates_removed:
            conn.executemany(
                "UPDATE assets SET status='removed' WHERE id=?",
                updates_removed
            )
        if updates_symlink:
            conn.executemany(
                "UPDATE assets SET status='symlink', canonical_path=? WHERE id=?",
                updates_symlink
            )

        processed += len(rows)
        elapsed = time.time() - t0
        rate = processed / elapsed if elapsed > 0 else 0
        pct = processed / total * 100
        print(f"  {processed:>10,} / {total:,}  ({pct:5.1f}%)  {rate:,.0f} rows/s  "
              f"valid={stats['valid']:,}  missing={stats['missing']:,}  "
              f"symlink={stats['symlink_valid']:,}  dangling={stats['symlink_dangling']:,}",
              flush=True)

        # Commit every 100k rows
        if processed % 100_000 < BATCH_SIZE:
            conn.commit()

    conn.commit()
    elapsed = time.time() - t0

    # Final counts from DB
    count_active = conn.execute("SELECT count(*) FROM assets WHERE status='active' OR status IS NULL").fetchone()[0]
    count_removed = conn.execute("SELECT count(*) FROM assets WHERE status='removed'").fetchone()[0]
    count_symlink = conn.execute("SELECT count(*) FROM assets WHERE status='symlink'").fetchone()[0]

    print(f"\n{'='*60}")
    print(f"Completed in {elapsed:.1f}s")
    print(f"  Total records:     {total:>10,}")
    print(f"  Valid (active):    {count_active:>10,}")
    print(f"  Removed (stale):   {count_removed:>10,}")
    print(f"  Symlinks:          {count_symlink:>10,}")
    print(f"  Skipped (other):   {stats['skipped_other_mount']:>10,}")
    print(f"  Dangling symlinks: {stats['symlink_dangling']:>10,}")
    print(f"{'='*60}")

    # Write stats for summary generation
    with open("/tmp/kb-cleanup-stats.txt", "w") as f:
        f.write(f"total={total}\n")
        f.write(f"active={count_active}\n")
        f.write(f"removed={count_removed}\n")
        f.write(f"symlink={count_symlink}\n")
        f.write(f"skipped={stats['skipped_other_mount']}\n")
        f.write(f"dangling={stats['symlink_dangling']}\n")
        f.write(f"elapsed={elapsed:.1f}\n")

    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()
