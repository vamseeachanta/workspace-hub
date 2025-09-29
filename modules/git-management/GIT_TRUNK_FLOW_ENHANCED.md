# 🌳 Enhanced Git Trunk Flow System

## Overview

The Enhanced Git Trunk Flow System provides a comprehensive, automated trunk-based development workflow designed for managing multiple repositories efficiently. This system emphasizes continuous integration, short-lived feature branches, and automated release management.

## 🚀 Quick Start

### Installation

The trunk flow commands are available as slash commands in all repositories after syncing:

```bash
# Make commands executable
chmod +x /mnt/github/github/.agent-os/commands/git-trunk-*.py

# Sync to all repositories (if using sync system)
/sync-all-commands
```

### Basic Usage

```bash
# Create a new feature branch
/git-trunk-flow-enhanced --create-feature user-authentication

# Check trunk flow status
/git-trunk-status

# Merge feature to trunk with smart conflict resolution
/git-trunk-flow-enhanced --smart-merge

# Sync all repositories
/git-trunk-sync-all
```

## 📋 Core Concepts

### Trunk-Based Development Principles

1. **Single Source of Truth**: The trunk branch (main/master) is always deployable
2. **Short-Lived Branches**: Feature branches live for days, not weeks
3. **Continuous Integration**: Frequent merges to trunk (at least daily)
4. **Feature Flags**: Deploy incomplete features behind flags
5. **Release Trains**: Regular, scheduled releases from trunk

### Branch Naming Conventions

- **Trunk**: `main` or `master`
- **Features**: `feature/description`
- **Releases**: `release/YYYY.MM.DD`
- **Hotfixes**: `hotfix/issue-description`

## 🛠️ Available Commands

### 1. git-trunk-flow-enhanced

The primary command for trunk-based development workflow.

#### Features

- **Feature Branch Management**: Create and manage short-lived feature branches
- **Smart Merge**: Intelligent conflict resolution with assisted merging
- **Parallel Updates**: Update multiple branches simultaneously
- **Feature Flags**: Integrate feature toggles for trunk-based deployment
- **Release Trains**: Automated release branch creation and tagging
- **Branch Analytics**: Metrics and insights on branch health
- **Policy Enforcement**: Ensure compliance with trunk-based development practices

#### Usage Examples

```bash
# Create a feature branch
/git-trunk-flow-enhanced --create-feature payment-integration

# Smart merge with conflict assistance
/git-trunk-flow-enhanced --smart-merge

# Update all branches in parallel
/git-trunk-flow-enhanced --parallel-update

# Create and manage feature flags
/git-trunk-flow-enhanced --feature-flag payment-system --enable-flag

# Start a release train
/git-trunk-flow-enhanced --release-train

# View branch analytics
/git-trunk-flow-enhanced --analytics

# Clean up merged branches
/git-trunk-flow-enhanced --cleanup

# Check policy compliance
/git-trunk-flow-enhanced --enforce-policy
```

### 2. git-trunk-status

Real-time dashboard showing trunk flow status.

#### Displays

- Current branch and trunk status
- Sync status (commits ahead/behind)
- Active feature branches
- Recent activity graph
- Feature flag status
- Policy compliance indicators

#### Usage

```bash
# Show status dashboard
/git-trunk-status

# Status for specific repository
/git-trunk-status --repo /path/to/repo

# Output in JSON format
/git-trunk-status --json
```

### 3. git-trunk-sync-all

Synchronize trunk-based development across multiple repositories.

#### Features

- Parallel repository synchronization
- Automatic trunk detection
- Feature branch updates
- Merged branch cleanup
- Policy enforcement across repos
- Detailed sync reports

#### Usage

```bash
# Sync all repositories
/git-trunk-sync-all

# Sync specific repositories
/git-trunk-sync-all --repos aceengineer-admin assetutilities

# Enforce policies across all repos
/git-trunk-sync-all --enforce-policies

# Custom parallel workers
/git-trunk-sync-all --max-workers 10
```

## 🔧 Configuration

### Repository Configuration

Each repository can have a `.trunk-flow.json` configuration file:

```json
{
  "trunk_branch": "main",
  "feature_prefix": "feature/",
  "release_prefix": "release/",
  "hotfix_prefix": "hotfix/",
  "max_branch_age_days": 14,
  "auto_delete_merged": true,
  "require_review": true,
  "feature_flags": {
    "feature_payment": {
      "enabled": false,
      "created_at": "2024-01-15T10:00:00",
      "branch": "feature/payment-system"
    }
  },
  "release_train": {
    "enabled": true,
    "schedule": "weekly",
    "day": "wednesday",
    "time": "14:00"
  },
  "metrics": {
    "branch_creation_count": 42,
    "merge_count": 156,
    "conflict_resolution_count": 8,
    "average_branch_lifetime_hours": 72
  }
}
```

## 📊 Advanced Features

### Feature Flags Integration

Manage features in production without long-lived branches:

```python
# Generated feature flag code snippet
if feature_flags.get('feature_payment', {'enabled': False})['enabled']:
    # New payment system code
    process_payment_v2()
else:
    # Existing payment code
    process_payment_v1()
```

### Smart Conflict Resolution

The system provides intelligent conflict resolution assistance:

1. **Automatic Detection**: Identifies conflict patterns
2. **Resolution Strategies**: Offers multiple resolution approaches
3. **Guided Resolution**: Step-by-step conflict resolution guidance
4. **Metrics Tracking**: Records conflict resolution patterns

### Parallel Branch Operations

Update multiple branches simultaneously for improved efficiency:

- Concurrent git operations
- Automatic merge from trunk
- Conflict detection and reporting
- Progress tracking

### Release Train Automation

Automated release management following a regular schedule:

