---
name: crossprovider codex unverified-live-state-assertions-in-plans-cause-
description: Unverified live-state assertions in plans cause rework
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, correctness, verification, mandatory-gate]
---

Plans repeatedly claim 'verified issue state' or 'file exists' with only self-asserted terminal output as proof. Under correctness review, these remain unverified dependencies. Fix: embed reproducible artifacts (e.g., commit SHAs, file checksums, issue-state snapshots taken at plan time) or mark assertions explicitly UNVERIFIED and remove from dependency reasoning.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
