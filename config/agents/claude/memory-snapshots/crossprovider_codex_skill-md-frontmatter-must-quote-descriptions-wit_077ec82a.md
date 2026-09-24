---
name: crossprovider codex skill-md-frontmatter-must-quote-descriptions-wit
description: SKILL.md frontmatter must quote descriptions with colons
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, yaml-syntax, skill-loader, error-prevention]
---

YAML descriptions in SKILL.md containing colons cause 'mapping values are not allowed' parse errors. Quote the description value: `description: "my feature: description"` to avoid config loader failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
