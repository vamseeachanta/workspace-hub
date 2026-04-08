---
title: "Skills System"
tags: [skills, system, knowledge-carrier, shared]
sources:
  - multi-agent-parity-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Skills System

The primary knowledge carrier across all agents. Skills are git-tracked markdown files that define capabilities, workflows, and domain knowledge.

## Scale

- 691+ skills across multiple agents and domains
- Covers: marine/offshore, drilling, FEA, CFD, standards, GTM, automation

## Structure

```
.claude/skills/
  <category>/
    <name>/
      SKILL.md          # Skill definition
.claude/commands/
  <category>/
    <name>.md           # Slash command (references SKILL.md)
```

A skill appears as `<category>:<name>` (e.g., `workspace-hub:repo-sync`).

## Registration

- Skills: `.claude/commands/<category>/<name>.md` + `.claude/skills/<category>/<name>/SKILL.md`
- Command file references SKILL.md via `@.claude/skills/<path>/SKILL.md`

## Cross-Agent Access

| Agent | Access Path |
|-------|-------------|
| Claude Code | `.claude/skills/` (native) |
| Codex | `.codex/skills` -> `../.claude/skills` (symlink) |
| Gemini | `.gemini/skills` -> `../.claude/skills` (symlink) |
| Hermes | symlink -> `.claude/skills/` |

## Cross-References

- **Related concept**: [[multi-agent-parity]]
- **Related concept**: [[compound-learning-loop]]
- **Related entity**: [GSD Framework](../entities/gsd-framework.md)
