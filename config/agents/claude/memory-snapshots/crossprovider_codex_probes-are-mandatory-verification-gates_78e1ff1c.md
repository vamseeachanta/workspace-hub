---
name: crossprovider codex probes-are-mandatory-verification-gates
description: Probes are mandatory verification gates
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [verification-gate, repo-integrity, mandatory-check]
---

Before reporting ingest completion, run frontmatter/link probe, scripts/enforcement/check-no-conflict-markers.sh, and git diff --check. These are not optional and must PASS. Blocking them masks defects at scale.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
