---
name: crossprovider codex absolute-path-hygiene-is-a-pre-commit-gate
description: Absolute-path hygiene is a pre-commit gate
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [safety, reproducibility, plan-review]
---

Plans are scanned for machine-specific absolute paths (`/home/`, `/mnt/`, `file://`, drive paths) before commit; these break reproducibility across machines. Flag and remove before staging.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
