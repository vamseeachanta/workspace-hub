---
name: github-sync
description: Multi-repository synchronization coordinator for version alignment, dependency sync, and cross-package integration. Use for package synchronization, version management, documentation alignment, and coordinated releases across multiple repositories.
---

# GitHub Sync Coordinator Skill

## Overview

This skill enables multi-package synchronization and version alignment across repositories with intelligent swarm coordination. It manages dependency resolution, documentation consistency, and cross-package integration for seamless multi-repository workflows.

**Key Capabilities:**
- Package dependency synchronization with conflict resolution
- Version alignment across multiple repositories
- Cross-package integration with automated testing
- Documentation synchronization for consistency
- Release coordination with deployment pipelines

## Quick Start

```bash
# Synchronize package dependencies across repos
gh api repos/:owner/:repo1/contents/package.json --jq '.content' | base64 -d > /tmp/pkg1.json
gh api repos/:owner/:repo2/contents/package.json --jq '.content' | base64 -d > /tmp/pkg2.json

# Compare and identify version differences
diff -u /tmp/pkg1.json /tmp/pkg2.json

# Create sync branch
gh api repos/:owner/:repo/git/refs \
  -f ref='refs/heads/sync/package-alignment' \
  -f sha=$(gh api repos/:owner/:repo/git/refs/heads/main --jq '.object.sha')
```

## When to Use

- **Package Synchronization**: Aligning versions across monorepo packages
- **Dependency Updates**: Coordinating major dependency upgrades
- **Documentation Sync**: Keeping README/CLAUDE.md files consistent
- **Release Coordination**: Managing synchronized releases
- **Cross-Repo Features**: Implementing features spanning multiple packages

## Usage Examples

### 1. Synchronize Package Dependencies

```bash
# Read current package states
REPO1_PKG=$(gh api repos/org/repo1/contents/package.json --jq '.content' | base64 -d)
REPO2_PKG=$(gh api repos/org/repo2/contents/package.json --jq '.content' | base64 -d)

# Create synchronization branch
gh api repos/org/repo1/git/refs \
  -f ref='refs/heads/sync/deps-alignment' \
  -f sha=$(gh api repos/org/repo1/git/refs/heads/main --jq '.object.sha')

# Update file with aligned versions
gh api repos/org/repo1/contents/package.json \
  --method PUT \
  -f message="feat: Align Node.js version requirements across packages" \
  -f branch="sync/deps-alignment" \
  -f content="$(echo '[updated package.json content]' | base64)" \
  -f sha="$(gh api repos/org/repo1/contents/package.json?ref=sync/deps-alignment --jq '.sha')"

# Create PR for review
gh pr create \
  --repo org/repo1 \
  --title "Sync: Align package dependencies" \
  --head sync/deps-alignment \
  --base main \
  --body "Aligns dependencies with org/repo2 for compatibility"
```

### 2. Documentation Synchronization

```bash
# Get source documentation
SOURCE_DOC=$(gh api repos/org/primary-repo/contents/CLAUDE.md --jq '.content' | base64 -d)

# Create sync branch on target repo
gh api repos/org/secondary-repo/git/refs \
  -f ref='refs/heads/sync/documentation' \
  -f sha=$(gh api repos/org/secondary-repo/git/refs/heads/main --jq '.object.sha')

# Update target documentation
gh api repos/org/secondary-repo/contents/CLAUDE.md \
  --method PUT \
  -f message="docs: Synchronize CLAUDE.md with primary repo" \
  -f branch="sync/documentation" \
  -f content="$(echo "$SOURCE_DOC" | base64)" \
  -f sha="$(gh api repos/org/secondary-repo/contents/CLAUDE.md?ref=main --jq '.sha' 2>/dev/null || echo '')"
```

### 3. Cross-Package Feature Integration

```bash
# Push multiple files to feature branch
gh api repos/org/monorepo/contents/package-a/src/feature.js \
  --method PUT \
  -f message="feat: Add cross-package feature" \
  -f branch="feature/cross-package" \
  -f content="$(cat feature-a.js | base64)"

gh api repos/org/monorepo/contents/package-b/src/integration.js \
  --method PUT \
  -f message="feat: Add integration for cross-package feature" \
  -f branch="feature/cross-package" \
  -f content="$(cat integration-b.js | base64)"

# Create coordinated PR
gh pr create \
  --repo org/monorepo \
  --title "Feature: Cross-Package Integration" \
  --head feature/cross-package \
  --base main \
  --body "## Cross-Package Feature

### Changes
- package-a: Core feature implementation
- package-b: Integration hooks

### Testing
- [x] Package dependency verification
- [x] Integration test suite
- [x] Cross-package compatibility"
```

