---
name: crossprovider codex semantic-evidence-cutoffs-cannot-be-machine-enfo
description: Semantic evidence cutoffs cannot be machine-enforced without explicit commit bounds
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [reproducibility, verification, security]
---

Plan phrases like 'evidence before this revision' are bypassable with backdated/corrected records if not frozen by commit hash or blob allowlist. Timestamp and filename-based cutoffs are not sufficient; must establish explicit commit range or immutable raw-evidence snapshot.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
