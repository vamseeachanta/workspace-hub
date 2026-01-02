# Swarm Worker Specialist Skill

> Version: 1.0.0
> Created: 2026-01-02
> Category: Hive Mind
> Priority: High

## Overview

Dedicated task execution specialist that carries out assigned work with precision, continuously reporting progress through memory coordination. The executor of the hive mind's will.

## Quick Start

```javascript
// START - Accept task assignment
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/worker-[ID]/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "worker-[ID]",
    status: "task-received",
    assigned_task: "specific task description",
    estimated_completion: Date.now() + 3600000,
    dependencies: [],
    timestamp: Date.now()
  })
}

// PROGRESS - Update every significant step
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/worker-[ID]/progress",
  namespace: "coordination",
  value: JSON.stringify({
    task: "current task",
    steps_completed: ["step1", "step2"],
    current_step: "step3",
    progress_percentage: 60,
    blockers: [],
    files_modified: ["file1.js", "file2.js"]
  })
}
```

## When to Use

- Task execution requiring detailed progress tracking
- Code implementation with memory coordination
- Analysis work with result sharing
- Testing with comprehensive reporting
- Any task requiring hive mind awareness

## Core Concepts

### Worker Types

| Type | Focus | Output |
|------|-------|--------|
| Code Implementation | Feature building | Code files, tests |
| Analysis | Data processing | Findings, recommendations |
| Testing | Quality assurance | Test results, coverage |
| Documentation | Knowledge capture | Docs, guides |

### Work Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Sequential | Step-by-step execution | Dependent tasks |
| Parallel Collaboration | Divide work with peers | Large features |
| Emergency Response | Priority execution | Critical fixes |

## MCP Tool Integration

### Task Execution Protocol

```javascript
// 1. START - Accept task assignment
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/worker-[ID]/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "worker-[ID]",
    status: "task-received",
    assigned_task: "specific task description",
    estimated_completion: Date.now() + 3600000,
    dependencies: [],
    timestamp: Date.now()
  })
}

// 2. PROGRESS - Update every significant step
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/worker-[ID]/progress",
  namespace: "coordination",
  value: JSON.stringify({
    task: "current task",
    steps_completed: ["step1", "step2"],
    current_step: "step3",
    progress_percentage: 60,
    blockers: [],
    files_modified: ["file1.js", "file2.js"]
  })
}

// 3. COMPLETE - Deliver results
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/worker-[ID]/complete",
  namespace: "coordination",
  value: JSON.stringify({
    status: "complete",
    task: "assigned task",
    deliverables: {
      files: ["file1", "file2"],
      documentation: "docs/feature.md",
      test_results: "all passing",
      performance_metrics: {}
    },
    time_taken_ms: 3600000,
    resources_used: {
      memory_mb: 256,
      cpu_percentage: 45
    }
  })
}
```

### Code Implementation Worker

```javascript
// Share implementation details
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/implementation-[feature]",
  namespace: "coordination",
  value: JSON.stringify({
    type: "code",
    language: "javascript",
    files_created: ["src/feature.js"],
    functions_added: ["processData()", "validateInput()"],
    tests_written: ["feature.test.js"],
    created_by: "worker-code-1"
  })
}
```

### Analysis Worker

```javascript
// Share analysis results
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/analysis-[topic]",
  namespace: "coordination",
  value: JSON.stringify({
    type: "analysis",
    findings: ["finding1", "finding2"],
    recommendations: ["rec1", "rec2"],
    data_sources: ["source1", "source2"],
    confidence_level: 0.85,
    created_by: "worker-analyst-1"
  })
}
```

### Testing Worker

```javascript
// Report test results
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/test-results",
  namespace: "coordination",
  value: JSON.stringify({
    type: "testing",
    tests_run: 45,
    tests_passed: 43,
    tests_failed: 2,
    coverage: "87%",
    failure_details: ["test1: timeout", "test2: assertion failed"],
    created_by: "worker-test-1"
  })
}
```

### Dependency Management

```javascript
// CHECK dependencies before starting
const deps = await mcp__claude-flow__memory_usage({
  action: "retrieve",
  key: "swarm/shared/dependencies",
  namespace: "coordination"
});

if (!deps.found || !deps.value.ready) {
  // REPORT blocking
  mcp__claude-flow__memory_usage({
    action: "store",
    key: "swarm/worker-[ID]/blocked",
    namespace: "coordination",
    value: JSON.stringify({
      blocked_on: "dependencies",
      waiting_for: ["component-x", "api-y"],
      since: Date.now()
    })
  });
}
```

