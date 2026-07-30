---
name: crossprovider codex derive-path-rule-definitions-from-validator-func
description: Derive path/rule definitions from validator functions, not hardcoded lists
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [architecture, single-source-of-truth]
---

Hardcoded path lists in workflows drift from tracked inventory; dynamic validator functions stay in sync with code changes. Make validators the single source of truth for classification rules.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
