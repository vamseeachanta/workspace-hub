# Claude Reflection Skill

> Self-improvement through learning from interactions

## Quick Reference

| Aspect | Details |
|--------|---------|
| **Version** | 1.0.0 |
| **Category** | workspace-hub |
| **Trigger** | Auto (on correction/preference detection) |
| **Storage** | `~/.claude/memory/` |

## Purpose

A meta-skill enabling Claude to:
- Learn from user corrections
- Capture workflow preferences
- Extract reusable patterns
- Build persistent knowledge across sessions

## Core Process

```
Reflect → Abstract → Generalize → Store
```

## Triggers

| Trigger Type | Example Phrases |
|--------------|-----------------|
| Direct Correction | "no, use X", "actually...", "that's wrong" |
| Preference | "I prefer...", "always...", "never..." |
| Memory Request | "remember:", "for next time..." |
| Reinforcement | "perfect!", "exactly!" |
| Repeated Pattern | Same workflow 3+ times |
| Error→Success | Failed approach → working solution |

## Storage Scopes

| Scope | Location | Persistence |
|-------|----------|-------------|
| Global | `~/.claude/memory/` | Permanent |
| Domain | `~/.claude/memory/domains/<name>/` | Permanent |
| Project | `.claude/memory/` | Per-project |
| Session | In-memory | Session only |

## Usage

This skill activates automatically when triggers are detected. No manual invocation needed.

## Files

- `~/.claude/memory/learnings.yaml` - Captured learnings
- `~/.claude/memory/preferences.yaml` - User preferences
- `~/.claude/memory/patterns.yaml` - Workflow patterns

## Related Skills

- `skill-learner` - Learning new skills
- `repo-readiness` - Repository preparation

## See Also

- [Full SKILL.md](./SKILL.md) - Complete documentation
