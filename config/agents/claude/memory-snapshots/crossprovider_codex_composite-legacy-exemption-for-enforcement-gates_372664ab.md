---
name: crossprovider codex composite-legacy-exemption-for-enforcement-gates
description: Composite legacy exemption for enforcement gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gate-pattern, backward-compatibility, version-management]
---

When adding enforcement gates to existing work, use composite criteria for backward compatibility: numeric ID parsing (WRK-NNN format, where N < 658 is exempt) AND created_at timestamp cutoff (items created before gate-activation date are exempt). Both conditions exempt; failure on either triggers enforcement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
