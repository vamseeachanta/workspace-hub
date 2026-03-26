#!/usr/bin/env bash
#
# Skill Graph Lookup — domain/capability routing from the skills knowledge graph
# Usage:
#   skill_graph.sh --domain <domain>              List skills in a domain
#   skill_graph.sh --capability "<query>"          Fuzzy-match capabilities
#   skill_graph.sh --edges-from <skill-id>          What skills consume this skill's output
#   skill_graph.sh --edges-to <skill-id>            What skills feed into this skill
#   skill_graph.sh --rebuild-index                 Regenerate skill-graph-index.yaml
#
# Version: 1.0.0
#

set -euo pipefail

# --- Resolve paths ---
_SG_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_SG_REPO_ROOT="$(cd "$_SG_SCRIPT_DIR/../../../.." && pwd)"
_SG_GRAPH_FILE="${SKILL_GRAPH_FILE:-$_SG_REPO_ROOT/.planning/skills/skills-knowledge-graph.yaml}"
_SG_INDEX_FILE="${SKILL_GRAPH_INDEX:-$_SG_REPO_ROOT/config/agents/skill-graph-index.yaml}"

# --- Helpers ---

_sg_check_graph() {
    if [[ ! -f "$_SG_GRAPH_FILE" ]]; then
        echo "Error: Skills knowledge graph not found at $_SG_GRAPH_FILE" >&2
        return 1
    fi
}

