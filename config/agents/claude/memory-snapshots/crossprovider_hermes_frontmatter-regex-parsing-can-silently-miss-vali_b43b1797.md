---
name: crossprovider hermes frontmatter-regex-parsing-can-silently-miss-vali
description: Frontmatter regex parsing can silently miss valid files with preamble
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parsing-fragility, frontmatter, regex]
---

Regex-based frontmatter detection fails on files with leading content. Llm-wiki #75: FRONTMATTER_RE didn't match pages starting with HTML comments before frontmatter, causing false-positive "missing frontmatter" reports. Document allowed preamble explicitly or use structural markers (e.g., XML parsers) instead of regex.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
