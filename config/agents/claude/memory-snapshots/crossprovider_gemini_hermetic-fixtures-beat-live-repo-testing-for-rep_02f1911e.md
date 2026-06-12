---
name: crossprovider gemini hermetic-fixtures-beat-live-repo-testing-for-rep
description: Hermetic fixtures beat live repo testing for repeatability
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, fixtures, isolation]
---

Testing against live work-queue items risks mutations and flakiness. Use mktemp -d with synthetic files + trap cleanup. Enables QUEUE_ROOT env var injection so scripts accept `--queue-root $TMPDIR` for testability without touching live state.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
