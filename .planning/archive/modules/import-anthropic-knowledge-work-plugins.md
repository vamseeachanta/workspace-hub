# Import Anthropic Knowledge-Work-Plugins into Workspace-Hub

## Metadata
- **title**: Import Knowledge-Work-Plugins
- **description**: Fetch all skills and commands from anthropics/knowledge-work-plugins and incorporate into workspace-hub skill system
- **version**: 1.0.0
- **module**: skills-import
- **session.id**: serene-munching-falcon
- **session.agent**: orchestrator
- **source**: https://github.com/anthropics/knowledge-work-plugins

---

## Overview

Import 55+ skills and 40+ commands from [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) into workspace-hub's `.claude/skills/` directory. This includes converting the source format (table frontmatter) to workspace-hub format (YAML frontmatter), creating new category directories, merging overlapping skills, and building a refresh mechanism for future updates.

---

## Source Inventory (11 Plugins, ~55 Skills, ~40 Commands)

### 1. sales/ (6 skills, 3 commands)
**Skills**: account-research, call-prep, competitive-intelligence, create-an-asset, daily-briefing, draft-outreach
**Commands**: /call-summary, /forecast, /pipeline-review
**Target**: `.claude/skills/business/sales/`

### 2. customer-support/ (5 skills, 5 commands)
**Skills**: ticket-triage, customer-research, response-drafting, escalation, knowledge-management
**Commands**: /triage, /research, /draft-response, /escalate, /kb-article
**Target**: `.claude/skills/business/customer-support/`

### 3. product-management/ (6 skills, 6 commands)
**Skills**: feature-spec, roadmap-management, stakeholder-comms, user-research-synthesis, competitive-analysis, metrics-tracking
**Commands**: /write-spec, /roadmap-update, /stakeholder-update, /synthesize-research, /competitive-brief, /metrics-review
**Target**: `.claude/skills/business/product/`

### 4. marketing/ (5 skills, 7 commands)
**Skills**: content-creation, campaign-planning, brand-voice, competitive-analysis, performance-analytics
**Commands**: /draft-content, /campaign-plan, /brand-review, /competitive-brief, /performance-report, /seo-audit, /email-sequence
**Target**: `.claude/skills/business/marketing/` (MERGE with existing)

### 5. legal/ (6 skills, 5 commands)
**Skills**: contract-review, nda-triage, compliance, canned-responses, legal-risk-assessment, meeting-briefing
**Commands**: /review-contract, /triage-nda, /vendor-check, /brief, /respond
**Target**: `.claude/skills/business/legal/`

### 6. finance/ (6 skills, 5 commands)
**Skills**: journal-entry-prep, reconciliation, financial-statements, variance-analysis, close-management, audit-support
**Commands**: /journal-entry, /reconciliation, /income-statement, /variance-analysis, /sox-testing
**Target**: `.claude/skills/business/finance/`

### 7. data/ (6 skills, 6 commands)
**Skills**: sql-queries, data-exploration, data-visualization, statistical-analysis, data-validation, interactive-dashboard-builder
**Commands**: /analyze, /explore-data, /write-query, /create-viz, /build-dashboard, /validate
**Target**: `.claude/skills/data/analytics/`

### 8. enterprise-search/ (3 skills, 2 commands)
**Skills**: search-strategy, source-management, knowledge-synthesis
**Commands**: /search, /digest
**Target**: `.claude/skills/business/enterprise-search/`

### 9. productivity/ (2 skills, 3 commands)
**Skills**: task-management, memory-management
**Commands**: /start, /update, /update --comprehensive
**Target**: `.claude/skills/business/productivity/` (MERGE with existing)

### 10. bio-research/ (6 skills, 0 commands)
**Skills**: single-cell-rna-qc, scvi-tools, nextflow-pipelines, clinical-trial-protocol, instrument-data-allotrope, scientific-problem-selection
**Target**: `.claude/skills/science/bio-research/`

### 11. cowork-plugin-management/ (1 skill, 0 commands)
**Skills**: cowork-plugin-customizer
**Target**: `.claude/skills/development/plugin-management/`

---

## Format Conversion

### Source format (knowledge-work-plugins)
```markdown
| name | description |
|------|-------------|
| skill-name | Description text... |

# Skill Title
Content...
```

### Target format (workspace-hub)
```yaml
---
name: skill-name
description: Description text...
version: 1.0.0
category: category-name
last_updated: 2026-02-03
source: https://github.com/anthropics/knowledge-work-plugins
related_skills:
  - related-skill-1
---

# Skill Title
Content...
```