# Extract all skill IDs belonging to a domain from the nodes section.
# Parses the YAML by tracking current node id and domain fields.
_sg_skills_by_domain() {
    local target_domain="$1"
    _sg_check_graph || return 1

    awk -v domain="$target_domain" '
    /^nodes:/ { in_nodes = 1; next }
    in_nodes && /^[a-z]/ { in_nodes = 0 }
    in_nodes && /^  - id:/ {
        id = $3
        gsub(/"/, "", id)
        current_id = id
        current_domain = ""
        next
    }
    in_nodes && /^    domain:/ {
        d = $2
        gsub(/"/, "", d)
        current_domain = d
        if (current_domain == domain && current_id != "") {
            print current_id
        }
    }
    ' "$_SG_GRAPH_FILE"
}

# Fuzzy-match capabilities: case-insensitive grep across capability lines,
# returning the skill ID that owns each matching capability.
_sg_skills_by_capability() {
    local query="$1"
    _sg_check_graph || return 1

    awk -v query="$query" '
    /^nodes:/ { in_nodes = 1; next }
    in_nodes && /^[a-z]/ { in_nodes = 0 }
    in_nodes && /^  - id:/ {
        id = $3
        gsub(/"/, "", id)
        current_id = id
        in_caps = 0
        next
    }
    in_nodes && /^    capabilities:/ { in_caps = 1; next }
    in_nodes && in_caps && /^      - "/ {
        cap = $0
        sub(/^[ \t]*- "/, "", cap)
        sub(/"[ \t]*$/, "", cap)
        if (index(tolower(cap), tolower(query)) > 0) {
            print current_id "\t" cap
        }
        next
    }
    in_nodes && in_caps && !/^      / { in_caps = 0 }
    ' "$_SG_GRAPH_FILE"
}

# Find edges where a given skill is the source (i.e. feeds downstream).
# Returns: target_id \t edge_type \t note
_sg_feeds_from() {
    local skill_id="$1"
    _sg_check_graph || return 1

    awk -v sid="$skill_id" '
    function flush_edge() {
        if (current_from == sid && current_to != "") {
            print current_to "\t" current_type "\t" current_note
        }
    }
    /^edges:/ { in_edges = 1; next }
    in_edges && /^[a-z]/ { flush_edge(); in_edges = 0 }
    in_edges && /^  - from:/ {
        flush_edge()
        f = $3; gsub(/"/, "", f)
        current_from = f
        current_to = ""; current_type = ""; current_note = ""
        next
    }
    in_edges && /^    to:/ {
        t = $2; gsub(/"/, "", t)
        current_to = t
    }
    in_edges && /^    type:/ {
        current_type = $2
    }
    in_edges && /^    note:/ {
        n = $0; sub(/^[ \t]*note: *"?/, "", n); sub(/"? *$/, "", n)
        current_note = n
    }
    END { if (in_edges) flush_edge() }
    ' "$_SG_GRAPH_FILE"
}

# Find edges where a given skill is the target (i.e. receives input from upstream).
# Returns: source_id \t edge_type \t note
_sg_feeds_to() {
    local skill_id="$1"
    _sg_check_graph || return 1

    awk -v sid="$skill_id" '
    function flush_edge() {
        if (current_to == sid && current_from != "") {
            print current_from "\t" current_type "\t" current_note
        }
    }
    /^edges:/ { in_edges = 1; next }
    in_edges && /^[a-z]/ { flush_edge(); in_edges = 0 }
    in_edges && /^  - from:/ {
        flush_edge()
        f = $3; gsub(/"/, "", f)
        current_from = f
        current_to = ""; current_type = ""; current_note = ""
        next
    }
    in_edges && /^    to:/ {
        t = $2; gsub(/"/, "", t)
        current_to = t
    }
    in_edges && /^    type:/ {
        current_type = $2
    }
    in_edges && /^    note:/ {
        n = $0; sub(/^[ \t]*note: *"?/, "", n); sub(/"? *$/, "", n)
        current_note = n
    }
    END { if (in_edges) flush_edge() }
    ' "$_SG_GRAPH_FILE"
}

# --- Rebuild index ---
# Generates config/agents/skill-graph-index.yaml from the knowledge graph
_sg_rebuild_index() {
    _sg_check_graph || return 1

    local out="$_SG_INDEX_FILE"
    mkdir -p "$(dirname "$out")"

    {
        echo "# Pre-computed index from .planning/skills/skills-knowledge-graph.yaml"
        echo "# Regenerate: scripts/coordination/routing/lib/skill_graph.sh --rebuild-index"
        echo "generated_at: \"$(date -u +%Y-%m-%d)\""
        echo "source: .planning/skills/skills-knowledge-graph.yaml"
        echo ""

        # --- by_domain ---
        # Emit "domain|skill_id" pairs, sort, then format as YAML
        echo "by_domain:"
        awk '
        /^nodes:/ { in_nodes = 1; next }
        in_nodes && /^[a-z]/ { in_nodes = 0 }
        in_nodes && /^  - id:/ {
            id = $3; gsub(/"/, "", id); current_id = id; next
        }
        in_nodes && /^    domain:/ {
            d = $2; gsub(/"/, "", d)
            print d "|" current_id
        }
        ' "$_SG_GRAPH_FILE" | sort | awk -F'|' '
        {
            if ($1 != prev) {
                print "  " $1 ":"
                prev = $1
            }
            print "    - " $2
        }'
        echo ""

        # --- by_input_type ---
        echo "by_input_type:"
        awk '
        /^nodes:/ { in_nodes = 1; next }
        in_nodes && /^[a-z]/ { in_nodes = 0 }
        in_nodes && /^  - id:/ {
            id = $3; gsub(/"/, "", id); current_id = id; next
        }
        in_nodes && /^    input_types:/ {
            line = $0
            sub(/.*\[/, "", line); sub(/\].*/, "", line)
            gsub(/ /, "", line)
            n = split(line, types, ",")
            for (i = 1; i <= n; i++) {
                if (types[i] != "") print types[i] "|" current_id
            }
        }
        ' "$_SG_GRAPH_FILE" | sort | awk -F'|' '
        {
            if ($1 != prev) {
                print "  " $1 ":"
                prev = $1
            }
            print "    - " $2
        }'
        echo ""

        # --- by_output_type ---
        echo "by_output_type:"
        awk '
        /^nodes:/ { in_nodes = 1; next }
        in_nodes && /^[a-z]/ { in_nodes = 0 }
        in_nodes && /^  - id:/ {
            id = $3; gsub(/"/, "", id); current_id = id; next
        }
        in_nodes && /^    output_types:/ {
            line = $0
            sub(/.*\[/, "", line); sub(/\].*/, "", line)
            gsub(/ /, "", line)
            n = split(line, types, ",")
            for (i = 1; i <= n; i++) {
                if (types[i] != "") print types[i] "|" current_id
            }
        }
        ' "$_SG_GRAPH_FILE" | sort | awk -F'|' '
        {
            if ($1 != prev) {
                print "  " $1 ":"
                prev = $1
            }
            print "    - " $2
        }'
        echo ""

        # --- feed_chains ---
        # Pre-compute multi-hop feed chains (A feeds B feeds C)
        echo "feed_chains:"
        awk '
        /^edges:/ { in_edges = 1; next }
        in_edges && /^[a-z]/ { in_edges = 0 }
        in_edges && /^  - from:/ {
            f = $3; gsub(/"/, "", f); current_from = f; next
        }
        in_edges && /^    to:/ {
            t = $2; gsub(/"/, "", t); current_to = t; next
        }
        in_edges && /^    type:/ {
            tp = $2
            if (tp == "feeds") {
                # Store edge: from -> to
                edge_count++
                from_arr[edge_count] = current_from
                to_arr[edge_count] = current_to
                # Track outgoing edges for chain building
                if (out[current_from] == "")
                    out[current_from] = current_to
                else
                    out[current_from] = out[current_from] "|" current_to
            }
        }
        END {
            # Build chains: for each edge A->B, if B->C exists, emit [A, B, C]
            seen_chains = 0
            for (i = 1; i <= edge_count; i++) {
                a = from_arr[i]
                b = to_arr[i]
                # Check if b has outgoing feeds edges
                if (out[b] != "") {
                    n = split(out[b], targets, "|")
                    for (j = 1; j <= n; j++) {
                        c = targets[j]
                        chain = a "|" b "|" c
                        if (!(chain in printed)) {
                            print "  - [" a ", " b ", " c "]"
                            printed[chain] = 1
                            seen_chains++
                        }
                    }
                }
            }
            # Also emit length-2 chains that are not part of longer chains
            for (i = 1; i <= edge_count; i++) {
                a = from_arr[i]
                b = to_arr[i]
                pair = a "|" b
                # Check if this pair is already the start of a 3-chain
                is_start = 0
                for (c in printed) {
                    if (index(c, pair "|") == 1) { is_start = 1; break }
                }
                # Check if this pair is the end of a 3-chain
                is_end = 0
                for (c in printed) {
                    if (index(c, "|" pair) > 0) { is_end = 1; break }
                }
                if (!is_start && !is_end) {
                    print "  - [" a ", " b "]"
                }
            }
        }
        ' "$_SG_GRAPH_FILE"
    } > "$out"

    echo "Index rebuilt: $out" >&2
}

# --- CLI entry point ---
# When sourced as a library, functions are available directly.
# When run as a script, parse arguments and dispatch.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -eq 0 ]]; then
        sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'
        exit 0
    fi

    case "$1" in
        --domain)
            [[ -z "${2:-}" ]] && { echo "Error: --domain requires a domain name" >&2; exit 1; }
            _sg_skills_by_domain "$2"
            ;;
        --capability)
            [[ -z "${2:-}" ]] && { echo "Error: --capability requires a search query" >&2; exit 1; }
            _sg_skills_by_capability "$2"
            ;;
        --edges-from|--feeds-from)
            [[ -z "${2:-}" ]] && { echo "Error: --edges-from requires a skill ID" >&2; exit 1; }
            _sg_feeds_from "$2"
            ;;
        --edges-to|--feeds-to)
            [[ -z "${2:-}" ]] && { echo "Error: --edges-to requires a skill ID" >&2; exit 1; }
            _sg_feeds_to "$2"
            ;;
        --rebuild-index)
            _sg_rebuild_index
            ;;
        -h|--help)
            sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'
            ;;
        *)
            echo "Error: Unknown option $1" >&2
            sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'
            exit 1
            ;;
    esac
fi
