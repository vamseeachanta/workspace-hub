---
name: crossprovider codex validator-scope-creep-allows-non-contract-algori
description: Validator scope creep allows non-contract algorithms
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [validation, contract, fail-closed]
---

Source-doc-key validator (#2389) accepted `sha512`, `sha1`, `md5`, and `sha256` but contract specifies only `sha256` as canonical and `md5` as legacy read-only. Validators must fail-closed: reject unknown algorithms and accept only explicitly-allowed namespaces. Tests that assert non-contract algorithms are accepted lock in the wrong contract and mask future regressions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
