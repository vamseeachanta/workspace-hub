---
name: crossprovider codex repo-placement-plans-must-gate-required-repos-to
description: Repo placement plans must gate required repos to declared paths only
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [repo-placement, validation-gates, location-contracts]
---

Plans proposing tier-1 checkout layout must define allowed-root policies and tests proving arbitrary local/remote roots fail for required repos. Without explicit path gating in validation, dispatch silently satisfies requirements from non-canonical placements that confuse subsequent agents and violate location contracts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
