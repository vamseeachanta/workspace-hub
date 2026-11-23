---
name: workflow-governance-assessment
version: 1.0.0
category: coordination
description: Class-level workflow governance, enforcement audits, and multi-tool architecture assessment.
tags: [governance, architecture, audit, workflow]
---

# Workflow Governance Assessment

## When to Use
Use when auditing enforcement infrastructure, comparing competing tool architectures, deciding governance upgrades for multi-agent workflows, or evaluating whether human approval gates can safely evolve into evidence-threshold / self-cycling agent gates.

## Class-Level Workflow
1. Map current enforcement points before proposing new controls.
2. Compare tools by workflow fit, failure modes, maintainability, and verification burden.
3. For hard-gate relaxation, define measurable thresholds before changing authority: repeated APPROVE/MINOR adversarial reviews with no unresolved MAJOR findings, passing legal/provenance scans, TDD evidence before implementation, passing verification after implementation, artifact-to-acceptance-criteria alignment, low user rework rate, no unauthorized label/status mutations, no secret/client-identifying leakage, and reproducible logs/artifacts.
4. Keep existing hard gates authoritative until the threshold evidence is proven over multiple cycles; then relax only the narrow gate covered by evidence.
5. Convert findings into bounded follow-up issues rather than open-ended audits.

## Gate Evolution Principle

The target operating model is not permanent user-managed orchestration. As agent rigor becomes consistently measurable, routine issue decomposition, plan drafting, adversarial review, legal/provenance checks, test design, implementation, verification, closeout evidence, and queue feeding should self-cycle. The user should increasingly focus on idea origination, GTM throughput, customer/prospect artifacts, and strategic approvals. Do not remove gates by assertion; replace them with threshold metrics and audit trails that provide confidence.

## Consolidated Session Learnings

Narrow skills absorbed during the 2026-04-29 umbrella consolidation are preserved under `references/`.
## Absorbed Narrow Skills (2026-04-29)

### `enforcement-audit-and-upgrade`

- Former skill demoted to `references/enforcement-audit-and-upgrade.md`.
- Preserved insight: Audit existing enforcement infrastructure, identify gaps between advisory and strict modes, create hard-gate scripts, and incrementally roll out enforcement. Pattern from #1876/#2017 enforcement audit session.

### `multi-tool-architecture-assessment`

- Former skill demoted to `references/multi-tool-architecture-assessment.md`.
- Preserved insight: Systematic comparison of competing tools/approaches before committing to a multi-account, multi-tool architecture. Uses parallel subagents for research, system-state audit, and data quality analysis. Produces a decision matrix with explicit trade-offs.
