---
name: resource-intelligence
description: Execute the Resource Intelligence stage for a WRK item using a standard
  artifact pack, P1/P2/P3 gap ranking, source-registry awareness, and a user pause/continue
  decision.
version: 1.1.0
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
- mining_checklist
- category_mining_map
tools:
- Read
- Write
- Edit
- Bash
- Grep
- Glob
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
- resource-intelligence-required-outputs
- resource-intelligence-required-outputs
- resource-intelligence-micro-skill-checklist-stage-16
- resource-intelligence-resource-mining-checklist
- resource-intelligence-categorymining-map
- resource-intelligence-targetrepospaths
- resource-intelligence-gap-ranking
- resource-intelligence-first-pass-routing-rule
- resource-intelligence-source-rules
- resource-intelligence-step-by-step-for-authors
- resource-intelligence-templates-and-scripts
tags: []
---

# Resource Intelligence

## Version History

- **1.1.1** (2026-03-07): Codex review fixes (WRK-1029)
  - stage-02 changed from chained_agent → task_agent (stop guard was contradicted by chained_stages)
  - Category→Mining Map: added `uncategorised` row
  - Stage 16 Micro-Skill Checklist added (was missing, only Stage 2 had one)
  - stage-16 blocking_condition: `lessons[]` → `additions[] and no_additions_rationale`
- **1.1.0** (2026-03-07): Stage 2/16 alignment with WRK-1028 stage isolation contract (WRK-1029)
  - `evidence/resource-intelligence.yaml` added as primary gate-passing exit artifact for Stage 2
  - `evidence/resource-intelligence-update.yaml` confirmed as Stage 16 gate artifact
  - `resource-intelligence-summary.md` retained as required companion (consumers unchanged)
  - Separate Stage 2 / Stage 16 sections with distinct checklists and stop guards
  - Stage 2 micro-skill checklist: 8 items including path setup and hard stop on artifacts
  - Resource Mining Checklist: 9 ordered categories (Skills → Online/additive)
  - Category→Mining Map: WRK `category` values mapped to mining priorities
  - target_repos→Paths: per-repo inventory path table
  - Schema: gate-verified fields distinguished from recommended/WARN fields
  - `domain.problem` and `domain.architecture_decision`: required in schema, WARN in gatepass
- **1.0.0** (2026-02-xx): Initial release

## Sub-Skills

- [Required Outputs (+2)](required-outputs/SKILL.md)
- [Required Outputs (+1)](required-outputs/SKILL.md)
- [Micro-Skill Checklist (Stage 16)](micro-skill-checklist-stage-16/SKILL.md)
- [Resource Mining Checklist](resource-mining-checklist/SKILL.md)
- [Category→Mining Map](categorymining-map/SKILL.md)
- [target_repos→Paths](targetrepospaths/SKILL.md)
- [Gap Ranking](gap-ranking/SKILL.md)
- [First-Pass Routing Rule](first-pass-routing-rule/SKILL.md)
- [Source Rules](source-rules/SKILL.md)
- [Step-by-Step for Authors (+2)](step-by-step-for-authors/SKILL.md)
- [Templates and Scripts](templates-and-scripts/SKILL.md)
