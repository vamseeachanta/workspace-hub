# Git Management Module

Tools and scripts for managing multiple Git repositories.

## 📁 Contents

### Scripts
- `check_all_repos_status.sh` - Check status of all repositories
- `pull_all_repos.sh` - Pull latest changes for all repositories
- `git_sync_all.sh` - Synchronize all repositories
- `batch_commit_all.sh` - Batch commit changes across repos
- `merge_and_cleanup_branches.sh` - Branch cleanup utilities
- `sync_repos.sh` - Repository synchronization
- `commit_and_sync_all.sh` - Commit and sync all repos
- `quick_trunk_cleanup.sh` - Quick trunk branch cleanup
- `check_trunk_status.sh` - Check trunk branch status
- `setup-trunk-flow.sh` - Setup trunk-based development
- `resolve_repos.sh` - Resolve repository issues

### Python Tools
- `git_sync_all_enhanced.py` - Enhanced Git synchronization

### Reports
- Various JSON reports for tracking sync operations

## 🚀 Usage

### Check All Repository Status
```bash
./check_all_repos_status.sh
```

### Pull All Repositories
```bash
./pull_all_repos.sh
```

### Sync All Repositories
```bash
./git_sync_all.sh
```

### Batch Commit
```bash
./batch_commit_all.sh "Your commit message"
```

## 📊 Features

- **Parallel Operations**: Handle multiple repositories simultaneously
- **Status Reporting**: Comprehensive status checks
- **Branch Management**: Automated branch operations
- **Conflict Resolution**: Smart conflict handling
- **Progress Tracking**: Real-time progress updates

## ⚙️ Configuration

Scripts use the repository structure defined in the parent `.gitignore` to identify managed repositories.

## 📝 Notes

- All scripts preserve individual repository independence
- Operations are non-destructive by default
- Uncommitted changes are detected and handled safely