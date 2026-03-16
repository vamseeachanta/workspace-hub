---
name: skill-learner-1-commit-analyzer
description: 'Sub-skill of skill-learner: 1. Commit Analyzer (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# 1. Commit Analyzer (+1)

## 1. Commit Analyzer


**Location:** `analyze_commit.sh`

```bash
#!/bin/bash
# Analyze recent commit for learning opportunities

REPO_PATH="${1:-.}"
COMMIT_HASH="${2:-HEAD}"

# Extract commit info

*See sub-skills for full details.*

## 2. Skill Creator (from Pattern)


**Location:** `create_skill_from_pattern.sh`

```bash
#!/bin/bash
# Create new skill from extracted pattern

PATTERN_NAME="$1"
CATEGORY="${2:-development}"
SOURCE_COMMIT="$3"


*See sub-skills for full details.*
