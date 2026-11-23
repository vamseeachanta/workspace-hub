# Plan: Claude-Reflect Skill Implementation

## Overview

Build a `claude-reflect` skill that analyzes 30 days of git history across all 26 workspace-hub submodules, extracts patterns using the Reflect-Abstract-Generalize-Store (RAGS) loop, and enhances/creates skills based on findings.

**Distinction from existing skills:**
| Skill | Trigger | Scope | Data Source |
|-------|---------|-------|-------------|
| `skill-learner` | Post-commit | Single repo | Last commit |
| `claude-reflection` (planned) | Auto/session | User interactions | Conversation |
| `claude-reflect` (this plan) | Manual/scheduled | All 26 repos | 30-day git history |

---

## Implementation Tasks

### 1. Create Skill Directory Structure

```
.claude/skills/workspace-hub/claude-reflect/
├── SKILL.md           # Main skill documentation
└── scripts/
    └── analyze-history.sh  # Git history extraction helper
```

### 2. SKILL.md Content

**Frontmatter:**
```yaml
---
name: claude-reflect
description: Periodic cross-repo reflection analyzing 30 days of git history, extracting patterns via RAGS loop, and enhancing/creating skills
version: 1.0.0
category: workspace-hub
type: skill
trigger: manual
auto_execute: false
capabilities:
  - multi_repo_git_analysis
  - pattern_extraction
  - pattern_scoring
  - skill_enhancement
  - skill_creation
  - cross_repo_sync
  - progress_tracking
tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
related_skills: [skill-learner, repo-sync, skill-creator]
---
```

**Core Workflow (RAGS Loop):**

1. **REFLECT** - Collect git history across repos
   - Enumerate submodules via `git submodule foreach`
   - Extract 30-day commit logs (hash, message, author, files, diff)
   - Aggregate into analysis structure

2. **ABSTRACT** - Identify patterns
   - Code patterns (imports, structures, techniques)
   - Workflow patterns (TDD, config-before-code, test-with-feature)
   - Commit message patterns (conventional commits, prefixes)
   - Correction patterns (fix commits, "actually" messages)
   - Tool usage patterns (libraries, frameworks)

3. **GENERALIZE** - Determine scope
   - Global (5+ repos): Store in `~/.claude/memory/`
   - Domain (2-4 repos, same domain): Store in domain-specific memory
   - Project (single repo): Store in repo's `.claude/knowledge/`

4. **STORE** - Persist and act
   - Score patterns (frequency, cross-repo impact, complexity, time-savings)
   - Score >= 0.8: Create new skill
   - Score 0.6-0.79: Enhance existing skill
   - Score < 0.6: Log for future reference
   - Update `~/.claude/state/skills-progress.yaml`

### 3. Commands

| Command | Description |
|---------|-------------|
| `/reflect` | Run reflection with default 30-day window |
| `/reflect --days 7` | Quick 7-day reflection |
| `/reflect --days 90` | Extended quarterly reflection |
| `/reflect --repo <name>` | Single repository reflection |
| `/reflect --dry-run` | Preview patterns without creating skills |

### 4. State Management

**Progress file** (`~/.claude/state/reflect-state.yaml`):
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
```

### 5. Integration Points

- **skill-learner**: Reuse pattern extraction logic, extend for multi-repo
- **repo-sync**: Use for parallel git operations across 26 submodules
- **skills-progress.yaml**: Add reflection history section
- **skill-registry.yaml**: Auto-update when new skills created

### 6. Register Command

Add to `.claude/commands/workspace-hub/reflect.md`:
```markdown
---
name: reflect
aliases: [claude-reflect]
description: Run periodic reflection on git history across all repos
---
# Loads skill
@~/.claude/skills/workspace-hub/claude-reflect/SKILL.md
```

---

## Critical Files to Create/Modify

| File | Action |
|------|--------|
| `.claude/skills/workspace-hub/claude-reflect/SKILL.md` | CREATE |
| `.claude/skills/workspace-hub/claude-reflect/scripts/analyze-history.sh` | CREATE |
| `.claude/commands/workspace-hub/reflect.md` | CREATE |
| `.claude/skill-registry.yaml` | UPDATE (add reflect entry) |

---

## Verification

1. **Manual test**: Run `/reflect --dry-run` and verify pattern extraction
2. **State persistence**: Check `~/.claude/state/reflect-state.yaml` created/updated
3. **Skill enhancement**: Verify an existing skill gets version bump with new examples
4. **Skill creation**: If high-scoring pattern found, verify new skill directory created
5. **Cross-repo**: Confirm all 26 submodules are analyzed (check logs)

---

## Design Decisions (Confirmed)

1. **Automation**: Auto-create/enhance skills when pattern score >= threshold (no manual approval required)
2. **Pattern Focus**: Extract all pattern types (code, workflow, commit messages, corrections, tool usage)
3. **Relationship**: Complement `claude-reflection` (keep both - this for git history, that for session interactions)

---

## Estimated Deliverables

- `SKILL.md`: ~400-600 lines (comprehensive documentation with examples)
- `analyze-history.sh`: ~100 lines (git extraction helper)
- `reflect.md` command: ~20 lines (command registration)
- State file schema: defined in SKILL.md
