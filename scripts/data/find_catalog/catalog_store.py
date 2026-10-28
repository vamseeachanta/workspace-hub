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

# Software tuning basis, not engineering coefficients or calibrated relevance:
# 20 hits keep the default response compact; the 1000-hit ceiling bounds response
# memory. SQLite FTS5 snippet() permits 1..64 tokens; 32 gives local context,
# with a separate 320-character ceiling for long tokens. Title/body/locator BM25
# weights 5/1/1 prefer title matches; these are initial heuristics, not measured
# quality claims. SQLite FTS5 reference: https://sqlite.org/fts5.html
DEFAULT_LIMIT = 20
MAX_LIMIT = 1000
EXCERPT_TOKENS = 32
EXCERPT_CHARS = 320
BM25_WEIGHTS = (5.0, 1.0, 1.0)


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
    for source in config["sources"]:
        root = Path(source["path"]).resolve()
        if (target == root or (root.is_dir() and target.is_relative_to(root))
                or (target.exists() and root.is_file() and target.samefile(root))):
            raise CatalogError("catalog output must not overlap configured inputs")
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


def find(path, query, *, domain=None, source=None, exposure=None, limit=DEFAULT_LIMIT):
    path = private_path(path)
    if not path.is_file():
        raise CatalogError("catalog missing; build it before searching")
    if type(limit) is not int or not 0 <= limit <= MAX_LIMIT:
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
    sql = ("SELECT r.metadata, snippet(search, 1, '', '', ' … ', ?) FROM search "
           "JOIN records r ON r.rowid = search.rowid WHERE " + " AND ".join(conditions)
           + " ORDER BY bm25(search, ?, ?, ?), r.source, r.id, r.locator LIMIT ?")
    try:
        with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as conn:
            results = []
            for metadata, excerpt in conn.execute(sql, (EXCERPT_TOKENS, *values, *BM25_WEIGHTS, limit)):
                result = json.loads(metadata)
                result.pop("body", None)
                result["excerpt"] = excerpt[:EXCERPT_CHARS]
                results.append(result)
            return results
    except sqlite3.Error as exc:
        raise CatalogError("catalog cannot be searched; check schema and rebuild") from exc
