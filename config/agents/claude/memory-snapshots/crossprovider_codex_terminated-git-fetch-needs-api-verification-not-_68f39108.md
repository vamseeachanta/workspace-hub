---
name: crossprovider codex terminated-git-fetch-needs-api-verification-not-
description: Terminated git fetch needs API verification, not blind retry
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-debugging, signal-recovery, api-verification]
---

When git fetch is externally terminated (signal 15), verify cached refs against GitHub API (ls-remote) before retrying or using cached state. Process termination is often independent of network; API verification distinguishes actual network failure from external kill signals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
