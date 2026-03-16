---
name: skill-creator
description: Create new Claude Code skills with proper structure, documentation, and
  best practices. Use when building custom skills for specific domains, workflows,
  or organizational needs.
version: 2.2.0
category: _internal
last_updated: 2026-03-05
official_plugin: skill-creator@claude-plugin-directory
related_skills:
- session-start
- sparc-workflow
- mcp-builder
- skill-learner
- improve
tags: []
see_also:
- skill-creator-official-plugin-reference
- skill-creator-canonical-reference
- skill-creator-instructions
- skill-creator-file-structure
- skill-creator-error-handling
- skill-creator-metrics
- skill-creator-1-clear-triggering
- skill-creator-detailed-instructions
- skill-creator-3-multi-stage-workflow-architecture
- skill-creator-step-1-define-the-skill-scope
- skill-creator-technical-skill-template
- skill-creator-creative-skill-template
- skill-creator-quality-checklist
- skill-creator-execution-checklist
- skill-creator-content-quality
- skill-creator-common-errors
- skill-creator-versioning
- skill-creator-metrics
- skill-creator-skill-discovery
---

# Skill Creator

## Overview

This skill guides the creation of new Claude Code skills. Skills are specialized instruction sets that enhance Claude's capabilities for specific domains, tasks, or workflows.

## When to Use

- Building custom skills for specific domains
- Creating reusable workflow templates
- Standardizing organizational processes
- Extending Claude Code capabilities
- Documenting specialized knowledge

## Quick Start

1. **Define scope** - Answer: What problem? Who uses it? What outputs?
2. **Create structure** - `.claude/skills/skill-name/SKILL.md`
3. **Write frontmatter** - Name, description, version, category
4. **Add content** - Overview, Instructions, Examples, Best Practices
5. **Test** - Verify skill triggers correctly

```bash
# Create skill directory
mkdir -p .claude/skills/my-new-skill

# Create SKILL.md with template
cat > .claude/skills/my-new-skill/SKILL.md << 'EOF'
---
name: my-new-skill
description: Action-oriented description. Use for X, Y, and Z.
version: 1.0.0
category: [builders|tools|content-design|communication|meta]
---

# My New Skill

## Overview
[1-2 sentences explaining purpose]

## When to Use
- Scenario 1
- Scenario 2

## Prerequisites
- Dependency 1
- Dependency 2

## Version History
- **1.0.0** (YYYY-MM-DD): Initial release
EOF
```

## Prerequisites

- Familiarity with YAML frontmatter
- Understanding of markdown structure
- Knowledge of the skill category taxonomy

### Deprecation

When retiring a skill:

```yaml
---
name: old-skill-name
description: DEPRECATED - Use new-skill-name instead. [Original description]
deprecated: true
deprecated_date: 2026-01-02
replacement: new-skill-name
---
```

## Related Skills

- [session-start-routine](../../meta/session-start-routine/SKILL.md) - Skill library maintenance
- [sparc-workflow](../../development/sparc-workflow/SKILL.md) - Development methodology
- [mcp-builder](../mcp-builder/SKILL.md) - MCP server creation

## Version History

- **2.2.0** (2026-03-05): Deduplicated hub SKILL.md; trimmed to <200 lines
- **2.1.0** (2026-03-04): Synced critical rules with Anthropic official guide
- **2.0.0** (2026-01-02): Upgraded to v2 template
- **1.0.0** (2024-10-15): Initial release

## Sub-Skills

- [Official Plugin Reference](official-plugin-reference/SKILL.md)
- [Canonical Reference](canonical-reference/SKILL.md)
- [Instructions](instructions/SKILL.md)
- [File Structure (+1)](file-structure/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)
- [1. Clear Triggering (+1)](1-clear-triggering/SKILL.md)
- [Detailed Instructions](detailed-instructions/SKILL.md)
- [3. Multi-Stage Workflow Architecture (+1)](3-multi-stage-workflow-architecture/SKILL.md)
- [Bad: Conceptual only](bad-conceptual-only/SKILL.md)
- [Good: Actionable](good-actionable/SKILL.md)
- [Step 1: Define the Skill Scope (+2)](step-1-define-the-skill-scope/SKILL.md)
- [[Task Category 1] (+1)](task-category-1/SKILL.md)
- [Technical Skill Template](technical-skill-template/SKILL.md)
- [Installation](installation/SKILL.md)
- [Operation 1 (+1)](operation-1/SKILL.md)
- [Configuration Options](configuration-options/SKILL.md)
- [Common Errors](common-errors/SKILL.md)
- [Step 1: [Name] (+2)](step-1-name/SKILL.md)
- [[Template Name]](template-name/SKILL.md)
- [Creative Skill Template](creative-skill-template/SKILL.md)
- [Principle 1: [Name] (+1)](principle-1-name/SKILL.md)
- [Style 1: [Name] (+1)](style-1-name/SKILL.md)
- [Phase 1: [Name] (+1)](phase-1-name/SKILL.md)
- [Technical Implementation](technical-implementation/SKILL.md)
- [Quality Checklist](quality-checklist/SKILL.md)
- [Inspiration & Examples](inspiration-examples/SKILL.md)
- [Examples](examples/SKILL.md)
- [Best Practices](best-practices/SKILL.md)
- [Advanced Usage](advanced-usage/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Content Quality (+3)](content-quality/SKILL.md)
- [Versioning](versioning/SKILL.md)
- [Skill Discovery (+2)](skill-discovery/SKILL.md)
- [Process Skill Template](process-skill-template/SKILL.md)
- [[Scenario]](scenario/SKILL.md)
