---
name: github-multi-repo
description: Cross-repository swarm orchestration for organization-wide automation and intelligent collaboration. Use for multi-repo coordination, synchronized operations, dependency management, and organization-wide policy changes.
---

# GitHub Multi-Repo Skill

## Overview

Cross-repository swarm orchestration for organization-wide automation. This skill handles multi-repo coordination, synchronized operations, dependency management, security updates, and organization-wide policy changes.

## Quick Start

```bash
# List organization repositories
gh repo list org --limit 100 --json name,description,languages

# Search across repositories
gh search code "pattern" --repo org/repo1 --repo org/repo2

# Clone multiple repos
for repo in repo1 repo2 repo3; do
  gh repo clone org/$repo
done

# Check repository info
gh api repos/org/repo --jq '{name, default_branch, languages, topics}'
```

## When to Use

- Coordinating changes across multiple repositories
- Organization-wide dependency updates
- Synchronized security patches
- Cross-repo refactoring operations
- Multi-service microservices coordination
- Library updates across consumers

## Core Capabilities

| Capability | Description |
|------------|-------------|
| Cross-repo initialization | Multi-repo swarm setup |
| Repository discovery | Auto-detect related repos |
| Synchronized operations | Coordinated changes |
| Dependency management | Cross-repo updates |
| Security coordination | Organization-wide patches |

## Usage Examples

### 1. Cross-Repo Swarm Initialization

```bash
# List organization repositories
REPOS=$(gh repo list org --limit 100 --json name,description,languages \
  --jq '.[] | select(.name | test("frontend|backend|shared"))')

# Get repository details
REPO_DETAILS=$(echo "$REPOS" | jq -r '.name' | while read -r repo; do
  gh api repos/org/$repo --jq '{name, default_branch, languages, topics}'
done | jq -s '.')

# Initialize swarm with repository context
npx ruv-swarm github multi-repo-init \
  --repo-details "$REPO_DETAILS" \
  --repos "org/frontend,org/backend,org/shared" \
  --topology hierarchical \
  --shared-memory \
  --sync-strategy eventual
```

### 2. Repository Discovery

```bash
# Search organization repositories
REPOS=$(gh repo list my-organization --limit 100 \
  --json name,description,languages,topics \
  --jq '.[] | select(.languages | keys | contains(["TypeScript"]))')

# Analyze repository dependencies
DEPS=$(echo "$REPOS" | jq -r '.name' | while read -r repo; do
  if gh api repos/my-organization/$repo/contents/package.json --jq '.content' 2>/dev/null; then
    gh api repos/my-organization/$repo/contents/package.json \
      --jq '.content' | base64 -d | jq '{name, dependencies, devDependencies}'
  fi
done | jq -s '.')

echo "Found $(echo "$REPOS" | jq length) TypeScript repositories"
echo "Dependencies: $DEPS"
```

### 3. Synchronized Dependency Update

```bash
# Create tracking issue
TRACKING_ISSUE=$(gh issue create \
  --repo org/main-repo \
  --title "Dependency Update: typescript@5.0.0" \
  --body "Tracking issue for updating TypeScript across all repositories" \
  --label "dependencies,tracking" \
  --json number -q .number)

# Get all repos with TypeScript
TS_REPOS=$(gh repo list org --limit 100 --json name | jq -r '.[].name' | \
  while read -r repo; do
    if gh api repos/org/$repo/contents/package.json 2>/dev/null | \
       jq -r '.content' | base64 -d | grep -q '"typescript"'; then
      echo "$repo"
    fi
  done)

# Update each repository
echo "$TS_REPOS" | while read -r repo; do
  gh repo clone org/$repo /tmp/$repo -- --depth=1
  cd /tmp/$repo

  npm install --save-dev typescript@5.0.0

  if npm test; then
    git checkout -b update-typescript-5
    git add package.json package-lock.json
    git commit -m "chore: Update TypeScript to 5.0.0

Part of #$TRACKING_ISSUE"

    git push origin HEAD
    gh pr create \
      --title "Update TypeScript to 5.0.0" \
      --body "Updates TypeScript to version 5.0.0

Tracking: #$TRACKING_ISSUE" \
      --label "dependencies"
  else
    gh issue comment $TRACKING_ISSUE \
      --body "Failed to update $repo - tests failing"
  fi
  cd -
  rm -rf /tmp/$repo
done
```

### 4. Initialize Multi-Repo Swarm

```javascript
// Initialize multi-repo swarm
mcp__claude-flow__swarm_init({ topology: "hierarchical", maxAgents: 8 })
mcp__claude-flow__agent_spawn({ type: "coordinator", name: "Multi-Repo Coordinator" })
mcp__claude-flow__agent_spawn({ type: "analyst", name: "Dependency Analyzer" })
mcp__claude-flow__agent_spawn({ type: "coder", name: "Update Agent" })
mcp__claude-flow__agent_spawn({ type: "tester", name: "Integration Tester" })

// Store multi-repo state
mcp__claude-flow__memory_usage({
    action: "store",
    key: "multi-repo/state",
    value: JSON.stringify({
        repositories: ["frontend", "backend", "shared"],
        topology: "hierarchical",
        syncStrategy: "eventual"
    })
})

// Orchestrate synchronized operations
mcp__claude-flow__task_orchestrate({
    task: "Update dependencies across all TypeScript repositories",
    strategy: "parallel",
    priority: "high"
})
```

### 5. Security Patch Coordination

