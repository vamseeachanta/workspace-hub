#!/usr/bin/env bash
# create-skills.sh - Auto-skill creation from patterns
# Part of RAGS loop: STORE phase with action
#
# Scoring formula (total = 100%):
#   - Git frequency: 22.5%
#   - Cross-repo spread: 22.5%
#   - Complexity: 15%
#   - Time savings: 15%
#   - Workflow patterns: 25% (from session tool sequences)

set -euo pipefail

# Auto-detect workspace root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
# Path: .claude/skills/coordination/workspace/claude-reflect/scripts - go up 6 levels
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(dirname "$(dirname "$(dirname "$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")")")")}"
# Fallback detection
if [[ ! -d "${WORKSPACE_ROOT}/.claude" ]]; then
    [[ -d "/mnt/github/workspace-hub" ]] && WORKSPACE_ROOT="/mnt/github/workspace-hub"
    [[ -d "/d/workspace-hub" ]] && WORKSPACE_ROOT="/d/workspace-hub"
fi

# State directory: prefer workspace-hub, fallback to home
if [[ -d "${WORKSPACE_ROOT}/.claude/state" ]]; then
    STATE_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_ROOT}/.claude/state}"
else
    STATE_DIR="${WORKSPACE_STATE_DIR:-${HOME}/.claude/state}"
fi

PATTERNS_DIR="${STATE_DIR}/patterns"
SKILLS_BASE="${SKILLS_BASE:-${WORKSPACE_ROOT}/.claude/skills}"
SKILLS_OUTPUT="${SKILLS_BASE}/workspace-hub/auto-generated"
MEMORY_DIR="${STATE_DIR}/memory/patterns"

mkdir -p "$SKILLS_OUTPUT" "$MEMORY_DIR"

# Scoring thresholds
THRESHOLD_CREATE=0.8    # Create new skill
THRESHOLD_ENHANCE=0.6   # Enhance existing
DRY_RUN="${DRY_RUN:-false}"

# Get latest pattern file
PATTERN_FILE="${1:-$(ls -t "$PATTERNS_DIR"/patterns_*.json 2>/dev/null | head -1)}"

# Optional second argument: session analysis file with skill_worthy_patterns
# Auto-detect latest session file if not provided
SESSION_FILE="${2:-$(ls -t "$PATTERNS_DIR"/sessions_*.json 2>/dev/null | head -1)}"

if [[ ! -f "$PATTERN_FILE" ]]; then
    echo "Error: No pattern file found" >&2
    exit 1
fi

echo "Processing patterns from: $PATTERN_FILE"
if [[ -n "$SESSION_FILE" && -f "$SESSION_FILE" ]]; then
    echo "Session workflows from: $SESSION_FILE"
    SESSION_ENABLED=true
else
    echo "No session file found, workflow pattern scoring disabled"
    SESSION_ENABLED=false
fi
echo "Dry run: $DRY_RUN"
echo ""

# Load skill_worthy_patterns from session file into associative array
# Format from analyze-sessions.sh: {sequence: "Read -> Edit", count: 5, skill_potential: "high"|"medium"|"low"}
declare -A SESSION_SKILL_PATTERNS
SESSION_PATTERNS_LOADED=0
if [[ "$SESSION_ENABLED" == "true" ]] && command -v jq &> /dev/null; then
    while IFS='|' read -r sequence count potential; do
        [[ -z "$sequence" ]] && continue
        # Store count and skill_potential for scoring
        SESSION_SKILL_PATTERNS["$sequence"]="${count}|${potential}"
        ((SESSION_PATTERNS_LOADED++)) || true
    done < <(jq -r '.skill_worthy_patterns[]? | "\(.sequence)|\(.count)|\(.skill_potential)"' "$SESSION_FILE" 2>/dev/null)
    if [[ $SESSION_PATTERNS_LOADED -gt 0 ]]; then
        echo "Loaded $SESSION_PATTERNS_LOADED workflow patterns from session analysis"
        echo ""
    fi
fi

