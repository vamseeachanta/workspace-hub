# GitHub Repos Management

This repository serves as a management layer for multiple GitHub project repositories. Each subdirectory contains its own independent git repository.

## 📁 Repository Structure

This parent repository tracks only management scripts and documentation, while individual project repositories remain independent.

### Individual Repositories

The following directories are independent git repositories and are excluded from this parent repo:

- `aceengineer-admin/` - Admin panel repository
- `aceengineer-website/` - Main website repository
- `aceengineercode/` - Core code repository
- `achantas-data/` - Data management repository
- `achantas-media/` - Media assets repository
- `acma-projects/` - ACMA projects repository
- `ai-native-traditional-eng/` - AI engineering repository
- `assethold/` - Asset holding repository
- `assetutilities/` - Asset utilities repository
- `client_projects/` - Client projects repository
- `coordination/` - Coordination tools repository
- `digitalmodel/` - Digital model repository
- `doris/` - Doris project repository
- `energy/` - Energy projects repository
- `frontierdeepwater/` - Frontier deepwater repository
- `hobbies/` - Hobbies projects repository
- `investments/` - Investment tracking repository
- `OGManufacturing/` - OG Manufacturing repository
- `pyproject-starter/` - Python project starter repository
- `rock-oil-field/` - Rock oil field repository
- `sabithaandkrishnaestates/` - Estates management repository
- `saipem/` - Saipem project repository
- `sd-work/` - SD work repository
- `seanation/` - Sea nation repository
- `teamresumes/` - Team resumes repository
- `worldenergydata/` - World energy data repository

## 🛠️ Management Scripts

This parent repository tracks the following management tools:

### Git Management
- `git_sync_all.sh` - Sync all repositories
- `batch_commit_all.sh` - Batch commit changes
- `merge_and_cleanup_branches.sh` - Branch cleanup utilities
- `sync_repos.sh` - Repository synchronization

### Setup and Configuration
- `setup_agents_folders.py` - Agent folder setup
- `setup_all_commands.py` - Command setup
- `propagate-slash-commands.sh` - Slash command propagation

### Analysis and Reporting
- `list_all_commands.py` - List available commands
- `verify_enhanced_specs.py` - Specification verification

## 🚀 Usage

### Working with Individual Repositories

Each subdirectory repository maintains its own:
- Git history
- Remote origin
- Branches
- Commits

To work with an individual repository:
```bash
cd <repository-name>/
git status
git pull
git push
```

### Managing All Repositories

Use the provided scripts to manage multiple repositories:

```bash
# Sync all repositories
./git_sync_all.sh

# Check status of all repos
for dir in */; do
  if [ -d "$dir/.git" ]; then
    echo "=== $dir ==="
    git -C "$dir" status -s
  fi
done

# Pull all repositories
for dir in */; do
  if [ -d "$dir/.git" ]; then
    echo "=== Pulling $dir ==="
    git -C "$dir" pull
  fi
done
```

## 📋 Management Commands

### Check All Repo Status
```bash
./check_all_repos_status.sh
```

### Batch Operations
```bash
./batch_commit_all.sh "commit message"
```

### Sync All
```bash
./sync_all_repos.sh
```

## ⚠️ Important Notes

1. **This parent repository does NOT track individual repository contents**
2. **Each subdirectory repository maintains complete independence**
3. **Changes to individual repos should be committed within those repos**
4. **The parent repo only tracks management scripts and documentation**

## 🔧 Initial Setup

If you're setting this up for the first time:

1. Clone this management repository
2. Clone individual repositories into their respective directories
3. Use management scripts to maintain all repositories

## 📝 Contributing

When adding new repositories:
1. Clone the new repo into a subdirectory
2. Add the directory name to `.gitignore`
3. Update this README with the new repository information

## 🔐 Security

- Individual repository credentials are managed separately
- No secrets or credentials are stored in this management repository
- Each repository maintains its own access controls

---

*Last updated: September 2025*