---
name: crossprovider codex synthetic-monkeypatch-reproducers-isolate-alloca
description: Synthetic monkeypatch reproducers isolate allocator logic from parsers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, monkeypatch, reproducers, isolation]
---

Test filename/slug deduplication by monkeypatching a fake attachment object and checking output paths directly, without invoking actual Office/PDF parsers. Reproducer returns early with synthetic output; this isolates the allocation logic from format-lane complexity and speeds up verification of edge cases (e.g., ordinal collision chains).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
