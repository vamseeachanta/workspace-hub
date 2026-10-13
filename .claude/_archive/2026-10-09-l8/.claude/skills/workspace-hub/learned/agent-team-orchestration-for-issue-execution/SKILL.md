---
name: agent-team-orchestration-for-issue-execution
description: Parallelize research, synthesize findings in main context, spawn independent reviewer, then commit—a structured 4-phase execution pattern for complex deliverables.
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["orchestration", "multi-agent", "code-execution", "quality-gate", "github-workflow"]
---

# Agent-Team Orchestration for Issue Execution

When executing a complex issue with multiple deliverables, spawn parallel agents for Phase A (research/validation), synthesize findings in your main context for Phase B (writing), spawn an independent reviewer for Phase C (who hasn't seen drafting), and commit in Phase D. This pattern ensures research parallelization, high-quality synthesis (where context density matters), and genuinely independent review validation. Pre-commit gates can be verified early to unblock the write phase.