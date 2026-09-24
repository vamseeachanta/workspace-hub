---
name: crossprovider codex plan-review-fanout-sh-has-known-provider-failure
description: plan-review-fanout.sh has known provider failure modes requiring hardening
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-automation, provider-quirks, shell-robustness]
---

Observed failures include provider timeouts (no timeout handling), Gemini trust prompts (missing trust-env configuration), Codex stderr-only structured output (stderr not promoted), and orphaned provider processes (no cleanup). Future hardening should add timeout/recovery, stderr capture, and process cleanup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
