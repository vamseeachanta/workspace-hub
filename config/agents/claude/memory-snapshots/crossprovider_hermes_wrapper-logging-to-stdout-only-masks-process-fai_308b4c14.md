---
name: crossprovider hermes wrapper-logging-to-stdout-only-masks-process-fai
description: Wrapper logging to stdout only masks process failures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [observability, logging, error-detection]
---

Empty logs can mean 'no output' or 'process failed'; logging stdout-only creates false-green health signals. Distinguish process exit code from output volume when assessing success.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
