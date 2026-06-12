---
name: crossprovider hermes yaml-frontmatter-parsing-via-regex-fails-on-mult
description: YAML frontmatter parsing via regex fails on multiline lists
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parsing, yaml, data-format]
---

Hand-rolled parse_frontmatter missed multiline YAML lists; false conformance failures. Use proper YAML parser (PyYAML, ruamel.yaml); don't attempt regex-based frontmatter extraction.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
