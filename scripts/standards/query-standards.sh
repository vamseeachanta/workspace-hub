#!/usr/bin/env bash
# query-standards.sh — Search engineering standards by natural-language query
# Usage: query-standards.sh "query" [--code DNV|API|ABS|BS|ISO] [--topic CP|fatigue|...] [--limit N]
# Returns: Ranked standard sections with doc name + page number citations
# Requires: data/standards-index/bm25.pkl (run ingest_standards.py ingest + build-index first)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
INDEX_DIR="${REPO_ROOT}/data/standards-index"

QUERY=""
CODE=""
TOPIC=""
LIMIT=10

while [[ $# -gt 0 ]]; do
    case "$1" in
        --code)    CODE="$2";    shift 2 ;;
        --topic)   TOPIC="$2";   shift 2 ;;
        --limit)   LIMIT="$2";   shift 2 ;;
        --index)   INDEX_DIR="$2"; shift 2 ;;
        -*)        echo "Unknown flag: $1" >&2; exit 1 ;;
        *)         QUERY="$1";   shift ;;
    esac
done

if [[ -z "$QUERY" && -z "$TOPIC" ]]; then
    echo "Usage: query-standards.sh \"query\" [--code DNV|API|ABS|BS|ISO] [--topic TOPIC] [--limit N]" >&2
    exit 1
fi

# Combine query + topic if both provided
FULL_QUERY="${QUERY}"
if [[ -n "$TOPIC" ]]; then
    FULL_QUERY="${FULL_QUERY} ${TOPIC}"
fi

uv run --no-project --with pymupdf --with rank_bm25 python3 - <<PYEOF
import sys
sys.path.insert(0, "${REPO_ROOT}")
from scripts.standards.ingest_standards import query_standards

query = "${FULL_QUERY}".strip()
code = "${CODE}" or None
limit = ${LIMIT}
index_dir = "${INDEX_DIR}"

results = query_standards(query, index_dir, code_family=code, limit=limit)

if not results:
    print("No results found.")
    if code:
        print(f"(Filtered to code family: {code})")
    sys.exit(0)

print(f"\n## Standards Search: '{query}'" + (f" [code: {code}]" if code else "") + "\n")
for i, r in enumerate(results, 1):
    doc = r["doc_name"]
    page = r["page"]
    family = r.get("code_family", "")
    snippet = r["text"][:200].replace("\n", " ").strip()
    print(f"{i}. **{doc}** (p.{page}) [{family}]")
    print(f"   > {snippet}...")
    print()
PYEOF
