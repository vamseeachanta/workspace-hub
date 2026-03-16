---
name: skill-learner
description: Post-commit skill that reviews completed work, identifies reusable patterns,
  and creates/enhances skills for continual learning. Auto-executes after commits
  to build organizational knowledge.
version: 1.0.0
category: coordination
type: skill
trigger: post-commit
auto_execute: true
capabilities:
- commit_analysis
- pattern_extraction
- skill_identification
- skill_enhancement
- knowledge_synthesis
- continual_learning
tools:
- Read
- Write
- Grep
- Glob
- Bash
related_skills:
- skill-creator
- claude-reflect
- knowledge-manager
- improve
- session-start
- repo-readiness
requires: []
see_also:
- skill-learner-external-reference-skillssh
- skill-learner-1-commit-analysis
- skill-learner-files-changed-12
- skill-learner-problem-solved
- skill-learner-analysis
- skill-learner-5-skill-enhancement
- skill-learner-commit-a1b2c3d4
- skill-learner-problem
- skill-learner-1-configuration-yaml
- skill-learner-lessons-learned
- skill-learner-applications
- skill-learner-learning-log
- skill-learner-commit-a1b2c3d4-npv-calculator-implementation
- skill-learner-commit-e5f6g7h8-marine-safety-data-processor
- skill-learner-execution-checklist
- skill-learner-post-commit-hook
- skill-learner-1-commit-analyzer
- skill-learner-3-bulk-learning-analysis
- skill-learner-no-patterns-found
- skill-learner-learning-metrics
- skill-learner-with-session-start-routine
tags: []
---

# Skill Learner

## Quick Start

```bash
# Manual trigger after commit
/skill-learner

# Auto-triggers after:
# - git commit (via post-commit hook)
# - Task completion
# - Feature implementation

# Review learning
cat .claude/skill-learning-log.md
```

## When to Use

**AUTO-EXECUTES (via hook):**
- After every git commit
- After task completion
- After feature implementation
- After bug fixes with significant patterns
- After refactoring work

**MANUAL TRIGGER:**
- To analyze recent work history
- To review learning opportunities
- To create skills from existing patterns
- After completing a project phase
- During knowledge capture sessions

## Prerequisites

- Git repository with commit history
- Access to committed files and diffs
- (Optional) Skills directory for new skill creation
- (Optional) Internet for pattern research

## Overview

The skill-learner performs post-commit analysis to identify reusable patterns, common workflows, and valuable techniques from completed work. It automatically creates new skills or enhances existing ones, ensuring continuous organizational learning.
### What It Analyzes

1. **Commit Content**: Files changed, code added, patterns used
2. **Commit Message**: Task description, context, intent
3. **Work Patterns**: Repeated workflows, common operations
4. **Problem Solutions**: How bugs were fixed, how features were built
5. **Tool Usage**: Libraries, frameworks, techniques employed
6. **Documentation**: Comments, docs added, conventions followed
### Output

Generates:
- Pattern analysis report
- Skill creation recommendations
- Enhanced existing skills
- Learning log with insights
- Knowledge base entries

## Quick Start

```bash
# Create NPV calculator
/financial-calculator-builder npv

# Create IRR calculator
/financial-calculator-builder irr

# Custom calculator
/financial-calculator-builder custom --config config/calc.yaml
```

## Related Skills

- financial-calculator-builder (created)
- plotly-visualization (enhanced)
- yaml-workflow-executor (existing)
```

## Related Skills

- [skill-creator](../../builders/skill-creator/SKILL.md) - Manual skill creation
- [session-start-routine](../../meta/session-start-routine/SKILL.md) - Session initialization
- [repo-readiness](../repo-readiness/SKILL.md) - Repository preparation
- [compliance-check](../compliance-check/SKILL.md) - Standards validation

## References

- [Skill Template](../../../../templates/SKILL_TEMPLATE_v2.md)
- [Pattern Library](../../../../.claude/knowledge/patterns/)
- [Learning Framework](../../../../docs/modules/ai/LEARNING_FRAMEWORK.md)

---

## Version History

- **1.0.0** (2026-01-07): Initial release - post-commit skill learning with pattern extraction, skill creation/enhancement, knowledge synthesis, auto-hook integration, learning log, metrics tracking, and continual learning capabilities

## Sub-Skills

- [1. Review Learning Log Regularly (+3)](1-review-learning-log-regularly/SKILL.md)

## Sub-Skills

- [External Reference: skills.sh](external-reference-skillssh/SKILL.md)
- [1. Commit Analysis](1-commit-analysis/SKILL.md)
- [Files Changed (12) (+3)](files-changed-12/SKILL.md)
- [Problem Solved (+3)](problem-solved/SKILL.md)
- [Analysis (+2)](analysis/SKILL.md)
- [5. Skill Enhancement](5-skill-enhancement/SKILL.md)
- [Commit: a1b2c3d4 (+3)](commit-a1b2c3d4/SKILL.md)
- [Problem](problem/SKILL.md)
- [1. Configuration (YAML) (+3)](1-configuration-yaml/SKILL.md)
- [Lessons Learned](lessons-learned/SKILL.md)
- [Applications](applications/SKILL.md)
- [Learning Log](learning-log/SKILL.md)
- [Commit: a1b2c3d4 - NPV Calculator Implementation](commit-a1b2c3d4-npv-calculator-implementation/SKILL.md)
- [Commit: e5f6g7h8 - Marine Safety Data Processor](commit-e5f6g7h8-marine-safety-data-processor/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Post-Commit Hook](post-commit-hook/SKILL.md)
- [1. Commit Analyzer (+1)](1-commit-analyzer/SKILL.md)
- [3. Bulk Learning Analysis](3-bulk-learning-analysis/SKILL.md)
- [No Patterns Found (+3)](no-patterns-found/SKILL.md)
- [Learning Metrics (+2)](learning-metrics/SKILL.md)
- [With Session Start Routine (+2)](with-session-start-routine/SKILL.md)
