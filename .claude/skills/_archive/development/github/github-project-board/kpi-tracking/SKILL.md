---
name: github-project-board-kpi-tracking
description: 'Sub-skill of github-project-board: KPI Tracking.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# KPI Tracking

## KPI Tracking


```bash
# Track key performance indicators
gh api graphql -f query='
  query($project: Int!, $owner: String!) {
    user(login: $owner) {
      projectV2(number: $project) {
        items(first: 100) {
          nodes {
            fieldValues(first: 10) {
              nodes {

*See sub-skills for full details.*
