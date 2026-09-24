---
name: crossprovider codex combined-test-cases-mask-which-condition-actuall
description: Combined test cases mask which condition actually failed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-design, test-isolation, adversarial-testing]
---

Tests that exercise multiple features/conditions in one assertion (e.g., mutate both locked-PDF status and shortcut role, then assert one error message) can pass even if one feature is broken—the first condition fails and masks the second. Split into isolated tests per feature so each condition failure surfaces independently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
