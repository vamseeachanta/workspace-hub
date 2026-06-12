---
name: crossprovider hermes yaml-unquoted-values-with-colons-are-truncated-a
description: YAML unquoted values with colons are truncated at comment symbol
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [yaml, parsing, configuration]
---

YAML descriptions with unquoted colons (e.g., `desc: value: with: colons # comment`) get truncated at the `#`. Solution: quote all values that contain colons or hyphens; prefer YAML block scalars (`|` / `>`) for multiline content.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
