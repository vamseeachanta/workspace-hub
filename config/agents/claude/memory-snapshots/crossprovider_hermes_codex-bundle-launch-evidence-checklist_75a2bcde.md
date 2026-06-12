---
name: crossprovider hermes codex-bundle-launch-evidence-checklist
description: Codex bundle launch evidence checklist
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [codex, bundle-monitoring, evidence, audit-trail]
---

Auditable evidence requires 75-item checklist covering launch ID/command/timestamp/PID, initial status, monitoring mechanism, polling interval, transient-state handling, terminal status with objective evidence (exit code/logs), and duration. Missing metadata at launch time is not retrospectively recoverable—capture PID/exit code/session handle immediately after launch.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
