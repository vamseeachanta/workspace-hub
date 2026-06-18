---
name: crossprovider codex regulatory-plans-need-row-level-validation-tests
description: Regulatory plans need row-level validation tests
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [regulatory-compliance, test-design, acceptance-criteria]
---

When acceptance criteria require row-level distinctions (binding-regulation vs design-standard vs needs-counsel-review), TDD must test status assignment per row, not just field presence or allowed-values checks. Undefined row-level logic is a TDD gap.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
