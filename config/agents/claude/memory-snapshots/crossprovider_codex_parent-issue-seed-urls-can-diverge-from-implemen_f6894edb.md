---
name: crossprovider codex parent-issue-seed-urls-can-diverge-from-implemen
description: parent issue seed URLs can diverge from implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, testing, traceability]
---

Parent issue references may specify one URL (e.g., issue #624) while dependent implementations use a different one (issue #626). Tests that only validate against implementation constants won't detect the divergence. Cross-reference parent issue seeds during implementation review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
