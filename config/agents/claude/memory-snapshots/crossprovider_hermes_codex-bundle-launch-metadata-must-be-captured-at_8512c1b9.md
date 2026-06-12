---
name: crossprovider hermes codex-bundle-launch-metadata-must-be-captured-at
description: Codex bundle launch metadata must be captured at launch time
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [codex, launch-traceability, autonomous-agents, evidence-capture]
---

Sidecar files (PID, exit codes, timestamps) must be written during launch; retroactive recovery of original parent shell PID, local exit codes, and Hermes process handles is impossible after process exit. Without these, bundles are classified as `blocked_partial` rather than `succeeded` even if work completed.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
