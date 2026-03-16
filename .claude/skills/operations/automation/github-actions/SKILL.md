---
name: github-actions
version: 1.0.0
description: CI/CD automation and workflow orchestration using GitHub Actions for
  builds, tests, deployments, and repository automation
author: workspace-hub
category: operations
type: skill
capabilities:
- ci_cd_pipelines
- matrix_builds
- reusable_workflows
- composite_actions
- artifact_management
- secret_management
- environment_deployments
- scheduled_automation
tools:
- github-cli
- act
- yaml-lint
tags:
- github
- actions
- ci-cd
- automation
- workflows
- devops
- pipelines
- testing
- deployment
platforms:
- github
- linux
- macos
- windows
related_skills:
- yaml-configuration
- bash-cli-framework
- git-sync-manager
requires: []
see_also:
- github-actions-whats-changed
- github-actions-5-reusable-workflows
scripts_exempt: true
---

# Github Actions

## When to Use This Skill

### USE when:

- Building CI/CD pipelines for GitHub repositories
- Automating tests across multiple OS/language versions
- Creating release and deployment workflows
- Publishing packages to npm, PyPI, Docker Hub
- Automating issue triage and PR management
- Scheduling periodic maintenance tasks
- Building reusable workflow components
- Implementing GitOps deployment patterns
### DON'T USE when:

- Repository not hosted on GitHub (use Jenkins, GitLab CI)
- Need complex DAG-based workflow orchestration (use Airflow)
- Require visual workflow design (use n8n, Activepieces)
- Self-hosted runners not available for compute-intensive tasks
- Need real-time event processing (use dedicated message queues)

## Prerequisites

### GitHub Repository Setup

```bash
# Create workflow directory
mkdir -p .github/workflows

# Verify GitHub CLI installed
gh --version

# Authenticate with GitHub
gh auth login

# Check workflow permissions
gh api repos/{owner}/{repo}/actions/permissions
```
### Local Testing with act

```bash
# Install act for local workflow testing
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Verify installation
act --version

*See sub-skills for full details.*
### Workflow Linting

```bash
# Install actionlint
brew install actionlint   # macOS
go install github.com/rhysd/actionlint/cmd/actionlint@latest  # Go

# Lint workflows
actionlint .github/workflows/*.yml

# YAML validation
pip install yamllint
yamllint .github/workflows/
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-17 | Initial release with comprehensive CI/CD patterns |

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [act - Local Testing](https://github.com/nektos/act)
- [actionlint - Workflow Linter](https://github.com/rhysd/actionlint)

---

*This skill provides production-ready patterns for GitHub Actions workflows, tested across multiple repositories and CI/CD pipelines.*

## Sub-Skills

- [1. Basic Workflow Structure](1-basic-workflow-structure/SKILL.md)
- [2. Matrix Builds for Cross-Platform Testing](2-matrix-builds-for-cross-platform-testing/SKILL.md)
- [3. Caching Strategies (+1)](3-caching-strategies/SKILL.md)
- [Integration with Slack Notifications (+1)](integration-with-slack-notifications/SKILL.md)
- [1. Security Best Practices (+3)](1-security-best-practices/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)

## Sub-Skills

- [What's Changed](whats-changed/SKILL.md)
- [5. Reusable Workflows (+5)](5-reusable-workflows/SKILL.md)
