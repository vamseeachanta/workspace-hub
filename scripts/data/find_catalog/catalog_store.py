"""Transactional SQLite FTS5 discovery catalog stored outside every Git tree."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import tempfile
from collections import Counter
from contextlib import closing
from pathlib import Path

from catalog_sources import records


class CatalogError(ValueError):
    """Configuration or catalog failure that cannot be reported as a search miss."""


def private_path(path):
    path = Path(path).resolve()
    markers = (parent / ".git" for parent in path.parents)
    if any(marker.is_file() or (marker / "HEAD").is_file() for marker in markers):
        raise CatalogError("catalog database must be outside every Git working tree")
    return path


def build(config):
    target = private_path(config["database"])
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, name = tempfile.mkstemp(prefix=".catalog-", suffix=".db", dir=target.parent)
    os.close(descriptor)
    temporary = Path(name)
    counts = Counter({source["id"]: 0 for source in config["sources"]})
    try:
        with closing(sqlite3.connect(temporary)) as conn:
            conn.execute("CREATE TABLE records (source TEXT, id TEXT, locator TEXT, domain TEXT, "
                         "exposure TEXT, title TEXT, body TEXT, metadata TEXT, "
                         "PRIMARY KEY(source, id, locator))")
            conn.execute("CREATE VIRTUAL TABLE search USING fts5(title, body, locator, "
                         "content='records', content_rowid='rowid')")
            conn.execute("CREATE INDEX filters ON records(source, domain, exposure)")
            for item in records(config):
                fields = (item[key] for key in ("source", "id", "locator", "domain", "exposure", "title", "body"))
                conn.execute("INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             (*fields, json.dumps(item, ensure_ascii=False, default=str)))
                counts[item["source"]] += 1
            conn.execute("INSERT INTO search(search) VALUES ('rebuild')")
            conn.execute("CREATE TABLE catalog_info (version INTEGER, counts TEXT)")
            conn.execute("INSERT INTO catalog_info VALUES (1, ?)", (json.dumps(counts),))
            conn.commit()
        with closing(sqlite3.connect(temporary)) as conn:
            if conn.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise CatalogError("catalog integrity check failed")
        temporary.replace(target)
        return dict(counts)
    finally:
        temporary.unlink(missing_ok=True)


def find(path, query, *, domain=None, source=None, exposure=None, limit=20):
    path = private_path(path)
    if not path.is_file():
        raise CatalogError("catalog missing; build it before searching")
    if not 0 <= limit <= 1000:
        raise CatalogError("limit must be between 0 and 1000")
    tokens = re.findall(r"[^\W_]+", query, re.UNICODE)
    if not tokens or limit == 0:
        return []
    match = " AND ".join('"' + token + '"' for token in tokens)
    conditions = ["search MATCH ?"]
    values = [match]
    for key, value in (("domain", domain), ("source", source), ("exposure", exposure)):
        if value is not None:
            conditions.append(f"r.{key} = ?")
            values.append(value)
    sql = ("SELECT r.metadata, snippet(search, 1, '', '', ' … ', 32) FROM search "
           "JOIN records r ON r.rowid = search.rowid WHERE " + " AND ".join(conditions)
           + " ORDER BY bm25(search, 5.0, 1.0, 1.0), r.source, r.id, r.locator LIMIT ?")
    try:
        with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as conn:
            results = []
            for metadata, excerpt in conn.execute(sql, (*values, limit)):
                result = json.loads(metadata)
                result.pop("body", None)
                result["excerpt"] = excerpt[:320]
                results.append(result)
            return results
    except sqlite3.Error as exc:
        raise CatalogError("catalog cannot be searched; check schema and rebuild") from exc
