---
name: crossprovider codex scheduler-job-run-must-catch-and-return-jobresul
description: Scheduler job run() must catch and return JobResult
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [scheduler-jobs, error-handling, exception-boundaries]
---

Job `run()` must catch all exceptions and return `JobResult` with proper status/error_msg/retryable fields. Exceptions that escape cause the scheduler to record them as `job_name="unknown"`, losing traceability. Keep fixture operations and refresh calls inside the try block, not after.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
