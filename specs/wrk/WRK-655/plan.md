---
title: "WRK-655 Resource Intelligence Skill and Stage Contract"
description: "Route C plan to operationalize Resource Intelligence as a first-class skill with a validator-ready artifact contract, gap-ranking model, and user-review pause behavior."
version: "0.1.0"
module: "work-queue"
session:
  id: "wrk-655-codex-20260228"
  agent: "codex"
  started: "2026-02-28T00:00:00Z"
  last_active: "2026-02-28T00:00:00Z"
  conversation_id: "wrk-655"
review:
  required_iterations: 1
  current_iteration: 0
  status: "draft"
  reviewers:
    claude:
      status: "pending"
      iteration: 0
      last_reviewed: ""
      feedback: ""
    openai_codex:
      status: "drafted"
      iteration: 0
      last_reviewed: "2026-02-28"
      feedback: "Initial Route C plan draft prepared."
    google_gemini:
      status: "pending"
      iteration: 0
      last_reviewed: ""
      feedback: ""
    legal_sanity:
      status: "pending"
      iteration: 0
      violations: 0
  approval_gate:
    min_iterations_met: false
    claude_approved: false
    codex_approved: false
    gemini_approved: false
    legal_sanity_passed: false
    ready_for_next_step: false
status: "draft"
progress: 15
phase: 1
blocked_by: []
created: "2026-02-28"
updated: "2026-02-28"
target_completion: "2026-03-07"
timeline: "phased rollout"
author: "codex"
reviewers:
  - claude
  - codex
  - gemini
assignees:
  - codex
technical:
  language: "markdown+bash+python"
  python_version: ">=3.10"
  dependencies:
    - "skill system"
    - "work-queue scripts"
    - "legal-sanity scan"
    - "document-intelligence skills"
  test_coverage: 80
  platforms:
    - linux
priority: "high"
complexity: "critical"
risk: "medium"
tags:
  - workflow
  - work-queue
  - skills
  - resource-intelligence
  - document-intelligence
links:
  spec: "/mnt/local-analysis/workspace-hub/specs/wrk/WRK-655/plan.md"
  docs:
    - "/mnt/local-analysis/workspace-hub/specs/wrk/WRK-624/plan.md"
    - "/mnt/local-analysis/workspace-hub/assets/WRK-624/wrk-624-workflow-review.html"
    - "/mnt/local-analysis/workspace-hub/.claude/skills/coordination/workspace/work-queue/SKILL.md"
history:
  - date: "2026-02-28"
    action: "created"
    by: "codex"
    notes: "Drafted Route C plan for the Resource Intelligence skill and stage contract."
---

# WRK-655 Resource Intelligence Skill and Stage Contract

> **Module**: work-queue | **Status**: draft | **Priority**: high
> **Created**: 2026-02-28 | **Target**: 2026-03-07

## Executive Summary

`WRK-655` turns `Resource Intelligence` from policy into an operational stage. The immediate goal is to make the stage executable through a first-class skill, inspectable through a visible skill map, and enforceable through a validator-ready artifact contract.

The current `WRK-624` workflow already says `Resource Intelligence` must exist, must rank gaps, and must pause when unresolved `P1` gaps remain. What is missing is the reusable machinery that makes different agents follow the same path. This item delivers that machinery.

The output of this work is not just one new skill file. It is a coherent stage definition spanning: skill trigger rules, artifact scaffolding, `P1/P2/P3` gap handling, user pause semantics, repo/document-intelligence integration, legal-scan proof, and validator-ready completion criteria.

## Problem Statement

`Resource Intelligence` is currently the loosest stage in the workflow:

- the stage is defined in `WRK-624`, but not yet implemented as a dedicated skill
- the artifact set is described, but not yet consistently scaffolded or validated
- the user pause rule is present in policy, but not yet operationalized in one reusable stage flow
- the knowledge sources are known, but not yet organized into a visible, tweakable skill map
- repo context, document intelligence, prior learnings, legal scan, and later comprehensive-learning handoff are still stitched together manually
- codes, standards, and relevant online documents are not yet systematically downloaded, indexed, and stored in the right long-term reference locations

