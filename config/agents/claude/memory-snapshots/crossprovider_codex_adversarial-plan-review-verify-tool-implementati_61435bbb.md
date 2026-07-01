---
name: crossprovider codex adversarial-plan-review-verify-tool-implementati
description: Adversarial plan review: verify tool implementations, not just flag existence
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [plan-review, verification, tooling-quirks]
---

When a plan claims a tool will enforce safety via a specific flag/behavior (e.g., --scan-public-path for fallback validation), read the actual tool implementation. A flag may exist but not fully implement the claimed safety (e.g., not reusing all checks for extra paths). This is a MAJOR blocker if the fallback's safety is not actually there.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
