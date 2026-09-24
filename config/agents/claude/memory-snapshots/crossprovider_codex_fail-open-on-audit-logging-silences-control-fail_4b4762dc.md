---
name: crossprovider codex fail-open-on-audit-logging-silences-control-fail
description: Fail-open on audit/logging silences control failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit, logging, controls, observability]
---

Using `|| true` on all audit logging call sites defeats the control objective because missing records are silent. Audit systems need detectable failure paths: stderr logs, sidecar markers, or counters. Without them, coverage gaps go unnoticed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
