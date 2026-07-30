---
name: crossprovider codex marp-frontmatter-can-render-client-visible-copy
description: Marp frontmatter can render client-visible copy
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [marp, client-facing, presentation-validation, content-guard]
---

Marp `header` and `footer` frontmatter fields render in the final presentation output even when content-validation tests only scan visible slide body. Guards on prohibited terms (e.g., `AI`, `frontier model`) must scan the full Marp source with frontmatter included, not just `text.split('---')[2]` visible content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
