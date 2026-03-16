---
name: repo-readiness-1-check-readiness-script
description: 'Sub-skill of repo-readiness: 1. Check Readiness Script (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# 1. Check Readiness Script (+1)

## 1. Check Readiness Script


**Location:** `.claude/skills/workspace-hub/repo-readiness/check_readiness.sh`

```bash
#!/bin/bash
# Repository Readiness Check Script

REPO_PATH="${1:-.}"
OUTPUT_FILE="${REPO_PATH}/.claude/readiness-report.md"

# Function: Check configuration

*See sub-skills for full details.*

## 2. Bulk Readiness Check


Check all repos in workspace:

```bash
#!/bin/bash
# Check readiness of all repositories in workspace-hub

WORKSPACE_ROOT="/mnt/github/workspace-hub"
READINESS_SCRIPT="$HOME/.claude/skills/workspace-hub/repo-readiness/check_readiness.sh"

# Get all repos from .gitignore

*See sub-skills for full details.*
