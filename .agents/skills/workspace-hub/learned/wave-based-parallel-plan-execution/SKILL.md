---
name: wave-based-parallel-plan-execution
description: Orchestrate phase execution by discovering dependencies, grouping into waves, spawning subagents, and collecting results with optional wave filtering
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["orchestration", "parallel-execution", "phase-management", "subagent-coordination"]
---

# Wave-Based Parallel Plan Execution

When executing multiple interdependent plans in a phase, use wave-based parallelization: orchestrator discovers all plans, analyzes dependencies, groups non-blocking plans into waves, spawns subagents (each with full execute-plan context), and collects results. Optional `--wave N` flag enables staged rollout or quota management. Phase verification only completes when no incomplete plans remain after the final wave finishes.