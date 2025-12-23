# Claude Code Skills Library

> User-level skills for Claude Code, accessible across all projects.
>
> Location: `~/.claude/skills/` (symlinked to `/mnt/github/workspace-hub/.claude/skills/`)

## Overview

This collection provides **22 specialized skills** organized into **7 categories**. Skills are triggered automatically based on their description field when Claude Code determines they're relevant to the current task.

## Quick Reference

| Category | Skills | Purpose |
|----------|--------|---------|
| [Document Handling](#document-handling) | 4 | Work with PDF, DOCX, PPTX, XLSX files |
| [Development](#development) | 2 | Build MCP servers, test web applications |
| [Content & Design](#content--design) | 4 | Frontend UI, themes, canvas graphics, algorithmic art |
| [Communication](#communication) | 4 | Internal comms, Slack GIFs, document collaboration, branding |
| [Builders](#builders) | 2 | Web artifacts, skill creation |
| [Workspace Hub](#workspace-hub) | 5 | Repository sync, SPARC workflow, agent orchestration |
| [Tools](#tools) | 1 | AI tool assessment and utilities |

## Directory Structure

```
skills/
├── document-handling/       # PDF, DOCX, PPTX, XLSX manipulation
├── development/             # MCP servers, web testing
├── content-design/          # UI, themes, graphics, generative art
├── communication/           # Business communications
├── builders/                # Meta-tools for creation
├── workspace-hub/           # Workspace-specific automation
├── tools/                   # Assessment and utility skills
└── README.md                # This file
```

---

## Skills by Category

### Document Handling

Work with business documents - reading, creating, editing, and analyzing files.

| Skill | Description |
|-------|-------------|
| [pdf](document-handling/pdf/SKILL.md) | Read, summarize, extract, and analyze PDF documents |
| [docx](document-handling/docx/SKILL.md) | Create and edit Word documents with formatting |
| [pptx](document-handling/pptx/SKILL.md) | Build PowerPoint presentations with slides and layouts |
| [xlsx](document-handling/xlsx/SKILL.md) | Generate Excel spreadsheets with formulas and charts |

### Development

Tools for building software - MCP servers for Claude integration, web application testing.

| Skill | Description |
|-------|-------------|
| [mcp-builder](development/mcp-builder/SKILL.md) | Build Model Context Protocol servers with Claude integration |
| [webapp-testing](development/webapp-testing/SKILL.md) | Test web applications with Playwright and Chrome DevTools |

### Content & Design

Create visual content - UI components, design systems, diagrams, and generative art.

| Skill | Description |
|-------|-------------|
| [frontend-design](content-design/frontend-design/SKILL.md) | Design and implement modern web UI components |
| [theme-factory](content-design/theme-factory/SKILL.md) | Create comprehensive design systems and themes |
| [canvas-design](content-design/canvas-design/SKILL.md) | Create diagrams, graphics, and visualizations with canvas |
| [algorithmic-art](content-design/algorithmic-art/SKILL.md) | Generate algorithmic and generative art with code |

### Communication

Business communications - internal memos, Slack engagement, collaborative editing, brand identity.

| Skill | Description |
|-------|-------------|
| [internal-comms](communication/internal-comms/SKILL.md) | Craft professional internal business communications |
| [slack-gif-creator](communication/slack-gif-creator/SKILL.md) | Create custom animated GIFs for Slack |
| [doc-coauthoring](communication/doc-coauthoring/SKILL.md) | Collaborate on documents with tracked changes |
| [brand-guidelines](communication/brand-guidelines/SKILL.md) | Create and maintain brand guidelines |

### Builders

Meta-tools for creating things - interactive web applications and new skills.

| Skill | Description |
|-------|-------------|
| [web-artifacts-builder](builders/web-artifacts-builder/SKILL.md) | Build self-contained interactive web applications |
| [skill-creator](builders/skill-creator/SKILL.md) | Create new Claude Code skills |

### Workspace Hub

Specialized for workspace-hub ecosystem - repository management, development methodology, AI orchestration.

| Skill | Description |
|-------|-------------|
| [repo-sync](workspace-hub/repo-sync/SKILL.md) | Manage and synchronize 26+ Git repositories |
| [sparc-workflow](workspace-hub/sparc-workflow/SKILL.md) | Apply SPARC methodology for systematic development |
| [agent-orchestration](workspace-hub/agent-orchestration/SKILL.md) | Orchestrate AI agents with Claude Flow swarms |
| [compliance-check](workspace-hub/compliance-check/SKILL.md) | Verify coding standards and workspace compliance |
| [workspace-cli](workspace-hub/workspace-cli/SKILL.md) | Use the unified workspace-hub CLI |

### Tools

Assessment and utility skills.

| Skill | Description |
|-------|-------------|
| [ai-tool-assessment](tools/ai-tool-assessment/SKILL.md) | Assess AI tool subscriptions, usage, and cost-effectiveness |

---

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

---

## Repository-Specific Skills

Individual repositories can have their own skills that supplement these global skills.

### Creating Repo-Specific Skills

1. Create a `.claude/skills/` directory in your repository
2. Add skill subdirectories with `SKILL.md` files
3. Skills will be available only when working in that repository

**Example:**
```
digitalmodel/
└── .claude/
    └── skills/
        └── structural-analysis/
            └── SKILL.md
```

For detailed guidance, see [REPO_SPECIFIC_SKILLS.md](../../docs/modules/ai/REPO_SPECIFIC_SKILLS.md).

---

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

---

## Creating New Skills

Use the [skill-creator](builders/skill-creator/SKILL.md) skill to create new skills:

1. Determine skill category
2. Create descriptive name (kebab-case)
3. Write clear trigger description
4. Include practical examples
5. Add to appropriate category directory
6. Update this index

---

## Installation Verification

Check that skills are accessible:

```bash
# Verify symlink
ls -la ~/.claude/skills

# List available categories
ls ~/.claude/skills/

# Check specific skill
cat ~/.claude/skills/document-handling/pdf/SKILL.md
```

---

## Related Documentation

- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Anthropic Official Skills](https://github.com/anthropics/skills)
- [Workspace Hub Documentation](../../docs/README.md)
- [AI Agent Guidelines](../../docs/modules/ai/AI_AGENT_GUIDELINES.md)
- [Repo-Specific Skills Guide](../../docs/modules/ai/REPO_SPECIFIC_SKILLS.md)

---

*Skills are user-level and available across all projects via symlink at `~/.claude/skills/`*
