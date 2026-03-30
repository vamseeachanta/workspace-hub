---
name: github-swarm-issue-3-progress-tracking
description: 'Sub-skill of github-swarm-issue: 3. Progress Tracking (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 3. Progress Tracking (+3)

## 3. Progress Tracking


```bash
# Track issue progress
track_progress() {
  local ISSUE_NUM=$1

  # Get current issue state
  ISSUE=$(gh issue view $ISSUE_NUM --json body,labels)
  BODY=$(echo "$ISSUE" | jq -r '.body')

  # Count completed vs total tasks

*See sub-skills for full details.*

## 4. Issue Comment Commands


Use these commands in issue comments:

```markdown
<!-- Analyze issue and suggest approach -->
/swarm analyze

<!-- Decompose into subtasks -->
/swarm decompose 5

<!-- Assign specific agent type -->

*See sub-skills for full details.*

## 5. Automated Triage


```bash
# Triage unlabeled issues
triage_issues() {
  # Get unlabeled issues
  gh issue list --label "" --json number,title,body | \
    jq -r '.[] | @base64' | while read -r encoded; do
      ISSUE=$(echo "$encoded" | base64 -d)
      NUM=$(echo "$ISSUE" | jq -r '.number')
      TITLE=$(echo "$ISSUE" | jq -r '.title')
      BODY=$(echo "$ISSUE" | jq -r '.body')

*See sub-skills for full details.*

## 6. Stale Issue Management


```bash
# Process stale issues
manage_stale_issues() {
  # Get issues not updated in 30 days
  STALE_DATE=$(date -d '30 days ago' '+%Y-%m-%d')

  gh issue list --state open --json number,title,updatedAt | \
    jq -r ".[] | select(.updatedAt < \"$STALE_DATE\") | .number" | \
    while read -r num; do
      # Check if already marked stale

*See sub-skills for full details.*
