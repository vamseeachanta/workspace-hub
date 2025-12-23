---
name: repo-sync
description: Manage and synchronize multiple Git repositories across workspace-hub. Use for bulk git operations, repository status checks, branch management, and coordinated commits across 26+ repositories.
---

# Repository Sync Skill

## Overview

This skill enables efficient management of multiple Git repositories in the workspace-hub ecosystem. It provides tools for bulk operations, status monitoring, and coordinated synchronization across all repositories.

## Quick Reference

### Common Commands

```bash
# List all repositories
./scripts/repository_sync list all

# Check status of all repos
./scripts/repository_sync status all

# Pull latest from all repos
./scripts/repository_sync pull all

# Commit and push all repos
./scripts/repository_sync sync all -m "Update message"

# Work with specific category
./scripts/repository_sync pull work
./scripts/repository_sync sync personal -m "Personal updates"
```

## Repository Categories

### Work Repositories

Business and client projects:
- `digitalmodel` - Digital model platform
- `energy` - Energy analysis tools
- `frontierdeepwater` - Deepwater engineering
- `aceengineer-admin` - Admin platform
- `aceengineer-website` - Company website

### Personal Repositories

Personal projects and experiments:
- Side projects
- Learning repositories
- Personal tools

### Viewing Categories

```bash
# List work repos
./scripts/repository_sync list work

# List personal repos
./scripts/repository_sync list personal

# List all repos
./scripts/repository_sync list all
```

## Core Operations

### 1. Status Check

View the state of all repositories:

```bash
./scripts/repository_sync status all
```

**Output indicators:**
- 🟢 **Clean**: No changes, up to date
- 🔴 **Uncommitted**: Has local changes
- 🟣 **Unpushed**: Has commits not pushed
- 🔵 **Behind**: Remote has updates
- 🟡 **Not cloned**: Repository missing locally

### 2. Pull Operations

Fetch and merge from remote:

```bash
# Pull all repositories
./scripts/repository_sync pull all

# Pull only work repos
./scripts/repository_sync pull work

# Pull specific repo
./scripts/repository_sync pull digitalmodel
```

### 3. Commit Operations

Stage and commit changes:

```bash
# Commit all with default message
./scripts/repository_sync commit all

# Commit with custom message
./scripts/repository_sync commit all -m "Update dependencies"

# Commit work repos only
./scripts/repository_sync commit work -m "Weekly sync"
```

### 4. Push Operations

Push committed changes to remote:

```bash
# Push all repositories
./scripts/repository_sync push all

# Push work repos
./scripts/repository_sync push work
```

### 5. Full Sync (Commit + Push)

Complete synchronization in one command:

```bash
# Sync all repos
./scripts/repository_sync sync all -m "End of day sync"

# Sync work repos
./scripts/repository_sync sync work -m "Client updates"
```

## Branch Management

### List Branches

```bash
# Show branches in all repos
./scripts/repository_sync branches all

# Show branches in work repos
./scripts/repository_sync branches work
```

### Fetch Remote Branches

Track all remote branches locally:

```bash
./scripts/repository_sync fetch-branches all
```

### Sync with Main

Update feature branches with main:

```bash
# Merge main into current branches
./scripts/repository_sync sync-main all

# Rebase instead of merge
./scripts/repository_sync sync-main all --rebase
```

### Switch Branches

Switch all repos to a specific branch:

```bash
# Switch to main
./scripts/repository_sync switch all main

# Switch to feature branch
./scripts/repository_sync switch work feature/new-design
```

## Configuration

### Repository URLs

Configure in `config/repos.conf`:

```bash
# Repository URL Configuration
digitalmodel=git@github.com:username/digitalmodel.git
energy=git@github.com:username/energy.git
aceengineer-admin=git@github.com:username/aceengineer-admin.git
```

### Categories

Defined in `.gitignore`:

