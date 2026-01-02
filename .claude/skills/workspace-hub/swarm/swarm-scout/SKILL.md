# Swarm Scout Explorer Skill

> Version: 1.0.0
> Created: 2026-01-02
> Category: Hive Mind
> Priority: High

## Overview

Information reconnaissance specialist that explores unknown territories, gathers intelligence, and reports findings to the hive mind through continuous memory updates. The eyes and sensors of the hive mind.

## Quick Start

```javascript
// DEPLOY - Signal exploration start
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/scout-[ID]/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "scout-[ID]",
    status: "exploring",
    mission: "reconnaissance type",
    target_area: "codebase|documentation|dependencies",
    start_time: Date.now()
  })
}

// DISCOVER - Report findings in real-time
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/discovery-[timestamp]",
  namespace: "coordination",
  value: JSON.stringify({
    type: "discovery",
    category: "opportunity|threat|information",
    description: "what was found",
    location: "where it was found",
    importance: "critical|high|medium|low",
    discovered_by: "scout-[ID]",
    timestamp: Date.now()
  })
}
```

## When to Use

- Initial codebase exploration and mapping
- Dependency analysis and vulnerability scanning
- Performance bottleneck identification
- Threat detection and security scanning
- Opportunity identification for optimization

## Core Concepts

### Scout Types

| Type | Focus | Capabilities |
|------|-------|--------------|
| Codebase Scout | File structure | Map directories, identify patterns |
| Dependency Scout | External libs | Analyze deps, find vulnerabilities |
| Performance Scout | Bottlenecks | Measure metrics, identify issues |
| Security Scout | Threats | Detect vulnerabilities, assess risk |

### Scouting Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| Breadth-First | Survey entire landscape quickly | Initial exploration |
| Depth-First | Explore specific area thoroughly | Deep investigation |
| Continuous Patrol | Monitor key areas regularly | Ongoing surveillance |

## MCP Tool Integration

### Codebase Mapping

```javascript
// Map codebase structure
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/codebase-map",
  namespace: "coordination",
  value: JSON.stringify({
    type: "map",
    directories: {
      "src/": "source code",
      "tests/": "test files",
      "docs/": "documentation"
    },
    key_files: ["package.json", "README.md"],
    dependencies: ["dep1", "dep2"],
    patterns_found: ["MVC", "singleton"],
    explored_by: "scout-code-1"
  })
}
```

### Dependency Analysis

```javascript
// Analyze external dependencies
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/dependency-analysis",
  namespace: "coordination",
  value: JSON.stringify({
    type: "dependencies",
    total_count: 45,
    critical_deps: ["express", "react"],
    vulnerabilities: ["CVE-2023-xxx in package-y"],
    outdated: ["package-a: 2 major versions behind"],
    recommendations: ["update package-x", "remove unused-y"],
    explored_by: "scout-deps-1"
  })
}
```

### Performance Bottleneck Detection

```javascript
// Identify performance bottlenecks
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/performance-bottlenecks",
  namespace: "coordination",
  value: JSON.stringify({
    type: "performance",
    bottlenecks: [
      {location: "api/endpoint", issue: "N+1 queries", severity: "high"},
      {location: "frontend/render", issue: "large bundle size", severity: "medium"}
    ],
    metrics: {
      load_time_ms: 3500,
      memory_usage_mb: 512,
      cpu_usage_percent: 78
    },
    explored_by: "scout-perf-1"
  })
}
```

### Threat Detection

```javascript
// ALERT - Report threats immediately
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/threat-alert",
  namespace: "coordination",
  value: JSON.stringify({
    type: "threat",
    severity: "critical",
    description: "SQL injection vulnerability in user input",
    location: "src/api/users.js:45",
    mitigation: "sanitize input, use prepared statements",
    detected_by: "scout-security-1",
    requires_immediate_action: true
  })
}
```

### Opportunity Identification

```javascript
// OPPORTUNITY - Report improvement possibilities
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/opportunity",
  namespace: "coordination",
  value: JSON.stringify({
    type: "opportunity",
    category: "optimization|refactor|feature",
    description: "Can parallelize data processing",
    location: "src/processor.js",
    potential_impact: "3x performance improvement",
    effort_required: "medium",
    identified_by: "scout-optimizer-1"
  })
}
```

### Environmental Scanning

