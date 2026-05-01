# Archived Skill: `delegate-task-4-lane-workaround`

Original path: `/home/vamsee/.hermes/skills/coordination/delegate-task-4-lane-workaround`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/delegate-task-4-lane-workaround`
Consolidation date: 2026-04-29

---

---
name: delegate-task-4-lane-workaround
description: Work around delegate_task batch concurrency cap when the user wants four parallel review lanes.
version: 1.0.0
author: Hermes Agent
category: coordination
tags: [delegate_task, parallelism, adversarial-review, queue-sweeps, subagents]
---

# Delegate Task 4-Lane Workaround

Use when the user explicitly wants 4 parallel subagent lanes, but a single `delegate_task(tasks=[...])` batch fails because the environment is capped at `delegation.max_concurrent_children=3`.

## Problem

In this environment, sending 4 tasks in one `delegate_task(tasks=[...])` call can fail with an error like:

`Too many tasks: 4 provided, but max_concurrent_children is 3.`

This happens before any task starts, so you do not get an automatic queue or partial execution.

## Reliable workaround

To preserve true 4-lane parallelism:

1. Put 3 tasks into one batched `delegate_task(tasks=[...])` call.
2. Put the 4th task into a separate single-task `delegate_task(goal=...)` call.
3. Launch those two delegate calls in parallel from the parent agent.
   - If available, use `multi_tool_use.parallel`.
4. Keep delegated tasks read-only when possible (`terminal`, `file`) and have the parent session do all persistent writes, GitHub comments, and artifact creation.

## Best fit

This pattern is especially useful for:
- adversarial plan-review sweeps
- issue triage across multiple independent items
- read-only repo audits where each lane produces a verdict or checklist

## Example pattern

Parent launches in parallel:
- Call A: `delegate_task(tasks=[task1, task2, task3])`
- Call B: `delegate_task(goal=task4)`

Then the parent:
- aggregates the returned summaries
- writes canonical review artifacts
- posts GitHub comments
- updates local tracking docs

## Why this is better than serial fallback

If the user asked for "4 at a time," dropping to 3 serially changes throughput and intent. Splitting into `3 + 1` preserves the requested concurrency without requiring config changes.

## Cautions

- Do not use delegated children for repo writes you need to persist.
- Be explicit about paths, issue numbers, and output schema because child summaries are compressed.
- If the task is data-gathering-heavy rather than reasoning-heavy, prefer `execute_code` instead of more subagents.
- Treat subagent timeouts as recoverable orchestration failures, not task failure. If one or more read-only lanes time out, immediately continue in the parent with direct `gh`/git/search/read-file grounding for the missing facts, then record which lanes timed out in the handoff. Do not let a timed-out research lane block obvious safe closeout actions that have been independently verified in the parent session.
