---
name: crossprovider hermes snippet-selection-is-lossy-on-lower-page-facts
description: Snippet selection is lossy on lower-page facts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [rag, snippet-extraction, information-loss]
---

_context_snippets() prefers early/frontmatter lines (len < 8) then truncates to 600 chars; required facts lower in a retrieved page are often omitted even when page is correct (e.g., marine-001 retrieves page but loses OrcaWave/digitalmodel mentions).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
