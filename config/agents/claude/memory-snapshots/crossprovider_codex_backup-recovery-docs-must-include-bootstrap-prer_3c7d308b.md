---
name: crossprovider codex backup-recovery-docs-must-include-bootstrap-prer
description: Backup recovery docs must include bootstrap prerequisites and post-restore validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [disaster-recovery, documentation, operational-runbooks]
---

Recovery procedures that list only file paths are incomplete. Include machine bootstrap requirements, restore ordering so state doesn't replay into a partial setup, ownership/permission verification, and a post-restore smoke test. Otherwise recovery fails silently with wrong state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
