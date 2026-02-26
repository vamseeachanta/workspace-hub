#!/usr/bin/env bash
# ABOUTME: WRK-328 — Query the agent-readable specs index (specs/index.yaml)
# ABOUTME: Filters by tag, repo, category, WRK reference, or free-text search term.
#
# Usage:
#   query-specs.sh --tag fatigue
#   query-specs.sh --repo digitalmodel
#   query-specs.sh --category modules
#   query-specs.sh --wrk WRK-328
#   query-specs.sh --search "pipeline installation"
#   query-specs.sh --repo worldenergydata --category repos
#   query-specs.sh --stats
#
# Requires: python3, PyYAML

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
INDEX_FILE="$HUB_ROOT/specs/index.yaml"

# Defaults
TAG=""
REPO=""
CATEGORY=""
WRK=""
SEARCH=""
LIMIT=50
FORMAT=table
STATS=false

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Query the agent-readable specs index (specs/index.yaml).

Options:
  --tag TAG          Filter by tag (matches any tag in the tags list)
  --repo REPO        Filter by target repo (digitalmodel, worldenergydata, ...)
  --category CAT     Filter by category (modules, repos, wrk, data-sources, archive, templates)
  --wrk WRK-NNN      Filter by WRK reference (e.g. WRK-328; case-insensitive)
  --search TERM      Free-text search in path, title, and description
  --limit N          Max results (default: 50)
  --format FORMAT    Output format: table|json|paths|yaml (default: table)
  --stats            Show index summary statistics and exit
  -h, --help         Show this help

Categories: modules, repos, wrk, data-sources, archive, templates, other

Examples:
  $(basename "$0") --tag fatigue
  $(basename "$0") --wrk WRK-328
  $(basename "$0") --repo worldenergydata --category repos
  $(basename "$0") --search "pipeline installation"
  $(basename "$0") --category wrk --format paths
  $(basename "$0") --stats
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --tag)      TAG="$2";      shift 2 ;;
        --repo)     REPO="$2";     shift 2 ;;
        --category) CATEGORY="$2"; shift 2 ;;
        --wrk)      WRK="$2";      shift 2 ;;
        --search)   SEARCH="$2";   shift 2 ;;
        --limit)    LIMIT="$2";    shift 2 ;;
        --format)   FORMAT="$2";   shift 2 ;;
        --stats)    STATS=true;    shift ;;
        -h|--help)  usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
    esac
done

# Check for index file
if [[ ! -f "$INDEX_FILE" ]]; then
    echo "ERROR: Specs index not found: $INDEX_FILE" >&2
    echo "Run: python3 scripts/readiness/build-specs-index.py" >&2
    exit 1
fi

python3 - "$INDEX_FILE" "$TAG" "$REPO" "$CATEGORY" "$WRK" "$SEARCH" \
           "$LIMIT" "$FORMAT" "$STATS" <<'PYEOF'
import sys
import yaml

index_file, tag, repo, category, wrk, search, limit, fmt, stats_mode = sys.argv[1:]
limit = int(limit)
stats_mode = stats_mode == "true"

with open(index_file, encoding="utf-8") as f:
    data = yaml.safe_load(f)

if stats_mode:
    print(f"Specs index — generated: {data.get('generated', 'unknown')}")
    print(f"Total specs: {data.get('total_specs', '?')}")
    print()
    print("By category:")
    for cat, cnt in sorted(data.get("by_category", {}).items()):
        print(f"  {cat:<16} {cnt:>5}")
    print()
    print("By repo:")
    for r, cnt in sorted(data.get("by_repo", {}).items()):
        print(f"  {r:<30} {cnt:>5}")
    by_wrk = data.get("by_wrk", {})
    if by_wrk:
        print()
        print("Top WRK references (specs per WRK):")
        top = sorted(by_wrk.items(), key=lambda kv: -kv[1])[:20]
        for w, cnt in top:
            print(f"  {w:<12} {cnt:>4}")
    sys.exit(0)

results = []
for rec in data.get("specs", []):
    # Apply filters
    if tag:
        rec_tags = [t.lower() for t in (rec.get("tags") or [])]
        if tag.lower() not in rec_tags:
            continue
    if repo and rec.get("repo", "").lower() != repo.lower():
        continue
    if category and rec.get("category", "").lower() != category.lower():
        continue
    if wrk:
        rec_wrks = [w.upper() for w in (rec.get("wrk_refs") or [])]
        if wrk.upper() not in rec_wrks:
            continue
    if search:
        needle = search.lower()
        haystack = " ".join([
            rec.get("path", ""),
            rec.get("title", "") or "",
            rec.get("description", "") or "",
        ]).lower()
        if needle not in haystack:
            continue
    results.append(rec)
    if len(results) >= limit:
        break

if fmt == "json":
    import json
    print(json.dumps(results, indent=2))
elif fmt == "paths":
    for r in results:
        print(r.get("path", ""))
elif fmt == "yaml":
    import yaml as _yaml
    print(_yaml.dump(results, default_flow_style=False, allow_unicode=True, sort_keys=False))
else:
    # Table format
    print(f"{'CATEGORY':<12} {'REPO':<22} {'TITLE':<45} {'PATH'}")
    print("-" * 120)
    for r in results:
        title = (r.get("title") or "")[:43]
        path = r.get("path", "")
        if len(path) > 55:
            path = "..." + path[-52:]
        repo_s = (r.get("repo") or "")[:20]
        cat = (r.get("category") or "")[:10]
        print(f"{cat:<12} {repo_s:<22} {title:<45} {path}")
    print(f"\n{len(results)} result(s) (limit={limit})")
PYEOF
