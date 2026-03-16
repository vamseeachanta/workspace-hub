---
name: agent-os-framework
description: Generate standardized .agent-os directory structure with product documentation,
  mission, tech-stack, roadmap, and decision records. Enables AI-native workflows.
version: 1.0.0
category: coordination
type: skill
trigger: manual
auto_execute: false
capabilities:
- product_documentation
- mission_definition
- tech_stack_documentation
- roadmap_planning
- decision_records
tools:
- Write
- Read
- Bash
related_skills:
- repo-readiness
- python-project-template
requires: []
see_also:
- agent-os-framework-directory-structure
- agent-os-framework-1-missionmd
- agent-os-framework-product-pitch
- agent-os-framework-primary-users
- agent-os-framework-before-this-product
- agent-os-framework-success-metrics
- agent-os-framework-what-makes-this-unique
- agent-os-framework-2-tech-stackmd
- agent-os-framework-python-311
- agent-os-framework-development-tools
- agent-os-framework-version-control
- agent-os-framework-data-storage
- agent-os-framework-apis
- agent-os-framework-why-python
- agent-os-framework-vision
- agent-os-framework-current-phase
- agent-os-framework-phase-overview
- agent-os-framework-phase-1-foundation
- agent-os-framework-milestones
- agent-os-framework-risks-and-mitigations
- agent-os-framework-external
- agent-os-framework-how-to-use-this-document
- agent-os-framework-dec-xxx-decision-title
- agent-os-framework-dec-001-package-manager-selection
- agent-os-framework-dec-004-pending-decision-title
- agent-os-framework-execution-checklist
tags: []
---

# Agent Os Framework

## Quick Start

```bash
# Generate full .agent-os structure
/agent-os-framework

# Generate for existing project
/agent-os-framework --update

# Generate specific component
/agent-os-framework --component mission
```

## When to Use

**USE when:**
- Setting up new repository
- Adding AI workflow support
- Documenting product vision
- Creating decision records

**DON'T USE when:**
- Project has complete .agent-os
- Non-product repositories (e.g., dotfiles)

## Prerequisites

- Repository initialized with git
- Basic project understanding
- Stakeholder input for mission

## Overview

Creates complete .agent-os structure:

1. **product/** - Core product documentation
2. **specs/** - Feature specifications
3. **standards/** - Code style guidelines
4. **instructions/** - Workflow instructions

## Overview

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| Language | Python | 3.11+ | Primary development |
| Package Manager | UV | Latest | Fast dependency management |
| Testing | pytest | 7.4+ | Test framework |
| Visualization | Plotly | 5.15+ | Interactive charts |
| Data | Pandas | 2.0+ | Data processing |

## Related Skills

- [repo-readiness](../repo-readiness/SKILL.md) - Validates .agent-os
- [python-project-template](../python-project-template/SKILL.md) - Creates initial structure

## References

- [Agent OS Framework](https://buildermethods.com/agent-os)
- [workspace-hub Standards](../../../docs/modules/standards/)

---

## Version History

- **1.0.0** (2026-01-14): Initial release - .agent-os framework with mission, tech-stack, roadmap, and decisions

## Sub-Skills

- [Example 1: New Project Setup (+1)](example-1-new-project-setup/SKILL.md)
- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Directory Structure](directory-structure/SKILL.md)
- [1. mission.md](1-missionmd/SKILL.md)
- [Product Pitch](product-pitch/SKILL.md)
- [Primary Users (+1)](primary-users/SKILL.md)
- [Before This Product (+1)](before-this-product/SKILL.md)
- [Success Metrics](success-metrics/SKILL.md)
- [What Makes This Unique (+1)](what-makes-this-unique/SKILL.md)
- [2. tech-stack.md](2-tech-stackmd/SKILL.md)
- [Python 3.11+ (+4)](python-311/SKILL.md)
- [Development Tools](development-tools/SKILL.md)
- [Version Control (+1)](version-control/SKILL.md)
- [Data Storage](data-storage/SKILL.md)
- [APIs (+1)](apis/SKILL.md)
- [Why Python? (+3)](why-python/SKILL.md)
- [Vision](vision/SKILL.md)
- [Current Phase](current-phase/SKILL.md)
- [Phase Overview](phase-overview/SKILL.md)
- [Phase 1: Foundation ✅ (+4)](phase-1-foundation/SKILL.md)
- [Milestones](milestones/SKILL.md)
- [Risks and Mitigations](risks-and-mitigations/SKILL.md)
- [External (+2)](external/SKILL.md)
- [How to Use This Document](how-to-use-this-document/SKILL.md)
- [DEC-XXX: [Decision Title]](dec-xxx-decision-title/SKILL.md)
- [DEC-001: Package Manager Selection (+2)](dec-001-package-manager-selection/SKILL.md)
- [DEC-004: [Pending Decision Title]](dec-004-pending-decision-title/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
