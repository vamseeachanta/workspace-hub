---
name: crossprovider codex gate-permission-assumptions-must-be-verified-aga
description: Gate/permission assumptions must be verified against actual config
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [governance, planning, enforcement]
---

Plans frequently make assumptions about what paths are blocked or allowed (e.g., '.claude/skills/ edits require plan-approval marker'). Verify these against actual `.claude/hooks/` whitelist config before designing constraints around them — the gate may already exempt the path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
