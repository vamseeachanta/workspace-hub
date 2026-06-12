---
name: crossprovider hermes python-raw-string-regex-escape-sequences-pitfall
description: Python raw string regex escape sequences pitfall
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [python, regex, common-bug, testing]
---

Raw strings r"word\\s*" match a literal backslash followed by 's', not whitespace. Correct pattern is r"word\s*" with single backslash. Common in frontmatter/CSV parsing where line-extraction regexes need careful escaping; double-check against test cases before committing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
