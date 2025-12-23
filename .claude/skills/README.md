# Claude Code Skills - Workspace Hub

> User-level skills library for Claude Code, accessible across all projects.
>
> Location: `~/.claude/skills/` (symlinked to `/mnt/github/workspace-hub/.claude/skills/`)

## Overview

This collection provides 21 specialized skills organized into 6 categories. Skills are triggered based on their description field when Claude Code determines they're relevant to the current task.

## Quick Reference

| Category | Skills | Purpose |
|----------|--------|---------|
| [Document Handling](#document-handling) | 4 | Work with PDF, DOCX, PPTX, XLSX files |
| [Development](#development) | 2 | Build MCP servers, test web applications |
| [Content & Design](#content--design) | 4 | Frontend UI, themes, canvas graphics, algorithmic art |
| [Communication](#communication) | 4 | Internal comms, Slack GIFs, document collaboration, branding |
| [Builders](#builders) | 2 | Web artifacts, skill creation |
| [Workspace Hub](#workspace-hub-custom) | 5 | Repository sync, SPARC workflow, agent orchestration |

## Skills by Category

### Document Handling

| Skill | Description |
|-------|-------------|
| [pdf](pdf/SKILL.md) | Read, summarize, extract, and analyze PDF documents |
| [docx](docx/SKILL.md) | Create and edit Word documents with formatting |
| [pptx](pptx/SKILL.md) | Build PowerPoint presentations with slides and layouts |
| [xlsx](xlsx/SKILL.md) | Generate Excel spreadsheets with formulas and charts |

### Development

| Skill | Description |
|-------|-------------|
| [mcp-builder](mcp-builder/SKILL.md) | Build Model Context Protocol servers with Claude integration |
| [webapp-testing](webapp-testing/SKILL.md) | Test web applications with Playwright and Chrome DevTools |

### Content & Design

| Skill | Description |
|-------|-------------|
| [frontend-design](frontend-design/SKILL.md) | Design and implement modern web UI components |
| [theme-factory](theme-factory/SKILL.md) | Create comprehensive design systems and themes |
| [canvas-design](canvas-design/SKILL.md) | Create diagrams, graphics, and visualizations with canvas |
| [algorithmic-art](algorithmic-art/SKILL.md) | Generate algorithmic and generative art with code |

### Communication

| Skill | Description |
|-------|-------------|
| [internal-comms](internal-comms/SKILL.md) | Craft professional internal business communications |
| [slack-gif-creator](slack-gif-creator/SKILL.md) | Create custom animated GIFs for Slack |
| [doc-coauthoring](doc-coauthoring/SKILL.md) | Collaborate on documents with tracked changes |
| [brand-guidelines](brand-guidelines/SKILL.md) | Create and maintain brand guidelines |

### Builders

| Skill | Description |
|-------|-------------|
| [web-artifacts-builder](web-artifacts-builder/SKILL.md) | Build self-contained interactive web applications |
| [skill-creator](skill-creator/SKILL.md) | Create new Claude Code skills |

### Workspace Hub Custom

| Skill | Description |
|-------|-------------|
| [repo-sync](repo-sync/SKILL.md) | Manage and synchronize 26+ Git repositories |
| [sparc-workflow](sparc-workflow/SKILL.md) | Apply SPARC methodology for systematic development |
| [agent-orchestration](agent-orchestration/SKILL.md) | Orchestrate AI agents with Claude Flow swarms |
| [compliance-check](compliance-check/SKILL.md) | Verify coding standards and workspace compliance |
| [workspace-cli](workspace-cli/SKILL.md) | Use the unified workspace-hub CLI |

## Usage

### Automatic Activation

Skills activate automatically when Claude Code determines they're relevant:

```
User: "Create a PDF summary of this document"
Claude: [Activates pdf skill, provides PDF processing guidance]

User: "I need to sync all my work repositories"
Claude: [Activates repo-sync skill, provides repository sync commands]
```

### Manual Invocation

Reference skills directly in prompts:

```
"Using the sparc-workflow skill, help me plan this feature"
"Apply the compliance-check skill to verify this repository"
```

## Skill Structure

Each skill follows this structure:

```
skill-name/
└── SKILL.md           # Skill definition with YAML frontmatter
```

### SKILL.md Format

```markdown
---
name: skill-name
description: Trigger description that tells Claude when to use this skill
---

# Skill Title

[Detailed instructions, templates, examples, best practices]
```

## Installation Verification

Check that skills are accessible:

```bash
# Verify symlink
ls -la ~/.claude/skills

# List available skills
ls ~/.claude/skills/

# Check specific skill
cat ~/.claude/skills/repo-sync/SKILL.md
```

## Creating New Skills

Use the [skill-creator](skill-creator/SKILL.md) skill to create new skills:

1. Determine skill category
2. Create descriptive name (kebab-case)
3. Write clear trigger description
4. Include practical examples
5. Add to this index

## Categories Explained

### Document Handling
Work with business documents - reading, creating, editing, and analyzing PDF, Word, PowerPoint, and Excel files.

### Development
Tools for building software - MCP servers for Claude integration, web application testing with browser automation.

### Content & Design
Create visual content - UI components, design systems, diagrams, and generative art.

### Communication
Business communications - internal memos, Slack engagement content, collaborative editing, brand identity.

### Builders
Meta-tools for creating things - interactive web applications and new skills.

### Workspace Hub Custom
Specialized for workspace-hub ecosystem - repository management, development methodology, AI orchestration, compliance.

## Related Documentation

- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Anthropic Official Skills](https://github.com/anthropics/skills)
- [Workspace Hub Documentation](../../docs/README.md)
- [AI Agent Guidelines](../../docs/modules/ai/AI_AGENT_GUIDELINES.md)

## Maintenance

### Adding Skills
1. Create directory under appropriate category
2. Add SKILL.md with proper frontmatter
3. Update this README index
4. Test activation trigger

### Updating Skills
1. Edit SKILL.md content
2. Maintain backward compatibility
3. Update examples if needed

### Removing Skills
1. Remove skill directory
2. Update this README index
3. Check for references in other documentation

---

*Skills are user-level and available across all projects via symlink at `~/.claude/skills/`*
