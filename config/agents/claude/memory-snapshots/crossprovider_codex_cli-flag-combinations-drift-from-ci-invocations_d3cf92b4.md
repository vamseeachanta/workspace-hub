---
name: crossprovider codex cli-flag-combinations-drift-from-ci-invocations
description: CLI flag combinations drift from CI invocations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [ci-coverage, implementation]
---

Validators may support new gates (--scan-public-path, --issue-comment-body-file, --review-issue N) but CI invokes them without those flags, exercising only default behavior. New gates in implementation require explicit CI step updates or remain untested.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
