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
  required_iterations: 3
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

## First-Pass Implemented Paths

- Canonical skill: `.claude/skills/workspace-hub/resource-intelligence/SKILL.md`
- Source-registry reference: `.claude/skills/workspace-hub/resource-intelligence/references/source-registry.md`
- Resource-pack scaffolder: `.claude/skills/workspace-hub/resource-intelligence/scripts/init-resource-pack.sh`
- Resource-pack validator: `.claude/skills/workspace-hub/resource-intelligence/scripts/validate-resource-pack.sh`
- Maturity sync/check: `.claude/skills/workspace-hub/resource-intelligence/scripts/sync-maturity-summary.py`
- Summary template: `.claude/skills/workspace-hub/resource-intelligence/templates/resource-intelligence-summary.md`
- Mounted-source registry: `data/document-index/mounted-source-registry.yaml`
- Maturity ledger: `data/document-index/resource-intelligence-maturity.yaml`
- Maturity summary: `data/document-index/resource-intelligence-maturity.md`
- Legal scan evidence: `.claude/work-queue/assets/WRK-655/legal-scan.md`

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

## Routing Capability Review Requirement

Before `agent-router` and `agent-usage-optimizer` are treated as authority for stage assignment, this WRK should produce one of:

1. a formal reviewed capability matrix covering routing, quota awareness, fallback behavior, and operational limits
2. an explicit interim-routing rule stating:
   - what those skills are allowed to influence
   - what remains user- or orchestrator-judgment
   - what evidence is required when overriding recommendations

Selected first-pass decision:

- use the interim-routing rule first
- `agent-router` is advisory for agent fit
- `agent-usage-optimizer` is advisory for quota/capacity
- the orchestrator retains final routing authority during the first implementation pass
- overrides or deviations should be recorded in WRK evidence when they materially affect execution

This first-pass routing decision is adopted for `WRK-655`; it is no longer an open blocker for this item.

## Scope

### Phase 1: Skill Design and Contract Definition

**Objective**: Define the canonical `Resource Intelligence` skill and the exact stage contract it implements.

**Tasks**:
- [ ] Create a new canonical `resource-intelligence` skill under `.claude/skills/`
- [ ] Define trigger conditions and invocation guidance
- [ ] Define required artifact outputs and minimum section requirements
- [ ] Define the visible knowledge map and role mapping
- [ ] Define `P1/P2/P3` ranking semantics and user pause behavior
- [ ] Define whether an existing skill is enhanced or a new canonical skill is created
- [ ] Review `agent-router` and `agent-usage-optimizer` as routing-capability authorities or document an interim rule

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
- [x] Create the canonical skill under `.claude/skills/workspace-hub/resource-intelligence/`
- [ ] Add references/scripts/assets only where they materially reduce ad hoc behavior
- [ ] Download relevant codes, standards, and online documents discovered during intelligence gathering only when they complement existing document-intelligence sources
- [ ] Record downloaded-source provenance in `resources.yaml`:
  - [ ] source URL or origin
  - [ ] license/access status
  - [ ] retrieval date
  - [ ] canonical storage path
  - [ ] duplicate or superseded relationship if applicable
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
- [x] Skill implementation
- [x] Resource-pack scaffolding
- [x] Stage summary template
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
- [ ] Define how additive downloaded-source storage is validated without duplicating existing document-intelligence sources
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
  - downloaded where licensing and access allow and only when they add value beyond already-available document-intelligence sources
  - documented in the document-intelligence system
  - placed in the relevant long-term reference location for future reuse
  - recorded with provenance and duplicate/superseded status
- Repository intelligence should compound over time rather than remain flatter than external document intelligence.
- Target maturity window: `3 months`
- Success metric:
  - `>80%` of tracked Resource-Intelligence documents in scope are marked `read`
  - key calculations derived from those documents are implemented in the repository ecosystem or explicitly linked to follow-on WRKs
- "Richer than document intelligence" means the repository can answer common planning/implementation questions through curated local knowledge, implemented calculations, prior decisions, and validated interpretations without re-reading raw source documents in most cases.
- The target direction is that repository intelligence becomes richer and more useful than raw document intelligence alone because it accumulates:
  - curated context
  - prior decisions
  - reusable patterns
  - validated local interpretations
  - cross-WRK learnings

## Repository-Native Example Set

These examples should be used to validate the stage against realistic `workspace-hub` sources:

1. `AGENTS.md` as the canonical agent contract source
2. `.claude/work-queue/process.md` as lifecycle/process source
3. `specs/wrk/WRK-624/plan.md` as the governing workflow spec
4. `assets/WRK-624/wrk-624-workflow-review.html` as the user-review surface
5. `scripts/work-queue/validate-queue-state.sh` as validator source
6. `scripts/work-queue/claim-item.sh` as claim-stage implementation source
7. `scripts/work-queue/close-item.sh` as close-stage implementation source
8. `.claude/skills/coordination/orchestration/agent-router/SKILL.md` as routing-authority input
9. `.claude/skills/ai/agent-usage-optimizer/SKILL.md` as quota-authority input
10. `.claude/skills/data/documents/document-rag-pipeline/SKILL.md` as document-intelligence pipeline input

## Current Document-Intelligence Assets and Source Mapping

Current document-intelligence assets already present in `workspace-hub`:

