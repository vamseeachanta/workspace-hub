"""Shared helpers for the drive-index refresh tests (module named uniquely —
bare `conftest` imports collide across suites in combined pytest runs)."""
import sqlite3
from pathlib import Path

def rows(db: Path, sql: str, params=()):
    conn = sqlite3.connect(db)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()
