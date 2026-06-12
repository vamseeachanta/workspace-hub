---
name: crossprovider hermes preserve-dirty-workspace-artifacts-during-cleanu
description: Preserve dirty workspace artifacts during cleanup operations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workspace-management, git-workflow, artifact-preservation]
---

Session-generated artifacts (review outputs, reports, handoffs, provider telemetry) are operationally relevant; use targeted committed staging during cleanup rather than broad reset/clean operations that lose evidence and provenance.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
