---
name: crossprovider gemini workspace-hub-entry-surfaces-and-control-plane-c
description: Workspace-hub entry surfaces and control-plane contracts must co-evolve
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [governance, configuration-management, workspace-hub, release-process]
---

Root provider entry files (CLAUDE.md, GEMINI.md, AGENTS.md) and control-plane contracts are co-owned governance artifacts. A provider/model release or contract change touching one must audit and update all others to prevent configuration drift and user-facing inconsistency.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
