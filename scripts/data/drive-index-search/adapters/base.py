from __future__ import annotations

from dataclasses import dataclass, field
import math
import re
from typing import Any


TOKEN_RE = re.compile(r"[A-Za-z0-9_./&+-]+")


class AdapterError(Exception):
    pass


@dataclass
class SearchResult:
    raw_path: str
    source_index: str
    adapter: str
    raw_score: float
    rank_basis: str
    meta: dict[str, Any] = field(default_factory=dict)
    canonical_path: str | None = None
    score: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "canonical_path": self.canonical_path or self.raw_path,
            "raw_path": self.raw_path,
            "source_index": self.source_index,
            "adapter": self.adapter,
            "score": self.score if self.score is not None else self.raw_score,
            "rank_basis": self.rank_basis,
            "meta": self.meta,
        }


def tokenize(query: str) -> list[str]:
    tokens = [token.lower() for token in TOKEN_RE.findall(query)]
    return [token for token in tokens if token]


def field_text(row: dict[str, Any], fields: list[str]) -> str:
    values = []
    for field_name in fields:
        value = row.get(field_name)
        if value is not None:
            values.append(str(value))
    return " ".join(values).lower()


def token_score(row: dict[str, Any], tokens: list[str], fields: list[str]) -> tuple[float, int]:
    if not tokens:
        return 0.0, 0
    text = field_text(row, fields)
    matched = sum(1 for token in tokens if token in text)
    if matched == 0:
        return 0.0, 0
    density = sum(text.count(token) for token in tokens)
    return matched / len(tokens) + min(math.log1p(density) / 10.0, 0.2), matched


def push_top(heap: list[tuple[float, int, SearchResult]], item: tuple[float, int, SearchResult], cap: int) -> None:
    import heapq

    if len(heap) < cap:
        heapq.heappush(heap, item)
    elif item[0] > heap[0][0]:
        heapq.heapreplace(heap, item)


class BaseAdapter:
    def __init__(self, index):
        self.index = index

    def search(self, tokens: list[str], limit: int) -> list[SearchResult]:
        raise NotImplementedError

    def interrupt(self) -> None:
        return None
