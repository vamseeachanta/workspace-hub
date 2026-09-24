---
name: crossprovider codex comment-based-guard-exemptions-must-protect-sing
description: Comment-based guard exemptions must protect single tokens, not entire lines
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, security-gates, guard-design]
---

Exemption comments like `# model-id-ok` that blanket-exempt a full line allow unrelated literals on that same line to bypass the guard. Design per-token exemptions using syntax that anchors to a specific value, so unintended literals in the same line cannot piggyback on the exemption.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
