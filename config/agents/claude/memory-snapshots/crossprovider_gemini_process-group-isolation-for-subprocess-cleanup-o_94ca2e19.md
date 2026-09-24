---
name: crossprovider gemini process-group-isolation-for-subprocess-cleanup-o
description: Process group isolation for subprocess cleanup on timeout
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [process-management, timeout, bash, cleanup]
---

Use `setsid` to launch subprocesses in an isolated process group; on timeout, kill the entire group (`kill -- -$pgid`) not just the direct child. Prevents resource leaks from grandchild processes spawned by the subprocess.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
