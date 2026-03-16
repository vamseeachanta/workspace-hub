---
name: core-researcher-example-1-codebase-analysis
description: 'Sub-skill of core-researcher: Example 1: Codebase Analysis (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Example 1: Codebase Analysis (+1)

## Example 1: Codebase Analysis


```javascript
// Analyze authentication system
Task("Researcher", "Analyze auth module architecture and patterns", "researcher")

// Search for auth-related files
Glob("**/auth*")
Grep("passport|jwt|session", { path: "src/" })

// Document findings
  action: "store",

*See sub-skills for full details.*

## Example 2: Dependency Mapping


```javascript
// Map all dependencies for a module
Task("Researcher", "Map dependencies for user-service module", "researcher")

// Find imports
Grep("^import.*from", { path: "src/user-service/" })

// Find exports
Grep("^export", { path: "src/user-service/" })


*See sub-skills for full details.*
