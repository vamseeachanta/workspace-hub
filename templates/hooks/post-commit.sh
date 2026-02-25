#!/bin/bash

# ABOUTME: Post-commit hook for automatic skill learning
# ABOUTME: Analyzes commits and creates/enhances skills from patterns

set -euo pipefail

# Configuration
REPO_PATH="$(pwd)"

# Try multiple locations for skill
SKILL_LOCATIONS=(
    "${HOME}/.claude/skills/workspace-hub/skill-learner"
    "${WORKSPACE_HUB:-/mnt/github/workspace-hub}/skills/workspace-hub/skill-learner"
    "${WORKSPACE_HUB:-D:/workspace-hub}/skills/workspace-hub/skill-learner"
    "./../../../skills/workspace-hub/skill-learner"
)

ANALYZER_SCRIPT=""
for loc in "${SKILL_LOCATIONS[@]}"; do
    if [ -f "$loc/analyze_commit.sh" ]; then
        ANALYZER_SCRIPT="$loc/analyze_commit.sh"
        break
    fi
done

if [ -z "$ANALYZER_SCRIPT" ]; then
    # Skill learner not installed, skip silently
    exit 0
fi

# Allow bypassing skill learning
if [ "${SKIP_SKILL_LEARNING:-0}" = "1" ]; then
    exit 0
fi

# Only run on significant commits (>50 lines changed)
LINES_CHANGED=$(git diff HEAD^ HEAD --shortstat 2>/dev/null | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo 0)

if [ "$LINES_CHANGED" -lt 50 ]; then
    # Small commit, skip learning
    exit 0
fi

# Run skill learning analysis (in background to not slow down commits)
echo ""
echo "========================================"
echo "Analyzing commit for learning..."
echo "========================================"

"$ANALYZER_SCRIPT" "$REPO_PATH" HEAD

echo ""
echo "✅ Skill learning analysis complete"
echo "Review: cat .claude/skill-learning-log.md"
echo ""

exit 0
