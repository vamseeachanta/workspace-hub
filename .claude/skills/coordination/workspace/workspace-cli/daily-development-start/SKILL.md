---
name: workspace-cli-daily-development-start
description: 'Sub-skill of workspace-cli: Daily Development Start (+4).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Daily Development Start (+4)

## Daily Development Start


```bash
# 1. Launch workspace CLI
./scripts/workspace

# 2. Repository Management -> Repository Sync Manager
# 3. Navigate to: Pull -> All
# Or directly:
./scripts/repository_sync pull all
```


## End of Day Sync


```bash
# Sync all work with commit message
./scripts/repository_sync sync work -m "$(date +%Y-%m-%d) updates"
```


## Setup New Repository


```bash
# 1. Configure URLs
./scripts/repository/configure_repos.sh

# 2. Clone repository
./scripts/repository_sync clone <repo-name>

# 3. Setup compliance
./scripts/compliance/setup_compliance.sh
```


## Code Quality Check


```bash
# Run refactor analysis
./scripts/development/refactor-analysis.sh

# Check compliance
./scripts/compliance/verify_compliance.sh
```


## Propagate Standards


```bash
# Update all repos with latest standards
./scripts/compliance/propagate_claude_config.py
./scripts/compliance/propagate_guidelines.sh
./scripts/compliance/propagate_interactive_mode.sh
```
