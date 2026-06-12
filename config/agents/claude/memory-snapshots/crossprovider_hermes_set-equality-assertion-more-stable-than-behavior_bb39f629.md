---
name: crossprovider hermes set-equality-assertion-more-stable-than-behavior
description: Set equality assertion more stable than behavioral regression tests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, regression, patterns, assertions]
---

Lock allowlists/configs via direct equality check on constants, not behavioral test. Assert `ALLOWED_LEGACY_FILES == {file1, file2}` directly. Catches additions/removals/path changes; simpler and more stable than verifying indirect behavior patterns.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
