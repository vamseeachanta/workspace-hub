---
name: crossprovider codex don-t-update-status-snapshots-until-deliverables
description: Don't update status snapshots until deliverables are tracked
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [governance, artifact-tracking, state-sync]
---

Marking issues as `status:implemented` in tracked snapshots before their deliverable artifacts are committed to Git creates invalid parent-completeness claims that fail governance checks. Only update status snapshots after implementation files are staged and tracked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
