---
name: crossprovider codex submodule-initialization-and-path-readability-si
description: Submodule initialization and path readability: silence is not validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [edge-cases, robustness, automation]
---

Automated checks that loop over expected repo directories must not silently skip uninitialized or unreadable submodules. Uninitialized checkouts and permission issues should produce explicit FAIL or WARN findings. Absence of an error is not proof of correctness. Discovered in WRK-1094: `check_config_drift.py` skipped repos whose directories were missing without reporting, masking checkout problems.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
