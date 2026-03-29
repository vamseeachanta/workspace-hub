---
name: self-improving-skills
description: Use after completing any complex task (5+ tool calls), fixing a tricky error, or discovering a non-trivial workflow. Also use when a loaded skill is outdated, incomplete, or wrong during execution.
---

# Self-Improving Skills

After substantial work, offer to capture it. When existing skills are wrong, fix them immediately.

## After Complex Tasks

When you finish a task that involved 5+ tool calls, overcame a tricky error, or discovered a non-trivial workflow:

1. **Offer** to save the approach as a skill: "This workflow could be saved as a reusable skill. Want me to create one?"
2. If yes, use `skill-creator` to create it in `.claude/skills/`
3. Focus on the **procedural knowledge** — exact steps, commands, pitfalls — not a narrative of what happened

## During Skill Use

When following a loaded skill and finding it outdated, incomplete, or wrong:

1. **Fix it immediately** — don't wait to be asked
2. Make targeted edits to the SKILL.md addressing the specific issue
3. Skills that aren't maintained become liabilities

## What NOT to Skill-ify

- One-off solutions or project-specific conventions (use CLAUDE.md or rules)
- Standard practices well-documented elsewhere
- Anything enforceable with a hook or script (automate it instead)
