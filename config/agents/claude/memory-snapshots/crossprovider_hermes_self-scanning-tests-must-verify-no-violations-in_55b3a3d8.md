---
name: crossprovider hermes self-scanning-tests-must-verify-no-violations-in
description: Self-scanning tests must verify no violations in same PR
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, merge-blocking]
---

If a test scans for legacy patterns, banned references, or other hygiene rules, the PR itself must not contain those violations. Split violations across branches can bypass the test; ensure self-scanning test runs on the merged result.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
