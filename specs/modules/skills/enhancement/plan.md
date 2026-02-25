# Plan: Add Comprehensive Claude Skills for Everyday Work

## Overview
Add ~43 new skills across 8 categories to `/mnt/github/workspace-hub/skills/` following existing patterns (comprehensive ~500-1000 lines, YAML frontmatter, code examples, scripts).

**Key Addition**: `claude-reflection` skill with cross-repo progress tracking system.

---

## Priority 0: Claude Reflection & Progress Tracking System

### `claude-reflection` Skill (workspace-hub category)

A meta-skill that enables Claude to:
- Learn from user corrections and preferences
- Capture workflow patterns worth automating
- Build persistent knowledge across sessions
- Self-improve through the Reflect → Abstract → Generalize loop

**Location**: `skills/workspace-hub/claude-reflection/SKILL.md`

### Cross-Repo Progress Tracking System

Track skill implementation progress across all repos. Claude checks progress state at session start and continues from where it left off.

**Progress State File**: `~/.claude/state/skills-progress.yaml`

```yaml
# ~/.claude/state/skills-progress.yaml
last_updated: 2025-01-17T10:30:00Z
current_phase: 1
skills:
  python-docx:
    status: completed
    completed_at: 2025-01-16T14:20:00Z
    repo: workspace-hub
  openpyxl:
    status: in_progress
    started_at: 2025-01-17T09:00:00Z
    repo: workspace-hub
    notes: "Core capabilities done, need integration examples"
  polars:
    status: pending

repos:
  workspace-hub:
    skills_dir: /mnt/github/workspace-hub/skills
    skills_completed: 2
    skills_total: 43
  digitalmodel:
    skills_dir: /mnt/github/digitalmodel/skills
    synced_from: workspace-hub
    last_sync: 2025-01-16T12:00:00Z
```

**Progress Tracking Behavior**:
1. **Session Start**: Claude reads `~/.claude/state/skills-progress.yaml`
2. **Resume Logic**: Continue from `in_progress` skill or next `pending` skill
3. **On Completion**: Update status, timestamp, increment counters
4. **Cross-Repo Sync**: Track which repos have synced skill updates

**Commands**:
- `/skills-progress` - Show current implementation status
- `/skills-continue` - Resume skill implementation from last position
- `/skills-sync <repo>` - Sync skills to another repo

---

## New Skill Categories & Skills

### 1. `automation/` - Workflow & Task Automation (5 skills)
| Skill | Description | Priority |
|-------|-------------|----------|
| `n8n` | Open-source workflow automation, node-based pipelines | High |
| `activepieces` | Self-hosted no-code automation | Medium |
| `airflow` | Python DAG workflow orchestration | High |
| `github-actions` | CI/CD and task automation patterns | High |
| `windmill` | Scripts to workflows and UIs | Medium |

### 2. `ai-prompting/` - AI & Prompt Engineering (5 skills)
| Skill | Description | Priority |
|-------|-------------|----------|
| `langchain` | Build LLM-powered applications | High |
| `dspy` | Compile prompts into self-improving pipelines | High |
| `prompt-engineering` | Comprehensive prompting techniques | High |
| `pandasai` | Conversational data analysis with LLMs | Medium |
| `agenta` | LLM prompt management and evaluation | Medium |

### 3. `office-docs/` - Office Document Automation (5 skills)
| Skill | Description | Priority |
|-------|-------------|----------|
| `python-docx` | Create/edit Word documents | High |
| `openpyxl` | Excel file manipulation | High |
| `python-pptx` | PowerPoint automation | High |
| `pypdf` | PDF extraction and manipulation | High |
| `docx-templates` | Template-based document generation | Medium |

### 4. `data-analysis/` - Data Analysis & Visualization (7 skills)
| Skill | Description | Priority |
|-------|-------------|----------|
| `polars` | Fast DataFrame library (Rust-based) | High |
| `streamlit` | Turn data scripts into web apps | High |
| `dash` | Build interactive dashboards | High |
| `autoviz` | Automatic EDA with one line | Medium |
| `ydata-profiling` | Automated data quality reports | Medium |
| `great-tables` | Publication-quality tables | Medium |
| `sweetviz` | EDA comparison reports | Low |

