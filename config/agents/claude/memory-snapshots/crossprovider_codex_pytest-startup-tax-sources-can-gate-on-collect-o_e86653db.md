---
name: crossprovider codex pytest-startup-tax-sources-can-gate-on-collect-o
description: Pytest startup tax sources can gate on --collect-only
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [pytest, performance, ci]
---

Heavy conftest work (regression DB loads via pandas) and plugin init (git describe on NTFS-FUSE, faker locale scan) run unconditionally even on `--collect-only`, adding >180s to every test listing. Gating these on whether tests will execute (not just collect) recovers fast-path performance without removing capability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