```bash
digitalmodel/        # Work
energy/              # Work
personal-project/    # Personal
mixed-repo/          # Work, Personal
```

### Configure Repositories

```bash
# Edit configuration
./scripts/repository_sync config

# Refresh repository list
./scripts/repository_sync refresh
```

## Workflows

### Daily Development Workflow

```bash
# Morning: Pull latest
./scripts/repository_sync pull all

# During day: Work on code...

# End of day: Sync everything
./scripts/repository_sync sync all -m "$(date +%Y-%m-%d) updates"
```

### Feature Branch Workflow

```bash
# Start feature in all work repos
./scripts/repository_sync switch work feature/new-feature

# Develop across repos...

# Keep in sync with main
./scripts/repository_sync sync-main work

# Push feature branches
./scripts/repository_sync push work

# Return to main
./scripts/repository_sync switch work main
```

### Release Workflow

```bash
# Create release branch
./scripts/repository_sync switch work release/v1.2.0

# Final sync and push
./scripts/repository_sync sync work -m "Release v1.2.0 preparation"

# After merge, back to main
./scripts/repository_sync switch work main
./scripts/repository_sync pull work
```

## Batch Operations

### Selective Operations

Target specific repositories:

```bash
# Multiple specific repos
./scripts/repository_sync sync digitalmodel energy -m "Update"

# Pattern-based (if supported)
./scripts/repository_sync sync "ace*" -m "Ace project updates"
```

### Parallel Execution

For faster operations on many repos:

```bash
# Built-in parallelization
./scripts/repository_sync pull all --parallel

# Or using xargs
ls -d */ | xargs -P 4 -I {} git -C {} pull
```

## Error Handling

### Merge Conflicts

When conflicts occur:

```bash
# Status will show conflicts
./scripts/repository_sync status all

# Resolve manually in affected repo
cd affected-repo
git status
# Fix conflicts...
git add .
git commit -m "Resolve conflicts"

# Continue with other repos
./scripts/repository_sync sync all
```

### Stale Branches

Clean up old branches:

```bash
# List stale remote-tracking branches
git remote prune origin --dry-run

# Prune stale branches
git remote prune origin
```

### Recovery

If things go wrong:

```bash
# Reset to remote state
cd repo-name
git fetch origin
git reset --hard origin/main

# Or restore from backup
git reflog
git reset --hard HEAD@{2}
```

## Integration

### With Workspace CLI

```bash
# Launch interactive menu
./scripts/workspace

# Navigate: Repository Management → Repository Sync Manager
```

### With AI Agents

Agents can use repository sync for:
- Coordinated code changes
- Cross-repo refactoring
- Synchronized releases
- Documentation updates

## Best Practices

### Commit Messages

Use consistent format:

```
[scope] action: description

Examples:
[all] update: Dependency refresh
[work] fix: Security patches
[docs] add: API documentation
```

### Frequency

- **Pull**: Start of each work session
- **Commit**: After completing logical units
- **Push**: End of work session or before breaks
- **Sync**: Daily minimum

### Verification

Always verify before pushing:

```bash
# Check what will be pushed
./scripts/repository_sync status all

# Review specific repo changes
cd repo-name && git diff origin/main
```

## Troubleshooting

### Authentication Issues

```bash
# Verify SSH key
ssh -T git@github.com

# Check credential helper
git config --global credential.helper
```

### Network Issues

```bash
# Test connectivity
git ls-remote origin

# Use HTTPS fallback
git remote set-url origin https://github.com/user/repo.git
```

### Permission Denied

```bash
# Check file permissions
ls -la .git/

# Fix permissions
chmod -R u+rwX .git/
```

## Related Documentation

- [Workspace CLI](../docs/modules/cli/WORKSPACE_CLI.md)
- [Repository Sync Documentation](../docs/modules/cli/REPOSITORY_SYNC.md)
- [Development Workflow](../docs/modules/workflow/DEVELOPMENT_WORKFLOW.md)