### Conversion rules
1. Extract `name` and `description` from the source table row
2. Wrap in YAML frontmatter (`---`)
3. Add `version: 1.0.0`, `category`, `last_updated: 2026-02-03`
4. Add `source: https://github.com/anthropics/knowledge-work-plugins`
5. Infer `related_skills` from the same plugin's other skills
6. Keep all content below the frontmatter unchanged

---

## Overlap Handling (Merge Strategy)

Skills that exist in both systems will be **merged**:

| Existing Skill | Source Equivalent | Merge Strategy |
|---|---|---|
| `marketing/competitive-analysis` | `marketing/competitive-analysis` | Enrich existing with Anthropic's framework sections |
| `marketing/content-strategy` | `marketing/content-creation` + `marketing/brand-voice` | Add campaign planning and brand voice review sections |
| `business/product/product-roadmap` | `product-management/roadmap-management` | Enrich with Anthropic's stakeholder update format |
| `business/productivity/today` | `productivity/task-management` | These are different enough to coexist as separate skills |

For merges: keep workspace-hub frontmatter, append non-overlapping sections from the source, and note the merge in a `## Sources` footer.

---

## Directory Structure (New)

```
.claude/skills/
├── business/
│   ├── sales/                      # NEW (6 skills + 3 commands)
│   │   ├── account-research/SKILL.md
│   │   ├── call-prep/SKILL.md
│   │   ├── competitive-intelligence/SKILL.md
│   │   ├── create-an-asset/SKILL.md
│   │   ├── daily-briefing/SKILL.md
│   │   ├── draft-outreach/SKILL.md
│   │   └── commands/               # command references
│   ├── customer-support/           # NEW (5 skills + 5 commands)
│   │   ├── ticket-triage/SKILL.md
│   │   ├── customer-research/SKILL.md
│   │   ├── response-drafting/SKILL.md
│   │   ├── escalation/SKILL.md
│   │   ├── knowledge-management/SKILL.md
│   │   └── commands/
│   ├── legal/                      # NEW (6 skills + 5 commands)
│   │   ├── contract-review/SKILL.md
│   │   ├── nda-triage/SKILL.md
│   │   ├── compliance/SKILL.md
│   │   ├── canned-responses/SKILL.md
│   │   ├── legal-risk-assessment/SKILL.md
│   │   ├── meeting-briefing/SKILL.md
│   │   └── commands/
│   ├── finance/                    # NEW (6 skills + 5 commands)
│   │   ├── journal-entry-prep/SKILL.md
│   │   ├── reconciliation/SKILL.md
│   │   ├── financial-statements/SKILL.md
│   │   ├── variance-analysis/SKILL.md
│   │   ├── close-management/SKILL.md
│   │   ├── audit-support/SKILL.md
│   │   └── commands/
│   ├── enterprise-search/          # NEW (3 skills + 2 commands)
│   │   ├── search-strategy/SKILL.md
│   │   ├── source-management/SKILL.md
│   │   ├── knowledge-synthesis/SKILL.md
│   │   └── commands/
│   ├── product/                    # EXISTING (enrich)
│   │   ├── product-roadmap/SKILL.md        # MERGE
│   │   ├── feature-spec/SKILL.md           # NEW
│   │   ├── stakeholder-comms/SKILL.md      # NEW
│   │   ├── user-research-synthesis/SKILL.md # NEW
│   │   ├── competitive-analysis/SKILL.md   # NEW
│   │   ├── metrics-tracking/SKILL.md       # NEW
│   │   └── commands/
│   ├── marketing/                  # EXISTING (merge + new)
│   │   ├── competitive-analysis/   # MERGE
│   │   ├── content-strategy/       # MERGE with content-creation
│   │   ├── campaign-planning/SKILL.md      # NEW
│   │   ├── brand-voice/SKILL.md            # NEW
│   │   ├── performance-analytics/SKILL.md  # NEW
│   │   └── commands/
│   ├── productivity/               # EXISTING (add new)
│   │   ├── task-management/SKILL.md        # NEW
│   │   ├── memory-management/SKILL.md      # NEW
│   │   └── ... (existing skills unchanged)
├── data/
│   └── analytics/                  # NEW (6 skills + 6 commands)
│       ├── sql-queries/SKILL.md
│       ├── data-exploration/SKILL.md
│       ├── data-visualization/SKILL.md
│       ├── statistical-analysis/SKILL.md
│       ├── data-validation/SKILL.md
│       ├── interactive-dashboard-builder/SKILL.md
│       └── commands/
├── science/                        # NEW top-level category
│   └── bio-research/               # NEW (6 skills)
│       ├── single-cell-rna-qc/SKILL.md
│       ├── scvi-tools/SKILL.md
│       ├── nextflow-pipelines/SKILL.md
│       ├── clinical-trial-protocol/SKILL.md
│       ├── instrument-data-allotrope/SKILL.md
│       └── scientific-problem-selection/SKILL.md
└── development/
    └── plugin-management/          # NEW (1 skill)
        └── cowork-plugin-customizer/SKILL.md
```

