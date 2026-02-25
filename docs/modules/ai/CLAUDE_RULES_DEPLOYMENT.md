# Claude Rules Deployment Guide

## Overview

This guide explains how to deploy and maintain the unified Claude rules across all repositories in the workspace-hub ecosystem.

## What Changed

### Integrated Rule Sets

The unified `CLAUDE.md` now combines three complementary rule sets:

1. **Part 1: Core Engineering Principles** (from obra's dotfiles)
   - Test-Driven Development (TDD) methodology
   - YAGNI and simplicity principles
   - Code quality standards (naming, comments, documentation)
   - Systematic debugging framework
   - Collaboration and communication guidelines

2. **Part 2: AI Orchestration** (existing workspace-hub rules)
   - SPARC methodology integration
   - Claude Flow and agent coordination
   - Parallel execution patterns
   - File organization standards
   - HTML reporting requirements

3. **Part 3: Project-Specific Context** (Agent OS)
   - Product mission and architecture
   - Development roadmap
   - Project-specific standards
   - Workflow instructions

### Files Updated

- `/mnt/github/workspace-hub/CLAUDE.md` - Root configuration
- `/mnt/github/workspace-hub/.claude/CLAUDE.md` - Claude Code specific
- Backups created: `CLAUDE.md.backup` in both locations

## Deployment Options

### Option 1: Manual Deployment to Specific Repository

```bash
# Copy unified rules to a specific repo
cp /mnt/github/workspace-hub/CLAUDE.md /path/to/repo/CLAUDE.md

# If repo has .claude/ directory
mkdir -p /path/to/repo/.claude
cp /mnt/github/workspace-hub/CLAUDE.md /path/to/repo/.claude/CLAUDE.md
```

### Option 2: Automated Propagation Script

```bash
# Propagate to specific repository
./modules/automation/propagate_claude_rules.sh /path/to/repo

# Propagate to all managed repositories (interactive)
./modules/automation/propagate_claude_rules.sh --all

# Dry run to preview changes
./modules/automation/propagate_claude_rules.sh --all --dry-run

# Force overwrite with backups
./modules/automation/propagate_claude_rules.sh --all --force --backup
```

### Script Options

- `-h, --help` - Show help message
- `-a, --all` - Propagate to all managed repositories
- `-d, --dry-run` - Preview changes without applying
- `-f, --force` - Overwrite without prompting
- `-b, --backup` - Create backups (default: true)
- `--no-backup` - Skip backup creation
- `-v, --verbose` - Verbose output

## Rule Precedence

When rules overlap, follow this precedence:

1. **Security/Safety**: Highest priority (universal)
2. **TDD Requirement**: MANDATORY from Part 1, non-negotiable
3. **Code Quality**: Part 1 standards for naming, comments, structure
4. **Orchestration**: Part 2 patterns for agent coordination
5. **Project-Specific**: Part 3 overrides defaults when explicitly defined

## Key Integration Points

### TDD + SPARC Workflow

- **SPARC** provides high-level feature development workflow
- **TDD** provides micro-level implementation discipline
- **Integration**: Apply TDD during SPARC's Refinement phase

### Version Control

- **Part 1**: Defines git discipline (frequent commits, WIP branches, hooks)
- **Part 2**: Provides automation tooling (command propagation, batch operations)
- **Together**: Disciplined practices + automated tools

### Code Quality

- **Part 1**: Naming conventions, comment standards, no duplication
- **Part 2**: File organization, modular design, reporting standards
- **Together**: Quality code in well-organized structure

## Validation Checklist

After deploying to a repository:

- [ ] File exists at `CLAUDE.md` in repository root
- [ ] File exists at `.claude/CLAUDE.md` (if `.claude/` directory present)
- [ ] File contains all three parts (Engineering, Orchestration, Context)
- [ ] Part 3 references appropriate product documentation
- [ ] TDD workflow is understood and will be followed
- [ ] Team aware of "push back" collaboration style

## Customization for Specific Repositories

### Project-Specific Overrides

Some repositories may need customization of Part 3 (Project-Specific Context):

1. Copy the unified template
2. Replace Part 3 with repository-specific documentation
3. Maintain Parts 1 and 2 unchanged for consistency

Example structure for custom Part 3:

```markdown
# PART 3: PROJECT-SPECIFIC CONTEXT ([REPO_NAME])

## Project Documentation

### Product Context
- **Mission:** @docs/MISSION.md
- **Architecture:** @docs/ARCHITECTURE.md
- **Roadmap:** @docs/ROADMAP.md

### Development Standards
- **Code Style:** @docs/CODE_STYLE.md
- **Testing Strategy:** @docs/TESTING.md

### Workflow Instructions

[Repository-specific workflow details]
```

## Maintenance

### Keeping Rules Updated

1. **Source of Truth**: `/mnt/github/workspace-hub/CLAUDE.md`
2. **Update Process**:
   - Edit source file in workspace-hub
   - Test changes locally
   - Propagate to other repositories using script
   - Document changes in git commit

### Monitoring Compliance

Periodically check that repositories:
- Have current version of unified rules
- Follow TDD discipline
- Maintain code quality standards
- Use parallel execution patterns

### Version History

- **v1.0.0** (2025-10-12): Initial integration of obra's rules
  - Added Part 1: Core Engineering Principles
  - Maintained Part 2: AI Orchestration
  - Preserved Part 3: Project Context
  - Created propagation script

## Troubleshooting

### Rule Conflicts

If you encounter conflicting rules:

1. Refer to Rule Precedence section above
2. Security/Safety rules always win
3. TDD is non-negotiable from Part 1
4. For other conflicts, consult team lead

### Deployment Issues

**Problem**: Script can't find repositories
**Solution**: Ensure repositories have `.git` directory and are under `/mnt/github`

**Problem**: Backup files accumulating
**Solution**: Backups include timestamp, clean up old ones periodically

**Problem**: Repository-specific customization lost
**Solution**: Use `--dry-run` first, maintain custom Part 3 separately

## Examples

### Deploy to New Repository

```bash
# 1. Clone/create repository
git clone <repo-url> /path/to/new-repo

# 2. Deploy unified rules
./modules/automation/propagate_claude_rules.sh /path/to/new-repo

# 3. Customize Part 3 if needed
nano /path/to/new-repo/CLAUDE.md

# 4. Commit
cd /path/to/new-repo
git add CLAUDE.md .claude/CLAUDE.md
git commit -m "Add unified Claude rules with TDD and SPARC methodology"
```

### Update Existing Repositories

```bash
# 1. Dry run to preview
./modules/automation/propagate_claude_rules.sh --all --dry-run

# 2. Review output, ensure no custom Part 3 will be lost

# 3. Execute with backups
./modules/automation/propagate_claude_rules.sh --all --backup

# 4. Verify updates
git diff /path/to/repo/CLAUDE.md
```

### Repository-Specific Deployment

```bash
# Deploy to specific repos only
./modules/automation/propagate_claude_rules.sh \
    /mnt/github/repo1 \
    /mnt/github/repo2 \
    /mnt/github/repo3
```

## Additional Resources

- **Integration Plan**: `docs/CLAUDE_RULES_INTEGRATION_PLAN.md`
- **Original obra rules**: https://github.com/obra/dotfiles
- **SPARC Documentation**: `docs/AI_AGENT_ORCHESTRATION.md`
- **Agent OS Standards**: `@~/.agent-os/standards/`

## Support

For questions or issues with Claude rules deployment:

1. Check this guide and integration plan
2. Review backups to understand what changed
3. Test with `--dry-run` before applying
4. Document any issues or needed customizations

## Changelog

### 2025-10-12 - v1.0.0
- Initial integration of obra's engineering principles
- Created unified three-part rule structure
- Developed propagation script with backup support
- Updated workspace-hub with new rules
- Documented deployment and maintenance procedures
