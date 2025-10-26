# Repository Sync Manager

> CLI tool for managing and synchronizing multiple Git repositories in workspace-hub

## Overview

The `repository_sync` script provides an interactive menu-driven interface for:
- Listing all repositories (categorized as Work/Personal)
- Cloning repositories that don't exist locally
- Bulk operations on Work or Personal repositories
- Managing repository URLs through a configuration file

## Quick Start

### 1. Run the script

```bash
./repository_sync
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

### 3. Use the menu

The interactive menu provides the following options:

```
╔════════════════════════════════════════════════════════════════╗
║                  Repository Sync Manager                      ║
╚════════════════════════════════════════════════════════════════╝

Repository Statistics:
  Total repositories: 73
  Work repositories: 17
  Personal repositories: 9

Main Menu:

  1) List all repositories
  2) List work repositories
  3) List personal repositories

  4) Clone all repositories
  5) Clone work repositories only
  6) Clone personal repositories only
  7) Clone specific repository

  8) Edit repository configuration
  9) Refresh repository list

  0) Exit
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
