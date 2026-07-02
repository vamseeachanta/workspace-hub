from __future__ import annotations

from adapters.base import SearchResult
from pathnorm import canonicalize_path


FILENAME_HIT_BONUS = 0.25
ALL_TOKENS_BONUS = 0.25


def ranked_merge(results: list[SearchResult], alias_map: dict[str, str], limit: int) -> list[SearchResult]:
    deduped: dict[str, SearchResult] = {}
    for result in results:
        result.canonical_path = canonicalize_path(result.raw_path, alias_map)
        result.score = _normalized_score(result)
        existing = deduped.get(result.canonical_path)
        if existing is None:
            deduped[result.canonical_path] = result
            continue
        keep, other = (result, existing) if _sort_key(result) < _sort_key(existing) else (existing, result)
        also_in = list(keep.meta.get("also_in", []))
        also_in.append(other.source_index)
        also_in.extend(other.meta.get("also_in", []))
        keep.meta["also_in"] = sorted(set(also_in))
        deduped[result.canonical_path] = keep
    return sorted(deduped.values(), key=_sort_key)[:limit]


def _normalized_score(result: SearchResult) -> float:
    if result.rank_basis == "fts_bm25":
        magnitude = max(0.0, -float(result.raw_score))
        return 1.0 / (1.0 + magnitude)
    matched = float(result.meta.get("matched_tokens", 0))
    total = max(float(result.meta.get("total_tokens", 1)), 1.0)
    score = matched / total
    path_lower = result.raw_path.rsplit("/", 1)[-1].lower()
    query_tokens = result.meta.get("query_tokens", [])
    if any(token in path_lower for token in query_tokens):
        score += FILENAME_HIT_BONUS
    if matched >= total:
        score += ALL_TOKENS_BONUS
    return max(0.0, min(score, 1.0))


def _sort_key(result: SearchResult) -> tuple[float, str, str]:
    return (-(result.score if result.score is not None else 0.0), result.canonical_path or result.raw_path, result.source_index)
