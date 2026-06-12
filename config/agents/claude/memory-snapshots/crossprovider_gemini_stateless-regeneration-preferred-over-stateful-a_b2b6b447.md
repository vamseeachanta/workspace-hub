---
name: crossprovider gemini stateless-regeneration-preferred-over-stateful-a
description: Stateless regeneration preferred over stateful artifact mutation
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [artifact-generation, html-rendering, state-management]
---

HTML/YAML lifecycle documents should regenerate entirely from source-of-truth YAML/MD on each write, not incrementally mutate existing files. Stateful mutation (parsing HTML, finding sections, updating divs) is fragile to structural drift and difficult to test. Adopt: read source artifacts → render entire document → write, making the output deterministic and auditable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
