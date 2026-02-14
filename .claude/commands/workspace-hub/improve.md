---
name: improve
aliases: [self-improve, ecosystem-improve]
description: Improve ecosystem files (config, skills, memory, rules, docs) from session learnings
category: workspace-hub
---

# Improve Command

Autonomous ecosystem improvement skill. Reads session signals (corrections, patterns, errors, insights) and applies improvements to CLAUDE.md, rules, memory, skills, and docs.

## Usage

```
/improve [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview improvements without applying them |
| `--scope <target>` | Limit to specific target: `memory`, `rules`, `skills`, `docs`, `config` |
| `--verbose` | Show detailed scoring and classification |

## Examples

```bash
# Full autonomous improvement (session exit)
/improve

# Preview only
/improve --dry-run

# Improve only memory files
/improve --scope memory

# Improve only skills (lifecycle management)
/improve --scope skills

# Verbose output with scoring details
/improve --verbose
```

## What It Improves

| Target | Location | Actions |
|--------|----------|---------|
| Config | `CLAUDE.md` | Resource Index updates, Core Rules patterns |
| Rules | `.claude/rules/*.md` | Add correction examples, new subsections |
| Memory | `.claude/memory/` | Add debugging lessons, tool conventions |
| Skills | `.claude/skills/**/*.md` | Create, enhance, deprecate, archive |
| Docs | `.claude/docs/` | Update stale references, fill gaps |

## Skill Reference

@.claude/skills/workspace-hub/improve/SKILL.md

## Related Commands

- `/reflect` - Periodic reflection on git history (produces signals consumed by `/improve`)
- `/insights` - Session analysis (produces insights consumed by `/improve`)
- `/knowledge` - Knowledge capture and retrieval
