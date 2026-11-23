---
name: github-repo-architect-monorepo-structure
description: 'Sub-skill of github-repo-architect: Monorepo Structure (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Monorepo Structure (+2)

## Monorepo Structure


```
project-root/
├── packages/
│   ├── package-a/
│   │   ├── src/
│   │   ├── .claude/
│   │   └── package.json
│   ├── package-b/
│   │   ├── src/
│   │   └── package.json

*See sub-skills for full details.*

## Command Structure


```
.claude/
├── commands/
│   ├── github/
│   │   ├── github-modes.md
│   │   ├── pr-manager.md
│   │   └── issue-tracker.md
│   ├── sparc/
│   │   ├── sparc-modes.md
│   │   └── coder.md

*See sub-skills for full details.*

## Integration Pattern


```javascript
const integrationPattern = {
    packages: {
            role: "orchestration_layer",
            dependencies: ["ruv-swarm"],
            provides: ["CLI", "workflows", "commands"]
        },
        "ruv-swarm": {
            role: "coordination_engine",
            dependencies: [],

*See sub-skills for full details.*
