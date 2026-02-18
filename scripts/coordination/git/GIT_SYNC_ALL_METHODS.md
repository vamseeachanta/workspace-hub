# 🔄 Git Sync All Repositories - Complete Guide

## Overview

Multiple methods are available to sync all your Git repositories, each with different features and use cases.

## 🚀 Quick Command Reference

```bash
# Method 1: Enhanced Git Sync (RECOMMENDED)
python3 /mnt/github/github/.agent-os/commands/git-sync-all-enhanced.py

# Method 2: Trunk Flow Sync
python3 /mnt/github/github/.agent-os/commands/git-trunk-sync-all.py

# Method 3: Basic Sync Script
bash /mnt/github/github/_organized_non_repo_files/sync_repos.sh

# Method 4: Manual Per-Repo Sync
for repo in */; do cd "$repo" && git pull && cd ..; done
```

## 📋 Method Comparison

| Feature | Enhanced Sync | Trunk Flow | Basic Script | Manual |
|---------|--------------|------------|--------------|--------|
| **Parallel Processing** | ✅ Yes (5 workers) | ✅ Yes (5 workers) | ❌ No | ❌ No |
| **Auto-Stash Changes** | ✅ Yes | ⚠️ Limited | ❌ No | ❌ No |
| **Conflict Resolution** | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| **Push Changes** | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| **Branch Management** | ✅ Yes | ✅ Advanced | ⚠️ Basic | ❌ No |
| **Error Recovery** | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| **Progress Reports** | ✅ Detailed | ✅ Yes | ⚠️ Basic | ❌ No |
| **Policy Enforcement** | ❌ No | ✅ Yes | ❌ No | ❌ No |

## 🎯 Method 1: Enhanced Git Sync (RECOMMENDED)

### Features
- **Smart Stashing**: Automatically stashes and restores uncommitted changes
- **Parallel Processing**: Syncs up to 5 repos simultaneously
- **Comprehensive Sync**: Fetches, pulls, and pushes as needed
- **Error Recovery**: Handles conflicts and errors gracefully
- **Detailed Reporting**: JSON reports with full sync details

### Usage
```bash
# Basic sync all repos
python3 /mnt/github/github/.agent-os/commands/git-sync-all-enhanced.py

# Sync specific repositories
python3 /mnt/github/github/.agent-os/commands/git-sync-all-enhanced.py --repos assetutilities aceengineer-admin

# Use more parallel workers
python3 /mnt/github/github/.agent-os/commands/git-sync-all-enhanced.py --max-workers 10

# Sequential sync (for debugging)
python3 /mnt/github/github/.agent-os/commands/git-sync-all-enhanced.py --sequential

# Pull only, don't push
python3 /mnt/github/github/.agent-os/commands/git-sync-all-enhanced.py --no-push
```

### What It Does
1. **Fetches** all remote changes
2. **Stashes** uncommitted changes automatically
3. **Switches** to default branch (main/master)
4. **Pulls** latest changes with rebase
5. **Pushes** local commits to remote
6. **Restores** stashed changes
7. **Reports** comprehensive status

### Output Example
```
🚀 Git Sync All - Processing 25 repositories
============================================================
🔄 Syncing assetutilities...
  📦 Stashed 5 changes
  ⬇️ Pulled 3 commits
  ⬆️ Pushed 2 commits
  📦 Restored stashed changes
✅ assetutilities: main (↑0 ↓0)
```

## 🌳 Method 2: Trunk Flow Sync

### Features
- **Trunk-Based Development**: Enforces trunk flow policies
- **Feature Branch Updates**: Merges trunk into feature branches
- **Branch Cleanup**: Removes merged branches
- **Policy Enforcement**: Checks branch age and practices
- **Release Management**: Supports release trains

### Usage
```bash
# Sync with trunk flow
python3 /mnt/github/github/.agent-os/commands/git-trunk-sync-all.py

# Enforce policies
python3 /mnt/github/github/.agent-os/commands/git-trunk-sync-all.py --enforce-policies

# Custom parallel workers
python3 /mnt/github/github/.agent-os/commands/git-trunk-sync-all.py --max-workers 10
```

### What It Does
1. **Fetches** all remotes with pruning
2. **Updates** trunk branch (main/master)
3. **Merges** trunk into all feature branches
4. **Cleans** merged branches
5. **Enforces** trunk flow policies
6. **Reports** compliance status

## 📝 Method 3: Basic Sync Script

### Features
- Simple bash script
- Sequential processing
- Basic fetch and pull
- Handles main/master detection

### Usage
```bash
bash /mnt/github/github/_organized_non_repo_files/sync_repos.sh
```

