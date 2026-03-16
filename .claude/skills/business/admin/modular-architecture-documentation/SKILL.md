---
name: modular-architecture-documentation
version: 1.0.0
category: business
description: Systematically document multi-module system architectures including module
  boundaries, CLI commands, and architecture decisions.
tags: []
scripts_exempt: true
see_also:
- modular-architecture-documentation-1-module-definition-framework
- modular-architecture-documentation-decision
- modular-architecture-documentation-tech-stackmd-modular-architecture-section
- modular-architecture-documentation-overview
- modular-architecture-documentation-decision
- modular-architecture-documentation-overview
- modular-architecture-documentation-decision
- modular-architecture-documentation-success-criteria
---

# Modular Architecture Documentation

## Overview

This skill provides a systematic approach to documenting multi-module system architectures, including module boundary definition, CLI command specification, shared component identification, and architecture decision documentation following Agent OS decisions.md patterns.

## When to Use

Use this skill when:
- Documenting modular architecture in tech-stack.md
- Implementing multi-module systems with independent CLI commands
- Defining module boundaries and responsibilities
- Identifying shared vs. module-specific components
- Documenting pyproject.toml entry points for modules
- Recording architecture decisions in decisions.md
- Ensuring module independence and cohesion
- Planning gradual feature adoption (Phase 1: Module A, Phase 2: Module B)

## Related Skills

- **Product Documentation Modernization** - For documenting architecture in tech-stack.md
- **Technology Stack Modernization** - For pyproject.toml configuration
- **Workspace-Hub Standards Compliance** - For ensuring architectural compliance

## References

### Architecture Patterns

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Modular Monolith](https://www.kamilgrzybek.com/blog/posts/modular-monolith-primer)
- [Python Application Layouts](https://realpython.com/python-application-layouts/)
### CLI Design

- [Click Documentation](https://click.palletsprojects.com/)
- [CLI Best Practices](https://clig.dev/)
### Agent OS Resources

- Agent OS Documentation: mission.md, tech-stack.md, roadmap.md, decisions.md
- Agent OS Decision Template: decisions.md format

## Version History

- **1.0.0** (2026-01-08): Initial release - comprehensive modular architecture documentation skill

## Sub-Skills

- [Example: 3-Module Invoice/Tax System](example-3-module-invoicetax-system/SKILL.md)
- [Module Naming (+4)](module-naming/SKILL.md)

## Sub-Skills

- [1. Module Definition Framework (+9)](1-module-definition-framework/SKILL.md)
- [Decision (+5)](decision/SKILL.md)
- [Tech-Stack.md Modular Architecture Section](tech-stackmd-modular-architecture-section/SKILL.md)
- [Overview (+7)](overview/SKILL.md)
- [Decision (+6)](decision/SKILL.md)
- [Overview (+6)](overview/SKILL.md)
- [Decision (+6)](decision/SKILL.md)
- [Success Criteria](success-criteria/SKILL.md)
