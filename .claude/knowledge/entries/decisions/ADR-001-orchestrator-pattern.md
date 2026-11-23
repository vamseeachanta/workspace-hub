---
id: ADR-001
type: decision
title: "Use orchestrator pattern for all execution"
category: architecture
tags: [orchestrator, delegation, subagents, context-management]
repos: [workspace-hub]
confidence: 1.0
created: "2026-01-30"
last_validated: "2026-01-30"
source_type: manual
related: [PAT-001]
status: active
access_count: 0
---

# Use Orchestrator Pattern for All Execution

## Context

Claude Code CLI sessions have limited context windows. Running verbose commands (tests, builds, searches) directly in the main session pollutes context and causes drift. Complex multi-step tasks require coordination without the orchestrator losing track of the overall goal.

## Decision

The main Claude Code instance acts as orchestrator only - it plans and coordinates but never executes complex tasks directly. All execution is delegated to subagents via the Task tool. The orchestrator stays lean at less than 20% context usage.

## Rationale

- Subagents isolate context pollution - their output doesn't consume orchestrator context
- Failed subagents can be discarded without losing orchestrator state
- Parallel subagents enable concurrent execution
- The orchestrator maintains a clear view of overall progress
- Consistent delegation pattern reduces cognitive load

## Consequences

- Every task requires explicit delegation decision (slight overhead for trivial tasks)
- Subagents lack shared context - each must receive sufficient instructions
- Debugging requires checking subagent output rather than seeing inline results
- More structured but less ad-hoc workflow
