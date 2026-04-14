# Repository Sync CLI - Menu Structure

## Current Command-Based Interface

| Command | Scope | Options | Description |
|---------|-------|---------|-------------|
| `list` | all/work/personal | - | List repositories with status |
| `clone` | all/work/personal/repo-name | - | Clone repositories |
| `commit` | all/work/personal | -m "message" | Stage and commit changes |
| `push` | all/work/personal | - | Push to remote |
| `pull` | all/work/personal | - | Pull from remote |
| `sync` | all/work/personal | -m "message" | Commit + push in one command |
| `status` | all/work/personal | - | Detailed git status |
| `branches` | all/work/personal | - | List all branches |
| `fetch-branches` | all/work/personal | - | Fetch and track remote branches |
| `sync-main` | all/work/personal | --rebase | Merge/rebase main into current |
| `switch` | all/work/personal | branch-name | Switch to specified branch |
| `config` | - | - | Edit configuration |
| `refresh` | - | - | Refresh repository list |
| `help` | - | - | Show help message |

## Proposed Multi-Level Interactive Menu

### Level 1: Main Menu

| Option | Category | Description |
|--------|----------|-------------|
| 1 | Repository Operations | View, clone, and manage repositories |
| 2 | Git Operations | Commit, push, pull, sync changes |
| 3 | Branch Management | Manage branches across repositories |
| 4 | Configuration | Edit settings and refresh |
| 5 | Help | Show detailed help |
| 0 | Exit | Exit the program |

### Level 2: Repository Operations Submenu

| Option | Action | Description |
|--------|--------|-------------|
| 1 | List All Repositories | View all repositories with status |
| 2 | List Work Repositories | View work repositories only |
| 3 | List Personal Repositories | View personal repositories only |
| 4 | Clone Repositories | Go to clone submenu |
| 5 | Repository Status | Go to status submenu |
| 0 | Back | Return to main menu |

#### Level 3: Clone Submenu

| Option | Scope | Description |
|--------|-------|-------------|
| 1 | Clone All | Clone all repositories |
| 2 | Clone Work Only | Clone work repositories only |
| 3 | Clone Personal Only | Clone personal repositories only |
| 4 | Clone Specific Repo | Select specific repository to clone |
| 0 | Back | Return to repository operations |

#### Level 3: Status Submenu

| Option | Scope | Description |
|--------|-------|-------------|
| 1 | Status All | Show detailed status for all repos |
| 2 | Status Work | Show status for work repos |
| 3 | Status Personal | Show status for personal repos |
| 0 | Back | Return to repository operations |

### Level 2: Git Operations Submenu

| Option | Action | Description |
|--------|--------|-------------|
| 1 | Commit Changes | Go to commit submenu |
| 2 | Push to Remote | Go to push submenu |
| 3 | Pull from Remote | Go to pull submenu |
| 4 | Full Sync | Go to sync submenu |
| 0 | Back | Return to main menu |

#### Level 3: Commit Submenu

| Option | Scope | Description |
|--------|-------|-------------|
| 1 | Commit All | Commit all repositories |
| 2 | Commit Work | Commit work repositories |
| 3 | Commit Personal | Commit personal repositories |
| - | (prompt) | Enter custom commit message |
| 0 | Back | Return to git operations |

#### Level 3: Push Submenu

| Option | Scope | Description |
|--------|-------|-------------|
| 1 | Push All | Push all repositories |
| 2 | Push Work | Push work repositories |
| 3 | Push Personal | Push personal repositories |
| 0 | Back | Return to git operations |

#### Level 3: Pull Submenu

| Option | Scope | Description |
|--------|-------|-------------|
| 1 | Pull All | Pull all repositories |
| 2 | Pull Work | Pull work repositories |
| 3 | Pull Personal | Pull personal repositories |
| 0 | Back | Return to git operations |

#### Level 3: Sync Submenu

| Option | Scope | Description |
|--------|-------|-------------|
| 1 | Sync All | Full sync all repositories |
| 2 | Sync Work | Full sync work repositories |
| 3 | Sync Personal | Full sync personal repositories |
| - | (prompt) | Enter custom commit message |
| 0 | Back | Return to git operations |

### Level 2: Branch Management Submenu

| Option | Action | Description |
|--------|--------|-------------|
| 1 | List Branches | Go to list branches submenu |
| 2 | Fetch Remote Branches | Go to fetch submenu |
| 3 | Sync with Main | Go to sync-main submenu |
| 4 | Switch Branch | Go to switch submenu |
| 0 | Back | Return to main menu |

#### Level 3: List Branches Submenu

| Option | Scope | Description |
|--------|-------|-------------|
| 1 | List All | List branches in all repos |
| 2 | List Work | List branches in work repos |
| 3 | List Personal | List branches in personal repos |
| 0 | Back | Return to branch management |

#### Level 3: Fetch Branches Submenu

| Option | Scope | Description |
|--------|-------|-------------|
| 1 | Fetch All | Fetch branches for all repos |
| 2 | Fetch Work | Fetch branches for work repos |
| 3 | Fetch Personal | Fetch branches for personal repos |
| 0 | Back | Return to branch management |

#### Level 3: Sync with Main Submenu

| Option | Scope | Description |
|--------|-------|-------------|
| 1 | Sync All (Merge) | Merge main into all repos |
| 2 | Sync Work (Merge) | Merge main into work repos |
| 3 | Sync Personal (Merge) | Merge main into personal repos |
| 4 | Sync All (Rebase) | Rebase all repos with main |
| 5 | Sync Work (Rebase) | Rebase work repos with main |
| 6 | Sync Personal (Rebase) | Rebase personal repos with main |
| 0 | Back | Return to branch management |

#### Level 3: Switch Branch Submenu

| Option | Scope | Description |
|--------|-------|-------------|
| 1 | Switch All | Switch all repos to branch |
| 2 | Switch Work | Switch work repos to branch |
| 3 | Switch Personal | Switch personal repos to branch |
| - | (prompt) | Enter branch name |
| 0 | Back | Return to branch management |

### Level 2: Configuration Submenu

| Option | Action | Description |
|--------|--------|-------------|
| 1 | Edit Configuration | Edit repos.conf file |
| 2 | Refresh Repository List | Refresh from .gitignore |
| 3 | View Statistics | Show repository counts |
| 0 | Back | Return to main menu |

## Navigation

- **Enter option number** to navigate to submenu
- **0** to go back one level
- **Ctrl+C** to exit at any time
- **Command-based mode still available** via command line arguments

## Example Navigation Flow

```
Main Menu (Level 1)
  ↓ Select: 2 (Git Operations)
Git Operations Menu (Level 2)
  ↓ Select: 1 (Commit Changes)
Commit Submenu (Level 3)
  ↓ Select: 2 (Commit Work)
  ↓ Enter commit message
  ↓ Execute commit operation
  ↓ Return to Commit Submenu
  ↓ Select: 0 (Back)
Git Operations Menu (Level 2)
  ↓ Select: 0 (Back)
Main Menu (Level 1)
```
