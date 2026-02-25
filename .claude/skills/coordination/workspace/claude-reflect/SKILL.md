---
name: claude-reflect
description: Periodic cross-repo reflection analyzing 30 days of git history, extracting patterns via RAGS loop, and auto-creating skills
version: 2.0.0
category: workspace-hub
type: skill
trigger: scheduled
auto_execute: true
cron: "0 5 * * *"
capabilities:
  - multi_repo_git_analysis
  - pattern_extraction
  - pattern_scoring
  - trend_analysis
  - skill_auto_creation
  - skill_enhancement
  - weekly_reports
  - cross_repo_sync
  - progress_tracking
tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
related_skills: [skill-learner, repo-sync, skill-creator, knowledge-manager, improve]
scripts:
  - analyze-history.sh
  - extract-patterns.sh
  - analyze-trends.sh
  - generate-report.sh
  - create-skills.sh
  - daily-reflect.sh
requires: []
see_also: []
---

# Claude Reflect Skill

> Automated daily reflection analyzing git history across all workspace-hub submodules, extracting patterns via RAGS loop, and auto-creating skills from recurring patterns.

## Quick Start

```bash
# Run full RAGS loop manually
/reflect

# Quick 7-day reflection
/reflect --days 7

# Preview patterns without creating skills
DRY_RUN=true /reflect

# Force weekly report generation
WEEKLY_REPORT=true /reflect
```

## Automated Execution

**Cron Schedule:** Daily at 5:00 AM
- Runs full RAGS loop automatically
- Generates weekly reports on Sundays
- Auto-creates skills when pattern score >= 0.8

## When to Use

- **Automated**: Runs daily via cron - no manual intervention needed
- **Manual**: Run `/reflect` to trigger immediate analysis
- Before planning new features to identify reusable patterns
- After major releases to capture learnings

## Distinction from Similar Skills

| Skill | Trigger | Scope | Data Source |
|-------|---------|-------|-------------|
| `skill-learner` | Post-commit | Single repo | Last commit |
| `claude-reflection` | Auto/session | User interactions | Conversation |
| `claude-reflect` | Manual/scheduled | All 26 repos | 30-day git history |

## Prerequisites

- Git access to all workspace-hub submodules
- `~/.claude/state/` directory for state persistence
- `~/.claude/memory/` directory for global patterns

## Overview

This skill analyzes git history across all 26+ workspace-hub submodules to extract development patterns and automatically enhance or create skills based on findings.

## Quick Reference

### Commands

| Command | Description |
|---------|-------------|
| `/reflect` | Run reflection with default 30-day window |
| `/reflect --days 7` | Quick 7-day reflection |
| `/reflect --days 90` | Extended quarterly reflection |
| `/reflect --repo <name>` | Single repository reflection |
| `/reflect --dry-run` | Preview patterns without creating skills |

## Core Workflow: RAGS Loop

### 1. REFLECT - Collect Git History

Enumerate and analyze git activity across all submodules:

```bash
# Enumerate submodules
git submodule foreach --quiet 'echo $name'

# Extract 30-day commits per repo
git log --since="30 days ago" --pretty=format:"%H|%s|%an|%ad" --date=short
```

**Data Collected:**
- Commit hash, message, author, date
- Files changed per commit
- Diff summaries
- Commit frequency patterns

### 2. ABSTRACT - Identify Patterns

Analyze collected data to identify recurring patterns:

**Pattern Types:**
1. **Code Patterns**: Import conventions, code structures, techniques
2. **Workflow Patterns**: TDD adoption, config-before-code, test-with-feature
3. **Commit Patterns**: Message conventions, prefixes (feat, fix, chore)
4. **Correction Patterns**: Fix commits, "actually" messages, immediate follow-ups
5. **Tool Patterns**: Framework usage, library adoption, tooling preferences

**Pattern Detection Heuristics:**
- Frequency: Pattern appears in 3+ commits
- Consistency: Same pattern used by multiple authors
- Spread: Pattern appears across multiple repositories

### 3. GENERALIZE - Determine Scope

Categorize patterns by their applicability:

| Scope | Criteria | Storage Location |
|-------|----------|------------------|
| **Global** | 5+ repos | `~/.claude/memory/patterns/` |
| **Domain** | 2-4 repos, same domain | `~/.claude/memory/domains/<domain>/` |
| **Project** | Single repo | `<repo>/.claude/knowledge/` |

### 4. STORE - Persist and Act

Score patterns and take appropriate action:

**Scoring Criteria:**
- **Frequency** (0.0-1.0): How often the pattern appears
- **Cross-repo Impact** (0.0-1.0): How many repos use it
- **Complexity** (0.0-1.0): Pattern sophistication
- **Time Savings** (0.0-1.0): Estimated automation benefit

**Weighted Score Calculation:**
```
score = (frequency * 0.3) + (cross_repo * 0.3) + (complexity * 0.2) + (time_savings * 0.2)
```

**Actions by Score:**
| Score Range | Action |
|-------------|--------|
| >= 0.8 | Create new skill automatically |
| 0.6 - 0.79 | Enhance existing skill |
| < 0.6 | Log for future reference |

## State Management

**State File**: `~/.claude/state/reflect-state.yaml`

```yaml
version: "1.0"
last_run: 2026-01-21T10:30:00Z
analysis_window_days: 30
repos_analyzed: 26
patterns_extracted: 45
actions_taken:
  skills_enhanced: 5
  skills_created: 2
  learnings_stored: 23
next_scheduled: 2026-02-21
history:
  - date: 2026-01-21
    patterns: 45
    skills_created: 2
    skills_enhanced: 5
```

