---
name: crossprovider codex diff-only-legal-scans-for-staged-reviews
description: Diff-only legal scans for staged reviews
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [legal-scanning, staged-reviews, workflow-pattern]
---

Running full-repo legal scans during staged-file reviews produces thousands of unrelated historical violations (e.g., pre-existing /mnt/ace paths), drowning signal. Use scripts/legal/legal-sanity-scan.sh --diff-only for stage-specific reviews to isolate defects in current change.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
