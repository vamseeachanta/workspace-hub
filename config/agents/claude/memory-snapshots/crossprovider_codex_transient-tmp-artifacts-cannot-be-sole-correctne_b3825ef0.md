---
name: crossprovider codex transient-tmp-artifacts-cannot-be-sole-correctne
description: Transient /tmp/ artifacts cannot be sole correctness basis
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, durable-vs-transient, evidence-standards]
---

Planning decisions that decompose work or make structural/architectural calls must use durable checked-in artifacts, not `/tmp/` inventory or local drafts. Even when transient evidence exists locally, the plan must define a corresponding durable artifact (checked into the repo or nested-repo) before implementation can be approved.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
