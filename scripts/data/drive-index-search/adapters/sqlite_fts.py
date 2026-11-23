from __future__ import annotations

import sqlite3
import threading

from adapters.base import AdapterError, BaseAdapter, SearchResult


def quote_fts_token(token: str) -> str:
    return '"' + token.replace('"', '""') + '"'


class SqliteFtsAdapter(BaseAdapter):
    def __init__(self, index):
        super().__init__(index)
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.Lock()

    def interrupt(self) -> None:
        with self._lock:
            if self._conn is not None:
                self._conn.interrupt()

    def search(self, tokens: list[str], limit: int) -> list[SearchResult]:
        params = self.index.adapter_params
        fts_table = _identifier(params["fts_table"])
        base_table = _identifier(params["base_table"])
        path_column = _identifier(params["path_column"])
        select_columns = [_identifier(col) for col in params.get("select_columns", [])]
        match = " OR ".join(quote_fts_token(token) for token in tokens)
        if not match:
            return []
        select_sql = ", ".join([f"base.{path_column} AS raw_path", *[f"base.{col} AS {col}" for col in select_columns]])
        sql = (
            f"SELECT {select_sql}, bm25({fts_table}) AS bm25_score "
            f"FROM {fts_table} JOIN {base_table} base ON base.rowid = {fts_table}.rowid "
            f"WHERE {fts_table} MATCH ? ORDER BY bm25_score LIMIT ?"
        )
        uri = f"file:{self.index.path}?mode=ro"
        try:
            conn = sqlite3.connect(uri, uri=True)
            with self._lock:
                self._conn = conn
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, (match, limit)).fetchall()
        except sqlite3.Error as exc:
            raise AdapterError(f"{self.index.id}: sqlite query failed: {exc}") from exc
        finally:
            with self._lock:
                conn_to_close = self._conn
                self._conn = None
            if conn_to_close is not None:
                conn_to_close.close()

        results = []
        for row in rows:
            meta = {key: row[key] for key in row.keys() if key not in {"raw_path", "bm25_score"}}
            meta["matched_tokens"] = len(tokens)
            meta["total_tokens"] = len(tokens)
            results.append(
                SearchResult(
                    raw_path=row["raw_path"],
                    source_index=self.index.id,
                    adapter=self.index.adapter,
                    raw_score=float(row["bm25_score"]),
                    rank_basis="fts_bm25",
                    meta=meta,
                )
            )
        return results


def _identifier(value: str) -> str:
    if not value.replace("_", "").isalnum():
        raise AdapterError(f"unsafe sqlite identifier: {value}")
    return value
