---
name: crossprovider codex read-only-contract-tests-via-string-grep-miss-ar
description: Read-only contract tests via string grep miss argv-list mutations
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, security-contracts, read-only-enforcement]
---

A read-only safety test that greps shell scripts for mutation patterns ('git push', 'gh issue comment') won't catch equivalent argv lists ['git', 'push'] in Python code. String-matching safety contracts are bypassable by restructuring calls into list form.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
