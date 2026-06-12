---
name: crossprovider hermes critical-parsing-must-anchor-regex-to-avoid-fals
description: Critical parsing must anchor regex to avoid false substring matches
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [regex-parsing, correctness, implementation-bugs]
---

Unanchored regex like `re.search(r"Plan-SHA256...")` can match within `Reviewed-Plan-SHA256`, returning wrong SHA. Use `^Plan-SHA256:` or equivalent anchoring for all authoritati ve parsing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
