---
name: crossprovider codex manual-file-enumerations-in-plans-are-fragile
description: Manual file enumerations in plans are fragile
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, verification, enumeration]
---

Issue #51's self-scan target list omitted edited files across multiple review rounds, persisting even after explicit repairs. Prefer file-discovery command outputs (rg, find) over manually maintained prose inventories in plan-review acceptance criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
