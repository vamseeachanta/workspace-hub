---
name: resource-intelligence
description: Execute the Resource Intelligence stage for a WRK item using a standard artifact pack, P1/P2/P3 gap ranking, source-registry awareness, and a user pause/continue decision.
version: 1.0.0
category: workspace-hub
type: skill
trigger: manual
auto_execute: false
capabilities:
  - wrk_resource_pack_generation
  - gap_ranking
  - source_registry_awareness
  - document_intelligence_linking
  - legal_scan_evidence
  - user_pause_gate
tools: [Read, Write, Edit, Bash, Grep, Glob]
related_skills:
  - work-queue
  - engineering-context-loader
  - document-inventory
  - document-rag-pipeline
  - knowledge-manager
  - legal-sanity
  - agent-router
  - agent-usage-optimizer
  - comprehensive-learning
requires: []
see_also:
  - references/source-registry.md
  - templates/resource-intelligence-summary.md
  - scripts/init-resource-pack.sh
---

# Resource Intelligence

Use this skill to execute the `Resource Intelligence` stage for a WRK item. The goal is to produce a standard artifact pack and a clear user decision:

- `pause_and_revise`
- `continue_to_planning`

## When to Use

- After WRK capture and before planning is treated as ready
- When a WRK needs repo context, source mapping, standards/documents, constraints, and open questions gathered in one repeatable way
- When the user asks for Resource Intelligence explicitly

## Required Outputs

Create or update these files under `.claude/work-queue/assets/WRK-<id>/`:

- `resource-pack.md`
- `sources.md`
- `constraints.md`
- `domain-notes.md`
- `open-questions.md`
- `resources.yaml`
- `resource-intelligence-summary.md`

## Core Workflow

1. Resolve the WRK item and read its current plan/spec.
2. Inventory existing repo-native sources first.
3. Check `data/document-index/registry.yaml`, `data/document-index/index.jsonl`, and `data/document-index/mounted-source-registry.yaml`.
4. Add complementary online sources only when they add value beyond current indexed sources.
5. Record source provenance and storage policy in `resources.yaml`.
6. Run or record legal-sanity evidence if needed.
7. Rank gaps as `P1`, `P2`, `P3`.
8. Write `resource-intelligence-summary.md` with the user decision.

## Gap Ranking

- `P1`: blocks stage pass
- `P2`: weakens planning materially
- `P3`: enhancement only

Use this rubric when classifying gaps:

- `P1`: the stage cannot safely continue because a required artifact, source, legal gate, or core context is missing or contradictory
- `P2`: the stage can continue, but planning quality or repeatability is materially weakened
- `P3`: the stage remains valid; the gap only improves ergonomics, automation depth, or future scale

If any unresolved `P1` gaps remain, the summary must say `pause_and_revise`.
If no unresolved `P1` gaps remain, the summary may say `continue_to_planning`.

## First-Pass Routing Rule

For the first implementation pass:

- `agent-router` is advisory for agent fit only
- `agent-usage-optimizer` is advisory for quota and capacity only
- the orchestrator retains final routing authority
- if the orchestrator deviates materially from these advisories, the WRK should record the override reason and risk acceptance in its evidence artifacts

## Source Rules

- Prefer repo-native and already-indexed sources first.
- Treat downloaded documents as additive complements, not replacements.
- Every downloaded source must record:
  - origin
  - license/access status
  - retrieval date
  - canonical storage path
  - duplicate/superseded status
  - status (`available` | `source_unavailable`)
  - fallback evidence when `status: source_unavailable`

## Source Registry

Read `references/source-registry.md` before adding or changing source-root mappings.

## Templates and Script

- Summary template: `templates/resource-intelligence-summary.md`
- Resource-pack scaffolder: `scripts/init-resource-pack.sh`
- Resource-pack validator: `scripts/validate-resource-pack.sh`
- Maturity sync/check: `scripts/sync-maturity-summary.py`

Use the scaffolder when starting a new WRK resource pack instead of hand-creating files.
Run the validator before treating the stage as passable.
