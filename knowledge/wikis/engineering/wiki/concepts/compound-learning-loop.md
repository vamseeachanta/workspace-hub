---
title: "Compound Learning Loop"
tags: [methodology, learning, skills, self-improvement]
sources:
  - compound-engineering-methodology
added: 2026-04-08
last_updated: 2026-04-08
---

# Compound Learning Loop

Skills improve from real work, not upfront design. Each engineering session produces artifacts that feed the next session. The learning loop is the engine of [[compound-engineering]].

## The Loop

```
Real work session
  -> Learnings extracted (scripts/learnings/extract-learnings.sh)
    -> Skills created or updated (.claude/skills/)
      -> Better tooling for next session
        -> More efficient work
          -> More learnings extracted
```

## Implementation

- **Post-commit hooks** detect patterns worth capturing
- **cross-agent-bridge.sh** syncs agent knowledge across systems
- **Session learnings** are extracted into `.claude/memory/topics/`
- **Skills** are the durable carrier -- not session memory

## Key Insight

The flywheel accelerates because:
1. Engineering work → new tools
2. New tools → faster work
3. Faster work → more tools
4. 691+ skills accumulated this way

## Anti-Patterns

- Designing skills upfront without real-world usage
- Storing knowledge only in session memory (lost at context reset)
- Manual knowledge transfer between sessions

## Cross-References

- **Related concept**: [[compound-engineering]]
- **Related concept**: [[multi-agent-parity]]
- **Related entity**: [Skills System](../entities/skills-system.md)
