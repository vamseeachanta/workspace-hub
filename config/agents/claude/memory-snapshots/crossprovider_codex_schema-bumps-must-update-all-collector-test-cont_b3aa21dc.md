---
name: crossprovider codex schema-bumps-must-update-all-collector-test-cont
description: Schema bumps must update all collector test contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema, testing, contracts]
---

If a schema version bump changes multiple implementations (Python, PowerShell, shell), all their test contracts and golden fixtures must update in parallel. Missing a test leg leaves the contract stale and breaks acceptance criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
