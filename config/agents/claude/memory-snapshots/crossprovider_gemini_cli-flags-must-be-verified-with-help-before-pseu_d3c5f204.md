---
name: crossprovider gemini cli-flags-must-be-verified-with-help-before-pseu
description: CLI flags must be verified with --help before pseudocode
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cli, pseudocode, verification]
---

Invalid CLI flags (e.g., `gemini -p` when `-p` doesn't exist) cause execution failure. Verify against `--help` or man pages before writing pseudocode. Don't invent flags from training data.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
