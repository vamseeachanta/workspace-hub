---
name: repo-readiness
description: Prepare any repository for new work by analyzing CLAUDE.md, file structure,
  mission/objectives, and establishing work readiness state. Auto-executes before
  new tasks to provide context.
version: 1.0.0
category: coordination
type: skill
trigger: pre-task
auto_execute: true
capabilities:
- claude_config_analysis
- structure_assessment
- mission_extraction
- context_preparation
- work_readiness_validation
tools:
- Read
- Glob
- Grep
- Bash
related_skills:
- compliance-check
- repo-sync
- sparc-workflow
requires: []
see_also:
- repo-readiness-1-configuration-analysis
- repo-readiness-claudemd-status-found
- repo-readiness-directory-organization-compliant
- repo-readiness-project-purpose
- repo-readiness-git-status-clean
- repo-readiness-logging-standards-compliant
- repo-readiness-key-conventions
- repo-readiness-overall-readiness-score
- repo-readiness-breakdown
- repo-readiness-execution-checklist
- repo-readiness-pre-task-hook
- repo-readiness-1-check-readiness-script
- repo-readiness-missing-configuration
- repo-readiness-performance-metrics
- repo-readiness-with-sparc-workflow
tags: []
---

# Repo Readiness

## Quick Start

```bash
# Manual trigger
/repo-readiness

# Auto-triggers before:
# - New task execution
# - Feature development
# - SPARC workflow initiation
# - Agent assignment

# Direct check
./scripts/check_repo_readiness.sh <repo-name>
```

## When to Use

**AUTO-EXECUTES (via hook):**
- Before starting any new task in a repository
- When switching to a different repository
- Before SPARC specification phase
- Before agent assignment for new work

**MANUAL TRIGGER:**
- When repository context is unclear
- Before major refactoring
- After long breaks from a repository
- When onboarding to an existing project
- Before cross-repo coordination

## Prerequisites

- Repository is cloned locally
- Git is initialized
- Read access to repository files
- (Optional) Internet for external documentation lookup

## Overview

The repo-readiness skill performs comprehensive analysis of a repository to establish complete work context before executing any new tasks. It replaces manual context gathering with automated, systematic preparation.
### What It Analyzes

1. **Configuration**: CLAUDE.md, .claude/*, .agent-os/*
2. **Structure**: Directory organization, module architecture
3. **Mission**: Product vision, objectives, technical decisions
4. **State**: Git status, dependencies, environment setup
5. **Standards**: Compliance with workspace-hub standards
6. **Context**: Historical decisions, conventions, patterns
### Output

Generates a comprehensive readiness report with:
- Configuration summary
- Structure analysis
- Mission & objectives extraction
- Readiness assessment (✅ Ready / ⚠️ Needs Attention / ❌ Not Ready)
- Recommended actions
- Context for AI agents

## Related Skills

- [compliance-check](../compliance-check/SKILL.md) - Standards validation
- [repo-sync](../repo-sync/SKILL.md) - Multi-repo management
- [sparc-workflow](../sparc-workflow/SKILL.md) - Development methodology
- [session-start-routine](../../meta/session-start-routine/SKILL.md) - Session initialization

## References

- [FILE_ORGANIZATION_STANDARDS.md](../../../docs/modules/standards/FILE_ORGANIZATION_STANDARDS.md)
- [AI_AGENT_GUIDELINES.md](../../../docs/modules/ai/AI_AGENT_GUIDELINES.md)
- [DEVELOPMENT_WORKFLOW.md](../../../docs/modules/workflow/DEVELOPMENT_WORKFLOW.md)
- [CLAUDE.md](../../../CLAUDE.md) - Root configuration template

---

## Version History

- **1.0.0** (2026-01-07): Initial release - comprehensive repository readiness skill with configuration analysis, structure assessment, mission extraction, state checking, standards compliance, auto-hook integration, bulk checking capabilities, error handling, and metrics tracking

## Sub-Skills

- [1. Run Before Every New Task (+4)](1-run-before-every-new-task/SKILL.md)

## Sub-Skills

- [1. Configuration Analysis](1-configuration-analysis/SKILL.md)
- [CLAUDE.md Status: ✅ Found (+3)](claudemd-status-found/SKILL.md)
- [Directory Organization: ✅ Compliant (+4)](directory-organization-compliant/SKILL.md)
- [Project Purpose (+4)](project-purpose/SKILL.md)
- [Git Status: ✅ Clean (+3)](git-status-clean/SKILL.md)
- [Logging Standards: ✅ Compliant (+4)](logging-standards-compliant/SKILL.md)
- [Key Conventions (+4)](key-conventions/SKILL.md)
- [Overall Readiness Score (+1)](overall-readiness-score/SKILL.md)
- [Breakdown (+2)](breakdown/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Pre-Task Hook (+1)](pre-task-hook/SKILL.md)
- [1. Check Readiness Script (+1)](1-check-readiness-script/SKILL.md)
- [Missing Configuration (+4)](missing-configuration/SKILL.md)
- [Performance Metrics (+2)](performance-metrics/SKILL.md)
- [With SPARC Workflow (+3)](with-sparc-workflow/SKILL.md)
