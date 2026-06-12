---
name: crossprovider gemini agent-to-skills-conversion-discard-framework-con
description: Agent-to-Skills conversion: discard framework config, preserve markdown
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [agents, skills, framework-migration]
---

Agent.yaml files in agent-os format contain obsolete framework metadata. The durable value is in markdown documentation (context/domain/*.md, system_prompt.md). Convert to SKILL.md under `.claude/skills/`, delete agent.yaml and directory structure. Applied to 3 agents in worldenergydata (WRK-200, commit cada24d).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