### 5. `productivity/` - Productivity & Task Management (5 skills)
| Skill | Description | Priority |
|-------|-------------|----------|
| `obsidian` | Knowledge management with markdown | High |
| `todoist-api` | Task management API integration | Medium |
| `notion-api` | Notion API for automation | Medium |
| `trello-api` | Kanban board automation | Low |
| `time-tracking` | RescueTime/Toggl integration patterns | Low |

### 6. `documentation/` - Documentation & Technical Writing (6 skills)
| Skill | Description | Priority |
|-------|-------------|----------|
| `mkdocs` | Project documentation with Markdown | High |
| `sphinx` | Python documentation generation | High |
| `pandoc` | Universal document converter | High |
| `marp` | Markdown-based slide presentations | Medium |
| `docusaurus` | Documentation websites (React) | Medium |
| `gitbook` | Publish documentation and books | Low |

### 7. `communication/` - Communication & Collaboration (4 skills)
| Skill | Description | Priority |
|-------|-------------|----------|
| `slack-api` | Slack bot and integration patterns | High |
| `teams-api` | Microsoft Teams automation | Medium |
| `miro-api` | Whiteboard automation | Low |
| `calendly-api` | Scheduling automation | Low |

### 8. `devtools/` - Development Utilities (5 skills)
| Skill | Description | Priority |
|-------|-------------|----------|
| `docker` | Containerization patterns | High |
| `cli-productivity` | jq, fzf, ripgrep patterns | High |
| `vscode-extensions` | Productivity plugins & settings | Medium |
| `raycast-alfred` | Launcher automation | Low |
| `git-advanced` | Advanced git workflows | High |

## Skill File Structure (Per Existing Pattern)

Each skill will have:
```
skills/<category>/<skill-name>/
├── SKILL.md          # Main documentation (500-1000 lines)
├── README.md         # Quick reference
└── scripts/          # Helper scripts (where applicable)
    └── *.sh
```

### SKILL.md Template Structure
```yaml
---
name: skill-name
description: One-line description
version: 1.0.0
category: category-name
type: skill
trigger: manual
auto_execute: false
capabilities:
  - capability1
  - capability2
tools:
  - Read
  - Write
  - Bash
tags: [tag1, tag2]
platforms: [python, linux, macos]
related_skills:
  - related-skill
---
```

