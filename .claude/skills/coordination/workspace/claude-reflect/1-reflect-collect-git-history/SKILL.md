---
name: claude-reflect-1-reflect-collect-git-history
description: 'Sub-skill of claude-reflect: 1. REFLECT - Collect Git History (+3).'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# 1. REFLECT - Collect Git History (+3)

## 1. REFLECT - Collect Git History


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

## 2. ABSTRACT - Identify Patterns


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

## 3. GENERALIZE - Determine Scope


Categorize patterns by their applicability:

| Scope | Criteria | Storage Location |
|-------|----------|------------------|
| **Global** | 5+ repos | `~/.claude/memory/patterns/` |
| **Domain** | 2-4 repos, same domain | `~/.claude/memory/domains/<domain>/` |
| **Project** | Single repo | `<repo>/.claude/knowledge/` |

## 4. STORE - Persist and Act


Score patterns and take appropriate action:

**Scoring Criteria:**
- **Frequency** (0.0-1.0): How often the pattern appears
- **Cross-repo Impact** (0.0-1.0): How many repos use it
- **Complexity** (0.0-1.0): Pattern sophistication
- **Time Savings** (0.0-1.0): Estimated automation benefit

**Weighted Score Calculation:**
```

*See sub-skills for full details.*
