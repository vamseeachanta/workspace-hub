---
name: crossprovider codex acceptance-criteria-that-can-silently-skip-or-by
description: Acceptance criteria that can silently skip or bypass verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, test-strategy, skip-bypass]
---

Tests that exit as 'skip' or 'not run' (e.g., when a license is not available, or under an optional conditional gate) do not verify the acceptance criterion. If the required environment is present, the test still won't run. Acceptance criteria must be either always-run or have explicit, documented opt-out gates, not silent skip conditions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
