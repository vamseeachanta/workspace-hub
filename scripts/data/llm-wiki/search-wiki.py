#!/usr/bin/env python3
"""Search the llm-wiki across OrcaFlex, OrcaWave, OrcFXAPI, and papers.

Usage:  python3 search-wiki.py "vessel RAO" [--product orcaflex] [--deep] [--limit 10]
Modes:  --fast (default) index only | --deep full-text grep across markdown files
"""
from __future__ import annotations
import argparse, json, math, re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WIKI_DIR = REPO_ROOT / "data" / "llm-wiki"
INDEX_PATH = WIKI_DIR / "search-index.json"
PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "papers"]
TITLE_W, SECTION_W, BODY_W = 3.0, 2.0, 1.0

def tokenize(text: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) > 1]

def _md_path(product: str, topic: dict) -> Path:
    fname = topic["file"] if topic["file"].endswith(".md") else topic["file"] + ".md"
    return WIKI_DIR / product / fname if product == "papers" else WIKI_DIR / product / "topics" / fname

def _load_topics(product: str) -> list[dict]:
    idx = WIKI_DIR / product / "index.json"
    if not idx.exists():
        return []
    data = json.loads(idx.read_text())
    return data.get("papers", []) if product == "papers" else data.get("topics", [])

def build_index(force: bool = False) -> list[dict]:
    """Build combined search index; auto-rebuilds when source index.json files are newer."""
    if not force and INDEX_PATH.exists():
        ts = INDEX_PATH.stat().st_mtime
        if not any((WIKI_DIR / p / "index.json").exists() and
                    (WIKI_DIR / p / "index.json").stat().st_mtime > ts for p in PRODUCTS):
            return json.loads(INDEX_PATH.read_text())
    entries: list[dict] = []
    for product in PRODUCTS:
        for t in _load_topics(product):
            title, secs = t.get("title", ""), t.get("sections", [])
            sp = t.get("section_path", [])
            entries.append({
                "product": product,
                "file": str(_md_path(product, t).relative_to(WIKI_DIR)),
                "title": title, "sections": secs,
                "category": " > ".join(sp) if sp else "",
                "title_tokens": tokenize(title),
                "section_tokens": tokenize(" ".join(secs + sp)),
            })
    supp = WIKI_DIR / "supplementary"
    if supp.is_dir():
        for md in sorted(supp.glob("*.md")):
            title = md.stem.replace("-", " ").title()
            entries.append({
                "product": "supplementary", "file": f"supplementary/{md.name}",
                "title": title, "sections": [], "category": "Supplementary",
                "title_tokens": tokenize(title), "section_tokens": [],
            })
    INDEX_PATH.write_text(json.dumps(entries, indent=2))
    return entries

def _idf(term: str, entries: list[dict]) -> float:
    dc = sum(1 for e in entries if term in e["title_tokens"] or term in e["section_tokens"])
    return math.log(len(entries) / dc) if dc else 0.0

def _best_section(sections: list[str], terms: list[str]) -> str:
    for s in sections:
        if any(t in s.lower() for t in terms):
            return s
    return ""

def search_fast(query: str, entries: list[dict],
                product_filter: str | None = None, limit: int = 20) -> list[dict]:
    """TF-IDF search over index (titles + sections)."""
    terms = tokenize(query)
    if not terms:
        return []
    idf = {t: _idf(t, entries) for t in terms}
    results = []
    for e in entries:
        if product_filter and e["product"] != product_filter:
            continue
        score, matched = 0.0, []
        for t in terms:
            tf = e["title_tokens"].count(t) * TITLE_W + e["section_tokens"].count(t) * SECTION_W
            if tf:
                matched.append(t)
                score += tf * idf[t]
        if score > 0:
            snip = e["title"]
            bs = _best_section(e["sections"], terms)
            if bs:
                snip += f" > {bs}"
            results.append({"file": e["file"], "product": e["product"],
                            "title": e["title"], "score": round(score, 3),
                            "snippet": snip, "matched": matched})
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:limit]

def search_deep(query: str, entries: list[dict],
                product_filter: str | None = None, limit: int = 20) -> list[dict]:
    """Full-text search across markdown files with TF-IDF scoring."""
    terms = tokenize(query)
    if not terms:
        return []
    doc_freq: dict[str, int] = {t: 0 for t in terms}
    texts: list[tuple[dict, str]] = []
    for e in entries:
        if product_filter and e["product"] != product_filter:
            continue
        p = WIKI_DIR / e["file"]
        if not p.exists():
            continue
        txt = p.read_text(errors="replace").lower()
        texts.append((e, txt))
        for t in terms:
            if t in txt:
                doc_freq[t] += 1
    n = len(texts)
    results = []
    for e, txt in texts:
        btok = tokenize(txt)
        score, matched = 0.0, []
        for t in terms:
            tf = (e["title_tokens"].count(t) * TITLE_W +
                  e["section_tokens"].count(t) * SECTION_W + btok.count(t) * BODY_W)
            if tf > 0:
                matched.append(t)
                score += tf * (math.log(n / doc_freq[t]) if doc_freq[t] else 0)
        if score > 0:
            snip = e["title"]
            for t in terms:
                idx = txt.find(t)
                if idx >= 0:
                    snip = "..." + txt[max(0, idx-40):idx+60].replace("\n", " ").strip() + "..."
                    break
            results.append({"file": e["file"], "product": e["product"],
                            "title": e["title"], "score": round(score, 3),
                            "snippet": snip, "matched": matched})
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:limit]

def search(query: str, deep: bool = False, product: str | None = None,
           limit: int = 20) -> list[dict]:
    """Main entry point — importable API."""
    entries = build_index()
    return search_deep(query, entries, product, limit) if deep else \
           search_fast(query, entries, product, limit)

def print_results(results: list[dict], query: str, deep: bool) -> None:
    mode = "deep" if deep else "fast"
    print(f"\n  Search: \"{query}\" ({mode} mode, {len(results)} results)\n")
    if not results:
        print("  No results found.")
        return
    for i, r in enumerate(results, 1):
        print(f"  {i:>2}. [{r['product']}] {r['title']}")
        print(f"      Score: {r['score']}  File: {r['file']}")
        print(f"      {r['snippet']}\n")

def main():
    ap = argparse.ArgumentParser(description="Search the llm-wiki")
    ap.add_argument("query", help="Search query")
    ap.add_argument("--product", choices=PRODUCTS + ["supplementary"])
    ap.add_argument("--deep", action="store_true", help="Full-text search")
    ap.add_argument("--fast", action="store_true", default=True, help="Index-only (default)")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--rebuild", action="store_true", help="Force rebuild index")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()
    if args.rebuild:
        build_index(force=True)
        print("Search index rebuilt.")
    results = search(args.query, deep=args.deep, product=args.product, limit=args.limit)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_results(results, args.query, args.deep)

if __name__ == "__main__":
    main()
