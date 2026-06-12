---
name: crossprovider hermes parser-robustness-frontmatter-regex-stopping-at-
description: Parser robustness: frontmatter regex stopping at first `---` creates unresolved edges
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parser-robustness, frontmatter, malformed-input]
---

Frontmatter parsers using greedy `---...---` regex without YAML validation can truncate at malformed closings, leaving cross-link fields incomplete and creating unresolved edge references. Example: llm-wiki #77 had `_parse_frontmatter` stopping at first `---`, causing target_refs like `'wikis/maritime-law/...'` from incomplete YAML keys. **Why:** malformed YAML in real files triggers silent failures in downstream generation/validation. **How to apply:** validate frontmatter as proper YAML using stdlib `yaml.safe_load()` not regex; reject files with parse errors; test parser against fixtures with malformed/nested `---` patterns.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
