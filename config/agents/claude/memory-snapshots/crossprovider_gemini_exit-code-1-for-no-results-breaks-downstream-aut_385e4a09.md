---
name: crossprovider gemini exit-code-1-for-no-results-breaks-downstream-aut
description: Exit code 1 for 'no results' breaks downstream automation
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cli-design, exit-codes, automation]
---

Returning exit 1 for 'query found nothing' conflates with errors. Automation scripts treat non-zero as failure. Return 0 with empty output; reserve non-zero for actual errors only.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
