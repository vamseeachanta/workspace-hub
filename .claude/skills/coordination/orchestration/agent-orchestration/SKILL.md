---
name: agent-orchestration
description: Orchestrate AI agents using Claude Flow, swarm coordination, and multi-agent
  workflows. Use for complex tasks requiring multiple specialized agents, parallel
  execution, or coordinated problem-solving.
version: 1.1.0
category: coordination
type: skill
capabilities:
- swarm_coordination
- agent_spawning
- task_orchestration
- memory_management
- parallel_execution
tools:
- Task
- Bash
related_skills:
- sparc-workflow
- repo-sync
- compliance-check
hooks:
  pre: ''
  post: ''
requires: []
see_also:
- agent-orchestration-core-agents
- agent-orchestration-hierarchical
- agent-orchestration-spawn-single-agent
- agent-orchestration-simple-task
- agent-orchestration-1-code-review-swarm
- agent-orchestration-execution-checklist
- agent-orchestration-check-swarm-status
- agent-orchestration-store-information
- agent-orchestration-agent-spawn-failures
- agent-orchestration-metrics-success-criteria
- agent-orchestration-topology-selection
- agent-orchestration-using-task-tool
- agent-orchestration-mcp-tools
- agent-orchestration-destroy-swarm
tags: []
---

# Agent Orchestration

## Quick Start

```javascript
// Initialize a swarm for complex task

// Spawn specialized agents
    agents: [
        { type: "coder", name: "backend" },
        { type: "tester", name: "qa" },
        { type: "reviewer", name: "quality" }
    ]
})

// Orchestrate the task
    task: "Build REST API with tests",
    strategy: "adaptive"
})
```

## When to Use

- Complex tasks requiring multiple specialized agents (coder, tester, reviewer)
- Parallel execution to speed up independent subtasks
- Code review requiring multiple perspectives (security, performance, style)
- Research tasks needing distributed information gathering
- Cross-repository changes requiring coordinated commits

## Prerequisites

- Understanding of swarm topologies
- Familiarity with agent types and capabilities
- Claude Code Task tool for agent execution

## Overview

This skill enables orchestration of multiple AI agents for complex tasks. It covers swarm initialization, agent spawning, task coordination, and multi-agent workflows using Claude Flow and the workspace-hub agent ecosystem.

## References

- [AI Agent Guidelines](../docs/modules/ai/AI_AGENT_GUIDELINES.md)
- [Development Workflow](../docs/modules/workflow/DEVELOPMENT_WORKFLOW.md)

---

## Version History

- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format - added Quick Start, When to Use, Execution Checklist, Error Handling consolidation, Metrics, Integration Points, MCP hooks
- **1.0.0** (2024-10-15): Initial release with swarm topologies, agent spawning, task orchestration, memory management, performance optimization

## Sub-Skills

- [Agent Selection (+2)](agent-selection/SKILL.md)

## Sub-Skills

- [Core Agents (+3)](core-agents/SKILL.md)
- [Hierarchical (+3)](hierarchical/SKILL.md)
- [Spawn Single Agent (+2)](spawn-single-agent/SKILL.md)
- [Simple Task (+2)](simple-task/SKILL.md)
- [1. Code Review Swarm (+2)](1-code-review-swarm/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Check Swarm Status (+3)](check-swarm-status/SKILL.md)
- [Store Information (+2)](store-information/SKILL.md)
- [Agent Spawn Failures (+3)](agent-spawn-failures/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [Topology Selection (+2)](topology-selection/SKILL.md)
- [Using Task Tool (+1)](using-task-tool/SKILL.md)
- [MCP Tools (+2)](mcp-tools/SKILL.md)
- [Destroy Swarm (+1)](destroy-swarm/SKILL.md)
