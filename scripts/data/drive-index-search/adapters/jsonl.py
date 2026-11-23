from __future__ import annotations

import heapq
import json

from adapters.base import AdapterError, BaseAdapter, SearchResult, push_top, token_score


OVERSAMPLE = 4


class JsonlAdapter(BaseAdapter):
    def search(self, tokens: list[str], limit: int) -> list[SearchResult]:
        params = self.index.adapter_params
        path_field = params["path_field"]
        search_fields = params.get("search_fields", [path_field])
        cap = max(limit * OVERSAMPLE, limit, 1)
        heap: list[tuple[float, int, SearchResult]] = []
        malformed = 0
        lowered = tokens
        try:
            with open(self.index.path, "r", encoding="utf-8", errors="replace") as handle:
                for line_no, line in enumerate(handle, start=1):
                    raw_line = line.lower()
                    if not any(token in raw_line for token in lowered):
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        malformed += 1
                        continue
                    score, matched = token_score(row, tokens, search_fields)
                    if score == 0:
                        continue
                    raw_path = row.get(path_field)
                    if not raw_path:
                        continue
                    meta = {key: value for key, value in row.items() if key != path_field}
                    meta["matched_tokens"] = matched
                    meta["total_tokens"] = len(tokens)
                    meta["malformed_lines"] = malformed
                    result = SearchResult(
                        raw_path=str(raw_path),
                        source_index=self.index.id,
                        adapter=self.index.adapter,
                        raw_score=score,
                        rank_basis="token_match",
                        meta=meta,
                    )
                    push_top(heap, (score, line_no, result), cap)
        except OSError as exc:
            raise AdapterError(f"{self.index.id}: jsonl read failed: {exc}") from exc

        return [item[2] for item in sorted(heap, key=lambda item: (-item[0], item[1]))[:limit]]
