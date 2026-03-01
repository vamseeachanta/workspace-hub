---
title: "WRK-664 Multi-Agent and Multi-Workstation Execution Contract"
description: "Route C plan to add deterministic stage-level agent/workstation assignment, machine-readiness gates, and remote coordination policy to the work-queue workflow."
version: "0.1.0"
module: "work-queue"
status: "draft"
created: "2026-03-01"
updated: "2026-03-01"
author: "codex"
reviewers:
  - claude
  - codex
  - gemini
priority: "high"
complexity: "complex"
tags:
  - workflow
  - work-queue
  - orchestration
  - workstations
  - agent-routing
---

# WRK-664 Multi-Agent and Multi-Workstation Execution Contract

## Executive Summary

`WRK-624` established lifecycle gates and `WRK-655` established Resource Intelligence contract quality. The remaining gap is deterministic execution routing across agents and machines. This plan defines stage-level assignment rules so each WRK can declare:

1. which AI agent is primary/secondary per stage
2. which workstation(s) are required per stage
3. what must pass before claim and execution
4. what evidence is required for machine handoff and remote coordination

This item stays parked until activation, but planning artifacts are prepared now so it can be resumed without redesign.

## Problem

Current workflow captures `provider`, `orchestrator`, and `computer`, but lacks a strict per-stage contract for multi-machine work. That creates risk for:

- license-bound work (for example, specific workstation-only tools)
- tasks requiring parallel runs on multiple machines
- mid-item handoffs between machines
- failed execution due to missing machine capability or unavailable remote access

## Target Outcome

Every active WRK can carry a machine-readable assignment contract:

- stage assignment matrix (`PLAN`, `CLAIM`, `EXECUTE`, `REVIEW`, `CLOSE`)
- required capabilities by stage
- workstation allocation by stage (single or list)
- fallback behavior when assigned machine is unavailable
- explicit pause/replan rules

## Stage Assignment Contract (Draft)

| Stage | Primary Agent | Secondary Agent | Workstation Scope | Required Gate |
|---|---|---|---|---|
| Resource Intelligence | claude | gemini | `ace-linux-1` | sources + legal + summary contract valid |
| Plan Draft | codex | claude | `ace-linux-1` | plan schema valid + HTML draft generated |
| Plan Cross-Review | claude/codex/gemini | - | any AI-capable host | required seed runs complete |
| Claim | orchestrator | agent-router + agent-usage-optimizer (advisory) | `ace-linux-1` | quota snapshot + routing evidence recorded |
| Execute | stage-assigned best-fit | alternate provider | assigned execution machines | machine capability + readiness pass |
| Cross-Review (impl) | claude/codex/gemini | - | any AI-capable host | route policy satisfied |
| Close/Archive | orchestrator | codex | `ace-linux-1` | queue validation + sync checks pass |

## Workstation Contract (Draft)

### Required fields (WRK frontmatter or linked assignment file)

- `orchestrator`
- `provider`
- `provider_alt`
- `computer` (single or list)
- `stage_assignments_ref` (new)
- `machine_capability_requirements` (new)
- `handoff_evidence_ref` (new, when multi-machine)

### Machine-readiness checks before execute

1. machine listed in `workstations` registry
2. required tools present
3. license state acceptable (if needed)
4. disk/network prerequisites met
5. fallback defined if unavailable

## Remote Coordination Policy (Draft)

- Remote execution is allowed only when:
  - machine assignment is explicit
  - task needs capabilities not present locally
  - handoff evidence is recorded
- If remote coordination is unavailable:
  - pause and surface gap as `P1`
  - propose alternate machine or defer path

## Phased Rollout

### Phase 1: Contract Definition
- define assignment schema and stage matrix
- define required evidence and fallback behavior

### Phase 2: Workflow Integration
- update work-queue templates/scripts to include new fields
- integrate checks with `workstations`, `agent-router`, and `agent-usage-optimizer`

### Phase 3: Validation
- apply to at least 3 representative WRKs
- verify pass/fail behavior for unavailable-machine scenarios

## Acceptance Criteria

- [ ] Route C plan approved with stage assignment matrix
- [ ] assignment schema fields finalized and documented
- [ ] machine-readiness gate defined and testable
- [ ] remote coordination policy defined with pause/fallback behavior
- [ ] 3 representative WRKs validated against contract
- [ ] HTML review surface includes assignment matrix and top gaps

## Decision Needed Now

1. Keep this item parked until activation window opens
2. Activate immediately and move to `pending`/`working`

## Parked State

This WRK remains intentionally parked (`status: blocked`) until you explicitly activate it.