## MCP Tool Integration

### Swarm-Coordinated Sync

```javascript
// Initialize sync coordination swarm

// Store sync state in memory
  action: "store",
  key: "sync/packages/status",
  value: {
    packages_synced: ["package-a", "package-b"],
    version_alignment: "completed",
    timestamp: Date.now()
  }
}

// Orchestrate validation
  task: "Validate package synchronization and run integration tests",
  strategy: "parallel",
  priority: "high"
}

// Load balance sync tasks
  swarmId: "sync-coordination-swarm",
  tasks: [
    "package_json_sync",
    "documentation_alignment",
    "version_compatibility_check",
    "integration_test_execution"
  ]
}
```

### Conflict Resolution

```javascript
// Initialize conflict resolution swarm

// Store conflict context
  action: "store",
  key: "sync/conflicts/current",
  value: {
    conflicts: ["version_mismatch", "dependency_conflict"],
    resolution_strategy: "automated_with_validation",
    priority_order: ["critical", "high", "medium"]
  }
}

// Coordinate resolution
```

## Synchronization Strategies

### Version Alignment Strategy

```javascript
const syncStrategy = {
  nodeVersion: ">=20.0.0",  // Align to highest requirement
  dependencies: {
    "typescript": "^5.0.0",  // Use latest stable
    "jest": "^29.0.0"
  },
  engines: {
    aligned: true,
    strategy: "highest_common"
  }
};
```

### Documentation Sync Pattern

```javascript
const docSyncPattern = {
  sourceOfTruth: "primary-repo/CLAUDE.md",
  targets: [
    "secondary-repo/CLAUDE.md",
    "tertiary-repo/CLAUDE.md"
  ],
  customSections: {
    "secondary-repo": "Package-Specific Configuration",
    "tertiary-repo": "Local Customizations"
  }
};
```

## Best Practices

### 1. Atomic Synchronization
- Use batch operations for related changes
- Maintain consistency across all sync operations
- Implement rollback mechanisms for failed syncs

### 2. Version Management
- Semantic versioning alignment
- Dependency compatibility validation
- Automated version bump coordination

### 3. Documentation Consistency
- Single source of truth for shared concepts
- Package-specific customizations in separate sections
- Automated documentation validation

### 4. Testing Integration
- Cross-package test validation before merge
- Integration test automation
- Performance regression detection

## Error Handling

### Recovery Procedures

```bash
# Check sync status
gh api repos/:owner/:repo/git/refs/heads/sync/package-alignment || echo "Branch not found"

# Rollback failed sync
git fetch origin
git checkout main
git branch -D sync/package-alignment
git push origin --delete sync/package-alignment

# Retry with fresh branch
gh api repos/:owner/:repo/git/refs \
  -f ref='refs/heads/sync/package-alignment-v2' \
  -f sha=$(gh api repos/:owner/:repo/git/refs/heads/main --jq '.object.sha')
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Version conflict | Incompatible dependencies | Use highest_common strategy |
| Merge conflict | Divergent changes | Manual resolution with sync coordinator |
| Test failures | Breaking changes | Run integration tests before merge |

## Monitoring and Metrics

### Sync Quality Metrics
- Package version alignment percentage
- Documentation consistency score
- Integration test success rate
- Synchronization completion time

### Automated Reporting

```bash
# Generate sync status report
gh api repos/:owner/:repo/pulls \
  --jq '[.[] | select(.head.ref | startswith("sync/"))] | length'

# Check CI status for sync PRs
gh pr list --search "head:sync/" --json number,statusCheckRollup
```

## Related Skills

- [github-workflow](../github-workflow/SKILL.md) - CI/CD pipeline automation
- [github-swarm-pr](../github-swarm-pr/SKILL.md) - PR management with swarms
- [github-swarm-issue](../github-swarm-issue/SKILL.md) - Issue-based coordination

---

## Version History

- **1.0.0** (2026-01-02): Initial skill conversion from sync-coordinator agent
