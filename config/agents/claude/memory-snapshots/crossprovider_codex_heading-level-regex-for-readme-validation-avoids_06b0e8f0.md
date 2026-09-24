---
name: crossprovider codex heading-level-regex-for-readme-validation-avoids
description: Heading-level regex for README validation avoids false positives
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, regex, documentation, validation]
---

Use grep -qEi "^#+[[:space:]]*${section}" to match markdown heading syntax specifically, not substring anywhere in the file. Prevents false matches when section keywords appear casually in body text.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
