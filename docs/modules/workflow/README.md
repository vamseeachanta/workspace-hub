# Development Workflow Documentation

This directory contains all documentation related to the development workflow, from requirements to implementation.

## Contents

| File | Description |
|------|-------------|
| [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) | Main workflow guide - 6-phase process |
| [DEVELOPMENT_WORKFLOW_GUIDELINES.md](DEVELOPMENT_WORKFLOW_GUIDELINES.md) | Detailed workflow standards |
| [DEVELOPMENT_WORKFLOW_SUMMARY.md](DEVELOPMENT_WORKFLOW_SUMMARY.md) | Quick reference summary |
| [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) | Implementation planning guide |

## Workflow Overview

The development workflow follows 6 phases:

```
1. User Prompt     → user_prompt.md (user-edited only)
2. YAML Config     → config/input/*.yaml (AI generates)
3. Pseudocode      → docs/pseudocode/*.md (AI generates, user approves)
4. TDD             → tests/ (write tests first)
5. Implementation  → src/ (make tests pass)
6. Bash Execution  → scripts/ (single command entry point)
```

## Quick Start

1. **Read** [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) for the complete process
2. **Reference** [DEVELOPMENT_WORKFLOW_GUIDELINES.md](DEVELOPMENT_WORKFLOW_GUIDELINES.md) for detailed standards
3. **Use** templates in `/templates/` for consistent structure

## Key Principles

- **User controls requirements** - Only users edit `user_prompt.md`
- **AI asks questions** - Clarify before implementing
- **YAML drives configuration** - Structured, machine-readable specs
- **Pseudocode before code** - Algorithm review before implementation
- **TDD mandatory** - Write failing tests first
- **Bash execution** - Single command entry points

## Related Documentation

- [AI Guidelines](../ai/) - AI agent workflow rules
- [Standards](../standards/) - Coding and compliance standards
- [Templates](../../templates/) - Workflow templates

---

*Part of the workspace-hub documentation infrastructure*
