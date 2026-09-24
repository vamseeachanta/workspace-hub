---
name: crossprovider gemini workflow-version-changes-require-template-defini
description: Workflow version changes require template definitions and backfill strategy for in-flight work
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow, migration, versioning]
---

Moving from one workflow version to another (e.g., adding new evidence requirements) must include explicit template definitions and migration/backfill policy for work items already in progress, not just forward-looking enforcement. Without it, the gap between old and new workflows will break or stall existing items.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
