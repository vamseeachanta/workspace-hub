#!/usr/bin/env bash
set -euo pipefail
# assign-providers.sh — Apply provider assignments to pending WRK items.
#
# Usage:
#   ./scripts/work-queue/assign-providers.sh               # apply assignments
#   ./scripts/work-queue/assign-providers.sh --list         # list pending items
#   ./scripts/work-queue/assign-providers.sh --verify       # verify all assigned
#
# Assignments are defined inline in the ASSIGNMENTS array below.
# Format: "WRK-NNN:provider[:provider_alt]"

QUEUE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/.claude/work-queue"
PENDING_DIR="$QUEUE_DIR/pending"

# ── Provider Assignments ─────────────────────────────────────────────
# Decided during planning based on task requirements and provider strengths:
#   codex  = focused code tasks, single-file, bug fixes, refactoring
#   gemini = research, data analysis, summarization, large documents
#   claude = orchestration, architecture, multi-file, sensitive (fallback)

ASSIGNMENTS=(
    # Personal/sensitive → claude
    "WRK-005:claude"        # Email cleanup — personal data
    "WRK-008:claude"        # Photo upload — personal, device access
    "WRK-133:claude"        # License agreement — legal/admin
    "WRK-141:claude"        # Family tree — personal/sensitive
    # Complex architecture / multi-repo → claude
    "WRK-015:claude"        # Metocean extrapolation — GIS + modeling
    "WRK-018:claude"        # BSEE to other regulators — multi-source arch
    "WRK-019:claude:gemini" # Cost data layer — architecture + research
    "WRK-020:claude"        # GIS skill — cross-application arch
    "WRK-023:claude"        # Property GIS timeline — multi-tool
    "WRK-031:claude"        # OrcaWave vs AQWA benchmark — complex analysis
    "WRK-036:claude"        # OrcaFlex deployment — complex analysis
    "WRK-039:claude"        # SPM benchmarking — complex analysis
    "WRK-043:claude"        # Parametric hull analysis — core engineering
    "WRK-045:claude"        # OrcaFlex rigid jumper — complex analysis
    "WRK-046:claude"        # OrcaFlex drilling riser — complex analysis
    "WRK-047:claude"        # OpenFOAM CFD — new capability
    "WRK-050:claude"        # Hardware consolidation — infrastructure
    "WRK-075:claude"        # OFFPIPE integration — new module
    "WRK-084:claude"        # Metocean aggregation — multi-source arch
    "WRK-099:claude"        # 3-way benchmark — analysis + debugging
    "WRK-106:claude"        # Hull panel geometry — core architecture
    "WRK-111:claude"        # BSEE interactive map — multi-repo, complex
    "WRK-126:claude"        # Benchmark all models — complex analysis
    "WRK-131:claude"        # Passing ship analysis — complex analysis
    "WRK-146:claude:gemini" # Website overhaul — strategy + content
    "WRK-147:claude"        # Strategy repo — strategy/sensitive
    "WRK-148:claude"        # GTM strategy — strategy/sensitive
    # Focused code / refactoring / config → codex
    "WRK-032:codex"         # Modular OrcaFlex pipeline — refactoring
    "WRK-048:codex"         # Blender configs — setup/config
    "WRK-064:codex"         # OrcaFlex converter — testing, single module
    "WRK-076:codex"         # Data scheduler — infrastructure code
    "WRK-081:codex"         # NPV calculator — follows existing pattern
    "WRK-085:codex"         # Sample data page — single page
    "WRK-101:codex"         # Mesh decimation — algorithm, single module
    "WRK-129:codex"         # Reporting OrcaFlex — templating
    "WRK-130:codex"         # Reporting OrcaWave — templating
    "WRK-132:codex:claude"  # OrcaWave benchmarks — code + domain
    "WRK-140:codex"         # gmsh integration — integration/config
    # Research / data / documents → gemini
    "WRK-021:gemini"        # Stock analysis — research/data
    "WRK-022:gemini"        # Property valuation — research/data
    "WRK-038:gemini"        # LNG terminal dataset — data compilation
    "WRK-041:gemini"        # Hobbies plan — planning/summarization
    "WRK-042:gemini"        # Investments plan — planning/summarization
    "WRK-080:gemini"        # Blog posts — writing/research
    "WRK-112:gemini"        # Appliance lifecycle — research/data
    "WRK-137:gemini"        # Rig spec PDFs — document processing
)

