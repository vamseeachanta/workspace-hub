---
name: crossprovider codex read-only-audit-gates-are-load-bearing-in-parall
description: Read-only audit gates are load-bearing in parallel agent environments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency, gates, safety, multi-agent]
---

When multiple agents run in parallel, pre-completion cleanup audits must execute in read-only mode (inspection only, no mutations) to avoid contamination or conflicting commits. Cleanup mutations should be deferred to single-agent phases or guarded by explicit user approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
