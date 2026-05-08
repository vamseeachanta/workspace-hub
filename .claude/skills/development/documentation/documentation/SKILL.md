---
name: documentation
version: 1.0.0
category: development
description: Generate professional documentation, technical writing, and presentations
  from code using MkDocs, Sphinx, and related tools.
type: reference
tags: []
---

# Documentation

## Overview

This library contains 6 documentation-focused skills for building comprehensive documentation systems. Each skill provides patterns for generating, transforming, and publishing technical content across multiple formats and platforms.

## Quick Start

```bash
# Browse available skills
ls skills/documentation/

# Read a skill
cat skills/documentation/mkdocs/SKILL.md

# Skills are documentation - integrate patterns into your build pipelines
```

## Overview

Brief description of the topic.

## Repo Markdown Save-and-Open Workflow

When a user asks to save an answer or evidence packet in a repository Markdown file:

1. Locate or clone the target repository; if a previous partial clone is corrupt, create a clean shallow clone in a clearly named local repo directory.
2. Save the Markdown near the source evidence when there is an obvious domain folder; use a descriptive filename rather than a temporary session name.
3. Include relative links to source documents when possible, plus enough quoted evidence for the file to stand alone.
4. Verify with `wc -l` and `git status --short -- <file>` so the user knows the exact path and tracked/untracked state.
5. Open the file with VS Code using `code -g "$FILE:1"` when available; fall back to `codium -g` or report the saved path if no editor CLI exists. In Hermes terminal calls, do not append shell `&` for editor launch; use the terminal tool's background mode for long-lived GUI commands, then wait/check the process result.

## Prerequisites

- Requirement 1
- Requirement 2

## Version History

- **1.0.0** (2026-01-17): Initial release with 6 documentation skills

---

*These skills enable documentation-as-code workflows, ensuring technical content stays synchronized with codebases and deployments.*

## Sub-Skills

- [MkDocs Setup (+3)](mkdocs-setup/SKILL.md)
- [1. Docs as Code (+1)](1-docs-as-code/SKILL.md)
- [Examples](examples/SKILL.md)
- [Common Issue 1](common-issue-1/SKILL.md)

## Sub-Skills

- [Available Skills](available-skills/SKILL.md)
- [Static Site Generators (+2)](static-site-generators/SKILL.md)
- [Skill Selection Guide](skill-selection-guide/SKILL.md)
- [Project Structure (+3)](project-structure/SKILL.md)
- [Agenda](agenda/SKILL.md)
- [Docusaurus Setup](docusaurus-setup/SKILL.md)
- [Integration with Workspace-Hub](integration-with-workspace-hub/SKILL.md)
- [Step 1 (+1)](step-1/SKILL.md)
- [3. Automated API Documentation (+2)](3-automated-api-documentation/SKILL.md)
- [Testing Documentation](testing-documentation/SKILL.md)
- [Contributing](contributing/SKILL.md)
- [Related Resources](related-resources/SKILL.md)
