---
name: crossprovider codex yolo-mode-requires-explicit-security-warning-and
description: YOLO mode requires explicit security warning and rollback path
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [security, configuration]
---

When enabling `--yolo` or `approval_policy="never"`, document prominently that this removes sandboxing and approval gates, recommend external hardening (isolated environment), and provide a documented escape: invoking the binary with explicit flags to restore safer settings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
