---
name: crossprovider codex adversarial-testing-surfaces-real-bypass-vectors
description: Adversarial testing surfaces real bypass vectors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, security, negative-controls]
---

Negative controls (testing for what should NOT pass) catch defects that positive tests miss. Enforcement code that appears to pass all cases can fail open on common edge forms (partial markers returning success, symlinks following out-of-tree, no-final-newline corruption) when not tested adversarially.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
