#!/usr/bin/env python3
"""skill_router.py — provider-neutral skill ranking over the full index (#3190).

Ranks ALL skills for a (query, provider, context_tags) triple from
config/agents/skill-index-full.yaml. Provider is RECORDED for audit but does NOT
affect ranking (skills are provider-neutral — the whole point). Backfilled
`when_to_use` entries are DOWN-WEIGHTED (auto-derived, low fidelity). Deterministic
tie-break by id so every provider sees the identical ordered set. Returns None on
no match (fail-open: prepend nothing).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX = REPO_ROOT / "config" / "agents" / "skill-index-full.yaml"
BACKFILL_WEIGHT = 0.2  # auto-derived when_to_use scores at 1/5 of an authored hit

_WORD = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return {t for t in _WORD.findall((text or "").lower()) if len(t) > 2}


def load_index(path=DEFAULT_INDEX) -> list[dict]:
    with open(path, "r", encoding="utf-8") as fh:
        return (yaml.safe_load(fh) or {}).get("skills", [])


def rank(query: str, context_tags=None, index=None, top_k: int = 5) -> list[dict]:
    if index is None:
        index = load_index()
    qtok = _tokens(query)
    ctags = {str(t).lower() for t in (context_tags or [])}
    scored = []
    for sk in index:
        wtok = _tokens(sk.get("when_to_use", ""))
        base = len(qtok & wtok)
        if base and sk.get("when_to_use_source") == "backfill":
            base *= BACKFILL_WEIGHT
        tag_hit = len(ctags & ({sk.get("family", "").lower()} | _tokens(sk.get("description", ""))))
        score = base + 0.5 * tag_hit
        if score > 0:
            scored.append((score, sk["id"], sk))
    scored.sort(key=lambda r: (-r[0], r[1]))  # deterministic: score desc, then id
    return [{"id": i, "score": round(s, 3), "source": sk.get("when_to_use_source")} for s, i, sk in scored[:top_k]]


def top_skill(query: str, provider: str = None, context_tags=None, index=None):
    """Top-1 matched skill id (provider recorded, NOT used to rank); None if no match."""
    r = rank(query, context_tags=context_tags, index=index, top_k=1)
    return r[0]["id"] if r else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("query")
    ap.add_argument("--provider", default=None, help="recorded for audit; does NOT affect ranking")
    ap.add_argument("--context-tags", action="append", default=[])
    ap.add_argument("--index", default=str(DEFAULT_INDEX))
    ap.add_argument("--top-k", type=int, default=5)
    args = ap.parse_args()
    idx = load_index(args.index)
    for hit in rank(args.query, context_tags=args.context_tags, index=idx, top_k=args.top_k):
        print(f"{hit['score']:>6}  {hit['id']}  [{hit['source']}]")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
