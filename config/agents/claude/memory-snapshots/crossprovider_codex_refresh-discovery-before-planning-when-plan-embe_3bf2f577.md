---
name: crossprovider codex refresh-discovery-before-planning-when-plan-embe
description: Refresh discovery before planning when plan embeds point-in-time counts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [planning, discovery, stale-evidence]
---

Plans that encode root folder counts, artifact inventories, or discovery snapshots from a prior date will stale quickly. Before accepting a plan, re-run the discovery from live state and verify actual vs. embedded counts; don't use stale evidence as acceptance criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
