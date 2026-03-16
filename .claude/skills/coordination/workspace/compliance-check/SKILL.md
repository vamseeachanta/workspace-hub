---
name: compliance-check
description: Verify and enforce coding standards, AI guidelines, and workspace compliance
  across repositories. Use for standards propagation, compliance verification, and
  enforcing development best practices.
version: 1.1.0
category: coordination
type: skill
capabilities:
- standards_verification
- compliance_propagation
- git_hooks_management
- ci_cd_integration
- code_quality_enforcement
tools:
- Bash
- Read
- Write
- Glob
- Grep
related_skills:
- repo-sync
- sparc-workflow
- workspace-cli
requires: []
see_also:
- compliance-check-1-ai-agent-guidelines
- compliance-check-quick-compliance-check
- compliance-check-execution-checklist
- compliance-check-repository-structure
- compliance-check-testing-standards
- compliance-check-logging-standards
- compliance-check-html-reporting
- compliance-check-ai-guidelines
- compliance-check-ai-compliance
- compliance-check-propagate-claudemd-configuration
- compliance-check-install-compliance-hooks
- compliance-check-common-compliance-failures
- compliance-check-metrics-success-criteria
- compliance-check-generate-compliance-report
- compliance-check-cicd-integration
- compliance-check-with-repository-sync
tags: []
---

# Compliance Check

## Quick Start

```bash
# Quick compliance check
./scripts/compliance/verify_compliance.sh

# Check specific repository
./scripts/compliance/verify_compliance.sh --repo=digitalmodel

# Propagate standards to all repos
./scripts/compliance/propagate_claude_config.py
```

## When to Use

- Setting up a new repository that needs workspace standards
- Verifying all repos meet coding and documentation standards
- Propagating updated guidelines across the workspace
- Installing pre-commit hooks for enforcement
- Auditing compliance before releases

## Prerequisites

- Access to workspace-hub compliance scripts
- Write access to target repositories
- Python 3.x for propagation scripts
- Git for hook installation

## Overview

This skill ensures consistent coding standards, AI usage guidelines, and development practices across all workspace-hub repositories. It covers verification, propagation, and enforcement of compliance requirements.

## References

- [AI Agent Guidelines](../docs/modules/ai/AI_AGENT_GUIDELINES.md)
- [Development Workflow](../docs/modules/workflow/DEVELOPMENT_WORKFLOW.md)
- [File Organization Standards](../docs/modules/standards/FILE_ORGANIZATION_STANDARDS.md)
- [Testing Standards](../docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md)
- [Logging Standards](../docs/modules/standards/LOGGING_STANDARDS.md)
- [HTML Reporting Standards](../docs/modules/standards/HTML_REPORTING_STANDARDS.md)

---

## Version History

- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format - added Quick Start, When to Use, Execution Checklist, Error Handling consolidation, Metrics, Integration Points
- **1.0.0** (2024-10-15): Initial release with compliance verification, propagation tools, git hooks, CI/CD integration, troubleshooting

## Sub-Skills

- [For Repository Maintainers (+2)](for-repository-maintainers/SKILL.md)

## Sub-Skills

- [1. AI Agent Guidelines (+3)](1-ai-agent-guidelines/SKILL.md)
- [Quick Compliance Check (+2)](quick-compliance-check/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Repository Structure](repository-structure/SKILL.md)
- [Testing Standards](testing-standards/SKILL.md)
- [Logging Standards](logging-standards/SKILL.md)
- [HTML Reporting](html-reporting/SKILL.md)
- [AI Guidelines](ai-guidelines/SKILL.md)
- [AI Compliance](ai-compliance/SKILL.md)
- [Propagate CLAUDE.md Configuration (+2)](propagate-claudemd-configuration/SKILL.md)
- [Install Compliance Hooks (+2)](install-compliance-hooks/SKILL.md)
- [Common Compliance Failures (+2)](common-compliance-failures/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [Generate Compliance Report (+1)](generate-compliance-report/SKILL.md)
- [CI/CD Integration (+1)](cicd-integration/SKILL.md)
- [With Repository Sync (+2)](with-repository-sync/SKILL.md)
