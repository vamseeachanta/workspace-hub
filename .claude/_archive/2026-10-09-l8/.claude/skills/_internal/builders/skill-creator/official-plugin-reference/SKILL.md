---
name: skill-creator-official-plugin-reference
description: 'Sub-skill of skill-creator: Official Plugin Reference.'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Official Plugin Reference

## Official Plugin Reference


This custom skill **extends** the official Anthropic `skill-creator` plugin:
- Install: `/plugin install skill-creator@claude-plugin-directory`
- Repo: `anthropics/claude-plugins-official/plugins/skill-creator`
- Capabilities: create skills, improve existing skills, run evals, benchmark performance with variance analysis

**Composition pattern**: invoke the official plugin for core skill creation mechanics.
This custom skill adds **workspace-specific conventions** on top:
- WRK linkage (every skill tied to a WRK item)
- Category taxonomy (`category:` / `subcategory:` fields)
- Gate compliance (verify-gate-evidence.py integration)
- Workspace-hub folder conventions and naming rules

**When the official plugin releases a new version**: update `official_plugin:` field above,
review the changelog, and adjust only the workspace-specific sections below that conflict.
Do NOT copy official plugin logic into this file — reference it.