```bash
# Scan all repos for vulnerable dependency
VULN_REPOS=()
for repo in $(gh repo list org --limit 100 --json name -q '.[].name'); do
  if gh api repos/org/$repo/contents/package.json 2>/dev/null | \
     jq -r '.content' | base64 -d | grep -q '"lodash": "4.17.19"'; then
    VULN_REPOS+=("$repo")
  fi
done

echo "Found ${#VULN_REPOS[@]} repos with vulnerable lodash"

# Create security tracking issue
SECURITY_ISSUE=$(gh issue create \
  --repo org/security-tracking \
  --title "SECURITY: Update lodash to 4.17.21" \
  --body "Critical security update for lodash CVE-XXXX

Affected repos:
$(printf '- %s\n' "${VULN_REPOS[@]}")" \
  --label "security,critical")

# Patch each repo
for repo in "${VULN_REPOS[@]}"; do
  gh repo clone org/$repo /tmp/$repo -- --depth=1
  cd /tmp/$repo

  npm install lodash@4.17.21
  npm audit fix

  git checkout -b security-lodash-update
  git add package.json package-lock.json
  git commit -m "security: Update lodash to 4.17.21

Fixes CVE-XXXX
Tracking: $SECURITY_ISSUE"

  git push origin HEAD
  gh pr create \
    --title "SECURITY: Update lodash to 4.17.21" \
    --body "Critical security update" \
    --label "security,critical"

  cd -
  rm -rf /tmp/$repo
done
```

## Multi-Repo Configuration

```yaml
# .swarm/multi-repo.yml
version: 1
organization: my-org
repositories:
  - name: frontend
    url: github.com/my-org/frontend
    role: ui
    agents: [coder, designer, tester]

  - name: backend
    url: github.com/my-org/backend
    role: api
    agents: [architect, coder, tester]

  - name: shared
    url: github.com/my-org/shared
    role: library
    agents: [analyst, coder]

coordination:
  topology: hierarchical
  communication: webhook
  memory: redis://shared-memory

dependencies:
  - from: frontend
    to: [backend, shared]
  - from: backend
    to: [shared]
```

## Synchronization Patterns

### Eventually Consistent

```javascript
{
    "sync": {
        "strategy": "eventual",
        "max-lag": "5m",
        "retry": {
            "attempts": 3,
            "backoff": "exponential"
        }
    }
}
```

### Strongly Consistent

```javascript
{
    "sync": {
        "strategy": "strong",
        "consensus": "raft",
        "quorum": 0.51,
        "timeout": "30s"
    }
}
```

### Hybrid Approach

```javascript
{
    "sync": {
        "default": "eventual",
        "overrides": {
            "security-updates": "strong",
            "dependency-updates": "strong",
            "documentation": "eventual"
        }
    }
}
```

## MCP Tool Integration

### Swarm Coordination

```javascript
mcp__claude-flow__swarm_init({
    topology: "hierarchical",
    maxAgents: 10,
    strategy: "balanced"
})

mcp__claude-flow__github_sync_coord({
    repos: ["org/frontend", "org/backend", "org/shared"]
})
```

### Memory for Multi-Repo State

```javascript
mcp__claude-flow__memory_usage({
    action: "store",
    key: "multi-repo/sync/status",
    namespace: "coordination",
    value: JSON.stringify({
        lastSync: Date.now(),
        repos: {
            frontend: { status: "synced", version: "2.0.0" },
            backend: { status: "synced", version: "2.1.0" },
            shared: { status: "synced", version: "1.5.0" }
        }
    })
})
```

### Metrics Collection

```javascript
mcp__claude-flow__github_metrics({
    repos: ["org/frontend", "org/backend"],
    metrics: ["commits", "prs", "issues", "contributors"]
})
```

## Use Cases

### Microservices Coordination

```bash
npx ruv-swarm github microservices \
  --services "auth,users,orders,payments" \
  --ensure-compatibility \
  --sync-contracts \
  --integration-tests
```

### Library Updates

```bash
npx ruv-swarm github lib-update \
  --library "org/shared-lib" \
  --version "2.0.0" \
  --find-consumers \
  --update-imports \
  --run-tests
```

### Organization-Wide Changes

```bash
npx ruv-swarm github org-policy \
  --policy "add-security-headers" \
  --repos "org/*" \
  --validate-compliance \
  --create-reports
```

## Best Practices

### 1. Repository Organization
- Clear repository roles and boundaries
- Consistent naming conventions
- Documented dependencies
- Shared configuration standards

### 2. Communication
- Use appropriate sync strategies
- Implement circuit breakers
- Monitor latency and failures
- Clear error propagation

### 3. Security
- Secure cross-repo authentication
- Encrypted communication channels
- Audit trail for all operations
- Principle of least privilege

## Monitoring and Visualization

### Multi-Repo Dashboard

```bash
npx ruv-swarm github multi-repo-dashboard \
  --port 3000 \
  --metrics "agent-activity,task-progress,memory-usage" \
  --real-time
```

### Dependency Graph

```bash
npx ruv-swarm github dep-graph \
  --format mermaid \
  --include-agents \
  --show-data-flow
```

### Health Monitoring

```bash
npx ruv-swarm github health-check \
  --repos "org/*" \
  --check "connectivity,memory,agents" \
  --alert-on-issues
```

## Troubleshooting

### Connectivity Issues

```bash
npx ruv-swarm github diagnose-connectivity \
  --test-all-repos \
  --check-permissions \
  --verify-webhooks
```

### Memory Synchronization

```bash
npx ruv-swarm github debug-memory \
  --check-consistency \
  --identify-conflicts \
  --repair-state
```

---

## Version History

- **1.0.0** (2025-01-02): Initial release - converted from multi-repo-swarm agent