Followed by sections:
1. **Header** - Title and description
2. **Quick Start** - Installation and basic usage
3. **When to Use** - Decision matrix (USE when / DON'T USE when)
4. **Prerequisites** - Required setup
5. **Core Capabilities** - 6+ code examples per capability
6. **Integration Examples** - Multi-tool workflows
7. **Best Practices** - Standards and conventions
8. **Troubleshooting** - Common issues and solutions
9. **Related Skills** - Cross-references
10. **Version History** - Changelog

## Implementation Phases

### Phase 0: Foundation Infrastructure (FIRST)
**Must complete before other skills**:
1. `claude-reflection` skill (workspace-hub category)
2. Progress tracking system (`~/.claude/state/skills-progress.yaml`)
3. Progress tracking commands (`/skills-progress`, `/skills-continue`, `/skills-sync`)

### Phase 1: High-Priority Foundation (18 skills)
Categories: office-docs (4), data-analysis (3), documentation (3), devtools (3), ai-prompting (3), automation (2)

Skills:
- `python-docx`, `openpyxl`, `python-pptx`, `pypdf`
- `polars`, `streamlit`, `dash`
- `mkdocs`, `sphinx`, `pandoc`
- `docker`, `cli-productivity`, `git-advanced`
- `langchain`, `dspy`, `prompt-engineering`
- `github-actions`, `airflow`

### Phase 2: Medium Priority (14 skills)
- `n8n`, `activepieces`, `windmill`
- `pandasai`, `agenta`
- `docx-templates`
- `autoviz`, `ydata-profiling`, `great-tables`
- `obsidian`, `todoist-api`, `notion-api`
- `marp`, `docusaurus`
- `slack-api`, `teams-api`, `vscode-extensions`

### Phase 3: Lower Priority (10 skills)
- `sweetviz`
- `trello-api`, `time-tracking`
- `gitbook`
- `miro-api`, `calendly-api`
- `raycast-alfred`

## Files to Create

### Phase 0: Foundation Files
- `skills/workspace-hub/claude-reflection/SKILL.md` - Core reflection skill
- `skills/workspace-hub/claude-reflection/README.md` - Quick reference
- `~/.claude/state/skills-progress.yaml` - Progress tracking state
- `~/.claude/commands/skills-progress.md` - Progress command
- `~/.claude/commands/skills-continue.md` - Continue command
- `~/.claude/commands/skills-sync.md` - Sync command

### Category README files (8 files)
- `skills/automation/README.md`
- `skills/ai-prompting/README.md`
- `skills/office-docs/README.md`
- `skills/data-analysis/README.md`
- `skills/productivity/README.md`
- `skills/documentation/README.md`
- `skills/communication/README.md`
- `skills/devtools/README.md`

### Skill directories and files (~42 skills × 2 files = 84+ files)
Each skill: `SKILL.md` + `README.md` minimum

### Update master index
- `skills/README.md` - Add new categories and skills

## Verification

1. **Structure check**: Each skill has SKILL.md with valid YAML frontmatter
2. **Content check**: Each skill has 6+ working code examples
3. **Cross-references**: Related skills properly linked
4. **README updates**: Master index includes all new skills
5. **Invocation test**: Skills load correctly via `/skill-name`
6. **Progress tracking**: `~/.claude/state/skills-progress.yaml` updates correctly
7. **Cross-repo sync**: Skills sync to other repos correctly

## Estimated Scope
- 43 new skills (42 + claude-reflection)
- 8 new category directories with READMEs
- ~500-1000 lines per skill = 21,500-43,000 lines total
- Progress tracking system (state file + 3 commands)
- Update master skills/README.md

## Questions Resolved
- Location: workspace-hub/skills/ (following existing practice)
- Depth: Comprehensive (500-1000 lines with scripts)
- Priority: All categories equally, phased by practical value
- Progress tracking: Via ~/.claude/state/skills-progress.yaml
- Cross-repo: Sync mechanism tracks which repos have which skills
- **Plans storage**: Save plans in workspace-hub (and relevant repos), not ~/.claude/plans/

## Post-Approval Actions
1. Move this plan to `/mnt/github/workspace-hub/.claude/plans/skills-enhancement.md`
2. Update CLAUDE.md to reference plans location in repo

---

## Appendix: Claude Reflection Skill Content

The full skill content provided by user (to be placed in `skills/workspace-hub/claude-reflection/SKILL.md`):

```yaml
---
name: claude-reflection
description: Self-improvement and learning skill that helps Claude learn from user interactions, corrections, and preferences
version: 1.0.0
category: workspace-hub
type: skill
trigger: auto
auto_execute: true
capabilities:
  - correction_detection
  - preference_capture
  - pattern_extraction
  - knowledge_persistence
  - cross_session_learning
tools:
  - Read
  - Write
  - Edit
tags: [meta, learning, self-improvement, memory]
platforms: [all]
related_skills:
  - skill-learner
  - repo-readiness
---
```

**Triggers** (auto-detect):
- Direct correction ("no, use X", "actually...", "that's wrong")
- Preference statement ("I prefer...", "always...", "never...")
- Explicit memory request ("remember:", "for next time...")
- Positive reinforcement ("perfect!", "exactly!")
- Repeated task pattern (same workflow 3+ times)
- Error then success (failed approach → working solution)

**Core Process**: Reflect → Abstract → Generalize → Store

**Storage Scopes**: Global | Domain | Project | Session
