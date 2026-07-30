---
name: crossprovider codex prebuilt-case-snapshots-must-use-positive-allowl
description: Prebuilt case snapshots must use positive allowlists, not full copies
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, architecture, CFD]
---

Full case copies include unattested residue: numeric time dirs, processor dirs, logs. Must construct snapshots from explicit input allowlist and reject every unexpected top-level entry. Add stale-time and processor-directory regression tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
