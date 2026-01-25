# Skill Learner

> Automatically analyze commits, extract patterns, and create/enhance skills for continual learning.

## Overview

The skill-learner automatically analyzes every commit to identify reusable patterns, extract knowledge, and create or enhance skills. This ensures continuous organizational learning from all development work.

## Quick Start

### 1. Analyze Single Commit

```bash
./analyze_commit.sh /path/to/repo HEAD
```

### 2. Install Hook (Single Repo)

```bash
./install_hook.sh /path/to/repo
```

### 3. Install Hooks (All Repos)

```bash
./bulk_install_hooks.sh
```

### 4. Review Learning

```bash
# View learning log
cat .claude/skill-learning-log.md

# View extracted patterns
ls -la .claude/knowledge/patterns/
```

## What It Does

After every significant commit (>50 lines), the skill-learner:

1. **Analyzes commit content**
   - Files changed
   - Code patterns used
   - Technologies employed

2. **Detects patterns**
   - Workflow patterns
   - Code patterns
   - Problem-solving approaches

3. **Assesses reusability**
   - Pattern frequency
   - Complexity
   - Domain applicability

4. **Recommends actions**
   - Create new skill (score ≥80)
   - Enhance existing skill (score 50-79)
   - Skip (score <50)

5. **Builds knowledge**
   - Updates learning log
   - Saves pattern documentation
   - Links related skills

## Reusability Scoring

The analyzer calculates a reusability score (0-100) based on:

- **YAML workflows**: +15 points
- **Bash execution**: +10 points
- **TDD approach**: +20 points
- **Plotly visualization**: +25 points
- **Financial calculations**: +30 points
- **API clients**: +20 points
- **Data validation**: +15 points
- **Pattern frequency**: +5-10 points per occurrence
- **Commit size**: +10-15 points for complex changes

**Score Interpretation:**
- **80-100**: High reusability → CREATE NEW SKILL
- **50-79**: Moderate reusability → ENHANCE EXISTING SKILL
- **0-49**: Low reusability → DOCUMENT ONLY

## Files

```
skill-learner/
├── SKILL.md                    # Full documentation
├── README.md                   # This file
├── analyze_commit.sh           # Commit analyzer
├── install_hook.sh             # Single repo hook installer
└── bulk_install_hooks.sh       # Bulk hook installer
```

## Workflow

### Automatic (via Hook)

```bash
# Developer makes commit
git add .
git commit -m "Add NPV calculator with Plotly"

# Hook auto-executes:
# 1. Analyzes commit
# 2. Detects patterns (Plotly, financial calc, YAML config)
# 3. Calculates score: 95/100
# 4. Recommends: CREATE NEW SKILL
# 5. Logs to .claude/skill-learning-log.md
# 6. Saves pattern to .claude/knowledge/patterns/

# Developer sees:
# ✅ Skill learning analysis complete
# Review: cat .claude/skill-learning-log.md
```

### Manual Analysis

```bash
# Analyze specific commit
./analyze_commit.sh . a1b2c3d4

# Analyze last commit
./analyze_commit.sh .

# Analyze last 10 commits
for commit in $(git log -10 --pretty=%H); do
    ./analyze_commit.sh . $commit
done
```

## Learning Log Format

```markdown
# Skill Learning Log

## 2026-01-07 14:30:45

**Commit**: a1b2c3d4567890
**Message**: Add NPV calculator with Plotly
**Reusability Score**: 95/100

**Patterns Detected**:
- plotly_viz
- financial_calc
- yaml_workflow
- bash_execution
- tdd_approach

**Recommendation**: CREATE NEW SKILL

---
```

## Pattern Knowledge Files

```markdown
# Pattern: Add NPV calculator with Plotly

**Discovered**: 2026-01-07
**Commit**: a1b2c3d4567890
**Score**: 95/100

## Patterns Used
- plotly_viz
- financial_calc
- yaml_workflow

## Files Changed
src/modules/npv/calculator.py
src/modules/npv/visualizer.py
config/input/npv_analysis.yaml
scripts/run_npv_analysis.sh

## Key Techniques
[To be documented]
```

## Bypassing Learning

```bash
# Skip for small/trivial commits
SKIP_SKILL_LEARNING=1 git commit -m "Fix typo"

# Disable temporarily
mv .git/hooks/post-commit .git/hooks/post-commit.disabled
```

## Best Practices

1. **Review logs weekly**
   ```bash
   cat .claude/skill-learning-log.md | head -50
   ```

2. **Act on high-score recommendations**
   ```bash
   grep "Score: 9" .claude/skill-learning-log.md
   ```

3. **Refine patterns periodically**
   ```bash
   # Review patterns directory
   ls .claude/knowledge/patterns/
   ```

4. **Share learning across teams**
   ```bash
   # Commit learning logs
   git add .claude/skill-learning-log.md
   git commit -m "Update skill learning log"
   ```

## Integration

### With Session Start Routine

The session-start-routine skill can review recent learning:

```bash
/session-start-routine

# Includes section:
# Recent Learning:
# - 3 patterns extracted this week
# - 1 skill creation recommended
# - 2 skills enhanced
```

### With Skill Creator

When creating skills manually, skill-learner provides context:

```bash
/skill-creator new-feature

# Skill learner suggests:
# Similar patterns: plotly_viz, data_validation
# Related skills: plotly-visualization, data-pipeline-processor
# Best practices from: commit a1b2c3d4
```

## Metrics

Track learning over time:

```bash
# Patterns per month
grep "^##" .claude/skill-learning-log.md | wc -l

# High-value patterns
grep "Score: [89][0-9]/100" .claude/skill-learning-log.md | wc -l

# Skills created from learning
# (manually track in skills directory)
```

## Troubleshooting

### Hook Not Triggering

```bash
# Check hook installed
ls -la .git/hooks/post-commit

# Make executable
chmod +x .git/hooks/post-commit

# Test manually
.git/hooks/post-commit
```

### No Patterns Detected

```bash
# Commit may be too small (<50 lines)
# Or patterns not yet recognized by analyzer
# Review commit manually for patterns
```

### Analyzer Script Not Found

```bash
# Verify skill installed
ls -la ~/.claude/skills/workspace-hub/skill-learner/

# Or check workspace-hub location
ls -la /mnt/github/workspace-hub/.claude/skills/workspace-hub/skill-learner/
```

## Related Skills

- [skill-creator](../../builders/skill-creator/SKILL.md) - Manual skill creation
- [session-start-routine](../../meta/session-start-routine/SKILL.md) - Session health check
- [repo-readiness](../repo-readiness/SKILL.md) - Pre-task preparation

---

**Version**: 1.0.0
**Created**: 2026-01-07
**Category**: workspace-hub