# Score a workflow pattern (0.0 - 1.0)
# Based on: sequence frequency, skill_potential rating (high/medium/low)
score_workflow_pattern() {
    local sequence="$1"
    local count="${2:-0}"
    local potential="${3:-low}"

    # Validate count
    [[ ! "$count" =~ ^[0-9]+$ ]] && count=0

    # Frequency score (based on occurrence count)
    local freq_score
    if (( count >= 10 )); then
        freq_score="1.00"
    elif (( count >= 5 )); then
        freq_score="0.80"
    elif (( count >= 3 )); then
        freq_score="0.60"
    elif (( count > 0 )); then
        freq_score=$(echo "scale=2; $count / 5" | bc)
    else
        freq_score="0.00"
    fi

    # Skill potential score (high/medium/low from analyze-sessions.sh)
    local potential_score
    case "$potential" in
        high)   potential_score="1.00" ;;
        medium) potential_score="0.60" ;;
        low)    potential_score="0.30" ;;
        *)      potential_score="0.30" ;;
    esac

    # Weighted workflow score: 60% frequency, 40% potential
    local workflow_score
    workflow_score=$(echo "scale=2; ($freq_score * 0.6) + ($potential_score * 0.4)" | bc 2>/dev/null)
    [[ -z "$workflow_score" || ! "$workflow_score" =~ ^[0-9.]+$ ]] && workflow_score="0.00"

    echo "$workflow_score"
}

