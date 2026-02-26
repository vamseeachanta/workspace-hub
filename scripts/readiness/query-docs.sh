#!/usr/bin/env bash
# ABOUTME: Query the document intelligence index for standards and references
# ABOUTME: Filters by domain, repo, source type, or free-text keyword
#
# Usage:
#   query-docs.sh --domain cp
#   query-docs.sh --repo digitalmodel
#   query-docs.sh --domain structural --repo digitalmodel
#   query-docs.sh --keyword "fatigue S-N"
#   query-docs.sh --source og_standards
#   query-docs.sh --status gap
#
# Requires: jq, python3

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
INDEX_FILE="$HUB_ROOT/data/document-index/index.jsonl"
REGISTRY_FILE="$HUB_ROOT/data/document-index/registry.yaml"

# Defaults
DOMAIN=""
REPO=""
SOURCE=""
KEYWORD=""
STATUS=""
LIMIT=50
FORMAT=table

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Query the document intelligence index.

Options:
  --domain DOMAIN      Filter by engineering domain (cp, structural, pipeline, ...)
  --repo REPO          Filter by target repo (digitalmodel, worldenergydata, ...)
  --source SOURCE      Filter by source type (og_standards, ace_project, dde_project, ...)
  --keyword KEYWORD    Full-text keyword search in path/title
  --status STATUS      Filter by status (implemented, gap, data_source, reference)
  --limit N            Max results (default: 50)
  --format FORMAT      Output format: table|json|paths (default: table)
  -h, --help           Show this help

Examples:
  $(basename "$0") --domain cp --repo digitalmodel
  $(basename "$0") --source og_standards --keyword "DNV"
  $(basename "$0") --status gap --repo digitalmodel
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --domain) DOMAIN="$2"; shift 2 ;;
        --repo) REPO="$2"; shift 2 ;;
        --source) SOURCE="$2"; shift 2 ;;
        --keyword) KEYWORD="$2"; shift 2 ;;
        --status) STATUS="$2"; shift 2 ;;
        --limit) LIMIT="$2"; shift 2 ;;
        --format) FORMAT="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Check for index
if [[ ! -f "$INDEX_FILE" ]]; then
    echo "ERROR: Index not found: $INDEX_FILE" >&2
    echo "Run Phase A first: python3 scripts/data/document-index/phase-a-index.py" >&2
    exit 1
fi

# Use Python for filtering (jq alone doesn't handle JSONL domain arrays well)
python3 - "$INDEX_FILE" "$DOMAIN" "$REPO" "$SOURCE" "$KEYWORD" "$STATUS" "$LIMIT" "$FORMAT" <<'PYEOF'
import sys
import json

index_file, domain, repo, source, keyword, status, limit, fmt = sys.argv[1:]
limit = int(limit)

results = []
with open(index_file) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Apply filters
        if domain and rec.get("domain") != domain:
            continue
        if repo and repo not in (rec.get("target_repos") or []):
            continue
        if source and rec.get("source") != source:
            continue
        if status and rec.get("status") != status:
            continue
        if keyword:
            kw = keyword.lower()
            searchable = " ".join([
                str(rec.get("path", "")),
                str(rec.get("org", "")),
                str(rec.get("doc_number", "")),
                str(rec.get("title", "") or ""),
            ]).lower()
            if kw not in searchable:
                continue

        results.append(rec)
        if len(results) >= limit:
            break

if fmt == "json":
    print(json.dumps(results, indent=2))
elif fmt == "paths":
    for r in results:
        print(r.get("path", ""))
else:
    # Table format
    print(f"{'SOURCE':<14} {'EXT':<5} {'SIZE_MB':<8} {'PATH'}")
    print("-" * 90)
    for r in results:
        path = r.get("path", "")
        # Truncate long paths
        if len(path) > 60:
            path = "..." + path[-57:]
        print(
            f"{r.get('source',''):<14} "
            f"{r.get('ext',''):<5} "
            f"{r.get('size_mb', 0):<8.1f} "
            f"{path}"
        )
    print(f"\n{len(results)} result(s) (limit={limit})")
PYEOF
