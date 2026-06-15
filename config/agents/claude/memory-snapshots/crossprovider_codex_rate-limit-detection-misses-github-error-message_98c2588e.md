---
name: crossprovider codex rate-limit-detection-misses-github-error-message
description: Rate-limit detection misses GitHub error-message variants
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [error-handling, resilience, github, robustness]
---

Current regex catches 'submitted too quickly', 'secondary rate', 'rate limit' but not 'abuse detection mechanism' or similar. GitHub's throttle messages vary; expand detection or honor `retry-after` hints when available.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