### Limitations
- No parallel processing
- No stash handling
- No push capability
- No conflict resolution
- Limited error handling

## 🔧 Method 4: Manual Commands

### For Quick Operations
```bash
# Pull all repos (current branch)
for repo in */; do 
  echo "=== $repo ==="
  cd "$repo" && git pull && cd ..
done

# Fetch all repos
for repo in */; do 
  cd "$repo" && git fetch --all && cd ..
done

# Check status of all repos
for repo in */; do 
  echo "=== $repo ==="
  cd "$repo" && git status -s && cd ..
done
```

## 📊 Best Practices

### Daily Workflow
```bash
# Morning sync - pull latest changes
python3 /mnt/github/github/.agent-os/commands/git-sync-all-enhanced.py

# Evening sync - push all changes
python3 /mnt/github/github/.agent-os/commands/git-sync-all-enhanced.py
```

### Weekly Maintenance
```bash
# Full trunk flow sync with cleanup
python3 /mnt/github/github/.agent-os/commands/git-trunk-sync-all.py

# Enforce policies
python3 /mnt/github/github/.agent-os/commands/git-trunk-sync-all.py --enforce-policies

# Clean old branches
python3 /mnt/github/github/.agent-os/commands/git-trunk-flow-enhanced.py --cleanup
```

## 🚨 Handling Common Issues

### Uncommitted Changes
The enhanced sync automatically:
1. Stashes changes before pulling
2. Pulls latest changes
3. Restores stashed changes

### Merge Conflicts
```bash
# If conflicts occur, manually resolve:
cd <repo-with-conflict>
git status                    # See conflicted files
# Edit files to resolve
git add .
git commit -m "Resolved conflicts"
git push
```

### Stale Branches
```bash
# Clean up old branches
python3 /mnt/github/github/.agent-os/commands/git-trunk-flow-enhanced.py --cleanup

# Or use trunk sync
python3 /mnt/github/github/.agent-os/commands/git-trunk-sync-all.py
```

## 📈 Monitoring and Reports

### View Sync Reports
```bash
# List recent reports
ls -la /mnt/github/github/git-sync-report-*.json
ls -la /mnt/github/github/trunk-sync-report-*.json

# View latest report
cat /mnt/github/github/git-sync-report-*.json | tail -1 | python -m json.tool
```

### Check Repository Status
```bash
# Individual repo status
python3 /mnt/github/github/.agent-os/commands/git-trunk-status.py

# All repos quick status
for repo in */; do 
  echo -n "$repo: "
  cd "$repo" && git status -sb | head -1 && cd ..
done
```

## 🎯 Recommendations

### For Different Scenarios

| Scenario | Recommended Method | Command |
|----------|-------------------|---------|
| **Daily sync** | Enhanced Sync | `git-sync-all-enhanced.py` |
| **Feature development** | Trunk Flow | `git-trunk-sync-all.py` |
| **Quick check** | Manual | `for repo in */; do...` |
| **CI/CD integration** | Enhanced Sync | `git-sync-all-enhanced.py --no-stash` |
| **Policy enforcement** | Trunk Flow | `git-trunk-sync-all.py --enforce-policies` |

### Setup Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Git sync aliases
alias gsa='python3 /mnt/github/github/.agent-os/commands/git-sync-all-enhanced.py'
alias gst='python3 /mnt/github/github/.agent-os/commands/git-trunk-sync-all.py'
alias gss='python3 /mnt/github/github/.agent-os/commands/git-trunk-status.py'

# Quick sync
alias sync-all='gsa'
alias sync-trunk='gst'
alias sync-status='gss'
```

## 💡 Pro Tips

1. **Always sync before starting work** to avoid conflicts
2. **Use enhanced sync for daily operations** - it handles most edge cases
3. **Run trunk flow weekly** to maintain clean branch structure
4. **Check reports** for repos needing attention
5. **Set up cron jobs** for automated syncing:

```bash
# Add to crontab for daily sync at 9 AM
0 9 * * * python3 /mnt/github/github/.agent-os/commands/git-sync-all-enhanced.py

# Weekly trunk flow cleanup on Sundays
0 10 * * 0 python3 /mnt/github/github/.agent-os/commands/git-trunk-sync-all.py
```

## 🔗 Related Commands

- `/git-trunk-flow-enhanced` - Advanced branch management
- `/git-trunk-status` - Repository status dashboard
- `/git-trunk-sync-all` - Trunk-based sync
- `/git-sync-all-enhanced` - Comprehensive sync

---

*Last Updated: 2024-08-12*

**Remember**: These commands are slash commands and can be made available in all repos via `/sync-all-commands`