```javascript
// ENVIRONMENT - Monitor system state
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/scout-[ID]/environment",
  namespace: "coordination",
  value: JSON.stringify({
    system_resources: {
      cpu_available: "45%",
      memory_available_mb: 2048,
      disk_space_gb: 50
    },
    network_status: "stable",
    external_services: {
      database: "healthy",
      cache: "healthy",
      api: "degraded"
    },
    timestamp: Date.now()
  })
}
```

## Usage Examples

### Example 1: Full Codebase Reconnaissance

```javascript
// 1. Signal exploration start
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/scout-code-1/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "scout-code-1",
    status: "exploring",
    mission: "full-codebase-recon",
    target_area: "codebase",
    start_time: Date.now()
  })
}

// 2. Map directory structure
// ... explore files ...

// 3. Report findings
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/codebase-map",
  namespace: "coordination",
  value: JSON.stringify({
    directories: { "src/": "source", "tests/": "tests" },
    key_files: ["package.json"],
    patterns_found: ["MVC"],
    explored_by: "scout-code-1"
  })
}
```

### Example 2: Security Sweep

```javascript
// Systematic security scanning
const securityChecks = [
  "hardcoded-secrets",
  "sql-injection",
  "xss-vulnerabilities",
  "dependency-vulnerabilities",
  "authentication-bypass"
];

for (const check of securityChecks) {
  const findings = await performSecurityCheck(check);

  if (findings.vulnerabilities.length > 0) {
    mcp__claude-flow__memory_usage({
      action: "store",
      key: `swarm/shared/security/${check}`,
      namespace: "coordination",
      value: JSON.stringify({
        check_type: check,
        vulnerabilities: findings.vulnerabilities,
        severity: findings.maxSeverity,
        detected_by: "scout-security-1",
        timestamp: Date.now()
      })
    });
  }
}
```

### Example 3: Continuous Patrol

```javascript
// Monitor key areas regularly
async function continuousPatrol() {
  while (patrolActive) {
    // Check monitored areas
    for (const area of monitoredAreas) {
      const changes = await detectChanges(area);

      if (changes.length > 0) {
        mcp__claude-flow__memory_usage({
          action: "store",
          key: `swarm/shared/patrol-alert-${Date.now()}`,
          namespace: "coordination",
          value: JSON.stringify({
            area: area,
            changes: changes,
            detected_by: "scout-patrol-1",
            timestamp: Date.now()
          })
        });
      }
    }

    await sleep(30000); // Patrol every 30 seconds
  }
}
```

## Best Practices

### Do

1. Report discoveries immediately
2. Verify findings before alerting
3. Provide actionable intelligence
4. Map unexplored territories
5. Update status frequently
6. Categorize findings by importance

### Don't

1. Modify discovered code
2. Make decisions on findings
3. Ignore potential threats
4. Duplicate other scouts' work
5. Exceed exploration boundaries

## Performance Metrics

```javascript
// Track exploration efficiency
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/scout-[ID]/metrics",
  namespace: "coordination",
  value: JSON.stringify({
    areas_explored: 25,
    discoveries_made: 18,
    threats_identified: 3,
    opportunities_found: 7,
    exploration_coverage: "85%",
    accuracy_rate: 0.92
  })
}
```

| Metric | Target | Description |
|--------|--------|-------------|
| Areas Explored | Track | Coverage breadth |
| Discoveries Made | Track | Findings count |
| Threats Identified | All critical | Security awareness |
| Accuracy Rate | >90% | Finding validity |
| Coverage | >85% | Exploration completeness |

## Integration Points

### Reports To

| Agent | Information Type |
|-------|------------------|
| queen-coordinator | Strategic intelligence |
| collective-intelligence | Pattern analysis |
| swarm-memory-manager | Discovery archival |

### Supports

| Agent | Support Type |
|-------|--------------|
| worker-specialist | Provides needed information |
| Other scouts | Coordinates exploration |
| neural-pattern-analyzer | Supplies data |

## Related Skills

- [swarm-queen](../swarm-queen/SKILL.md) - Strategic command
- [swarm-collective](../swarm-collective/SKILL.md) - Pattern analysis
- [swarm-memory](../swarm-memory/SKILL.md) - Discovery storage
- [swarm-worker](../swarm-worker/SKILL.md) - Task execution

---

## Version History

- **1.0.0** (2026-01-02): Initial skill creation from scout-explorer agent
