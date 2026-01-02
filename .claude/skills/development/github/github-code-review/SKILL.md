---
name: github-code-review
description: Deploy specialized AI agents to perform comprehensive, intelligent code reviews that go beyond traditional static analysis. Use for automated multi-agent review, security vulnerability analysis, performance bottleneck detection, and architecture pattern validation.
---

# GitHub Code Review Skill

## Overview

Deploy specialized AI agents for comprehensive code reviews. This skill provides multi-agent review capabilities covering security vulnerabilities, performance bottlenecks, architecture patterns, and code style enforcement.

## Quick Start

```bash
# Get PR details for review
gh pr view 123 --json files,additions,deletions,title,body

# Get PR diff
gh pr diff 123

# Post review comment
gh pr review 123 --comment --body "Review findings..."

# Approve PR
gh pr review 123 --approve --body "LGTM!"

# Request changes
gh pr review 123 --request-changes --body "Please fix..."
```

## When to Use

- Automated code review for pull requests
- Security vulnerability analysis
- Performance bottleneck detection
- Architecture pattern validation
- Style and convention enforcement
- Multi-agent collaborative review

## Review Agents

### Security Agent

| Check | Description |
|-------|-------------|
| SQL injection | Detect SQL injection vulnerabilities |
| XSS | Cross-site scripting attack vectors |
| Authentication | Auth bypasses and flaws |
| Cryptographic | Weak crypto implementations |
| Secrets | Exposed credentials or API keys |
| CORS | Misconfiguration issues |

### Performance Agent

| Metric | Description |
|--------|-------------|
| Algorithm complexity | Big-O analysis |
| Query efficiency | N+1 queries, slow queries |
| Memory patterns | Allocation and leaks |
| Cache utilization | Caching opportunities |
| Bundle size | Impact on bundle size |

### Style Agent

| Check | Description |
|-------|-------------|
| Code formatting | Consistent formatting |
| Naming conventions | Variable/function naming |
| Documentation | Comment quality |
| Test coverage | Missing tests |
| Error handling | Proper error patterns |

### Architecture Agent

| Pattern | Description |
|---------|-------------|
| SOLID principles | Single responsibility, etc. |
| DRY violations | Code duplication |
| Coupling metrics | Component dependencies |
| Layer violations | Architecture boundaries |
| Circular dependencies | Dependency cycles |

## Usage Examples

### 1. Multi-Agent Review System

```bash
# Get PR details
PR_DATA=$(gh pr view 123 --json files,additions,deletions,title,body)
PR_DIFF=$(gh pr diff 123)

# Initialize swarm with PR context
npx ruv-swarm github review-init \
  --pr 123 \
  --pr-data "$PR_DATA" \
  --diff "$PR_DIFF" \
  --agents "security,performance,style,architecture" \
  --depth comprehensive

# Post initial review status
gh pr comment 123 --body "Multi-agent code review initiated"
```

### 2. Security-Focused Review

```bash
# Get changed files
CHANGED_FILES=$(gh pr view 123 --json files --jq '.files[].path')

# Run security review
SECURITY_RESULTS=$(npx ruv-swarm github review-security \
  --pr 123 \
  --files "$CHANGED_FILES" \
  --check "owasp,cve,secrets,permissions" \
  --suggest-fixes)

# Post findings based on severity
if echo "$SECURITY_RESULTS" | grep -q "critical"; then
  gh pr review 123 --request-changes --body "$SECURITY_RESULTS"
  gh pr edit 123 --add-label "security-review-required"
else
  gh pr comment 123 --body "$SECURITY_RESULTS"
fi
```

### 3. Initialize Review Swarm

```javascript
// Initialize code review swarm
mcp__claude-flow__swarm_init({ topology: "hierarchical", maxAgents: 5 })
mcp__claude-flow__agent_spawn({ type: "reviewer", name: "Security Reviewer" })
mcp__claude-flow__agent_spawn({ type: "reviewer", name: "Performance Reviewer" })
mcp__claude-flow__agent_spawn({ type: "reviewer", name: "Style Reviewer" })
mcp__claude-flow__agent_spawn({ type: "architect", name: "Architecture Reviewer" })

// Orchestrate parallel review
mcp__claude-flow__task_orchestrate({
    task: "Comprehensive code review covering security, performance, style, and architecture",
    strategy: "parallel",
    priority: "high"
})
```

### 4. Post Inline Comments