That looseness causes the stage to drift toward ad hoc research behavior, which weakens plan quality and makes later validation harder.

## Target Outcome

After `WRK-655`, a `Resource Intelligence` run for any WRK should:

1. trigger through a defined ecosystem skill
2. produce a standard artifact set
3. rank gaps as `P1/P2/P3`
4. surface unresolved `P1` gaps to the user first
5. pause for explicit user review when unresolved `P1` gaps remain
6. continue to planning only when `P1` gaps are cleared or explicitly handled
7. expose a knowledge map showing which skills and systems were used
8. leave behind artifacts that a validator can check mechanically

## Knowledge Map

| Role | Skill / System | Purpose |
|---|---|---|
| Lifecycle wrapper | `work-queue` | Keeps the stage aligned with WRK lifecycle artifacts and transitions |
| Domain scoping | `engineering-context-loader` | Narrows the domain-relevant skills, standards, and memory/spec context |
| Repo/document scan | `document-inventory` | Catalogs local document sets before deeper processing |
| Document intelligence | `document-rag-pipeline` | Builds searchable context when source volume or ambiguity justifies it |
| Prior learnings | `knowledge-manager` | Surfaces prior decisions, patterns, corrections, and gotchas |
| Legal gate | `legal-sanity` | Checks imported/generated artifacts for sensitive content |
| Agent fit | `agent-router` | Helps select the right model mix for later plan/review work |
| Quota awareness | `agent-usage-optimizer` | Keeps downstream claim/review work within available capacity |
| Deep learning handoff | `comprehensive-learning` | Consumes stage outputs later for slower ecosystem synthesis |

## Scope

### Phase 1: Skill Design and Contract Definition

**Objective**: Define the canonical `Resource Intelligence` skill and the exact stage contract it implements.

**Tasks**:
- [ ] Decide whether to enhance an existing skill or create a new canonical `resource-intelligence` skill
- [ ] Define trigger conditions and invocation guidance
- [ ] Define required artifact outputs and minimum section requirements
- [ ] Define the visible knowledge map and role mapping
- [ ] Define `P1/P2/P3` ranking semantics and user pause behavior

**Deliverables**:
- [ ] Skill design decision
- [ ] Stage contract document
- [ ] Gap-ranking contract

**Exit Criteria**:
- [ ] The stage can be described as one repeatable skill-driven workflow
- [ ] The user-facing pause rule is unambiguous

### Phase 2: Skill Implementation and Artifact Scaffolding

**Objective**: Implement the skill and create reusable scaffolding for stage artifacts.

**Tasks**:
- [ ] Create or update the canonical skill under `.claude/skills/`
- [ ] Add references/scripts/assets only where they materially reduce ad hoc behavior
- [ ] Download relevant codes, standards, and online documents discovered during intelligence gathering
- [ ] Place downloaded source documents in the relevant long-term repo/document reference locations
- [ ] Record those sources in document intelligence so they remain searchable and reusable
- [ ] Define or add scaffolding for:
  - [ ] `resource-pack.md`
  - [ ] `sources.md`
  - [ ] `constraints.md`
  - [ ] `domain-notes.md`
  - [ ] `open-questions.md`
  - [ ] `resources.yaml`
- [ ] Define the user-facing stage summary format including top `P1` gaps and continue/pause decision

**Deliverables**:
- [ ] Skill implementation
- [ ] Resource-pack scaffolding
- [ ] Stage summary template
- [ ] Downloaded and documented standards / online reference set

**Exit Criteria**:
- [ ] An agent can execute the stage via the skill rather than hand-rolling the process
- [ ] The skill map is visible and tweakable

### Phase 3: Validator-Ready Rules and Workflow Integration

**Objective**: Make the stage mechanically checkable and wire it back into the workflow.

**Tasks**:
- [ ] Define minimum pass conditions for stage completion
- [ ] Define where legal-scan proof is stored
- [ ] Define how document-intelligence indexing is recorded
- [ ] Define validator checks for artifact presence and minimum completeness
- [ ] Update workflow references to point at the new skill contract

