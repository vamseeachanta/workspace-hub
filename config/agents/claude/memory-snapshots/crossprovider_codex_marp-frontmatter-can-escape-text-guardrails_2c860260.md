---
name: crossprovider codex marp-frontmatter-can-escape-text-guardrails
description: Marp frontmatter can escape text guardrails
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [marp, text-guards, rendering-escape]
---

Marp `header` and `footer` frontmatter directives render client-visible content that may escape body-only text scanners. Guardrail tests for forbidden terms must parse full renderable source, including frontmatter and HTML-comment stripping, not just visible slide body.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
