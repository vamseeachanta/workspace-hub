from __future__ import annotations

import yaml

from adapters.base import AdapterError, BaseAdapter, SearchResult, token_score


class YamlCatalogAdapter(BaseAdapter):
    def search(self, tokens: list[str], limit: int) -> list[SearchResult]:
        params = self.index.adapter_params
        path_fields = params.get("path_fields", ["path"])
        text_fields = params.get("text_fields", [])
        try:
            with open(self.index.path, "r", encoding="utf-8") as handle:
                doc = yaml.safe_load(handle) or {}
        except (OSError, yaml.YAMLError) as exc:
            raise AdapterError(f"{self.index.id}: yaml read failed: {exc}") from exc

        rows = []
        for ordinal, item in enumerate(_items(doc, params.get("items_key", "auto"))):
            raw_path = next((item.get(field) for field in path_fields if item.get(field)), None)
            if not raw_path:
                continue
            score, matched = token_score(item, tokens, [*path_fields, *text_fields])
            if score == 0:
                continue
            meta = {key: value for key, value in item.items() if key not in path_fields}
            meta["matched_tokens"] = matched
            meta["total_tokens"] = len(tokens)
            rows.append(
                (
                    -score,
                    ordinal,
                    SearchResult(
                        raw_path=str(raw_path),
                        source_index=self.index.id,
                        adapter=self.index.adapter,
                        raw_score=score,
                        rank_basis="token_match",
                        meta=meta,
                    ),
                )
            )
        return [row[2] for row in sorted(rows)[:limit]]


def _items(value, items_key):
    if items_key != "auto" and isinstance(value, dict):
        value = value.get(items_key, [])
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        yield from value
        return
    if isinstance(value, dict):
        for child in value.values():
            yield from _items(child, "auto")
