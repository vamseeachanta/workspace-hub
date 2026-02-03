---
id: ADR-003
type: decision
title: "Import anthropics/knowledge-work-plugins into workspace-hub skills"
category: skills
tags: [skills, knowledge-work-plugins, import, sync, anthropic, upstream]
repos: [workspace-hub]
confidence: 0.95
created: "2026-02-03"
last_validated: "2026-02-03"
source_type: session
related: [ADR-002]
status: active
access_count: 0
---

# Import anthropics/knowledge-work-plugins into Workspace-Hub Skills

## Context

The workspace-hub `.claude/skills/` directory contained 113 skills across 8 categories. Anthropic published a reference repository (`anthropics/knowledge-work-plugins`) with 55+ production-quality skills and 40+ commands covering business domains (sales, legal, finance, customer support, enterprise search), data analytics, bio-research, and plugin management. Many of these skills complemented existing workspace-hub capabilities.

## Decision

Import all skills and commands from `anthropics/knowledge-work-plugins` into workspace-hub's `.claude/skills/` directory using a structured process:

1. **Format conversion**: Source uses table-style frontmatter; workspace-hub uses YAML frontmatter with `name`, `description`, `version`, `category`, `last_updated`, `source`, `related_skills` fields
2. **Category mapping**: 11 source plugins mapped to workspace-hub directories (e.g., `sales` → `business/sales/`, `data` → `data/analytics/`, `bio-research` → `science/bio-research/`)
3. **Merge strategy**: 3 overlapping skills (competitive-analysis, content-strategy, product-roadmap) merged by keeping existing content and appending non-overlapping sections with `## Sources` footer
4. **Refresh mechanism**: Sync script at `scripts/skills/sync-knowledge-work-plugins.sh` for future upstream updates

## Results

- 40 new SKILL.md files across 8 new category directories
- 42 command .md files
- 3 existing skills enriched via merge
- 1 standalone brand-voice skill extracted from merge spillover
- Total skills grew from 113 to 272 (central) / 297 (including repo-specific)
- Commit: `4357c50` (99 files changed, 14,759 insertions)

## Rationale

- Anthropic-authored skills represent best practices for Claude-based workflows
- Importing rather than linking preserves workspace-hub's self-contained nature
- Format conversion maintains consistency across the skill catalog
- Merge strategy preserves domain-specific content already in workspace-hub
- Sync script enables repeatable updates without manual re-import

## Consequences

- Skills directory is significantly larger (272 vs 113 SKILL.md files)
- Upstream changes require running sync script to detect drift
- Merged skills have dual attribution in `## Sources` sections
- New categories (sales, legal, finance, etc.) may need workspace-specific customization over time

## References

- Plan spec: `specs/modules/serene-munching-falcon.md`
- Sync script: `scripts/skills/sync-knowledge-work-plugins.sh`
- Sync skill: `.claude/skills/workspace-hub/skill-sync/SKILL.md`
- Source: https://github.com/anthropics/knowledge-work-plugins
