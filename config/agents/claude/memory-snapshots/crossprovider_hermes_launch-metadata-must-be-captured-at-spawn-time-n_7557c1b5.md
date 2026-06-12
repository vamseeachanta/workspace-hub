---
name: crossprovider hermes launch-metadata-must-be-captured-at-spawn-time-n
description: Launch metadata must be captured at spawn time, not reconstructed
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [process-monitoring, evidence-collection, ops-instrumentation]
---

Parent shell command, PID, exit code, and initial launch status cannot be durably recovered after process exits if not logged at spawn time. Downstream evidence collection (git commits, closed issues, branch state) is possible, but execution context is lost. Instrument launches to write launch-manifest at spawn with timestamp, command, PID.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