```bash
# Get diff with context
PR_DIFF=$(gh pr diff 123 --color never)
PR_FILES=$(gh pr view 123 --json files)

# Generate review comments
COMMENTS=$(npx ruv-swarm github review-comment \
  --pr 123 \
  --diff "$PR_DIFF" \
  --files "$PR_FILES" \
  --style "constructive" \
  --include-examples \
  --suggest-fixes)

# Post inline comments
echo "$COMMENTS" | jq -c '.[]' | while read -r comment; do
  FILE=$(echo "$comment" | jq -r '.path')
  LINE=$(echo "$comment" | jq -r '.line')
  BODY=$(echo "$comment" | jq -r '.body')

  gh api \
    --method POST \
    /repos/owner/repo/pulls/123/comments \
    -f path="$FILE" \
    -f line="$LINE" \
    -f body="$BODY" \
    -f commit_id="$(gh pr view 123 --json headRefOid -q .headRefOid)"
done
```

## Review Configuration

```yaml
# .github/review-swarm.yml
version: 1
review:
  auto-trigger: true
  required-agents:
    - security
    - performance
    - style
  optional-agents:
    - architecture
    - accessibility
    - i18n

  thresholds:
    security: block
    performance: warn
    style: suggest

  rules:
    security:
      - no-eval
      - no-hardcoded-secrets
      - proper-auth-checks
    performance:
      - no-n-plus-one
      - efficient-queries
      - proper-caching
    architecture:
      - max-coupling: 5
      - min-cohesion: 0.7
      - follow-patterns
```

## MCP Tool Integration

### Swarm Coordination

```javascript
// Initialize review swarm
mcp__claude-flow__swarm_init({
    topology: "hierarchical",
    maxAgents: 5,
    strategy: "specialized"
})

// Spawn specialized reviewers
mcp__claude-flow__agents_spawn_parallel({
    agents: [
        { type: "reviewer", name: "security-agent", capabilities: ["security-audit"] },
        { type: "reviewer", name: "perf-agent", capabilities: ["performance-analysis"] },
        { type: "reviewer", name: "style-agent", capabilities: ["code-style"] }
    ]
})
```

### Memory for Review State

```javascript
// Store review findings
mcp__claude-flow__memory_usage({
    action: "store",
    key: "review/pr-123/findings",
    value: JSON.stringify({
        security: { issues: 2, severity: "medium" },
        performance: { issues: 1, severity: "low" },
        style: { issues: 5, severity: "info" }
    })
})
```

## GitHub Actions Integration

```yaml
# .github/workflows/auto-review.yml
name: Automated Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  swarm-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Setup GitHub CLI
        run: echo "${{ secrets.GITHUB_TOKEN }}" | gh auth login --with-token

      - name: Run Review Swarm
        run: |
          PR_NUM=${{ github.event.pull_request.number }}
          PR_DATA=$(gh pr view $PR_NUM --json files,title,body,labels)

          REVIEW_OUTPUT=$(npx ruv-swarm github review-all \
            --pr $PR_NUM \
            --pr-data "$PR_DATA" \
            --agents "security,performance,style,architecture")

          echo "$REVIEW_OUTPUT" | gh pr review $PR_NUM --comment -F -

          if echo "$REVIEW_OUTPUT" | grep -q "approved"; then
            gh pr review $PR_NUM --approve
          elif echo "$REVIEW_OUTPUT" | grep -q "changes-requested"; then
            gh pr review $PR_NUM --request-changes -b "See review comments above"
          fi
```

## Comment Templates

### Security Issue

```markdown
**Security Issue: [Type]**

**Severity**: Critical / High / Low

**Description**:
[Clear explanation of the security issue]

**Impact**:
[Potential consequences if not addressed]

**Suggested Fix**:
```language
[Code example of the fix]
```

**References**:
- [OWASP Guide](link)
```

### Performance Issue

```markdown
**Performance Issue: [Type]**

**Impact**: [Expected performance degradation]

**Current**:
```language
[Current code]
```

**Suggested**:
```language
[Optimized code]
```
```

## Best Practices

### 1. Review Configuration
- Define clear review criteria
- Set appropriate thresholds
- Configure agent specializations
- Establish override procedures

### 2. Comment Quality
- Provide actionable feedback
- Include code examples
- Reference documentation
- Maintain respectful tone

### 3. Performance
- Cache analysis results
- Incremental reviews for large PRs
- Parallel agent execution
- Smart comment batching

---

## Version History

- **1.0.0** (2025-01-02): Initial release - converted from code-review-swarm agent