**Deliverables**:
- [ ] Validator-ready stage rules
- [ ] Updated workflow references
- [ ] Integration notes for follow-on enforcement work

**Exit Criteria**:
- [ ] The stage can be validated consistently across WRKs
- [ ] `WRK-624` references the new skill contract cleanly

## Gap Priority Model

### `P1` gaps

These block stage pass and must be shown to the user first:

- missing or weak source coverage
- missing legal-scan result when required
- unclear or contradictory problem context
- no credible path to required repo/domain knowledge
- missing artifact required for minimum stage completion

### `P2` gaps

These materially weaken planning, but do not force an automatic stop unless they accumulate:

- incomplete constraints
- stale repo knowledge
- unresolved open questions with medium planning impact
- partial or weak document-intelligence coverage

### `P3` gaps

These are useful enhancements rather than blockers:

- optional ecosystem learnings
- extra indexing or enrichment
- broader but non-essential source expansion

### User pause rule

- unresolved `P1` gaps -> present `pause and revise`
- no unresolved `P1` gaps -> present `continue to planning`

## Intelligence Growth Requirement

- As part of intelligence gathering, relevant codes, standards, and documents found online should be:
  - downloaded where licensing and access allow
  - documented in the document-intelligence system
  - placed in the relevant long-term reference location for future reuse
- Repository intelligence should compound over time rather than remain flatter than external document intelligence.
- The target direction is that, within a defined future maturity window, repository intelligence becomes richer and more useful than raw document intelligence alone because it accumulates:
  - curated context
  - prior decisions
  - reusable patterns
  - validated local interpretations
  - cross-WRK learnings

## Testing Strategy

1. Stage-path tests
- [ ] skill can be invoked from a WRK context
- [ ] artifact set is generated as expected

2. Gap-ranking tests
- [ ] `P1` gaps surface first
- [ ] unresolved `P1` gaps trigger pause output
- [ ] no `P1` gaps permits continue output

3. Validator-readiness tests
- [ ] minimum artifact presence can be checked mechanically
- [ ] legal-scan proof path is resolvable
- [ ] document-intelligence indexing record is resolvable when used

4. Workflow integration tests
- [ ] `WRK-624` references can point at the skill cleanly
- [ ] follow-on workflow docs remain coherent

## File-Level Change Plan

- [ ] Create or update the canonical skill under `.claude/skills/`
- [ ] Add any needed references/scripts/assets for that skill
- [ ] Update `WRK-624` references once the skill path is final
- [ ] Add validator notes or follow-on hooks if immediate enforcement is not yet part of this WRK

## Review Strategy

- Route C review with provider diversity: Claude, Codex, Gemini
- Full-bundle review is preferred because this is workflow/governance work
- Review should focus on:
  - whether the skill contract is too vague
  - whether the knowledge map is sufficient but not bloated
  - whether `P1` pause logic is operationally clear
  - whether validator-readiness is concrete enough for later enforcement

## Rollback Strategy

- If the new skill contract is too broad or unstable, keep `WRK-624` stage language and narrow the skill to a smaller wrapper first
- If validator-ready rules prove premature, keep them documented but advisory and defer hard enforcement to follow-on workflow items
- Do not remove existing `WRK-624` stage language unless the replacement skill contract is at least equally explicit

## Acceptance Criteria

- [ ] Resource Intelligence executes through a defined skill, not ad hoc instructions
- [ ] Skill defines required artifacts for `resource-pack.md`, `sources.md`, `constraints.md`, `domain-notes.md`, `open-questions.md`, and `resources.yaml`
- [ ] Skill defines a visible `P1/P2/P3` gap-ranking model
- [ ] Skill defines user-pause behavior for unresolved `P1` gaps
- [ ] Stage knowledge map is documented and easy for the user to inspect/tweak
- [ ] Validator-ready rules are documented for minimum stage completion
- [ ] `WRK-624` references are updated to point at the new skill contract
- [ ] Relevant online codes, standards, and documents are downloaded, documented in document intelligence, and placed in the appropriate long-term reference location
- [ ] The plan defines how repository intelligence should grow over time beyond raw document intelligence
- [ ] Legal scan passes