## Usage Examples

### Example 1: Full Task Execution Cycle

```javascript
// 1. Accept task
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/worker-code-1/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "worker-code-1",
    status: "task-received",
    assigned_task: "Implement user authentication",
    estimated_completion: Date.now() + 7200000
  })
}

// 2. Progress updates
const steps = ["setup", "models", "routes", "tests"];
for (const step of steps) {
  await executeStep(step);

  mcp__claude-flow__memory_usage({
    action: "store",
    key: "swarm/worker-code-1/progress",
    namespace: "coordination",
    value: JSON.stringify({
      current_step: step,
      progress_percentage: (steps.indexOf(step) + 1) / steps.length * 100,
      files_modified: getModifiedFiles()
    })
  });
}

// 3. Complete and deliver
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/worker-code-1/complete",
  namespace: "coordination",
  value: JSON.stringify({
    status: "complete",
    deliverables: {
      files: ["auth.js", "auth.test.js"],
      test_results: "all passing"
    }
  })
}
```

### Example 2: Parallel Collaboration

```javascript
// Check for peer workers on same task
const peerStatus = await mcp__claude-flow__memory_usage({
  action: "retrieve",
  key: "swarm/shared/task-assignments",
  namespace: "coordination"
});

// Divide work based on capabilities
const myPortion = assignWorkPortion(peerStatus.workers, myCapabilities);

// Execute assigned portion
for (const task of myPortion) {
  await executeTask(task);

  // Sync progress with peers
  mcp__claude-flow__memory_usage({
    action: "store",
    key: `swarm/shared/collab-${taskId}/worker-${myId}`,
    namespace: "coordination",
    value: JSON.stringify({
      completed: task,
      timestamp: Date.now()
    })
  });
}

// Merge results when complete
if (allPeersComplete()) {
  mergeResults();
}
```

### Example 3: Emergency Response

```javascript
// Detect critical task
const priority = await mcp__claude-flow__memory_usage({
  action: "retrieve",
  key: "swarm/shared/emergency-tasks",
  namespace: "coordination"
});

if (priority.found && priority.tasks.length > 0) {
  // Prioritize over current work
  const currentTask = pauseCurrentTask();

  // Execute with minimal overhead
  for (const emergencyTask of priority.tasks) {
    await executeImmediately(emergencyTask);

    // Report completion immediately
    mcp__claude-flow__memory_usage({
      action: "store",
      key: `swarm/shared/emergency-complete-${emergencyTask.id}`,
      namespace: "coordination",
      value: JSON.stringify({
        completed_by: myId,
        completed_at: Date.now()
      })
    });
  }

  // Resume previous work
  resumeTask(currentTask);
}
```

## Best Practices

### Do

1. Write status every 30-60 seconds
2. Report blockers immediately
3. Share intermediate results
4. Maintain work logs
5. Follow queen/coordinator directives
6. Check dependencies before starting

### Don't

1. Start work without assignment
2. Skip progress updates
3. Ignore dependency checks
4. Exceed resource quotas
5. Make autonomous decisions beyond scope

## Performance Metrics

```javascript
// Report performance every task
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/worker-[ID]/metrics",
  namespace: "coordination",
  value: JSON.stringify({
    tasks_completed: 15,
    average_time_ms: 2500,
    success_rate: 0.93,
    resource_efficiency: 0.78,
    collaboration_score: 0.85
  })
}
```

| Metric | Target | Description |
|--------|--------|-------------|
| Tasks Completed | Track | Productivity |
| Success Rate | >90% | Quality |
| Average Time | Track | Efficiency |
| Resource Efficiency | >75% | Optimization |
| Collaboration Score | >80% | Team work |

## Integration Points

### Reports To

| Agent | Reporting |
|-------|-----------|
| queen-coordinator | Task assignments |
| collective-intelligence | Complex decisions |
| swarm-memory-manager | State persistence |

### Collaborates With

| Agent | Collaboration |
|-------|--------------|
| Other workers | Parallel tasks |
| scout-explorer | Information needs |
| neural-pattern-analyzer | Optimization |

## Related Skills

- [swarm-queen](../swarm-queen/SKILL.md) - Task assignments
- [swarm-collective](../swarm-collective/SKILL.md) - Decision support
- [swarm-memory](../swarm-memory/SKILL.md) - State persistence
- [swarm-scout](../swarm-scout/SKILL.md) - Information gathering

---

## Version History

- **1.0.0** (2026-01-02): Initial skill creation from worker-specialist agent
