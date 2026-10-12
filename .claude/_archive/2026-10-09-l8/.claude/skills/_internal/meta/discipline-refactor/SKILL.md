---
name: discipline-refactor
description: Reorganize any repository by discipline/domain with module-based structure.
  Code in src/<pkg>/modules/, documents in <folder>/modules/. Orchestrates Explore,
  Plan, and general-purpose subagents. Works standalone.
version: 2.0.0
category: _internal
triggers:
- refactor by discipline
- organize by domain
- restructure repository
- module-based organization
- discipline-based organization
prerequisites: none
standalone: true
calls_skills:
- skill-creator
- git-sync-manager
- parallel-batch-executor
calls_subagents:
- Explore
- Plan
- general-purpose
- Bash
tags: []
see_also:
- discipline-refactor-core-principles
- discipline-refactor-target-repository-structure
- discipline-refactor-orchestration-architecture
- discipline-refactor-phase-1-analysis
- discipline-refactor-phase-2-planning
- discipline-refactor-phase-3-execution
- discipline-refactor-phase-4-validation
- discipline-refactor-standard-folders-module-structure
- discipline-refactor-how-to-identify-disciplines
- discipline-refactor-python-package
- discipline-refactor-rollback
- discipline-refactor-verification-checklist
---

# Discipline Refactor

## Sub-Skills

- [Core Principles](core-principles/SKILL.md)
- [Target Repository Structure](target-repository-structure/SKILL.md)
- [Orchestration Architecture](orchestration-architecture/SKILL.md)
- [Phase 1: Analysis](phase-1-analysis/SKILL.md)
- [Phase 2: Planning](phase-2-planning/SKILL.md)
- [Phase 3: Execution](phase-3-execution/SKILL.md)
- [Phase 4: Validation](phase-4-validation/SKILL.md)
- [Standard Folders → Module Structure (+1)](standard-folders-module-structure/SKILL.md)
- [How to Identify Disciplines](how-to-identify-disciplines/SKILL.md)
- [Python Package (+1)](python-package/SKILL.md)
- [Rollback](rollback/SKILL.md)
- [Verification Checklist](verification-checklist/SKILL.md)
