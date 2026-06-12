---
name: crossprovider hermes background-job-delegation-via-file-based-prompt-
description: Background job delegation via file-based prompt + subprocess polling
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [delegation, background-jobs, subprocess-pattern, multi-session]
---

Delegating long-running tasks to Claude sub-jobs via file-based prompt files + background subprocess with loop polling allows main session to remain responsive. Sub-job prompt should reference pre-approved plan marker to gate execution; loop checks monitor process state without blocking.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
