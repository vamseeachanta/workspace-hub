---
name: crossprovider hermes json-artifact-companions-need-security-scanning
description: JSON artifact companions need security scanning
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, security, json-artifacts, report-generation]
---

When a report generator emits both markdown and JSON artifacts, the validator must scan the JSON companion's raw text for forbidden/private patterns before schema validation, not just the markdown. Tests passed in llm-wiki #75 with markdown-only scanning; adversarial review caught the gap.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
