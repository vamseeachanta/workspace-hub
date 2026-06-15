---
name: crossprovider codex host-mount-paths-should-not-be-committed-to-trac
description: Host mount paths should not be committed to tracked files
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [repo-hygiene, portability]
---

Environment-specific absolute paths (e.g., `/mnt/ace/frontierdeepwater/`) in tracked README or config files break portability and pollute version control. Use relative paths or env-var substitution instead; flag this as a repo invariant violation during independent review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