---

## Execution Steps

### Step 1: Fetch all source skill files
- WebFetch each SKILL.md from GitHub (55 files)
- WebFetch each command .md from GitHub (~40 files)
- Store raw content for conversion
- **Parallelize**: fetch up to 5 files concurrently per subagent

### Step 2: Create new directory structure
- Create all new directories listed above
- `mkdir -p` for each path

### Step 3: Convert and write new skills (non-overlapping)
- Convert table frontmatter → YAML frontmatter
- Add `source`, `version`, `last_updated`, `category`, `related_skills`
- Write SKILL.md files to target directories
- **~45 new skills** (non-overlapping)

### Step 4: Merge overlapping skills
- Read existing workspace-hub skill
- Read source skill content
- Merge: keep existing frontmatter + structure, append unique sections from source
- Add `## Sources` footer noting the merge
- **~5 merged skills**

### Step 5: Write command reference files
- Convert command .md files to workspace-hub format
- Place in `commands/` subdirectory under each category
- Each command gets a single `.md` file

### Step 6: Update skills-index.yaml
- Regenerate the skills index to include new skills
- Update category counts
- Add new categories (science, data/analytics)

### Step 7: Update skills README.md
- Add new categories and skill counts
- Add source attribution section

### Step 8: Build refresh mechanism
- Create `scripts/skills/sync-knowledge-work-plugins.sh`
- Script fetches latest from GitHub, diffs against local, reports changes
- Can be run manually or on schedule
- Outputs a diff report showing new/updated/removed skills

---

## Refresh Mechanism Design

### Script: `scripts/skills/sync-knowledge-work-plugins.sh`

```bash
#!/bin/bash
# Sync skills from anthropics/knowledge-work-plugins
# Usage: ./scripts/skills/sync-knowledge-work-plugins.sh [--dry-run] [--plugin=sales]

REPO_URL="https://github.com/anthropics/knowledge-work-plugins"
PLUGINS=(sales customer-support product-management marketing legal finance data enterprise-search productivity bio-research cowork-plugin-management)
```

**Features**:
- `--dry-run`: show what would change without writing
- `--plugin=X`: sync only a specific plugin
- `--diff`: show content diff for changed skills
- Generates a sync report in `specs/modules/skill-sync-report.md`

### Companion skill: `.claude/skills/workspace-hub/skill-sync/SKILL.md`
- Documents the sync process
- Provides `/skill-sync` command reference
- Lists the mapping table (source plugin → target directory)

---

## Verification

1. **File count**: Confirm ~55 new SKILL.md files + ~40 command .md files created
2. **Format check**: Grep for valid YAML frontmatter in all new files
3. **Source attribution**: All new files contain `source: https://github.com/anthropics/knowledge-work-plugins`
4. **Merged files**: Read merged skills to confirm both original and new content present
5. **Index updated**: `skills-index.yaml` reflects new counts
6. **Refresh script**: Run `sync-knowledge-work-plugins.sh --dry-run` to confirm it detects current state as in-sync
7. **No regressions**: Existing skills unchanged (except merged ones)

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| WebFetch rate limits | Batch fetches, retry with backoff |
| Source content changes | Refresh script handles future updates |
| Large file count | Delegate to subagents, parallelize |
| Merge conflicts | Manual review for 5 overlap cases |
| gh CLI not authenticated | Use WebFetch for all GitHub access |

---

## Estimated Scope

- **New directories**: ~15
- **New SKILL.md files**: ~50
- **Merged SKILL.md files**: ~5
- **New command .md files**: ~40
- **New scripts**: 1 (sync script)
- **Updated files**: 2 (skills-index.yaml, skills/README.md)
