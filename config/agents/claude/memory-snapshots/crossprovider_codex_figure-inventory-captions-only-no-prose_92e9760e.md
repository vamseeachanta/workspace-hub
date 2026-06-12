---
name: crossprovider codex figure-inventory-captions-only-no-prose
description: Figure inventory: captions only, no prose
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [llm-wiki, figure-inventory, filtering]
---

llm-wiki figure inventories must include ONLY actual figure captions (pattern 'Figure N <Title>'), not body prose mentions ('Figure N provides...'). De-duplicate by figure ID. Prose-reference rows are structural noise that breaks downstream analysis.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
