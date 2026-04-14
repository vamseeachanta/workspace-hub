# Skill Template v2.0

> Enhanced skill template combining agent capabilities with skill structure
> Version: 2.0.0
> Created: 2026-01-02

## Template Structure

```markdown
---
name: skill-name
description: Trigger description that tells Claude when to use this skill (auto-detection)
version: 1.0.0
category: development|workspace-hub|tools|document-handling|etc
type: skill|agent|hybrid
capabilities:
  - capability_1
  - capability_2
tools:
  - Tool1
  - Tool2
  - mcp__tool_name
related_skills:
  - related-skill-1
  - related-skill-2
hooks:
  pre: |
    # Pre-execution hook (optional)
  post: |
    # Post-execution hook (optional)
---

# Skill Title

> One-line summary of what this skill does

## Quick Start

[30-second quick reference - the minimum needed to use this skill]

## When to Use

- Trigger scenario 1
- Trigger scenario 2
- Trigger scenario 3

## Prerequisites

- Prerequisite 1
- Prerequisite 2

## Core Concepts

[Key concepts the user needs to understand]

## Implementation Pattern

[Code examples, dataclasses, functions - the core implementation]

## Configuration

[YAML/JSON configuration examples for practical usage]

## Usage Examples

### Example 1: Basic Usage
[Complete working example]

### Example 2: Advanced Usage
[More complex example]

## Execution Checklist

- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Best Practices

- Best practice 1
- Best practice 2

## Error Handling

[What to do when things go wrong]

## Metrics & Success Criteria

- Metric 1: target value
- Metric 2: target value

## Integration Points

### MCP Tools
[MCP tool integration examples]

### Hooks
[Claude Flow hook integration]

### Related Skills
- [skill-1](path/to/SKILL.md) - Description
- [skill-2](path/to/SKILL.md) - Description

## References

- [External Doc 1](url)
- [External Doc 2](url)

## Version History

- **1.0.0** (YYYY-MM-DD): Initial release
```

## Frontmatter Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Unique identifier (kebab-case) |
| `description` | Yes | string | Trigger description for auto-detection |
| `version` | Yes | string | Semantic version (MAJOR.MINOR.PATCH) |
| `category` | Yes | string | Skill category for organization |
| `type` | No | string | `skill`, `agent`, or `hybrid` |
| `capabilities` | No | array | List of capabilities |
| `tools` | No | array | Required tools (Claude tools + MCP tools) |
| `related_skills` | No | array | Cross-references to related skills |
| `hooks` | No | object | Pre/post execution hooks |

## Section Guidelines

### Quick Start (REQUIRED)
- Maximum 5 lines
- Show the most common use case
- Include runnable code if applicable

### When to Use (REQUIRED)
- List 3-5 trigger scenarios
- Use bullet points
- Be specific about when this skill applies

### Core Concepts (REQUIRED for complex skills)
- Explain key terminology
- Include equations/formulas if relevant
- Keep it educational

### Implementation Pattern (REQUIRED)
- Include complete, runnable code
- Use dataclasses for structured data
- Follow Python/TypeScript best practices
- Include type hints

### Configuration (RECOMMENDED)
- Show YAML configuration examples
- Include all configurable options
- Provide sensible defaults

### Usage Examples (REQUIRED)
- At least 2 examples (basic + advanced)
- Complete, copy-paste-runnable code
- Include expected output

### Execution Checklist (RECOMMENDED for workflows)
- Use checkbox format `- [ ]`
- Sequential steps
- Actionable items

### Error Handling (REQUIRED for production skills)
- Common error scenarios
- Recovery procedures
- Troubleshooting tips

### Metrics & Success Criteria (RECOMMENDED)
- Quantifiable outcomes
- Target values
- How to measure success

## Migration from Agents

When converting agents to skills:

1. **Frontmatter**: Keep `name`, `description`, `capabilities`, `hooks`
2. **Add**: `version`, `category`, `related_skills`
3. **Remove**: `type` (agent type), `color`, `priority` (use category instead)
4. **Convert `tools`**: Keep MCP tools, map Claude Code tools
5. **Expand content**: Add sections: Quick Start, When to Use, Configuration, Examples

## Categories

| Category | Description | Location |
|----------|-------------|----------|
| `development` | Software development tools | Central |
| `workspace-hub` | Workspace ecosystem | Central |
| `tools` | Assessment and utilities | Central |
| `document-handling` | Document processing | Central |
| `builders` | Creation meta-tools | Central |
| `content-design` | Visual content | Central |
| `communication` | Business comms | Central |
| `meta` | Skills about skills | Central |
| `engineering` | Domain engineering | Repo-specific |
| `swarm` | Swarm coordination | Central |
| `github` | GitHub integration | Central |
| `consensus` | Distributed systems | Central |
| `optimization` | Performance tools | Central |
| `cloud` | Cloud platform tools | Central |

## Version History

- **2.0.0** (2026-01-02): Enhanced template with agent integration, hooks, capabilities
