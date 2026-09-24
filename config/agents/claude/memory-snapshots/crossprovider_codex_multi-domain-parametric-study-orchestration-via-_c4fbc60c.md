---
name: crossprovider codex multi-domain-parametric-study-orchestration-via-
description: Multi-domain parametric study orchestration via enum dispatch
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [orchestration, parametric, architecture, design-pattern, extensibility]
---

Single coordinator entry point with StudyType enum (WALL_THICKNESS, FATIGUE, ORCAFLEX_CAMPAIGN, COMBINED_WT_FATIGUE) dispatches to specialized parametric sweeps. Each domain has a params dataclass with __post_init__ validation; orchestrator composes results into unified report. Extensible for new domain types without modifying router logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
