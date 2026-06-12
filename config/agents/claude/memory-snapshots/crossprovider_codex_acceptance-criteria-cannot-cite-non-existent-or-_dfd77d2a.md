---
name: crossprovider codex acceptance-criteria-cannot-cite-non-existent-or-
description: Acceptance criteria cannot cite non-existent or deferred CLI subcommands
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, acceptance-criteria, test-coverage]
---

Plan acceptance criteria naming provider auth/tool invocations must verify those subcommands exist in the current version. Deferring test coverage to future versions introduces silent failure modes when deferred tests eventually reveal defects that invalidate the prior approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
