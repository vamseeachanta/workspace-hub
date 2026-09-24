---
name: crossprovider gemini test-stub-implementations-for-no-op-behavior-and
description: Test stub implementations for no-op behavior and signal future updates
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, stubs, incomplete-code, coverage]
---

Tests for incomplete/stub code should verify that methods return None and don't raise exceptions under various inputs. Surface in test docstrings that assertions will need updating once the real implementation arrives. This pattern prevents stub behavior from silently becoming the expected contract.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