```bash
# Enable release train
/git-trunk-flow-enhanced --enable-train

# Configure in .trunk-flow.json
{
  "release_train": {
    "enabled": true,
    "schedule": "weekly",
    "day": "wednesday",
    "time": "14:00"
  }
}

# Start release train manually
/git-trunk-flow-enhanced --release-train
```

## 📈 Metrics and Analytics

### Branch Health Metrics

- **Branch Age**: Track how long branches have been active
- **Merge Frequency**: Monitor integration frequency
- **Conflict Rate**: Measure and reduce merge conflicts
- **Cycle Time**: Time from branch creation to merge

### Dashboard Visualization

```
📊 Branch Analytics Dashboard
==================================================
📈 Total branches: 15
✅ Active branches: 12
⚠️ Stale branches (>14 days): 3

📊 Workflow Metrics:
  - Branch Creation Count: 156
  - Merge Count: 142
  - Conflict Resolution Count: 8
  - Average Branch Lifetime Hours: 72

🗑️ Stale branches to consider cleaning:
  - feature/old-feature (21 days old)
  - feature/abandoned-work (18 days old)
```

## 🚨 Policy Enforcement

### Trunk Flow Policies

1. **Maximum Branch Age**: Default 14 days
2. **No Direct Trunk Commits**: Enforce feature branch usage
3. **Regular Integration**: At least daily merges
4. **Clean History**: Squash merges for feature branches
5. **Automated Cleanup**: Remove merged branches

### Violation Detection

```bash
# Check single repository
/git-trunk-flow-enhanced --enforce-policy

# Check all repositories
/git-trunk-sync-all --enforce-policies
```

## 🔄 Workflow Examples

### Standard Feature Development

```bash
# 1. Create feature branch
/git-trunk-flow-enhanced --create-feature user-profile

# 2. Develop and commit changes
git add .
git commit -m "feat: implement user profile"

# 3. Create feature flag (optional)
/git-trunk-flow-enhanced --feature-flag user-profile

# 4. Smart merge to trunk
/git-trunk-flow-enhanced --smart-merge

# 5. Clean up
/git-trunk-flow-enhanced --cleanup
```

### Multi-Repository Sync

```bash
# 1. Check status across all repos
for repo in */; do
  cd "$repo"
  /git-trunk-status
  cd ..
done

# 2. Sync all repositories
/git-trunk-sync-all

# 3. Verify policy compliance
/git-trunk-sync-all --enforce-policies
```

### Release Process

```bash
# 1. Ensure all features are merged
/git-trunk-flow-enhanced --analytics

# 2. Start release train
/git-trunk-flow-enhanced --release-train

# 3. Deploy release branch
# Automated via CI/CD pipeline
```

## 🎯 Best Practices

### Do's

- ✅ Keep feature branches short-lived (< 2 weeks)
- ✅ Merge to trunk at least daily
- ✅ Use feature flags for incomplete features
- ✅ Run policy enforcement regularly
- ✅ Clean up merged branches promptly
- ✅ Keep trunk always deployable

### Don'ts

- ❌ Create long-lived feature branches
- ❌ Commit directly to trunk
- ❌ Delay integration for "perfection"
- ❌ Skip conflict resolution
- ❌ Ignore policy violations
- ❌ Merge broken code to trunk

## 🔍 Troubleshooting

### Common Issues

#### Merge Conflicts

```bash
# Use smart merge for assistance
/git-trunk-flow-enhanced --smart-merge

# Manual resolution if needed
git status  # See conflicted files
# Edit files to resolve conflicts
git add .
git commit
```

#### Stale Branches

```bash
# Identify stale branches
/git-trunk-flow-enhanced --analytics

# Clean up automatically
/git-trunk-flow-enhanced --cleanup

# Force cleanup (careful!)
/git-trunk-flow-enhanced --cleanup --force
```

#### Policy Violations

```bash
# Check violations
/git-trunk-flow-enhanced --enforce-policy

# Fix age violations
/git-trunk-flow-enhanced --smart-merge  # Merge old branches
/git-trunk-flow-enhanced --cleanup       # Remove merged branches
```

## 📚 Integration with CI/CD

### GitHub Actions Example

```yaml
name: Trunk Flow CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  enforce-policies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check Trunk Policies
        run: |
          python /git-trunk-flow-enhanced.py --enforce-policy
      
  auto-cleanup:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v2
      - name: Clean Merged Branches
        run: |
          python /git-trunk-flow-enhanced.py --cleanup
```

## 🚀 Advanced Configuration

### Custom Branch Patterns

Modify `.trunk-flow.json` for custom branch naming:

```json
{
  "feature_prefix": "feat/",
  "release_prefix": "rel/",
  "hotfix_prefix": "fix/",
  "experimental_prefix": "exp/"
}
```

### Release Train Scheduling

Configure automated releases:

```json
{
  "release_train": {
    "enabled": true,
    "schedule": "daily|weekly|biweekly|monthly",
    "day": "monday|tuesday|...|sunday",
    "time": "HH:MM",
    "auto_tag": true,
    "auto_deploy": false
  }
}
```

### Metrics Collection

Track detailed metrics:

```json
{
  "metrics": {
    "track_cycle_time": true,
    "track_lead_time": true,
    "track_deployment_frequency": true,
    "track_mttr": true,
    "export_to": "datadog|prometheus|custom"
  }
}
```

## 🤝 Contributing

To contribute improvements to the trunk flow system:

1. Create a feature branch
2. Implement improvements
3. Test across multiple repositories
4. Submit with documentation updates

## 📄 License

This trunk flow system is part of the repository tooling and follows the repository's license.

---

*Last Updated: 2024-08-12*
*Version: 1.0.0*

**💡 Tip**: These commands are available in all repositories after running `/sync-all-commands`