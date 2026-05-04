---
name: github-release-swarm-swarm-coordination
description: 'Sub-skill of github-release-swarm: Swarm Coordination (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Swarm Coordination (+1)

## Swarm Coordination


```javascript
    topology: "hierarchical",
    maxAgents: 6,
    strategy: "sequential"
})

    tasks: [
        { task: "generate-changelog", agent: "changelog-agent" },
        { task: "build-artifacts", agent: "build-agent" },
        { task: "run-tests", agent: "test-agent" }

*See sub-skills for full details.*

## Memory for Release State


```javascript
    action: "store",
    key: "release/v2.0.0/state",
    value: JSON.stringify({
        stage: "testing",
        changelog: "generated",
        artifacts: ["npm", "docker"],
        tests: "running"
    })
})
```
