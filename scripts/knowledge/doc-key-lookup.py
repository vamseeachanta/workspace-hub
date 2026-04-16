#!/usr/bin/env python3
"""doc-key-lookup.py — Unified lookup across the intelligence pyramid by doc_key.

Given a doc_key (content_hash), path fragment, or standard ID, returns all related
artifacts: registry entries, file paths, wiki pages, and standards-transfer-ledger
entries. Implements the lookup service described in #2207 provenance contract.

Usage:
    uv run scripts/knowledge/doc-key-lookup.py <query> [--by key|path|standard] [--json]

Examples:
    uv run scripts/knowledge/doc-key-lookup.py sha256:0d75d96f237eb621b360267e00a0f0de
    uv run scripts/knowledge/doc-key-lookup.py "API-RP-2SK" --by standard
    uv run scripts/knowledge/doc-key-lookup.py "OMAE2009-79769" --by path
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX_JSONL = REPO_ROOT / "data" / "document-index" / "index.jsonl"
STD_LEDGER = REPO_ROOT / "data" / "document-index" / "standards-transfer-ledger.yaml"
WIKIS_DIR = REPO_ROOT / "knowledge" / "wikis"
WIKI_DOMAINS = ["engineering", "marine-engineering", "maritime-law", "naval-architecture", "personal"]


def normalize_key(key: str) -> str:
    """Strip sha256: prefix for comparison."""
    if key.startswith("sha256:"):
        return key[7:]
    return key.lower()


def search_index_by_key(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search index.jsonl by content_hash (doc_key)."""
    if not INDEX_JSONL.exists():
        return []

    normalized = normalize_key(query)
    matches = []

    with open(INDEX_JSONL, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            ch = record.get("content_hash", "")
            if normalize_key(str(ch)) == normalized:
                matches.append(record)
                if len(matches) >= limit:
                    break

    return matches


def search_index_by_path(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search index.jsonl by path fragment (case-insensitive)."""
    if not INDEX_JSONL.exists():
        return []

    query_lower = query.lower()
    matches = []

    with open(INDEX_JSONL, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            path = str(record.get("path", "")).lower()
            if query_lower in path:
                matches.append(record)
                if len(matches) >= limit:
                    break

    return matches


def search_standards_ledger(query: str, by: str = "standard") -> List[Dict[str, Any]]:
    """Search standards-transfer-ledger.yaml by standard ID or title."""
    if not STD_LEDGER.exists():
        return []

    text = STD_LEDGER.read_text(encoding="utf-8")
    if not HAS_YAML:
        # Minimal search: grep for the query
        matches = []
        for line in text.split("\n"):
            if query.lower() in line.lower():
                matches.append({"match_line": line.strip()})
        return matches[:10]

    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        return []

    entries = data.get("standards", data.get("entries", []))
    if isinstance(data, dict) and not entries:
        # The ledger may be a flat list of standards keyed by various names
        # Try to find entries that match
        entries = []
        for key, val in data.items():
            if isinstance(val, dict):
                val["_key"] = key
                entries.append(val)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        entries.append(item)

    query_lower = query.lower()
    matches = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        entry_id = str(entry.get("id", "")).lower()
        title = str(entry.get("title", "")).lower()
        doc_paths = entry.get("doc_path", entry.get("doc_paths", ""))
        if isinstance(doc_paths, list):
            doc_paths = " ".join(str(p) for p in doc_paths)

        if (query_lower in entry_id
            or query_lower in title
            or query_lower in str(doc_paths).lower()):
            matches.append(entry)

    return matches[:20]


def search_wiki_pages(query: str, by: str = "key") -> List[Dict[str, str]]:
    """Search wiki pages for references to a doc_key or standard ID."""
    query_lower = query.lower()
    normalized = normalize_key(query) if by == "key" else query_lower
    matches = []

    for domain in WIKI_DOMAINS:
        wiki_dir = WIKIS_DIR / domain / "wiki"
        if not wiki_dir.exists():
            continue

        for md_file in wiki_dir.rglob("*.md"):
            if md_file.name in ("index.md", "log.md"):
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            if normalized in content.lower():
                rel = md_file.relative_to(REPO_ROOT)
                # Extract title from frontmatter
                title = md_file.stem.replace("-", " ").title()
                if content.startswith("---"):
                    end = content.find("\n---", 3)
                    if end != -1:
                        for line in content[3:end].split("\n"):
                            if line.strip().startswith("title:"):
                                title = line.split(":", 1)[1].strip().strip('"\'')
                                break

                matches.append({
                    "domain": domain,
                    "page": str(rel),
                    "title": title,
                })
                if len(matches) >= 20:
                    return matches

    return matches


def run_lookup(query: str, by: str = "key", json_output: bool = False) -> int:
    """Run unified lookup and display results."""
    results = {
        "query": query,
        "lookup_type": by,
        "timestamp": datetime.now().isoformat(),
        "index_records": [],
        "standards_ledger": [],
        "wiki_pages": [],
    }
    total = 0

    if by == "key":
        results["index_records"] = search_index_by_key(query)
        results["wiki_pages"] = search_wiki_pages(query, by="key")
        # Also check standards ledger for any matching doc_key
        results["standards_ledger"] = search_standards_ledger(query, by="key")
    elif by == "path":
        results["index_records"] = search_index_by_path(query)
        results["wiki_pages"] = search_wiki_pages(query, by="path")
        results["standards_ledger"] = search_standards_ledger(query, by="path")
    elif by == "standard":
        results["standards_ledger"] = search_standards_ledger(query, by="standard")
        results["wiki_pages"] = search_wiki_pages(query, by="standard")
        # If standards ledger has doc_paths, also search index
        for std in results["standards_ledger"]:
            doc_path = std.get("doc_path", std.get("doc_paths", ""))
            if isinstance(doc_path, list) and doc_path:
                path_results = search_index_by_path(Path(doc_path[0]).name, limit=5)
                results["index_records"].extend(path_results)
            elif isinstance(doc_path, str) and doc_path:
                path_results = search_index_by_path(Path(doc_path).name, limit=5)
                results["index_records"].extend(path_results)

    total = (
        len(results["index_records"])
        + len(results["standards_ledger"])
        + len(results["wiki_pages"])
    )

    if json_output:
        # Simplify index records for JSON output
        for rec in results["index_records"]:
            for key in list(rec.keys()):
                if rec[key] is None:
                    del rec[key]
        print(json.dumps(results, indent=2, default=str))
    else:
        print(f"{'=' * 60}")
        print(f" doc_key Lookup: {query}")
        print(f" Type: {by} | Found: {total} artifact(s)")
        print(f"{'=' * 60}")

        if results["index_records"]:
            print(f"\n## Registry (index.jsonl) — {len(results['index_records'])} record(s)")
            for rec in results["index_records"][:10]:
                path = rec.get("path", "<no path>")
                source = rec.get("source", "?")
                domain = rec.get("domain", "?")
                status = rec.get("status", "?")
                ch = rec.get("content_hash", "?")
                print(f"  {source}/{domain} [{status}] {ch}")
                print(f"    {path}")

        if results["standards_ledger"]:
            print(f"\n## Standards Ledger — {len(results['standards_ledger'])} match(es)")
            for std in results["standards_ledger"][:10]:
                sid = std.get("id", std.get("_key", "?"))
                title = std.get("title", "?")
                org = std.get("org", "?")
                status = std.get("status", "?")
                print(f"  [{org}] {sid}: {title} ({status})")

        if results["wiki_pages"]:
            print(f"\n## Wiki Pages — {len(results['wiki_pages'])} page(s)")
            for page in results["wiki_pages"]:
                print(f"  [{page['domain']}] {page['title']}")
                print(f"    {page['page']}")

        if total == 0:
            print(f"\n  No artifacts found for query: {query}")

        print(f"\n{'=' * 60}")

    return 0 if total > 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="Unified doc_key lookup across the intelligence pyramid (#2207)",
    )
    parser.add_argument("query", help="doc_key hash, path fragment, or standard ID")
    parser.add_argument("--by", "-b", choices=["key", "path", "standard"],
                        default="key", help="Lookup type (default: key)")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output results as JSON")
    args = parser.parse_args()

    # Auto-detect lookup type if not specified and query looks like a path or standard
    if args.by == "key":
        if "/" in args.query or "." in args.query and not args.query.startswith("sha256:"):
            args.by = "path"
        elif re.match(r"^[A-Z]{2,}", args.query):
            args.by = "standard"

    sys.exit(run_lookup(args.query, by=args.by, json_output=args.json))


if __name__ == "__main__":
    main()
