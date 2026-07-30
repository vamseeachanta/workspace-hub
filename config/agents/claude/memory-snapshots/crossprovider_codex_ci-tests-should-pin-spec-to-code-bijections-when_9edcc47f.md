---
name: crossprovider codex ci-tests-should-pin-spec-to-code-bijections-when
description: CI tests should pin spec-to-code bijections when specs rely on naming/metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [ci-validation, identifiers, bijection]
---

If a reference index or spec assumes identifier correspondence (e.g., section-id == explorer-filename or explorer-stem), add a test that loads both systems and verifies exact bijection, catching silent renames and orphaned entries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
