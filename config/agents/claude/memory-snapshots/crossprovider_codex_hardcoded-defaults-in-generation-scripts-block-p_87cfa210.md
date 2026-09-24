---
name: crossprovider codex hardcoded-defaults-in-generation-scripts-block-p
description: Hardcoded defaults in generation scripts block parent state clearing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [generation-scripts, state-clearing, parent-blocker-logic]
---

When a data-generation script has hardcoded default classifications (e.g., 'standards-disposition = needs-follow-up'), updating only the input metadata snapshot is insufficient to clear parent blockers. The script logic itself must be modified to detect when the blocking condition is resolved. Found in private-ingest-readiness-matrix where disposition status required explicit code changes, not just metadata updates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
