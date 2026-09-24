---
name: sparc-pseudocode
description: SPARC Pseudocode phase specialist for algorithm design, data structure
  selection, complexity analysis, and design pattern identification
version: 1.0.0
category: development
type: hybrid
capabilities:
- algorithm_design
- logic_flow
- data_structures
- complexity_analysis
- pattern_selection
tools:
- Read
- Write
- Edit
- Grep
- Glob
related_skills:
- sparc-specification
- sparc-architecture
- sparc-refinement
hooks:
  pre: 'echo "SPARC Pseudocode phase initiated"

    memory_store "sparc_phase" "pseudocode"

    # Retrieve specification from memory

    memory_search "spec_complete" | tail -1

    '
  post: 'echo "Pseudocode phase complete"

    memory_store "pseudo_complete_$(date +%s)" "Algorithms designed"

    '
requires: []
tags: []
---

# Sparc Pseudocode

## Quick Start

```bash
# Invoke SPARC Pseudocode phase

# Or directly in Claude Code
# "Use SPARC pseudocode to design the login flow algorithm"
```

## When to Use

- Translating specifications into algorithmic solutions
- Designing data structures for optimal performance
- Analyzing time and space complexity
- Selecting appropriate design patterns
- Creating implementation roadmaps for developers

## Prerequisites

- Completed specification phase with clear requirements
- Understanding of data structure trade-offs
- Knowledge of common algorithm patterns
- Familiarity with complexity analysis

## Core Concepts

### SPARC Pseudocode Phase

The Pseudocode phase bridges specifications and implementation:

1. **Design algorithmic solutions** - Language-agnostic logic
2. **Select optimal data structures** - Based on access patterns
3. **Analyze complexity** - Time and space requirements
4. **Identify design patterns** - Reusable solutions
5. **Create implementation roadmap** - Guide for developers
### Complexity Classes

| Class | Description | Example |
|-------|-------------|---------|
| O(1) | Constant | Hash lookup |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Array scan |
| O(n log n) | Linearithmic | Merge sort |
| O(n^2) | Quadratic | Nested loops |

## Implementation Pattern

### Algorithm Structure

```
ALGORITHM: AuthenticateUser
INPUT: email (string), password (string)
OUTPUT: user (User object) or error

BEGIN
    // Validate inputs
    IF email is empty OR password is empty THEN
        RETURN error("Invalid credentials")
    END IF

*See sub-skills for full details.*
### Data Structure Selection

```
DATA STRUCTURES:

UserCache:
    Type: LRU Cache with TTL
    Size: 10,000 entries
    TTL: 5 minutes
    Purpose: Reduce database queries for active users

    Operations:

*See sub-skills for full details.*
### Algorithm Patterns

```
PATTERN: Rate Limiting (Token Bucket)

ALGORITHM: CheckRateLimit
INPUT: userId (string), action (string)
OUTPUT: allowed (boolean)

CONSTANTS:
    BUCKET_SIZE = 100
    REFILL_RATE = 10 per second

*See sub-skills for full details.*

## Metrics & Success Criteria

- All algorithms have documented complexity
- Subroutines are clearly defined
- Data structures are justified with operations
- Design patterns are identified where applicable
- Pseudocode is language-agnostic

## Integration Points

### MCP Tools

```javascript
// Store pseudocode phase completion
  action: "store",
  key: "sparc/pseudocode/algorithms",
  namespace: "coordination",
  value: JSON.stringify({
    algorithms: ["AuthenticateUser", "CheckRateLimit"],
    patterns: ["strategy", "observer"],
    complexity: "O(log n)",
    timestamp: Date.now()
  })
}
```
### Hooks

```bash
# Pre-pseudocode hook

# Post-pseudocode hook
```
### Related Skills

- [sparc-specification](../sparc-specification/SKILL.md) - Previous phase: requirements
- [sparc-architecture](../sparc-architecture/SKILL.md) - Next phase: system design
- [sparc-refinement](../sparc-refinement/SKILL.md) - TDD implementation phase

## References

- [Big O Notation](https://en.wikipedia.org/wiki/Big_O_notation)
- [Design Patterns](https://refactoring.guru/design-patterns)

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from agent to skill format

## Sub-Skills

- [Configuration](configuration/SKILL.md)
- [Example 1: Search Algorithm (+2)](example-1-search-algorithm/SKILL.md)
- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
