---
name: crossprovider codex yaml-frontmatter-validator-uses-regex-parsing-no
description: YAML frontmatter validator uses regex parsing, not proper YAML
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, validator, yaml, defect]
---

llm-wiki validate_wiki_doc_key_contract.py hand-parses YAML frontmatter with regex. This allows duplicate doc_key lines to pass if the first is valid, and conditional 'required when available' text to satisfy unconditional 'required' field checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
