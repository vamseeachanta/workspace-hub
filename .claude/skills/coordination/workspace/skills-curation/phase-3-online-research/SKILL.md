---
name: skills-curation-phase-3-online-research
description: "Sub-skill of skills-curation: Phase 3 \u2014 Online Research."
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Phase 3 — Online Research

## Phase 3 — Online Research


**Purpose**: search the web for developments relevant to the research targets surfaced in Phase 2, and identify new skills where capability gaps exist.

**Research targets come from:**

- Top N high-gap skills from graph review
- Stale skills flagged in Phase 1
- Active domain areas with no existing coverage

**Primary external source — check skills.sh first:**

Before running any WebSearch queries, check https://skills.sh/ for proven implementations
in the target domain:

- Browse the leaderboard for high-install skills relevant to the domain
- Read the raw SKILL.md on GitHub to inspect content passively
- Key GitHub sources: obra/superpowers, anthropics/skills, wshobson/agents
- Prefer adoption + adaptation over invention: if skills.sh has a proven skill, adopt it
  rather than creating a net-new skill from scratch (subject to license gate — see Adoption Workflow below)

**For each research target:**

1. Check https://skills.sh/ for existing proven implementations (see above)
2. Run `WebSearch` with a focused query if skills.sh has no match:
   - `"<skill domain> best practices 2026 python"`
   - `"<tool name> new features changelog 2026"`
   - `"alternatives to <tool> 2026"`
3. Assess findings:
   - New tool/pattern with no existing skill → shallow or deep gap?
   - Existing skill content outdated → queue enhancement
   - Deprecation found → flag in skill frontmatter
4. Collect research yield (findings per query)

**Yield tracking:**

```
findings_this_run = new_skills_identified + updates_queued + deprecations_found
```

---
