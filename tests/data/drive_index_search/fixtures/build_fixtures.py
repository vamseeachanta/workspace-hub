from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parent


def build_sqlite(path: Path) -> None:
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE assets (
            file_path TEXT NOT NULL,
            file_name TEXT,
            file_size INTEGER,
            modified_date TEXT,
            engineering_domain TEXT
        );
        CREATE VIRTUAL TABLE assets_fts
        USING fts5(title, description, content='assets', content_rowid='rowid');
        """
    )
    rows = [
        ("/fixture/ace/mooring-fatigue.pdf", "mooring-fatigue.pdf", 100, "2026-01-01", "marine", "mooring fatigue", "mooring fatigue design note"),
        ("/fixture/ace/mooring-only.pdf", "mooring-only.pdf", 90, "2026-01-02", "marine", "mooring", "line layout"),
        ("/fixture/ace/fatigue-only.pdf", "fatigue-only.pdf", 80, "2026-01-03", "marine", "fatigue", "detail check"),
        ("/fixture/ace/riser-note.pdf", "riser-note.pdf", 70, "2026-01-04", "marine", "riser", "unrelated"),
    ]
    for file_path, file_name, size, modified, domain, title, description in rows:
        cur = conn.execute(
            "INSERT INTO assets(file_path, file_name, file_size, modified_date, engineering_domain) VALUES (?, ?, ?, ?, ?)",
            (file_path, file_name, size, modified, domain),
        )
        conn.execute(
            "INSERT INTO assets_fts(rowid, title, description) VALUES (?, ?, ?)",
            (cur.lastrowid, title, description),
        )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    build_sqlite(ROOT / "fixture.db")
