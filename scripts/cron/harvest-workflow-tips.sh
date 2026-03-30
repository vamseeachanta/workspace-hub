#!/usr/bin/env bash
# ABOUTME: Harvest workflow tip candidates from Wednesday ai-tooling research output
# ABOUTME: Scans .planning/research/ for ai-tooling reports, extracts feature mentions
# Usage: bash harvest-workflow-tips.sh <WORKSPACE_ROOT>
# Called from comprehensive-learning-nightly.sh on Wednesdays only

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
RESEARCH_DIR="$WORKSPACE_ROOT/.planning/research"
CANDIDATES="$WORKSPACE_ROOT/config/workflow-tips/candidates.yaml"
CATALOG="$WORKSPACE_ROOT/config/workflow-tips/tips-catalog.yaml"
TODAY=$(date +%Y-%m-%d)

[[ -t 1 ]] && GREEN='\033[0;32m' NC='\033[0m' || GREEN='' NC=''
log() { echo -e "${GREEN}[harvest-tips]${NC} $*"; }

# Find today's or most recent ai-tooling research file
research_file=""
for f in "$RESEARCH_DIR/$TODAY-ai-tooling.md" \
         "$RESEARCH_DIR"/????-??-??-ai-tooling.md; do
    if [[ -f "$f" ]]; then
        research_file="$f"
    fi
done

if [[ -z "$research_file" || ! -f "$research_file" ]]; then
    log "No ai-tooling research file found — skipping"
    exit 0
fi

research_date=$(basename "$research_file" | grep -oP '^\d{4}-\d{2}-\d{2}')
log "Scanning: $research_file"

# Extract lines mentioning features, commands, flags
features=$(grep -iE '(slash command|/[a-z]+|--[a-z]+|new feature|CLI flag|claude code|hidden|under.?utiliz)' \
    "$research_file" 2>/dev/null | head -20 || true)

if [[ -z "$features" ]]; then
    log "No feature mentions found — skipping"
    exit 0
fi

# Check which are already in catalog or candidates
existing=""
[[ -f "$CATALOG" ]] && existing=$(grep "oneliner:" "$CATALOG" | tr '[:upper:]' '[:lower:]')
[[ -f "$CANDIDATES" ]] && existing="$existing $(grep "oneliner:" "$CANDIDATES" 2>/dev/null | tr '[:upper:]' '[:lower:]')"

# Ensure candidates file exists
if [[ ! -f "$CANDIDATES" ]]; then
    cat > "$CANDIDATES" <<'EOF'
# ABOUTME: Auto-populated by harvest-workflow-tips.sh from Wednesday ai-tooling research
# ABOUTME: Review and promote worthy entries to tips-catalog.yaml manually
candidates: []
EOF
fi

added=0
while IFS= read -r line; do
    # Skip empty lines and headers
    [[ -z "$line" || "$line" =~ ^# ]] && continue

    # Clean up the line for use as a oneliner
    clean="${line#- }"
    clean="${clean#* }"
    clean_lower=$(echo "$clean" | tr '[:upper:]' '[:lower:]')

    # Skip if already known (fuzzy: check first 40 chars)
    check="${clean_lower:0:40}"
    [[ "$existing" == *"$check"* ]] && continue

    # Append to candidates
    if grep -q "^candidates: \[\]" "$CANDIDATES"; then
        sed -i "s/^candidates: \[\]/candidates:/" "$CANDIDATES"
    fi

    cat >> "$CANDIDATES" <<EOF
  - name: "$(echo "$clean" | head -c 60)"
    oneliner: "$clean"
    source: "ai-tooling research $research_date"
    discovered: $TODAY
EOF
    added=$((added + 1))
done <<< "$features"

log "Added $added candidate(s) to $CANDIDATES"
