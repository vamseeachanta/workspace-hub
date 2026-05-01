---
name: engineering-domain-reconnaissance
version: 1.0.0
category: engineering
description: "Class-level external engineering domain reconnaissance: field development, external drive ingest planning, and source-to-artifact conversion."
tags: [engineering, reconnaissance, ingest, field-development]
---

# Engineering Domain Reconnaissance

## When to Use
Use when surveying external engineering data/code/document sources, planning safe ingests, or turning field/domain reconnaissance into structured repository artifacts.

## Class-Level Workflow
1. Inventory source systems and sensitivity before copying or indexing anything.
2. Keep metadata-only sweeps separate from content extraction when confidentiality is uncertain.
3. Convert domain findings into durable repo-aligned artifacts with provenance.
4. Defer destructive moves until storage layout, naming, and rollback are clear.

## Needs-Data Unblock Review Pattern
Use this when an engineering/data-pipeline GitHub issue is already `status:plan-approved` but still has `status:needs-data`, or when the user clarifies where source data should come from.

1. Reconcile the parent issue and its explicit unblocker issue(s) before executing the parent. Verify live GitHub labels, local approval marker, latest comments, and prerequisite issues.
2. Convert the user's clarification into durable GitHub comments on both the parent and unblocker issue so future workers do not re-ask the same source/data question.
3. For local standards/code corpora such as `/mnt/ace/acma-codes`, treat the mounted corpus as source-of-record and keep raw PDFs/files out of git/wiki. Produce metadata-first or curated summary/wiki artifacts with provenance back-links to the source path.
4. For online engineering dataset backfills, state the minimum unblock schema explicitly: required fields, source URLs, confidence, and conflict handling. Keep the parent `status:needs-data` until validation proves the threshold is met.
5. Separate source-readiness from implementation readiness: do not remove `status:needs-data` or start parent implementation until the unblocker artifact exists and a small validation check passes.
6. If prerequisites split scope (for example standards routing vs source content), keep completed blockers documented but focus execution on the remaining live blocker.

## Consolidated Session Learnings

Narrow skills absorbed during the 2026-04-29 umbrella consolidation are preserved under `references/`.

## Absorbed Narrow Skills (2026-04-29)

### `field-dev-code-recon`

- Former skill demoted to `references/field-dev-code-recon.md`.
- Preserved insight: Extract field development information from external sources (LinkedIn posts, technical content), map against digitalmodel codebase coverage, document gaps, and create actionable GitHub issues.

### `external-drive-ingest-planning`

- Former skill demoted to `references/external-drive-ingest-planning.md`.
- Preserved insight: Plan safe external-drive ingests into repo-aligned storage such as /mnt/ace: read-only mounts, manifests, staged rsync, dedupe-merge gates, GitHub issue traceability, and governance/execution split.
