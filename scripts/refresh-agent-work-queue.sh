#!/bin/bash
# Auto-refresh agent work queue from GitHub label queries
# Run weekly on Sunday, regenerates notes/agent-work-queue.md

set -e
cd /mnt/local-analysis/workspace-hub

REPO="vamseeachanta/workspace-hub"
QUEUE_FILE="notes/agent-work-queue.md"
DATE=$(date +%Y-%m-%d)

gh_issue_query() {
  gh -R "$REPO" issue list -L 100 --label "$1" --json number,title,labels \
    --jq '.[] | "#" + (.number|tostring) + "\t" + .title + "\t" + ([.labels[] | select(.name | startswith("cat:") or startswith("dark-intelligence") or startswith("domain:")) | .name] | join(","))'
}

echo "# Agent Work Queue — Week of $DATE" > "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "> Auto-generated from GitHub label queries. agent: labels on issues are the source of truth." >> "$QUEUE_FILE"
echo "> Refresh: ./scripts/refresh-agent-work-queue.sh" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "---" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"

GEMINI_COUNT=$(gh -R "$REPO" issue list -L 200 --label "agent:gemini" 2>/dev/null | wc -l)
CLAUDE_COUNT=$(gh -R "$REPO" issue list -L 200 --label "agent:claude" 2>/dev/null | wc -l)
CODEX_COUNT=$(gh -R "$REPO" issue list -L 200 --label "agent:codex" 2>/dev/null | wc -l)
UNASSIGNED=$(gh -R "$REPO" issue list -L 500 2>/dev/null | grep -v "agent:" | wc -l)

echo "## Queue Summary" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "| Agent | Total |" >> "$QUEUE_FILE"
echo "|-------|-------|" >> "$QUEUE_FILE"
echo "| **GEMINI** | $GEMINI_COUNT |" >> "$QUEUE_FILE"
echo "| **CLAUDE** | $CLAUDE_COUNT |" >> "$QUEUE_FILE"
echo "| **CODEX** | $CODEX_COUNT |" >> "$QUEUE_FILE"
echo "| **UNASSIGNED** | $UNASSIGNED |" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "---" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"

echo "## Gemini Queue (Research / Prep)" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "### High Priority" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "| # | Issue | What to Do |" >> "$QUEUE_FILE"
echo "|---|-------|------------|" >> "$QUEUE_FILE"
gh_issue_query "agent:gemini,priority:high" | while IFS=$'\t' read -r num title labels; do
  echo "| $num | $title | |" >> "$QUEUE_FILE"
done
echo "" >> "$QUEUE_FILE"

echo "### Medium Priority" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "| # | Issue | What to Do |" >> "$QUEUE_FILE"
echo "|---|-------|------------|" >> "$QUEUE_FILE"
gh_issue_query "agent:gemini,priority:medium" | while IFS=$'\t' read -r num title labels; do
  echo "| $num | $title | |" >> "$QUEUE_FILE"
done
echo "" >> "$QUEUE_FILE"
echo "---" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"

echo "## Claude Queue (Implementation / Architecture)" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "### High Priority" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "| # | Issue | What to Do |" >> "$QUEUE_FILE"
echo "|---|-------|------------|" >> "$QUEUE_FILE"
gh_issue_query "agent:claude,priority:high" | while IFS=$'\t' read -r num title labels; do
  echo "| $num | $title | |" >> "$QUEUE_FILE"
done
echo "" >> "$QUEUE_FILE"

echo "### Medium Priority" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "| # | Issue | What to Do |" >> "$QUEUE_FILE"
echo "|---|-------|------------|" >> "$QUEUE_FILE"
gh_issue_query "agent:claude,priority:medium" | while IFS=$'\t' read -r num title labels; do
  echo "| $num | $title | |" >> "$QUEUE_FILE"
done
echo "" >> "$QUEUE_FILE"
echo "---" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"

echo "## Codex Queue (Tests / Bounded / Review)" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "### High Priority" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "| # | Issue | What to Do |" >> "$QUEUE_FILE"
echo "|---|-------|------------|" >> "$QUEUE_FILE"
gh_issue_query "agent:codex,priority:high" | while IFS=$'\t' read -r num title labels; do
  echo "| $num | $title | |" >> "$QUEUE_FILE"
done
echo "" >> "$QUEUE_FILE"

echo "### Medium Priority" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"
echo "| # | Issue | What to Do |" >> "$QUEUE_FILE"
echo "|---|-------|------------|" >> "$QUEUE_FILE"
gh_issue_query "agent:codex,priority:medium" | while IFS=$'\t' read -r num title labels; do
  echo "| $num | $title | |" >> "$QUEUE_FILE"
done
echo "" >> "$QUEUE_FILE"

echo "*Auto-generated. Last refresh: $DATE*" >> "$QUEUE_FILE"
git add "$QUEUE_FILE" 2>/dev/null || true
echo "Queue refreshed at $DATE"
