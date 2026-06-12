---
name: crossprovider hermes repo-ecosystem-audit-in-dependency-order-avoids-
description: Repo ecosystem audit in dependency order avoids rework
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture-audit, dependency-management, planning]
---

When auditing multi-repo systems, audit base dependencies first (e.g., assetutilities), then consumers (digitalmodel, assethold, worldenergydata). Reverse order causes rework when upstream changes are discovered late. Critical for refactoring epics.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
