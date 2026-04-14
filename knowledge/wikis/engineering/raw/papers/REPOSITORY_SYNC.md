# Repository Sync Manager

> CLI tool for managing and synchronizing multiple Git repositories in workspace-hub

## Overview

The `repository_sync` script provides a command-based interface for:
- Listing all repositories (categorized as Work/Personal)
- Cloning repositories that don't exist locally
- Bulk git operations (commit, push, pull, sync) on Work or Personal repositories
- Branch management (fetch, sync with main, switch branches)
- Managing repository URLs through a configuration file

## Quick Start

### 1. Run the script

```bash
./scripts/repository_sync
```

### 2. Configure repository URLs

On first run, the script will create a template configuration file:
```
config/repos.conf
```

Edit this file to add your repository URLs:

```bash
# Example configuration
digitalmodel=git@github.com:username/digitalmodel.git
aceengineer-admin=git@github.com:username/aceengineer-admin.git
energy=git@github.com:username/energy.git
```

### 3. Use the commands

The script provides command-based operations. Basic usage:

```bash
./scripts/repository_sync <command> [scope] [options]
```

**Available commands:**
- `list` - View repository status
- `clone` - Download repositories
- `commit` - Stage and commit changes
- `push` - Upload to remote
- `pull` - Download from remote
- `sync` - Commit + push in one command
- `status` - Detailed git information
- `branches` - List all branches
- `fetch-branches` - Fetch and track remote branches
- `sync-main` - Merge/rebase main into current branch
- `switch` - Switch to specified branch
- `config` - Edit configuration
- `refresh` - Refresh repository list
- `help` - Show help message

**Scope options:**
- `all` - All repositories (default)
- `work` - Work repositories only
- `personal` - Personal repositories only
- `<repo-name>` - Specific repository

**Quick examples:**
```bash
# List all work repositories
./scripts/repository_sync list work

# Clone all personal repositories
./scripts/repository_sync clone personal

# Commit all repos with custom message
./scripts/repository_sync commit all -m "Fix critical bug"

# Full sync work repos
./scripts/repository_sync sync work
```

## Features

### Repository Discovery

The script automatically parses `.gitignore` to discover repositories and their categories:

```bash
aceengineer-admin/   # Personal
aceengineer-website/ # Personal, Work
digitalmodel/        # Work
energy/              # Work
```

Repositories are categorized as:
- **Work**: Business/client repositories
- **Personal**: Personal projects
- **Both**: Repositories that serve both purposes

### Repository Listing

View repository status with color-coded information:

```
Repository                     Category        Status       URL
--------------------------------------------------------------------------------
digitalmodel                   Work            Cloned       git@github.com:user/digitalmodel.git
aceengineer-admin              Personal        Not cloned   git@github.com:user/aceengineer-admin.git
energy                         Work            Cloned       git@github.com:user/energy.git
```

Status indicators:
- 🟢 **Cloned**: Repository exists locally
- 🟡 **Not cloned**: Repository needs to be cloned

### Bulk Cloning

Clone multiple repositories at once:

```bash
# Clone all repositories
Option 4: Clone all repositories

# Clone only work repositories
Option 5: Clone work repositories only

# Clone only personal repositories
Option 6: Clone personal repositories only
```

The script will:
- Skip repositories that already exist
- Report success/failure for each clone operation
- Provide a summary at the end

### Individual Repository Cloning

Clone a specific repository:

```bash
# Option 7: Clone specific repository

Available repositories:

 1) aceengineer-admin          [Not cloned]
 2) aceengineer-website        [Cloned]
 3) digitalmodel               [Cloned]
 4) energy                     [Not cloned]
 ...

Enter repository number (or 0 to cancel): 1
```

### Git Operations

The script provides comprehensive git operations for all repositories:

#### Commit Operations

Stage and commit all changes in repositories:

```bash
# Commit all repositories
./scripts/repository_sync commit all

# Commit work repositories with custom message
./scripts/repository_sync commit work -m "Update dependencies"

# Commit personal repositories
./scripts/repository_sync commit personal
```

**Workflow:**
1. Script checks each repository for uncommitted changes
2. Stages all changes (`git add .`)
3. Commits with the provided message (or default)
4. Skips repositories with no changes

**Commit message format:**
```
Your custom message (or default: "Update: Batch commit from repository_sync")

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

#### Push Operations

Push committed changes to remote:

```bash
# Push all repositories
./scripts/repository_sync push all

# Push work repositories only
./scripts/repository_sync push work

