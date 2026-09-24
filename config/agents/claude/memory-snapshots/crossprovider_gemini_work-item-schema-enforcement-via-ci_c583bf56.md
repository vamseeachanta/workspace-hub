---
name: crossprovider gemini work-item-schema-enforcement-via-ci
description: Work item schema enforcement via CI
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [schema-enforcement, work-queue-governance, ci-gates]
---

Enforce required frontmatter fields (status, plan_reviewed, plan_approved, provider, complexity, created_at, target_repos) on active WRK items via pre-commit or CI. Fail on missing or invalid enum values to prevent operational inconsistency.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
