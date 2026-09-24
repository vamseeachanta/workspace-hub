---
name: crossprovider codex governance-surfaces-are-repo-tracked-runtime-lay
description: Governance surfaces are repo-tracked; runtime layers are separate authorities
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, governance, workspace-hub, control-plane]
---

workspace-hub's governance surfaces (AGENTS.md, CONTROL_PLANE_CONTRACT.md, `config/scheduled-tasks/schedule-tasks.yaml`, docs/plans/) are the durable authority. Hermes, system-cron, and native-provider runtimes are execution layers that receive governance from repo. Config assertions in code or runtime output must be verified against repo-tracked truth, not assumed authoritative.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