# Push personal repositories only
./scripts/repository_sync push personal
```

**Workflow:**
1. Checks for unpushed commits
2. Pushes to remote origin
3. Skips repositories with nothing to push
4. Reports success/failure for each repository

#### Pull Operations

Pull updates from remote:

```bash
# Pull all repositories
./scripts/repository_sync pull all

# Pull work repositories only
./scripts/repository_sync pull work

# Pull personal repositories only
./scripts/repository_sync pull personal
```

**Workflow:**
1. Pulls latest changes from remote
2. Updates local branches
3. Reports success/failure

#### Full Sync Operations

Complete synchronization (commit + push):

```bash
# Full sync all repositories
./scripts/repository_sync sync all

# Full sync work repositories with custom message
./scripts/repository_sync sync work -m "End of day sync"

# Full sync personal repositories
./scripts/repository_sync sync personal
```

**Workflow:**
1. Commits all changes (if any)
2. Pushes to remote (if needed)
3. One-command workflow for quick syncs

### Branch Management

The script provides advanced branch management across all repositories:

#### List Branches

View all branches in repositories:

```bash
# List branches in all repositories
./scripts/repository_sync branches all

# List branches in work repositories
./scripts/repository_sync branches work

# List branches in personal repositories
./scripts/repository_sync branches personal
```

**Displays:**
- Current branch (highlighted in green)
- All local branches
- Remote branches (first 5, with count of additional branches)

#### Fetch All Remote Branches

Fetch all remote branches and create local tracking branches:

```bash
# Fetch branches for all repositories
./scripts/repository_sync fetch-branches all

# Fetch branches for work repositories only
./scripts/repository_sync fetch-branches work

# Fetch branches for personal repositories only
./scripts/repository_sync fetch-branches personal
```

**Workflow:**
1. Fetches all remotes (`git fetch --all`)
2. Identifies all remote branches
3. Creates local tracking branches for any remote branches not already tracked
4. Reports number of branches created per repository

**Use case:** After a team member pushes new feature branches, quickly track them locally across all repos.

#### Sync with Main Branch

Merge or rebase main branch into current feature branches:

```bash
# Merge main into current branches (all repos)
./scripts/repository_sync sync-main all

# Rebase current branches with main (work repos only)
./scripts/repository_sync sync-main work --rebase

# Merge main into current branches (personal repos)
./scripts/repository_sync sync-main personal
```

**Workflow:**
1. Determines main branch name (main or master)
2. Fetches latest from origin
3. Checks for uncommitted changes (blocks if found)
4. Merges or rebases origin/main into current branch
5. Aborts on conflicts and reports which repos need manual resolution

**Important notes:**
- Repositories already on main/master are skipped
- Requires clean working directory (no uncommitted changes)
- On conflict, operation is aborted and repository is left clean
- Use `--rebase` flag for rebase instead of merge

**Use case:** Keep all feature branches up to date with latest main branch changes.

#### Switch Branches

Switch all repositories to a specified branch:

```bash
# Switch all repos to feature/new-design branch
./scripts/repository_sync switch all feature/new-design

# Switch work repos to main branch
./scripts/repository_sync switch work main

# Switch personal repos to develop branch
./scripts/repository_sync switch personal develop
```

**Workflow:**
1. Checks if branch exists locally
2. If local: switches to branch (`git checkout branch`)
3. If remote only: creates local tracking branch and switches
4. If branch doesn't exist: skips repository with warning

**Use case:** Quickly switch entire workspace to a specific branch for testing or development.

### Repository Status

Enhanced status display shows git state:

```
Repository                     Category        Git Status       URL
--------------------------------------------------------------------------------
digitalmodel                   Work            Clean           git@github.com:user/digitalmodel.git
aceengineer-admin              Personal        Uncommitted     git@github.com:user/aceengineer-admin.git
energy                         Work            Unpushed        git@github.com:user/energy.git
frontierdeepwater              Work            Behind remote   git@github.com:user/frontierdeepwater.git
```

**Status Indicators:**
- 🟢 **Clean**: No changes, up to date with remote
- 🔴 **Uncommitted**: Has uncommitted local changes
- 🟣 **Unpushed**: Has commits not pushed to remote
- 🔵 **Behind remote**: Remote has commits not pulled locally
- 🟡 **Not cloned**: Repository doesn't exist locally

## Configuration

### Repository Configuration File

Location: `config/repos.conf`

Format:
```bash
# Repository URL Configuration
# Format: repo_name=git_url

# Comment lines start with #
repo_name=git_url