# ── Functions ─────────────────────────────────────────────────────────

list_pending() {
    echo "=== Pending Work Items ==="
    echo ""
    printf "%-10s %-60s %-10s %-10s\n" "ID" "Title" "Provider" "Alt"
    printf "%-10s %-60s %-10s %-10s\n" "----" "----" "----" "----"
    for f in "$PENDING_DIR"/WRK-*.md; do
        [[ -f "$f" ]] || continue
        local id title provider provider_alt
        id=$(basename "$f" .md)
        title=$(awk '/^---$/{if(++c==2)exit} c==1 && /^title:/{sub(/^title:[[:space:]]*/,"");print}' "$f")
        provider=$(awk '/^---$/{if(++c==2)exit} c==1 && /^provider:/{sub(/^provider:[[:space:]]*/,"");print}' "$f")
        provider_alt=$(awk '/^---$/{if(++c==2)exit} c==1 && /^provider_alt:/{sub(/^provider_alt:[[:space:]]*/,"");print}' "$f")
        printf "%-10s %-60s %-10s %-10s\n" "$id" "${title:0:60}" "${provider:--}" "${provider_alt:--}"
    done
}

apply_assignments() {
    local applied=0 skipped=0 missing=0
    for entry in "${ASSIGNMENTS[@]}"; do
        IFS=: read -r wrk_id provider provider_alt <<< "$entry"
        local file="$PENDING_DIR/${wrk_id}.md"
        if [[ ! -f "$file" ]]; then
            echo "SKIP: $wrk_id — file not found in pending/"
            ((missing++)) || true
            continue
        fi
        # Insert provider fields into frontmatter
        if grep -q "^provider:" "$file"; then
            # Update existing provider field
            sed -i "s/^provider:.*$/provider: ${provider}/" "$file"
        elif grep -q "^brochure_status:" "$file"; then
            # Insert after brochure_status
            sed -i "/^brochure_status:/a provider: ${provider}" "$file"
        else
            # No brochure_status — insert before closing ---
            # Use awk to insert before the second --- line
            awk -v prov="provider: ${provider}" '
                /^---$/ { count++ }
                count == 2 && !done { print prov; done=1 }
                { print }
            ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
        fi
        if [[ -n "${provider_alt:-}" ]]; then
            if grep -q "^provider_alt:" "$file"; then
                sed -i "s/^provider_alt:.*$/provider_alt: ${provider_alt}/" "$file"
            else
                sed -i "/^provider:/a provider_alt: ${provider_alt}" "$file"
            fi
        fi
        echo "  $wrk_id → provider: $provider${provider_alt:+, alt: $provider_alt}"
        ((applied++)) || true
    done
    echo ""
    echo "Applied: $applied | Skipped/missing: $missing"
}

verify_assignments() {
    echo "=== Verification ==="
    local ok=0 missing=0
    for f in "$PENDING_DIR"/WRK-*.md; do
        [[ -f "$f" ]] || continue
        local id provider
        id=$(basename "$f" .md)
        provider=$(awk '/^---$/{if(++c==2)exit} c==1 && /^provider:/{sub(/^provider:[[:space:]]*/,"");print}' "$f")
        if [[ -z "$provider" ]]; then
            echo "MISSING: $id has no provider"
            ((missing++)) || true
        else
            ((ok++)) || true
        fi
    done
    echo ""
    echo "Assigned: $ok | Missing: $missing"
    [[ $missing -eq 0 ]] && echo "All pending items have providers assigned."
    return $missing
}

# ── Main ──────────────────────────────────────────────────────────────

case "${1:-apply}" in
    --list)   list_pending ;;
    --verify) verify_assignments ;;
    *)        apply_assignments ;;
esac
