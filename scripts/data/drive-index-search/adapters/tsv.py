from __future__ import annotations

import csv

from adapters.base import AdapterError, BaseAdapter, SearchResult, push_top, token_score


OVERSAMPLE = 4


class TsvAdapter(BaseAdapter):
    def search(self, tokens: list[str], limit: int) -> list[SearchResult]:
        params = self.index.adapter_params
        path_column = params["path_column"]
        search_columns = params.get("search_columns", [path_column])
        passthrough = params.get("passthrough_columns", [])
        cap = max(limit * OVERSAMPLE, limit, 1)
        heap = []
        try:
            with open(self.index.path, "r", encoding="utf-8", errors="replace", newline="") as handle:
                reader = csv.DictReader(handle, delimiter="\t")
                header = reader.fieldnames or []
                required = {path_column, *search_columns, *passthrough}
                missing = sorted(required.difference(header))
                if missing:
                    raise AdapterError(f"{self.index.id}: missing required column(s): {', '.join(missing)}")
                for line_no, row in enumerate(reader, start=2):
                    if not any(token in "\t".join(row.values()).lower() for token in tokens):
                        continue
                    score, matched = token_score(row, tokens, search_columns)
                    if score == 0:
                        continue
                    meta = {column: row.get(column) for column in passthrough}
                    meta["matched_tokens"] = matched
                    meta["total_tokens"] = len(tokens)
                    result = SearchResult(
                        raw_path=row[path_column],
                        source_index=self.index.id,
                        adapter=self.index.adapter,
                        raw_score=score,
                        rank_basis="token_match",
                        meta=meta,
                    )
                    push_top(heap, (score, line_no, result), cap)
        except OSError as exc:
            raise AdapterError(f"{self.index.id}: tsv read failed: {exc}") from exc
        return [item[2] for item in sorted(heap, key=lambda item: (-item[0], item[1]))[:limit]]
