---
name: crossprovider codex subtle-error-message-changes-violate-behavior-pr
description: Subtle error-message changes violate behavior-preservation claims
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, behavior-preservation, error-handling]
---

Refactors that change `ValueError` text or other observable error strings are visible runtime behavior changes. Plans claiming 'no behavior change' must be scrutinized for string/message mutations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
