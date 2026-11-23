#!/usr/bin/env bash
# wiki-query-context.sh — Query llm-wiki for agent context
#
# Searches across multiple wiki domains and cross-links JSONL store.
# Returns compact results suitable for agent consumption.
#
# Usage:
#   bash scripts/knowledge/wiki-query-context.sh "mooring line failure"
#   bash scripts/knowledge/wiki-query-context.sh "pipeline corrosion" --domains engineering,marine-engineering
#   bash scripts/knowledge/wiki-query-context.sh "OrcaFlex VIV" --json --limit 5
#
# Issue: #2123
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# ── Defaults ────────────────────────────────────────────────────────────────
QUERY=""
DOMAINS=""
LIMIT=5
JSON_OUTPUT=false

# ── Parse arguments ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --domains)   DOMAINS="$2"; shift 2 ;;
        --limit)     LIMIT="$2"; shift 2 ;;
        --json)      JSON_OUTPUT=true; shift ;;
        --help|-h)
            echo "Usage: wiki-query-context.sh <query> [--domains d1,d2] [--limit N] [--json]"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2; exit 1
            ;;
        *)
            QUERY="$1"; shift
            ;;
    esac
done

if [[ -z "$QUERY" ]]; then
    echo "Error: no query provided" >&2
    echo "Usage: wiki-query-context.sh <query> [--domains d1,d2] [--limit N] [--json]" >&2
    exit 1
fi

# ── Resolve wiki domains ───────────────────────────────────────────────────
WIKIS_DIR="${REPO_ROOT}/knowledge/wikis"
CROSS_LINKS="${WIKIS_DIR}/cross-links.jsonl"

if [[ -n "$DOMAINS" ]]; then
    IFS=',' read -ra DOMAIN_LIST <<< "$DOMAINS"
else
    # Auto-discover domain wikis (skip personal, health-reports)
    DOMAIN_LIST=()
    for d in "${WIKIS_DIR}"/*/; do
        dname="$(basename "$d")"
        [[ "$dname" == "personal" || "$dname" == "health-reports" ]] && continue
        [[ -d "${d}wiki" ]] && DOMAIN_LIST+=("$dname")
    done
fi

# ── Query each wiki domain ─────────────────────────────────────────────────
ALL_RESULTS=()
RESULT_COUNT=0

for domain in "${DOMAIN_LIST[@]}"; do
    wiki_dir="${WIKIS_DIR}/${domain}"
    if [[ ! -d "${wiki_dir}/wiki" ]]; then
        continue
    fi

    # Run llm_wiki.py query and capture output
    query_output=$(cd "${REPO_ROOT}" && uv run scripts/knowledge/llm_wiki.py query "$QUERY" --wiki "$domain" 2>/dev/null) || continue

    # Parse results — each line is a result with format: "  score  path  title"
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        # Skip header/summary lines
        [[ "$line" == *"results for"* ]] && continue
        [[ "$line" == *"Query:"* ]] && continue
        [[ "$line" == *"---"* ]] && continue
        [[ "$line" == *"No results"* ]] && continue

        RESULT_COUNT=$((RESULT_COUNT + 1))
        if [[ $RESULT_COUNT -le $LIMIT ]]; then
            ALL_RESULTS+=("${domain}|${line}")
        fi
    done <<< "$query_output"
done

# ── Check cross-links for entity matches ───────────────────────────────────
CROSS_LINK_MATCHES=()
if [[ -f "$CROSS_LINKS" ]]; then
    # Extract query terms for entity matching
    for term in $QUERY; do
        # Search cross-links JSONL for entity mentions
        matches=$(grep -i "$term" "$CROSS_LINKS" 2>/dev/null | head -3) || true
        if [[ -n "$matches" ]]; then
            while IFS= read -r match; do
                CROSS_LINK_MATCHES+=("$match")
            done <<< "$matches"
        fi
    done
fi

# ── Output results ─────────────────────────────────────────────────────────
if [[ "$JSON_OUTPUT" == "true" ]]; then
    # JSON output for programmatic consumption
    echo "{"
    echo "  \"query\": \"${QUERY}\","
    echo "  \"domains_searched\": [$(printf '"%s",' "${DOMAIN_LIST[@]}" | sed 's/,$//' )],"
    echo "  \"result_count\": ${RESULT_COUNT},"
    echo "  \"results\": ["

    first=true
    for result in "${ALL_RESULTS[@]}"; do
        domain="${result%%|*}"
        detail="${result#*|}"
        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo ","
        fi
        # Escape double quotes in detail
        detail_escaped="${detail//\"/\\\"}"
        printf '    {"domain": "%s", "detail": "%s"}' "$domain" "$detail_escaped"
    done

    echo ""
    echo "  ],"
    echo "  \"cross_link_count\": ${#CROSS_LINK_MATCHES[@]}"
    echo "}"
else
    # Human-readable output
    echo "=== Wiki Context: \"${QUERY}\" ==="
    echo "Domains searched: ${DOMAIN_LIST[*]}"
    echo ""

    if [[ ${#ALL_RESULTS[@]} -eq 0 ]]; then
        echo "No wiki results found."
    else
        echo "── Wiki Results (top ${LIMIT}) ──"
        for result in "${ALL_RESULTS[@]}"; do
            domain="${result%%|*}"
            detail="${result#*|}"
            echo "  [${domain}] ${detail}"
        done
    fi

    if [[ ${#CROSS_LINK_MATCHES[@]} -gt 0 ]]; then
        echo ""
        echo "── Cross-Link Matches ──"
        for match in "${CROSS_LINK_MATCHES[@]}"; do
            # Extract key fields from JSONL
            source=$(echo "$match" | grep -o '"source_page": "[^"]*"' | head -1 | cut -d'"' -f4)
            target=$(echo "$match" | grep -o '"target_page": "[^"]*"' | head -1 | cut -d'"' -f4)
            types=$(echo "$match" | grep -o '"link_types": \[[^]]*\]' | head -1)
            echo "  ${source} <-> ${target} ${types}"
        done
    fi

    echo ""
    echo "Total: ${RESULT_COUNT} wiki result(s), ${#CROSS_LINK_MATCHES[@]} cross-link(s)"
fi
