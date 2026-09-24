---
name: crossprovider codex error-handling-must-preserve-interface-contracts
description: Error handling must preserve interface contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [api-contracts, error-handling, json-envelope]
---

If an API promises stable JSON envelopes for all responses, error paths (invalid args, parser failures) must also emit the envelope—don't let argparse errors print raw text. Wrap argument parsing in try-except, emit JSON error envelope. Tests must exercise error cases with envelope verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
