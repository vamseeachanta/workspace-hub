---
name: crossprovider codex shared-checkout-tests-need-fixtures-or-skip-logi
description: Shared-checkout tests need fixtures or skip logic, not permanent collect_ignore
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, technical-debt]
---

Tests that depend on sibling wiki checkouts (e.g., citation resolution tests referencing workspace-hub wikis) must either vendor minimal fixtures or skip when standalone. Using collect_ignore as a ratchet is acceptable for interim CI survival, but must be paired with a formal remediation issue that removes the ignore and fixes the root cause—never leave ratchets permanent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
