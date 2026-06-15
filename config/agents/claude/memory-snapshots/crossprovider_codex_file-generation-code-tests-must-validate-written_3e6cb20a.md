---
name: crossprovider codex file-generation-code-tests-must-validate-written
description: File-generation code tests must validate written artifacts, not just return payloads
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, file-generation, test-coverage-gap]
---

Tests that assert on in-memory return values can pass while generated files are corrupted by downstream transformations (e.g., sanitizers, mutations applied only at write time). Pattern: add file-level assertions to validate the actual written content/format, not just what the function returns in memory.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
