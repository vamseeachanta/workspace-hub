---
name: crossprovider gemini untrusted-boundary-markers-in-review-transport
description: Untrusted boundary markers in review transport
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [review-transport, security, prompt-injection-defense, shell-patterns]
---

Use timestamped, random-suffixed boundary markers (REVIEW-CONTENT-{timestamp}-{pid}) to isolate untrusted review content in shell scripts, preventing prompt injection in Claude/Gemini review submissions. Pattern discovered in WRK-640 hardening work.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
