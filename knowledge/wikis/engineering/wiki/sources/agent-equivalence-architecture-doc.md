---
title: "Agent Equivalence Architecture (Source)"
tags: [source, agents, equivalence, architecture]
source_path: docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md
source_type: module-doc
ingested: 2026-04-08
---

# Source: Agent Equivalence Architecture

**Path**: `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`

## Summary

Architecture document for providing workflow-equivalent behavior across Claude Code, Codex CLI, and Gemini CLI. Defines the orchestrator/subagent session model, source of truth locations, and provider-neutral wrapper scripts.

## Key Extractions

- **Session rule**: provider where session starts = orchestrator; others = subagents
- **Source of truth**: GitHub issues + approved `.planning/` artifacts
- **Wrapper scripts**: `session.sh`, `work.sh`, `plan.sh`, `execute.sh`, `review.sh`
- **Review normalization**: `normalize-verdicts.sh` maps to APPROVE/MINOR/MAJOR/NO_OUTPUT/ERROR

## Pages Created From This Source

- [Agent Delegation](../concepts/agent-delegation.md)
- [Orchestrator-Worker Separation](../concepts/orchestrator-worker-separation.md)