| Asset | Path | Role |
|---|---|---|
| Registry | `data/document-index/registry.yaml` | Source-bucket counts and aggregate registry |
| Main index | `data/document-index/index.jsonl` | Queryable document-intelligence index |
| Backup index | `data/document-index/index.jsonl.bak` | Safety copy of the main index |
| Shards | `data/document-index/shards/` | Sharded source-index inputs |
| Summaries | `data/document-index/summaries/` | Per-document summary artifacts |
| Transfer ledger | `data/document-index/standards-transfer-ledger.yaml` | Standards transfer tracking |
| Enhancement plan | `data/document-index/enhancement-plan.yaml` | Index improvement planning artifact |

Observed indexed source buckets:

| Source bucket | Example path | Likely mount/root class |
|---|---|---|
| `ace_project` | `/mnt/ace/docs/K07NL17002-M00-IA-A-REP-00037_1.pdf` | local mounted drive |
| `ace_standards` | `/mnt/ace/docs/_standards/og_standards_api_search.txt` | local mounted drive |
| `og_standards` | `/mnt/ace/0000 O&G/0000 Codes & Standards/Codes & Standards Database.xls` | local mounted drive |
| `dde_project` | `/mnt/remote/ace-linux-2/dde/documents/0000 Personal/11511/11511 Repair Analysis.pptx` | remote mounted drive |
| `workspace_spec` | `/mnt/local-analysis/workspace-hub/specs/archive/legacy-agent-os/product/decisions.md` | local workspace |
| `api_metadata` | `api://worldenergydata/BSEE` | API source |

Implication for `WRK-655`:

- mounted and remote-mounted sources are already part of the indexed estate
- the remaining gap is an explicit source-registry contract, not discovery from zero
- this WRK should map source buckets to canonical mount roots and storage policy rather than redefining document intelligence itself

## Proposed Mounted-Source Registry Schema

To close the remaining gap, the Resource Intelligence stage should define a registry row or YAML object with:

- `source_id`
- `document_intelligence_bucket`
- `mount_root`
- `local_or_remote`
- `index_artifact_ref`
- `registry_ref`
- `canonical_storage_policy`
- `provenance_rule`
- `dedup_rule`
- `availability_check_ref`

Registry location decision:

- use the best-structured location as long as it remains clearly linked to:
  - `data/document-index/registry.yaml`
  - `data/document-index/index.jsonl`
  - the relevant long-term reference locations
- preferred implementation:
  - a dedicated mounted-source registry file beside the existing document-intelligence registry
  - cross-linked from the main registry and from Resource Intelligence documentation

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

5. Example-based validation tests
- [ ] `AGENTS.md` only path produces a valid minimal resource pack
- [ ] `WRK-624` spec + HTML path produces a workflow-focused resource pack
- [ ] scripts-only path (`validate-queue-state.sh`, `claim-item.sh`, `close-item.sh`) produces implementation-grounded constraints
- [ ] routing-skills path (`agent-router`, `agent-usage-optimizer`) produces a capability-review note or interim-routing rule
- [ ] mixed local + additive online-source path records provenance and duplicate status correctly

Minimum first-pass execution cases:

1. `AGENTS.md`
2. `specs/wrk/WRK-624/plan.md`
3. `scripts/work-queue/validate-queue-state.sh`
4. `.claude/skills/coordination/orchestration/agent-router/SKILL.md`
5. one remote-mounted `dde_project` example

## File-Level Change Plan

- [ ] Create or update the canonical skill under `.claude/skills/`
- [ ] Add any needed references/scripts/assets for that skill
- [ ] Update `WRK-624` references once the skill path is final
- [ ] Add validator notes or follow-on hooks if immediate enforcement is not yet part of this WRK

## Review Strategy

- Route C review with provider diversity: Claude, Codex, Gemini
- Route C seed depth: `3 seeds/provider`
- Full-bundle review is preferred because this is workflow/governance work
- Review should focus on:
  - whether the skill contract is too vague
  - whether the knowledge map is sufficient but not bloated
  - whether `P1` pause logic is operationally clear
  - whether validator-readiness is concrete enough for later enforcement
  - whether additive downloaded-source rules are precise enough to avoid storage drift
  - whether the 3-month intelligence metric is concrete enough to track
  - whether the routing-authority decision needs full review now or should stay open pending more context

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
- [ ] `agent-router` and `agent-usage-optimizer` are formally reviewed for routing/quota authority or bounded by an explicit interim rule
- [ ] Validator-ready rules are documented for minimum stage completion
- [ ] `WRK-624` references are updated to point at the new skill contract
- [ ] Relevant online codes, standards, and documents are added only as complements to existing document-intelligence sources, documented with provenance, and placed in the appropriate long-term reference location
- [ ] The plan defines a 3-month repository-intelligence maturity target and tracking method
- [ ] The plan includes repository-native example cases for validating the stage
- [ ] Legal scan passes

## Tracking Artifacts

The 3-month maturity target should be tracked through both:

1. a YAML ledger as the source of truth
2. a linked Markdown summary for human review

Contract:

- Markdown must link to the YAML ledger directly
- YAML remains the canonical state artifact
- Markdown may summarize, but must not diverge from the YAML record

First-pass enforcement:

- `sync-maturity-summary.py` generates the Markdown summary from the YAML ledger
- `sync-maturity-summary.py --check` fails if the Markdown summary has drifted

## Decisions Adopted

1. Canonical skill path:
   - `.claude/skills/workspace-hub/resource-intelligence/SKILL.md`
2. Mounted-source registry model:
   - dedicated linked registry at `data/document-index/mounted-source-registry.yaml`
3. Tracking pair:
   - YAML ledger + linked Markdown summary
4. Routing authority for first pass:
   - interim-routing rule first
