---
name: crossprovider hermes inventory-fixtures-should-be-committed-artifacts
description: Inventory fixtures should be committed artifacts for deterministic tests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, ci-determinism, fixtures, inventory]
---

For repo portfolio/inventory testing (e.g., docs/REPO_MISSION_PORTFOLIO.md), commit a `docs/registry/repo-portfolio-inventory.yaml` fixture and have tests parse it, not live filesystem. Allow WORKSPACE_HUB_PORTFOLIO_ROOT env var to override (for live dev), but CI uses committed snapshot to avoid flakiness from filesystem state drift.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
