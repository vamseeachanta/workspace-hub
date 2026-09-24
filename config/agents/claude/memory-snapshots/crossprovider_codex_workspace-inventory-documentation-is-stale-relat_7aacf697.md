---
name: crossprovider codex workspace-inventory-documentation-is-stale-relat
description: Workspace inventory documentation is stale relative to actual state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [docs-drift, workspace-inventory, onboarding]
---

Docs claim 26+ repos and root `.agent-os`, but actual workspace has 25 child Git repos and no root `.agent-os`. Docs list non-existent repos (`energy`, `ai-native-traditional-eng`) and miss live repos (`CAD-DEVELOPMENTS`, `aceengineer-strategy`). Prior evaluation issue #1467 concluded on `.agent-os` removal; docs were not updated. Inventory must be synchronized with live state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
