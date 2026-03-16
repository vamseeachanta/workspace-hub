---
name: agent-orchestration-1-code-review-swarm
description: 'Sub-skill of agent-orchestration: 1. Code Review Swarm (+2).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# 1. Code Review Swarm (+2)

## 1. Code Review Swarm


```javascript
// Initialize review swarm
    topology: "hierarchical",
    maxAgents: 4
});

// Spawn review agents
    agents: [
        { type: "reviewer", name: "security-reviewer" },
        { type: "reviewer", name: "performance-reviewer" },

*See sub-skills for full details.*

## 2. Feature Implementation


```javascript
// Sequential SPARC workflow

// Phase agents
const phases = [
    { type: "specialist", name: "specification-agent" },
    { type: "specialist", name: "pseudocode-agent" },
    { type: "architect", name: "architecture-agent" },
    { type: "coder", name: "implementation-agent" },
    { type: "tester", name: "testing-agent" }

*See sub-skills for full details.*

## 3. Research and Analysis


```javascript
// Mesh for collaborative research

    agents: [
        { type: "researcher", name: "literature-reviewer" },
        { type: "analyst", name: "data-analyst" },
        { type: "documenter", name: "summary-writer" }
    ]
});

    task: "Research and analyze best practices for microservices",
    strategy: "adaptive"
});
```