# Examples:
digitalmodel=git@github.com:username/digitalmodel.git
aceengineer-admin=git@github.com:username/aceengineer-admin.git
energy=https://github.com/username/energy.git
```

### Repository Categories

Categories are determined from `.gitignore` comments:

```bash
# .gitignore format
aceengineer-admin/   # Personal
digitalmodel/        # Work
aceengineer-website/ # Personal, Work
```

Supported categories:
- `# Personal` - Personal repositories
- `# Work` - Work repositories
- `# Personal, Work` or `# Work, Personal` - Both categories

## Usage Examples

### Example 1: First Time Setup

```bash
# Run the script
./repository_sync

# Edit configuration (Option 8)
# Add repository URLs in config/repos.conf

# Clone all work repositories (Option 5)
```

### Example 2: Clone Personal Repos Only

```bash
# Run the script
./repository_sync

# List personal repositories (Option 3)
# Review the list

# Clone personal repositories (Option 6)
```

### Example 4: Commit and Push All Repos

```bash
# Run the script
./repository_sync

# Commit all repositories (Option 10)
# Enter commit message when prompted

# Push all repositories to remote (Option 13)
```

### Example 5: Full Sync Workflow

```bash
# Run the script
./repository_sync

# Full sync all repos (Option 19)
# This commits changes AND pushes to remote in one operation
```

### Example 6: Daily Development Workflow

```bash
# Morning: Pull latest changes
./repository_sync → Option 16 (Pull all repositories)

# During work: Make changes in various repos
# ...

# End of day: Commit and push all changes
./repository_sync → Option 19 (Full sync all)
```

### Example 3: Add New Repository

1. Add the repository to `.gitignore`:
   ```bash
   new-project/   # Work
   ```

2. Run the script and refresh (Option 9)

3. Edit configuration (Option 8) and add URL:
   ```bash
   new-project=git@github.com:username/new-project.git
   ```

4. Clone the specific repository (Option 7)

## Repository Statistics

The script automatically counts and displays:

- **Total repositories**: All repositories found in `.gitignore`
- **Work repositories**: Repositories marked as `# Work`
- **Personal repositories**: Repositories marked as `# Personal`

Repositories marked as both Work and Personal are counted in both categories.

## Error Handling

The script handles common errors:

### Missing Configuration
```
⚠ Repository configuration file not found
Creating template configuration file...
Please edit config/repos.conf with your repository URLs
```

### Repository Already Exists
```
⊘ digitalmodel already exists, skipping
```

### Clone Failure
```
✗ Failed to clone aceengineer-admin
```

### No URL Configured
```
✗ No URL configured for new-project
```

## Tips

1. **Use SSH URLs for convenience**: Configure SSH keys to avoid entering passwords
   ```bash
   repo=git@github.com:username/repo.git
   ```

2. **Edit configuration from menu**: Use Option 8 to edit `repos.conf` directly
   ```bash
   # Opens in your default editor (nano/vim/etc)
   ```

3. **Refresh after changes**: Use Option 9 after modifying `.gitignore` or `repos.conf`

4. **Check status before cloning**: Use listing options (1-3) to review what will be cloned

5. **Clone in stages**: Clone work repos first, then personal repos separately for better organization

## Advanced Usage

### Custom Editor

Set your preferred editor for configuration editing:

```bash
export EDITOR=vim
./repository_sync
# Option 8 will now use vim
```

### Batch Operations

The script supports batch operations through the menu:

```bash
# Clone all work repositories
# The script will:
#   - Check each repository's existence
#   - Skip existing repositories
#   - Clone missing repositories
#   - Report success/failure for each
#   - Provide summary statistics
```

## Troubleshooting

### Script Won't Run

```bash
# Make sure the script is executable
chmod +x repository_sync
```

### Config File Not Found

The script will automatically create a template. Just run:
```bash
./repository_sync
```

### Wrong Repository Count

After modifying `.gitignore`:
1. Use Option 9 to refresh
2. Or restart the script

### Clone Failures

Common causes:
- Missing URL in `repos.conf`
- Invalid git URL
- Network connectivity issues
- Permission denied (check SSH keys)

## File Locations

```
workspace-hub/
├── repository_sync           # Main script
├── config/
│   └── repos.conf           # Repository URL configuration
├── .gitignore               # Repository list with categories
└── docs/
    └── REPOSITORY_SYNC.md   # This documentation
```

## Related Documentation

- [Git Management Module](modules/git-management/README.md)
- [Workspace Hub Overview](README.md)
- [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)

## Version History

- **v1.0.0** (2025-10-26): Initial release
  - Interactive CLI menu
  - Repository parsing from `.gitignore`
  - Work/Personal categorization
  - Bulk and individual cloning
  - Configuration management
