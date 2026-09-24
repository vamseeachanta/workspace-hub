---
name: crossprovider gemini email-queue-uses-local-first-state-gmail-side-op
description: Email queue uses local-first state; Gmail-side ops deferred
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [email, architecture]
---

Email workflows use local JSONL + snapshot as source-of-truth, not Gmail labels. Gmail-side delete/archive deferred to follow-on issue pending `gmail.modify` re-auth. Separation clarifies scope and defers safety-critical operations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
