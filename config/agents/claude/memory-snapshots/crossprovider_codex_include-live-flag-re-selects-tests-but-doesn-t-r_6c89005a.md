---
name: crossprovider codex include-live-flag-re-selects-tests-but-doesn-t-r
description: --include-live flag re-selects tests but doesn't restore strict signaling
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, gate-defeat]
---

A flag that re-selects previously deselected tests still allows failures to be masked if expected-failures.txt is global. Strict validation requires either mode-specific expected-failures or ignoring the list when the flag is set.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
