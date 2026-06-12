---
name: crossprovider gemini pid-liveness-via-kill-0-misses-reuse-risk
description: PID liveness via kill -0 misses reuse risk
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [process-management, liveness-detection]
---

After machine reboot or long delay, PIDs are reused by unrelated processes. `kill -0 $pid` confirms a process exists but not which one. Validate process identity via `/proc/$pid/cmdline` check or process name verification before relying on PID-based liveness.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
