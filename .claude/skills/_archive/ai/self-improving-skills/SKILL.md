---
name: self-improving-skills
description: Use after completing any complex task (5+ tool calls), fixing a tricky error, or discovering a non-trivial workflow. Also use when a loaded skill is outdated, incomplete, or wrong during execution.
---

# Self-Improving Skills

After substantial work, offer to capture it. When existing skills are wrong, fix them immediately.

## After Complex Tasks

When you finish a task that involved 5+ tool calls, overcame a tricky error, or discovered a non-trivial workflow:

1. **Prefer updating an existing class-level skill** that was loaded or clearly governed the work; add concise procedural knowledge, pitfalls, or a reference pointer.
2. Use `references/` for session-specific detail, transcripts, evidence shapes, or narrow recipes; keep `SKILL.md` as the class-level operating guide.
3. Create a new skill only when no existing umbrella covers the class, and name it at the class level rather than after today's issue/PR/error.
4. If the user explicitly asks to update the skill library, be active: a no-op is appropriate only when there is genuinely no workflow/style/tooling signal.
5. Focus on the **procedural knowledge** — exact steps, commands, pitfalls — not a narrative of what happened

## During Skill Use

When following a loaded skill and finding it outdated, incomplete, or wrong:

1. **Fix it immediately** — don't wait to be asked
2. Make targeted edits to the SKILL.md addressing the specific issue
3. Skills that aren't maintained become liabilities

## What NOT to Skill-ify

- One-off solutions or project-specific conventions (use CLAUDE.md or rules)
- Standard practices well-documented elsewhere
- Anything enforceable with a hook or script (automate it instead)