# Score a pattern (0.0 - 1.0)
# Weights: freq=22.5%, repo=22.5%, complexity=15%, savings=15%, workflow=25% (total=100%)
score_pattern() {
    local repos="${1:-0}"
    local count="${2:-0}"
    local message="${3:-}"

    # Validate and sanitize numeric inputs (default to 0 if invalid)
    [[ ! "$repos" =~ ^[0-9]+$ ]] && repos=0
    [[ ! "$count" =~ ^[0-9]+$ ]] && count=0

    # Frequency score (based on occurrence count)
    local freq_score
    if (( count > 10 )); then
        freq_score="1.00"
    elif (( count > 0 )); then
        freq_score=$(echo "scale=2; $count / 10" | bc)
    else
        freq_score="0.00"
    fi

    # Cross-repo score (based on number of repos)
    local repo_score
    if (( repos > 10 )); then
        repo_score="1.00"
    elif (( repos > 0 )); then
        repo_score=$(echo "scale=2; $repos / 10" | bc)
    else
        repo_score="0.00"
    fi

    # Complexity score (longer messages = more complex patterns)
    local msg_len=${#message}
    local complexity_score
    if (( msg_len > 50 )); then
        complexity_score="0.80"
    elif (( msg_len > 0 )); then
        complexity_score=$(echo "scale=2; $msg_len / 62.5" | bc)
    else
        complexity_score="0.00"
    fi

    # Time savings estimate (cross-repo = high savings)
    local savings_score
    if (( repos > 5 )); then
        savings_score="0.90"
    elif (( repos > 0 )); then
        savings_score=$(echo "scale=2; $repos / 5.5" | bc)
    else
        savings_score="0.00"
    fi

    # Workflow pattern score (25% weight)
    # Find the best matching workflow pattern from session analysis
    local workflow_score="0.00"
    if [[ $SESSION_PATTERNS_LOADED -gt 0 ]]; then
        local best_wf_score="0.00"
        for seq in "${!SESSION_SKILL_PATTERNS[@]}"; do
            local data="${SESSION_SKILL_PATTERNS[$seq]}"
            local wf_count="${data%%|*}"
            local wf_potential="${data##*|}"
            # Calculate workflow score for this pattern
            if [[ "$wf_count" =~ ^[0-9]+$ ]] && (( wf_count >= 3 )); then
                local wf_score
                wf_score=$(score_workflow_pattern "$seq" "$wf_count" "$wf_potential")
                # Use highest workflow score found
                if (( $(echo "$wf_score > $best_wf_score" | bc -l 2>/dev/null || echo 0) )); then
                    best_wf_score="$wf_score"
                fi
            fi
        done
        workflow_score="$best_wf_score"
    fi

    # Weighted final score (total = 100%)
    # freq=22.5%, repo=22.5%, complexity=15%, savings=15%, workflow=25%
    local final
    final=$(echo "scale=2; ($freq_score * 0.225) + ($repo_score * 0.225) + ($complexity_score * 0.15) + ($savings_score * 0.15) + ($workflow_score * 0.25)" | bc 2>/dev/null)
    # Cap at 1.0
    if [[ -n "$final" ]] && (( $(echo "$final > 1.0" | bc -l 2>/dev/null || echo 0) )); then
        final="1.00"
    fi
    # Fallback if bc fails
    [[ -z "$final" || ! "$final" =~ ^[0-9.]+$ ]] && final="0.00"

    echo "$final"
}

# Safe score comparison - returns 0 (true) if score >= threshold, 1 (false) otherwise
# Handles empty/invalid scores gracefully
score_gte() {
    local score="${1:-0}"
    local threshold="${2:-1}"

    # Validate inputs - treat invalid as 0
    [[ -z "$score" || ! "$score" =~ ^[0-9]*\.?[0-9]+$ ]] && score="0"
    [[ -z "$threshold" || ! "$threshold" =~ ^[0-9]*\.?[0-9]+$ ]] && threshold="1"

    # Use bc for comparison, redirect errors
    local result
    result=$(echo "$score >= $threshold" | bc -l 2>/dev/null) || result="0"

    # Return based on bc result (1 = true, 0 = false)
    [[ "$result" == "1" ]] && return 0 || return 1
}

# Create a skill from a pattern
create_skill() {
    local pattern_name="$1"
    local pattern_desc="$2"
    local repos="$3"
    local score="$4"

    # Generate skill name from pattern
    local skill_name=$(echo "$pattern_name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | cut -c1-30)
    local skill_dir="${SKILLS_OUTPUT}/${skill_name}"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY RUN] Would create skill: $skill_name (score: $score)"
        return
    fi

    mkdir -p "$skill_dir"

    cat > "${skill_dir}/SKILL.md" << EOF
---
name: ${skill_name}
description: Auto-generated skill from cross-repo pattern - ${pattern_desc}
version: 1.0.0
category: workspace-hub/auto-generated
type: skill
auto_generated: true
source_pattern: "${pattern_name}"
creation_date: $(date -Iseconds)
score: ${score}
source_repos:
$(echo "$repos" | tr ',' '\n' | sed 's/^/  - /')
---

# ${pattern_name}

> Auto-generated skill from recurring cross-repository pattern

## Pattern Details

**Description:** ${pattern_desc}

**Score:** ${score}

**Detected in repositories:**
$(echo "$repos" | tr ',' '\n' | sed 's/^/- /')

## When to Use

This skill was auto-generated because the pattern "${pattern_name}" was detected across multiple repositories. Use this when performing similar operations.

## Implementation

Based on the detected pattern, this skill captures:

1. The workflow or code pattern identified
2. Common implementation approach
3. Cross-repository applicability

## Examples

*Examples extracted from commit history:*

\`\`\`
Pattern: ${pattern_name}
Repos: ${repos}
\`\`\`

---

*Auto-generated by claude-reflect on $(date "+%Y-%m-%d")*
EOF

    echo "Created skill: $skill_dir"
}

# Create a skill from a workflow pattern (tool sequence)
create_workflow_skill() {
    local sequence="$1"
    local count="$2"
    local potential="$3"
    local score="$4"
    local suggested_name="$5"

    # Generate skill name from sequence or use suggested name
    local skill_name
    if [[ -n "$suggested_name" ]]; then
        skill_name="$suggested_name"
    else
        skill_name=$(echo "$sequence" | tr '[:upper:]' '[:lower:]' | sed 's/ -> /-/g' | sed 's/[^a-z0-9-]//g' | cut -c1-30)
    fi
    local skill_dir="${SKILLS_OUTPUT}/${skill_name}"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY RUN] Would create workflow skill: $skill_name (score: $score)"
        return
    fi

    mkdir -p "$skill_dir"

    cat > "${skill_dir}/SKILL.md" << EOF
---
name: ${skill_name}
description: Auto-generated skill from workflow pattern - ${sequence}
version: 1.0.0
category: workspace-hub/auto-generated
type: workflow-skill
auto_generated: true
source: workflow_pattern
workflow_sequence: "${sequence}"
workflow_count: ${count}
skill_potential: ${potential}
creation_date: $(date -Iseconds)
score: ${score}
---

# ${skill_name}

> Auto-generated skill from repeated session workflow pattern

## Workflow Details

**Tool Sequence:** \`${sequence}\`

**Occurrence Count:** ${count}

**Skill Potential:** ${potential}

**Score:** ${score}

## When to Use

This skill was auto-generated because the workflow pattern "${sequence}" was detected frequently in session logs. Use this when performing similar tool sequences.

## Workflow Pattern

The detected tool sequence follows this pattern:

\`\`\`
${sequence}
\`\`\`

## Suggested Automation

Based on this workflow pattern, consider:

1. Creating a script that automates this sequence
2. Adding a Claude Code hook for common triggers
3. Documenting when this pattern is most useful

---

*Auto-generated from session workflow analysis on $(date "+%Y-%m-%d")*
*Source: skill_worthy_patterns from session analysis*
EOF

    echo "Created workflow skill: $skill_dir"
}

# Store pattern in memory (for patterns below threshold)
store_learning() {
    local pattern="$1"
    local repos="$2"
    local score="$3"

    local memory_file="${MEMORY_DIR}/learnings.yaml"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY RUN] Would store learning: $pattern (score: $score)"
        return
    fi

    # Append to learnings file
    cat >> "$memory_file" << EOF

- pattern: "${pattern}"
  repos: "${repos}"
  score: ${score}
  date: $(date -Iseconds)
EOF

    echo "Stored learning: $pattern"
}

# Create a skill with an embedded script
create_script_skill() {
    local pattern="$1"
    local examples="$2"
    local repos="$3"
    local score="$4"
    local skill_type="$5"

    # Generate skill name from pattern
    local skill_name=$(echo "$pattern" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/<[^>]*>//g' | cut -c1-30)
    [[ -z "$skill_name" ]] && skill_name="auto-script-$(date +%s)"
    local skill_dir="${SKILLS_OUTPUT}/${skill_name}"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY RUN] Would create script skill: $skill_name (score: $score)"
        return
    fi

    mkdir -p "$skill_dir"

    # Create SKILL.md
    cat > "${skill_dir}/SKILL.md" << EOF
---
name: ${skill_name}
description: Auto-generated script skill from session patterns
version: 1.0.0
category: workspace-hub/auto-generated
type: script-skill
auto_generated: true
skill_type: ${skill_type}
source_pattern: "${pattern}"
creation_date: $(date -Iseconds)
score: ${score}
source_repos:
$(echo "$repos" | tr ',' '\n' | sed 's/^/  - /')
---

# ${skill_name}

> Auto-generated script skill from repeated command patterns

## Pattern Details

**Type:** ${skill_type}
**Score:** ${score}

**Detected in repositories:**
$(echo "$repos" | tr ',' '\n' | sed 's/^/- /')

## Command Pattern

\`\`\`bash
${pattern}
\`\`\`

## Examples from Sessions

\`\`\`bash
${examples}
\`\`\`

## Script

See \`run.sh\` for the automation script.

---

*Auto-generated by claude-reflect on $(date "+%Y-%m-%d")*
EOF

    # Create a basic run.sh script
    cat > "${skill_dir}/run.sh" << 'SCRIPT_EOF'
#!/usr/bin/env bash
# Auto-generated script from session pattern
# Pattern: PATTERN_PLACEHOLDER
set -euo pipefail

# Cross-platform detection
detect_workspace_hub() {
    case "$(uname -s)" in
        Linux*) for d in "/mnt/github/workspace-hub" "$HOME/github/workspace-hub"; do [[ -d "$d" ]] && echo "$d" && return; done ;;
        Darwin*) for d in "$HOME/github/workspace-hub"; do [[ -d "$d" ]] && echo "$d" && return; done ;;
        MINGW*|MSYS*|CYGWIN*) for d in "/c/github/workspace-hub" "$HOME/github/workspace-hub"; do [[ -d "$d" ]] && echo "$d" && return; done ;;
    esac
    echo "$HOME"
}

WORKSPACE_HUB="$(detect_workspace_hub)"

# TODO: Implement pattern logic here
# Based on pattern: PATTERN_PLACEHOLDER
echo "Script skill: SKILL_NAME_PLACEHOLDER"
echo "Edit this script to implement the pattern."
SCRIPT_EOF

    # Replace placeholders
    sed -i "s|PATTERN_PLACEHOLDER|${pattern}|g" "${skill_dir}/run.sh" 2>/dev/null || \
    sed -i '' "s|PATTERN_PLACEHOLDER|${pattern}|g" "${skill_dir}/run.sh" 2>/dev/null || true
    sed -i "s|SKILL_NAME_PLACEHOLDER|${skill_name}|g" "${skill_dir}/run.sh" 2>/dev/null || \
    sed -i '' "s|SKILL_NAME_PLACEHOLDER|${skill_name}|g" "${skill_dir}/run.sh" 2>/dev/null || true

    chmod +x "${skill_dir}/run.sh"

    echo "Created script skill: $skill_dir"
}

# Enhance existing skill with new script or pattern
enhance_skill() {
    local skill_dir="$1"
    local pattern="$2"
    local examples="$3"
    local score="$4"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY RUN] Would enhance skill: $skill_dir"
        return
    fi

    local enhancement_file="${skill_dir}/ENHANCEMENTS.md"

    cat >> "$enhancement_file" << EOF

## Enhancement $(date "+%Y-%m-%d")

**Pattern:** ${pattern}
**Score:** ${score}

\`\`\`bash
${examples}
\`\`\`

EOF

    echo "Enhanced skill: $skill_dir"
}

# Map workflow sequences to suggested skill names
map_workflow_to_skill_name() {
    local sequence="$1"

    case "$sequence" in
        "Read "*" Edit"*|"Read -> Edit")
            echo "code-review"
            ;;
        "Grep "*" Read "*" Edit"*|"Grep -> Read -> Edit")
            echo "search-and-fix"
            ;;
        "Grep "*" Read"*|"Grep -> Read")
            echo "code-search"
            ;;
        "Read "*" Write"*|"Read -> Write")
            echo "file-transform"
            ;;
        "Bash "*" Read"*|"Bash -> Read")
            echo "command-inspect"
            ;;
        "Glob "*" Read"*|"Glob -> Read")
            echo "file-explore"
            ;;
        "Read "*" Bash"*|"Read -> Bash")
            echo "config-execute"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Process workflow patterns from session analysis
process_workflow_patterns() {
    if [[ $SESSION_PATTERNS_LOADED -eq 0 ]]; then
        echo "No workflow patterns to process"
        return
    fi

    echo ""
    echo "=== Processing Workflow Patterns ==="
    echo ""

    local workflow_skills_created=0

    for seq in "${!SESSION_SKILL_PATTERNS[@]}"; do
        local data="${SESSION_SKILL_PATTERNS[$seq]}"
        local wf_count="${data%%|*}"
        local wf_potential="${data##*|}"

        # Skip patterns with low count
        [[ ! "$wf_count" =~ ^[0-9]+$ ]] && continue
        (( wf_count < 3 )) && continue

        # Calculate workflow score
        local wf_score
        wf_score=$(score_workflow_pattern "$seq" "$wf_count" "$wf_potential")

        # Get suggested skill name
        local suggested_name
        suggested_name=$(map_workflow_to_skill_name "$seq")

        echo "Workflow: \"$seq\""
        echo "  Count: $wf_count | Potential: $wf_potential | Score: $wf_score"

        # Determine action based on score
        if score_gte "$wf_score" "$THRESHOLD_CREATE"; then
            echo "  Action: CREATE WORKFLOW SKILL"
            create_workflow_skill "$seq" "$wf_count" "$wf_potential" "$wf_score" "$suggested_name"
            ((workflow_skills_created++)) || true
        elif score_gte "$wf_score" "$THRESHOLD_ENHANCE"; then
            echo "  Action: STORE FOR ENHANCEMENT"
            store_learning "workflow:$seq" "session" "$wf_score"
        else
            echo "  Action: STORE LEARNING"
            store_learning "workflow:$seq" "session" "$wf_score"
        fi
        echo ""
    done

    echo "Workflow skills created: $workflow_skills_created"
    WORKFLOW_SKILLS_CREATED=$workflow_skills_created
}

# Process script ideas if available
process_script_ideas() {
    local script_ideas_file="${PATTERNS_DIR}/script-ideas_*.json"
    local latest_ideas=$(ls -t $script_ideas_file 2>/dev/null | head -1)

    if [[ ! -f "$latest_ideas" ]]; then
        echo "No script ideas file found, skipping script-based skill creation"
        return
    fi

    echo ""
    echo "=== Processing Script Ideas ==="
    echo ""

    local scripts_created=0

    while IFS='|' read -r pattern examples repos score skill_type; do
        [[ -z "$pattern" ]] && continue

        # Validate score before comparison
        [[ -z "$score" || ! "$score" =~ ^[0-9]*\.?[0-9]+$ ]] && score="0"

        echo "Script Idea: \"${pattern:0:40}...\""
        echo "  Type: $skill_type | Score: $score"

        if score_gte "$score" "$THRESHOLD_CREATE"; then
            echo "  Action: CREATE SCRIPT SKILL"
            create_script_skill "$pattern" "$examples" "$repos" "$score" "$skill_type"
            ((scripts_created++)) || true
        elif score_gte "$score" "$THRESHOLD_ENHANCE"; then
            echo "  Action: STORE FOR ENHANCEMENT"
            store_learning "$pattern" "$repos" "$score"
        else
            echo "  Action: STORE LEARNING"
            store_learning "$pattern" "$repos" "$score"
        fi
        echo ""
    done < <(jq -r '.skill_candidates[] | "\(.pattern)|\(.examples | join("; "))|\(.repos | join(","))|\(.score)|\(.skill_type)"' "$latest_ideas" 2>/dev/null)

    echo "Script skills created: $scripts_created"
    SKILLS_CREATED=$((SKILLS_CREATED + scripts_created))
}

# Process patterns
echo "=== Processing Cross-Repo Patterns ==="
echo ""

SKILLS_CREATED=0
SKILLS_ENHANCED=0
LEARNINGS_STORED=0
WORKFLOW_SKILLS_CREATED=0

# Extract and process each cross-repo pattern
# Using process substitution to avoid subshell (so counters persist)
while IFS='|' read -r message repos count; do
    # Skip empty lines
    [[ -z "$message" ]] && continue

    # Validate count before calculations
    [[ ! "$count" =~ ^[0-9]+$ ]] && count=0

    repo_count=$(echo "$repos" | tr ',' '\n' | grep -c . 2>/dev/null) || repo_count=0
    score=$(score_pattern "$repo_count" "$count" "$message")

    # Truncate message for display
    short_msg="${message:0:50}"

    echo "Pattern: \"$short_msg...\""
    echo "  Repos: $repo_count | Count: $count | Score: $score"

    # Determine action based on score
    if score_gte "$score" "$THRESHOLD_CREATE"; then
        echo "  Action: CREATE SKILL"
        create_skill "$message" "Pattern detected in $repo_count repositories" "$repos" "$score"
        ((SKILLS_CREATED++)) || true
    elif score_gte "$score" "$THRESHOLD_ENHANCE"; then
        echo "  Action: ENHANCE EXISTING"
        store_learning "$message" "$repos" "$score"
        ((SKILLS_ENHANCED++)) || true
    else
        echo "  Action: STORE LEARNING"
        store_learning "$message" "$repos" "$score"
        ((LEARNINGS_STORED++)) || true
    fi
    echo ""
done < <(jq -r '.cross_repo_patterns[] | "\(.message)|\(.repos | join(","))|\(.count)"' "$PATTERN_FILE" 2>/dev/null)

# Process workflow patterns from session analysis
process_workflow_patterns

# Update state file
STATE_FILE="${STATE_DIR}/reflect-state.yaml"
if [[ -f "$STATE_FILE" ]] && [[ "$DRY_RUN" != "true" ]]; then
    cat >> "$STATE_FILE" << EOF
last_skill_creation: $(date -Iseconds)
actions_taken:
  skills_created: $SKILLS_CREATED
  skills_enhanced: $SKILLS_ENHANCED
  workflow_skills_created: $WORKFLOW_SKILLS_CREATED
  learnings_stored: $LEARNINGS_STORED
EOF
fi

# Process script ideas for script-based skills
process_script_ideas

echo "=== Summary ==="
echo "Skills Created: $SKILLS_CREATED"
echo "Workflow Skills Created: $WORKFLOW_SKILLS_CREATED"
echo "Skills Enhanced: $SKILLS_ENHANCED"
echo "Learnings Stored: $LEARNINGS_STORED"
