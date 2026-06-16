---
name: crossprovider codex comment-based-security-exemptions-apply-line-wid
description: Comment-based security exemptions apply line-wide, not token-scoped
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [security, parsing, comment-directives]
---

Directive comments like `# model-id-ok` disable checking for the entire line rather than just the annotated token, allowing multiple violations on the same line where only one should be exempted. Security exemptions should be token-scoped or use an allowlist to avoid unintended deferrals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
