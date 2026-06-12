---
name: crossprovider hermes csv-field-newline-escaping-causes-parse-failures
description: CSV field newline escaping causes parse failures and cascades to validation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [csv, schema, validation]
---

Literal newlines mid-string after frontmatter (e.g., `frontmatter:sources\n,`) cause CSV parse failures. Solution: convert to escaped format `\\n`. Multiple test failures traced to this class of syntax error; fix at generator/schema level, not test workarounds.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
