"""Shared helpers for the drive-index builder tests (module named uniquely —
bare `conftest` imports collide across suites in combined pytest runs)."""
import os
import sqlite3
from pathlib import Path

def rows(db: Path, sql: str, params=()):
    conn = sqlite3.connect(db)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()



def make_raw_byte_file(root: Path) -> None:
    parent = root / "documents"
    raw = os.fsencode(parent) + b"/bad_\xff_name.txt"
    fd = os.open(raw, os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        os.write(fd, b"bad name")
    finally:
        os.close(fd)
