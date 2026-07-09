---
name: crossprovider codex 69-legal-scanner-requires-repo-bounded-paths-in-
description: #69 legal scanner requires repo-bounded paths in public-surface-scan features
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [#69-integration, legal-scanner, security-gate]
---

The #69 legal scanner (scripts/legal/legal_sanity_scan.py:340-347) rejects scan paths outside the repository. Any feature integrating with #69 (e.g., #68) must use repo-relative classified temp paths and remove them before clean-state verification. Tests should verify #69 remains a sibling gate, not replaced by the integrating feature.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
