---
name: crossprovider codex adversarial-reviews-require-affirmative-verifica
description: Adversarial reviews require affirmative verification, not silence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, adversarial-stance]
---

Returning an empty review or only praising well-structured work is a failure. Default to MINOR/MAJOR unless affirmatively verified against specific checks (file reads, tool invocations, reproduction). Explicitly state what was checked even if no defects were found.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
