---
name: crossprovider codex approved-cli-contracts-are-binding-acceptance-cr
description: Approved CLI contracts are binding acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cli-design, acceptance-criteria, issue-2945]
---

When an approved plan specifies exact flag names (--issue, --pr-range, --artifact, --format), those flags become acceptance criteria. Implementation must match exactly. Issue #2945: plan named 4 repeatable flags, implementation used different 4 flags, tests did not catch the mismatch because they only tested the implemented flags.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
