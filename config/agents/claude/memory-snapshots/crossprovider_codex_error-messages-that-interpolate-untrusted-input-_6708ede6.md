---
name: crossprovider codex error-messages-that-interpolate-untrusted-input-
description: Error messages that interpolate untrusted input can leak through CI artifacts and tracebacks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, privacy, error-handling, input-validation]
---

Exception messages that format the full rejected input (e.g., source labels) into the message text can escape into CI logs, GitHub comments, and tracebacks. Prefer generic rejection reasons that reference only the identifier/rank, not the untrusted value itself. This applies to validation failures, parse errors, and any code path where the failure might be logged or shared outside the secure boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
