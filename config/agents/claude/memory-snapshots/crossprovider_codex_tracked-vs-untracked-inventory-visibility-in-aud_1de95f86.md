---
name: crossprovider codex tracked-vs-untracked-inventory-visibility-in-aud
description: Tracked vs untracked inventory visibility in audits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [auditing, inventory-systems, data-loss-prevention]
---

Audit systems that scan both git-tracked state and filesystem state must explicitly model and report filesystem-only items separately, since untracked files can be silently lost if not surfaced as high-signal findings. The weekly skills audit discovered this gap: it was tracking overall inventory but not reporting untracked active skills as a first-class defect class.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