## Pattern Output Format

```yaml
patterns:
  - id: "pattern-001"
    type: "workflow"
    name: "TDD Test-First Pattern"
    description: "Tests created before implementation"
    evidence:
      - repo: "aceengineer-admin"
        commits: ["abc123", "def456"]
      - repo: "digitalmodel"
        commits: ["ghi789"]
    frequency: 0.85
    cross_repo_score: 0.9
    complexity_score: 0.7
    time_savings_score: 0.8
    final_score: 0.83
    recommended_action: "create_skill"
```

## Integration Points

### With skill-learner
- Shares pattern extraction logic
- Extended for multi-repo analysis
- Complementary triggers (post-commit vs periodic)

### With repo-sync
- Uses parallel git operations
- Leverages submodule enumeration

### With skill-creator
- Invoked when score >= 0.8
- Passes pattern data for skill generation

### State Files Updated
- `~/.claude/state/reflect-state.yaml`: Reflection history
- `~/.claude/state/skills-progress.yaml`: Skill updates
- `.claude/skill-registry.yaml`: New skill entries

## Execution Checklist

- [ ] Verify git access to all submodules (`git submodule status`)
- [ ] Ensure state directory exists (`~/.claude/state/`)
- [ ] Run with `--dry-run` first to preview patterns
- [ ] Review extracted patterns before skill creation
- [ ] Verify created/enhanced skills work correctly
- [ ] Check state file for accurate tracking

## Error Handling

### Submodule Access Issues
```bash
# Check submodule status
git submodule status

# Update submodules
git submodule update --init --recursive
```

### Empty History
If no commits found in window, reflection completes with warning:
```
Warning: No commits found in the last 30 days
Consider running with --days 90 for a larger window
```

### Pattern Scoring Issues
If pattern scores seem incorrect:
1. Check evidence commit counts
2. Verify cross-repo detection
3. Review pattern categorization

## Workflows

### Weekly Reflection

```bash
# Quick weekly review
/reflect --days 7

# Review patterns
cat ~/.claude/state/reflect-state.yaml
```

### Monthly Deep Reflection

```bash
# Full 30-day analysis
/reflect

# Extended with skill creation
/reflect --days 30
```

### Quarterly Review

```bash
# Extended quarterly analysis
/reflect --days 90

# Review all created skills
ls .claude/skills/
```

## Metrics & Success Criteria

- **Analysis Coverage**: 100% of active submodules analyzed
- **Pattern Detection Rate**: >= 5 patterns per reflection
- **Skill Creation Quality**: Created skills rated useful by user
- **State Persistence**: All runs tracked in state file
- **Performance**: Full reflection completes in < 10 minutes

## Best Practices

### Run Frequency
- Weekly: `--days 7` for quick insights
- Monthly: Default 30-day for comprehensive analysis
- Quarterly: `--days 90` for strategic patterns

### Pattern Review
- Always use `--dry-run` before creating skills
- Review high-scoring patterns manually
- Verify cross-repo patterns are genuine

### Skill Creation
- Check created skills compile/work
- Add examples from actual commits
- Link to source evidence

## Scripts Architecture

The skill uses a modular pipeline of scripts:

```
daily-reflect.sh (orchestrator)
├── analyze-history.sh    # REFLECT: Extract git commits
├── extract-patterns.sh   # ABSTRACT: Identify patterns
├── analyze-trends.sh     # GENERALIZE: Cross-day trends
├── create-skills.sh      # STORE: Auto-create skills
└── generate-report.sh    # Weekly digest reports
```

### Script Details

| Script | Phase | Input | Output |
|--------|-------|-------|--------|
| `analyze-history.sh` | REFLECT | Git repos | `analysis_*.json` |
| `extract-patterns.sh` | ABSTRACT | Analysis JSON | `patterns_*.json` |
| `analyze-trends.sh` | GENERALIZE | Multiple patterns | `trends_*.json` |
| `create-skills.sh` | STORE | Patterns | Skills + learnings |
| `generate-report.sh` | Report | All data | `weekly_digest_*.md` |

### Output Locations

```
~/.claude/state/
├── reflect-state.yaml       # Current state
├── reflect-history/         # Raw analysis files
│   └── analysis_*.json
├── patterns/                # Extracted patterns
│   └── patterns_*.json
├── trends/                  # Trend analysis
│   └── trends_*.json
└── reports/                 # Weekly digests
    └── weekly_digest_*.md

~/.claude/memory/patterns/
└── learnings.yaml           # Low-score patterns for reference

.claude/skills/workspace-hub/auto-generated/
└── <skill-name>/            # Auto-created skills
    └── SKILL.md
```

## References

- [Skill Learner](../skill-learner/SKILL.md) - Post-commit pattern extraction
- [Repo Sync](../repo-sync/SKILL.md) - Multi-repo operations
- [Skill Creator](../../builders/skill-creator/SKILL.md) - Skill generation

---

## Version History

- **2.0.0** (2026-01-21): Full RAGS loop implementation
  - Added pattern extraction engine (`extract-patterns.sh`)
  - Added cross-daily trend analysis (`analyze-trends.sh`)
  - Added actionable reports generator (`generate-report.sh`)
  - Added auto-skill creation module (`create-skills.sh`)
  - Updated `daily-reflect.sh` to orchestrate all phases
  - Weekly reports auto-generated on Sundays
- **1.0.0** (2026-01-21): Initial release with basic RAGS spec
